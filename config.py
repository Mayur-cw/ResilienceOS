"""
Central configuration for ResilienceOS — every threshold, path, and color lives here
so the demo can be tuned from one place. Every other file should import from this
module rather than hardcoding these values.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

PROFILE_CSV = DATA_DIR / "borrower_profile.csv"
MONTHLY_CSV = DATA_DIR / "borrower_monthly.csv"
RELATIONSHIPS_CSV = DATA_DIR / "relationships.csv"

TEMPORARY_TREND_CUTOFF = -20
STRUCTURAL_TREND_CUTOFF = -15
VULNERABLE_TREND_CUTOFF = -10
MIN_BUFFER_MONTHS_FOR_TEMPORARY = 1.5
RBI_DEBT_BURDEN_CAP = 0.50

SEVERITY_BASE = {
    "Stable": 10,
    "Temporary": 50,
    "Vulnerable": 65,
    "Structural": 90,
}

SEVERITY_EXTRA_CAP = 20

MAX_HOPS = 3
DECAY = 0.6
IMPACT_ALERT_THRESHOLD = 20

INTERVENTION_CANDIDATES = {
    "Do Nothing": (1.0, 1.0),
    "Group Restructuring": (0.6, 0.6),
    "Grace Period (Targeted)": (0.45, 0.75),
    "Targeted Support (Recommended)": (0.25, 0.25),
}

INTERVENTION_ORDER = list(INTERVENTION_CANDIDATES.keys())
HEALTHY_IMPACT_WEIGHT = 0.6

BG = "#0B1220"
CARD = "#141C2E"
MINT = "#02C39A"
MINT_DARK = "#0F3A33"
ICE = "#8FD9FF"
MUTED = "#9AA7B8"
WHITE = "#FFFFFF"
RED = "#EB5757"
ORANGE = "#F2994A"
AMBER = "#F5C243"
GREEN = "#27AE60"

STATE_COLOR = {
    "Stable": GREEN,
    "Temporary": AMBER,
    "Vulnerable": ORANGE,
    "Structural": RED,
}

STATE_EMOJI = {
    "Stable": "🟢",
    "Temporary": "🟡",
    "Vulnerable": "🟠",
    "Structural": "🔴",
}


def risk_color(score: float) -> str:
    """Map a 0-100 impact/risk score to a hex color, same bands used everywhere."""
    if score < 20:
        return GREEN
    if score < 40:
        return AMBER
    if score < 70:
        return ORANGE
    return RED