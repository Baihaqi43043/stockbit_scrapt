import httpx
import json

def snippet(data, length=300):
    s = str(data)
    return s if len(s) <= length else s[:length] + "..."

def main():
    token_file = r"E:\xampp\htdocs\stockbit_scrapt\.token_cache.json"
    token = json.loads(open(token_file).read())["access_token"]
        
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "Mozilla/5.0",
        "Origin": "https://stockbit.com"
    }

    urls = [
        "https://exodus.stockbit.com/marketdetectors/ADRO?transaction_type=TRANSACTION_TYPE_NET&market_board=MARKET_BOARD_REGULER&investor_type=INVESTOR_TYPE_ALL&limit=25&from=2026-03-20&to=2026-03-20",
        "https://exodus.stockbit.com/marketdetectors/ADRO?transaction_type=TRANSACTION_TYPE_NET&market_board=MARKET_BOARD_REGULER&investor_type=INVESTOR_TYPE_ALL&limit=25&date_start=2026-03-20&date_end=2026-03-20",
        "https://exodus.stockbit.com/findata-view/foreign-domestic/v1/chart-data/ADRO?market_type=MARKET_TYPE_REGULAR&period=PERIOD_RANGE_1D&from=2026-03-20&to=2026-03-20"
    ]

    with httpx.Client(headers=headers, timeout=15) as client:
        for url in urls:
            print("URL:", url.split("?")[0], url.split("?")[1][-40:])
            res = client.get(url)
            print("Status:", res.status_code)
            try:
                data = res.json()
                if "data" in data and isinstance(data["data"], dict) and "from" in data["data"]:
                    print("Returned Date:", data["data"]["from"], "-", data["data"]["to"])
                elif "data" in data and isinstance(data["data"], dict) and "summary" in data["data"]:
                    print("Returned Date Range:", data["data"]["summary"].get("date_range"))
                else:
                    print("Snippet:", snippet(data))
            except:
                pass
            print("-")

if __name__ == "__main__":
    main()
