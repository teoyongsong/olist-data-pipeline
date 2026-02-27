"""
Ingest Olist Brazilian E-Commerce CSV files into PostgreSQL raw_olist schema.
Download dataset from Kaggle: Brazilian E-Commerce Public Dataset by Olist.
Place CSVs in DATA_DIR (default: project/data/olist).
"""
import os
import sys

import pandas as pd
from sqlalchemy import create_engine, text

# Add project root for config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_connection_string, DATA_DIR

RAW_SCHEMA = "raw_olist"

# Map Kaggle CSV filenames to table names (without schema)
TABLE_MAPPING = {
    "olist_customers_dataset.csv": "customers",
    "olist_orders_dataset.csv": "orders",
    "olist_order_items_dataset.csv": "order_items",
    "olist_order_payments_dataset.csv": "order_payments",
    "olist_products_dataset.csv": "products",
    "olist_sellers_dataset.csv": "sellers",
    "olist_geolocation_dataset.csv": "geolocation",
    "olist_order_reviews_dataset.csv": "order_reviews",
}


def main():
    engine = create_engine(get_connection_string())

    if not os.path.isdir(DATA_DIR):
        print(f"DATA_DIR not found: {DATA_DIR}")
        print("Create it and place Olist CSV files there (from Kaggle).")
        sys.exit(1)

    with engine.begin() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {RAW_SCHEMA};"))

    for filename, table in TABLE_MAPPING.items():
        path = os.path.join(DATA_DIR, filename)
        if not os.path.isfile(path):
            print(f"Skip (file not found): {path}")
            continue
        df = pd.read_csv(path)
        full_table = f"{RAW_SCHEMA}.{table}"
        df.to_sql(
            table,
            con=engine,
            schema=RAW_SCHEMA,
            if_exists="replace",
            index=False,
            method="multi",
            chunksize=5000,
        )
        print(f"Loaded {len(df)} rows into {full_table}")

    print("Ingestion complete.")


if __name__ == "__main__":
    main()
