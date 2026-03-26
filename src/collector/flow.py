import time
from typing import Optional
from datetime import datetime
import httpx
import config
from src.auth import get_valid_token
from src.database.connection import get_connection

# Endpoints
BANDARMOLOGI_URL = f"{config.BASE_URL}/marketdetectors/{{ticker}}?transaction_type=TRANSACTION_TYPE_NET&market_board=MARKET_BOARD_REGULER&investor_type=INVESTOR_TYPE_ALL&limit=25"
FOREIGN_FLOW_URL = f"{config.BASE_URL}/findata-view/foreign-domestic/v1/chart-data/{{ticker}}?market_type=MARKET_TYPE_REGULAR&period=PERIOD_RANGE_1D"

def _parse(val) -> Optional[float]:
    if val is None: return None
    try: return float(str(val).replace(",", "").strip())
    except: return None

def get_headers():
    token = get_valid_token()
    return {
        "Authorization": f"Bearer {token}",
        "User-Agent": "Mozilla/5.0",
        "Origin": "https://stockbit.com"
    }

def get_retail_brokers() -> list:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT code FROM broker_master WHERE is_retail = TRUE")
        return [row[0] for row in cur.fetchall()]
    except:
        return []
    finally:
        conn.close()

def fetch_flow_data(ticker: str, target_date: datetime.date = None) -> dict:
    headers = get_headers()
    today = target_date if target_date else datetime.now().date()
    retail_brokers = get_retail_brokers()
    date_str = today.strftime("%Y-%m-%d")
    
    result = {
        "broker_tx": [],
        "metrics": {
            "symbol": ticker,
            "date": today,
            "close_price": 0,
            "volume": 0,
            "foreign_net_val": 0,
            "retail_net_val": 0,
            "big_money_net_val": 0,
            "accdist_status": None
        }
    }
    
    # URL dinamis berdasarkan tanggal
    bndr_url = BANDARMOLOGI_URL.format(ticker=ticker) + f"&from={date_str}&to={date_str}"
    ff_url = FOREIGN_FLOW_URL.format(ticker=ticker) + f"&from={date_str}&to={date_str}"
    
    # Dictionary to merge broker buy and sell
    brokers_dict = {}

    with httpx.Client(headers=headers, timeout=30) as client:
        # 1. Fetch Market Detector & Broker Summary
        try:
            res_b = client.get(bndr_url)
            res_b.raise_for_status()
            data_b = res_b.json().get("data", {})
            detector = data_b.get("bandar_detector", {})
            bs = data_b.get("broker_summary", {})
            
            if detector:
                result["metrics"]["accdist_status"] = detector.get("avg", {}).get("accdist")
            
            # Combine Buy
            for b in bs.get("brokers_buy", []):
                code = b.get("netbs_broker_code")
                brokers_dict[code] = brokers_dict.get(code, {"net_lot": 0, "net_val": 0, "avg_price": 0})
                brokers_dict[code]["net_lot"] += _parse(b.get("blot") or 0)
                brokers_dict[code]["net_val"] += _parse(b.get("bval") or 0)
                brokers_dict[code]["avg_price"] = _parse(b.get("netbs_buy_avg_price")) # Simplification: use buy avg if net buyer

            # Combine Sell (stockbit provides negative values for sell lot and val)
            for s in bs.get("brokers_sell", []):
                code = s.get("netbs_broker_code")
                brokers_dict[code] = brokers_dict.get(code, {"net_lot": 0, "net_val": 0, "avg_price": 0})
                brokers_dict[code]["net_lot"] += _parse(s.get("slot") or 0) # usually negative
                brokers_dict[code]["net_val"] += _parse(s.get("sval") or 0) # usually negative
                # if broker was primarily a seller, overwrite avg_price
                if brokers_dict[code]["net_lot"] < 0:
                    brokers_dict[code]["avg_price"] = _parse(s.get("netbs_sell_avg_price"))

            # Calculate retail vs big money
            retail_val = 0
            big_money_val = 0
            
            for code, data in brokers_dict.items():
                val = data["net_val"]
                if code in retail_brokers:
                    retail_val += val
                else:
                    big_money_val += val
                    
                result["broker_tx"].append({
                    "symbol": ticker,
                    "date": today,
                    "broker_code": code,
                    "net_lot": data["net_lot"],
                    "net_val": data["net_val"],
                    "avg_price": data["avg_price"]
                })

            result["metrics"]["retail_net_val"] = retail_val
            result["metrics"]["big_money_net_val"] = big_money_val
            
        except Exception as e:
            print(f"[flow] Fetch Bandarmologi Error: {e}")

        time.sleep(config.REQUEST_DELAY)
        
        # 2. Fetch Foreign Flow
        try:
            res_f = client.get(ff_url)
            res_f.raise_for_status()
            f_data = res_f.json().get("data", {}).get("summary", {})
            net_f = _parse(f_data.get("net_foreign", {}).get("value", {}).get("raw") or 0)
            result["metrics"]["foreign_net_val"] = net_f
        except Exception as e:
            print(f"[flow] Fetch Foreign Flow Error: {e}")
            
    return result
