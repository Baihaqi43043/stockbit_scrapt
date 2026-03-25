"""
Buffett-Style Checklist Scorer

Setiap kriteria diberi poin 0 atau 1.
Total skor 0-10 → verdict:
  8-10 = DEEP_VALUE
  6-7  = WATCH
  4-5  = FAIR
  0-3  = AVOID
"""

from typing import Optional


CRITERIA = [
    # (key, label, check_fn)
    # ── Moat & Profitability ─────────────────────────────────────────
    ("net_margin",      "Net Margin > 10%",            lambda v: v is not None and v > 10),
    ("roe",             "ROE > 15%",                   lambda v: v is not None and v > 15),
    ("roic",            "ROIC > 12%",                  lambda v: v is not None and v > 12),
    # ── Safety ───────────────────────────────────────────────────────
    ("der",             "DER < 0.5",                   lambda v: v is not None and v < 0.5),
    ("current_ratio",   "Current Ratio ≥ 1.5",         lambda v: v is not None and v >= 1.5),
    # ── Cash Flow Quality ────────────────────────────────────────────
    ("fcf_ttm",         "FCF TTM > 0",                 lambda v: v is not None and v > 0),
    ("sloan_ratio",     "Sloan Ratio < 10% (laba riil)",lambda v: v is not None and v < 10),
    # ── Growth ───────────────────────────────────────────────────────
    ("revenue_cagr_5y", "Revenue CAGR 5Y > 5%",        lambda v: v is not None and v > 5),
    ("eps_cagr_5y",     "EPS CAGR 5Y > 5%",            lambda v: v is not None and v > 5),
    ("incremental_roe", "Incremental ROE > 15%",        lambda v: v is not None and v > 15),
    # ── Capital Allocation ───────────────────────────────────────────
    ("retention_ratio", "Retention Ratio > 50%",        lambda v: v is not None and v > 50),
    ("piotroski_score", "Piotroski F-Score ≥ 7",        lambda v: v is not None and v >= 7),
    # ── Valuation ────────────────────────────────────────────────────
    ("margin_of_safety","Margin of Safety > 30%",       lambda v: v is not None and v > 30),
    ("graham_number",   "Price < Graham Number",        None),  # dihitung manual
]


def run_checklist(fundamental: dict, valuation: dict, current_price: float) -> dict:
    """
    Jalankan semua kriteria Buffett.
    Return dict dengan score, verdict, dan detail per kriteria.
    """
    merged = {**fundamental, **valuation}
    results = []
    score   = 0

    for i, (key, label, check_fn) in enumerate(CRITERIA):
        if key == "graham_number":
            # Special case: cek apakah harga < graham number
            gn    = valuation.get("graham_number")
            passed = bool(gn and gn > 0 and current_price < gn)
            val    = gn
        else:
            val    = merged.get(key)
            passed = check_fn(val) if check_fn else False

        if passed:
            score += 1

        results.append({
            "label":  label,
            "value":  val,
            "passed": passed,
        })

    total = len(CRITERIA)

    # Verdict (dari 14 kriteria)
    if score >= 11:
        verdict = "DEEP_VALUE"
    elif score >= 8:
        verdict = "WATCH"
    elif score >= 5:
        verdict = "FAIR"
    else:
        verdict = "AVOID"

    # Notes
    failed = [r["label"] for r in results if not r["passed"]]
    notes  = "GAGAL: " + "; ".join(failed) if failed else "Semua kriteria terpenuhi"

    return {
        "buffett_score": score,
        "verdict":       verdict,
        "notes":         notes,
        "details":       results,
    }


def print_checklist(symbol: str, checklist: dict, valuation: dict, current_price: float):
    """Print hasil checklist ke terminal."""
    print(f"\n{'='*55}")
    print(f" BUFFETT CHECKLIST — {symbol}")
    print(f"{'='*55}")
    for item in checklist["details"]:
        status = "✓" if item["passed"] else "✗"
        val_str = f"{item['value']:.2f}" if isinstance(item["value"], (int, float)) and item["value"] is not None else str(item["value"])
        print(f"  [{status}] {item['label']:<35} ({val_str})")

    print(f"\n  Score      : {checklist['buffett_score']}/{len(CRITERIA)}")
    print(f"  Verdict    : {checklist['verdict']}")

    print(f"\n  Harga      : Rp {current_price:,.0f}")
    if valuation.get("graham_number"):
        print(f"  Graham No. : Rp {valuation['graham_number']:,.2f}")
    if valuation.get("dcf_intrinsic"):
        print(f"  DCF Value  : Rp {valuation['dcf_intrinsic']:,.2f}")
        print(f"  Growth Rate: {valuation.get('dcf_growth_rate', 0):.1f}% (auto dari CAGR)")
    if valuation.get("margin_of_safety") is not None:
        mos = valuation["margin_of_safety"]
        label = "DISKON" if mos > 0 else "MAHAL"
        print(f"  MoS        : {mos:.1f}% → {label}")
    if valuation.get("owner_earnings") is not None:
        print(f"  Owner Earn.: Rp {valuation['owner_earnings']:,.0f} B")
    if valuation.get("revenue_cagr_5y") is not None:
        print(f"  Rev CAGR 5Y: {valuation['revenue_cagr_5y']:.1f}%")
    if valuation.get("eps_cagr_5y") is not None:
        print(f"  EPS CAGR 5Y: {valuation['eps_cagr_5y']:.1f}%")
    if valuation.get("sloan_ratio") is not None:
        sr = valuation["sloan_ratio"]
        sr_label = "OK" if sr < 10 else "RED FLAG (laba akrual)"
        print(f"  Sloan Ratio: {sr:.1f}% → {sr_label}")
    if valuation.get("retention_ratio") is not None:
        print(f"  Retention  : {valuation['retention_ratio']:.1f}% laba ditahan")
    if valuation.get("incremental_roe") is not None:
        print(f"  Incr. ROE  : {valuation['incremental_roe']:.1f}%")

    print(f"\n  Catatan    : {checklist['notes']}")
    print(f"{'='*55}")
