"""
Engine module for evaluating borrower debt capacity and vulnerability.
Calculates regulatory debt thresholds and an underlying structural vulnerability 
score used in network propagation mechanics.
"""

import sys
from pathlib import Path
from typing import Union, Dict, Any

import pandas as pd
import numpy as np

# Ensure the script can import config from the project root
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from config import RBI_DEBT_BURDEN_CAP


def calculate_debt_burden(profile_row: Union[dict, pd.Series], monthly_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculates a borrower's debt burden, buffer runway, and structural vulnerability.
    
    Args:
        profile_row (dict | pd.Series): Profile data for a single borrower. Expected keys 
            include 'household_income', 'savings_buffer', and 'other_loan_emi'.
        monthly_df (pd.DataFrame): 12 rows of the borrower's monthly cashflow data, 
            expected to contain 'month', 'mfi_repayment_due', and 'expenses' columns.
            
    Returns:
        dict: Containing total_monthly_obligations, debt_burden_ratio, exceeds_rbi_cap, 
            cash_buffer_months, and structural_vulnerability.
    """
    # Extract profile attributes
    household_income = float(profile_row["household_income"])
    savings_buffer = float(profile_row["savings_buffer"])
    other_loan_emi = float(profile_row["other_loan_emi"])
    
    # Sort chronological to confidently slice the last 3 months (months 10, 11, 12)
    df_sorted = monthly_df.sort_values(by="month").reset_index(drop=True)
    
    # Average MFI repayment due across the most recent 3 months
    recent_3_months = df_sorted.iloc[-3:]
    avg_mfi_repayment_due = recent_3_months["mfi_repayment_due"].mean()
    
    # Total monthly obligations
    total_monthly_obligations = float(avg_mfi_repayment_due + other_loan_emi)
    
    # Debt burden ratio
    debt_burden_ratio = total_monthly_obligations / household_income if household_income > 0 else 0.0
    
    # Exceeds RBI cap:
    # This mirrors India's RBI rule that a household's total loan repayments 
    # across all lenders must not exceed 50% of monthly household income.
    exceeds_rbi_cap = bool(debt_burden_ratio > RBI_DEBT_BURDEN_CAP)
    
    # Cash buffer months
    avg_expenses = df_sorted["expenses"].mean()
    cash_buffer_months = savings_buffer / avg_expenses if avg_expenses > 0 else 0.0
    
    # Structural vulnerability:
    # This represents how exposed this borrower is to ABSORBING another borrower's 
    # stress through a relationship (used later by the propagation engine). It is 
    # deliberately independent of this borrower's own income trend, because someone 
    # can look financially fine today on their own numbers and still be structurally 
    # fragile underneath.
    structural_vulnerability = (min(debt_burden_ratio, 1.0) + (1.0 - min(cash_buffer_months / 3.0, 1.0))) / 2.0
    
    return {
        "total_monthly_obligations": total_monthly_obligations,
        "debt_burden_ratio": debt_burden_ratio,
        "exceeds_rbi_cap": exceeds_rbi_cap,
        "cash_buffer_months": cash_buffer_months,
        "structural_vulnerability": float(structural_vulnerability)
    }