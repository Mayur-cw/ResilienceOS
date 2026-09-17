"""Classify individual borrower risk into interpretable product states."""

from __future__ import annotations

from typing import Any, Mapping


RISK_STATES = (
    "Stable",
    "Temporary Stress",
    "Vulnerable",
    "Structural Deterioration",
)


class RiskClassificationError(ValueError):
    """Raised when a stress prediction cannot be classified."""


def classify_risk(
    prediction: Mapping[str, Any],
    behavioural_indicators: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a frontend-friendly risk classification for one borrower.

    ``prediction`` is the result returned by ``ml.predict_stress.predict_stress``.
    The classifier uses the model probability and interpretable behavioural
    signals; it does not recalculate the prediction or inspect network data.
    """

    borrower_id = prediction.get("borrower_id")
    probability = _probability(prediction.get("stress_probability"))
    indicators = dict(
        behavioural_indicators
        or prediction.get("relevant_behavioural_indicators", {})
        or {}
    )
    drivers = _build_drivers(indicators)
    state, rationale = _classify_state(probability, drivers)

    return {
        "borrower_id": borrower_id,
        "risk_state": state,
        "stress_probability": probability,
        "risk_band": _risk_band(probability),
        "summary": rationale,
        "major_risk_drivers": drivers,
        "explanation": {
            "text": rationale,
            "drivers": drivers,
            "qualifier": (
                "These signals are associated with the classification and do not "
                "establish a causal diagnosis."
            ),
        },
        "relevant_behavioural_indicators": indicators,
    }


def _probability(value: Any) -> float:
    try:
        probability = float(value)
    except (TypeError, ValueError) as error:
        raise RiskClassificationError("stress_probability must be numeric") from error
    if not 0.0 <= probability <= 1.0:
        raise RiskClassificationError("stress_probability must be between 0.0 and 1.0")
    return probability


def _risk_band(probability: float) -> str:
    if probability >= 0.66:
        return "high"
    if probability >= 0.33:
        return "moderate"
    return "low"


def _classify_state(
    probability: float,
    drivers: list[dict[str, Any]],
) -> tuple[str, str]:
    driver_codes = {driver["code"] for driver in drivers}
    persistent_codes = driver_codes.intersection(
        {
            "payment_delay_increasing",
            "borrowing_frequency_increasing",
            "attendance_declining",
            "repayment_behaviour_deteriorating",
        }
    )
    burden_codes = driver_codes.intersection(
        {"installment_burden", "repayment_behaviour_deteriorating"}
    )

    if probability >= 0.66 and len(persistent_codes) >= 2:
        return (
            "Structural Deterioration",
            "Elevated predicted stress aligns with multiple persistent behavioural changes.",
        )
    if probability >= 0.66 or len(persistent_codes) >= 2:
        return (
            "Vulnerable",
            "The borrower shows elevated predicted stress or multiple adverse behavioural signals.",
        )
    if probability >= 0.33 or persistent_codes or burden_codes:
        return (
            "Temporary Stress",
            "Recent or moderate adverse signals indicate a period of elevated predicted stress.",
        )
    return (
        "Stable",
        "Current indicators remain broadly aligned with the available personal baseline.",
    )


def _build_drivers(indicators: Mapping[str, Any]) -> list[dict[str, Any]]:
    drivers: list[dict[str, Any]] = []
    _add_driver(
        drivers,
        indicators,
        "recent_payment_delay",
        lambda value: value > 0,
        "payment_delay_increasing",
        "Payment delays increasing",
        "Recent repayment timing is slower than on-time behaviour.",
    )
    _add_driver(
        drivers,
        indicators,
        "payment_delay_trend",
        lambda value: value > 0,
        "payment_delay_increasing",
        "Payment delays increasing",
        "Recent delay is above the available personal repayment baseline.",
    )
    _add_driver(
        drivers,
        indicators,
        "borrowing_frequency_change",
        lambda value: value > 0,
        "borrowing_frequency_increasing",
        "Borrowing frequency increasing relative to personal baseline",
        "Borrowing frequency is above the borrower’s recorded baseline.",
    )
    _add_driver(
        drivers,
        indicators,
        "attendance_trend",
        lambda value: value < -0.05,
        "attendance_declining",
        "Attendance declining relative to personal baseline",
        "Attendance is below the borrower’s recorded baseline.",
    )
    _add_driver(
        drivers,
        indicators,
        "current_payment_ratio",
        lambda value: value < 1,
        "repayment_behaviour_deteriorating",
        "Repayment behaviour deteriorating",
        "The latest payment is below the expected installment amount.",
    )
    _add_driver(
        drivers,
        indicators,
        "configured_baseline_delay_deviation",
        lambda value: value > 0,
        "repayment_behaviour_deteriorating",
        "Repayment behaviour deteriorating",
        "The latest delay is above the configured personal baseline.",
    )
    _add_driver(
        drivers,
        indicators,
        "installment_to_income_ratio",
        lambda value: value >= 0.25,
        "installment_burden",
        "Installment burden is elevated",
        "The monthly installment represents a substantial share of monthly income.",
    )

    deduplicated: dict[str, dict[str, Any]] = {}
    for driver in drivers:
        existing = deduplicated.get(driver["code"])
        if existing is None or abs(driver["value"]) > abs(existing["value"]):
            deduplicated[driver["code"]] = driver
    return sorted(
        deduplicated.values(),
        key=lambda driver: (-abs(driver["value"]), driver["code"]),
    )


def _add_driver(
    drivers: list[dict[str, Any]],
    indicators: Mapping[str, Any],
    indicator_name: str,
    condition,
    code: str,
    label: str,
    detail: str,
) -> None:
    value = indicators.get(indicator_name)
    if value is None:
        return
    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        return
    if numeric_value != numeric_value or not condition(numeric_value):
        return
    drivers.append(
        {
            "code": code,
            "label": label,
            "detail": detail,
            "indicator": indicator_name,
            "value": numeric_value,
        }
    )
