import pandas as pd
import numpy as np
from scipy import stats
from sklearn.ensemble import IsolationForest
from typing import List, Dict, Any


def detect_anomalies(df: pd.DataFrame, column_profiles: List[Dict]) -> List[Dict]:
    """
    Run all anomaly detectors on the dataframe.
    Returns a list of detected anomalies with severity and context.
    """
    anomalies = []

    for profile in column_profiles:
        col = profile["column_name"]
        if col not in df.columns:
            continue

        series = df[col]

        # 1. NULL SPIKE CHECK
        null_pct = profile["null_pct"]
        if null_pct > 10:
            severity = "critical" if null_pct > 20 else "warning"
            anomalies.append({
                "column_name": col,
                "anomaly_type": "null_spike",
                "severity": severity,
                "detected_value": f"{null_pct}% nulls",
                "expected_range": "< 5% nulls",
                "affected_rows": profile["null_count"],
            })

        # 2. DUPLICATE CHECK
        dup_pct = (profile["duplicate_count"] / max(len(df), 1)) * 100
        if dup_pct > 5:
            anomalies.append({
                "column_name": col,
                "anomaly_type": "duplicates",
                "severity": "warning",
                "detected_value": f"{profile['duplicate_count']} duplicate rows",
                "expected_range": "0 duplicates expected",
                "affected_rows": profile["duplicate_count"],
            })

        # 3. OUTLIER DETECTION (numeric columns only)
        if pd.api.types.is_numeric_dtype(series):
            clean = series.dropna()
            if len(clean) > 10:
                # Z-score method
                z_scores = np.abs(stats.zscore(clean))
                outlier_count = int((z_scores > 3).sum())
                if outlier_count > 0:
                    outlier_vals = clean[z_scores > 3]
                    anomalies.append({
                        "column_name": col,
                        "anomaly_type": "statistical_outlier",
                        "severity": "warning" if outlier_count < 50 else "critical",
                        "detected_value": f"{outlier_count} outliers, max={round(float(outlier_vals.max()), 2)}",
                        "expected_range": f"mean={round(float(clean.mean()), 2)} ±3σ ({round(float(clean.std()), 2)})",
                        "affected_rows": outlier_count,
                    })

                # Isolation Forest (multi-column anomaly detection)
                if len(clean) > 50:
                    iso = IsolationForest(contamination=0.05, random_state=42)
                    preds = iso.fit_predict(clean.values.reshape(-1, 1))
                    iso_outliers = int((preds == -1).sum())
                    if iso_outliers > 0 and iso_outliers != outlier_count:
                        anomalies.append({
                            "column_name": col,
                            "anomaly_type": "isolation_forest_outlier",
                            "severity": "info",
                            "detected_value": f"{iso_outliers} anomalous rows detected by ML",
                            "expected_range": "< 5% contamination",
                            "affected_rows": iso_outliers,
                        })

    return anomalies


def detect_schema_drift(current_profiles: List[Dict], previous_profiles: List[Dict]) -> List[Dict]:
    """
    Detect schema drift between current run and previous run.
    """
    if not previous_profiles:
        return []

    anomalies = []
    prev_cols = {p["column_name"]: p for p in previous_profiles}
    curr_cols = {p["column_name"]: p for p in current_profiles}

    # Columns added
    for col in curr_cols:
        if col not in prev_cols:
            anomalies.append({
                "column_name": col,
                "anomaly_type": "schema_drift_added",
                "severity": "info",
                "detected_value": f"Column '{col}' was added",
                "expected_range": "Schema should match previous run",
                "affected_rows": 0,
            })

    # Columns removed
    for col in prev_cols:
        if col not in curr_cols:
            anomalies.append({
                "column_name": col,
                "anomaly_type": "schema_drift_removed",
                "severity": "critical",
                "detected_value": f"Column '{col}' was removed",
                "expected_range": "Schema should match previous run",
                "affected_rows": 0,
            })

    # Type changes
    for col in curr_cols:
        if col in prev_cols:
            if curr_cols[col]["data_type"] != prev_cols[col]["data_type"]:
                anomalies.append({
                    "column_name": col,
                    "anomaly_type": "schema_drift_type_change",
                    "severity": "warning",
                    "detected_value": f"Type changed: {prev_cols[col]['data_type']} → {curr_cols[col]['data_type']}",
                    "expected_range": f"Expected: {prev_cols[col]['data_type']}",
                    "affected_rows": 0,
                })

    return anomalies
