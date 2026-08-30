# AI Data Quality Guardian

An AI-powered data quality monitoring platform. Users upload a CSV (or connect a
database table). The system profiles the data, detects anomalies with statistical
and ML methods, sends anomaly context to Claude for a plain-English explanation and
fix, stores results in PostgreSQL, and renders everything on a React dashboard.

## Tech stack
- **Backend:** Python, FastAPI, Apache Airflow
- **Profiling/Detection:** pandas, scipy, scikit-learn
- **AI Engine:** Anthropic Claude API
- **Database:** PostgreSQL (SQLAlchemy)
- **Frontend:** React + Vite + Tailwind CSS + Recharts
- **Infrastructure:** Docker + Docker Compose

## Layout
- `backend/` — FastAPI app, profiler, anomaly detector, Claude integration, Airflow DAG
- `frontend/` — React dashboard (Vite + Tailwind + Recharts)
- `migrations/` — raw SQL schema, applied automatically on backend startup
- `docker/` — Postgres multi-database init script

## Local setup
See `README.md` for step-by-step run instructions.

## Notes for future changes
- `backend/ai_engine/explainer.py` reads the Claude model id from the
  `ANTHROPIC_MODEL` env var (defaults to `claude-sonnet-4-6`). Confirm this is a
  model your API key can access before relying on AI explanations — if not, set
  `ANTHROPIC_MODEL` in `.env` to a model you have access to.
- The `postgres` service creates both `qualitydb` and `airflow` databases via
  `docker/init-multiple-dbs.sh`, since the official Postgres image only
  auto-creates a single `POSTGRES_DB`.
- `backend/Dockerfile` builds with the repo root as context (see
  `docker-compose.yml`) so it can reach the root `requirements.txt`.
