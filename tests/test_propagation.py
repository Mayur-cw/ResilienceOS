"""TODO: test_propagation"""
"""
Run this file from the project root using:
python -m tests.test_propagation
"""
import networkx as nx
from engine.propagation import propagate_shock

def run_tests():
    """Run all network propagation assertions."""
    
    # (a) Build 3-node graph, assert B's impact is meaningfully higher than C's
    G = nx.Graph()
    G.add_edge('A', 'B', weight=0.9)
    G.add_edge('A', 'C', weight=0.1)
    
    vulnerability_scores = {'A': 0.5, 'B': 0.5, 'C': 0.5}
    
    res_a = propagate_shock('A', 80, G, vulnerability_scores)
    
    assert 'B' in res_a and 'C' in res_a, "Nodes B and C should be included in propagation result."
    assert res_a['B']['impact_score'] > res_a['C']['impact_score'], (
        f"Expected B's impact ({res_a['B']['impact_score']}) to be > "
        f"C's impact ({res_a['C']['impact_score']})."
    )
    assert res_a['B']['hop_distance'] == 1
    assert res_a['B']['primary_path'] == ['A', 'B']

    # (b) Build a graph with isolated node D, confirm result ONLY contains D
    G_isolated = nx.Graph()
    G_isolated.add_node('D')
    
    res_b = propagate_shock('D', 80, G_isolated, {'D': 0.5})
    
    assert len(res_b) == 1, f"Expected exactly 1 node in result, got {len(res_b)}."
    assert 'D' in res_b, "Node D must be the only node in the propagation result."

    print("PASSED: test_propagation.py")

if __name__ == "__main__":
    run_tests()