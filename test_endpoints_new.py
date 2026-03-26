import httpx
import json
import time

def snippet(data, length=300):
    s = str(data)
    return s if len(s) <= length else s[:length] + "..."

def main():
    token_file = r"E:\xampp\htdocs\stockbit_scrapt\.token_cache.json"
    with open(token_file, "r") as f:
        token = json.loads(f.read())["access_token"]
        
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Origin": "https://stockbit.com",
        "Referer": "https://stockbit.com/"
    }

    urls = [
        "https://exodus.stockbit.com/order-trade/running-trade?sort=DESC&limit=50&order_by=RUNNING_TRADE_ORDER_BY_TIME&symbols%5B%5D=ADRO",
        "https://exodus.stockbit.com/marketdetectors/ADRO?transaction_type=TRANSACTION_TYPE_NET&market_board=MARKET_BOARD_REGULER&investor_type=INVESTOR_TYPE_ALL&limit=25",
        "https://exodus.stockbit.com/findata-view/foreign-domestic/v1/chart-data/ADRO?market_type=MARKET_TYPE_REGULAR&period=PERIOD_RANGE_1D",
        "https://exodus.stockbit.com/order-trade/running-trade/chart/ADRO?period=RT_PERIOD_LAST_1_DAY&investor_type=INVESTOR_TYPE_ALL&market_board=BOARD_TYPE_REGULAR",
        "https://exodus.stockbit.com/order-trade/trade-book/chart?symbol=ADRO&time_interval=1m"
    ]

    with httpx.Client(headers=headers, timeout=15) as client:
        for i, url in enumerate(urls, 1):
            print(f"[{i}] Testing: {url}")
            try:
                res = client.get(url)
                print(f"    Status: {res.status_code}")
                try:
                    data = res.json()
                    keys = list(data.keys())
                    print(f"    Keys: {keys}")
                    # Pretty print the first chunk of data
                    # Let's drill down into 'data' if it exists
                    if "data" in data:
                        print(f"    Data snippet: {snippet(data['data'])}")
                    elif "response" in data:
                        print(f"    Data snippet: {snippet(data['response'])}")
                    else:
                        print(f"    Data snippet: {snippet(data)}")
                except json.JSONDecodeError:
                    print(f"    Text snippet: {snippet(res.text)}")
            except Exception as e:
                print(f"    Error: {e}")
            print("-" * 70)
            time.sleep(1)

if __name__ == "__main__":
    main()
