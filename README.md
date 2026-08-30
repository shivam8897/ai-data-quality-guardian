# 🛡️ AI Data Quality Guardian

An AI-powered data quality monitoring platform. Upload any CSV and the system will:

1. Profile the data (nulls, duplicates, schema drift, outliers)
2. Detect anomalies using statistical + ML methods (Z-score, Isolation Forest)
3. Send anomaly context to Claude → get a plain-English explanation, root cause,
   business impact, and a concrete fix
4. Store results in PostgreSQL
5. Show everything on a React dashboard (health score, anomaly table, column quality)

## Prerequisites
- Docker + Docker Compose, **or** Python 3.11+ and Node 20+ for a manual run
- An Anthropic API key

## Quick start (Docker)

```bash
cp .env.example .env
# edit .env and set ANTHROPIC_API_KEY

docker-compose up --build
```

- Backend: http://localhost:8000
- Frontend: http://localhost:5173
- Airflow: http://localhost:8080

## Manual setup

```bash
# 1. Copy env file
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# 2. Start PostgreSQL with Docker
docker-compose up -d postgres

# 3. Install Python dependencies
cd backend
pip install -r ../requirements.txt

# 4. Migrations run automatically on backend startup (backend/database.py),
#    or apply them manually:
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

## Connecting a database table instead of a CSV

Use the "Connect DB" button in the dashboard, or call the API directly:

```bash
curl -X POST http://localhost:8000/api/connect \
  -H "Content-Type: application/json" \
  -d '{
        "connection_string": "postgresql://user:pass@host:5432/dbname",
        "table_name": "orders",
        "sample_rows": 100000
      }'
```

The connection string is used only to fetch the table and is never persisted.

## Running backend tests

```bash
cd backend
pip install -r ../requirements-dev.txt
pytest tests/ -v
```

## Project structure

```
ai_data_quality/
├── backend/
│   ├── main.py                 FastAPI app + /api/upload, /api/runs
│   ├── database.py             DB connection + migration runner
│   ├── models.py                SQLAlchemy models
│   ├── profiler/                CSV + SQL table profiling
│   ├── anomaly/                 Anomaly detection + health scoring
│   ├── ai_engine/                Claude prompt building + API calls
│   └── airflow/dags/            Scheduled quality-check DAG
├── frontend/
│   └── src/components/          Dashboard UI (Recharts + Tailwind)
├── migrations/                  Raw SQL schema
└── docker/                      Postgres multi-db init script
```

## Configuration notes

- `ANTHROPIC_MODEL` (optional env var) overrides the Claude model id used in
  `backend/ai_engine/explainer.py` — defaults to `claude-sonnet-4-6`. Set it to a
  model your API key has access to if that default isn't available.
- The Postgres container creates both the `qualitydb` and `airflow` databases on
  first start via `docker/init-multiple-dbs.sh`.
- `ALERT_WEBHOOK_URL` (optional env var) — if set, the Airflow DAG posts a JSON
  `{"text": "..."}` payload (Slack-incoming-webhook-compatible) here whenever a
  scheduled run's health score drops below 70. Without it, alerts are logged only.
