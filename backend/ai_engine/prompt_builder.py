from typing import List, Dict


def build_explanation_prompt(anomaly: Dict, column_profile: Dict, source_name: str) -> str:
    """
    Build a structured prompt for Claude to explain an anomaly
    and suggest a concrete fix.
    """
    return f"""You are a senior data engineer analyzing a data quality issue.

SOURCE: {source_name}
COLUMN: {anomaly['column_name']}
ANOMALY TYPE: {anomaly['anomaly_type']}
SEVERITY: {anomaly['severity']}
DETECTED: {anomaly['detected_value']}
EXPECTED: {anomaly['expected_range']}
AFFECTED ROWS: {anomaly.get('affected_rows', 'unknown')}

COLUMN STATS:
- Data type: {column_profile.get('data_type', 'unknown')}
- Null %: {column_profile.get('null_pct', 0)}%
- Distinct values: {column_profile.get('distinct_count', 'unknown')}
- Mean: {column_profile.get('mean_value', 'N/A')}
- Std dev: {column_profile.get('std_dev', 'N/A')}
- Sample values: {column_profile.get('sample_values', '[]')}

Respond in this exact JSON format (no markdown, no extra text):
{{
  "explanation": "One clear sentence explaining what went wrong and likely why.",
  "root_cause": "The most probable technical root cause (e.g. ETL failure, upstream bug, data entry error).",
  "business_impact": "What business decision could be wrong because of this issue.",
  "recommendation": "One concrete action the engineer should take right now.",
  "fix_code": "A short SQL query or Python snippet that fixes or investigates the issue. Use the actual column name."
}}"""


def build_summary_prompt(anomalies: List[Dict], health_score: float, source_name: str) -> str:
    """
    Build a prompt for an overall run summary from Claude.
    """
    anomaly_summary = "\n".join([
        f"- [{a['severity'].upper()}] {a['column_name']}: {a['anomaly_type']} — {a['detected_value']}"
        for a in anomalies
    ])

    return f"""You are a senior data engineer. Summarize this data quality run in 2-3 sentences.
Be direct and actionable. Mention the most critical issue first.

SOURCE: {source_name}
HEALTH SCORE: {health_score}/100
ANOMALIES FOUND:
{anomaly_summary if anomaly_summary else 'No anomalies detected.'}

Respond with plain text only. No markdown. No bullet points. Just 2-3 sentences."""
