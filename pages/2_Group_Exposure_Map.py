import matplotlib.pyplot as plt
import networkx as nx
import streamlit as st

from config import BG, CARD, MINT, MUTED, STATE_COLOR, WHITE, risk_color
from engine.network import (
    assign_microfinance_groups,
    build_graph,
    summarize_microfinance_groups,
)
from ui.theme import inject_global_css, render_page_header, render_sidebar_brand  # <-- ADD IMPORT
from utils.analysis import analyze_group_baseline
from utils.helpers import load_all_data_or_stop


def main():
    st.set_page_config(page_title="ResilienceOS", page_icon="🛡️", layout="wide") # <-- ADD THIS LINE
    inject_global_css()
    render_sidebar_brand()

    render_page_header(
        "Group Exposure Map",
        "Manage connected borrower groups, not isolated borrower records",
    )

    if "target_borrower" not in st.session_state:
        st.session_state.target_borrower = None

    profile_df, monthly_df, relationships_df = load_all_data_or_stop()
    baseline_df = analyze_group_baseline(profile_df, monthly_df)
    borrower_ids = profile_df["borrower_id"].tolist()
    graph = build_graph(relationships_df, borrower_ids)
    group_by_borrower = assign_microfinance_groups(graph)
    group_summary = summarize_microfinance_groups(graph, baseline_df)
    borrower_states = dict(zip(baseline_df["borrower_id"], baseline_df["state"]))
    name_map = dict(zip(baseline_df["borrower_id"], baseline_df["name"]))

    total_groups = len(group_summary)
    exposed_groups = int((group_summary["highest_state"] != "Stable").sum())
    highest_group = group_summary.sort_values("max_risk", ascending=False).iloc[0]

    metric_a, metric_b, metric_c, metric_d = st.columns(4)
    metric_a.metric("Management groups", total_groups)
    metric_b.metric("Groups needing action", exposed_groups)
    
    metric_c.metric("Highest-risk group", highest_group["group"].replace("Group ", ""))
    metric_d.metric("Group peak risk", f"{highest_group['max_risk']:.0f}")

    st.markdown("### Choose a management view")

    default_group_idx = 0
    if st.session_state.target_borrower:
        borrower_to_id = dict(zip(profile_df["name"], profile_df["borrower_id"]))
        target_id = borrower_to_id.get(st.session_state.target_borrower)
        if target_id and target_id in group_by_borrower:
            target_group = group_by_borrower[target_id]
            group_list = group_summary["group"].tolist()
            if target_group in group_list:
                default_group_idx = group_list.index(target_group)


    group_list = group_summary["group"].tolist()

    group_labels = dict(
        zip(group_summary["group"], group_summary["group_label"])
    )

    # Make sure the default index is always valid
    default_group_idx = min(
        default_group_idx,
        max(0, len(group_list) - 1)
    )

    selected_group = st.selectbox(
        "Management group",
        options=group_list,
        index=default_group_idx,
        format_func=lambda group: group_labels.get(group, str(group)),
        label_visibility="collapsed",
    )

    selected_ids = [
        borrower_id
        for borrower_id, group in group_by_borrower.items()
        if group == selected_group
    ]
    selected_summary = group_summary[group_summary["group"] == selected_group].iloc[0]
    selected_baseline = baseline_df[baseline_df["borrower_id"].isin(selected_ids)].copy()
    highest_risk = selected_baseline.sort_values("severity_score", ascending=False).iloc[0]

    group_col, action_col = st.columns([1.35, 1])
    with group_col:
        st.markdown(
            f"### {selected_group}"
            f"<span style='color:{MUTED};font-size:14px;font-weight:400;'>"
            f"  · {int(selected_summary['borrowers'])} borrowers</span>",
            unsafe_allow_html=True,
        )
        st.caption(
            f"Led by {selected_summary['highest_state'].lower()} risk. "
            "Edges represent observed economic or social dependency."
        )
    with action_col:
        st.markdown(
            f"<div style='background:{CARD};border-left:4px solid "
            f"{risk_color(float(highest_risk['severity_score']))};padding:12px 16px;"
            f"border-radius:8px;margin-top:8px;'>"
            f"<div style='color:{MUTED};font-size:11px;text-transform:uppercase;'>Priority borrower</div>"
            f"<div style='color:{WHITE};font-size:20px;font-weight:700;'>{highest_risk['name']}</div>"
            f"<div style='color:{MUTED};font-size:13px;'>{highest_risk['state']} · "
            f"{highest_risk['severity_score']:.0f}/100 risk</div></div>",
            unsafe_allow_html=True,
        )
        st.write("")
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button(f"Inspect {highest_risk['name']} →", use_container_width=True):
                st.session_state.target_borrower = highest_risk["name"]
                st.switch_page("pages/1_Borrower_Intelligence.py")
        with btn_col2:
            if st.button(f"Shock in Lab ⚡", use_container_width=True):
                st.session_state.target_borrower = highest_risk["name"]
                st.switch_page("pages/3_Intervention_Lab.py")

    st.write("")
    graph_col, table_col = st.columns([1.35, 1])
    selected_graph = graph.subgraph(selected_ids).copy()

    with graph_col:
        fig, ax = plt.subplots(figsize=(10, 6.5), dpi=200)
        fig.patch.set_facecolor(BG)
        ax.set_facecolor(BG)
        if len(selected_graph) > 1:
            pos = nx.spring_layout(selected_graph, seed=42, k=5, iterations=100)
        else:
            pos = {selected_ids[0]: (0.5, 0.5)}

        node_colors = [STATE_COLOR[borrower_states[node]] for node in selected_graph.nodes()]
        node_labels = {node: name_map[node] for node in selected_graph.nodes()}
        node_sizes = [
            1800 if borrower_states[node] != "Stable" else 1300
            for node in selected_graph.nodes()
        ]
        edge_widths = [
            selected_graph[u][v].get("weight", 0) * 5
            for u, v in selected_graph.edges()
        ]

        nx.draw_networkx_edges(
            selected_graph, pos, ax=ax, width=edge_widths, edge_color=MUTED, alpha=0.65
        )
        nx.draw_networkx_nodes(
            selected_graph,
            pos,
            ax=ax,
            node_color=node_colors,
            node_size=node_sizes,
            edgecolors=[
                MINT if node == highest_risk["borrower_id"] else BG
                for node in selected_graph.nodes()
            ],
            linewidths=3,
        )
        nx.draw_networkx_labels(
            selected_graph,
            pos,
            labels=node_labels,
            font_color=WHITE,
            font_weight="bold",
            ax=ax,
        )
        ax.set_title(
            "Dependency network",
            color=WHITE,
            loc="left",
            pad=16,
            fontsize=14,
            fontweight="bold",
        )
        ax.axis("off")
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)
        
        st.markdown("""
        <div style="font-size: 12px; color: #9AA7B8; margin-top: 8px; background: #141C2E; padding: 12px 20px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center;">
            <b>Edge Strength:</b>
            <div style="display: flex; align-items: center;"><div style="width: 24px; height: 4px; background: #9AA7B8; margin-right: 8px; border-radius: 2px;"></div> <span style="color:#FFF;">Strong</span></div>
            <div style="display: flex; align-items: center;"><div style="width: 24px; height: 2px; background: #9AA7B8; margin-right: 8px; border-radius: 1px;"></div> <span style="color:#FFF;">Medium</span></div>
            <div style="display: flex; align-items: center;"><div style="width: 24px; height: 1px; background: #9AA7B8; margin-right: 8px;"></div> <span style="color:#FFF;">Weak</span></div>
        </div>
        """, unsafe_allow_html=True)
        st.caption("The mint outline marks the first borrower to review.")

    with table_col:
        st.markdown("#### Group action queue")
        action_df = selected_baseline.sort_values("severity_score", ascending=False)[
            ["name", "state", "severity_score", "debt_burden_ratio", "cash_buffer_months"]
        ].rename(
            columns={
                "name": "Borrower",
                "state": "State",
                "severity_score": "Risk",
                "debt_burden_ratio": "Debt",
                "cash_buffer_months": "Buffer",
            }
        )
        action_df["Risk"] = action_df["Risk"].round(0).astype(int)
        action_df["Debt"] = (action_df["Debt"] * 100).round(0).astype(int).astype(str) + "%"
        action_df["Buffer"] = action_df["Buffer"].round(1).astype(str) + " mo"
        st.dataframe(action_df, use_container_width=True, hide_index=True)
        
        # QUICK ACTION ROW 1: Inspect any borrower from the table
        st.markdown("<div style='margin-top: 10px; color: #9AA7B8; font-size: 11px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase;'>Quick Inspect</div>", unsafe_allow_html=True)
        q_col1, q_col2 = st.columns([1.5, 1])
        with q_col1:
            jump_borrower = st.selectbox(
                "Select borrower", 
                options=action_df["Borrower"].tolist(),
                label_visibility="collapsed",
                key="jump_b"
            )
        with q_col2:
            if st.button("Profile →", use_container_width=True, key="btn_jump_b"):
                st.session_state.target_borrower = jump_borrower
                st.switch_page("pages/1_Borrower_Intelligence.py")

    st.markdown("---")
    st.markdown("### Portfolio groups")
    
    portfolio_df = group_summary[
        ["group", "borrowers", "highest_state", "average_risk", "average_debt", "average_buffer"]
    ].rename(
        columns={
            "group": "Group",
            "borrowers": "Borrowers",
            "highest_state": "Highest state",
            "average_risk": "Avg risk",
            "average_debt": "Avg debt",
            "average_buffer": "Avg buffer",
        }
    )
    portfolio_df["Avg risk"] = portfolio_df["Avg risk"].round(0).astype(int)
    portfolio_df["Avg debt"] = (
        (portfolio_df["Avg debt"] * 100).round(0).astype(int).astype(str) + "%"
    )
    portfolio_df["Avg buffer"] = portfolio_df["Avg buffer"].round(1).astype(str) + " mo"
    st.dataframe(portfolio_df, use_container_width=True, hide_index=True)

    # QUICK ACTION ROW 2: Load any group directly from the bottom table
    st.markdown("<div style='margin-top: 6px; color: #9AA7B8; font-size: 11px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase;'>Quick Navigate</div>", unsafe_allow_html=True)
    g_col1, g_col2 = st.columns([1, 4])
    with g_col1:
        jump_group = st.selectbox(
            "Select group",
            options=portfolio_df["Group"].tolist(),
            label_visibility="collapsed",
            key="jump_g"
        )
    with g_col2:
        if st.button("Load Group Map ↑", use_container_width=False, key="btn_jump_g"):
            # Update state to the riskiest borrower in the selected group so the top layout re-renders perfectly
            target_ids = [bid for bid, g in group_by_borrower.items() if g == jump_group]
            top_b_df = baseline_df[baseline_df["borrower_id"].isin(target_ids)].sort_values("severity_score", ascending=False)
            if not top_b_df.empty:
                st.session_state.target_borrower = top_b_df.iloc[0]["name"]
                st.rerun()


if __name__ == "__main__":
    main()