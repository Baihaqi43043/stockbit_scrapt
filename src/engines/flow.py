from typing import List, Dict

def calculate_absorption_pct(retail_net_val: float, big_money_net_val: float) -> float:
    """
    Menghitung seberapa banyak jualan ritel diserap oleh Big Money.
    Syarat ideal: retail_net_val < 0 (ritel jualan) dan big_money_net_val > 0 (big money beli).
    """
    if retail_net_val >= 0: # Ritel tidak jualan
        return 0
    
    abs_pct = abs(big_money_net_val / retail_net_val) * 100
    return round(abs_pct, 2)

def detect_hidden_accumulation(price_change_pct: float, big_money_flow: float) -> bool:
    """
    Mendeteksi akumulasi tersembunyi: 
    Harga turun atau stagnan, tapi Big Money masuk besar.
    """
    return price_change_pct <= 0.5 and big_money_flow > 0

def get_broker_concentration(broker_transactions: List[Dict]) -> Dict:
    """
    Menganalisis konsentrasi TOP 3 dan TOP 5 broker pembeli.
    """
    # Urutkan berdasarkan net_val DESC (pembeli terbesar)
    buyers = sorted([tx for tx in broker_transactions if tx['net_val'] > 0], 
                    key=lambda x: x['net_val'], reverse=True)
    
    total_buy_val = sum(tx['net_val'] for tx in buyers)
    if total_buy_val == 0:
        return {"top3": 0, "top5": 0}
    
    top3_val = sum(tx['net_val'] for tx in buyers[:3])
    top5_val = sum(tx['net_val'] for tx in buyers[:5])
    
    return {
        "top3": round((top3_val / total_buy_val) * 100, 2),
        "top5": round((top5_val / total_buy_val) * 100, 2)
    }
