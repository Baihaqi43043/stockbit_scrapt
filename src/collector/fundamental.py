"""
Collector untuk data fundamental dari endpoint:
GET https://exodus.stockbit.com/keystats/ratio/v1/{TICKER}?year_limit=10

closure_fin_items_results index mapping:
  0 = Valuation
  1 = Per Share
  2 = Solvency
  3 = Management Effectiveness
  4 = Profitability
  5 = Growth
  6 = Dividend
  7 = Market Rank (Piotroski dll)
  8 = Income Statement
  9 = Balance Sheet
  10= Cash Flow
  11= Price Performance (52wk high/low)
"""

import json
import time
import httpx
import config
from src.auth import get_valid_token


KEYSTATS_URL = f"{config.BASE_URL}/keystats/ratio/v1/{{ticker}}?year_limit=10"


def _parse_value(val) -> float | None:
    """Ubah string angka ke float, return None kalau tidak bisa."""
    if val is None:
        return None
    try:
        cleaned = str(val).replace(",", "").replace("%", "").strip()
        return float(cleaned) if cleaned not in ("", "-", "N/A") else None
    except (ValueError, TypeError):
        return None


def _find_item(fin_name_results: list, keyword: str) -> float | None:
    """Cari nilai dari list berdasarkan nama (case-insensitive partial match)."""
    keyword_lower = keyword.lower()
    for entry in fin_name_results:
        fitem = entry.get("fitem", {})
        name  = fitem.get("name", "").lower()
        if keyword_lower in name:
            return _parse_value(fitem.get("value"))
    return None


def _extract_section(sections: list, index: int) -> list:
    """Ambil fin_name_results dari index tertentu dengan aman."""
    try:
        return sections[index].get("fin_name_results", [])
    except (IndexError, AttributeError):
        return []


def fetch_fundamental(ticker: str) -> dict:
    """
    Fetch dan parse data fundamental untuk satu ticker.
    Return dict siap simpan ke tabel fundamental_data.
    """
    token = get_valid_token()
    headers = {**config.DEFAULT_HEADERS, "Authorization": f"Bearer {token}"}
    url = KEYSTATS_URL.format(ticker=ticker)

    with httpx.Client(headers=headers, timeout=30) as client:
        resp = client.get(url)

    if resp.status_code == 401:
        # Token expired di tengah jalan, force refresh
        from src.auth import login
        token = login()["access_token"]
        headers["Authorization"] = f"Bearer {token}"
        with httpx.Client(headers=headers, timeout=30) as client:
            resp = client.get(url)

    resp.raise_for_status()
    body = resp.json()
    raw  = resp.text

    data_root = body.get("data", {})
    stats     = data_root.get("stats", {})
    sections  = data_root.get("closure_fin_items_results", [])

    valuation   = _extract_section(sections, 0)
    per_share   = _extract_section(sections, 1)
    solvency    = _extract_section(sections, 2)
    mgmt_eff    = _extract_section(sections, 3)
    profitab    = _extract_section(sections, 4)
    growth      = _extract_section(sections, 5)
    dividend    = _extract_section(sections, 6)
    mkt_rank    = _extract_section(sections, 7)

    result = {
        # Valuation
        "pe_ratio":     _find_item(valuation, "p/e ratio (ttm)") or _find_item(valuation, "p/e"),
        "pe_annual":    _find_item(valuation, "p/e annual"),
        "forward_pe":   _find_item(valuation, "forward p/e"),
        "pb_ratio":     _find_item(valuation, "p/b"),
        "ps_ratio":     _find_item(valuation, "p/s"),
        "ev_ebitda":    _find_item(valuation, "ev/ebitda"),
        "peg":          _find_item(valuation, "peg"),

        # Per Share
        "eps_ttm":            _find_item(per_share, "eps ttm"),
        "eps_annual":         _find_item(per_share, "eps annuali"),
        "bvps":               _find_item(per_share, "book value"),
        "revenue_per_share":  _find_item(per_share, "revenue/share"),

        # Solvency
        "current_ratio":  _find_item(solvency, "current ratio"),
        "der":            _find_item(solvency, "debt to equity") or _find_item(solvency, "d/e"),
        "debt_to_assets": _find_item(solvency, "debt/assets"),

        # Profitability
        "gross_margin": _find_item(profitab, "gross margin"),
        "op_margin":    _find_item(profitab, "operating margin"),
        "net_margin":   _find_item(profitab, "net margin"),

        # Management Effectiveness
        "roe":  _find_item(mgmt_eff, "roe"),
        "roa":  _find_item(mgmt_eff, "roa"),
        "roic": _find_item(mgmt_eff, "roic"),

        # Growth
        "revenue_qoq":    _find_item(growth, "revenue qoq"),
        "revenue_yoy":    _find_item(growth, "revenue yoy"),
        "net_income_qoq": _find_item(growth, "net income qoq"),
        "net_income_yoy": _find_item(growth, "net income yoy"),

        # Dividend
        "dividend_yield": _find_item(dividend, "yield"),
        "payout_ratio":   _find_item(dividend, "payout"),

        # Market
        "market_cap":       _parse_value(stats.get("market_cap")),
        "enterprise_value": _parse_value(stats.get("enterprise_value")),

        # Piotroski
        "piotroski_score": _find_item(mkt_rank, "piotroski"),

        "raw_json": raw,
    }

    time.sleep(config.REQUEST_DELAY)
    return result
