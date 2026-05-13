import httpx
import time
import config
from src.auth import get_valid_token

INFO_URL = f"{config.BASE_URL}/findata-view/info/v1/{{ticker}}"

def fetch_company_profile(ticker: str) -> dict:
    """
    Mengambil profil perusahaan (Sektor, Industri, Deskripsi).
    """
    token = get_valid_token()
    headers = {**config.DEFAULT_HEADERS, "Authorization": f"Bearer {token}"}
    url = INFO_URL.format(ticker=ticker)
    
    with httpx.Client(headers=headers, timeout=30) as client:
        resp = client.get(url)
    
    if resp.status_code != 200:
        return {}
        
    data = resp.json().get("data", {})
    return {
        "sector": data.get("sector"),
        "industry": data.get("industry"),
        "sub_industry": data.get("sub_industry"),
        "description": data.get("description"),
        "company_name": data.get("name")
    }
