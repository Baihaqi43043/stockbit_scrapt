import httpx
import json
import sys
import os

# Add current directory to path so we can import config and auth
sys.path.insert(0, os.getcwd())

import config
from src.auth import get_valid_token

def test_price_response(ticker):
    token = get_valid_token()
    headers = {**config.DEFAULT_HEADERS, "Authorization": f"Bearer {token}"}
    url = f"{config.BASE_URL}/company-price-feed/v2/orderbook/companies/{ticker}"
    
    with httpx.Client(headers=headers, timeout=30) as client:
        resp = client.get(url)
    
    print(json.dumps(resp.json(), indent=2))

if __name__ == "__main__":
    test_price_response("BBCA")
