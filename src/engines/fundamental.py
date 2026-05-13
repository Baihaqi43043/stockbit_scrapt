import math
from typing import Optional

def calculate_graham_number(eps: float, bvps: float) -> Optional[float]:
    """
    Rumus Graham: sqrt(22.5 * EPS * BVPS)
    Hanya valid jika EPS dan BVPS positif.
    """
    if eps <= 0 or bvps <= 0:
        return None
    return math.sqrt(22.5 * eps * bvps)

def calculate_dcf_intrinsic(fcf: float, growth_rate: float, discount_rate: float, terminal_growth: float = 0.02, years: int = 10) -> float:
    """
    Sederhana DCF (Discounted Cash Flow).
    fcf: Free Cash Flow saat ini (miliar)
    growth_rate: Estimasi pertumbuhan (desimal, misal 0.10 untuk 10%)
    discount_rate: WACC atau rate yang diinginkan (desimal, misal 0.12)
    """
    intrinsic_value = 0
    current_fcf = fcf
    
    # 1. Projecting FCF for next N years
    for y in range(1, years + 1):
        current_fcf *= (1 + growth_rate)
        intrinsic_value += current_fcf / ((1 + discount_rate) ** y)
        
    # 2. Terminal Value
    terminal_value = (current_fcf * (1 + terminal_growth)) / (discount_rate - terminal_growth)
    intrinsic_value += terminal_value / ((1 + discount_rate) ** years)
    
    return intrinsic_value

def get_valuation_verdict(current_price: float, intrinsic_value: float) -> str:
    if not intrinsic_value or intrinsic_value <= 0:
        return "N/A"
    
    mos = (intrinsic_value - current_price) / intrinsic_value
    if mos > 0.30:
        return "Undervalued (Strong Buy)"
    elif mos > 0.10:
        return "Undervalued (Buy)"
    elif mos < -0.20:
        return "Overvalued (Sell)"
    else:
        return "Fair Value (Hold)"
