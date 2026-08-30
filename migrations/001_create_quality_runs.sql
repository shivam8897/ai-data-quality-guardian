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
