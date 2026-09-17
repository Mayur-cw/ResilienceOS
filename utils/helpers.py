"""
utils/helpers.py

UI-support plumbing and data loading for the ResilienceOS Streamlit app.
This module handles loading and validating the primary CSV data files.
"""

import pandas as pd
import streamlit as st
import logging
from config import PROFILE_CSV, MONTHLY_CSV, RELATIONSHIPS_CSV


logger = logging.getLogger(__name__)


PROFILE_COLUMNS = {
    "borrower_id",
    "name",
    "household_income",
    "savings_buffer",
    "other_loan_emi",
}
MONTHLY_COLUMNS = {
    "borrower_id",
    "month",
    "income",
    "expenses",
    "mfi_repayment_due",
    "mfi_repayment_paid",
}
RELATIONSHIP_COLUMNS = {
    "borrower_a",
    "borrower_b",
    "relationship_type",
    "weight",
}


def _require_columns(df: pd.DataFrame, required: set[str], name: str) -> None:
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"Validation failed: {name} is missing columns: {missing}")


def _require_numeric(df: pd.DataFrame, columns: set[str], name: str) -> None:
    for column in columns:
        values = pd.to_numeric(df[column], errors="coerce")
        if values.isna().any():
            raise ValueError(
                f"Validation failed: {name}.{column} contains non-numeric or missing values."
            )


def validate_dataframes(
    profile_df: pd.DataFrame,
    monthly_df: pd.DataFrame,
    relationships_df: pd.DataFrame,
) -> None:
    """Validate the three input tables before any engine calculations run."""
    _require_columns(profile_df, PROFILE_COLUMNS, "profile_df")
    _require_columns(monthly_df, MONTHLY_COLUMNS, "monthly_df")
    _require_columns(relationships_df, RELATIONSHIP_COLUMNS, "relationships_df")

    if profile_df["borrower_id"].isna().any() or profile_df["borrower_id"].duplicated().any():
        raise ValueError("Validation failed: borrower IDs must be present and unique.")
    if profile_df["name"].isna().any() or profile_df["name"].duplicated().any():
        raise ValueError("Validation failed: borrower names must be present and unique.")

    _require_numeric(
        profile_df,
        {"household_income", "savings_buffer", "other_loan_emi"},
        "profile_df",
    )
    _require_numeric(
        monthly_df,
        {"month", "income", "expenses", "mfi_repayment_due", "mfi_repayment_paid"},
        "monthly_df",
    )
    _require_numeric(relationships_df, {"weight"}, "relationships_df")

    profile_ids = set(profile_df["borrower_id"])
    monthly_ids = set(monthly_df["borrower_id"])
    unknown_monthly_ids = monthly_ids - profile_ids
    if unknown_monthly_ids:
        raise ValueError(
            f"Validation failed: monthly_df contains unknown borrower IDs: {sorted(unknown_monthly_ids)}"
        )

    expected_months = set(range(1, 13))
    for borrower_id in profile_ids:
        borrower_monthly = monthly_df[monthly_df["borrower_id"] == borrower_id]
        actual_months = set(borrower_monthly["month"])
        if len(borrower_monthly) != 12 or actual_months != expected_months:
            raise ValueError(
                f"Validation failed: borrower_id '{borrower_id}' must have exactly one row for each month 1-12."
            )

    if ((profile_df[["household_income", "savings_buffer", "other_loan_emi"]] < 0).any().any()):
        raise ValueError("Validation failed: profile financial values cannot be negative.")
    if ((monthly_df[["income", "expenses", "mfi_repayment_due", "mfi_repayment_paid"]] < 0).any().any()):
        raise ValueError("Validation failed: monthly financial values cannot be negative.")

    if ((relationships_df["weight"] < 0) | (relationships_df["weight"] > 1)).any():
        raise ValueError("Validation failed: relationship weights must be between 0 and 1.")
    if (relationships_df["borrower_a"] == relationships_df["borrower_b"]).any():
        raise ValueError("Validation failed: relationships cannot connect a borrower to itself.")

    relationship_pairs = relationships_df.apply(
        lambda row: tuple(sorted((row["borrower_a"], row["borrower_b"]))), axis=1
    )
    if relationship_pairs.duplicated().any():
        raise ValueError("Validation failed: duplicate borrower relationships are not allowed.")

    relationship_ids = set(relationships_df["borrower_a"]) | set(relationships_df["borrower_b"])
    unknown_relationship_ids = relationship_ids - profile_ids
    if unknown_relationship_ids:
        raise ValueError(
            "Validation failed: relationships_df contains unknown borrower IDs: "
            f"{sorted(unknown_relationship_ids)}"
        )


@st.cache_data
def load_all_data() -> tuple:
    """
    Load and validate borrower profile, monthly, and relationship data from CSVs.
    
    Returns:
        tuple: A 3-tuple containing (profile_df, monthly_df, relationships_df).
        
    Raises:
        FileNotFoundError: If any of the required CSV files are missing.
        ValueError: If data integrity validations fail (e.g., missing months or invalid IDs).
    """
    try:
        profile_df = pd.read_csv(PROFILE_CSV)
        monthly_df = pd.read_csv(MONTHLY_CSV)
        relationships_df = pd.read_csv(RELATIONSHIPS_CSV)
    except FileNotFoundError:
        raise FileNotFoundError("Data files not found — run `python data/generate_data.py` first.")

    validate_dataframes(profile_df, monthly_df, relationships_df)

    return profile_df, monthly_df, relationships_df


def load_all_data_or_stop() -> tuple:
    """Load validated data and render a recoverable Streamlit error on failure."""
    try:
        return load_all_data()
    except (FileNotFoundError, ValueError, pd.errors.ParserError) as error:
        st.error("ResilienceOS could not load a valid borrower dataset.")
        st.caption(str(error))
        st.info("Regenerate the demo data with `python3 data/generate_data.py`, then reload this page.")
        st.stop()
    except Exception:
        logger.exception("Unexpected failure while loading ResilienceOS data")
        st.error("ResilienceOS encountered an unexpected data-loading error.")
        st.info("Check the terminal logs, then reload the app after correcting the dataset.")
        st.stop()