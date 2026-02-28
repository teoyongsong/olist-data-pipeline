# Pipeline Orchestration

Recommendations for orchestrating the full pipeline and scheduling regular ELT and data-quality runs.

---

## Pipeline Steps to Orchestrate

| Step | Command / Action |
|------|------------------|
| 1. Ingest | `python ingestion/ingest_raw_olist.py` |
| 2. dbt deps | `cd dbt_olist && dbt deps && cd ..` |
| 3. ELT (dbt run) | `cd dbt_olist && dbt run && cd ..` |
| 4. dbt tests | `cd dbt_olist && dbt test && cd ..` |
| 5. Data quality | `python data_quality/ge_raw_order_items.py` |

Or run the sequence in one go: `python orchestration/flow.py` (works with or without Prefect).

---

## Orchestration Options Compared

| Option | Pros | Cons | Best for |
|--------|------|------|----------|
| **Cron** | Simple, no extra stack, works on any server | No UI, limited retries/alerting, manual logging | Single server, low complexity |
| **GitHub Actions** | Free for repos, versioned in repo, CI/CD | Not ideal for long-running jobs; 6h limit; needs secrets | Trigger on push/schedule; lightweight CI |
| **Airflow** | DAGs, retries, UI, rich ecosystem | Self-hosted setup and ops | Teams that need visibility and control |
| **Google Cloud Composer** | Managed Airflow, GCP integration | Cost, GCP lock-in | GCP shops, production at scale |

---

## Recommendation by Scenario

### 1. **Start simple: Cron (recommended for this project initially)**

- **Use when:** You run the pipeline on one machine (e.g. dev laptop, single VM, or small server).
- **Schedule:** Daily or weekly (e.g. `0 2 * * *` for 2 AM).
- **Technology:** Built into Linux/macOS; Task Scheduler on Windows.

**Example (Linux/macOS):**

```bash
# Edit crontab: crontab -e
# Run pipeline daily at 2 AM (set PATH and load .env first)
0 2 * * * cd /path/to/olist-data-pipeline && . .env 2>/dev/null; export $(grep -v '^#' .env | xargs) && python orchestration/flow.py >> logs/pipeline.log 2>&1
```

Use a wrapper script so env and paths are correct (see `orchestration/run_pipeline.sh` below).

---

### 2. **CI/CD and scheduled runs: GitHub Actions**

- **Use when:** You want scheduled runs and/or “run on git push” without maintaining a server.
- **Technology:** GitHub Actions with `workflow_dispatch` and `schedule`.

**Use for:**
- Scheduled ELT + data quality (e.g. nightly).
- Running the pipeline on push to `main` (optional).

**Limitations:** Job timeout (6 hours default), secrets for DB and paths; runner has to have Python, dbt, and DB access (or use a self-hosted runner near your DB).

---

### 3. **Production and visibility: Airflow**

- **Use when:** You need a DAG UI, retries, backfills, and multiple pipelines.
- **Technology:** Self-hosted Airflow (Docker/dedicated server) or managed (e.g. Cloud Composer).

**Use for:**
- Clear dependency graph: ingest → dbt run → dbt test → data quality.
- Retries, alerts, and logs in one place.
- Adding more DAGs later (e.g. other sources).

---

### 4. **Managed Airflow on GCP: Google Cloud Composer**

- **Use when:** You are on GCP and want managed Airflow without hosting it yourself.
- **Technology:** Cloud Composer (managed Airflow).

**Use for:** Same as Airflow, with less ops and GCP-native integration (e.g. BigQuery, GCS, Cloud SQL).

---

## Suggested Path for This Repo

1. **Short term:** Use **cron** (or Task Scheduler) + `orchestration/flow.py` to schedule daily/weekly runs. Add a small wrapper script and log directory.
2. **Next:** Add a **GitHub Actions** workflow for scheduled runs (and optionally on push) so pipeline definition lives in the repo.
3. **If you outgrow that:** Move to **Airflow** or **Cloud Composer** and keep the same steps (ingest → dbt → data quality), calling the same commands from tasks.

---

## Quick Start: Cron + Wrapper Script

Below is a wrapper you can run from cron so env and paths are correct.

**File: `orchestration/run_pipeline.sh`** (create this; see next section for contents)

- Loads `.env` from the project root.
- Runs `python orchestration/flow.py`.
- Writes logs to `logs/pipeline.log`.

Cron example (run daily at 2 AM):

```cron
0 2 * * * /path/to/olist-data-pipeline/orchestration/run_pipeline.sh
```

---

## Quick Start: GitHub Actions (Scheduled)

A workflow file can trigger the same pipeline on a schedule (e.g. nightly) and optionally on `workflow_dispatch`. It would:

- Check out the repo.
- Set up Python and install dependencies (+ dbt-postgres).
- Load `POSTGRES_*` and `DATA_DIR` from GitHub secrets.
- Run `python orchestration/flow.py`.

Place the workflow under `.github/workflows/` (e.g. `run-pipeline.yml`). Configure secrets in the repo settings.

**Note:** For GitHub Actions to run the pipeline, the runner must reach your PostgreSQL instance (e.g. use a public IP, VPN, or self-hosted runner near the DB). `DATA_DIR` must point to a path that has the Olist CSVs (e.g. mount or download in the job). For a DB on your laptop or private network, cron or a self-hosted runner is usually simpler.

---

## Run orchestration on GCP (no GitHub / no local cron)

These options run and schedule the pipeline entirely on Google Cloud.

### Option A: Google Cloud Composer (managed Airflow)

1. **Create a Composer environment** (Airflow on GCP):
   ```bash
   gcloud composer environments create olist-pipeline \
     --location us-central1 \
     --image-version composer-2-latest
   ```
2. **Upload a DAG** that runs your pipeline steps (ingest → dbt run → dbt test → data quality). Each step can be a `BashOperator` that runs your Python/dbt commands, or a custom operator. Store the repo (or a zip) in a GCS bucket and point Composer at it, or use a DAG that clones the repo and runs `python orchestration/flow.py`.
3. **Set Airflow variables** for `POSTGRES_*` and `DATA_DIR` (or use Secret Manager and read in the DAG).
4. **Schedule** the DAG in the Airflow UI (e.g. daily); Composer runs it on that schedule.

**Result:** Managed Airflow in GCP; DAG UI, retries, and logs; no GitHub or local machine involved.

---

### Option B: Cloud Run Job + Cloud Scheduler

1. **Containerize** the pipeline (Dockerfile that installs Python, dbt-postgres, runs `python orchestration/flow.py`). Data and DB must be reachable from the container (e.g. Cloud SQL, GCS for CSVs).
2. **Create a Cloud Run job** that runs this image. Configure env vars or Secret Manager for `POSTGRES_*` and `DATA_DIR`.
3. **Create a Cloud Scheduler job** that triggers the Cloud Run job on a schedule (e.g. `0 2 * * *` for daily 2 AM).

**Result:** Serverless, scheduled runs on GCP; no Airflow UI, no GitHub.

---

### Option C: Compute Engine VM + cron

1. **Create a GCE VM** (e.g. e2-small), attach a disk if needed.
2. **Clone the repo** and install Python, dbt-postgres, dependencies. Put Olist CSVs in `DATA_DIR` (or mount a GCS bucket). Use Cloud SQL or a Postgres instance the VM can reach.
3. **Set up cron** on the VM the same way as local cron:
   ```bash
   0 2 * * * /home/ubuntu/olist-data-pipeline/orchestration/run_pipeline.sh
   ```

**Result:** Same as “cron on a server,” but the server is on GCP; no GitHub, no Composer.
