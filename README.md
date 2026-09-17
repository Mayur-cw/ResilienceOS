## ResilienceOS

ResilienceOS is an explainable Streamlit decision-support prototype for understanding borrower stress, network exposure, and intervention choices.

### Run locally

```bash
python3 -m pip install -r requirements.txt
python3 data/generate_data.py
streamlit run app.py
```

The app opens with the group baseline. Use the sidebar for borrower intelligence, the exposure map, and the Intervention Lab.

### Test and quality checks

Install development tools with `python3 -m pip install -r requirements-dev.txt`, then run:

```bash
python3 -m tests.test_stress
python3 -m tests.test_propagation
python3 -m tests.test_intervention
python3 -m tests.test_data_validation
python3 -m compileall app.py engine pages ui utils tests
ruff check .
mypy engine utils
```

The demo dataset is deterministic and lives in `data/`. The engine rules, thresholds, and visual theme are centralized in `config.py`.
