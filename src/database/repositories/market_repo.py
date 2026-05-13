from datetime import datetime
from src.database.connection import get_connection

def save_price(symbol: str, data: dict):
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

def save_news(symbol: str, news_list: list):
    if not news_list: return
    conn = get_connection()
    try:
        cur = conn.cursor()
        for n in news_list:
            cur.execute(
                """
                INSERT INTO news (symbol, news_id, title, summary, url, image_url, published_at, source)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE title=VALUES(title)
                """,
                (symbol, n["news_id"], n["title"], n["summary"], n["url"], n["image_url"], n["published_at"], n["source"])
            )
        conn.commit()
    finally:
        conn.close()

def save_dividend(symbol: str, div_list: list):
    if not div_list: return
    conn = get_connection()
    try:
        cur = conn.cursor()
        for d in div_list:
            cur.execute(
                """
                INSERT INTO dividend_history (symbol, year, dps, ex_date, payment_date, div_type)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE dps=VALUES(dps)
                """,
                (symbol, d["year"], d["dps"], d["ex_date"], d["payment_date"], d["div_type"])
            )
        conn.commit()
    finally:
        conn.close()
