"""Generate individual borrower financial-stress predictions."""

from __future__ import annotations

import json
import pickle
from pathlib import Path
from typing import Any

import pandas as pd

from ml.feature_engineering import load_and_engineer_features


RISK_LEVEL_THRESHOLDS = (
    (0.66, "high"),
    (0.33, "moderate"),
    (0.0, "low"),
)
BEHAVIOURAL_INDICATORS = (
    "recent_payment_delay",
    "historical_average_delay",
    "payment_delay_trend",
    "missed_or_partial_payment_frequency",
    "partial_payment_frequency",
    "historical_on_time_rate",
    "current_payment_ratio",
    "attendance_trend",
    "borrowing_frequency_change",
    "deviation_from_personal_baseline",
    "configured_baseline_delay_deviation",
)


class StressPredictionError(ValueError):
    """Raised when a borrower stress prediction cannot be generated."""


def predict_stress(
    borrower_id: str,
    data_dir: str | Path = "data",
    model_path: str | Path = "models/stress_model.pkl",
) -> dict[str, Any]:
    """Return an individual stress prediction for ``borrower_id``.

    This is the public service-layer entry point. It loads the persisted model,
    reuses the point-in-time feature-engineering pipeline, and uses the latest
    available repayment observation for the requested borrower. No network or
    cross-borrower calculation is performed.
    """

    normalized_borrower_id = str(borrower_id).strip()
    if not normalized_borrower_id:
        raise StressPredictionError("borrower_id cannot be blank")

    artifact = _load_model_artifact(model_path)
    feature_names = _artifact_feature_names(artifact)
    features = load_and_engineer_features(data_dir)
    borrower_features = features.loc[
        features["borrower_id"].astype(str) == normalized_borrower_id
    ]
    if borrower_features.empty:
        raise StressPredictionError(f"Borrower not found: {normalized_borrower_id}")

    feature_row = borrower_features.iloc[[0]]
    missing_features = sorted(set(feature_names) - set(feature_row.columns))
    if missing_features:
        raise StressPredictionError(
            f"Feature pipeline is missing model features: {missing_features}"
        )

    model = artifact["model"]
    try:
        stress_probability = float(
            model.predict_proba(feature_row.loc[:, feature_names])[0, 1]
        )
    except (AttributeError, IndexError, ValueError) as error:
        raise StressPredictionError(f"Unable to predict borrower stress: {error}") from error

    stress_probability = min(max(stress_probability, 0.0), 1.0)
    return {
        "borrower_id": normalized_borrower_id,
        "stress_probability": stress_probability,
        "risk_level": _risk_level(stress_probability),
        "major_risk_factors": _major_risk_factors(feature_row.iloc[0]),
        "relevant_behavioural_indicators": _behavioural_indicators(feature_row.iloc[0]),
    }


def _load_model_artifact(model_path: str | Path) -> dict[str, Any]:
    path = Path(model_path)
    if not path.is_file():
        raise StressPredictionError(f"Stress model does not exist: {path}")
    try:
        with path.open("rb") as model_file:
            artifact = pickle.load(model_file)
    except (OSError, pickle.PickleError, EOFError, ImportError, AttributeError) as error:
        raise StressPredictionError(f"Unable to load stress model {path}: {error}") from error
    if not isinstance(artifact, dict) or "model" not in artifact:
        raise StressPredictionError("Stress model artifact has an invalid format")
    return artifact


def _artifact_feature_names(artifact: dict[str, Any]) -> list[str]:
    feature_names = artifact.get("feature_names")
    if not isinstance(feature_names, list) or not feature_names:
        raise StressPredictionError("Stress model artifact does not define feature_names")
    return feature_names


def _risk_level(probability: float) -> str:
    for threshold, level in RISK_LEVEL_THRESHOLDS:
        if probability >= threshold:
            return level
    return "unknown"


def _behavioural_indicators(row: pd.Series) -> dict[str, Any]:
    indicators = {}
    for name in BEHAVIOURAL_INDICATORS:
        if name in row.index:
            indicators[name] = _json_value(row[name])
    return indicators


def _major_risk_factors(row: pd.Series) -> list[str]:
    factors: list[tuple[float, str]] = []

    _add_positive_factor(
        factors,
        row,
        "recent_payment_delay",
        lambda value: value > 0,
        lambda value: (float(value), f"Recent repayment delay of {int(value)} day(s)"),
    )
    _add_positive_factor(
        factors,
        row,
        "current_payment_ratio",
        lambda value: value < 1,
        lambda value: (
            float(1 - value),
            f"Current payment covers {value:.0%} of the expected amount",
        ),
    )
    _add_positive_factor(
        factors,
        row,
        "attendance_trend",
        lambda value: value < 0,
        lambda value: (
            float(-value),
            f"Attendance is {abs(value):.0%} below the personal baseline",
        ),
    )
    _add_positive_factor(
        factors,
        row,
        "borrowing_frequency_change",
        lambda value: value > 0,
        lambda value: (float(value), f"Borrowing frequency increased by {value:.0f}"),
    )
    _add_positive_factor(
        factors,
        row,
        "configured_baseline_delay_deviation",
        lambda value: value > 0,
        lambda value: (
            float(value),
            f"Delay is {int(value)} day(s) above the configured baseline",
        ),
    )
    _add_positive_factor(
        factors,
        row,
        "installment_to_income_ratio",
        lambda value: value >= 0.25,
        lambda value: (
            float(value),
            f"Installment burden is {value:.0%} of monthly income",
        ),
    )

    factors.sort(key=lambda item: (-item[0], item[1]))
    return [description for _, description in factors[:3]]


def _add_positive_factor(
    factors: list[tuple[float, str]],
    row: pd.Series,
    column: str,
    condition,
    formatter,
) -> None:
    if column not in row.index or pd.isna(row[column]):
        return
    value = float(row[column])
    if condition(value):
        factors.append(formatter(value))


def _json_value(value: Any) -> Any:
    if pd.isna(value):
        return None
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if hasattr(value, "item"):
        return value.item()
    return value


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("borrower_id")
    parser.add_argument("--data-dir", default="data")
    parser.add_argument("--model-path", default="models/stress_model.pkl")
    arguments = parser.parse_args()
    print(
        json.dumps(
            predict_stress(
                arguments.borrower_id,
                arguments.data_dir,
                arguments.model_path,
            ),
            indent=2,
        )
    )
