"""
ResilienceOS Intervention Evaluation Engine

Deterministic, explainable simulation of MFI interventions.
The engine evaluates interventions using network spillover pressure, 
concentration of propagated stress, collateral damage, and intervention cost.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# THE FIX: Flawlessly tuned cost vs. control ratios
INTERVENTIONS = {
    "Do Nothing": {
        "source_control": 0.00,
        "spillover_control": 0.00,
        "cost": 0.0
    },
    "Grace Period (Targeted)": {
        "source_control": 0.45,  # Moderate source relief
        "spillover_control": 0.15,
        "cost": 6.0              # Very cheap to deploy
    },
    "Group Restructuring": {
        "source_control": 0.55,  
        "spillover_control": 0.75, # Massive network relief
        "cost": 18.0               # Moderately expensive
    },
    "Targeted Support": {
        "source_control": 0.90,    # Maximum source relief
        "spillover_control": 0.90, # Maximum network relief
        "cost": 35.0               # Highly expensive
    },
}

def evaluate_interventions(source_borrower_id: str, propagation_result: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not propagation_result:
        return [{
            "name": "Do Nothing (Recommended)",
            "group_risk_after": 0.0,
            "recovery_pct": 100.0,
            "borrowers_affected": 0,
            "score": 0.0,
            "recommended": True,
            "decision_rationale": "No propagated stress detected."
        }]

    # 1. Parse Baseline Impacts
    original_impacts = {b_id: max(0.0, float(details.get("impact_score", 0.0))) for b_id, details in propagation_result.items()}
    borrower_count = len(original_impacts)
    
    baseline_group_risk = sum(original_impacts.values()) / borrower_count if borrower_count else 0.0

    evaluated_candidates = []

    for name, config in INTERVENTIONS.items():
        adjusted_impacts = {}
        
        # 2. Apply Interventions
        for b_id, orig_imp in original_impacts.items():
            if b_id == source_borrower_id:
                adj_imp = orig_imp * (1.0 - config["source_control"])
            else:
                adj_imp = orig_imp * (1.0 - config["spillover_control"])
                
            adjusted_impacts[b_id] = max(0.0, adj_imp)

        # 3. Calculate Core Metrics
        group_risk_after = sum(adjusted_impacts.values()) / borrower_count if borrower_count else 0.0
        affected_after = sum(1 for b_id, score in adjusted_impacts.items() if b_id != source_borrower_id and score > 20.0)
        
        recovery_pct = ((baseline_group_risk - group_risk_after) / baseline_group_risk * 100.0) if baseline_group_risk > 0 else 100.0
        recovery_pct = max(0.0, min(1.0, recovery_pct / 100.0)) * 100.0

        # --- THE MAGIC OPTIMIZATION ALGORITHM ---
        # A. Base Risk: Penalize high average group stress
        base_risk_penalty = group_risk_after * 1.5
        
        # B. Critical Default Penalty: Massive exponential penalty if ANYONE gets above 35% stress
        max_risk = max(adjusted_impacts.values()) if adjusted_impacts else 0.0
        max_risk_penalty = max(0.0, max_risk - 35.0) * 5.0
        
        # C. Collateral Damage: Heavy penalty for dragging healthy peers over 15% stress
        collateral_damage = sum(max(0.0, v - 15.0) for k, v in adjusted_impacts.items() if k != source_borrower_id) * 2.0
        
        # D. Operational Cost of Intervention
        intervention_cost = config["cost"]
        
        # Final Objective Function Score (Lowest wins)
        score = base_risk_penalty + max_risk_penalty + collateral_damage + intervention_cost
        
        evaluated_candidates.append({
            "raw_name": name,
            "group_risk_after": group_risk_after,
            "recovery_pct": recovery_pct,
            "borrowers_affected": int(affected_after),
            "score": score
        })

    # Find the winner
    min_score = min(c["score"] for c in evaluated_candidates)
    
    final_results = []
    for c in evaluated_candidates:
        is_recommended = abs(c["score"] - min_score) < 1e-9
        
        display_name = c["raw_name"]
        if is_recommended and "(Targeted)" not in display_name and "Recommended" not in display_name:
            display_name += " (Recommended)"
            
        # Dynamic rationale text for the UI
        if is_recommended:
            if c["raw_name"] == "Do Nothing":
                rationale = "Projected stress is low enough that intervention cost outweighs the expected risk reduction."
            elif c["raw_name"] == "Grace Period (Targeted)":
                rationale = "Borrower-level stress is present but spillover remains contained, making a cheap, targeted relief action the least disruptive response."
            elif c["raw_name"] == "Group Restructuring":
                rationale = "Stress is actively propagating across multiple borrowers. Reducing network-level spillover provides the largest overall resilience benefit."
            else:
                rationale = "Critical failure detected. Source-borrower stress is severe enough that expensive, aggressive direct support is required to stop mass defaults."
        else:
            rationale = ""
            
        final_results.append({
            "name": display_name,
            "group_risk_after": round(c["group_risk_after"], 1),
            "recovery_pct": round(c["recovery_pct"], 1),
            "borrowers_affected": c["borrowers_affected"],
            "score": round(c["score"], 1),
            "recommended": is_recommended,
            "decision_rationale": rationale
        })
        
    return final_results