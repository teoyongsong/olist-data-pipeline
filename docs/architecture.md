# Pipeline Architecture & Design Choices

## High-Level Architecture

1. **Source**: Olist Brazilian E-Commerce CSVs (Kaggle).
2. **Ingestion**: Python script (pandas + SQLAlchemy) loads CSVs into PostgreSQL schema `raw_olist`.
3. **ELT**: dbt builds staging views (`stg_olist`) and mart tables (`dw`: dimensions + `fact_order_items`).
4. **Data quality**: dbt tests (schema + relationships) and a data-quality script (pandas + optional Great Expectations) on raw/staging.
5. **Consumption**: Jupyter notebooks (and optionally BI tools) query the `dw` star schema via SQLAlchemy.

You can illustrate this in Draw.io or Excalidraw as: **Source → Ingest → Raw → dbt (Staging → Marts) → Quality → Analysis/BI**.

## Why PostgreSQL

- **Familiar and robust**: Standard SQL, ACID, good for teaching and production-like setups.
- **Ecosystem**: Works with dbt, SQLAlchemy, Great Expectations, and BI tools without extra adapters.
- **Portability**: Same pipeline pattern can be run against a cloud Postgres (e.g. RDS, Cloud SQL) or migrated to BigQuery/Snowflake by changing dbt profile and dialect.

## Why dbt

- **Version-controlled transforms**: All staging and mart logic in SQL under Git.
- **Documentation and testing**: `schema.yml` documents models and declares tests (uniqueness, nulls, FKs).
- **Incremental and scaling**: Easy to add incremental models later if data volume grows.
- **Clear layering**: Staging (clean raw) → marts (business-ready star schema) keeps responsibilities clear.

## Why Star Schema (dw)

- **Query efficiency**: Most analytics (revenue by month, by category, by customer segment) need one fact table and a few dimension lookups — minimal joins and simple aggregations.
- **Business alignment**: Grain (one row per order item) matches how the business thinks about “sales” and supports KPIs (revenue, units, late delivery, first-time vs repeat).
- **Extensibility**: New attributes (e.g. customer region, product brand) go into dimensions without changing historical fact rows.

## Why This Data Quality Setup

- **dbt tests**: Fast, versioned, and run with `dbt test` after every `dbt run` — catch integrity and basic schema issues in the warehouse layer.
- **Script (pandas + optional GE)**: Validates raw data (e.g. non-null keys, non-negative amounts) so bad data is caught early. Pandas fallback keeps the script runnable even without GE installed; setting `USE_GREAT_EXPECTATIONS=1` enables full GE reporting.

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Raw data missing or malformed | Ingestion script validates file presence; data quality script checks key columns and value ranges. |
| dbt run fails (e.g. missing refs) | Run in order: staging first, then dims, then fact; use `dbt run` and fix compilation errors. |
| Postgres down or out of capacity | Use connection pooling and monitor; plan migration to managed Postgres or cloud warehouse if needed. |
| Stale or incomplete Olist data | Document dataset scope and refresh process; consider scheduled re-ingestion (e.g. cron or Prefect). |

## Optional Orchestration

`orchestration/flow.py` runs: ingest → dbt run → dbt test → data quality. This can be executed manually, via cron, or with Prefect for scheduling and observability. For production, you could move to Airflow/Composer or a CI job (e.g. GitHub Actions) that runs the same steps on a schedule.
