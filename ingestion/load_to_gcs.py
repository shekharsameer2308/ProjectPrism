"""
ingestion/load_to_gcs.py
Uploads raw marketing and transactional datasets to Google Cloud Storage (GCS)
using date-partitioned paths: gs://<bucket>/raw/<table_name>/dt=YYYY-MM-DD/
"""

import os

import pandas as pd
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

GCP_PROJECT = os.getenv("GCP_PROJECT_ID", "globalretail-analytics-prod")
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "globalretail-marketing-lake-raw")
CREDS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
LOCAL_LAKE_DIR = os.path.join(BASE_DIR, "data", "lake_raw")

# Mapping of tables to their partition date column
DATE_COLUMNS = {
    "raw_ad_spend": "date",
    "raw_orders": "order_ts",
    "raw_returns": "return_ts",
    "raw_touchpoints": "touch_ts",
    "raw_customers": "first_order_date",
}


def get_gcs_client():
    """Initializes Google Cloud Storage client if credentials exist."""
    if CREDS_PATH and os.path.exists(CREDS_PATH):
        try:
            from google.cloud import storage
            client = storage.Client.from_service_account_json(CREDS_PATH, project=GCP_PROJECT)
            print(f"--> [GCS] Authenticated via service account key: {CREDS_PATH}")
            return client
        except Exception as e:  # noqa: BLE001
            print(f"--> [GCS] Notice: Unable to authenticate with GCP ({e}). Falling back to local lake mode.")
            return None
    return None


def upload_table_to_gcs(table_name: str, client=None, bucket_name: str = GCS_BUCKET_NAME):
    """
    Partitions a raw parquet table by date and uploads to GCS:
    gs://<bucket_name>/raw/<table_name>/dt=YYYY-MM-DD/<table_name>.parquet
    Also maintains a local partitioned lake replica under data/lake_raw/.
    """
    parquet_path = os.path.join(RAW_DATA_DIR, f"{table_name}.parquet")
    if not os.path.exists(parquet_path):
        csv_path = os.path.join(RAW_DATA_DIR, f"{table_name}.csv")
        if not os.path.exists(csv_path):
            print(f"--> [GCS] Skipping {table_name}: source file not found in {RAW_DATA_DIR}")
            return
        df = pd.read_csv(csv_path)
    else:
        df = pd.read_parquet(parquet_path)

    date_col = DATE_COLUMNS.get(table_name)
    os.makedirs(LOCAL_LAKE_DIR, exist_ok=True)

    if date_col and date_col in df.columns:
        # Extract date string YYYY-MM-DD
        dt_series = pd.to_datetime(df[date_col], errors="coerce").dt.strftime("%Y-%m-%d")
        unique_dates = dt_series.dropna().unique()
        print(f"--> [GCS] Ingesting {table_name} ({len(df):,} rows) across {len(unique_dates):,} daily partitions...")

        # Sample upload / batch partition
        uploaded_partitions = 0
        for dt_val in sorted(unique_dates):
            part_df = df[dt_series == dt_val]
            part_filename = f"{table_name}.parquet"
            gcs_blob_path = f"raw/{table_name}/dt={dt_val}/{part_filename}"

            # Save locally to partitioned lake structure
            local_part_dir = os.path.join(LOCAL_LAKE_DIR, table_name, f"dt={dt_val}")
            os.makedirs(local_part_dir, exist_ok=True)
            local_part_file = os.path.join(local_part_dir, part_filename)
            part_df.to_parquet(local_part_file, index=False)

            if client:
                try:
                    bucket = client.bucket(bucket_name)
                    blob = bucket.blob(gcs_blob_path)
                    blob.upload_from_filename(local_part_file)
                except Exception as upload_err:  # noqa: BLE001
                    print(f"    [Warning] Failed GCS upload for {gcs_blob_path}: {upload_err}")
            uploaded_partitions += 1

        print(f"    ✓ {table_name}: {uploaded_partitions:,} date partitions prepared (path: raw/{table_name}/dt=YYYY-MM-DD/)")

    else:
        # Non-date-partitioned static dimension (e.g. raw_products)
        gcs_blob_path = f"raw/{table_name}/current/{table_name}.parquet"
        local_static_dir = os.path.join(LOCAL_LAKE_DIR, table_name, "current")
        os.makedirs(local_static_dir, exist_ok=True)
        local_static_file = os.path.join(local_static_dir, f"{table_name}.parquet")
        df.to_parquet(local_static_file, index=False)

        if client:
            try:
                bucket = client.bucket(bucket_name)
                blob = bucket.blob(gcs_blob_path)
                blob.upload_from_filename(local_static_file)
            except Exception as upload_err:  # noqa: BLE001
                print(f"    [Warning] Failed GCS upload for {gcs_blob_path}: {upload_err}")

        print(f"    ✓ {table_name}: static snapshot stored (path: {gcs_blob_path})")


def run_gcs_ingestion():
    client = get_gcs_client()
    tables = [
        "raw_products",
        "raw_ad_spend",
        "raw_customers",
        "raw_orders",
        "raw_order_items",
        "raw_touchpoints",
        "raw_returns",
    ]
    print("==========================================================================")
    print(f"GCS Landing Lake Ingestion: Target Bucket = gs://{GCS_BUCKET_NAME}")
    print("==========================================================================")
    for table in tables:
        upload_table_to_gcs(table, client=client)
    print("==> GCS Lake ingestion completed.")


if __name__ == "__main__":
    run_gcs_ingestion()
