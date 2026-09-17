"""Create interpretable borrower features from point-in-time source data."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from utils.data_loader import load_project_data


BORROWER_FEATURE_INPUTS = (
    "borrower_id",
    "monthly_income",
    "loan_amount",
    "monthly_installment",
    "existing_loans",
    "previous_loans",
    "previous_late_payments",
    "attendance_rate",
    "borrowing_frequency",
    "baseline_delay_days",
    "current_attendance_rate",
    "current_borrowing_frequency",
)
REPAYMENT_FEATURE_INPUTS = (
    "borrower_id",
    "date",
    "expected_amount",
    "paid_amount",
    "delay_days",
    "payment_status",
)
FEATURE_COLUMNS = (
    "borrower_id",
    "observation_date",
    "historical_observation_count",
    "recent_payment_delay",
    "historical_average_delay",
    "payment_delay_trend",
    "missed_or_partial_payment_frequency",
    "partial_payment_frequency",
    "historical_on_time_rate",
    "current_payment_ratio",
    "attendance_trend",
    "borrowing_frequency_change",
    "debt_to_income_ratio",
    "installment_to_income_ratio",
    "previous_repayment_performance",
    "deviation_from_personal_baseline",
    "configured_baseline_delay_deviation",
)


class FeatureEngineeringError(ValueError):
    """Raised when source data cannot produce the requested features."""


def build_feature_table(
    borrowers: pd.DataFrame,
    repayments: pd.DataFrame,
    observation_date: str | pd.Timestamp | None = None,
) -> pd.DataFrame:
    """Build one point-in-time feature row for each borrower.

    For each borrower, the latest repayment on or before ``observation_date``
    is treated as the current observation. The personal repayment baseline is
    calculated only from that borrower's strictly earlier records. If no cutoff
    is supplied, the latest repayment date in the input is used as the global
    cutoff. No records after the cutoff can affect the result.
    """

    _require_columns(borrowers, BORROWER_FEATURE_INPUTS, "borrowers")
    _require_columns(repayments, REPAYMENT_FEATURE_INPUTS, "repayments")

    borrower_frame = borrowers.copy()
    repayment_frame = repayments.copy()
    borrower_frame["borrower_id"] = borrower_frame["borrower_id"].astype(str).str.strip()
    repayment_frame["borrower_id"] = repayment_frame["borrower_id"].astype(str).str.strip()
    repayment_frame["date"] = pd.to_datetime(repayment_frame["date"], errors="coerce")
    if repayment_frame["date"].isna().any():
        raise FeatureEngineeringError("repayments.date contains invalid dates")

    cutoff = _resolve_cutoff(repayment_frame["date"], observation_date)
    repayment_frame = repayment_frame.loc[repayment_frame["date"] <= cutoff].copy()
    repayment_frame = repayment_frame.sort_values(
        ["borrower_id", "date", "repayment_id"], kind="mergesort"
    )

    rows = []
    for borrower in borrower_frame.to_dict(orient="records"):
        borrower_id = borrower["borrower_id"]
        borrower_repayments = repayment_frame.loc[
            repayment_frame["borrower_id"] == borrower_id
        ]
        row = _build_borrower_features(borrower, borrower_repayments)
        rows.append(row)

    return pd.DataFrame(rows, columns=FEATURE_COLUMNS)


def engineer_features(
    borrowers: pd.DataFrame,
    repayments: pd.DataFrame,
    observation_date: str | pd.Timestamp | None = None,
) -> pd.DataFrame:
    """Alias for the public feature-table builder used by services."""

    return build_feature_table(borrowers, repayments, observation_date)


def load_and_engineer_features(
    data_dir: str | Path,
    observation_date: str | pd.Timestamp | None = None,
) -> pd.DataFrame:
    """Load validated project data once, then build borrower features."""

    data = load_project_data(data_dir)
    return build_feature_table(data.borrowers, data.repayments, observation_date)


def _build_borrower_features(
    borrower: dict,
    borrower_repayments: pd.DataFrame,
) -> dict:
    current = borrower_repayments.iloc[-1] if not borrower_repayments.empty else None
    historical = borrower_repayments.iloc[:-1] if current is not None else borrower_repayments

    historical_count = len(historical)
    historical_delay = _mean(historical, "delay_days")
    current_delay = _value(current, "delay_days")
    current_payment_ratio = _ratio(
        _value(current, "paid_amount"), _value(current, "expected_amount")
    )
    historical_on_time_rate = _status_rate(historical, "on_time")
    non_on_time_frequency = _non_on_time_frequency(historical)
    partial_frequency = _status_frequency(historical, "partial")

    monthly_income = _number(borrower.get("monthly_income"))
    loan_amount = _number(borrower.get("loan_amount"))
    monthly_installment = _number(borrower.get("monthly_installment"))
    existing_loans = _number(borrower.get("existing_loans"))

    return {
        "borrower_id": borrower["borrower_id"],
        "observation_date": _value(current, "date"),
        "historical_observation_count": historical_count,
        "recent_payment_delay": current_delay,
        "historical_average_delay": historical_delay,
        "payment_delay_trend": _difference(current_delay, historical_delay),
        "missed_or_partial_payment_frequency": non_on_time_frequency,
        "partial_payment_frequency": partial_frequency,
        "historical_on_time_rate": historical_on_time_rate,
        "current_payment_ratio": current_payment_ratio,
        "attendance_trend": _difference(
            _number(borrower.get("current_attendance_rate")),
            _number(borrower.get("attendance_rate")),
        ),
        "borrowing_frequency_change": _difference(
            _number(borrower.get("current_borrowing_frequency")),
            _number(borrower.get("borrowing_frequency")),
        ),
        "debt_to_income_ratio": _ratio(loan_amount, monthly_income * 12),
        "installment_to_income_ratio": _ratio(monthly_installment, monthly_income),
        "previous_repayment_performance": _ratio(
            _number(borrower.get("previous_loans"))
            - _number(borrower.get("previous_late_payments")),
            _number(borrower.get("previous_loans")),
        ),
        "deviation_from_personal_baseline": _difference(current_delay, historical_delay),
        "configured_baseline_delay_deviation": _difference(
            current_delay, _number(borrower.get("baseline_delay_days"))
        ),
    }


def _resolve_cutoff(
    dates: pd.Series,
    observation_date: str | pd.Timestamp | None,
) -> pd.Timestamp:
    if observation_date is None:
        return dates.max()
    cutoff = pd.to_datetime(observation_date, errors="coerce")
    if pd.isna(cutoff):
        raise FeatureEngineeringError(f"Invalid observation_date: {observation_date}")
    return cutoff


def _require_columns(
    frame: pd.DataFrame,
    required_columns: tuple[str, ...],
    dataset_name: str,
) -> None:
    missing = sorted(set(required_columns) - set(frame.columns))
    if missing:
        raise FeatureEngineeringError(
            f"{dataset_name} data is missing required columns: {missing}"
        )


def _value(row: pd.Series | None, column: str):
    if row is None:
        return pd.NA
    return row[column]


def _number(value):
    if value is None or pd.isna(value):
        return float("nan")
    return float(value)


def _mean(frame: pd.DataFrame, column: str):
    if frame.empty:
        return float("nan")
    return float(frame[column].mean())


def _ratio(numerator, denominator):
    numerator = _number(numerator)
    denominator = _number(denominator)
    if pd.isna(numerator) or pd.isna(denominator) or denominator == 0:
        return float("nan")
    return numerator / denominator


def _difference(current, baseline):
    current = _number(current)
    baseline = _number(baseline)
    if pd.isna(current) or pd.isna(baseline):
        return float("nan")
    return current - baseline


def _ratio_of_count(frame: pd.DataFrame, condition) -> float:
    if frame.empty:
        return float("nan")
    return float(condition(frame).sum()) / len(frame)


def _status_frequency(frame: pd.DataFrame, status: str) -> float:
    return _ratio_of_count(frame, lambda values: values["payment_status"].eq(status))


def _non_on_time_frequency(frame: pd.DataFrame) -> float:
    return _ratio_of_count(frame, lambda values: values["payment_status"].ne("on_time"))


def _status_rate(frame: pd.DataFrame, status: str) -> float:
    return _status_frequency(frame, status)