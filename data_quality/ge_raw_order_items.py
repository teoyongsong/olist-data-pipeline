"""
Data quality checks on raw_olist.order_items.
Run after ingestion. Requires: pip install great_expectations sqlalchemy psycopg2-binary pandas
Set POSTGRES_* env vars or .env (see config in project root).
"""
import os
import sys

import pandas as pd
from sqlalchemy import create_engine

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_connection_string


def run_checks_pandas(df: pd.DataFrame) -> bool:
    """Simple pandas-based checks (no GE dependency)."""
    ok = True
    for col in ["order_id", "order_item_id", "product_id", "seller_id"]:
        if df[col].isna().any():
            print(f"FAIL: {col} has nulls")
            ok = False
    if (df["price"] < 0).any():
        print("FAIL: price has negative values")
        ok = False
    if (df["freight_value"] < 0).any():
        print("FAIL: freight_value has negative values")
        ok = False
    return ok


def main():
    engine = create_engine(get_connection_string())
    df = pd.read_sql("SELECT * FROM raw_olist.order_items", engine)

    if df.empty:
        print("raw_olist.order_items is empty. Run ingestion first.")
        sys.exit(1)

    # Option 1: Great Expectations (if you want full GE reports)
    use_ge = os.environ.get("USE_GREAT_EXPECTATIONS", "0").strip().lower() in ("1", "true", "yes")
    if use_ge:
        try:
            import great_expectations as gx
            from great_expectations.core.batch import RuntimeBatchRequest

            context = gx.get_context()
            datasource = context.sources.add_pandas(name="pandas_ds")
            asset = datasource.add_dataframe_asset(name="order_items")
            batch_request = asset.build_batch_request(dataframe=df)
            suite_name = "raw_order_items_quality"
            try:
                suite = context.suites.get(suite_name)
            except Exception:
                suite = context.suites.add(expectation_suite_name=suite_name)

            validator = context.get_validator(
                batch_request=batch_request,
                expectation_suite=suite,
            )
            validator.expect_column_values_to_not_be_null("order_id")
            validator.expect_column_values_to_not_be_null("order_item_id")
            validator.expect_column_values_to_not_be_null("product_id")
            validator.expect_column_values_to_not_be_null("seller_id")
            validator.expect_column_values_to_be_between("price", min_value=0)
            validator.expect_column_values_to_be_between("freight_value", min_value=0)
            validator.save_expectation_suite()
            results = validator.validate()
            print(results)
            if not results["success"]:
                sys.exit(1)
        except Exception as e:
            print("Great Expectations run failed, falling back to pandas checks:", e)
            if not run_checks_pandas(df):
                sys.exit(1)
    else:
        if not run_checks_pandas(df):
            sys.exit(1)

    print("Data quality checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
