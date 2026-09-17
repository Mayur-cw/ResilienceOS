🧠 Architecture: The Two-Track Engine

ResilienceOS was built with a dual-engine architecture to balance immediate explainability with future scalability:

1. The UI Simulation Engine (/engine): The Streamlit prototype is powered by a deterministic, rules-based engine. We use strict financial thresholds (e.g., RBI Debt Caps) to ensure that every classification is 100% explainable and transparent to the lender during the visual simulation.

2. The Production ML Pipeline (/ml_research_backend): For future deployment, we have built and trained a Scikit-Learn predictive pipeline. It features automated feature engineering on trailing repayment data to output probabilistic risk scores. This pipeline is ready to be wrapped in a Flask/FastAPI layer for real-time integration with Core Banking Systems.