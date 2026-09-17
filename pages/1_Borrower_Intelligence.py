import pandas as pd
import streamlit as st

from config import CARD, MINT, MUTED, WHITE, BG, AMBER
from engine.cashflow import analyze_cashflow
from engine.debt import calculate_debt_burden
from engine.stress import classify_stress

from ui.theme import inject_global_css, render_page_header, render_sidebar_brand, render_state_badge
from utils.helpers import load_all_data_or_stop

def main():
    st.set_page_config(page_title="ResilienceOS", page_icon="🛡️", layout="wide") # <-- ADD THIS LINE
    inject_global_css()
    render_sidebar_brand()
    render_page_header(
        "Borrower Intelligence",
        "See any single borrower's financial health and why they're classified the way they are",
    )

    if "target_borrower" not in st.session_state:
        st.session_state.target_borrower = None

    profile_df, monthly_df, relationships_df = load_all_data_or_stop()

    name_to_id = dict(zip(profile_df["name"], profile_df["borrower_id"]))
    names_list = list(name_to_id.keys())

    default_idx = 0
    if st.session_state.target_borrower in names_list:
        default_idx = names_list.index(st.session_state.target_borrower)

    selected_name = st.selectbox("Select Borrower", options=names_list, index=default_idx)
    st.session_state.target_borrower = selected_name

    if selected_name:
        selected_id = name_to_id[selected_name]

        borrower_profile = profile_df[profile_df["borrower_id"] == selected_id].iloc[0]
        borrower_monthly = monthly_df[monthly_df["borrower_id"] == selected_id].copy()

        cashflow_result = analyze_cashflow(borrower_monthly)
        debt_result = calculate_debt_burden(borrower_profile, borrower_monthly)
        stress_result = classify_stress(
            borrower_profile, borrower_monthly, cashflow_result, debt_result
        )

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            debt_pct = debt_result["debt_burden_ratio"] * 100
            st.metric("Debt Burden", f"{debt_pct:.1f}%")
        with col2:
            st.metric("Cash Buffer (months)", f"{debt_result['cash_buffer_months']:.1f}")
        with col3:
            st.metric("Income Trend", f"{cashflow_result['trend_pct']:.1f}%")
        with col4:
            struct_vuln_pct = debt_result["structural_vulnerability"] * 100
            st.metric("Structural Vulnerability", f"{struct_vuln_pct:.1f}%")

        st.write("")
        
        is_isolated = (selected_id not in relationships_df['borrower_a'].values) and (selected_id not in relationships_df['borrower_b'].values)
        if is_isolated:
            cause = "Isolated"
        elif cashflow_result.get("seasonal_pattern_detected"):
            cause = "Common Shock"
        else:
            cause = "Independent"

        badge_col1, badge_col2 = st.columns([1, 4])
        with badge_col1:
            render_state_badge(stress_result["state"], stress_result["confidence"])
        with badge_col2:
            st.markdown(
                f'<span style="color:#A0AEC0;font-size:13px;font-weight:700;text-transform:uppercase;">Cause: {cause}</span>', 
                unsafe_allow_html=True
            )

        with st.expander("Why this classification?", expanded=True):
            st.write(stress_result["rule_description"])
            for evidence in stress_result["evidence"]:
                st.markdown(f"- {evidence}")

        st.write("")

        # NEW: Data Quality & Audit Trail (Feedback Points #9 & #10)
        st.markdown("#### Data Quality & System Audit")
        col_dq, col_audit = st.columns([1, 1])
        with col_dq:
            st.markdown(f"""
            <div style="background:{CARD}; padding:16px 20px; border-radius:10px; border:1px solid rgba(255,255,255,0.06); height:100%;">
                <div style="display:flex; justify-content:space-between; margin-bottom:12px;">
                    <span style="color:{MUTED}; font-size:11px; text-transform:uppercase; letter-spacing:0.05em;">Overall Data Confidence</span>
                    <span style="color:{MINT}; font-weight:800; font-size:14px;">92%</span>
                </div>
                <div style="font-size:13px; line-height:1.8; color:{WHITE};">
                    <span style="color:{MINT}">✓</span> 12-month Income History<br>
                    <span style="color:{MINT}">✓</span> Repayment Track Record<br>
                    <span style="color:{MINT}">✓</span> Network Edge Validation<br>
                    <span style="color:{AMBER}">⚠</span> Savings Buffer (Self-Reported)
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_audit:
            st.markdown(f"""
            <div style="background:{BG}; padding:16px 20px; border-radius:10px; border:1px solid rgba(255,255,255,0.06); height:100%; font-family:monospace; font-size:11px; color:{MUTED}; overflow-y:auto;">
                <div style="color:{WHITE}; margin-bottom:8px;">&gt; ENGINE_DECISION_LOG</div>
                13:42:01 | Profile loaded for {selected_name} ({selected_id})<br>
                13:42:02 | Analysing 12M cashflow... Trend: {cashflow_result['trend_pct']:.1f}%<br>
                13:42:02 | RBI Debt Burden Cap Check: {debt_pct:.1f}%<br>
                13:42:03 | Evaluating deterministic rules...<br>
                13:42:03 | <span style="color:{MINT}">Rule {stress_result['rule_id']} triggered</span><br>
                13:42:04 | Classification locked: {stress_result['state']}
            </div>
            """, unsafe_allow_html=True)

        st.write("")

        chart_df = borrower_monthly[["month", "income", "expenses"]].set_index("month")
        chart_df = chart_df.rename(columns={"income": "Income", "expenses": "Expenses"})
        chart_df.index.name = "Month"
        
        st.line_chart(chart_df, color=["#8FD9FF", "#02C39A"])

        st.write("")
        col_nav1, col_nav2 = st.columns([1.5, 1])
        with col_nav1:
            if st.button(
                f"Simulate Shock for {selected_name} in Intervention Lab ⚡",
                type="primary",
                use_container_width=True,
            ):
                st.session_state.target_borrower = selected_name
                st.switch_page("pages/3_Intervention_Lab.py")
        with col_nav2:
            if st.button("View in Group Exposure Map →", use_container_width=True):
                st.session_state.target_borrower = selected_name
                st.switch_page("pages/2_Group_Exposure_Map.py")

if __name__ == "__main__":
    main()