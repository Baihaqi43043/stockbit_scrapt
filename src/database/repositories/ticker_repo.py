from src.database.connection import get_connection

def upsert_ticker(symbol: str, company_name: str = None, sector: str = None, industry: str = None):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO tickers (symbol, company_name, sector, industry)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                company_name = COALESCE(VALUES(company_name), company_name),
                sector       = COALESCE(VALUES(sector), sector),
                industry     = COALESCE(VALUES(industry), industry)
            """,
            (symbol, company_name, sector, industry),
        )
        conn.commit()
    finally:
        conn.close()

def get_ticker_info(symbol: str):
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM tickers WHERE symbol = %s", (symbol,))
        return cur.fetchone()
    finally:
        conn.close()
