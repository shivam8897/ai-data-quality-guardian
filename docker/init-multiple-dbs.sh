#!/bin/bash
# Creates additional databases on first Postgres container start.
# The official postgres image only auto-creates POSTGRES_DB; this script
# reads a comma-separated POSTGRES_MULTIPLE_DATABASES list and creates the rest.
set -e

if [ -n "$POSTGRES_MULTIPLE_DATABASES" ]; then
  echo "[init] Creating multiple databases: $POSTGRES_MULTIPLE_DATABASES"
  IFS=',' read -ra DBS <<< "$POSTGRES_MULTIPLE_DATABASES"
  for db in "${DBS[@]}"; do
    db_trimmed=$(echo "$db" | xargs)
    echo "[init] Creating database '$db_trimmed' if not exists"
    psql -v ON_ERROR_STOP=0 --username "$POSTGRES_USER" <<-EOSQL
      SELECT 'CREATE DATABASE "$db_trimmed"' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$db_trimmed')\gexec
EOSQL
  done
fi
