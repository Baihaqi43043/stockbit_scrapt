"""
Valuation Engine — Buffett Style

Kalkulasi:
1. Revenue CAGR (5 & 10 tahun)
2. EPS CAGR (5 & 10 tahun)
3. Owner Earnings = Net Income + D&A - CapEx
4. Graham Number = sqrt(22.5 × EPS × BVPS)
5. DCF (Discounted Cash Flow) → Intrinsic Value per saham
6. Margin of Safety = (Intrinsic - Price) / Intrinsic × 100%
"""

import math
from typing import Optional


# ──────────────────────────────────────────────────────────────────────
# 1. CAGR
# ──────────────────────────────────────────────────────────────────────

def calc_cagr(start_value: float, end_value: float, years: int) -> Optional[float]:
    """
    CAGR = (end/start)^(1/years) - 1
    Return None jika start <= 0 atau end <= 0 (tidak bisa hitung CAGR negatif ke positif).
    """
    if years <= 0 or start_value is None or end_value is None:
        return None
    if start_value <= 0 or end_value <= 0:
        return None
    try:
        return ((end_value / start_value) ** (1.0 / years) - 1) * 100
    except (ZeroDivisionError, ValueError):
        return None


def calc_revenue_cagr(historical_rows: list, years: int = 5) -> Optional[float]:
    """
    Hitung Revenue CAGR dari data kuartalan.
    Pakai Annual (sum Q1+Q2+Q3+Q4) per tahun.
    """
    annual = _annual_sum(historical_rows, "revenue")
    return _cagr_from_annual(annual, years)


def calc_eps_cagr(historical_rows: list, years: int = 5) -> Optional[float]:
    """
    Hitung EPS CAGR dari data kuartalan.
    Pakai sum EPS per tahun (TTM-style).
    """
    annual = _annual_sum(historical_rows, "eps")
    return _cagr_from_annual(annual, years)


def _annual_sum(rows: list, field: str) -> dict:
    """Aggregate quarterly rows jadi annual sum: {year: total}"""
    totals = {}
    for row in rows:
        if row.get("quarter", 0) == 0:
            continue
        val = row.get(field)
        if val is None:
            continue
        year = int(row["year"])
        totals[year] = totals.get(year, 0.0) + float(val)
    return totals


def _cagr_from_annual(annual: dict, years: int) -> Optional[float]:
    sorted_years = sorted(annual.keys())
    if len(sorted_years) < 2:
        return None
    latest_year = sorted_years[-1]
    target_year = latest_year - years
    # Cari tahun terdekat dengan target
    base_year = min(sorted_years, key=lambda y: abs(y - target_year))
    if base_year == latest_year:
        return None
    actual_years = latest_year - base_year
    return calc_cagr(annual[base_year], annual[latest_year], actual_years)


# ──────────────────────────────────────────────────────────────────────
# 2. Average ROE dari historical EPS + BVPS
# ──────────────────────────────────────────────────────────────────────

def calc_avg_roe(historical_rows: list, bvps: float, years: int = 5) -> Optional[float]:
    """
    Approximasi Average ROE menggunakan annual EPS / BVPS.
    (Kurang akurat karena BVPS hanya current, tapi cukup untuk screening)
    """
    if not bvps or bvps <= 0:
        return None
    annual_eps = _annual_sum(historical_rows, "eps")
    sorted_years = sorted(annual_eps.keys(), reverse=True)[:years]
    if not sorted_years:
        return None
    roe_list = [(annual_eps[y] / bvps) * 100 for y in sorted_years if annual_eps[y] is not None]
    return sum(roe_list) / len(roe_list) if roe_list else None


# ──────────────────────────────────────────────────────────────────────
# 3. Owner Earnings
# ──────────────────────────────────────────────────────────────────────

def calc_owner_earnings(
    net_income_ttm: Optional[float],
    da_ttm: Optional[float],
    capex_ttm: Optional[float],
) -> Optional[float]:
    """
    Owner Earnings (Buffett) = Net Income + D&A - CapEx
    Semua dalam miliar IDR.
    D&A sering tidak tersedia langsung → approximasi dari EBITDA - EBIT kalau ada.
    """
    if net_income_ttm is None:
        return None
    da    = da_ttm or 0.0
    capex = abs(capex_ttm) if capex_ttm is not None else 0.0
    return net_income_ttm + da - capex


def estimate_da(ebitda_ttm: Optional[float], ev_ebit: Optional[float],
                ev_ebitda: Optional[float]) -> Optional[float]:
    """
    Estimasi D&A dari: EBITDA - EBIT
    Kita tidak punya EBIT langsung, tapi bisa approx dari EV/EBIT dan EV/EBITDA.
    D&A ≈ EBITDA × (1 - EV_EBIT/EV_EBITDA) — hanya jika kedua rasio ada.
    """
    if ebitda_ttm and ev_ebit and ev_ebitda and ev_ebitda != 0:
        try:
            ratio = ev_ebit / ev_ebitda
            return ebitda_ttm * (1 - ratio)
        except (ZeroDivisionError, TypeError):
            pass
    return None


# ──────────────────────────────────────────────────────────────────────
# 4. Graham Number
# ──────────────────────────────────────────────────────────────────────

def calc_graham_number(eps: Optional[float], bvps: Optional[float]) -> Optional[float]:
    """
    Graham Number = sqrt(22.5 × EPS × BVPS)
    Hanya valid jika EPS > 0 dan BVPS > 0.
    """
    if eps is None or bvps is None or eps <= 0 or bvps <= 0:
        return None
    try:
        return math.sqrt(22.5 * eps * bvps)
    except ValueError:
        return None


# ──────────────────────────────────────────────────────────────────────
# 5. DCF — Discounted Cash Flow
# ──────────────────────────────────────────────────────────────────────

def calc_dcf(
    owner_earnings_per_share: float,
    growth_rate_pct: float,
    discount_rate_pct: float = 10.0,
    terminal_growth_pct: float = 3.0,
    projection_years: int = 10,
) -> Optional[float]:
    """
    Two-stage DCF:
    Stage 1: FCF tumbuh dengan growth_rate selama projection_years
    Stage 2: Terminal value dengan terminal_growth setelahnya

    Return: Intrinsic Value per saham (dalam IDR)

    Catatan: owner_earnings_per_share dalam IDR
    """
    if owner_earnings_per_share is None or owner_earnings_per_share <= 0:
        return None
    if discount_rate_pct <= terminal_growth_pct:
        return None

    try:
        g  = growth_rate_pct / 100
        r  = discount_rate_pct / 100
        tg = terminal_growth_pct / 100

        # Stage 1: PV of projected cash flows
        pv_stage1 = 0.0
        cf = owner_earnings_per_share
        for t in range(1, projection_years + 1):
            cf *= (1 + g)
            pv_stage1 += cf / ((1 + r) ** t)

        # Stage 2: Terminal value (Gordon Growth Model)
        terminal_cf = cf * (1 + tg)
        terminal_value = terminal_cf / (r - tg)
        pv_terminal = terminal_value / ((1 + r) ** projection_years)

        return pv_stage1 + pv_terminal
    except (ZeroDivisionError, ValueError, OverflowError):
        return None


# ──────────────────────────────────────────────────────────────────────
# 6. Sloan Ratio — Earnings Quality
# ──────────────────────────────────────────────────────────────────────

def calc_sloan_ratio(
    net_income_ttm: Optional[float],
    cfo_ttm: Optional[float],
    total_assets: Optional[float],
) -> Optional[float]:
    """
    Sloan Ratio = (Net Income - CFO) / Total Assets

    Interpretasi:
      < -10% : Laba jauh lebih rendah dari kas masuk → konservatif, bagus
      -10% s/d 10% : Normal
      > 10%  : Laba berasal dari akrual (piutang dll), bukan kas → RED FLAG

    Buffett suka perusahaan dengan Sloan Ratio rendah (laba = kas nyata).
    """
    if net_income_ttm is None or cfo_ttm is None or not total_assets or total_assets == 0:
        return None
    try:
        return ((float(net_income_ttm) - float(cfo_ttm)) / float(total_assets)) * 100
    except (ZeroDivisionError, TypeError):
        return None


# ──────────────────────────────────────────────────────────────────────
# 7. Retention Ratio & Incremental ROE
# ──────────────────────────────────────────────────────────────────────

def calc_retention_ratio(payout_ratio_pct: Optional[float]) -> Optional[float]:
    """
    Retention Ratio = 1 - Payout Ratio
    Jika payout_ratio NULL (tidak bagi dividen), return 100% (semua laba ditahan).
    """
    if payout_ratio_pct is None:
        return 100.0   # tidak bagi dividen = 100% ditahan
    return max(0.0, 100.0 - float(payout_ratio_pct))


def calc_incremental_roe(historical_rows: list) -> Optional[float]:
    """
    Incremental ROE = ΔNet Income / Retained Earnings (estimasi dari laba ditahan kumulatif)

    Karena kita tidak punya historical equity, kita approximasi:
    Retained Earnings ≈ kumulatif net income tahun-tahun sebelumnya (kasar).

    Return: % — seberapa efisien perusahaan menginvestasikan laba yang ditahan.
    Buffett standard: > 15%.
    """
    annual_ni = _annual_sum(historical_rows, "net_income")
    years = sorted(annual_ni.keys())
    if len(years) < 3:
        return None

    # Ambil 5 tahun terakhir kalau ada
    recent = years[-5:] if len(years) >= 5 else years

    incremental_roes = []
    for i in range(1, len(recent)):
        prev_year = recent[i - 1]
        curr_year = recent[i]
        delta_ni         = annual_ni[curr_year] - annual_ni[prev_year]
        retained_earnings = annual_ni[prev_year]  # proxy: laba tahun lalu
        if retained_earnings and retained_earnings > 0:
            incremental_roes.append((delta_ni / retained_earnings) * 100)

    return sum(incremental_roes) / len(incremental_roes) if incremental_roes else None


# ──────────────────────────────────────────────────────────────────────
# 8. Margin of Safety
# ──────────────────────────────────────────────────────────────────────

def calc_margin_of_safety(intrinsic_value: float, current_price: float) -> Optional[float]:
    """
    MoS = (Intrinsic - Price) / Intrinsic × 100%
    Positif = saham diskon, Negatif = saham mahal.
    """
    if not intrinsic_value or intrinsic_value <= 0 or not current_price:
        return None
    return ((intrinsic_value - current_price) / intrinsic_value) * 100


# ──────────────────────────────────────────────────────────────────────
# 7. Master: run all valuations
# ──────────────────────────────────────────────────────────────────────

def run_valuation(fundamental: dict, historical_rows: list, current_price: float) -> dict:
    """
    Jalankan semua kalkulasi valuasi dari fundamental snapshot + historical data.
    Return dict siap simpan ke valuation_results.
    """
    def _f(key):
        v = fundamental.get(key)
        return float(v) if v is not None else None

    eps_annual  = _f("eps_annual")
    bvps        = _f("bvps")
    net_income  = _f("net_income_ttm")
    capex       = _f("capex_ttm")
    ebitda      = _f("ebitda_ttm")
    ev_ebit     = _f("ev_ebit")
    ev_ebitda   = _f("ev_ebitda")
    _mktcap = fundamental.get("market_cap")
    shares  = float(_mktcap) / current_price if _mktcap and current_price else None

    # D&A estimation
    da = estimate_da(ebitda, ev_ebit, ev_ebitda)

    # Owner Earnings (total, miliar IDR)
    oe_total = calc_owner_earnings(net_income, da, capex)

    # Owner Earnings per share
    oe_per_share = None
    if oe_total is not None and shares and shares > 0:
        # shares dalam miliar (market_cap dalam miliar IDR / price)
        # net_income dalam miliar IDR, shares dalam miliar lembar
        oe_per_share = (oe_total / shares) * 1_000_000_000 / 1_000_000_000
        # Sebenarnya: oe_per_share = oe_total (B IDR) / shares (B lembar) = IDR per lembar
        oe_per_share = oe_total / shares if shares else None

    # CAGR
    rev_cagr_5  = calc_revenue_cagr(historical_rows, 5)
    rev_cagr_10 = calc_revenue_cagr(historical_rows, 10)
    eps_cagr_5  = calc_eps_cagr(historical_rows, 5)
    eps_cagr_10 = calc_eps_cagr(historical_rows, 10)

    # Graham Number
    graham = calc_graham_number(eps_annual, bvps)

    # DCF growth rate: pakai rata-rata rev_cagr dan eps_cagr, atau fallback 5%
    valid_cagrs = [c for c in [rev_cagr_5, eps_cagr_5] if c is not None and c > 0]
    growth_rate = min(sum(valid_cagrs) / len(valid_cagrs), 15.0) if valid_cagrs else 5.0

    # DCF
    dcf_value = None
    if oe_per_share and oe_per_share > 0:
        dcf_value = calc_dcf(
            owner_earnings_per_share=oe_per_share,
            growth_rate_pct=growth_rate,
            discount_rate_pct=10.0,
            terminal_growth_pct=3.0,
            projection_years=10,
        )

    # Pilih intrinsic value: DCF utama, Graham sebagai fallback
    intrinsic = dcf_value or graham

    # Margin of Safety
    mos = calc_margin_of_safety(intrinsic, current_price) if intrinsic else None

    # Sloan Ratio
    sloan = calc_sloan_ratio(
        net_income_ttm=_f("net_income_ttm"),
        cfo_ttm=_f("cfo_ttm"),
        total_assets=_f("total_assets"),
    )

    # Retention Ratio
    retention = calc_retention_ratio(_f("payout_ratio"))

    # Incremental ROE
    inc_roe = calc_incremental_roe(historical_rows)

    return {
        "current_price":    current_price,
        "revenue_cagr_5y":  rev_cagr_5,
        "revenue_cagr_10y": rev_cagr_10,
        "eps_cagr_5y":      eps_cagr_5,
        "eps_cagr_10y":     eps_cagr_10,
        "owner_earnings":   oe_total,
        "dcf_intrinsic":    dcf_value,
        "dcf_growth_rate":  growth_rate,
        "dcf_discount_rate":10.0,
        "margin_of_safety": mos,
        "graham_number":    graham,
        "sloan_ratio":      sloan,
        "retention_ratio":  retention,
        "incremental_roe":  inc_roe,
        "_da_estimate":     da,
        "_oe_per_share":    oe_per_share,
    }
