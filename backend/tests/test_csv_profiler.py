import json

import pandas as pd

from profiler.csv_profiler import profile_dataframe


def test_profile_dataframe_basic_stats():
    df = pd.DataFrame({
        "id": [1, 2, 3, 4, 5],
        "amount": [10.0, 20.0, None, 40.0, 50.0],
        "name": ["a", "b", "b", "c", None],
    })

    result = profile_dataframe(df)

    assert result["total_rows"] == 5
    assert result["total_columns"] == 3

    profiles = {p["column_name"]: p for p in result["column_profiles"]}

    amount = profiles["amount"]
    assert amount["null_count"] == 1
    assert amount["null_pct"] == 20.0
    assert amount["mean_value"] == 30.0

    name = profiles["name"]
    assert name["null_count"] == 1
    assert name["distinct_count"] == 3  # a, b, c


def test_profile_dataframe_quality_score_penalises_nulls():
    clean_df = pd.DataFrame({"col": [1, 2, 3, 4, 5]})
    dirty_df = pd.DataFrame({"col": [1, None, None, None, 5]})

    clean_score = profile_dataframe(clean_df)["column_profiles"][0]["quality_score"]
    dirty_score = profile_dataframe(dirty_df)["column_profiles"][0]["quality_score"]

    assert clean_score == 100.0
    assert dirty_score < clean_score


def test_profile_dataframe_empty():
    df = pd.DataFrame({"col": []})
    result = profile_dataframe(df)
    assert result["total_rows"] == 0
    assert result["column_profiles"][0]["null_pct"] == 0


def test_profile_dataframe_single_value_std_is_not_nan():
    # pandas std() with a single value is NaN (ddof=1), which is not valid JSON —
    # this must come back as a real number, not float('nan').
    df = pd.DataFrame({"col": [42.0]})
    result = profile_dataframe(df)
    std_dev = result["column_profiles"][0]["std_dev"]
    assert std_dev == 0.0
    json.dumps(result["column_profiles"])  # must not raise
