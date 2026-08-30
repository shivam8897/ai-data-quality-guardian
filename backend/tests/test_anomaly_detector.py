import numpy as np
import pandas as pd

from anomaly.detector import detect_anomalies, detect_schema_drift


def _profile_for(df, col):
    """Minimal column_profiles entry, matching csv_profiler's shape enough for detector.py."""
    series = df[col]
    null_count = int(series.isnull().sum())
    distinct_count = int(series.nunique())
    total = len(df)
    return {
        "column_name": col,
        "data_type": str(series.dtype),
        "null_count": null_count,
        "null_pct": round((null_count / total) * 100, 2) if total else 0,
        "duplicate_count": max(total - distinct_count - null_count, 0),
    }


def test_detect_anomalies_flags_null_spike():
    df = pd.DataFrame({"col": [1, None, None, None, 5]})  # 60% null
    profiles = [_profile_for(df, "col")]

    anomalies = detect_anomalies(df, profiles)

    null_anomalies = [a for a in anomalies if a["anomaly_type"] == "null_spike"]
    assert len(null_anomalies) == 1
    assert null_anomalies[0]["severity"] == "critical"


def test_detect_anomalies_flags_statistical_outlier():
    rng = np.random.default_rng(42)
    values = list(rng.normal(0, 1, 100)) + [1000]  # one obvious outlier
    df = pd.DataFrame({"col": values})
    profiles = [_profile_for(df, "col")]

    anomalies = detect_anomalies(df, profiles)

    outlier_anomalies = [a for a in anomalies if a["anomaly_type"] == "statistical_outlier"]
    assert len(outlier_anomalies) == 1


def test_detect_anomalies_no_anomalies_on_clean_data():
    df = pd.DataFrame({"col": range(20)})
    profiles = [_profile_for(df, "col")]

    anomalies = detect_anomalies(df, profiles)

    assert anomalies == []


def test_detect_schema_drift_added_removed_and_type_change():
    previous = [
        {"column_name": "a", "data_type": "int64"},
        {"column_name": "b", "data_type": "object"},
    ]
    current = [
        {"column_name": "a", "data_type": "float64"},  # type change
        {"column_name": "c", "data_type": "object"},   # added
        # "b" removed
    ]

    anomalies = detect_schema_drift(current, previous)
    types = {a["anomaly_type"] for a in anomalies}

    assert "schema_drift_added" in types
    assert "schema_drift_removed" in types
    assert "schema_drift_type_change" in types


def test_detect_schema_drift_no_previous_run():
    assert detect_schema_drift([{"column_name": "a", "data_type": "int64"}], []) == []
