"""
Collector untuk data fundamental dari endpoint:
GET https://exodus.stockbit.com/keystats/ratio/v1/{TICKER}?year_limit=3

closure_fin_items_results index mapping:
  0  = Valuation
  1  = Per Share
  2  = Solvency
  3  = Management Effectiveness
  4  = Profitability
  5  = Growth
  6  = Dividend
  7  = Market Rank
  8  = Income Statement
  9  = Balance Sheet
  10 = Cash Flow
  11 = Price Performance
"""

import time
from typing import Optional
import httpx
import config
from src.auth import get_valid_token


KEYSTATS_URL = f"{config.BASE_URL}/keystats/ratio/v1/{{ticker}}?year_limit=3"


def _parse_value(val) -> Optional[float]:
    """
    Ubah string angka ke float.
    Handle: '15.10%', '(422 B)', '23,880 B', '-0.64%', '-'
    """
    if val is None:
        return None
    s = str(val).strip()
    if s in ("", "-", "N/A"):
        return None
    # Format negatif akuntansi: (422 B) → -422
    negative = s.startswith("(") and s.endswith(")")
    if negative:
        s = s[1:-1]
    s = s.replace(",", "").replace("%", "").replace(" B", "").replace(" T", "").strip()
    try:
        result = float(s)
        return -result if negative else result
    except (ValueError, TypeError):
        return None


def _parse_str(val) -> Optional[str]:
    """Return string value, None kalau kosong/dash."""
    if val is None:
        return None
    s = str(val).strip()
    return s if s not in ("", "-") else None


def _find_val(items: list, keyword: str) -> Optional[float]:
    """Cari float value dari list berdasarkan nama (case-insensitive partial match)."""
    kw = keyword.lower()
    for entry in items:
        fitem = entry.get("fitem", {})
        if kw in fitem.get("name", "").lower():
            return _parse_value(fitem.get("value"))
    return None


def _find_str(items: list, keyword: str) -> Optional[str]:
    """Cari string value dari list."""
    kw = keyword.lower()
    for entry in items:
        fitem = entry.get("fitem", {})
        if kw in fitem.get("name", "").lower():
            return _parse_str(fitem.get("value"))
    return None


def _sec(sections: list, index: int) -> list:
    """Ambil fin_name_results dari section index tertentu."""
    try:
        return sections[index].get("fin_name_results", [])
    except (IndexError, AttributeError):
        return []


def fetch_fundamental(ticker: str) -> dict:
    """
    Fetch dan parse semua data fundamental untuk satu ticker.
    Return dict siap simpan ke tabel fundamental_data.
    """
    token   = get_valid_token()
    headers = {**config.DEFAULT_HEADERS, "Authorization": f"Bearer {token}"}
    url     = KEYSTATS_URL.format(ticker=ticker)

    with httpx.Client(headers=headers, timeout=30) as client:
        resp = client.get(url)

    if resp.status_code == 401:
        from src.auth import login_via_browser
        token = login_via_browser()["access_token"]
        headers["Authorization"] = f"Bearer {token}"
        with httpx.Client(headers=headers, timeout=30) as client:
            resp = client.get(url)

    resp.raise_for_status()
    body = resp.json()
    raw  = resp.text

    data_root = body.get("data", {})
    stats     = data_root.get("stats", {})
    sections  = data_root.get("closure_fin_items_results", [])

    s0  = _sec(sections, 0)   # Valuation
    s1  = _sec(sections, 1)   # Per Share
    s2  = _sec(sections, 2)   # Solvency
    s3  = _sec(sections, 3)   # Management Effectiveness
    s4  = _sec(sections, 4)   # Profitability
    s5  = _sec(sections, 5)   # Growth
    s6  = _sec(sections, 6)   # Dividend
    s7  = _sec(sections, 7)   # Market Rank
    s8  = _sec(sections, 8)   # Income Statement
    s9  = _sec(sections, 9)   # Balance Sheet
    s10 = _sec(sections, 10)  # Cash Flow
    s11 = _sec(sections, 11)  # Price Performance

    result = {
        # ── Section 0: Valuation ─────────────────────────────────────
        "pe_ratio":          _find_val(s0, "current pe ratio (ttm)"),
        "pe_annual":         _find_val(s0, "current pe ratio (annualised)"),
        "forward_pe":        _find_val(s0, "forward pe ratio"),
        "ihsg_pe_ttm":       _find_val(s0, "ihsg pe ratio"),
        "earnings_yield":    _find_val(s0, "earnings yield"),
        "ps_ratio":          _find_val(s0, "current price to sales"),
        "pb_ratio":          _find_val(s0, "current price to book value"),
        "price_to_cashflow": _find_val(s0, "current price to cashflow"),
        "price_to_fcf":      _find_val(s0, "current price to free cashflow"),
        "ev_ebit":           _find_val(s0, "ev to ebit (ttm)"),
        "ev_ebitda":         _find_val(s0, "ev to ebitda"),
        "peg":               _find_val(s0, "peg ratio"),
        "peg_3yr":           _find_val(s0, "peg ratio (3yr)"),
        "peg_forward":       _find_val(s0, "peg (forward)"),

        # ── Section 1: Per Share ──────────────────────────────────────
        "eps_ttm":           _find_val(s1, "current eps (ttm)"),
        "eps_annual":        _find_val(s1, "current eps (annualised)"),
        "revenue_per_share": _find_val(s1, "revenue per share"),
        "cash_per_share":    _find_val(s1, "cash per share"),
        "bvps":              _find_val(s1, "current book value per share"),
        "fcf_per_share":     _find_val(s1, "free cashflow per share"),

        # ── Section 2: Solvency ───────────────────────────────────────
        "current_ratio":     _find_val(s2, "current ratio"),
        "quick_ratio":       _find_val(s2, "quick ratio"),
        "der":               _find_val(s2, "debt to equity ratio"),
        "lt_debt_equity":    _find_val(s2, "lt debt/equity"),
        "total_liab_equity": _find_val(s2, "total liabilities/equity"),
        "debt_to_assets":    _find_val(s2, "total debt/total assets"),
        "financial_leverage":_find_val(s2, "financial leverage"),
        "interest_coverage": _find_val(s2, "interest coverage"),
        "fcf_quarter":       _find_val(s2, "free cash flow (quarter)"),
        "altman_z_score":    _find_val(s2, "altman z-score"),

        # ── Section 3: Management Effectiveness ──────────────────────
        "roa":               _find_val(s3, "return on assets"),
        "roe":               _find_val(s3, "return on equity"),
        "roce":              _find_val(s3, "return on capital employed"),
        "roic":              _find_val(s3, "return on invested capital"),
        "days_sales_out":    _find_val(s3, "days sales outstanding"),
        "days_inventory":    _find_val(s3, "days inventory"),
        "days_payables":     _find_val(s3, "days payables outstanding"),
        "cash_conv_cycle":   _find_val(s3, "cash conversion cycle"),
        "receivables_turn":  _find_val(s3, "receivables turnover"),
        "asset_turnover":    _find_val(s3, "asset turnover"),
        "inventory_turnover":_find_val(s3, "inventory turnover"),

        # ── Section 4: Profitability ──────────────────────────────────
        "gross_margin":      _find_val(s4, "gross profit margin"),
        "op_margin":         _find_val(s4, "operating profit margin"),
        "net_margin":        _find_val(s4, "net profit margin"),

        # ── Section 5: Growth ─────────────────────────────────────────
        "revenue_yoy":       _find_val(s5, "revenue (quarter yoy growth)"),
        "gross_profit_yoy":  _find_val(s5, "gross profit (quarter yoy growth)"),
        "net_income_yoy":    _find_val(s5, "net income (quarter yoy growth)"),
        "revenue_qoq":       None,
        "net_income_qoq":    None,

        # ── Section 6: Dividend ───────────────────────────────────────
        "dividend_amount":   _find_val(s6, "dividend"),
        "dividend_ttm":      _find_val(s6, "dividend (ttm)"),
        "payout_ratio":      _find_val(s6, "payout ratio"),
        "dividend_yield":    _find_val(s6, "dividend yield"),
        "dividend_ex_date":  _find_str(s6, "latest dividend ex-date"),

        # ── Section 7: Market Rank ────────────────────────────────────
        "piotroski_score":   _find_val(s7, "piotroski f-score"),
        "eps_rating":        _find_val(s7, "eps rating"),
        "relative_strength": _find_val(s7, "relative strength rating"),
        "rank_market_cap":   _find_val(s7, "rank (market cap)"),
        "rank_pe_ttm":       _find_val(s7, "rank (current pe ratio ttm)"),
        "rank_earnings_yld": _find_val(s7, "rank (earnings yield)"),
        "rank_ps":           _find_val(s7, "rank (p/s)"),
        "rank_pb":           _find_val(s7, "rank (p/b)"),
        "rank_near_52wk_high":_find_val(s7, "rank (near 52 weeks high)"),

        # ── Section 8: Income Statement (miliar IDR) ──────────────────
        "revenue_ttm":       _find_val(s8, "revenue (ttm)"),
        "gross_profit_ttm":  _find_val(s8, "gross profit (ttm)"),
        "ebitda_ttm":        _find_val(s8, "ebitda (ttm)"),
        "net_income_ttm":    _find_val(s8, "net income (ttm)"),

        # ── Section 9: Balance Sheet (miliar IDR) ─────────────────────
        "cash_bs":           _find_val(s9, "cash (quarter)"),
        "total_assets":      _find_val(s9, "total assets"),
        "total_liabilities": _find_val(s9, "total liabilities"),
        "working_capital":   _find_val(s9, "working capital"),
        "common_equity":     _find_val(s9, "common equity"),
        "lt_debt":           _find_val(s9, "long-term debt"),
        "st_debt":           _find_val(s9, "short-term debt"),
        "total_debt":        _find_val(s9, "total debt"),
        "net_debt":          _find_val(s9, "net debt"),
        "total_equity":      _find_val(s9, "total equity"),

        # ── Section 10: Cash Flow (miliar IDR) ────────────────────────
        "cfo_ttm":           _find_val(s10, "cash from operations"),
        "cfi_ttm":           _find_val(s10, "cash from investing"),
        "cff_ttm":           _find_val(s10, "cash from financing"),
        "capex_ttm":         _find_val(s10, "capital expenditure"),
        "fcf_ttm":           _find_val(s10, "free cash flow (ttm)"),

        # ── Section 11: Price Performance (%) ────────────────────────
        "return_1w":         _find_val(s11, "1 week price returns"),
        "return_1m":         _find_val(s11, "1 month price returns"),
        "return_3m":         _find_val(s11, "3 month price returns"),
        "return_6m":         _find_val(s11, "6 month price returns"),
        "return_1y":         _find_val(s11, "1 year price returns"),
        "return_3y":         _find_val(s11, "3 year price returns"),
        "return_5y":         _find_val(s11, "5 year price returns"),
        "return_10y":        _find_val(s11, "10 year price returns"),
        "return_ytd":        _find_val(s11, "year to date price returns"),

        # ── Stats (dari root data) ────────────────────────────────────
        "market_cap":        _parse_value(stats.get("market_cap")),
        "enterprise_value":  _parse_value(stats.get("enterprise_value")),

        "raw_json": raw,
    }

    time.sleep(config.REQUEST_DELAY)
    return result
