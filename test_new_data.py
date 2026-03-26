import httpx
import json
import time
from datetime import datetime, timedelta

def main():
    token_file = r"E:\xampp\htdocs\stockbit_scrapt\.token_cache.json"
    with open(token_file, "r") as f:
        token = json.loads(f.read())["access_token"]
        
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "Mozilla/5.0",
        "Origin": "https://stockbit.com"
    }

    ticker = "ADRO"
    test_date = "2026-03-26"  # Tanggal kemarin yang ada perdagangannya
    
    print(f"--- 1. Testing freq di Broker Summary ({test_date}) ---")
    bndr_url = f"https://exodus.stockbit.com/marketdetectors/{ticker}?transaction_type=TRANSACTION_TYPE_NET&market_board=MARKET_BOARD_REGULER&investor_type=INVESTOR_TYPE_ALL&limit=25&from={test_date}&to={test_date}"
    
    with httpx.Client(headers=headers, timeout=15) as client:
        res = client.get(bndr_url)
        data = res.json().get("data", {}).get("broker_summary", {})
        
        buys = data.get("brokers_buy", [])
        if buys:
            print(f"Ditemukan {len(buys)} broker buy.")
            print(f"Contoh Broker Buy pertama: {buys[0].get('netbs_broker_code')}")
            print(f"  - Net Lot : {buys[0].get('blot')}")
            print(f"  - Net Val : {buys[0].get('bval')}")
            print(f"  - Freq    : {buys[0].get('freq')}")
        else:
            print("Tidak ada data broker buy untuk tanggal tersebut.")
            
        print("\n--- 2. Testing Harga Historis (Chart API) ---")
        # Mengubah target date ke Unix Timestamp
        target_dt = datetime.strptime(test_date, "%Y-%m-%d")
        # Tarik data rentang 5 hari agar dapat prev_close
        start_dt = target_dt - timedelta(days=5)
        
        from_ts = int(start_dt.timestamp())
        to_ts = int(target_dt.timestamp()) + 86400 # +1 hari
        
        # Endpoint standard tradingview stockbit
        chart_url = f"https://exodus.stockbit.com/chart/history?symbol={ticker}&resolution=D&from={from_ts}&to={to_ts}"
        
        try:
            res2 = client.get(chart_url)
            cdata = res2.json()
            print("Status Code:", res2.status_code)
            if cdata.get("s") == "ok":
                print(f"Berhasil mendapat data chart!")
                print(f"Timestamps: {cdata.get('t')}")
                print(f"Close Price: {cdata.get('c')}")
                # Menghitung change_pct hari terakhir
                closes = cdata.get('c')
                if len(closes) >= 2:
                    last_c = closes[-1]
                    prev_c = closes[-2]
                    change_pct = ((last_c - prev_c) / prev_c) * 100
                    print(f"Close: {last_c}, Prev Close: {prev_c}, Change: {change_pct:.2f}%")
            else:
                print(f"Response Error: {cdata}")
        except Exception as e:
            print(f"Request Error: {e}")

if __name__ == "__main__":
    main()
