"""ResilienceOS portfolio command center."""

import streamlit as st

st.set_page_config(
    page_title="ResilienceOS",
    page_icon="🛡️",
    layout="wide",
)

import pandas as pd  # noqa: E402

from config import CARD, MINT, MUTED, STATE_COLOR, STATE_EMOJI, WHITE, risk_color  # noqa: E402
from engine.network import assign_microfinance_groups, build_graph, summarize_microfinance_groups  # noqa: E402
from ui.theme import inject_global_css, render_sidebar_brand  # noqa: E402
from utils.analysis import analyze_group_baseline  # noqa: E402
from utils.helpers import load_all_data_or_stop  # noqa: E402

inject_global_css()
render_sidebar_brand()

# PROBLEM STATEMENT FRAME BANNER
st.markdown(
    f"""
    <div style="background:#0F1A2E; border-left:3px solid {MINT}; padding:12px 16px; border-radius:8px; margin-bottom:0px;">
        <span style="color:{MINT}; font-weight:700; font-size:13px; letter-spacing:0.05em;">WHEN ONE BORROWER FALLS BEHIND</span>
        <span style="color:{MUTED}; margin-left:12px; font-size:14px;">Identify stress · Understand relationships · Predict propagation · Intervene early</span>
    </div>
    """,
    unsafe_allow_html=True,
)

profile_df, monthly_df, relationships_df = load_all_data_or_stop()
baseline_df = analyze_group_baseline(profile_df, monthly_df)
graph = build_graph(relationships_df, profile_df["borrower_id"].tolist())
group_by_borrower = assign_microfinance_groups(graph)
group_summary = summarize_microfinance_groups(graph, baseline_df)

stable_count = int((baseline_df["state"] == "Stable").sum())
watch_count = len(baseline_df) - stable_count
action_count = int((group_summary["highest_state"] != "Stable").sum())
priority = baseline_df.sort_values("severity_score", ascending=False).iloc[0]
priority_group = group_by_borrower[priority["borrower_id"]]

st.markdown(
    f"""
    <div style="padding: 18px 0 18px 0;">
        <div style="color:{MINT};font-size:11px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;">
            Portfolio command center
        </div>
        <div style="color:{WHITE};font-size:42px;font-weight:800;line-height:1.1;margin-top:8px;">
            ResilienceOS
        </div>
        <div style="color:{MUTED};font-size:16px;line-height:1.5;margin-top:10px;max-width:720px;">
            See where borrower stress is concentrated, understand how it can travel,
            and decide which group needs attention first.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

metric_a, metric_b, metric_c, metric_d = st.columns(4)
metric_a.metric("Borrowers monitored", len(baseline_df))
metric_b.metric("Stable today", stable_count)
metric_c.metric("Borrowers on watch", watch_count)
metric_d.metric("Groups needing action", action_count)

st.write("")

# --- ROW 1: HERO ACTION & PRIORITY QUEUE ---
hero_col, queue_col = st.columns([1, 1.4])

with hero_col:
    st.markdown(
        f"""
        <div style="background:{CARD};border-left:5px solid {risk_color(float(priority['severity_score']))};
                    border-radius:10px;padding:22px 24px;height:100%; display:flex; flex-direction:column; justify-content:center;">
            <div style="color:{MUTED};font-size:11px;text-transform:uppercase;letter-spacing:.12em;">
                Next management action
            </div>
            <div style="color:{WHITE};font-size:32px;font-weight:800;margin-top:8px;">
                Review {priority['name']}
            </div>
            <div style="color:{MUTED};font-size:14px;margin-top:6px;">
                {STATE_EMOJI.get(priority['state'], '')} {priority['state']} stress ·
                {priority['severity_score']:.0f}/100 severity · {priority_group}
            </div>
            <div style="color:{WHITE};font-size:14px;line-height:1.5;margin-top:20px;">
                Start with the highest-risk borrower, then inspect the surrounding group
                before choosing an intervention.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with queue_col:
    st.markdown("#### Individual Priority Queue")
    queue = baseline_df.sort_values("severity_score", ascending=False).head(5).copy()
    queue["Borrower"] = queue["name"]
    queue["State"] = queue["state"].map(lambda state: f"{STATE_EMOJI.get(state, '')} {state}")
    queue["Group"] = queue["borrower_id"].map(group_by_borrower)
    
    st.dataframe(
        queue[["Borrower", "Group", "State", "severity_score", "debt_burden_ratio"]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Borrower": st.column_config.TextColumn("Borrower", width="medium"),
            "Group": st.column_config.TextColumn("Group", width="small"),
            "State": st.column_config.TextColumn("Status", width="medium"),
            "severity_score": st.column_config.ProgressColumn(
                "Risk Score", help="Engine Severity Score", min_value=0, max_value=100, width="medium"
            ),
            "debt_burden_ratio": st.column_config.NumberColumn(
                "Debt Burden", help="EMI / Income Ratio", format="%.2f", width="small"
            ),
        }
    )

st.write("---")

# --- ROW 2: CHARTS & GROUP LIST ---
chart_col, groups_col = st.columns([1, 1.4])

with chart_col:
    st.markdown("#### Portfolio Risk Profile")
    state_counts = baseline_df["state"].value_counts().reindex(
        ["Stable", "Temporary", "Vulnerable", "Structural"], fill_value=0
    )
    st.bar_chart(state_counts, color=MINT, height=270)
    st.caption("Baseline classification before any new shock is applied.")

with groups_col:
    st.markdown("#### Group Pulse & Action Board")
    group_display = group_summary.copy()
    group_display["State"] = group_display["highest_state"].map(lambda s: f"{STATE_EMOJI.get(s, '')} {s}")
    
    st.dataframe(
        group_display[["group", "borrowers", "State", "max_risk", "average_risk"]].sort_values("max_risk", ascending=False),
        use_container_width=True,
        hide_index=True,
        height=270,
        column_config={
            "group": st.column_config.TextColumn("Group", width="medium"),
            "borrowers": st.column_config.NumberColumn("Members", width="small"),
            "State": st.column_config.TextColumn("Peak Status", width="medium"),
            "max_risk": st.column_config.ProgressColumn(
                "Peak Risk", min_value=0, max_value=100, width="medium"
            ),
            "average_risk": st.column_config.NumberColumn(
                "Avg Risk", format="%d", width="small"
            ),
        }
    )

st.write("")

# METHODOLOGY EXPANDER
with st.expander("System Methodology & Requirements", expanded=False):
    st.markdown(f"""
    <div style="font-size: 13px; color: {MUTED};">
    <b>Analysis Flow:</b><br>
    COLLECT DATA → ASSESS STRESS → BUILD NETWORK → MODEL PROPAGATION → IDENTIFY RISK TYPE → EARLY WARNING → TARGETED INTERVENTION<br><br>
    
    <b>Data Requirements:</b><br>
    • <b>Borrower Profile:</b> Household income, savings buffer, other loan EMIs.<br>
    • <b>Cashflow History:</b> 12-month trailing income, expenses, and MFI repayment history.<br>
    • <b>Relationship Graph:</b> Economic and social connections with dependency weights (0 to 1).
    </div>
    """, unsafe_allow_html=True)

st.write("")
st.markdown(
    f"""
    <div style="background:{CARD};border-radius:10px;padding:16px 20px;margin-top:10px;">
        <span style="color:{MINT};font-weight:800;">NEXT</span>
        <span style="color:{WHITE};margin-left:10px;">
            Navigate to <b>Borrower Intelligence</b> to inspect a profile,
            or open <b>Intervention Lab</b> to simulate a shock and compare responses.
        </span>
    </div>
    """,
    unsafe_allow_html=True,
)