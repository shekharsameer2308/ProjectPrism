# Changelog

All notable changes to the **Omnichannel Marketing ROI & Attribution Engine** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - 2026-10-22

### Phase 3: dbt Staging Layer, Sources & Data Quality (Completed)
- **Sources & Freshness (`models/staging/sources.yml`):**
  - Configured all 7 raw sources with table descriptions, schema specifications, and freshness monitors (`warn_after: 24h`, `error_after: 48h`).
  - Executed `dbt source freshness`; validated that freshness assertions correctly flag historical datasets as expected in pre-production.
- **Staging SQL Models (`models/staging/stg_*.sql`):**
  - Implemented 7 staging models following CTE pattern:
    - `stg_ad_spend`: Deduplicated spend on `(spend_date, platform, campaign_id)`, mapped null campaigns to `'unattributed'`, standardized platform names.
    - `stg_customers`: Deduplicated on `customer_id`, trimmed geographic regions.
    - `stg_orders`: Deduplicated on `order_id` (cleansed ~2% noise), cast timestamps to UTC, normalized financial fields.
    - `stg_order_items`: Generated surrogate key `order_item_id`, computed line-level revenue and COGS.
    - `stg_returns`: Deduplicated refunds on `(order_id, sku)`, normalized UTC timestamps.
    - `stg_touchpoints`: Deduplicated on `touch_id` (cleansed ~2% noise), mapped null campaign IDs to `'unattributed'`.
    - `stg_products`: Deduplicated on `sku`, computed unit gross margin and gross margin rate.
- **Testing & Verification (`models/staging/schema.yml`):**
  - Authored documentation and tests across all staging entities: `unique`, `not_null`, `accepted_values` (`order_status`, `touch_type`, `platform`), and referential integrity `relationships` (`orders -> customers`, `order_items -> orders`, `order_items -> products`, `returns -> orders`, `touchpoints -> customers`).
  - Ran `dbt build --select staging`: **100% pass rate (69/69 resources: 7 models + 62 tests)** with 0 failures and 0 warnings.

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
