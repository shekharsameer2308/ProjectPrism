# Changelog

All notable changes to the **Omnichannel Marketing ROI & Attribution Engine** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - 2026-10-22

### Phase 2: Synthetic Data & Lake Ingestion (Completed)
- **Synthetic Data Engine (`data_gen/generate.py`):**
  - Generated 24 months (731 days, 2024-01-01 to 2025-12-31) of data with fixed random seed (`Seed=42`).
  - Total 2-year acquisition spend calibrated to **$82.47M (~$41.2M/year)** across Google Ads, Meta Ads, TikTok Ads, and Programmatic Display.
  - Generated all 7 raw entities: `raw_products` (20 SKUs), `raw_ad_spend` (7,310 rows), `raw_customers` (113,487 rows), `raw_orders` (131,225 rows), `raw_order_items` (221,807 rows), `raw_touchpoints` (194,799 rows), and `raw_returns` (14,972 rows).
  - Planted the revenue leak in `Meta_Prospecting_BroadDeal`: boasts **4.10x platform-reported ROAS**, but drives deep coupons (37.5%), high return rates (18.8%+), carrier shipping, and fees, resulting in **negative contribution margin (-$538K CM, -0.04x CM-ROAS)**.
  - Injected realistic data engineering noise: ~2% duplicate orders and touchpoints; ~1% null campaign IDs for dbt quality testing.
  - Persisted both Parquet and CSV formats to `data/raw/`.
- **Testing (`data_gen/tests/test_generate.py`):**
  - Added Pytest suites asserting non-empty datasets, positive financial prices/COGS/fees, annual spend scale, planted leak behavior, and noise presence. 5/5 tests passing.
- **Verification Script (`data_gen/verify_leak.py`):**
  - Added audit utility printing spend by platform, reported ROAS vs CM-ROAS, and full financial waterfall of the leak campaign.
- **GCS & BigQuery Ingestion (`ingestion/load_to_gcs.py`, `ingestion/load_to_bq.py`):**
  - Implemented partitioned GCS upload logic (`raw/{table}/dt=YYYY-MM-DD/`) and local lake replica (`data/lake_raw/`).
  - Implemented BigQuery load script with date partitioning and clustering specifications per table.

### Phase 1: Foundations (Completed)
- **Scaffolding:** Initialized full directory structure for data generation, ingestion, dbt project, Airflow DAGs, Looker specifications, and executive pitch materials.
- **Environment & Secrets:** Created `.env.example` with standard GCP, BigQuery datasets, and data generation environment parameters. Created comprehensive `.gitignore`.
- **Reproducibility:** Built unified `Makefile` providing `make setup`, `make generate`, `make run`, `make test`, `make lint`, and `make airflow-up`.
- **Orchestration:** Implemented `docker-compose.yml` for local Airflow 2.9 (Postgres, Webserver, Scheduler).
- **Dependencies:** Configured `requirements.txt` for Python 3.11/3.12 with Google Cloud SDKs, dbt-bigquery, Faker, Pandas, PyArrow, and Pytest.
- **Documentation:** Authored baseline `README.md` and initial `docs/kpi_definitions.md`.
