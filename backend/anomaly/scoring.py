from typing import List, Dict


def calculate_health_score(column_profiles: List[Dict], anomalies: List[Dict]) -> float:
    """
    Calculate overall data health score (0-100).
    Starts at 100 and deducts points for anomalies by severity.
    """
    score = 100.0

    severity_penalties = {
        "critical": 20,
        "warning": 8,
        "info": 2,
    }

    for anomaly in anomalies:
        severity = anomaly.get("severity", "info")
        score -= severity_penalties.get(severity, 2)

    # Also penalise based on average column quality
    if column_profiles:
        avg_col_quality = sum(p["quality_score"] for p in column_profiles) / len(column_profiles)
        # Blend: 70% anomaly-based, 30% column quality
        score = (score * 0.7) + (avg_col_quality * 0.3)

    return round(max(score, 0), 2)
