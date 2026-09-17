"""
Fixed, deliberately-designed demo dataset generator for ResilienceOS.
"""

import sys
import random
import pandas as pd
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import config

def generate_profiles() -> pd.DataFrame:
    data = [
        # THE CORE DEMO GROUP (Group 01)
        ["B01", "Maya",  "Seasonal agricultural income", 23650, 20000, 0, 36000, 12],
        ["B02", "Asha",  "Stable-looking business", 22000, 9000, 2000, 42000, 18],
        ["B03", "Ravi",  "Independent local retailer", 28000, 35000, 500, 38000, 10],
        ["B04", "Imran", "Independent shopkeeper", 22000, 24000, 0, 33000, 12],
        ["B05", "Priya", "Independent borrower", 24000, 5000, 2000, 36000, 12],
        ["B06", "Kiran", "Local supplier", 25000, 15000, 0, 30000, 12],
        ["B07", "Rahul", "Shares transport logistics", 23000, 12000, 0, 25000, 12]
    ]
    
    # 10 PLACEHOLDER GROUPS
    random.seed(42)
    names = ["Vikram", "Sunita", "Amit", "Neha", "Rohit", "Pooja", "Sanjay", "Anjali", "Suresh", "Kavita",
             "Manish", "Ritu", "Deepak", "Sneha", "Vijay", "Aarti", "Prakash", "Rekha", "Anil", "Swati",
             "Manoj", "Geeta", "Rajesh", "Meena", "Sunil", "Jyoti", "Ramesh", "Sushma", "Vinod", "Poonam"]
    
    b_idx = 8
    for g in range(10):
        g_names = names[g*3 : g*3+3]
        for i in range(3):
            b_id = f"B{b_idx+i:02d}"
            inc = random.randint(18, 35) * 1000
            sav = random.randint(5, 20) * 1000
            emi = random.choice([0, 1000, 2000])
            
            # INJECTING STRUCTURAL VARIANCE FOR THE DASHBOARD:
            if g == 4 and i == 0:  # Group 06: Vulnerable (Low savings, High EMI)
                sav = 1000
                emi = 4500
            if g == 7 and i == 2:  # Group 09: Structural risk profile
                sav = 500
                emi = 3000
                
            data.append([b_id, g_names[i], "Standard portfolio borrower", inc, sav, emi, 30000, 12])
        b_idx += 3

    columns = [
        "borrower_id", "name", "persona_note", "household_income",
        "savings_buffer", "other_loan_emi", "mfi_loan_amount", "mfi_tenure_months"
    ]
    return pd.DataFrame(data, columns=columns)


def generate_monthly_data() -> pd.DataFrame:
    data = [
        # B01 (Maya) - Stable
        ["B01", 1, 25000, 12000, 3000, 3000], ["B01", 2, 26000, 12200, 3000, 3000], ["B01", 3, 15000, 11800, 3000, 3000],
        ["B01", 4, 24000, 12000, 3000, 3000], ["B01", 5, 25500, 12300, 3000, 3000], ["B01", 6, 26500, 12000, 3000, 3000],
        ["B01", 7, 25000, 12100, 3000, 3000], ["B01", 8, 24500, 12000, 3000, 3000], ["B01", 9, 15500, 11900, 3000, 3000],
        ["B01", 10, 25000, 12000, 3000, 3000], ["B01", 11, 26000, 12100, 3000, 3000], ["B01", 12, 27000, 12200, 3000, 3000],
        # B02 (Asha) - Stable
        ["B02", 1, 20000, 13000, 3500, 3500], ["B02", 2, 20200, 13100, 3500, 3500], ["B02", 3, 19800, 12900, 3500, 3500],
        ["B02", 4, 20100, 13000, 3500, 3500], ["B02", 5, 20300, 13200, 3500, 3500], ["B02", 6, 19900, 13000, 3500, 3500],
        ["B02", 7, 20000, 13000, 3500, 3500], ["B02", 8, 20200, 13100, 3500, 3500], ["B02", 9, 19800, 12900, 3500, 3500],
        ["B02", 10, 20100, 13000, 3500, 3500], ["B02", 11, 20000, 13000, 3500, 3500], ["B02", 12, 20200, 13100, 3500, 3500],
        # B03 (Ravi) - Stable
        ["B03", 1, 28000, 14000, 3200, 3200], ["B03", 2, 28200, 14100, 3200, 3200], ["B03", 3, 27800, 13900, 3200, 3200],
        ["B03", 4, 28100, 14000, 3200, 3200], ["B03", 5, 28300, 14200, 3200, 3200], ["B03", 6, 27900, 14000, 3200, 3200],
        ["B03", 7, 28000, 14000, 3200, 3200], ["B03", 8, 28200, 14100, 3200, 3200], ["B03", 9, 27800, 13900, 3200, 3200],
        ["B03", 10, 28100, 14000, 3200, 3200], ["B03", 11, 28000, 14000, 3200, 3200], ["B03", 12, 28200, 14100, 3200, 3200],
        # B04 (Imran) - Stable
        ["B04", 1, 22000, 12000, 2800, 2800], ["B04", 2, 22100, 12050, 2800, 2800], ["B04", 3, 21900, 11950, 2800, 2800],
        ["B04", 4, 22000, 12000, 2800, 2800], ["B04", 5, 22200, 12100, 2800, 2800], ["B04", 6, 21900, 11950, 2800, 2800],
        ["B04", 7, 22000, 12000, 2800, 2800], ["B04", 8, 22100, 12050, 2800, 2800], ["B04", 9, 21900, 11950, 2800, 2800],
        ["B04", 10, 22000, 12000, 2800, 2800], ["B04", 11, 22000, 12000, 2800, 2800], ["B04", 12, 22100, 12050, 2800, 2800],
        # B05 (Priya) - Structural
        ["B05", 1, 30000, 15000, 3000, 3000], ["B05", 2, 29000, 15000, 3000, 3000], ["B05", 3, 27500, 14800, 3000, 3000],
        ["B05", 4, 26000, 15000, 3000, 3000], ["B05", 5, 24000, 15200, 3000, 3000], ["B05", 6, 22000, 15000, 3000, 3000],
        ["B05", 7, 20000, 15000, 3000, 3000], ["B05", 8, 18500, 14900, 3000, 2500], ["B05", 9, 17000, 15000, 3000, 2000],
        ["B05", 10, 16000, 15100, 3000, 1500], ["B05", 11, 15000, 15000, 3000, 1000], ["B05", 12, 14000, 15000, 3000, 1000],
        # B06 (Kiran) - Stable
        ["B06", 1, 25000, 14000, 3000, 3000], ["B06", 2, 25200, 14100, 3000, 3000], ["B06", 3, 24800, 13900, 3000, 3000],
        ["B06", 4, 25100, 14000, 3000, 3000], ["B06", 5, 25300, 14200, 3000, 3000], ["B06", 6, 24900, 14000, 3000, 3000],
        ["B06", 7, 25000, 14000, 3000, 3000], ["B06", 8, 25200, 14100, 3000, 3000], ["B06", 9, 24800, 13900, 3000, 3000],
        ["B06", 10, 25100, 14000, 3000, 3000], ["B06", 11, 25000, 14000, 3000, 3000], ["B06", 12, 25200, 14100, 3000, 3000],
        # B07 (Rahul) - Stable
        ["B07", 1, 23000, 12000, 2500, 2500], ["B07", 2, 23100, 12100, 2500, 2500], ["B07", 3, 22900, 11900, 2500, 2500],
        ["B07", 4, 23000, 12000, 2500, 2500], ["B07", 5, 23200, 12200, 2500, 2500], ["B07", 6, 22800, 11800, 2500, 2500],
        ["B07", 7, 23000, 12000, 2500, 2500], ["B07", 8, 23100, 12100, 2500, 2500], ["B07", 9, 22900, 11900, 2500, 2500],
        ["B07", 10, 23000, 12000, 2500, 2500], ["B07", 11, 23000, 12000, 2500, 2500], ["B07", 12, 23100, 12100, 2500, 2500],
    ]
    
    # Procedurally generate the rest, but inject life-events
    random.seed(42)
    b_idx = 8
    for g in range(10):
        for i in range(3):
            b_id = f"B{b_idx+i:02d}"
            base_inc = random.randint(18, 35) * 1000
            for m in range(1, 13):
                m_inc = base_inc + random.randint(-500, 500)
                m_exp = int(base_inc * 0.5) + random.randint(-300, 300)
                mfi_due = 2500
                mfi_paid = 2500
                
                # INJECTING MONTHLY CASHFLOW STRESS:
                if g == 1 and i == 1: # Group 03: Temporary Dip (Seasonal)
                    if m in [8, 9, 10]:
                        m_inc = int(base_inc * 0.55)
                if g == 4 and i == 0: # Group 06: Vulnerable Drop
                    if m >= 10:
                        m_inc = int(base_inc * 0.6)
                if g == 7 and i == 2: # Group 09: Structural Collapse
                    if m >= 9:
                        m_inc = int(base_inc * 0.4)
                        mfi_paid = 0 if m >= 11 else 1000

                data.append([b_id, m, m_inc, m_exp, mfi_due, mfi_paid])
        b_idx += 3

    columns = [
        "borrower_id", "month", "income", "expenses",
        "mfi_repayment_due", "mfi_repayment_paid"
    ]
    return pd.DataFrame(data, columns=columns)


def generate_relationships() -> pd.DataFrame:
    data = [
        ["B01", "B02", "shared_business", 0.75],
        ["B01", "B03", "same_village", 0.15],
        ["B02", "B06", "supply_chain", 0.60], 
        ["B03", "B07", "shared_assets", 0.35], 
        ["B02", "B03", "village_committee", 0.25], 
        ["B06", "B07", "shared_market", 0.40],     
        ["B01", "B07", "extended_family", 0.20]    
    ]
    
    random.seed(42)
    b_idx = 8
    for g in range(10):
        g_ids = [f"B{b_idx+i:02d}" for i in range(3)]
        data.append([g_ids[0], g_ids[1], "co-borrower", round(random.uniform(0.4, 0.8), 2)])
        data.append([g_ids[1], g_ids[2], "family", round(random.uniform(0.2, 0.5), 2)])
        b_idx += 3

    columns = ["borrower_a", "borrower_b", "relationship_type", "weight"]
    return pd.DataFrame(data, columns=columns)


if __name__ == "__main__":
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    df_profile = generate_profiles()
    df_monthly = generate_monthly_data()
    df_relationships = generate_relationships()
    
    df_profile.to_csv(config.PROFILE_CSV, index=False)
    df_monthly.to_csv(config.MONTHLY_CSV, index=False)
    df_relationships.to_csv(config.RELATIONSHIPS_CSV, index=False)
    
    print("✅ Dashboard variance data generated successfully.")