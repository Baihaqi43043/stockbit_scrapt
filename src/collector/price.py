"""
Collector harga real-time dari endpoint:
GET https://exodus.stockbit.com/company-price-feed/v2/orderbook/companies/{TICKER}

Data 52-week high/low diambil dari keystats section index 11 (Price Performance).
"""

import time
import httpx
import config
from src.auth import get_valid_token


PRICE_URL = f"{config.BASE_URL}/company-price-feed/v2/orderbook/companies/{{ticker}}"
KEYSTATS_URL = f"{config.BASE_URL}/keystats/ratio/v1/{{ticker}}?year_limit=1"


def _parse(val) -> float | None:
    if val is None:
        return None
    try:
        return float(str(val).replace(",", "").strip())
    except (ValueError, TypeError):
        return None


def _find_item(fin_name_results: list, keyword: str) -> float | None:
    keyword_lower = keyword.lower()
    for entry in fin_name_results:
        fitem = entry.get("fitem", {})
        name  = fitem.get("name", "").lower()
        if keyword_lower in name:
            try:
                return float(str(fitem.get("value", "")).replace(",", "").strip())
            except (ValueError, TypeError):
                return None
    return None


def fetch_price(ticker: str) -> dict:
    """
    Fetch snapshot harga + 52-week high/low untuk satu ticker.
    Return dict siap simpan ke tabel price_data.
    """
    token   = get_valid_token()
    headers = {**config.DEFAULT_HEADERS, "Authorization": f"Bearer {token}"}

    # --- Harga real-time ---
    url  = PRICE_URL.format(ticker=ticker)
    with httpx.Client(headers=headers, timeout=30) as client:
        resp = client.get(url)
    resp.raise_for_status()
    ob = resp.json().get("data", {})

    result = {
        "last_price":  _parse(ob.get("lastprice")),
        "open_price":  _parse(ob.get("open")),
        "high_price":  _parse(ob.get("high")),
        "low_price":   _parse(ob.get("low")),
        "close_price": _parse(ob.get("close") or ob.get("previousclose")),
        "volume":      _parse(ob.get("volume")),
        "frequency":   _parse(ob.get("frequency")),
        "change_val":  _parse(ob.get("change")),
        "change_pct":  _parse(ob.get("percentage_change")),
        "week52_high": None,
        "week52_low":  None,
    }

    time.sleep(config.REQUEST_DELAY)

    # --- 52-week high/low dari keystats price performance (section index 11) ---
    try:
        ks_url = KEYSTATS_URL.format(ticker=ticker)
        with httpx.Client(headers=headers, timeout=30) as client:
            ks_resp = client.get(ks_url)
        ks_resp.raise_for_status()
        sections = ks_resp.json().get("data", {}).get("closure_fin_items_results", [])
        price_perf = sections[11].get("fin_name_results", []) if len(sections) > 11 else []
        result["week52_high"] = _find_item(price_perf, "52-week high") or _find_item(price_perf, "52 week high")
        result["week52_low"]  = _find_item(price_perf, "52-week low")  or _find_item(price_perf, "52 week low")
    except Exception:
        pass  # 52wk data opsional, tidak fatal

    time.sleep(config.REQUEST_DELAY)
    return result
