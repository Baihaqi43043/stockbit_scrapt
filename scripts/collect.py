"""
Entry point: jalankan collector untuk semua ticker di config.

Usage:
    python scripts/collect.py              # collect + analyze semua ticker
    python scripts/collect.py BUMI         # collect satu ticker
    python scripts/collect.py BUMI --price-only
    python scripts/collect.py BUMI --fundamental-only
    python scripts/collect.py BUMI --no-analyze
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from src.collector.fundamental  import fetch_fundamental
from src.collector.price        import fetch_price
from src.collector.historical   import fetch_historical, save_historical
from src.database.repository    import upsert_ticker, save_fundamental, save_price, save_valuation
from src.database.repository    import get_latest_fundamental, get_historical_rows
from src.analyzer.valuation     import run_valuation
from src.analyzer.checklist     import run_checklist, print_checklist


def collect(ticker: str, do_fundamental=True, do_price=True, do_analyze=True):
    print(f"\n{'='*55}")
    print(f" {ticker}")
    print(f"{'='*55}")

    upsert_ticker(ticker)

    fundamental_data = None
    price_data       = None

    if do_fundamental:
        print("[collect] Fetching fundamental + historical...")
        try:
            fundamental_data = fetch_fundamental(ticker)
            save_fundamental(ticker, fundamental_data)

            hist_rows = fetch_historical(ticker)
            save_historical(ticker, hist_rows)

            print(f"  P/E: {fundamental_data.get('pe_ratio')}  "
                  f"P/B: {fundamental_data.get('pb_ratio')}  "
                  f"ROE: {fundamental_data.get('roe')}%  "
                  f"DER: {fundamental_data.get('der')}  "
                  f"Net Mgn: {fundamental_data.get('net_margin')}%")
        except Exception as e:
            print(f"[collect] ERROR fundamental: {e}")

    if do_price:
        print("[collect] Fetching price...")
        try:
            price_data = fetch_price(ticker)
            save_price(ticker, price_data)
            if price_data.get("company_name"):
                upsert_ticker(ticker, company_name=price_data["company_name"])
            print(f"  {price_data.get('company_name')} | "
                  f"Rp {price_data.get('last_price'):,.0f} "
                  f"({price_data.get('change_pct'):+.2f}%) | "
                  f"52wk: {price_data.get('week52_low')}–{price_data.get('week52_high')}")
        except Exception as e:
            print(f"[collect] ERROR price: {e}")

    if do_analyze:
        print("[analyze] Running Buffett valuation...")
        try:
            fund  = fundamental_data or get_latest_fundamental(ticker)
            price = price_data.get("last_price") if price_data else None

            if not fund or not price:
                print("[analyze] Data tidak cukup untuk analisis.")
                return

            hist  = get_historical_rows(ticker)
            val   = run_valuation(fund, hist, price)
            check = run_checklist(fund, val, price)

            # Gabungkan, strip key non-DB, lalu simpan
            DB_KEYS = {
                "current_price", "revenue_cagr_5y", "revenue_cagr_10y",
                "eps_cagr_5y", "eps_cagr_10y", "owner_earnings",
                "dcf_intrinsic", "dcf_growth_rate", "dcf_discount_rate",
                "margin_of_safety", "graham_number",
                "sloan_ratio", "retention_ratio", "incremental_roe",
                "buffett_score", "verdict", "notes", "calculated_at",
            }
            result = {k: v for k, v in {**val, **check, "calculated_at": datetime.now()}.items() if k in DB_KEYS}
            save_valuation(ticker, result)

            print_checklist(ticker, check, val, price)

        except Exception as e:
            print(f"[analyze] ERROR: {e}")
            import traceback; traceback.print_exc()


def main():
    args = sys.argv[1:]

    price_only       = "--price-only"       in args
    fundamental_only = "--fundamental-only" in args
    no_analyze       = "--no-analyze"       in args
    args = [a for a in args if not a.startswith("--")]

    do_fundamental = not price_only
    do_price       = not fundamental_only
    do_analyze     = not no_analyze and not price_only

    tickers = args if args else config.TICKERS
    print(f"Tickers: {tickers} | fundamental={do_fundamental} price={do_price} analyze={do_analyze}")

    for ticker in tickers:
        collect(ticker.upper(), do_fundamental, do_price, do_analyze)

    print("\n[collect] Selesai.")


if __name__ == "__main__":
    main()
