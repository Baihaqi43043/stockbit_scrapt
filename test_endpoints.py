import httpx
import json
import time

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
    base_url = "https://exodus.stockbit.com"

    endpoints_to_test = [
        # Try to find exactly what the broker summary endpoint is.
        # Commonly it's /chart/broker-summary/... or /company-data/...
        ("/v3/broker-summary/BBCA?start_date=2024-01-01&end_date=2024-01-02&type=all", "GET"),
        ("/chart/broker-summary/BBCA", "GET"),
        ("/saham/broker-summary/BBCA", "GET"),
        ("/bandarmologi/broker-summary/v1/BBCA", "GET"),
        ("/company/BBCA/broker-summary", "GET"),
        ("/chart/foreign/v1/BBCA", "GET"),
        ("/company-price-feed/v2/orderbook/companies/BBCA", "GET") # We know this one works
    ]

    with httpx.Client(headers=headers, timeout=10) as client:
        for ep, meth in endpoints_to_test:
            print(f"Testing {meth} {ep}")
            try:
                res = client.request(meth, base_url + ep)
                print(f"Status: {res.status_code}")
                # Print first 200 chars of response
                print(f"Data: {res.text[:200]}")
            except Exception as e:
                print(f"Error: {e}")
            print("-" * 50)
            time.sleep(1)

if __name__ == "__main__":
    main()
