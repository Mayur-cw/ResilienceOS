"""TODO: test_intervention"""
"""
Run this file from the project root using:
python -m tests.test_intervention
"""
from engine.intervention import evaluate_interventions
import config

def run_tests():
    """Run all intervention evaluation assertions."""
    
    # (a) Evaluate a 3-borrower propagation map
    # A is source, B and C are affected
    prop_result_3 = {
        'A': {'impact_score': 80},
        'B': {'impact_score': 45},
        'C': {'impact_score': 25},
    }
    candidates_3 = evaluate_interventions('A', prop_result_3)
    
    assert len(candidates_3) == 4, f"Expected exactly 4 intervention candidates, got {len(candidates_3)}."
    
    # Check strict order compliance against config
    candidate_names = [c['name'] for c in candidates_3]
    assert candidate_names == config.INTERVENTION_ORDER, f"Order mismatch. Expected {config.INTERVENTION_ORDER}, got {candidate_names}."
    
    # Check exactly one candidate is marked as recommended=True
    recommended_count = sum(1 for c in candidates_3 if c.get('recommended') is True)
    assert recommended_count == 1, f"Expected exactly 1 recommended candidate, got {recommended_count}."
    
    # Verify 'Targeted Support' affects <= 'Group Restructuring'
    targeted = next(c for c in candidates_3 if c['name'] == 'Targeted Support (Recommended)')
    group = next(c for c in candidates_3 if c['name'] == 'Group Restructuring')
    assert targeted['borrowers_affected'] <= group['borrowers_affected'], "Targeted Support should affect fewer or equal borrowers compared to Group Restructuring."

    # (b) Evaluate an isolated borrower propagation map (like Imran)
    prop_result_1 = {'D': {'impact_score': 80}}
    candidates_1 = evaluate_interventions('D', prop_result_1)
    
    for c in candidates_1:
        assert c['borrowers_affected'] == 0, f"Expected 0 collateral borrowers affected for '{c['name']}', got {c['borrowers_affected']}."

    print("PASSED: test_intervention.py")

if __name__ == "__main__":
    run_tests()