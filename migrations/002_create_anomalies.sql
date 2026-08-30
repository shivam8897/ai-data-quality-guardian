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
