# Changelog

All notable changes to the **Omnichannel Marketing ROI & Attribution Engine** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - 2026-10-22

### Phase 6: Airflow Orchestration & Backfill Resilience (Completed)
- **Daily Ingestion DAG (`airflow/dags/ingest_daily.py`):**
  - Scheduled daily at `02:00 UTC` (`0 2 * * *`).
  - Tasks: `extract_daily_partition` $\to$ `upload_to_gcs_partition` $\to$ `load_to_bigquery_partition` $\to$ `verify_ingestion_quality`.
  - Configured 2-hour SLA, exponential backoff retries (2 retries, 5m initial delay), execution timeouts (45m), and failure callback (`notify_pipeline_failure`).
  - Designed for date-partitioned idempotency (`dt={{ ds }}`) with partition overwrite semantics.
- **Daily Transformation DAG (`airflow/dags/dbt_build_daily.py`):**
  - Scheduled daily at `04:00 UTC` (`0 4 * * *`).
  - Tasks: `dbt_source_freshness` $\to$ `dbt_staging_build` $\to$ `dbt_intermediate_build` $\to$ `dbt_marts_build` $\to$ `dbt_singular_tests` $\to$ `dbt_docs_generate`.
  - Configured 1-hour SLA, automated retries, and contextual failure callback (`notify_dbt_failure`).
- **7-Day Backfill & Idempotency Testing (`airflow/test_backfill.py`):**
  - Executed a 7-day backfill test (`2025-01-01` to `2025-01-07`).
  - Verified that duplicate re-runs produce identical row counts across all raw tables with **zero duplicate accumulation**.

### Phase 5: Consumption Marts & Revenue Leak Discovery (Completed)
- **Executive Consumption Marts (`models/marts/mart_*.sql`):**
  - Built all 5 production consumption marts:
    - `mart_unit_economics`: Daily unit economics for the CFO (Blended CAC, Blended CPA, gross margin, shipping margin, net revenue, contribution margin, and true CM-ROAS).
    - `mart_channel_performance`: Campaign-level audit for the CMO contrasting self-reported platform ROAS against true multi-touch CM-ROAS, channel CAC, and CPA with dynamic `model_name` filtering.
    - `mart_customer_retention`: Monthly cohort retention heatmaps (D30, D60, D90) and 12-month cumulative CM LTV curves segmented by first-order acquisition channel for the CSO.
    - `mart_attribution_comparison`: Side-by-side comparison of Last-Touch vs. Linear, Position-Based, and Time-Decay models, isolating over-credited channels (Google Brand Search: -$4.76M / -32.2% under multi-touch) and under-credited top-of-funnel discovery (TikTok Spark TopFunnel: +$1.03M under multi-touch).
    - `mart_campaign_margin_leak`: Flagship consulting model ranking campaigns by CM-ROAS, calculating net margin destruction, and segmenting margin efficiency.
- **Planted Revenue Leak Validated:**
  - `Meta_Prospecting_BroadDeal`:
    - Total Spend: **$12,487,826.46**
    - Platform Reported Revenue: **$51,204,098.24** (**4.10x Platform ROAS** > 3.0)
    - Realized Net Revenue: **$653,794.10**
    - Realized Contribution Margin: **-$487,199.22** (**-0.04x True CM-ROAS** < 1.0)
    - Net Margin Destruction: **$12.98M**
    - Classified as: **`CRITICAL REVENUE LEAK`**
- **Testing & Verification (`models/marts/schema.yml`):**
  - Added surrogate primary keys, not-null constraints, and accepted values tests.
  - Full project dbt build passed: **152 of 152 operations passed (20 models + 132 tests)** with 0 errors and 0 warnings.

### Phase 4: Intermediate Business Logic & Multi-Touch Attribution (Completed)
- **Order Economics (`models/intermediate/int_order_margin.sql`):**
  - Calculated per-order unit economics: Net Revenue (`gross_revenue - discount - refunds`), Total COGS, Shipping Margin (`charged - cost`), Payment Fees, and Contribution Margin (`Net Revenue - COGS - Shipping - Fees`).
- **Customer Lifecycle (`models/intermediate/int_customer_orders.sql`):**
  - Sequenced customer order history with window functions; generated `customer_order_sequence`, `is_first_order`, `is_repeat_order`, and purchase frequency intervals (`days_since_first_order`, `days_since_previous_order`).
- **Attribution Windowing (`models/intermediate/int_touchpoints_windowed.sql`):**
  - Filtered touches within configurable lookback windows: 30-day click and 24-hour impression windows prior to purchase. Handled fallback direct/organic paths. Sequenced touches ascending and descending per order.
- **Attribution Models (4 Methodologies):**
  - `int_attribution_last_click.sql`: Last-touch (100% credit to conversion touch).
  - `int_attribution_linear.sql`: Uniform credit (`1 / N`) across all touches.
  - `int_attribution_position_based.sql`: 40/20/40 U-shaped credit (rewards discovery and conversion equally, with 20% across middle touches).
  - `int_attribution_time_decay.sql`: Exponential decay with a 7-day half-life (`2^(-age/7d)`).
- **Unioned Attributed Revenue (`models/intermediate/int_attributed_revenue.sql`):**
  - Combined all 4 attribution models with `model_name` selector, attributing volume (orders, new customers) and financial economics (net revenue, COGS, contribution margin) by fractional weights.
- **Singular Credit Conservation Test (`tests/assert_attribution_credit_sums_to_one.sql`):**
  - Added strict singular test verifying that attributed credit per order sums to exactly **1.0** across all models.
  - All **99 dbt tests passed** across staging and intermediate layers.

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
