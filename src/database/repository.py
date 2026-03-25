from datetime import datetime
from src.database.connection import get_connection


def upsert_ticker(symbol: str, company_name: str = None, sector: str = None):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO tickers (symbol, company_name, sector)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                company_name = COALESCE(VALUES(company_name), company_name),
                sector       = COALESCE(VALUES(sector), sector)
            """,
            (symbol, company_name, sector),
        )
        conn.commit()
    finally:
        conn.close()


def save_fundamental(symbol: str, data: dict):
    """Simpan satu baris snapshot fundamental."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO fundamental_data (
                symbol, fetched_at,
                pe_ratio, pe_annual, forward_pe, pb_ratio, ps_ratio, ev_ebitda, peg,
                eps_ttm, eps_annual, bvps, revenue_per_share,
                current_ratio, der, debt_to_assets,
                gross_margin, op_margin, net_margin,
                roe, roa, roic,
                revenue_qoq, revenue_yoy, net_income_qoq, net_income_yoy,
                dividend_yield, payout_ratio,
                market_cap, enterprise_value, piotroski_score,
                raw_json
            ) VALUES (
                %(symbol)s, %(fetched_at)s,
                %(pe_ratio)s, %(pe_annual)s, %(forward_pe)s, %(pb_ratio)s, %(ps_ratio)s, %(ev_ebitda)s, %(peg)s,
                %(eps_ttm)s, %(eps_annual)s, %(bvps)s, %(revenue_per_share)s,
                %(current_ratio)s, %(der)s, %(debt_to_assets)s,
                %(gross_margin)s, %(op_margin)s, %(net_margin)s,
                %(roe)s, %(roa)s, %(roic)s,
                %(revenue_qoq)s, %(revenue_yoy)s, %(net_income_qoq)s, %(net_income_yoy)s,
                %(dividend_yield)s, %(payout_ratio)s,
                %(market_cap)s, %(enterprise_value)s, %(piotroski_score)s,
                %(raw_json)s
            )
            """,
            {**data, "symbol": symbol, "fetched_at": datetime.now()},
        )
        conn.commit()
    finally:
        conn.close()


def save_price(symbol: str, data: dict):
    """Simpan satu baris snapshot harga."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO price_data (
                symbol, fetched_at,
                last_price, open_price, high_price, low_price, close_price,
                volume, frequency, change_val, change_pct,
                week52_high, week52_low
            ) VALUES (
                %(symbol)s, %(fetched_at)s,
                %(last_price)s, %(open_price)s, %(high_price)s, %(low_price)s, %(close_price)s,
                %(volume)s, %(frequency)s, %(change_val)s, %(change_pct)s,
                %(week52_high)s, %(week52_low)s
            )
            """,
            {**data, "symbol": symbol, "fetched_at": datetime.now()},
        )
        conn.commit()
    finally:
        conn.close()


def get_latest_fundamental(symbol: str) -> dict | None:
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT * FROM fundamental_data WHERE symbol = %s ORDER BY fetched_at DESC LIMIT 1",
            (symbol,),
        )
        return cur.fetchone()
    finally:
        conn.close()
