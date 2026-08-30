import os
import json
import anthropic
from typing import List, Dict
from .prompt_builder import build_explanation_prompt, build_summary_prompt

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

CLAUDE_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")


def explain_anomaly(anomaly: Dict, column_profile: Dict, source_name: str) -> Dict:
    """
    Send anomaly context to Claude and get plain English explanation + fix.
    Returns dict with explanation, root_cause, recommendation, fix_code.
    """
    prompt = build_explanation_prompt(anomaly, column_profile, source_name)
    raw = ""

    try:
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )

        raw = message.content[0].text.strip()

        # Parse JSON response
        result = json.loads(raw)
        return {
            "ai_explanation": result.get("explanation", ""),
            "ai_recommendation": result.get("recommendation", ""),
            "ai_fix_code": result.get("fix_code", ""),
            "root_cause": result.get("root_cause", ""),
            "business_impact": result.get("business_impact", ""),
        }

    except json.JSONDecodeError:
        # Fallback if Claude doesn't return clean JSON
        return {
            "ai_explanation": raw[:500] if raw else "Could not generate explanation.",
            "ai_recommendation": "Review the column manually.",
            "ai_fix_code": "",
            "root_cause": "Unknown",
            "business_impact": "Unknown",
        }
    except Exception as e:
        return {
            "ai_explanation": f"AI explanation unavailable: {str(e)}",
            "ai_recommendation": "Check your ANTHROPIC_API_KEY.",
            "ai_fix_code": "",
            "root_cause": "API error",
            "business_impact": "Unknown",
        }


def generate_run_summary(anomalies: List[Dict], health_score: float, source_name: str) -> str:
    """
    Generate a one-paragraph summary of the entire quality run.
    """
    prompt = build_summary_prompt(anomalies, health_score, source_name)

    try:
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text.strip()
    except Exception as e:
        return f"Quality run completed. Health score: {health_score}/100. {len(anomalies)} anomalies detected."
