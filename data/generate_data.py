"""
Deliberately-designed demo dataset generator for ResilienceOS.

This module hardcodes exact borrower personas for the primary demo group
(Maya's network) and for four "flagged" borrowers scattered across the wider
portfolio, so the classification engine has genuine Temporary / Vulnerable /
Structural cases to find outside Group 01. Every other placeholder borrower
gets a procedurally generated but seeded (reproducible) trajectory built from
a named livelihood archetype, so the portfolio feels populated by real small
businesses rather than repeated filler rows.
"""

import random
import sys
from pathlib import Path

import pandas as pd

# Ensure the script can import config whether run from root or from within /data
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import config

# ---------------------------------------------------------------------------
# CORE DEMO GROUP (Group 01) — unchanged, hand-crafted narrative personas.
# ---------------------------------------------------------------------------

CORE_DEMO_PROFILES = [
    ["B01", "Maya",  "Seasonal agricultural income; two comparable dips this year, both fully recovered", 23650, 20000, 0, 36000, 12],
    ["B02", "Asha",  "Stable-looking business, economically linked to Maya through a shared supply arrangement", 22000, 9000, 2000, 42000, 18],
    ["B03", "Ravi",  "Independent local retailer; only a weak village-level connection to Maya", 28000, 35000, 500, 38000, 10],
    ["B04", "Imran", "Independent shopkeeper with no financial relationship to the rest of this group", 22000, 24000, 0, 33000, 12],
    ["B05", "Priya", "Independent borrower with a genuine multi-month income decline and no historical recovery pattern", 24000, 5000, 2000, 36000, 12],
    ["B06", "Kiran", "Local supplier dependent on Asha's business volume", 25000, 15000, 0, 30000, 12],
    ["B07", "Rahul", "Shares transport logistics with Ravi", 23000, 12000, 0, 25000, 12],
]

CORE_DEMO_MONTHLY = [
    # B01 (Maya) — seasonal dips at month 3 and 9, both fully recovered
    ["B01", 1, 25000, 12000, 3000, 3000], ["B01", 2, 26000, 12200, 3000, 3000], ["B01", 3, 15000, 11800, 3000, 3000],
    ["B01", 4, 24000, 12000, 3000, 3000], ["B01", 5, 25500, 12300, 3000, 3000], ["B01", 6, 26500, 12000, 3000, 3000],
    ["B01", 7, 25000, 12100, 3000, 3000], ["B01", 8, 24500, 12000, 3000, 3000], ["B01", 9, 15500, 11900, 3000, 3000],
    ["B01", 10, 25000, 12000, 3000, 3000], ["B01", 11, 26000, 12100, 3000, 3000], ["B01", 12, 27000, 12200, 3000, 3000],
    # B02 (Asha)
    ["B02", 1, 20000, 13000, 3500, 3500], ["B02", 2, 20200, 13100, 3500, 3500], ["B02", 3, 19800, 12900, 3500, 3500],
    ["B02", 4, 20100, 13000, 3500, 3500], ["B02", 5, 20300, 13200, 3500, 3500], ["B02", 6, 19900, 13000, 3500, 3500],
    ["B02", 7, 20000, 13000, 3500, 3500], ["B02", 8, 20200, 13100, 3500, 3500], ["B02", 9, 19800, 12900, 3500, 3500],
    ["B02", 10, 20100, 13000, 3500, 3500], ["B02", 11, 20000, 13000, 3500, 3500], ["B02", 12, 20200, 13100, 3500, 3500],
    # B03 (Ravi)
    ["B03", 1, 28000, 14000, 3200, 3200], ["B03", 2, 28200, 14100, 3200, 3200], ["B03", 3, 27800, 13900, 3200, 3200],
    ["B03", 4, 28100, 14000, 3200, 3200], ["B03", 5, 28300, 14200, 3200, 3200], ["B03", 6, 27900, 14000, 3200, 3200],
    ["B03", 7, 28000, 14000, 3200, 3200], ["B03", 8, 28200, 14100, 3200, 3200], ["B03", 9, 27800, 13900, 3200, 3200],
    ["B03", 10, 28100, 14000, 3200, 3200], ["B03", 11, 28000, 14000, 3200, 3200], ["B03", 12, 28200, 14100, 3200, 3200],
    # B04 (Imran)
    ["B04", 1, 22000, 12000, 2800, 2800], ["B04", 2, 22100, 12050, 2800, 2800], ["B04", 3, 21900, 11950, 2800, 2800],
    ["B04", 4, 22000, 12000, 2800, 2800], ["B04", 5, 22200, 12100, 2800, 2800], ["B04", 6, 21900, 11950, 2800, 2800],
    ["B04", 7, 22000, 12000, 2800, 2800], ["B04", 8, 22100, 12050, 2800, 2800], ["B04", 9, 21900, 11950, 2800, 2800],
    ["B04", 10, 22000, 12000, 2800, 2800], ["B04", 11, 22000, 12000, 2800, 2800], ["B04", 12, 22100, 12050, 2800, 2800],
    # B05 (Priya) — sustained multi-month collapse, no recovery
    ["B05", 1, 30000, 15000, 3000, 3000], ["B05", 2, 29000, 15000, 3000, 3000], ["B05", 3, 27500, 14800, 3000, 3000],
    ["B05", 4, 26000, 15000, 3000, 3000], ["B05", 5, 24000, 15200, 3000, 3000], ["B05", 6, 22000, 15000, 3000, 3000],
    ["B05", 7, 20000, 15000, 3000, 3000], ["B05", 8, 18500, 14900, 3000, 2500], ["B05", 9, 17000, 15000, 3000, 2000],
    ["B05", 10, 16000, 15100, 3000, 1500], ["B05", 11, 15000, 15000, 3000, 1000], ["B05", 12, 14000, 15000, 3000, 1000],
    # B06 (Kiran)
    ["B06", 1, 25000, 14000, 3000, 3000], ["B06", 2, 25200, 14100, 3000, 3000], ["B06", 3, 24800, 13900, 3000, 3000],
    ["B06", 4, 25100, 14000, 3000, 3000], ["B06", 5, 25300, 14200, 3000, 3000], ["B06", 6, 24900, 14000, 3000, 3000],
    ["B06", 7, 25000, 14000, 3000, 3000], ["B06", 8, 25200, 14100, 3000, 3000], ["B06", 9, 24800, 13900, 3000, 3000],
    ["B06", 10, 25100, 14000, 3000, 3000], ["B06", 11, 25000, 14000, 3000, 3000], ["B06", 12, 25200, 14100, 3000, 3000],
    # B07 (Rahul)
    ["B07", 1, 23000, 12000, 2500, 2500], ["B07", 2, 23100, 12100, 2500, 2500], ["B07", 3, 22900, 11900, 2500, 2500],
    ["B07", 4, 23000, 12000, 2500, 2500], ["B07", 5, 23200, 12200, 2500, 2500], ["B07", 6, 22800, 11800, 2500, 2500],
    ["B07", 7, 23000, 12000, 2500, 2500], ["B07", 8, 23100, 12100, 2500, 2500], ["B07", 9, 22900, 11900, 2500, 2500],
    ["B07", 10, 23000, 12000, 2500, 2500], ["B07", 11, 23000, 12000, 2500, 2500], ["B07", 12, 23100, 12100, 2500, 2500],
]

CORE_DEMO_RELATIONSHIPS = [
    ["B01", "B02", "shared_business", 0.75],
    ["B01", "B03", "same_village", 0.15],
    ["B02", "B06", "supply_chain", 0.60],       # Asha supplies Kiran
    ["B03", "B07", "shared_assets", 0.35],       # Ravi shares transport with Rahul
    ["B02", "B03", "village_committee", 0.25],   # Asha and Ravi
    ["B06", "B07", "shared_market", 0.40],       # Kiran and Rahul
    ["B01", "B07", "extended_family", 0.20],     # Maya and Rahul
]

# ---------------------------------------------------------------------------
# WIDER PORTFOLIO (Groups 02-11) — one connected micro-group each, built from
# named livelihood archetypes. Four borrowers are "flagged": their monthly
# trajectories are hand-tuned so the engine classifies them as Temporary,
# Vulnerable, or Vulnerable-via-debt-load — proving the system finds risk
# beyond the demo group without ever outranking Priya's Structural case.
# Every other borrower gets a seeded, bounded-noise "stable" trajectory so
# the portfolio still reads as one coherent dataset, not a patchwork.
# ---------------------------------------------------------------------------

# (borrower_a_index, borrower_b_index, relationship_type, weight) — indices are
# positions within that group's member list below.
_GROUP_SPECS = [
    {
        "group_label": "Group 02",
        "members": [
            ("Vikram", "Runs a hardware store on the main road; demand has stayed flat and predictable all year.", "stable"),
            ("Sunita", "Co-borrows with Vikram; tailoring unit serving local schools with a steady, separate customer base.", "stable"),
            ("Amit", "Auto-rickshaw driver on a fixed town route; fares have held steady month to month.", "stable"),
        ],
        "edges": [(0, 1, "co-borrower", 0.40), (1, 2, "family", 0.30)],
    },
    {
        "group_label": "Group 03",
        "members": [
            ("Neha", "Dairy farmer selling to the local cooperative; milk collection income is consistent.", "stable"),
            ("Rohit", "Neha's neighbor and occasional cattle-feed supplier; income tracks her steady demand.", "stable"),
            ("Pooja", "Runs a small provision store two lanes over; unrelated trade, only a weak village-level tie.", "stable"),
        ],
        "edges": [(0, 1, "neighboring_business", 0.35), (1, 2, "village_committee", 0.15)],
    },
    {
        "group_label": "Group 04",
        "members": [
            ("Sanjay", "Sells seasonal produce at the weekly market; an earlier dip this year fully recovered within weeks, but the current one hasn't turned yet.", "seasonal_temporary"),
            ("Anjali", "Sanjay's sister-in-law; a home-stitching business that keeps its own steady rhythm regardless of his seasonal swings.", "stable"),
            ("Suresh", "Loosely linked to the family through a shared handcart; income is independent and steady.", "stable"),
        ],
        "edges": [(0, 1, "family", 0.55), (1, 2, "shared_equipment", 0.25)],
    },
    {
        "group_label": "Group 05",
        "members": [
            ("Kavita", "Handloom weaver supplying a nearby exporter on standing orders.", "stable"),
            ("Manish", "Sits on the same village committee as Kavita; runs a steady stationery shop near the school.", "stable"),
            ("Ritu", "Manish's spouse; manages a small papad-making unit with a stable weekly order cycle.", "stable"),
        ],
        "edges": [(0, 1, "village_committee", 0.30), (1, 2, "family", 0.45)],
    },
    {
        "group_label": "Group 06",
        "members": [
            ("Deepak", "Runs a small hardware-supply stall; a key wholesale client scaled back orders months ago and volumes keep sliding with no sign of recovery.", "declining_vulnerable"),
            ("Sneha", "Buys stock through Deepak's supply line; her own counter has held up so far, but the link is worth watching if he falls further behind.", "stable"),
            ("Vijay", "Works the same market row; only a weak co-borrower tie to the rest of the group.", "stable"),
            ("Aarti", "Vijay's cousin; family tie only, income unrelated to the group's trade.", "stable"),
        ],
        "edges": [(0, 1, "supply_chain", 0.70), (1, 2, "co-borrower", 0.30), (2, 3, "family", 0.25)],
    },
    {
        "group_label": "Group 07",
        "members": [
            ("Prakash", "Bicycle-repair stall with a loyal set of regular customers.", "stable"),
            ("Rekha", "Prakash's spouse; runs a bangle and trinket stand near the same bus stand.", "stable"),
        ],
        "edges": [(0, 1, "family", 0.40)],
    },
    {
        "group_label": "Group 08",
        "members": [
            ("Anil", "Carpentry workshop taking on a steady run of small local furniture orders.", "stable"),
            ("Swati", "Anil's regular customer and neighboring shop owner; sells sweets with steady local demand.", "stable"),
            ("Manoj", "Mason on a small local contracting crew; income has stayed level all year.", "stable"),
        ],
        "edges": [(0, 1, "neighboring_business", 0.30), (1, 2, "co-borrower", 0.25)],
    },
    {
        "group_label": "Group 09",
        "members": [
            ("Geeta", "Poultry supplier carrying two informal loans on top of the MFI loan; income has only dipped mildly, but combined repayments now sit close to the RBI debt-burden cap and a recent installment went unpaid.", "debt_vulnerable"),
            ("Rajesh", "Part of the same informal lending circle as Geeta; his own repayments are current, but the circle's exposure to her debt load is worth flagging.", "stable"),
            ("Meena", "Rajesh's relative; family tie only, finances are independent.", "stable"),
        ],
        "edges": [(0, 1, "informal_lending_circle", 0.60), (1, 2, "family", 0.20)],
    },
    {
        "group_label": "Group 10",
        "members": [
            ("Sushma", "Runs a fish stall at the daily market; catch and sales have stayed steady.", "stable"),
            ("Sunil", "Shares a transport-pooling arrangement with Sushma to reach the market each morning.", "stable"),
            ("Jyoti", "Sunil's co-borrower on a separate small loan; embroidery unit with standing wholesale orders.", "stable"),
            ("Ramesh", "Jyoti's neighbor; runs a mobile-repair shop with a steady base of repeat customers.", "stable"),
        ],
        "edges": [(0, 1, "transport_pooling", 0.35), (1, 2, "co-borrower", 0.40), (2, 3, "neighboring_business", 0.30)],
    },
    {
        "group_label": "Group 11",
        "members": [
            ("Vinod", "Handicrafts trader tied to a festival export cycle; a similar dip earlier this year recovered in full, but the current one is deeper and still running.", "seasonal_temporary_2"),
            ("Poonam", "Vinod's regular supplier; a similar seasonal rhythm, but this cycle her stock has cleared on time.", "stable"),
            ("Farhan", "Poonam's neighbor; runs a steady grocery counter unrelated to the export trade.", "stable"),
        ],
        "edges": [(0, 1, "shared_supplier", 0.55), (1, 2, "neighboring_business", 0.25)],
    },
]

# Hand-tuned month-by-month data for the four flagged archetypes, verified
# against engine/cashflow.py + engine/debt.py + engine/stress.py to land in
# the intended state and to stay below Priya's Structural severity (100).
_FLAGGED_ARCHETYPES = {
    "seasonal_temporary": {  # -> Temporary, severity ~38
        "income": [24000, 24500, 14000, 23500, 24200, 24800, 24000, 24300, 23800, 22000, 14000, 12000],
        "expenses": [12000] * 12,
        "due": [2500] * 12,
        "paid": [2500] * 12,
        "household_income": 24000, "savings_buffer": 13000, "other_loan_emi": 0,
        "mfi_loan_amount": 30000, "mfi_tenure_months": 12,
    },
    "declining_vulnerable": {  # -> Vulnerable (income-driven), severity ~48
        "income": [25000, 25200, 24800, 25100, 24900, 25000, 24000, 23500, 23000, 21000, 16000, 14000],
        "expenses": [13000] * 12,
        "due": [2600] * 12,
        "paid": [2600] * 12,
        "household_income": 25000, "savings_buffer": 8000, "other_loan_emi": 0,
        "mfi_loan_amount": 32000, "mfi_tenure_months": 12,
    },
    "debt_vulnerable": {  # -> Vulnerable (debt-driven), severity ~43
        "income": [26000, 26200, 25800, 26100, 25900, 26000, 25000, 24000, 23500, 22500, 21000, 20000],
        "expenses": [15000] * 12,
        "due": [3200] * 12,
        "paid": [3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 2200, 3200],
        "household_income": 26000, "savings_buffer": 3500, "other_loan_emi": 9000,
        "mfi_loan_amount": 38000, "mfi_tenure_months": 14,
    },
    "seasonal_temporary_2": {  # -> Temporary, severity ~39 (proves the pattern isn't a fluke)
        "income": [22000, 22300, 22600, 10000, 21900, 22400, 22000, 21800, 22200, 19000, 13000, 10000],
        "expenses": [11500] * 12,
        "due": [2400] * 12,
        "paid": [2400] * 12,
        "household_income": 22000, "savings_buffer": 12500, "other_loan_emi": 500,
        "mfi_loan_amount": 28000, "mfi_tenure_months": 12,
    },
}


def _stable_monthly_series(rng: random.Random, base_income: float) -> tuple[list[int], list[int]]:
    """Builds one borrower's 12-month income + expenses with mild drift, noise,
    and (sometimes) a single mid-year dip that fully recovers — enough texture
    to look real on a line chart without ever approaching a stress threshold."""
    drift_pct = rng.uniform(-8, 8)
    noise_pct = rng.uniform(3, 6)
    income = []
    for m in range(12):
        frac = m / 11
        trended = base_income * (1 + (drift_pct / 100) * frac)
        noise = rng.uniform(-noise_pct, noise_pct) / 100
        income.append(trended * (1 + noise))

    # Optional single-month wobble, always inside months 7-9 (index 6-8) so it
    # never touches the baseline (months 1-6) or recent (months 11-12) windows.
    if rng.random() < 0.5:
        dip_idx = rng.choice([6, 7, 8])
        dip_pct = rng.uniform(10, 18)
        income[dip_idx] *= (1 - dip_pct / 100)

    income = [round(v) for v in income]
    expense_ratio = rng.uniform(0.48, 0.60)
    expenses = [round(v * expense_ratio * (1 + rng.uniform(-0.03, 0.03))) for v in income]
    return income, expenses


def _build_placeholder_roster() -> list[dict]:
    """Builds the full spec for every placeholder borrower once, so profile,
    monthly, and relationship generation all stay consistent with each other."""
    rng = random.Random(42)
    roster = []
    b_idx = 8

    for spec in _GROUP_SPECS:
        member_ids = []
        for name, note, archetype in spec["members"]:
            borrower_id = f"B{b_idx:02d}"
            b_idx += 1
            member_ids.append(borrower_id)

            if archetype in _FLAGGED_ARCHETYPES:
                a = _FLAGGED_ARCHETYPES[archetype]
                income, expenses, due, paid = a["income"], a["expenses"], a["due"], a["paid"]
                household_income = a["household_income"]
                savings_buffer = a["savings_buffer"]
                other_loan_emi = a["other_loan_emi"]
                mfi_loan_amount = a["mfi_loan_amount"]
                mfi_tenure_months = a["mfi_tenure_months"]
            else:
                base_income = rng.randint(18, 38) * 1000
                income, expenses = _stable_monthly_series(rng, base_income)
                due_ratio = rng.uniform(0.08, 0.14)
                due_amount = round(base_income * due_ratio / 100) * 100
                due = [due_amount] * 12
                paid = list(due)  # no missed payments for stable borrowers
                household_income = base_income
                savings_buffer = round(rng.uniform(0.5, 3.0) * (sum(expenses) / 12) / 100) * 100
                other_loan_emi = round(base_income * rng.uniform(0, 0.10) / 100) * 100
                mfi_loan_amount = rng.choice([25000, 30000, 35000, 40000, 45000, 50000])
                mfi_tenure_months = rng.choice([10, 12, 14, 18, 24])

            roster.append({
                "borrower_id": borrower_id,
                "name": name,
                "persona_note": note,
                "household_income": household_income,
                "savings_buffer": savings_buffer,
                "other_loan_emi": other_loan_emi,
                "mfi_loan_amount": mfi_loan_amount,
                "mfi_tenure_months": mfi_tenure_months,
                "income": income,
                "expenses": expenses,
                "due": due,
                "paid": paid,
            })

        for a_idx, b_idx_rel, rel_type, weight in spec["edges"]:
            roster.append({
                "_edge": (member_ids[a_idx], member_ids[b_idx_rel], rel_type, weight)
            })

    return roster


def generate_profiles() -> pd.DataFrame:
    """Generates the static borrower profile data."""
    data = list(CORE_DEMO_PROFILES)
    for entry in _build_placeholder_roster():
        if "_edge" in entry:
            continue
        data.append([
            entry["borrower_id"], entry["name"], entry["persona_note"],
            entry["household_income"], entry["savings_buffer"], entry["other_loan_emi"],
            entry["mfi_loan_amount"], entry["mfi_tenure_months"],
        ])

    columns = [
        "borrower_id", "name", "persona_note", "household_income",
        "savings_buffer", "other_loan_emi", "mfi_loan_amount", "mfi_tenure_months"
    ]
    return pd.DataFrame(data, columns=columns)


def generate_monthly_data() -> pd.DataFrame:
    """Generates the 12-month trailing financial records for each borrower."""
    data = list(CORE_DEMO_MONTHLY)
    for entry in _build_placeholder_roster():
        if "_edge" in entry:
            continue
        borrower_id = entry["borrower_id"]
        for m in range(12):
            data.append([
                borrower_id, m + 1,
                entry["income"][m], entry["expenses"][m],
                entry["due"][m], entry["paid"][m],
            ])

    columns = [
        "borrower_id", "month", "income", "expenses",
        "mfi_repayment_due", "mfi_repayment_paid"
    ]
    return pd.DataFrame(data, columns=columns)


def generate_relationships() -> pd.DataFrame:
    """Generates the financial dependency graph edge list."""
    data = list(CORE_DEMO_RELATIONSHIPS)
    for entry in _build_placeholder_roster():
        if "_edge" in entry:
            data.append(list(entry["_edge"]))

    columns = ["borrower_a", "borrower_b", "relationship_type", "weight"]
    return pd.DataFrame(data, columns=columns)


if __name__ == "__main__":
    # Ensure the data directory exists
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Generate the DataFrames
    df_profile = generate_profiles()
    df_monthly = generate_monthly_data()
    df_relationships = generate_relationships()

    # Write files to target locations using config paths
    df_profile.to_csv(config.PROFILE_CSV, index=False)
    df_monthly.to_csv(config.MONTHLY_CSV, index=False)
    df_relationships.to_csv(config.RELATIONSHIPS_CSV, index=False)

    # Print confirmations
    print(f"✅ Generated {len(df_profile)} rows in {config.PROFILE_CSV.name}")
    print(f"✅ Generated {len(df_monthly)} rows in {config.MONTHLY_CSV.name}")
    print(f"✅ Generated {len(df_relationships)} rows in {config.RELATIONSHIPS_CSV.name}")