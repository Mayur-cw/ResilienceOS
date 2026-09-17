"""
Engine module for simulating financial stress propagation through the relationship graph.

Implements a bounded BFS relaxation algorithm to calculate how shock from one borrower
propagates to connected peers based on relationship weight, structural vulnerability,
and distance decay.
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any, List

import networkx as nx

# Ensure the script can import config from the project root
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from config import MAX_HOPS, DECAY


def propagate_shock(
    source_borrower_id: str,
    source_severity: float,
    graph: nx.Graph,
    vulnerability_scores: Dict[str, float],
    max_hops: Optional[int] = None,
    decay: Optional[float] = None
) -> Dict[str, Dict[str, Any]]:
    """
    Propagates financial shock from a source borrower across a relationship graph
    using a bounded BFS/relaxation approach.
    
    Args:
        source_borrower_id (str): The borrower who originated the shock.
        source_severity (float): Source borrower's severity score (0-100) after the shock.
        graph (nx.Graph): NetworkX undirected graph with 'weight' on edges.
        vulnerability_scores (Dict[str, float]): Map of borrower IDs to their
            structural vulnerability scores (0-1) calculated from baseline debt/buffers.
        max_hops (int, optional): Maximum propagation depth. Defaults to config.MAX_HOPS.
        decay (float, optional): Attenuation factor applied beyond hop 1. Defaults to config.DECAY.

    Returns:
        Dict[str, Dict[str, Any]]: Mapping of reached borrower IDs to their impact details:
            - impact_score (float): Maximum shock score reaching this node (rounded to 1 decimal).
            - hop_distance (int): Distance in hops from the source.
            - primary_path (List[str]): Sequence of borrower IDs along the maximum-impact path.
            Borrowers not reached within max_hops are omitted.
    """
    if max_hops is None:
        max_hops = MAX_HOPS
    if decay is None:
        decay = DECAY

    # max_hops and decay act as a deliberate safeguard against a shock unrealistically
    # cascading through an entire network, reflecting localized economic damping.
    impact: Dict[str, float] = {source_borrower_id: float(source_severity)}
    hop_distance: Dict[str, int] = {source_borrower_id: 0}
    primary_path: Dict[str, List[str]] = {source_borrower_id: [source_borrower_id]}
    frontier: List[str] = [source_borrower_id]

    for hop in range(1, max_hops + 1):
        next_frontier: List[str] = []
        for node in frontier:
            for neighbor in graph.neighbors(node):
                edge_weight = float(graph[node][neighbor]["weight"])
                neighbor_vuln = float(vulnerability_scores.get(neighbor, 0.0))
                
                candidate = impact[node] * edge_weight * neighbor_vuln
                if hop > 1:
                    candidate *= decay
                candidate = min(candidate, 100.0)

                if neighbor not in impact or candidate > impact[neighbor]:
                    impact[neighbor] = candidate
                    hop_distance[neighbor] = hop
                    primary_path[neighbor] = primary_path[node] + [neighbor]
                    next_frontier.append(neighbor)

        frontier = next_frontier
        if not frontier:
            break

    # Format output dictionary and round impact_score to 1 decimal place
    results: Dict[str, Dict[str, Any]] = {}
    for node_id, score in impact.items():
        results[node_id] = {
            "impact_score": round(score, 1),
            "hop_distance": hop_distance[node_id],
            "primary_path": primary_path[node_id]
        }

    return results