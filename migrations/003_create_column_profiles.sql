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
