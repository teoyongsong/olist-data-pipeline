# Data quality

- **Great Expectations**: `ge_raw_order_items.py` runs expectations on `raw_olist.order_items` (non-null keys, non-negative price/freight). Run after ingestion.
- **dbt tests**: In `dbt_olist/models/marts/schema.yml` (uniqueness, not null, referential integrity). Run with `dbt test` after `dbt run`.
