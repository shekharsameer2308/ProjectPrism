"""
data_gen/init_local_db.py
Initializes local analytics database (DuckDB) from data/raw/*.parquet
so dbt can run full builds and tests locally with zero GCP friction.
"""

import os

import duckdb

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "analytics.duckdb")
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")

TABLES = [
    "raw_products",
    "raw_ad_spend",
    "raw_customers",
    "raw_orders",
    "raw_order_items",
    "raw_touchpoints",
    "raw_returns",
]


def init_db():
    print(f"--> Initializing local database at {DB_PATH}...")
    con = duckdb.connect(DB_PATH)
    con.execute("CREATE SCHEMA IF NOT EXISTS raw;")

    for tbl in TABLES:
        parquet_file = os.path.join(RAW_DIR, f"{tbl}.parquet")
        if os.path.exists(parquet_file):
            con.execute(f"CREATE OR REPLACE TABLE raw.{tbl} AS SELECT * FROM read_parquet('{parquet_file}');")
            count = con.execute(f"SELECT COUNT(*) FROM raw.{tbl}").fetchone()[0]
            print(f"    ✓ Loaded raw.{tbl}: {count:,} rows")
        else:
            print(f"    [Warning] Missing {parquet_file}")

    con.close()
    print("==> Local database initialization complete.")


if __name__ == "__main__":
    init_db()
