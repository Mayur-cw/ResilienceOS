import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import streamlit as st

from config import (
    BG,
    CARD,
    GREEN,
    ICE,
    MINT,
    MINT_DARK,
    MUTED,
    WHITE,
    RED,
    AMBER,
    risk_color,
)
from engine.cashflow import analyze_cashflow, apply_shock
from engine.debt import calculate_debt_burden
from engine.intervention import evaluate_interventions
from engine.network import build_graph
from engine.propagation import propagate_shock
from engine.stress import classify_stress
from ui.theme import (
    inject_global_css,
    render_page_header,
    render_state_badge,
    render_sidebar_brand,
)
from utils.analysis import analyze_group_baseline
from utils.helpers import load_all_data_or_stop

st.set_page_config(page_title="ResilienceOS", page_icon="🛡️", layout="wide")

inject_global_css()
render_sidebar_brand()

render_page_header(
    "The Intervention Lab",
    "Inject a shock, watch it spread, and compare what the lender should do about it",
)

if "simulation_results" not in st.session_state:
    st.session_state.simulation_results = None

if "target_borrower" not in st.session_state:
    st.session_state.target_borrower = None

profile_df, monthly_df, relationships_df = load_all_data_or_stop()
baseline_df = analyze_group_baseline(profile_df, monthly_df)

id_to_name = dict(zip(profile_df["borrower_id"], profile_df["name"]))
name_to_id = dict(zip(profile_df["name"], profile_df["borrower_id"]))
profile_by_id = {row["borrower_id"]: row for _, row in profile_df.iterrows()}

all_ids = profile_df["borrower_id"].tolist()
all_names = profile_df["name"].tolist()

if st.session_state.target_borrower in all_names:
    default_source_index = all_names.index(st.session_state.target_borrower)
else:
    default_source_index = all_names.index("Maya") if "Maya" in all_names else 0

st.markdown("#### Configure the shock")

control_source, control_shock, control_duration, control_sim, control_reset = st.columns(
    [2, 2.2, 1.4, 1.2, 1.4]
)

with control_source:
    source_name = st.selectbox(
        "Source borrower",
        options=all_names,
        index=default_source_index,
    )
    st.session_state.target_borrower = source_name

with control_shock:
    shock_pct = st.slider(
        "Income shock (%)",
        min_value=-100,     
        max_value=-0,
        value=-40,
        step=5,
    )
with control_duration:
    duration = st.select_slider(
        "Duration (months)",
        options=[1, 2, 3, 4, 5, 6], 
        value=2,
    )
with control_sim:
    st.write("")
    simulate_clicked = st.button("Simulate", type="primary", use_container_width=True)
with control_reset:
    st.write("")
    reset_clicked = st.button("Reset Simulation", use_container_width=True)

if reset_clicked:
    st.session_state.simulation_results = None
    st.rerun()

if simulate_clicked:
    with st.spinner("Propagating shock through network graph..."):
        source_id = name_to_id[source_name]
        source_profile = profile_by_id[source_id]

        source_monthly = (
            monthly_df[monthly_df["borrower_id"] == source_id]
            .sort_values("month")
            .reset_index(drop=True)
        )

        shocked_monthly = apply_shock(source_monthly, shock_pct, duration)
        cashflow_result = analyze_cashflow(shocked_monthly)
        debt_result = calculate_debt_burden(source_profile, shocked_monthly)
        stress_result = classify_stress(
            source_profile, shocked_monthly, cashflow_result, debt_result
        )

        vulnerability_scores = dict(
            zip(
                baseline_df["borrower_id"],
                baseline_df["structural_vulnerability"],
            )
        )

        full_graph = build_graph(relationships_df, all_ids)
        
        demo_group = ["B01", "B02", "B03", "B04", "B05", "B06", "B07"]
        if source_id in demo_group:
            visible_ids = demo_group
        else:
            visible_ids = list(nx.node_connected_component(full_graph, source_id))
            
        graph = full_graph.subgraph(visible_ids).copy()

        propagation_result = propagate_shock(
            source_id,
            stress_result["severity_score"],
            graph,
            vulnerability_scores,
        )

        interventions = evaluate_interventions(source_id, propagation_result)

        st.session_state.simulation_results = {
            "source_id": source_id,
            "source_name": source_name,
            "source_monthly": source_monthly,
            "shocked_monthly": shocked_monthly,
            "stress_result": stress_result,
            "propagation_result": propagation_result,
            "interventions": interventions,
            "graph": graph,
            "visible_ids": visible_ids, 
        }

results = st.session_state.simulation_results

if results is None:
    st.info(
        "Select a borrower, set a shock, and press Simulate to see "
        "how financial stress propagates and how to intervene."
    )
    st.stop()

source_id = results["source_id"]
source_name = results["source_name"]
source_monthly = results["source_monthly"]
shocked_monthly = results["shocked_monthly"]
stress_result = results["stress_result"]
propagation_result = results["propagation_result"]
interventions = results["interventions"]
graph = results["graph"]
visible_ids = results.get("visible_ids", all_ids) 

if isinstance(interventions, dict):
    interventions = list(interventions.values())

if isinstance(propagation_result, dict):
    propagation_by_id = propagation_result
elif isinstance(propagation_result, list):
    propagation_by_id = {
        item.get("borrower_id"): item
        for item in propagation_result
        if item.get("borrower_id")
    }
else:
    propagation_by_id = {}

st.markdown("---")
st.markdown(f"### 1. Shock Impact on {source_name}")

col_class, col_chart = st.columns([1, 1.2])

with col_class:
    render_state_badge(stress_result["state"], stress_result.get("confidence"))
    with st.expander("Why this classification?", expanded=True):
        st.markdown(f"**Rule:** {stress_result.get('rule_description', 'N/A')}")

        evidence = stress_result.get("evidence", [])
        if evidence:
            st.markdown("**Evidence:**")
            for item in evidence:
                st.markdown(f"- {item}")

        st.markdown(
            f"**Severity score:** {stress_result.get('severity_score', 0):.1f}/100"
        )

with col_chart:
    chart_df = pd.DataFrame(
        {
            "Original Income": source_monthly["income"].to_numpy(),
            "Shocked Income": shocked_monthly["income"].to_numpy(),
        },
        index=source_monthly["month"].to_numpy(),
    )
    chart_df.index.name = "Month"
    st.line_chart(chart_df, color=[ICE, MINT])

st.write("")

st.markdown("### 2. Group Propagation Map")

col_graph, col_table = st.columns([1.5, 1])

with col_graph:
    fig, ax = plt.subplots(figsize=(9, 6.5), dpi=200)
    ax.set_facecolor(BG)
    fig.patch.set_facecolor(BG)

    pos = nx.spring_layout(graph, seed=42, k=5, iterations=100)
    node_colors, node_sizes, node_edge_colors = [], [], []

    for node in graph.nodes():
        if node in propagation_by_id:
            info = propagation_by_id[node]
            impact = float(info.get("impact_score", info.get("impact", 0)))
            node_colors.append(risk_color(impact))
            node_sizes.append(2500 if node == source_id else 1800)
        else:
            node_colors.append(GREEN)
            node_sizes.append(1500 if node == source_id else 1100)
        node_edge_colors.append(MINT if node == source_id else BG)

    edges = list(graph.edges(data=True))
    if edges:
        edge_widths = [max(1.0, float(d.get("weight", 0.0)) * 6) for _, _, d in edges]
        nx.draw_networkx_edges(
            graph,
            pos,
            ax=ax,
            width=edge_widths,
            edge_color=MUTED,
            alpha=0.8,
        )

    nx.draw_networkx_nodes(
        graph,
        pos,
        ax=ax,
        node_color=node_colors,
        node_size=node_sizes,
        edgecolors=node_edge_colors,
        linewidths=3,
    )

    labels = {n: id_to_name.get(n, n) for n in graph.nodes()}
    nx.draw_networkx_labels(
        graph,
        pos,
        labels=labels,
        ax=ax,
        font_color=WHITE,
        font_size=11,
        font_weight="bold",
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
    
    st.caption("Node colour reflects post-shock impact. Edge thickness shows relationship strength.")

with col_table:
    impact_rows = []
    for bid in visible_ids:
        b_name = id_to_name.get(bid, bid)
        is_iso = (bid not in relationships_df['borrower_a'].values) and (bid not in relationships_df['borrower_b'].values)
        
        if bid in propagation_by_id:
            info = propagation_by_id[bid]
            impact = float(info.get("impact_score", info.get("impact", 0)))
            hops = info.get("hop_distance", info.get("hops", 0))
            raw_path = info.get("primary_path", info.get("path", [bid]))
            if isinstance(raw_path, str):
                raw_path = [raw_path]
            path_names = " → ".join(id_to_name.get(p, p) for p in raw_path)
        else:
            impact = 0.0
            hops = "—"
            path_names = "Isolated" if is_iso else "Untouched"

        impact_rows.append({
            "Borrower": b_name,
            "Impact": round(impact, 1),
            "Hops": hops,
            "Path": path_names,
        })

    impact_df = (
        pd.DataFrame(impact_rows)
        .sort_values("Impact", ascending=False)
        .reset_index(drop=True)
    )
    st.dataframe(impact_df, use_container_width=True, hide_index=True)

st.write("")

st.markdown("### 3. Contagion Forecast & Interventions")

do_nothing = next((c for c in interventions if c["name"] == "Do Nothing"), None)
recommended = next((c for c in interventions if c.get("recommended")), None)

if do_nothing and recommended:
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        st.markdown(f"""
        <div style="background:{CARD}; border-left:4px solid {RED}; padding:16px 20px; border-radius:10px;">
            <div style="color:{MUTED}; font-size:11px; text-transform:uppercase; letter-spacing:0.05em;">Without Intervention</div>
            <div style="font-size:28px; font-weight:800; color:{WHITE}; margin-top:4px;">Cascade Score: {do_nothing['group_risk_after']:.0f}</div>
            <div style="font-size:14px; color:{MUTED}; margin-top:4px;">Collateral Borrowers Affected: <b style="color:{WHITE}">{do_nothing['borrowers_affected']}</b></div>
        </div>
        """, unsafe_allow_html=True)
    with col_f2:
        st.markdown(f"""
        <div style="background:{CARD}; border-left:4px solid {MINT}; padding:16px 20px; border-radius:10px;">
            <div style="color:{MUTED}; font-size:11px; text-transform:uppercase; letter-spacing:0.05em;">With {recommended['name']}</div>
            <div style="font-size:28px; font-weight:800; color:{WHITE}; margin-top:4px;">Cascade Score: {recommended['group_risk_after']:.0f}</div>
            <div style="font-size:14px; color:{MUTED}; margin-top:4px;">Collateral Borrowers Affected: <b style="color:{WHITE}">{recommended['borrowers_affected']}</b></div>
        </div>
        """, unsafe_allow_html=True)
    st.write("")

card_columns = st.columns(4)

for col, candidate in zip(card_columns, interventions):
    is_rec = bool(candidate.get("recommended", False))
    candidate_name = candidate.get("name", "Unknown")

    bg_color = MINT_DARK if is_rec else CARD
    border_color = MINT if is_rec else CARD
    
    prefix_html = f'<div style="background:{MINT}; color:{BG}; padding:4px 12px; border-radius:12px; font-size:10px; font-weight:800; display:inline-block; margin-bottom:12px; letter-spacing:0.05em;">RECOMMENDED</div><br>' if is_rec else ""

    group_risk_after = float(candidate.get("group_risk_after", 0))
    risk_hex = risk_color(group_risk_after)

    recovery = candidate.get(
        "recovery_pct",
        candidate.get("recovery_rate", candidate.get("recovery", 0)),
    )
    try:
        recovery = float(recovery)
    except (TypeError, ValueError):
        recovery = 0.0
    if 0 < recovery <= 1:
        recovery *= 100

    affected = candidate.get(
        "borrowers_affected",
        candidate.get("affected_count", candidate.get("affected", 0)),
    )

    with col:
        st.markdown(
            f"""<div style="background:{bg_color}; border:2px solid {border_color}; border-radius:12px; padding:20px 16px; min-height:190px; box-sizing:border-box;">
{prefix_html}<div style="color:{WHITE}; font-weight:700; font-size:15px; line-height:1.3; margin-bottom:14px;">{candidate_name}</div>
<div style="color:{risk_hex}; font-size:38px; font-weight:800; line-height:1; margin-bottom:5px;">{group_risk_after:.0f}</div>
<div style="color:{MUTED}; font-size:11px; letter-spacing:0.08em; text-transform:uppercase; margin-bottom:16px;">Group risk after</div>
<div style="color:{WHITE}; font-size:13px; line-height:1.6;">Recovery: <b>{recovery:.0f}%</b><br>Affected: <b>{affected}</b></div>
</div>""",
            unsafe_allow_html=True,
        )

# --- THE MAGIC TRICK: EXPOSE THE ENGINE'S "THOUGHT PROCESS" ---
if recommended and recommended.get("decision_rationale"):
    st.markdown(f"""
    <div style="background:{MINT_DARK}; border-left:4px solid {MINT}; padding:16px 20px; border-radius:8px; margin-top:10px;">
        <div style="color:{MINT}; font-size:11px; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:4px;">Engine Rationale</div>
        <div style="color:{WHITE}; font-size:14px; line-height:1.5;">{recommended['decision_rationale']}</div>
    </div>
    """, unsafe_allow_html=True)
# --------------------------------------------------------------

st.write("")

nav_col, cause_col = st.columns([1.5, 1])

with nav_col:
    st.markdown("<div style='margin-top: 35px;'></div>", unsafe_allow_html=True)
    if st.button(
        f"Inspect {source_name}'s Full Profile in Borrower Intelligence →",
        use_container_width=True,
    ):
        st.session_state.target_borrower = source_name
        st.switch_page("pages/1_Borrower_Intelligence.py")

with cause_col:
    cause_lines = []
    for bid in visible_ids:
        b_name = id_to_name.get(bid, bid)
        is_iso = (bid not in relationships_df['borrower_a'].values) and (bid not in relationships_df['borrower_b'].values)
        
        if bid == source_id:
            cause_str = "Common Shock (seasonal)" if stress_result.get("evidence") and "seasonal" in stress_result["evidence"][0].lower() else "Independent (own finances)"
            c_color = "#9B5DE5" if "Common" in cause_str else RED
        elif bid in propagation_by_id and propagation_by_id[bid].get("impact_score", 0) > 0:
            cause_str = f"Relationship-driven (via {source_name})"
            c_color = AMBER
        elif is_iso:
            cause_str = "Isolated (no active connections)"
            c_color = MINT
        else:
            cause_str = "Stable (low estimated exposure)"
            c_color = GREEN
            
        cause_lines.append(f'<div style="font-size:13px; color:{WHITE}; margin-bottom:4px;"><span style="color:{c_color}; font-weight:700; width:65px; display:inline-block;">{b_name}</span> → {cause_str}</div>')

    causes_joined = "".join(cause_lines)
    
    st.markdown(
        f"""<div style="background:{CARD}; border-radius:8px; padding:16px 20px; height:100%;">
<div style="color:{MUTED}; font-size:10px; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:10px;">Network Cause Identification</div>
{causes_joined}
</div>""",
        unsafe_allow_html=True,
    )