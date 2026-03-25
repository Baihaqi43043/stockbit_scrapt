"""
Collector dividend history dari keystats.

Data ada di: data.dividend_group.dividend_year_values
Format: [{period, dividend, ex_date, payment_date}, ...]

Bisa ada multiple dividen per tahun (interim + final).
"""

import time
from typing import Optional
import httpx
import config
from src.auth import get_valid_token
from src.database.connection import get_connection

KEYSTATS_URL = f"{config.BASE_URL}/keystats/ratio/v1/{{ticker}}?year_limit=3"


def _parse_float(val) -> Optional[float]:
    if val is None:
        return None
    s = str(val).strip()
    if s in ("", "-", "N/A"):
        return None
    try:
        return float(s.replace(",", ""))
    except (ValueError, TypeError):
        return None


def _parse_date(val: str) -> Optional[str]:
    """
    Parse tanggal Stockbit seperti '25 Nov 25' atau '28 May 25' → 'YYYY-MM-DD'.
    """
    if not val or str(val).strip() in ("", "-"):
        return None
    months = {
        "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
        "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
    }
    parts = str(val).strip().split()
    if len(parts) == 3:
        try:
            day   = int(parts[0])
            month = months.get(parts[1], 0)
            yr    = int(parts[2])
            year  = 2000 + yr if yr < 100 else yr
            if month:
                return f"{year:04d}-{month:02d}-{day:02d}"
        except (ValueError, IndexError):
            pass
    return None


def fetch_dividend(ticker: str) -> list:
    """
    Fetch dividend history untuk satu ticker dari keystats dividend_group.
    Return list of dicts: {year, dps, ex_date, payment_date, div_type}
    """
    token   = get_valid_token()
    headers = {**config.DEFAULT_HEADERS, "Authorization": f"Bearer {token}"}
    url     = KEYSTATS_URL.format(ticker=ticker)

    with httpx.Client(headers=headers, timeout=30) as client:
        resp = client.get(url)
    resp.raise_for_status()

    div_group = resp.json().get("data", {}).get("dividend_group", {})
    items     = div_group.get("dividend_year_values", [])

    rows = []
    for item in items:
        year     = item.get("period")
        dps      = _parse_float(item.get("dividend"))
        ex_date  = _parse_date(item.get("ex_date"))
        pay_date = _parse_date(item.get("payment_date"))

        if not year:
            continue

        # Tentukan tipe: kalau 2 data dalam tahun sama → interim + final
        # (akan di-handle di aggregasi sisi DB — kita simpan per event)
        rows.append({
            "year":         int(year),
            "dps":          dps,
            "ex_date":      ex_date,
            "payment_date": pay_date,
            "div_type":     "annual",   # di-update saat save kalau ada duplikat
        })

    # Tandai interim/final kalau ada 2+ event dalam tahun yang sama
    year_counts = {}
    for r in rows:
        year_counts[r["year"]] = year_counts.get(r["year"], 0) + 1

    for r in rows:
        if year_counts[r["year"]] > 1:
            r["div_type"] = "interim/final"

    time.sleep(config.REQUEST_DELAY)
    print(f"[dividend] {len(rows)} event dividen untuk {ticker}")
    return rows


def save_dividend(symbol: str, rows: list):
    """
    Simpan dividend history ke DB.
    Kalau 1 tahun punya 2 event (interim+final), simpan total DPS per tahun.
    """
    if not rows:
        return

    # Agregasi per tahun: sum DPS, ambil ex_date terbaru
    from collections import defaultdict
    annual = defaultdict(lambda: {"dps": 0.0, "ex_date": None, "payment_date": None, "div_type": "annual"})
    for r in rows:
        y = r["year"]
        annual[y]["dps"] += r["dps"] or 0.0
        # Simpan ex_date yang paling awal (first dividen of year)
        if r["ex_date"] and (annual[y]["ex_date"] is None or r["ex_date"] < annual[y]["ex_date"]):
            annual[y]["ex_date"] = r["ex_date"]
        if r["payment_date"]:
            annual[y]["payment_date"] = r["payment_date"]
        if r["div_type"] != "annual":
            annual[y]["div_type"] = r["div_type"]

    conn = get_connection()
    try:
        cur = conn.cursor()
        for year, data in annual.items():
            cur.execute(
                """
                INSERT INTO dividend_history (symbol, year, dps, ex_date, payment_date, div_type)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    dps          = VALUES(dps),
                    ex_date      = COALESCE(VALUES(ex_date), ex_date),
                    payment_date = COALESCE(VALUES(payment_date), payment_date),
                    div_type     = VALUES(div_type),
                    fetched_at   = CURRENT_TIMESTAMP
                """,
                (symbol, year, data["dps"] or None,
                 data["ex_date"], data["payment_date"], data["div_type"]),
            )
        conn.commit()
        print(f"[dividend] {len(annual)} tahun dividen tersimpan untuk {symbol}.")
    finally:
        conn.close()


def get_dividend_rows(symbol: str) -> list:
    """Ambil dividend history dari DB (desc by year)."""
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT year, dps, ex_date, payment_date, div_type "
            "FROM dividend_history WHERE symbol = %s ORDER BY year DESC",
            (symbol,),
        )
        return cur.fetchall()
    finally:
        conn.close()
