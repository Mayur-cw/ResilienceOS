"""Run with: python3 -m tests.test_data_validation"""

import pandas as pd

from utils.helpers import load_all_data, validate_dataframes


def run_tests():
    profile_df, monthly_df, relationships_df = load_all_data()

    invalid_monthly = monthly_df.copy()
    invalid_monthly.loc[0, "month"] = 99
    try:
        validate_dataframes(profile_df, invalid_monthly, relationships_df)
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid month coverage should be rejected")

    invalid_relationships = relationships_df.copy()
    invalid_relationships.loc[0, "weight"] = 1.5
    try:
        validate_dataframes(profile_df, monthly_df, invalid_relationships)
    except ValueError:
        pass
    else:
        raise AssertionError("Out-of-range relationship weights should be rejected")

    missing_column_profile = profile_df.drop(columns=["household_income"])
    try:
        validate_dataframes(missing_column_profile, monthly_df, relationships_df)
    except ValueError:
        pass
    else:
        raise AssertionError("Missing required columns should be rejected")

    assert isinstance(profile_df, pd.DataFrame)
    print("PASSED: test_data_validation.py")


if __name__ == "__main__":
    run_tests()