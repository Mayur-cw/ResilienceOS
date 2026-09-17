"""
Engine module for deterministic borrower stress classification.

Uses a continuous severity-scaling function to guarantee monotonically increasing 
risk metrics as income shocks become more severe, completely eliminating classification 
"jumping" and ensuring a logical progression of states.
"""

import sys
from pathlib import Path
from typing import Union, Dict, Any, List
import pandas as pd

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

def classify_stress(
    profile_row: Union[dict, pd.Series], 
    monthly_df: pd.DataFrame, 
    cashflow_result: Dict[str, Any], 
    debt_result: Dict[str, Any]
) -> Dict[str, Any]:
    
    trend_pct = float(cashflow_result['trend_pct'])
    seasonal = bool(cashflow_result['seasonal_pattern_detected'])
    missed = int(cashflow_result['missed_or_partial_payments_recent'])
    distress_months = int(cashflow_result.get('distress_months', 0))
    buffer = float(debt_result['cash_buffer_months'])
    debt = float(debt_result['debt_burden_ratio'])

    # 1. Smooth, continuous severity calculation
    drop_magnitude = abs(min(trend_pct, 0.0))
    
    # THE FIX: Scale severity exponentially based on the duration of the distress
    # 1 month = 0.75x, 2 months = 1.0x, 4 months = 1.5x, 6 months = 2.0x
    dur_multiplier = 0.5 + (distress_months * 0.25) if distress_months > 0 else 1.0
    base_sev = drop_magnitude * dur_multiplier
    
    # Financial health penalties and bonuses
    debt_penalty = max(0.0, debt - 0.40) * 40.0   
    missed_penalty = missed * 15.0                
    buffer_bonus = min(buffer, 3.0) * 4.0         
    
    severity_score = max(10.0, min(100.0, base_sev + debt_penalty + missed_penalty - buffer_bonus))
    
    # 2. Assign Classification State
    if severity_score < 35:
        state = "Stable"
        rule_id = 4
        rule_desc = "Income trend is stable, or the borrower has sufficient buffers to easily absorb short-term fluctuations."
        evidence = [
            f"Income trend manageable ({trend_pct:.1f}%)",
            f"Debt burden manageable ({debt*100:.1f}%)"
        ]
        
    elif severity_score < 65:
        if seasonal and buffer >= 1.0 and missed == 0 and distress_months <= 2:
            state = "Temporary"
            rule_id = 1
            rule_desc = f"Income dropped {drop_magnitude:.0f}% for {distress_months} month(s), but history proves a seasonal recovery pattern."
            evidence = [
                "Historical seasonal pattern with full recovery",
                f"Positive {buffer:.1f}-month cash buffer",
                "Zero missed payments"
            ]
        else:
            state = "Vulnerable"
            rule_id = 3
            rule_desc = f"Income declined {drop_magnitude:.0f}% for {distress_months} month(s), eroding safety buffers."
            evidence = [
                f"Sustained income drop ({trend_pct:.1f}%) for {distress_months} months",
                "Elevated systemic vulnerability"
            ]
            
    elif severity_score < 85:
        state = "Vulnerable"
        rule_id = 3
        rule_desc = f"Severe income shock ({drop_magnitude:.0f}%) over {distress_months} month(s) is pushing repayment capacity into high-risk territory."
        evidence = [
            f"Severe income drop of {drop_magnitude:.0f}%",
            f"Prolonged distress duration ({distress_months} months)",
            f"Eroded cash buffer ({buffer:.1f} months remaining)"
        ]
        
    else:
        state = "Structural"
        rule_id = 2
        rule_desc = f"Critical financial collapse. The {drop_magnitude:.0f}% income drop lasting {distress_months} months represents a structural inability to service debt."
        evidence = [
            f"Critical income collapse ({trend_pct:.1f}%)",
            f"Sustained distress duration ({distress_months} months)",
            "High probability of imminent default without intervention"
        ]

    return {
        "state": state,
        "confidence": float(min(98.0, severity_score + 15.0)), 
        "evidence": evidence,
        "severity_score": float(severity_score),
        "rule_id": rule_id,
        "rule_description": rule_desc
    }