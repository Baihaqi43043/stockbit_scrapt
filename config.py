import os
from dotenv import load_dotenv

load_dotenv()

# Stockbit
STOCKBIT_USERNAME   = os.getenv("STOCKBIT_USERNAME", "")
STOCKBIT_PASSWORD   = os.getenv("STOCKBIT_PASSWORD", "")
STOCKBIT_PLAYER_ID  = os.getenv("STOCKBIT_PLAYER_ID", "")

# Base URLs
BASE_URL    = "https://exodus.stockbit.com"
LOGIN_URL   = f"{BASE_URL}/login/v6/username"
REFRESH_URL = f"{BASE_URL}/login/refresh"

# Database
DB_HOST     = os.getenv("DB_HOST", "localhost")
DB_PORT     = int(os.getenv("DB_PORT", 3306))
DB_NAME     = os.getenv("DB_NAME", "stockbit_data")
DB_USER     = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# Tickers
TICKERS = [t.strip() for t in os.getenv("TICKERS", "BUMI").split(",")]

# Request settings
REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", 0.5))

# Request headers (imitasi browser)
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "X-DeviceType": "Google Chrome",
    "X-Platform":   "PC",
    "X-AppVersion": "3.17.2",
    "Content-Type": "application/json",
    "Accept":       "application/json",
    "Accept-Language": "id-ID,id;q=0.9",
    "Origin":       "https://stockbit.com",
    "Referer":      "https://stockbit.com/",
}
