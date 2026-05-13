import mysql.connector
import json

def find_industry():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="stockbit_data"
        )
        cur = conn.cursor()
        cur.execute("SELECT raw_json FROM fundamental_data WHERE symbol = 'BBCA' LIMIT 1")
        row = cur.fetchone()
        if not row:
            print("No data found for BBCA")
            return
            
        data = json.loads(row[0])
        
        # Look for sector/industry in the root or stats
        keys = data.keys()
        print(f"Root keys: {list(keys)}")
        
        data_inner = data.get("data", {})
        print(f"Data inner keys: {list(data_inner.keys())}")
        
        if "info" in data_inner:
            print(f"Info: {data_inner['info']}")
            
        # Search for common sector names
        text = row[0].lower()
        if "bank" in text: print("Found 'bank'")
        if "finance" in text: print("Found 'finance'")
        if "industry" in text: print("Found 'industry'")
        if "sector" in text: print("Found 'sector'")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_industry()
