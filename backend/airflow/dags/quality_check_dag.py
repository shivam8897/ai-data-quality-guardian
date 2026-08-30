from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, "/app")

default_args = {
    "owner": "dq-guardian",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": False,
}

def run_quality_check(**context):
    """
    Main task: runs the full quality check pipeline.
    Can be triggered on schedule or by file upload via API.
    Returns the pipeline result so it can be pulled via XCom by send_alert.
    """
    import requests

    file_path = context["dag_run"].conf.get("file_path")
    source_name = context["dag_run"].conf.get("source_name", "scheduled_check")

    if file_path and os.path.exists(file_path):
        with open(file_path, "rb") as f:
            response = requests.post(
                "http://backend:8000/api/upload",
                files={"file": (source_name, f, "text/csv")},
            )
        response.raise_for_status()
        result = response.json()
        print(f"[DAG] Quality check result: {result}")
        return result
    else:
        print("[DAG] No file_path provided. Scheduled run — skipping.")
        return None


def send_alert(**context):
    """Alert task: fires if health score is below threshold."""
    ti = context["task_instance"]
    result = ti.xcom_pull(task_ids="run_quality_check")
    if result and result.get("health_score", 100) < 70:
        message = (
            f"[ALERT] Data quality critical for '{result.get('source_name')}': "
            f"health score {result['health_score']}/100 "
            f"({len(result.get('anomalies', []))} anomalies detected)"
        )
        print(message)

        webhook_url = os.getenv("ALERT_WEBHOOK_URL")
        if webhook_url:
            import requests
            try:
                requests.post(webhook_url, json={"text": message}, timeout=10)
            except Exception as e:
                print(f"[ALERT] Failed to deliver webhook alert: {e}")
        else:
            print("[ALERT] ALERT_WEBHOOK_URL not set — skipping delivery, logged above only.")


with DAG(
    dag_id="daily_quality_check",
    default_args=default_args,
    description="Run data quality checks daily at 6am",
    schedule_interval="0 6 * * *",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["data-quality", "ai"],
) as dag:

    quality_task = PythonOperator(
        task_id="run_quality_check",
        python_callable=run_quality_check,
        provide_context=True,
    )

    alert_task = PythonOperator(
        task_id="send_alert_if_critical",
        python_callable=send_alert,
        provide_context=True,
    )

    quality_task >> alert_task
