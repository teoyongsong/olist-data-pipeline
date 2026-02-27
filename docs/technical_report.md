# Technical Report Outline

Use this outline for your written report (and to support the executive presentation).

## 1. Introduction

- **Objective**: Build an end-to-end data pipeline for Olist e-commerce data: ingestion, warehouse design, ELT, data quality, and analysis.
- **Scope**: Raw CSVs → PostgreSQL → star schema → validated datasets → Python-based metrics and exploratory analysis.

## 2. Technical Approach

### 2.1 Tool Selection

- **PostgreSQL**: Central warehouse; supports standard SQL, dbt, and BI tools.
- **dbt**: ELT and testing; staging and marts as code.
- **Python (pandas, SQLAlchemy)**: Ingestion and analysis; optional Great Expectations for data quality.
- **Rationale**: Balance of simplicity, reproducibility, and alignment with common data-engineering practice.

### 2.2 Data Ingestion

- Script: `ingestion/ingest_raw_olist.py` reads CSVs from a configurable directory and loads them into schema `raw_olist` with one table per source file.
- Design choice: Full refresh (replace) per run; incremental loading can be added later if needed.

### 2.3 Data Warehouse Design (Star Schema)

- **Grain of the fact table**: One row per order item (`order_id` + `order_item_id`).
- **Dimensions**: Customer (with CLV and tenure segment), Product, Seller, Date.
- **Fact**: `fact_order_items` — foreign keys to dimensions, measures (price, freight_value, total_item_value), and flags (is_late_delivery, is_first_order).
- **Justification**: Supports revenue and unit analysis by time, product, customer segment, and seller; keeps queries simple and performant; allows adding new attributes in dimensions without rewriting history.

### 2.4 ELT Pipeline (dbt)

- **Staging**: Clean and cast raw columns (e.g. timestamps, numeric types); no business logic.
- **Marts**: Build `dim_customer`, `dim_product`, `dim_seller`, `dim_date`, and `fact_order_items` from staging and refs.
- **Derived fields**: e.g. `customer_lifetime_value`, `tenure_segment`, `total_item_value`, `is_late_delivery`, `is_first_order`.

### 2.5 Data Quality

- **dbt**: Tests on marts (uniqueness, not null, referential integrity).
- **Custom script**: Checks on raw `order_items` (non-null keys, non-negative price/freight); optional Great Expectations for richer reporting.

## 3. Findings and Insights

Findings below are from the EDA notebook (`analysis/eda_and_metrics.ipynb`) run against the star schema in `dw_dw`.

### 3.1 Monthly sales trends

Revenue and order volume grow strongly over the period. Early months (e.g. Sep 2016 ~R$355, Oct 2016 ~R$57k) are low; by 2017 monthly revenue reaches roughly R$400k–R$586k (e.g. May and July 2017 ~R$585k), with order counts in the thousands and items sold in the thousands per month. The pipeline delivers a clear view of growth and seasonality; the monthly revenue bar chart in the notebook is the main visual for reporting.

### 3.2 Top-selling product categories

Top categories by revenue (from the notebook):

| Rank | Category                 | Revenue (R$)   | Items sold |
|------|--------------------------|----------------|------------|
| 1    | beleza_saude             | ~1,441,248     | 9,670      |
| 2    | relogios_presentes       | ~1,305,542     | 5,991      |
| 3    | cama_mesa_banho          | ~1,241,682     | 11,115     |
| 4    | esporte_lazer            | ~1,156,656     | 8,641      |
| 5    | informatica_acessorios   | ~1,059,272     | 7,827      |

Beleza/saúde and relógios/presentes lead revenue; cama_mesa_banho has the highest item count among the top five. Implications: focus assortment and marketing on these categories; consider margin and inventory depth for high-volume categories like cama_mesa_banho.

### 3.3 Customer segmentation (tenure and CLV)

Customer segmentation by tenure shows one segment dominating in the current data: **Loyal** customers (99,441) with total revenue ~R$15.8M and average revenue per customer ~R$159.33. This indicates that most tracked customers fall in the Loyal segment and drive the bulk of revenue; the notebook’s pie and bar charts by tenure segment support reporting on concentration and average value per customer.

### 3.4 Late delivery rate

Among order items with a delivery date, **6.6%** of items are late (7,265 late vs 102,931 on-time). Late items still generate substantial revenue (~R$1.15M vs ~R$14.27M on-time), so improving on-time delivery can protect revenue and satisfaction without losing the current late-delivery revenue in the long run. The metric is reproducible from `dw_dw.fact_order_items` via the notebook.

## 4. Limitations and Future Work

- Dataset is historical and static; document assumptions and date range.
- Possible extensions: incremental dbt models, more dimensions (e.g. geography), orchestration on a schedule, BI dashboards.

## 5. Conclusion

- Summarize delivered pipeline (ingestion → star schema → quality → analysis).
- Emphasize how the design supports business questions and scales (e.g. adding sources or moving to a cloud warehouse).

---

Use the Jupyter notebook outputs (tables and charts) in this report and in the executive slide deck.
