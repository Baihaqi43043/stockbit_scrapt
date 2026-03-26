import httpx
import json

def main():
    token_file = r"E:\xampp\htdocs\stockbit_scrapt\.token_cache.json"
    with open(token_file, "r") as f:
        token = json.loads(f.read())["access_token"]
        
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "Mozilla/5.0",
        "Origin": "https://stockbit.com"
    }

    url_bandar = "https://exodus.stockbit.com/marketdetectors/ADRO?transaction_type=TRANSACTION_TYPE_NET&market_board=MARKET_BOARD_REGULER&investor_type=INVESTOR_TYPE_ALL&limit=25"

    with httpx.Client(headers=headers, timeout=15) as client:
        res = client.get(url_bandar)
        with open("bandar_full.json", "w") as out:
            json.dump(res.json(), out, indent=2)
            
        res2 = client.get("https://exodus.stockbit.com/order-trade/trade-book/chart?symbol=ADRO&time_interval=1m")
        with open("tradebook_full.json", "w") as out:
            json.dump(res2.json(), out, indent=2)

if __name__ == "__main__":
    main()
