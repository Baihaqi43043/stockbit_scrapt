import sys
import os

# Add src to path
sys.path.insert(0, os.getcwd())

def test_imports():
    print("Testing imports...")
    try:
        from src.database.repository import upsert_ticker, save_fundamental
        from src.engines.fundamental import calculate_graham_number
        from src.engines.flow import calculate_absorption_pct
        from src.collector.profile import fetch_company_profile
        print("✓ All imports successful!")
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False
    return True

def test_db_connection():
    print("Testing DB connection...")
    try:
        from src.database.connection import get_connection
        conn = get_connection()
        conn.close()
        print("✓ DB connection successful!")
    except Exception as e:
        print(f"✗ DB connection error: {e}")
        return False
    return True

if __name__ == "__main__":
    if test_imports() and test_db_connection():
        print("\nReady to run!")
    else:
        sys.exit(1)
