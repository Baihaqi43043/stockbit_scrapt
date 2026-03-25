from datetime import datetime
from typing import Optional
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
    """Simpan snapshot fundamental lengkap ke DB."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO fundamental_data (
                symbol, fetched_at,
                -- Section 0: Valuation
                pe_ratio, pe_annual, forward_pe, ihsg_pe_ttm, earnings_yield,
                ps_ratio, pb_ratio, price_to_cashflow, price_to_fcf,
                ev_ebit, ev_ebitda, peg, peg_3yr, peg_forward,
                -- Section 1: Per Share
                eps_ttm, eps_annual, revenue_per_share, cash_per_share, bvps, fcf_per_share,
                -- Section 2: Solvency
                current_ratio, quick_ratio, der, lt_debt_equity, total_liab_equity,
                debt_to_assets, financial_leverage, interest_coverage, fcf_quarter, altman_z_score,
                -- Section 3: Management Effectiveness
                roa, roe, roce, roic,
                days_sales_out, days_inventory, days_payables, cash_conv_cycle,
                receivables_turn, asset_turnover, inventory_turnover,
                -- Section 4: Profitability
                gross_margin, op_margin, net_margin,
                -- Section 5: Growth
                revenue_yoy, gross_profit_yoy, net_income_yoy, revenue_qoq, net_income_qoq,
                -- Section 6: Dividend
                dividend_amount, dividend_ttm, payout_ratio, dividend_yield, dividend_ex_date,
                -- Section 7: Market Rank
                piotroski_score, eps_rating, relative_strength,
                rank_market_cap, rank_pe_ttm, rank_earnings_yld, rank_ps, rank_pb, rank_near_52wk_high,
                -- Section 8: Income Statement
                revenue_ttm, gross_profit_ttm, ebitda_ttm, net_income_ttm,
                -- Section 9: Balance Sheet
                cash_bs, total_assets, total_liabilities, working_capital,
                common_equity, lt_debt, st_debt, total_debt, net_debt, total_equity,
                -- Section 10: Cash Flow
                cfo_ttm, cfi_ttm, cff_ttm, capex_ttm, fcf_ttm,
                -- Section 11: Price Performance
                return_1w, return_1m, return_3m, return_6m, return_1y,
                return_3y, return_5y, return_10y, return_ytd,
                -- Market stats
                market_cap, enterprise_value,
                raw_json
            ) VALUES (
                %(symbol)s, %(fetched_at)s,
                %(pe_ratio)s, %(pe_annual)s, %(forward_pe)s, %(ihsg_pe_ttm)s, %(earnings_yield)s,
                %(ps_ratio)s, %(pb_ratio)s, %(price_to_cashflow)s, %(price_to_fcf)s,
                %(ev_ebit)s, %(ev_ebitda)s, %(peg)s, %(peg_3yr)s, %(peg_forward)s,
                %(eps_ttm)s, %(eps_annual)s, %(revenue_per_share)s, %(cash_per_share)s, %(bvps)s, %(fcf_per_share)s,
                %(current_ratio)s, %(quick_ratio)s, %(der)s, %(lt_debt_equity)s, %(total_liab_equity)s,
                %(debt_to_assets)s, %(financial_leverage)s, %(interest_coverage)s, %(fcf_quarter)s, %(altman_z_score)s,
                %(roa)s, %(roe)s, %(roce)s, %(roic)s,
                %(days_sales_out)s, %(days_inventory)s, %(days_payables)s, %(cash_conv_cycle)s,
                %(receivables_turn)s, %(asset_turnover)s, %(inventory_turnover)s,
                %(gross_margin)s, %(op_margin)s, %(net_margin)s,
                %(revenue_yoy)s, %(gross_profit_yoy)s, %(net_income_yoy)s, %(revenue_qoq)s, %(net_income_qoq)s,
                %(dividend_amount)s, %(dividend_ttm)s, %(payout_ratio)s, %(dividend_yield)s, %(dividend_ex_date)s,
                %(piotroski_score)s, %(eps_rating)s, %(relative_strength)s,
                %(rank_market_cap)s, %(rank_pe_ttm)s, %(rank_earnings_yld)s, %(rank_ps)s, %(rank_pb)s, %(rank_near_52wk_high)s,
                %(revenue_ttm)s, %(gross_profit_ttm)s, %(ebitda_ttm)s, %(net_income_ttm)s,
                %(cash_bs)s, %(total_assets)s, %(total_liabilities)s, %(working_capital)s,
                %(common_equity)s, %(lt_debt)s, %(st_debt)s, %(total_debt)s, %(net_debt)s, %(total_equity)s,
                %(cfo_ttm)s, %(cfi_ttm)s, %(cff_ttm)s, %(capex_ttm)s, %(fcf_ttm)s,
                %(return_1w)s, %(return_1m)s, %(return_3m)s, %(return_6m)s, %(return_1y)s,
                %(return_3y)s, %(return_5y)s, %(return_10y)s, %(return_ytd)s,
                %(market_cap)s, %(enterprise_value)s,
                %(raw_json)s
            )
            """,
            {**data, "symbol": symbol, "fetched_at": datetime.now()},
        )
        conn.commit()
    finally:
        conn.close()


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


def get_latest_fundamental(symbol: str) -> Optional[dict]:
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


def get_historical_rows(symbol: str) -> list:
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT year, quarter, revenue, net_income, eps FROM historical_quarterly "
            "WHERE symbol = %s ORDER BY year, quarter",
            (symbol,),
        )
        return cur.fetchall()
    finally:
        conn.close()


def save_valuation(symbol: str, data: dict):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO valuation_results (
                symbol, calculated_at, current_price,
                revenue_cagr_5y, revenue_cagr_10y, eps_cagr_5y, eps_cagr_10y,
                owner_earnings, dcf_intrinsic, dcf_growth_rate, dcf_discount_rate,
                margin_of_safety, graham_number,
                sloan_ratio, retention_ratio, incremental_roe,
                buffett_score, verdict, notes
            ) VALUES (
                %(symbol)s, %(calculated_at)s, %(current_price)s,
                %(revenue_cagr_5y)s, %(revenue_cagr_10y)s, %(eps_cagr_5y)s, %(eps_cagr_10y)s,
                %(owner_earnings)s, %(dcf_intrinsic)s, %(dcf_growth_rate)s, %(dcf_discount_rate)s,
                %(margin_of_safety)s, %(graham_number)s,
                %(sloan_ratio)s, %(retention_ratio)s, %(incremental_roe)s,
                %(buffett_score)s, %(verdict)s, %(notes)s
            )
            """,
            {**data, "symbol": symbol},
        )
        conn.commit()
    finally:
        conn.close()
