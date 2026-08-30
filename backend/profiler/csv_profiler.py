import pandas as pd
import numpy as np
import json
from typing import List, Dict, Any


def profile_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Profile a pandas DataFrame and return column-level statistics.
    Shared by the CSV and SQL profilers.
    """
    total_rows = len(df)
    total_cols = len(df.columns)

    column_profiles = []

    for col in df.columns:
        series = df[col]
        dtype = str(series.dtype)
        null_count = int(series.isnull().sum())
        null_pct = round((null_count / total_rows) * 100, 2) if total_rows > 0 else 0
        distinct_count = int(series.nunique())
        duplicate_count = int(total_rows - distinct_count - null_count)

        min_val = max_val = mean_val = std_val = None

        if pd.api.types.is_numeric_dtype(series):
            clean = series.dropna()
            if len(clean) > 0:
                min_val = str(round(float(clean.min()), 4))
                max_val = str(round(float(clean.max()), 4))
                mean_val = round(float(clean.mean()), 4)
                # std() is NaN for a single value (ddof=1) — NaN isn't valid JSON
                raw_std = clean.std()
                std_val = round(float(raw_std), 4) if pd.notna(raw_std) else 0.0

        # Quality score: penalise nulls and duplicates
        quality_score = 100.0
        quality_score -= min(null_pct * 2, 50)
        dup_pct = (duplicate_count / total_rows * 100) if total_rows > 0 else 0
        quality_score -= min(dup_pct, 30)
        quality_score = max(round(quality_score, 2), 0)

        sample_values = json.dumps(
            series.dropna().head(5).astype(str).tolist()
        )

        column_profiles.append({
            "column_name": col,
            "data_type": dtype,
            "null_count": null_count,
            "null_pct": null_pct,
            "distinct_count": distinct_count,
            "duplicate_count": max(duplicate_count, 0),
            "min_value": min_val,
            "max_value": max_val,
            "mean_value": mean_val,
            "std_dev": std_val,
            "quality_score": quality_score,
            "sample_values": sample_values,
        })

    return {
        "total_rows": total_rows,
        "total_columns": total_cols,
        "column_profiles": column_profiles,
        "dataframe": df,
    }


def profile_csv(file_path: str) -> Dict[str, Any]:
    """
    Profile a CSV file and return column-level statistics.
    Returns a dict with overall stats and per-column profiles.
    """
    df = pd.read_csv(file_path)
    return profile_dataframe(df)
