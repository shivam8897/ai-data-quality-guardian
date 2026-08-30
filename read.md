# 🛡️ AI Data Quality Guardian — Full Build Instructions for Claude

> **Instructions for Claude Code / VS Code Claude:**
> Read this entire file first. Then build every file listed in the folder structure below, using the exact code provided in each section. Do not skip any file. After building, run the setup commands at the bottom.

---

## What This Project Is

An AI-powered data quality monitoring platform. Any user can upload a CSV or connect a database. The system automatically:
1. Profiles the data (nulls, duplicates, schema drift, outliers)
2. Detects anomalies using statistical + ML methods
3. Sends anomaly context to Claude AI → gets plain English explanation + fix suggestion
4. Stores results in PostgreSQL
5. Shows everything on a React dashboard (health score, anomaly cards, column quality)

**This is what Monte Carlo Data charges $50K/year for. We build it open source with AI.**

---

## Tech Stack

- **Backend:** Python, FastAPI, Apache Airflow
- **Profiling/Detection:** pandas, scipy, scikit-learn, prophet
- **AI Engine:** Anthropic Claude API (claude-sonnet-4-6)
- **Database:** PostgreSQL (SQLAlchemy)
- **Frontend:** React + Vite + Tailwind CSS + Recharts
- **Infrastructure:** Docker + Docker Compose

---

## Folder Structure to Build

```
ai-data-quality-guardian/
├── CLAUDE.md                          ← this file
├── README.md
├── .env.example
├── docker-compose.yml
├── requirements.txt
│
├── backend/
│   ├── main.py                        ← FastAPI app
│   ├── database.py                    ← DB connection
│   ├── models.py                      ← SQLAlchemy models
│   │
│   ├── profiler/
│   │   ├── __init__.py
│   │   ├── csv_profiler.py            ← Profile CSV files
│   │   └── sql_profiler.py            ← Profile DB tables
│   │
│   ├── anomaly/
│   │   ├── __init__.py
│   │   ├── detector.py                ← Main anomaly detector
│   │   └── scoring.py                 ← Health score calculator
│   │
│   ├── ai_engine/
│   │   ├── __init__.py
│   │   ├── explainer.py               ← Claude API integration
│   │   └── prompt_builder.py          ← Build prompts from anomaly data
│   │
│   └── airflow/
│       └── dags/
│           └── quality_check_dag.py   ← Main Airflow DAG
│
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── index.css
│       └── components/
│           ├── Sidebar.jsx
│           ├── Topbar.jsx
│           ├── HealthScore.jsx
│           ├── KpiCards.jsx
│           ├── AnomalyTable.jsx
│           ├── AiInsightCard.jsx
│           ├── ColumnQuality.jsx
│           ├── TrendChart.jsx
│           └── UploadModal.jsx
│
└── migrations/
    ├── 001_create_quality_runs.sql
    ├── 002_create_anomalies.sql
    └── 003_create_column_profiles.sql
```

---

## FILE 1: `.env.example`

```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/qualitydb
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=qualitydb

# Anthropic
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Airflow
AIRFLOW__CORE__EXECUTOR=LocalExecutor
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://postgres:password@localhost:5432/airflow
AIRFLOW__CORE__FERNET_KEY=your_fernet_key_here
AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION=false
AIRFLOW__API__AUTH_BACKENDS=airflow.api.auth.backend.basic_auth

# App
FRONTEND_URL=http://localhost:5173
```

---

## FILE 2: `requirements.txt`

```txt
fastapi==0.111.0
uvicorn==0.30.1
sqlalchemy==2.0.30
psycopg2-binary==2.9.9
pandas==2.2.2
numpy==1.26.4
scipy==1.13.1
scikit-learn==1.5.0
prophet==1.1.5
anthropic==0.28.0
python-multipart==0.0.9
python-dotenv==1.0.1
apache-airflow==2.9.2
pydantic==2.7.4
alembic==1.13.1
httpx==0.27.0
```

---

## FILE 3: `docker-compose.yml`

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_MULTIPLE_DATABASES: qualitydb,airflow
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/qualitydb
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    depends_on:
      - postgres
    volumes:
      - ./backend:/app
      - ./uploads:/app/uploads

  airflow-webserver:
    image: apache/airflow:2.9.2
    command: webserver
    ports:
      - "8080:8080"
    environment:
      - AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://postgres:password@postgres:5432/airflow
      - AIRFLOW__CORE__EXECUTOR=LocalExecutor
      - AIRFLOW__CORE__FERNET_KEY=${AIRFLOW__CORE__FERNET_KEY}
      - AIRFLOW__API__AUTH_BACKENDS=airflow.api.auth.backend.basic_auth
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/qualitydb
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    depends_on:
      - postgres
    volumes:
      - ./backend/airflow/dags:/opt/airflow/dags
      - ./uploads:/opt/airflow/uploads

  airflow-scheduler:
    image: apache/airflow:2.9.2
    command: scheduler
    environment:
      - AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://postgres:password@postgres:5432/airflow
      - AIRFLOW__CORE__EXECUTOR=LocalExecutor
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/qualitydb
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    depends_on:
      - postgres
    volumes:
      - ./backend/airflow/dags:/opt/airflow/dags
      - ./uploads:/opt/airflow/uploads

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "5173:5173"
    depends_on:
      - backend

volumes:
  postgres_data:
```

---

## FILE 4: `migrations/001_create_quality_runs.sql`

```sql
CREATE TABLE IF NOT EXISTS quality_runs (
    id              SERIAL PRIMARY KEY,
    source_name     VARCHAR(255) NOT NULL,
    source_type     VARCHAR(50) NOT NULL,
    file_path       TEXT,
    run_at          TIMESTAMP DEFAULT NOW(),
    health_score    NUMERIC(5,2),
    total_rows      INTEGER,
    total_columns   INTEGER,
    status          VARCHAR(20) DEFAULT 'running',
    triggered_by    VARCHAR(50) DEFAULT 'user',
    duration_secs   NUMERIC(8,2)
);
```

---

## FILE 5: `migrations/002_create_anomalies.sql`

```sql
CREATE TABLE IF NOT EXISTS anomalies (
    id                  SERIAL PRIMARY KEY,
    run_id              INTEGER REFERENCES quality_runs(id) ON DELETE CASCADE,
    column_name         VARCHAR(255),
    anomaly_type        VARCHAR(100),
    severity            VARCHAR(20),
    detected_value      TEXT,
    expected_range      TEXT,
    affected_rows       INTEGER,
    ai_explanation      TEXT,
    ai_recommendation   TEXT,
    ai_fix_code         TEXT,
    created_at          TIMESTAMP DEFAULT NOW()
);
```

---

## FILE 6: `migrations/003_create_column_profiles.sql`

```sql
CREATE TABLE IF NOT EXISTS column_profiles (
    id              SERIAL PRIMARY KEY,
    run_id          INTEGER REFERENCES quality_runs(id) ON DELETE CASCADE,
    column_name     VARCHAR(255),
    data_type       VARCHAR(50),
    null_count      INTEGER,
    null_pct        NUMERIC(5,2),
    distinct_count  INTEGER,
    duplicate_count INTEGER,
    min_value       TEXT,
    max_value       TEXT,
    mean_value      NUMERIC,
    std_dev         NUMERIC,
    quality_score   NUMERIC(5,2),
    sample_values   TEXT
);
```

---

## FILE 7: `backend/database.py`

```python
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/qualitydb")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def run_migrations():
    migrations_dir = os.path.join(os.path.dirname(__file__), "..", "migrations")
    migration_files = sorted([
        f for f in os.listdir(migrations_dir) if f.endswith(".sql")
    ])
    with engine.connect() as conn:
        for migration_file in migration_files:
            filepath = os.path.join(migrations_dir, migration_file)
            with open(filepath, "r") as f:
                sql = f.read()
            conn.execute(text(sql))
            conn.commit()
            print(f"[DB] Ran migration: {migration_file}")
```

---

## FILE 8: `backend/models.py`

```python
from sqlalchemy import Column, Integer, String, Numeric, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class QualityRun(Base):
    __tablename__ = "quality_runs"

    id = Column(Integer, primary_key=True, index=True)
    source_name = Column(String(255), nullable=False)
    source_type = Column(String(50), nullable=False)
    file_path = Column(Text)
    run_at = Column(DateTime, default=datetime.utcnow)
    health_score = Column(Numeric(5, 2))
    total_rows = Column(Integer)
    total_columns = Column(Integer)
    status = Column(String(20), default="running")
    triggered_by = Column(String(50), default="user")
    duration_secs = Column(Numeric(8, 2))

    anomalies = relationship("Anomaly", back_populates="run", cascade="all, delete")
    column_profiles = relationship("ColumnProfile", back_populates="run", cascade="all, delete")


class Anomaly(Base):
    __tablename__ = "anomalies"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("quality_runs.id", ondelete="CASCADE"))
    column_name = Column(String(255))
    anomaly_type = Column(String(100))
    severity = Column(String(20))
    detected_value = Column(Text)
    expected_range = Column(Text)
    affected_rows = Column(Integer)
    ai_explanation = Column(Text)
    ai_recommendation = Column(Text)
    ai_fix_code = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    run = relationship("QualityRun", back_populates="anomalies")


class ColumnProfile(Base):
    __tablename__ = "column_profiles"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("quality_runs.id", ondelete="CASCADE"))
    column_name = Column(String(255))
    data_type = Column(String(50))
    null_count = Column(Integer)
    null_pct = Column(Numeric(5, 2))
    distinct_count = Column(Integer)
    duplicate_count = Column(Integer)
    min_value = Column(Text)
    max_value = Column(Text)
    mean_value = Column(Numeric)
    std_dev = Column(Numeric)
    quality_score = Column(Numeric(5, 2))
    sample_values = Column(Text)

    run = relationship("QualityRun", back_populates="column_profiles")
```

---

## FILE 9: `backend/profiler/csv_profiler.py`

```python
import pandas as pd
import numpy as np
import json
from typing import List, Dict, Any


def profile_csv(file_path: str) -> Dict[str, Any]:
    """
    Profile a CSV file and return column-level statistics.
    Returns a dict with overall stats and per-column profiles.
    """
    df = pd.read_csv(file_path)
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
                std_val = round(float(clean.std()), 4)

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
```

---

## FILE 10: `backend/anomaly/detector.py`

```python
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
```

---

## FILE 11: `backend/anomaly/scoring.py`

```python
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
```

---

## FILE 12: `backend/ai_engine/prompt_builder.py`

```python
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
```

---

## FILE 13: `backend/ai_engine/explainer.py`

```python
import os
import json
import anthropic
from typing import List, Dict
from .prompt_builder import build_explanation_prompt, build_summary_prompt

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def explain_anomaly(anomaly: Dict, column_profile: Dict, source_name: str) -> Dict:
    """
    Send anomaly context to Claude and get plain English explanation + fix.
    Returns dict with explanation, root_cause, recommendation, fix_code.
    """
    prompt = build_explanation_prompt(anomaly, column_profile, source_name)

    try:
        message = client.messages.create(
            model="claude-sonnet-4-6",
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
            model="claude-sonnet-4-6",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text.strip()
    except Exception as e:
        return f"Quality run completed. Health score: {health_score}/100. {len(anomalies)} anomalies detected."
```

---

## FILE 14: `backend/main.py`

```python
import os
import uuid
import time
import json
import shutil
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv

load_dotenv()

from database import get_db, run_migrations, engine
from models import Base, QualityRun, Anomaly, ColumnProfile
from profiler.csv_profiler import profile_csv
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


@app.get("/health")
def health_check():
    return {"status": "ok", "version": "1.0.0"}


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

    start_time = time.time()

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
        # Step 1: Profile
        profile_result = profile_csv(file_path)
        df = profile_result["dataframe"]
        column_profiles = profile_result["column_profiles"]

        # Step 2: Detect anomalies
        anomalies = detect_anomalies(df, column_profiles)

        # Step 3: Schema drift (compare with last run)
        last_run = (
            db.query(QualityRun)
            .filter(QualityRun.source_name == file.filename, QualityRun.id != run.id)
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

        # Step 4: Calculate health score
        health_score = calculate_health_score(column_profiles, anomalies)

        # Step 5: AI Explanation for each anomaly
        col_profile_map = {p["column_name"]: p for p in column_profiles}
        saved_anomalies = []

        for anomaly in anomalies:
            col_profile = col_profile_map.get(anomaly["column_name"], {})
            ai_result = explain_anomaly(anomaly, col_profile, file.filename)

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

        # Step 6: Save column profiles
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

        # Step 7: AI run summary
        run_summary = generate_run_summary(saved_anomalies, health_score, file.filename)

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
            "source_name": file.filename,
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
```

---

## FILE 15: `backend/airflow/dags/quality_check_dag.py`

```python
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
        print(f"[DAG] Quality check result: {response.json()}")
    else:
        print(f"[DAG] No file_path provided. Scheduled run — skipping.")


def send_alert(**context):
    """Alert task: fires if health score is below threshold."""
    ti = context["task_instance"]
    result = ti.xcom_pull(task_ids="run_quality_check")
    if result and result.get("health_score", 100) < 70:
        print(f"[ALERT] Health score critical: {result['health_score']}")
        # Add your Slack/email alert here


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
```

---

## FILE 16: `frontend/package.json`

```json
{
  "name": "dq-guardian-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "recharts": "^2.12.7",
    "axios": "^1.7.2",
    "lucide-react": "^0.383.0",
    "clsx": "^2.1.1"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.1",
    "vite": "^5.3.1",
    "tailwindcss": "^3.4.4",
    "autoprefixer": "^10.4.19",
    "postcss": "^8.4.39"
  }
}
```

---

## FILE 17: `frontend/src/App.jsx`

```jsx
import { useState, useEffect } from "react";
import axios from "axios";
import Sidebar from "./components/Sidebar";
import Topbar from "./components/Topbar";
import KpiCards from "./components/KpiCards";
import HealthScore from "./components/HealthScore";
import TrendChart from "./components/TrendChart";
import AnomalyTable from "./components/AnomalyTable";
import AiInsightCard from "./components/AiInsightCard";
import ColumnQuality from "./components/ColumnQuality";
import UploadModal from "./components/UploadModal";

const API = "http://localhost:8000";

export default function App() {
  const [runs, setRuns] = useState([]);
  const [selectedRun, setSelectedRun] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showUpload, setShowUpload] = useState(false);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    fetchRuns();
  }, []);

  const fetchRuns = async () => {
    try {
      const res = await axios.get(`${API}/api/runs`);
      setRuns(res.data);
      if (res.data.length > 0 && !selectedRun) {
        fetchRunDetail(res.data[0].id);
      }
    } catch (err) {
      console.error("Failed to fetch runs:", err);
    }
  };

  const fetchRunDetail = async (runId) => {
    setLoading(true);
    try {
      const res = await axios.get(`${API}/api/runs/${runId}`);
      setSelectedRun(res.data);
    } catch (err) {
      console.error("Failed to fetch run detail:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (file) => {
    setUploading(true);
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await axios.post(`${API}/api/upload`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setSelectedRun(res.data);
      await fetchRuns();
      setShowUpload(false);
    } catch (err) {
      alert("Upload failed: " + (err.response?.data?.detail || err.message));
    } finally {
      setUploading(false);
    }
  };

  const run = selectedRun;
  const criticalCount = run?.anomalies?.filter(a => a.severity === "critical").length || 0;
  const warningCount = run?.anomalies?.filter(a => a.severity === "warning").length || 0;
  const topAnomaly = run?.anomalies?.find(a => a.severity === "critical") || run?.anomalies?.[0];

  return (
    <div style={{ display: "flex", height: "100vh", background: "#f0f2f5", fontFamily: "Inter, sans-serif" }}>
      <Sidebar runs={runs} selectedRunId={run?.id} onSelectRun={fetchRunDetail} />

      <div style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}>
        <Topbar
          sourceName={run?.source_name || "No data"}
          onUpload={() => setShowUpload(true)}
          onRefresh={fetchRuns}
        />

        {loading ? (
          <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", color: "#98a2b3" }}>
            Running quality check...
          </div>
        ) : run ? (
          <div style={{ flex: 1, overflowY: "auto", padding: "18px 20px", display: "flex", flexDirection: "column", gap: 14 }}>
            <KpiCards
              healthScore={run.health_score}
              totalRows={run.total_rows}
              criticalCount={criticalCount}
              warningCount={warningCount}
              duration={run.duration_secs}
            />

            <div style={{ display: "grid", gridTemplateColumns: "1.4fr 1fr", gap: 12 }}>
              <TrendChart runs={runs} currentRunId={run.id} />
              <HealthScore score={run.health_score} anomalyCount={run.anomalies?.length || 0} />
            </div>

            {topAnomaly && <AiInsightCard anomaly={topAnomaly} />}

            <AnomalyTable anomalies={run.anomalies || []} />

            <ColumnQuality profiles={run.column_profiles || []} />
          </div>
        ) : (
          <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", flexDirection: "column", gap: 12 }}>
            <p style={{ color: "#98a2b3", fontSize: 14 }}>No data yet. Upload a CSV to get started.</p>
            <button
              onClick={() => setShowUpload(true)}
              style={{ background: "#18181b", color: "#fff", border: "none", padding: "8px 20px", borderRadius: 8, cursor: "pointer", fontSize: 13, fontWeight: 500 }}
            >
              Upload CSV
            </button>
          </div>
        )}
      </div>

      {showUpload && (
        <UploadModal
          onUpload={handleUpload}
          onClose={() => setShowUpload(false)}
          uploading={uploading}
        />
      )}
    </div>
  );
}
```

---

## FILE 18: `frontend/src/components/UploadModal.jsx`

```jsx
import { useState, useRef } from "react";

export default function UploadModal({ onUpload, onClose, uploading }) {
  const [dragging, setDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const inputRef = useRef();

  const handleFile = (file) => {
    if (file && file.name.endsWith(".csv")) {
      setSelectedFile(file);
    } else {
      alert("Please upload a CSV file.");
    }
  };

  return (
    <div style={{
      position: "fixed", inset: 0, background: "rgba(0,0,0,0.4)",
      display: "flex", alignItems: "center", justifyContent: "center", zIndex: 100
    }}>
      <div style={{
        background: "#fff", borderRadius: 14, padding: 28, width: 420,
        boxShadow: "0 20px 60px rgba(0,0,0,0.15)"
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
          <h2 style={{ fontSize: 16, fontWeight: 600, color: "#101828" }}>Upload CSV for Quality Check</h2>
          <button onClick={onClose} style={{ background: "none", border: "none", cursor: "pointer", fontSize: 20, color: "#98a2b3" }}>×</button>
        </div>

        <div
          onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={(e) => { e.preventDefault(); setDragging(false); handleFile(e.dataTransfer.files[0]); }}
          onClick={() => inputRef.current.click()}
          style={{
            border: `2px dashed ${dragging ? "#3b82f6" : "#e5e7eb"}`,
            borderRadius: 10, padding: "32px 20px", textAlign: "center",
            cursor: "pointer", background: dragging ? "#eff6ff" : "#f9fafb",
            transition: "all 0.15s", marginBottom: 16
          }}
        >
          <input ref={inputRef} type="file" accept=".csv" style={{ display: "none" }} onChange={(e) => handleFile(e.target.files[0])} />
          <div style={{ fontSize: 32, marginBottom: 8 }}>📂</div>
          {selectedFile ? (
            <p style={{ fontSize: 13, color: "#3b82f6", fontWeight: 500 }}>{selectedFile.name}</p>
          ) : (
            <>
              <p style={{ fontSize: 13, color: "#344054", fontWeight: 500 }}>Drop your CSV here or click to browse</p>
              <p style={{ fontSize: 12, color: "#98a2b3", marginTop: 4 }}>Supports any CSV file with headers</p>
            </>
          )}
        </div>

        <div style={{ display: "flex", gap: 8 }}>
          <button onClick={onClose} style={{
            flex: 1, padding: "9px 0", border: "1px solid #e5e7eb", borderRadius: 8,
            background: "#fff", color: "#344054", fontSize: 13, fontWeight: 500, cursor: "pointer"
          }}>Cancel</button>
          <button
            onClick={() => selectedFile && onUpload(selectedFile)}
            disabled={!selectedFile || uploading}
            style={{
              flex: 1, padding: "9px 0", border: "none", borderRadius: 8,
              background: selectedFile && !uploading ? "#18181b" : "#e5e7eb",
              color: selectedFile && !uploading ? "#fff" : "#98a2b3",
              fontSize: 13, fontWeight: 600, cursor: selectedFile ? "pointer" : "not-allowed"
            }}
          >
            {uploading ? "Analysing..." : "Run Quality Check"}
          </button>
        </div>
      </div>
    </div>
  );
}
```

---

## INSTRUCTIONS FOR CLAUDE IN VS CODE

After creating all files above, run these commands in order:

```bash
# 1. Copy env file
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# 2. Start PostgreSQL with Docker
docker-compose up -d postgres

# 3. Install Python dependencies
cd backend
pip install -r ../requirements.txt

# 4. Run migrations
psql -U postgres -d qualitydb -f ../migrations/001_create_quality_runs.sql
psql -U postgres -d qualitydb -f ../migrations/002_create_anomalies.sql
psql -U postgres -d qualitydb -f ../migrations/003_create_column_profiles.sql

# 5. Start backend
uvicorn main:app --reload --port 8000

# 6. In a new terminal — install and start frontend
cd frontend
npm install
npm run dev

# 7. Open browser at http://localhost:5173
# Upload any CSV file and watch the magic happen
```

### What Claude in VS Code should also create:
- `frontend/src/components/Sidebar.jsx` — list of past runs
- `frontend/src/components/Topbar.jsx` — search bar, upload button, avatar
- `frontend/src/components/KpiCards.jsx` — 4 metric cards at top
- `frontend/src/components/HealthScore.jsx` — circular score gauge
- `frontend/src/components/TrendChart.jsx` — bar chart of score history
- `frontend/src/components/AnomalyTable.jsx` — table of anomalies with AI explanation
- `frontend/src/components/AiInsightCard.jsx` — highlighted AI card for top anomaly
- `frontend/src/components/ColumnQuality.jsx` — column health bars

**Design reference:** Build the frontend to match the Shopeers-style dashboard:
- White cards, light gray background (#f0f2f5)
- Blue gradient accent (#3b82f6 → #6366f1)
- Inter font, JetBrains Mono for data values
- Severity colors: red=#ef4444, amber=#f59e0b, green=#22c55e, blue=#3b82f6
- Recharts for all charts

---

## Project Summary (for your portfolio)

> "I built an end-to-end AI data quality platform. Users upload any CSV — the system automatically profiles every column, detects anomalies using Z-score, IQR, and Isolation Forest, then sends each anomaly to Claude AI which returns a plain English explanation, root cause, business impact, and a fix with actual code. Everything is orchestrated by Apache Airflow, stored in PostgreSQL, and visualized in a React dashboard with a live health score. It's modeled after how enterprise tools like Monte Carlo Data work internally."