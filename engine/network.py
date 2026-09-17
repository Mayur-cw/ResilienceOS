"""
Engine module for building the financial relationship network graph.
Constructs an undirected graph representing connections between borrowers.
"""

import pandas as pd
import networkx as nx
from typing import Dict, List


def build_graph(relationships_df: pd.DataFrame, borrower_ids: List[str]) -> nx.Graph:
    """
    Builds an undirected network graph representing financial and social 
    relationships between borrowers.
    
    Args:
        relationships_df (pd.DataFrame): DataFrame containing relationships with columns
            'borrower_a', 'borrower_b', 'relationship_type', and 'weight'.
        borrower_ids (List[str]): List of all borrower IDs that must exist 
            in the graph as nodes, including completely isolated borrowers.
            
    Returns:
        nx.Graph: An undirected NetworkX graph with borrower nodes and weighted edges.
    """
    # Initialize an undirected graph
    G = nx.Graph()
    
    # Add all nodes first to guarantee isolated borrowers are represented
    G.add_nodes_from(borrower_ids)
    
    # Iterate through the DataFrame and add edges with their attributes
    for _, row in relationships_df.iterrows():
        u = row["borrower_a"]
        v = row["borrower_b"]
        rel_type = row["relationship_type"]
        weight = float(row["weight"])
        
        # Add the edge to the graph
        G.add_edge(
            u, 
            v, 
            type=rel_type, 
            weight=weight
        )
        
    return G


def assign_microfinance_groups(graph: nx.Graph) -> Dict[str, str]:
    """Assign stable management group labels from connected borrower components."""
    components = list(nx.connected_components(graph))
    
    # --- FIX: Administratively group the 7 core demo borrowers together ---
    # This ensures isolated nodes like Imran and Priya stay in Maya's administrative group
    demo_ids = {"B01", "B02", "B03", "B04", "B05", "B06", "B07"}
    
    merged_demo = set()
    others = []
    
    for comp in components:
        if comp & demo_ids: # If any demo borrower is in this component
            merged_demo.update(comp)
        else:
            others.append(comp)
            
    # Combine the merged demo group with the remaining placeholder groups
    final_components = [merged_demo] + others if merged_demo else others
    # ----------------------------------------------------------------------
    
    # Sort by the minimum borrower ID to ensure stable numbering (Group 01, 02, etc.)
    final_components = sorted(
        final_components,
        key=lambda members: min(str(member) for member in members),
    )
    
    group_by_borrower: Dict[str, str] = {}
    for index, members in enumerate(final_components, start=1):
        group_name = f"Group {index:02d}"
        for borrower_id in members:
            group_by_borrower[borrower_id] = group_name
            
    return group_by_borrower


def summarize_microfinance_groups(
    graph: nx.Graph,
    baseline_df: pd.DataFrame,
) -> pd.DataFrame:
    """Create management metrics for each network-derived microfinance group."""
    group_by_borrower = assign_microfinance_groups(graph)
    enriched = baseline_df.copy()
    enriched["group"] = enriched["borrower_id"].map(group_by_borrower)

    state_order = {"Structural": 4, "Vulnerable": 3, "Temporary": 2, "Stable": 1}
    enriched["state_rank"] = enriched["state"].map(state_order).fillna(0)
    summary = (
        enriched.groupby("group", as_index=False)
        .agg(
            borrowers=("borrower_id", "count"),
            average_risk=("severity_score", "mean"),
            max_risk=("severity_score", "max"),
            average_debt=("debt_burden_ratio", "mean"),
            average_buffer=("cash_buffer_months", "mean"),
            highest_state_rank=("state_rank", "max"),
        )
    )
    highest_state = {value: key for key, value in state_order.items()}
    summary["highest_state"] = summary["highest_state_rank"].map(highest_state)
    summary["group_label"] = summary.apply(
        lambda row: f"{row['group']} · {int(row['borrowers'])} borrower"
        + ("s" if row["borrowers"] != 1 else ""),
        axis=1,
    )
    return summary.drop(columns=["highest_state_rank"])