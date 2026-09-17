"""
Run this file from the project root using:
python -m tests.test_stress
"""
import pandas as pd
# FIXED: Corrected import and added prerequisite dependencies
from engine.stress import classify_stress
from engine.cashflow import analyze_cashflow
from engine.debt import calculate_debt_burden

def run_tests():
    profile_a = pd.Series({"borrower_id": "T01", "household_income": 100, "savings_buffer": 100.0, "other_loan_emi": 0})
    monthly_a = pd.DataFrame({
        "month": range(1, 13),
        "income": [100, 100, 100, 100, 40, 40, 40, 100, 100, 100, 40, 40],
        "expenses": [50] * 12,
        "mfi_repayment_due": [10] * 12,
        "mfi_repayment_paid": [10] * 12
    })
    # FIXED: Calculate prerequisites and pass 4 arguments
    cf_a = analyze_cashflow(monthly_a)
    debt_a = calculate_debt_burden(profile_a, monthly_a)
    res_a = classify_stress(profile_a, monthly_a, cf_a, debt_a)
    assert res_a["state"] == "Temporary", f"Expected 'Temporary', got {res_a['state']}"

    profile_b = pd.Series({"borrower_id": "T02", "household_income": 100, "savings_buffer": 0.5, "other_loan_emi": 0})
    monthly_b = pd.DataFrame({
        "month": range(1, 13),
        "income": [100, 95, 90, 85, 80, 75, 70, 65, 60, 55, 50, 45],
        "expenses": [60] * 12,
        "mfi_repayment_due": [10] * 12,
        "mfi_repayment_paid": [10, 10, 10, 10, 10, 10, 10, 5, 0, 0, 0, 0]
    })
    cf_b = analyze_cashflow(monthly_b)
    debt_b = calculate_debt_burden(profile_b, monthly_b)
    res_b = classify_stress(profile_b, monthly_b, cf_b, debt_b)
    assert res_b["state"] == "Structural", f"Expected 'Structural', got {res_b['state']}"

    profile_c = pd.Series({"borrower_id": "T03", "household_income": 200, "savings_buffer": 250.0, "other_loan_emi": 0})
    monthly_c = pd.DataFrame({
        "month": range(1, 13),
        "income": [200] * 12,
        "expenses": [50] * 12,
        "mfi_repayment_due": [10] * 12,
        "mfi_repayment_paid": [10] * 12
    })
    cf_c = analyze_cashflow(monthly_c)
    debt_c = calculate_debt_burden(profile_c, monthly_c)
    res_c = classify_stress(profile_c, monthly_c, cf_c, debt_c)
    assert res_c["state"] == "Stable", f"Expected 'Stable', got {res_c['state']}"

    profile_d = pd.Series({"borrower_id": "B01", "household_income": 200, "savings_buffer": 125.0, "other_loan_emi": 0})
    maya_income = [200, 200, 80, 80, 80, 200, 200, 200, 200, 200, 80, 80]
    
    monthly_d = pd.DataFrame({
        "month": range(1, 13),
        "income": maya_income,
        "expenses": [50] * 12,
        "mfi_repayment_due": [10] * 12,
        "mfi_repayment_paid": [10] * 12
    })
    cf_d = analyze_cashflow(monthly_d)
    debt_d = calculate_debt_burden(profile_d, monthly_d)
    res_d = classify_stress(profile_d, monthly_d, cf_d, debt_d)
    assert res_d["state"] == "Temporary", f"Expected 'Temporary' despite extreme shock, got {res_d['state']}"

    print("PASSED: test_stress.py")

if __name__ == "__main__":
    run_tests()