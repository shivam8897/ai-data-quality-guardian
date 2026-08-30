import os
import uuid
import time
import json
import shutil
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from dotenv import load_dotenv

load_dotenv()

from database import get_db, run_migrations, engine
from models import Base, QualityRun, Anomaly, ColumnProfile
from profiler.csv_profiler import profile_csv
from profiler.sql_profiler import profile_table
from anomaly.detector import detect_anomalies, detect_schema_drift
from anomaly.scoring import calculate_health_score
from ai_engine.explainer import explain_anomaly, generate_run_summary

# Create tables
Base.metadata.create_all(bind=engine)

# Run SQL migrations
try:
    run_migrations()
except Exception as e:
    print(f"[WARN] Migration warning: {e}")

app = FastAPI(title="AI Data Quality Guardian", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class ConnectRequest(BaseModel):
    connection_string: str
    table_name: str
    sample_rows: Optional[int] = None


@app.get("/health")
def health_check():
    return {"status": "ok", "version": "1.0.0"}


def run_quality_pipeline(db: Session, run: QualityRun, profile_result: dict) -> dict:
    """
    Shared pipeline used by both the CSV upload and DB-connect endpoints:
    anomaly detection, schema drift, health scoring, AI explanations, persistence.
    """
    start_time = time.time()
    df = profile_result["dataframe"]
    column_profiles = profile_result["column_profiles"]

    try:
        # Step 1: Detect anomalies
        anomalies = detect_anomalies(df, column_profiles)

        # Step 2: Schema drift (compare with last run for the same source)
        last_run = (
            db.query(QualityRun)
            .filter(QualityRun.source_name == run.source_name, QualityRun.id != run.id)
            .order_by(QualityRun.run_at.desc())
            .first()
        )
        if last_run:
            prev_profiles = [
                {
                    "column_name": cp.column_name,
                    "data_type": cp.data_type,
                    "null_pct": float(cp.null_pct or 0),
                    "quality_score": float(cp.quality_score or 0),
                }
                for cp in last_run.column_profiles
            ]
            schema_anomalies = detect_schema_drift(column_profiles, prev_profiles)
            anomalies.extend(schema_anomalies)

        # Step 3: Calculate health score
        health_score = calculate_health_score(column_profiles, anomalies)

        # Step 4: AI explanation for each anomaly
        col_profile_map = {p["column_name"]: p for p in column_profiles}
        saved_anomalies = []

        for anomaly in anomalies:
            col_profile = col_profile_map.get(anomaly["column_name"], {})
            ai_result = explain_anomaly(anomaly, col_profile, run.source_name)

            db_anomaly = Anomaly(
                run_id=run.id,
                column_name=anomaly["column_name"],
                anomaly_type=anomaly["anomaly_type"],
                severity=anomaly["severity"],
                detected_value=anomaly["detected_value"],
                expected_range=anomaly["expected_range"],
                affected_rows=anomaly.get("affected_rows", 0),
                ai_explanation=ai_result["ai_explanation"],
                ai_recommendation=ai_result["ai_recommendation"],
                ai_fix_code=ai_result["ai_fix_code"],
            )
            db.add(db_anomaly)
            saved_anomalies.append({**anomaly, **ai_result})

        # Step 5: Save column profiles
        for cp in column_profiles:
            db_cp = ColumnProfile(
                run_id=run.id,
                column_name=cp["column_name"],
                data_type=cp["data_type"],
                null_count=cp["null_count"],
                null_pct=cp["null_pct"],
                distinct_count=cp["distinct_count"],
                duplicate_count=cp["duplicate_count"],
                min_value=cp["min_value"],
                max_value=cp["max_value"],
                mean_value=cp["mean_value"],
                std_dev=cp["std_dev"],
                quality_score=cp["quality_score"],
                sample_values=cp["sample_values"],
            )
            db.add(db_cp)

        # Step 6: AI run summary
        run_summary = generate_run_summary(saved_anomalies, health_score, run.source_name)

        # Update run record
        duration = round(time.time() - start_time, 2)
        run.health_score = health_score
        run.total_rows = profile_result["total_rows"]
        run.total_columns = profile_result["total_columns"]
        run.status = "completed"
        run.duration_secs = duration
        db.commit()

        return {
            "run_id": run.id,
            "source_name": run.source_name,
            "health_score": health_score,
            "total_rows": profile_result["total_rows"],
            "total_columns": profile_result["total_columns"],
            "duration_secs": duration,
            "anomalies": saved_anomalies,
            "column_profiles": column_profiles,
            "ai_summary": run_summary,
            "status": "completed",
        }

    except Exception as e:
        run.status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {str(e)}")


@app.post("/api/upload")
async def upload_and_check(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Main endpoint: user uploads a CSV file.
    Runs full quality check pipeline and returns results.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    # Save file
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Create run record
    run = QualityRun(
        source_name=file.filename,
        source_type="csv",
        file_path=file_path,
        status="running",
        triggered_by="user",
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    try:
        profile_result = profile_csv(file_path)
    except Exception as e:
        run.status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Failed to read CSV: {str(e)}")

    return run_quality_pipeline(db, run, profile_result)


@app.post("/api/connect")
async def connect_and_check(
    req: ConnectRequest,
    db: Session = Depends(get_db)
):
    """
    Connect to a database table, profile it, and run the full quality check
    pipeline — the DB-source equivalent of /api/upload.
    Note: the connection string is used to fetch data and is never persisted.
    """
    # Create run record (never store the connection string — only the table name)
    run = QualityRun(
        source_name=req.table_name,
        source_type="database",
        file_path=req.table_name,
        status="running",
        triggered_by="user",
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    try:
        profile_result = profile_table(req.connection_string, req.table_name, req.sample_rows)
    except ValueError as e:
        run.status = "failed"
        db.commit()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        run.status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Failed to connect/query table: {str(e)}")

    return run_quality_pipeline(db, run, profile_result)


@app.get("/api/runs")
def get_runs(limit: int = 20, db: Session = Depends(get_db)):
    """Get recent quality runs."""
    runs = (
        db.query(QualityRun)
        .order_by(QualityRun.run_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": r.id,
            "source_name": r.source_name,
            "health_score": float(r.health_score or 0),
            "total_rows": r.total_rows,
            "total_columns": r.total_columns,
            "status": r.status,
            "run_at": r.run_at.isoformat(),
            "anomaly_count": len(r.anomalies),
        }
        for r in runs
    ]


@app.get("/api/runs/{run_id}")
def get_run_detail(run_id: int, db: Session = Depends(get_db)):
    """Get full details for a specific run."""
    run = db.query(QualityRun).filter(QualityRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    return {
        "id": run.id,
        "source_name": run.source_name,
        "health_score": float(run.health_score or 0),
        "total_rows": run.total_rows,
        "total_columns": run.total_columns,
        "status": run.status,
        "run_at": run.run_at.isoformat(),
        "duration_secs": float(run.duration_secs or 0),
        "anomalies": [
            {
                "id": a.id,
                "column_name": a.column_name,
                "anomaly_type": a.anomaly_type,
                "severity": a.severity,
                "detected_value": a.detected_value,
                "expected_range": a.expected_range,
                "affected_rows": a.affected_rows,
                "ai_explanation": a.ai_explanation,
                "ai_recommendation": a.ai_recommendation,
                "ai_fix_code": a.ai_fix_code,
            }
            for a in run.anomalies
        ],
        "column_profiles": [
            {
                "column_name": cp.column_name,
                "data_type": cp.data_type,
                "null_pct": float(cp.null_pct or 0),
                "duplicate_count": cp.duplicate_count,
                "quality_score": float(cp.quality_score or 0),
                "mean_value": float(cp.mean_value) if cp.mean_value else None,
                "std_dev": float(cp.std_dev) if cp.std_dev else None,
            }
            for cp in run.column_profiles
        ],
    }
