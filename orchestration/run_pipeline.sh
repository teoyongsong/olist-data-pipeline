#!/usr/bin/env bash
# Wrapper for cron (or manual) runs of the full pipeline.
# Usage: ./orchestration/run_pipeline.sh
# Cron example (daily 2 AM): 0 2 * * * /path/to/olist-data-pipeline/orchestration/run_pipeline.sh

set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# Load .env if present (export POSTGRES_*, DATA_DIR, etc.)
if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

# Optional: ensure logs dir exists
mkdir -p logs

# Run pipeline (ingest -> dbt run -> dbt test -> data quality)
exec python orchestration/flow.py >> logs/pipeline.log 2>&1
