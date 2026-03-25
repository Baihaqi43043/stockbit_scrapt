"""
Collector historical quarterly data (10 tahun) dari keystats.

financial_year_parent.financial_year_groups:
  Group 0 = Net Income per kuartal (miliar IDR)
  Group 1 = EPS per kuartal
  Group 2 = Revenue per kuartal (miliar IDR)
"""

import time
from typing import Optional
import httpx
import config
from src.auth import get_valid_token
from src.database.connection import get_connection

KEYSTATS_URL = f"{config.BASE_URL}/keystats/ratio/v1/{{ticker}}?year_limit=10"

QUARTER_MAP = {"Q1": 1, "Q2": 2, "Q3": 3, "Q4": 4, "FY": 0}


def _parse(val) -> Optional[float]:
    if val is None:
        return None
    s = str(val).strip()
    if s in ("", "-", "N/A"):
        return None
    negative = s.startswith("(") and s.endswith(")")
    if negative:
        s = s[1:-1]
    s = s.replace(",", "").replace(" B", "").replace(" T", "").strip()
    try:
        result = float(s)
        return -result if negative else result
    except (ValueError, TypeError):
        return None


def _parse_group(groups: list, index: int) -> dict:
    """
    Parse satu group jadi dict: {(year, quarter): value}
    """
    result = {}
    try:
        group = groups[index]
    except IndexError:
        return result

    for yv in group.get("financial_year_values", []):
        year = int(yv.get("year", 0))
        for pv in yv.get("period_values", []):
            period  = pv.get("period", "")
            quarter = QUARTER_MAP.get(period, None)
            if quarter is None:
                continue
            val = _parse(pv.get("quarter_value"))
            result[(year, quarter)] = val

    return result


def fetch_historical(ticker: str) -> list[dict]:
    """
    Fetch historical quarterly data untuk satu ticker.
    Return list of dicts siap simpan ke historical_quarterly.
    """
    token   = get_valid_token()
    headers = {**config.DEFAULT_HEADERS, "Authorization": f"Bearer {token}"}
    url     = KEYSTATS_URL.format(ticker=ticker)

    with httpx.Client(headers=headers, timeout=30) as client:
        resp = client.get(url)
    resp.raise_for_status()

    groups = resp.json().get("data", {}).get("financial_year_parent", {}).get("financial_year_groups", [])

    net_income_map = _parse_group(groups, 0)
    eps_map        = _parse_group(groups, 1)
    revenue_map    = _parse_group(groups, 2)

    # Gabungkan semua (year, quarter) yang ada
    all_keys = set(net_income_map) | set(eps_map) | set(revenue_map)

    rows = []
    for (year, quarter) in sorted(all_keys):
        rows.append({
            "year":       year,
            "quarter":    quarter,
            "revenue":    revenue_map.get((year, quarter)),
            "net_income": net_income_map.get((year, quarter)),
            "eps":        eps_map.get((year, quarter)),
        })

    time.sleep(config.REQUEST_DELAY)
    return rows


def save_historical(symbol: str, rows: list[dict]):
    """Simpan/update historical quarterly ke DB."""
    if not rows:
        return
    conn = get_connection()
    try:
        cur = conn.cursor()
        for row in rows:
            cur.execute(
                """
                INSERT INTO historical_quarterly (symbol, year, quarter, revenue, net_income, eps)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    revenue    = VALUES(revenue),
                    net_income = VALUES(net_income),
                    eps        = VALUES(eps),
                    fetched_at = CURRENT_TIMESTAMP
                """,
                (symbol, row["year"], row["quarter"],
                 row["revenue"], row["net_income"], row["eps"]),
            )
        conn.commit()
        print(f"[historical] {len(rows)} rows saved untuk {symbol}.")
    finally:
        conn.close()
