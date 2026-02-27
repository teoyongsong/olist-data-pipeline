# Olist E-Commerce Data Pipeline

End-to-end data pipeline and analysis for the **Brazilian E-Commerce Public Dataset by Olist**: ingestion into PostgreSQL, star-schema ELT with dbt, data quality checks, and Python analysis.

## Architecture Overview

```
[CSV files] --> [Python ingest] --> [PostgreSQL raw_olist]
                                        |
                                        v
[dbt] staging (stg_olist) --> marts (dw: dim_*, fact_order_items)
                                        |
                    +-------------------+-------------------+
                    v                   v                   v
              [dbt test]        [Great Expectations]   [Jupyter / BI]
```

- **Data source**: [Olist Dataset on Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) — download and place CSVs in `data/olist/`.
- **Warehouse**: PostgreSQL (`raw_olist` = raw tables, `stg_olist` = staging views, `dw` = star schema).
- **ELT**: dbt (staging + marts).
- **Quality**: dbt tests (uniqueness, nulls, FKs) + optional Great Expectations on raw tables.
- **Analysis**: Jupyter notebook using SQLAlchemy against `dw`.

## Prerequisites

- Python 3.10+
- PostgreSQL 14+ (running locally or remote)
- [dbt-core](https://docs.getbt.com/docs/get-started/installation) with Postgres adapter (`pip install dbt-postgres` or use project `requirements.txt`)

## Quick Start

### 1. Clone and install

```bash
cd olist-data-pipeline
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
pip install dbt-postgres
```

### 2. Configure environment

Copy `.env.example` to `.env` and set:

- `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB=olist_dw`
- `DATA_DIR` = path to folder containing Olist CSV files (e.g. `./data/olist`)

Create the database:

```sql
CREATE DATABASE olist_dw;
```

For **dbt**, the same variables must be in your environment (e.g. `set POSTGRES_PASSWORD=yourpassword` in Windows before `dbt run`, or use a tool that loads `.env` into the shell).

### 3. Download data

Download the [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) from Kaggle and extract the CSVs into `data/olist/`.

### 4. Run the pipeline

```bash
# Ingest raw CSVs into raw_olist
python ingestion/ingest_raw_olist.py

# Install dbt packages (optional, for extra macros)
cd dbt_olist && dbt deps && cd ..

# Build star schema (staging + marts)
cd dbt_olist && dbt run && dbt test && cd ..

# Data quality on raw table (pandas checks; set USE_GREAT_EXPECTATIONS=1 for full GE)
python data_quality/ge_raw_order_items.py
```

### 5. Analysis

Open `analysis/eda_and_metrics.ipynb` in Jupyter and run all cells (ensure `.env` / config point to your Postgres DB).

### Optional: Run full pipeline (orchestration)

```bash
python orchestration/flow.py
```

With Prefect installed, this runs as a Prefect flow; otherwise it runs the same steps in sequence.

## Project Structure

```
olist-data-pipeline/
├── config.py                 # DB URL and paths from env
├── requirements.txt
├── .env.example
├── ingestion/
│   └── ingest_raw_olist.py   # Load CSVs -> raw_olist
├── dbt_olist/                # dbt project
│   ├── dbt_project.yml
│   ├── profiles.yml          # uses POSTGRES_* env vars
│   ├── models/
│   │   ├── sources.yml
│   │   ├── staging/          # stg_customers, stg_orders, ...
│   │   └── marts/            # dim_customer, dim_product, dim_seller, dim_date, fact_order_items
│   └── packages.yml          # dbt_utils (optional)
├── data_quality/
│   ├── ge_raw_order_items.py # Checks on raw_olist.order_items
│   └── README.md
├── analysis/
│   └── eda_and_metrics.ipynb # Monthly trends, top products, segmentation, late delivery
├── orchestration/
│   └── flow.py               # Optional Prefect/sequential pipeline
└── docs/
    ├── architecture.md       # Design and tool choices
    └── technical_report.md   # Schema justification and findings outline
```

## Star Schema (dw)

| Table             | Type   | Description |
|------------------|--------|-------------|
| `dim_customer`   | Dimension | Customer attributes, CLV, tenure_segment |
| `dim_product`    | Dimension | Product category and attributes |
| `dim_seller`     | Dimension | Seller location |
| `dim_date`       | Dimension | Date spine 2016–2018 |
| `fact_order_items` | Fact  | One row per order item; keys to dims; measures: price, freight_value, total_item_value, is_late_delivery, is_first_order |

## Documentation

- **docs/architecture.md** — Pipeline architecture, tool choices (Postgres, dbt, GE), and scaling notes.
- **docs/technical_report.md** — Schema design justification, testing strategy, and outline for findings/insights report.

## License

Code in this repo is for educational use. Olist dataset is subject to its own license on Kaggle.
