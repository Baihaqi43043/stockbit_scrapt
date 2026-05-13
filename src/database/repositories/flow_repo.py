from src.database.connection import get_connection

def save_flow_tracker(ticker: str, data: dict, price_data: dict = None):
    conn = get_connection()
    try:
        cur = conn.cursor()
        
        # 1. Stock Daily Metrics
        metrics = data.get("metrics")
        if metrics:
            if price_data:
                metrics["close_price"] = price_data.get("close_price") or 0
                metrics["volume"] = price_data.get("volume") or 0
                metrics["change_pct"] = price_data.get("change_pct", metrics.get("change_pct"))
                
            cur.execute(
                """
                INSERT INTO stock_daily_metrics (
                    symbol, date, close_price, change_pct, volume, foreign_net_val, retail_net_val, big_money_net_val, accdist_status
                ) VALUES (
                    %(symbol)s, %(date)s, %(close_price)s, %(change_pct)s, %(volume)s, %(foreign_net_val)s, %(retail_net_val)s, %(big_money_net_val)s, %(accdist_status)s
                )
                ON DUPLICATE KEY UPDATE
                    close_price = VALUES(close_price),
                    change_pct = VALUES(change_pct),
                    volume = VALUES(volume),
                    foreign_net_val = VALUES(foreign_net_val),
                    retail_net_val = VALUES(retail_net_val),
                    big_money_net_val = VALUES(big_money_net_val),
                    accdist_status = VALUES(accdist_status)
                """,
                metrics
            )
            
        # 2. Broker Transaction Daily (Batch Insert)
        broker_tx = data.get("broker_tx", [])
        if broker_tx and len(broker_tx) > 0:
            date_val = broker_tx[0]["date"]
            cur.execute("DELETE FROM broker_transaction_daily WHERE symbol = %s AND date = %s", (ticker, date_val))
            
            insert_query = """
                INSERT INTO broker_transaction_daily (
                    symbol, date, broker_code, net_lot, net_val, avg_price, freq
                ) VALUES (
                    %(symbol)s, %(date)s, %(broker_code)s, %(net_lot)s, %(net_val)s, %(avg_price)s, %(freq)s
                )
            """
            cur.executemany(insert_query, broker_tx)
            
        conn.commit()
    finally:
        conn.close()

def get_broker_master():
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM broker_master")
        return cur.fetchall()
    finally:
        conn.close()
