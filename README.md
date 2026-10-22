# Omnichannel Marketing ROI & Attribution Engine
> **Enterprise Modern Data Stack Prototype for GlobalRetail Co. ($40M Annual Acquisition Spend)**

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![dbt BigQuery](https://img.shields.io/badge/dbt-1.8+-orange.svg)](https://www.getdbt.com/)
[![Airflow 2.9](https://img.shields.io/badge/Airflow-2.9.2-teal.svg)](https://airflow.apache.org/)
[![Google BigQuery](https://img.shields.io/badge/Warehouse-Google%20BigQuery-4285F4.svg)](https://cloud.google.com/bigquery)

---

## 1. Executive Summary & Consulting Scenario

**GlobalRetail Co.** is an omnichannel consumer enterprise deploying **$40M annually** in customer acquisition across Google Ads, Meta, TikTok, and Programmatic Display.

### The Business Challenge
- **Fragmented Data Silos:** Ad spend, impressions, and clicks reside in self-reporting ad platforms; customer transactions, COGS, discounts, returns, and payment fees live in ERP / Shopify.
- **The Platform ROAS Illusion:** Platform-reported ROAS is revenue-based and self-attributed. Certain high-spending campaigns (e.g. `Meta_Prospecting_BroadDeal`) boast platform ROAS of **~4.0x**, giving marketing leadership a false signal of efficiency.
- **The Planted Margin Leak:** When accounting for heavily discounted product selections, high return rates (25%+), payment processing fees (2.9%), shipping costs, and unit COGS, these campaigns actually generate a **negative contribution margin (CM-ROAS < 1.0)**.
- **The Solution:** A modern, reproducible analytics engine that unifies ad spend and financial transactions, applies multi-touch attribution (Last-Click, Linear, Position-Based 40/20/40, Time-Decay), and computes true **Contribution Margin ROAS (CM-ROAS)** and **Blended CAC** across three executive dashboards (CFO, CMO, CSO).

---

## 2. High-Level Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│ 1. Data Ingestion & Lake Landing (GCS)                     │
│    Synthetic Generator (Seed=42, $40M Spend)                │
│    Date-Partitioned Parquet/CSV in gs://.../raw/           │
└──────────────────────────────┬──────────────────────────────┘
                               │ [Airflow: ingest_daily DAG]
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Cloud Data Warehouse (Google BigQuery)                   │
│    • raw: raw_ad_spend, raw_orders, raw_returns, etc.       │
└──────────────────────────────┬──────────────────────────────┘
                               │ [Airflow: dbt_build_daily DAG]
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Transformation & Testing (dbt Core)                      │
│    • staging (stg_*): Deduplication, casting, UTC normalization │
│    • intermediate (int_*): Per-order margins, attribution models│
│    • marts (mart_*): Unit economics, channel performance, leaks │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Executive Business Intelligence (Looker Studio)          │
│    • CFO: Unit Economics & Margin Waterfall                 │
│    • CMO: Channel Performance & CM-ROAS vs Platform ROAS    │
│    • CSO: Customer Cohort Retention & Lifetime Value        │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Quickstart & Reproducibility

### Prerequisites
- Python 3.11 or 3.12
- Docker & Docker Compose
- Google Cloud Platform account with BigQuery & Cloud Storage enabled (or local sandbox)

### One-Command Setup
```bash
# 1. Clone & setup environment
git clone <repo-url>
cd automation

# 2. Set up virtualenv and install dependencies
make setup

# 3. Configure credentials
cp .env.example .env
# Edit .env with your GCP project ID and Service Account key path

# 4. Generate 24 months of synthetic data ($40M spend, Seed=42)
make generate

# 5. Run tests
make test
```

### Full Pipeline Commands
| Command | Action |
|---|---|
| `make setup` | Provisions directories, `.env`, virtualenv, and installs dependencies |
| `make generate` | Generates 24 months of synthetic raw data (`Seed=42`) |
| `make test` | Executes unit tests, sanity checks, and dbt test suites |
| `make ingest-gcs` | Uploads date-partitioned raw datasets to GCS bucket |
| `make ingest-bq` | Loads raw datasets into BigQuery `raw` dataset |
| `make dbt-deps` | Installs dbt package dependencies |
| `make dbt-build` | Executes all dbt models and schema tests |
| `make dbt-docs` | Builds dbt documentation and dependency DAG |
| `make run` | Runs full automated pipeline (generate -> ingest -> dbt) |
| `make airflow-up` | Launches local Airflow orchestrator (Webserver & Scheduler) |
| `make airflow-down`| Stops Airflow services |

---

## 4. Implementation Status

| Phase | Description | Status |
|---|---|---|
| **Phase 1** | Foundations & Scaffolding (Makefile, Docker, Env, Structure) | **Completed** |
| **Phase 2** | Synthetic Data Generator (Seed=42, Planted Leak) & Ingestion | **Completed** |
| **Phase 3** | dbt Staging Layer, Sources, Freshness & Schema Tests | Pending |
| **Phase 4** | Intermediate Layer (CM Calculation & 4 Attribution Models) | Pending |
| **Phase 5** | Consumption Marts & Margin Leak Analysis | Pending |
| **Phase 6** | Airflow Orchestration & Backfill DAGs | Pending |
| **Phase 7** | Looker Studio Dashboards & Field Specs | Pending |
| **Phase 8** | Consulting Pitch Folder (Deck, SOW, Architecture) | Pending |

---

## 5. Planted Data Patterns & Validation

- **Meta Prospecting BroadDeal:** Platform ROAS ~4.0x, but negative Contribution Margin ROAS (< 1.0) due to low margin SKUs, high return rates (~25%), and fees.
- **TikTok Top-of-Funnel:** Undervalued on Last-Click, rewarded on Multi-Touch (Position-Based / Linear).
- **Google Brand Search:** Artificially elevated Last-Click ROAS, largely cannibalizing organic traffic.
- **Attribution Credit Invariance:** Credit per converted order strictly sums to **1.0** across all models.
