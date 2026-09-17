"""Train the deterministic individual financial-stress model."""

from __future__ import annotations

import argparse
import json
import pickle
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from ml.feature_engineering import FEATURE_COLUMNS, build_feature_table
from utils.data_loader import load_project_data


TARGET_NAME = "stress_next_30_days"
RANDOM_STATE = 42
TARGET_HORIZON_DAYS = 30
SCHEDULE_GRACE_DAYS = 1
MODEL_VERSION = "stress-model-demo-1"

FEATURE_NAMES = tuple(column for column in FEATURE_COLUMNS if column not in {
    "borrower_id",
    "observation_date",
})


class ModelTrainingError(ValueError):
    """Raised when the training data cannot support deterministic model fitting."""


def build_training_dataset(
    borrowers: pd.DataFrame,
    repayments: pd.DataFrame,
    horizon_days: int = TARGET_HORIZON_DAYS,
) -> pd.DataFrame:
    """Create leakage-safe training rows from current and next repayment records.

    A row is built at a repayment observation date. Its target is derived only
    from the next scheduled repayment, never from the current repayment used to
    create the features. The one-day schedule grace accommodates the synthetic
    dataset's 31-day monthly dates while preserving the named 30-day monitoring
    target.
    """

    if horizon_days < 1:
        raise ModelTrainingError("horizon_days must be positive")

    repayment_frame = repayments.copy()
    repayment_frame["date"] = pd.to_datetime(repayment_frame["date"], errors="coerce")
    if repayment_frame["date"].isna().any():
        raise ModelTrainingError("repayments.date contains invalid dates")
    repayment_frame = repayment_frame.sort_values(
        ["borrower_id", "date", "repayment_id"], kind="mergesort"
    )

    rows = []
    max_days = horizon_days + SCHEDULE_GRACE_DAYS
    for borrower_id, borrower_repayments in repayment_frame.groupby(
        "borrower_id", sort=True
    ):
        borrower_repayments = borrower_repayments.reset_index(drop=True)
        if len(borrower_repayments) < 2:
            continue

        borrower = borrowers.loc[borrowers["borrower_id"].astype(str) == str(borrower_id)]
        if borrower.empty:
            raise ModelTrainingError(f"No borrower record found for {borrower_id}")

        for index in range(len(borrower_repayments) - 1):
            current = borrower_repayments.iloc[index]
            next_repayment = borrower_repayments.iloc[index + 1]
            days_until_next = int((next_repayment["date"] - current["date"]).days)
            if days_until_next <= 0 or days_until_next > max_days:
                continue

            historical_cut = repayment_frame.loc[
                (repayment_frame["borrower_id"].astype(str) == str(borrower_id))
                & (repayment_frame["date"] <= current["date"])
            ]
            snapshot = build_feature_table(
                borrower,
                historical_cut,
                observation_date=current["date"],
            ).iloc[0]
            row = snapshot.to_dict()
            row[TARGET_NAME] = int(_repayment_is_stressed(next_repayment))
            row["next_repayment_date"] = next_repayment["date"]
            row["days_until_next_repayment"] = days_until_next
            rows.append(row)

    if not rows:
        raise ModelTrainingError("No point-in-time training rows were generated")
    return pd.DataFrame(rows)


def train_and_save_model(
    data_dir: str | Path = "data",
    models_dir: str | Path = "models",
    test_size: float = 0.25,
) -> dict:
    """Train candidate models, save the selected model, and return metadata."""

    if not 0 < test_size < 1:
        raise ModelTrainingError("test_size must be between 0 and 1")

    data = load_project_data(data_dir)
    training_data = build_training_dataset(data.borrowers, data.repayments)
    if training_data[TARGET_NAME].nunique() < 2:
        raise ModelTrainingError("Training target must contain both classes")

    excluded_feature_names = [
        feature_name
        for feature_name in FEATURE_NAMES
        if training_data[feature_name].notna().sum() == 0
    ]
    selected_feature_names = tuple(
        feature_name for feature_name in FEATURE_NAMES if feature_name not in excluded_feature_names
    )
    if not selected_feature_names:
        raise ModelTrainingError("No usable feature columns remain after validation")

    X = training_data.loc[:, selected_feature_names]
    y = training_data[TARGET_NAME].astype(int)
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    candidates = _build_candidates()
    metrics = {}
    fitted_candidates = {}
    for name, candidate in candidates.items():
        candidate.fit(X_train, y_train)
        metrics[name] = _evaluate(candidate, X_test, y_test)
        fitted_candidates[name] = candidate

    selected_name = max(
        metrics,
        key=lambda name: (
            metrics[name]["recall"],
            metrics[name]["f1"],
            metrics[name]["roc_auc"],
            metrics[name]["precision"],
        ),
    )
    selected_model = fitted_candidates[selected_name]

    output_dir = Path(models_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    model_path = output_dir / "stress_model.pkl"
    metadata_path = output_dir / "model_metadata.json"
    with model_path.open("wb") as model_file:
        pickle.dump(
            {
                "model": selected_model,
                "feature_names": list(selected_feature_names),
                "target_name": TARGET_NAME,
                "model_version": MODEL_VERSION,
            },
            model_file,
            protocol=pickle.HIGHEST_PROTOCOL,
        )

    metadata = {
        "model_version": MODEL_VERSION,
        "target": TARGET_NAME,
        "target_definition": (
            "1 when the next scheduled repayment within the 30-day monitoring "
            "window is delayed or partial; otherwise 0. The synthetic monthly "
            "schedule is 31 days, so a one-day schedule grace is applied."
        ),
        "target_horizon_days": TARGET_HORIZON_DAYS,
        "schedule_grace_days": SCHEDULE_GRACE_DAYS,
        "data_directory": str(Path(data_dir)),
        "training_rows": int(len(training_data)),
        "positive_rows": int(y.sum()),
        "negative_rows": int((y == 0).sum()),
        "feature_names": list(selected_feature_names),
        "excluded_all_null_features": excluded_feature_names,
        "selected_model": selected_name,
        "selection_priority": ["recall", "f1", "roc_auc", "precision"],
        "random_state": RANDOM_STATE,
        "test_size": test_size,
        "metrics": metrics,
        "outputs": {
            "model": str(model_path),
            "metadata": str(metadata_path),
        },
    }
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return metadata


def _build_candidates() -> dict[str, Pipeline]:
    return {
        "logistic_regression": Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="median", add_indicator=True)),
                ("scaler", StandardScaler()),
                (
                    "classifier",
                    LogisticRegression(
                        class_weight="balanced",
                        max_iter=1000,
                        random_state=RANDOM_STATE,
                    ),
                ),
            ]
        ),
        "random_forest": Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="median", add_indicator=True)),
                (
                    "classifier",
                    RandomForestClassifier(
                        class_weight="balanced",
                        max_depth=5,
                        min_samples_leaf=2,
                        n_estimators=200,
                        n_jobs=1,
                        random_state=RANDOM_STATE,
                    ),
                ),
            ]
        ),
    }


def _evaluate(model: Pipeline, X_test: pd.DataFrame, y_test: pd.Series) -> dict[str, float]:
    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)[:, 1]
    return {
        "precision": float(precision_score(y_test, predictions, zero_division=0)),
        "recall": float(recall_score(y_test, predictions, zero_division=0)),
        "f1": float(f1_score(y_test, predictions, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, probabilities)),
    }


def _repayment_is_stressed(repayment: pd.Series) -> bool:
    return bool(
        repayment["delay_days"] > 0
        or repayment["payment_status"] != "on_time"
        or repayment["paid_amount"] < repayment["expected_amount"]
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", default="data")
    parser.add_argument("--models-dir", default="models")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    metadata = train_and_save_model(args.data_dir, args.models_dir)
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
