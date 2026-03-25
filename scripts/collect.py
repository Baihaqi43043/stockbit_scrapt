"""
Entry point: jalankan collector untuk semua ticker di config.

Usage:
    python scripts/collect.py              # collect semua ticker
    python scripts/collect.py BUMI         # collect satu ticker
    python scripts/collect.py BUMI --price-only
    python scripts/collect.py BUMI --fundamental-only
"""

import sys
import os

# Pastikan root project ada di path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from src.collector.fundamental import fetch_fundamental
from src.collector.price import fetch_price
from src.database.repository import upsert_ticker, save_fundamental, save_price


def collect(ticker: str, do_fundamental: bool = True, do_price: bool = True):
    print(f"\n{'='*50}")
    print(f"[collect] Ticker: {ticker}")
    print(f"{'='*50}")

    upsert_ticker(ticker)

    if do_fundamental:
        print(f"[collect] Fetching fundamental data...")
        try:
            data = fetch_fundamental(ticker)
            save_fundamental(ticker, data)
            print(f"[collect] Fundamental saved.")
            print(f"          P/E      : {data.get('pe_ratio')}")
            print(f"          P/B      : {data.get('pb_ratio')}")
            print(f"          EPS TTM  : {data.get('eps_ttm')}")
            print(f"          ROE      : {data.get('roe')}")
            print(f"          DER      : {data.get('der')}")
            print(f"          Net Mgn  : {data.get('net_margin')}")
            print(f"          Rev YoY  : {data.get('revenue_yoy')}")
            print(f"          NI YoY   : {data.get('net_income_yoy')}")
            print(f"          Piotroski: {data.get('piotroski_score')}")
        except Exception as e:
            print(f"[collect] ERROR fundamental: {e}")

    if do_price:
        print(f"[collect] Fetching price data...")
        try:
            data = fetch_price(ticker)
            save_price(ticker, data)
            print(f"[collect] Price saved.")
            print(f"          Last     : {data.get('last_price')}")
            print(f"          Change % : {data.get('change_pct')}")
            print(f"          52wk High: {data.get('week52_high')}")
            print(f"          52wk Low : {data.get('week52_low')}")
        except Exception as e:
            print(f"[collect] ERROR price: {e}")


def main():
    args = sys.argv[1:]

    # Parse flags
    price_only       = "--price-only"       in args
    fundamental_only = "--fundamental-only" in args
    args = [a for a in args if not a.startswith("--")]

    do_fundamental = not price_only
    do_price       = not fundamental_only

    tickers = args if args else config.TICKERS

    print(f"[collect] Tickers: {tickers}")
    print(f"[collect] Fundamental: {do_fundamental} | Price: {do_price}")

    for ticker in tickers:
        collect(ticker.upper(), do_fundamental=do_fundamental, do_price=do_price)

    print(f"\n[collect] Selesai.")


if __name__ == "__main__":
    main()
