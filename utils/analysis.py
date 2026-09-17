"""Cached composition of the deterministic borrower-analysis engines."""

from typing import Any, Dict

import pandas as pd
import streamlit as st

from engine.cashflow import analyze_cashflow
from engine.debt import calculate_debt_burden
from engine.stress import classify_stress


@st.cache_data
def analyze_group_baseline(
    profile_df: pd.DataFrame,
    monthly_df: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate baseline metrics once for all borrowers and cache the result."""
    rows = []
    monthly_by_borrower: Dict[Any, pd.DataFrame] = {
        borrower_id: borrower_monthly.sort_values("month").reset_index(drop=True)
        for borrower_id, borrower_monthly in monthly_df.groupby("borrower_id")
    }

    for _, profile_row in profile_df.iterrows():
        borrower_id = profile_row["borrower_id"]
        borrower_monthly = monthly_by_borrower[borrower_id]
        cashflow_result = analyze_cashflow(borrower_monthly)
        debt_result = calculate_debt_burden(profile_row, borrower_monthly)
        stress_result = classify_stress(
            profile_row,
            borrower_monthly,
            cashflow_result,
            debt_result,
        )
        rows.append(
            {
                "borrower_id": borrower_id,
                "name": profile_row["name"],
                "state": stress_result["state"],
                "confidence": stress_result["confidence"],
                "severity_score": stress_result["severity_score"],
                "debt_burden_ratio": debt_result["debt_burden_ratio"],
                "cash_buffer_months": debt_result["cash_buffer_months"],
                "structural_vulnerability": debt_result["structural_vulnerability"],
                "trend_pct": cashflow_result["trend_pct"],
            }
        )

    return pd.DataFrame(rows)