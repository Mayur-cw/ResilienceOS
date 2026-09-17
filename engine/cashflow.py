"""
Engine module for processing and shocking borrower cashflow data.
Contains deterministic mathematical rules for analyzing income trends, 
volatility, and simulating stress on historical monthly data.
"""

import pandas as pd
import numpy as np
from numbers import Integral, Real

def analyze_cashflow(monthly_df: pd.DataFrame) -> dict:
    """
    Analyzes 12 months of cashflow data for a single borrower to extract
    key financial metrics, trends, and seasonal patterns.
    """
    df = monthly_df.sort_values(by="month").reset_index(drop=True)
    income_series = df["income"]
    
    # THE FIX: Lock baseline to the first 6 months to guarantee it is NEVER 
    # contaminated by the shock simulation (which has a max duration of 6 months).
    baseline_avg_income = income_series.iloc[:6].mean()
    recent_avg_income = income_series.iloc[-2:].mean()
    
    if baseline_avg_income != 0:
        trend_pct = ((recent_avg_income - baseline_avg_income) / baseline_avg_income) * 100.0
    else:
        trend_pct = 0.0
        
    mean_income = income_series.mean()
    income_volatility = income_series.std() / mean_income if mean_income != 0 else 0.0
        
    # Detect seasonal pattern in the first 9 months
    seasonal_pattern_detected = False
    for i in range(9):
        current_income = income_series.iloc[i]
        if current_income <= recent_avg_income * 1.15:
            max_in_next_3 = income_series.iloc[i+1 : i+4].max()
            if max_in_next_3 >= current_income * 1.2:
                seasonal_pattern_detected = True
                break
                
    # NEW FEATURE: Count exactly how long the borrower has been in distress
    distress_months = 0
    for val in reversed(income_series.tolist()):
        if val < baseline_avg_income * 0.90:  # 10% below baseline is distress
            distress_months += 1
        else:
            break
                
    recent_3_months = df.iloc[-3:]
    missed_payments_mask = recent_3_months["mfi_repayment_paid"] < recent_3_months["mfi_repayment_due"]
    missed_or_partial_payments_recent = int(missed_payments_mask.sum())
    
    avg_expenses = df["expenses"].mean()
    
    return {
        "recent_avg_income": float(recent_avg_income),
        "baseline_avg_income": float(baseline_avg_income),
        "trend_pct": float(trend_pct),
        "income_volatility": float(income_volatility),
        "seasonal_pattern_detected": bool(seasonal_pattern_detected),
        "distress_months": distress_months, # Exposed to the stress engine
        "missed_or_partial_payments_recent": missed_or_partial_payments_recent,
        "avg_expenses": float(avg_expenses)
    }

def apply_shock(monthly_df: pd.DataFrame, shock_pct: float, duration_months: int) -> pd.DataFrame:
    required_columns = {"month", "income"}
    missing_columns = sorted(required_columns - set(monthly_df.columns))
    if missing_columns:
        raise ValueError(f"Cannot apply shock: missing columns {missing_columns}")

    df_shocked = monthly_df.sort_values(by="month").reset_index(drop=True).copy()
    
    if duration_months > 0:
        multiplier = 1.0 + (shock_pct / 100.0)
        target_indices = df_shocked.index[-duration_months:]
        df_shocked.loc[target_indices, "income"] = df_shocked.loc[target_indices, "income"] * multiplier
        
    return df_shocked