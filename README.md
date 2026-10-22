# Omnichannel Marketing ROI & Attribution Engine
> **Enterprise Modern Data Stack Prototype for GlobalRetail Co. ($40M Annual Acquisition Spend)**

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![dbt BigQuery](https://img.shields.io/badge/dbt-1.8+-orange.svg)](https://www.getdbt.com/)
[![Airflow 2.9](https://img.shields.io/badge/Airflow-2.9.2-teal.svg)](https://airflow.apache.org/)
[![Google BigQuery](https://img.shields.io/badge/Warehouse-Google%20BigQuery-4285F4.svg)](https://cloud.google.com/bigquery)
[![Tests Passing](https://img.shields.io/badge/Tests-152%20Passing-brightgreen.svg)]()

---

## 1. Executive Summary & Consulting Scenario

**GlobalRetail Co.** is an omnichannel consumer enterprise deploying **$40M annually** in customer acquisition across Google Ads, Meta Ads, TikTok Ads, and Programmatic Display.

### The Business Challenge
- **Fragmented Data Silos:** Ad spend, impressions, and clicks reside in self-reporting ad platforms; customer transactions, COGS, discounts, returns, and payment fees live in ERP / Shopify.
- **The Platform ROAS Illusion:** Platform-reported ROAS is revenue-based and self-attributed. Certain high-spending campaigns (e.g. `Meta_Prospecting_BroadDeal`) boast platform ROAS of **~4.10x**, giving marketing leadership a false signal of efficiency.
- **The Planted Margin Leak:** When accounting for heavily discounted product selections (37.5% coupon rate), high return rates (18.8%), carrier shipping costs, merchant payment fees (2.9% + $0.30), and unit COGS, these campaigns actually generate a **negative contribution margin (-0.04x CM-ROAS)**, destroying **$12.98M** in enterprise capital.
- **The Solution:** A modern analytics engine that unifies ad spend and financial transactions, applies multi-touch attribution (Last-Click, Linear, Position-Based 40/20/40, Time-Decay), and computes true **Contribution Margin ROAS (CM-ROAS)** and **Blended CAC** across three executive dashboards (CFO, CMO, CSO).

---

## 2. Modern Data Stack Architecture

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 1. Data Ingestion & Lake Landing (GCS)                                 │
│    Synthetic Generator (Seed=42, $40M/yr Spend Target)                 │
│    Date-Partitioned Parquet/CSV in gs://.../raw/{table}/dt=YYYY-MM-DD/ │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ [Airflow: ingest_daily DAG]
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 2. Cloud Data Warehouse (Google BigQuery)                              │
│    • raw: raw_ad_spend, raw_orders, raw_returns, etc.                  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ [Airflow: dbt_build_daily DAG]
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 3. Transformation & Testing (dbt Core)                                 │
│    • staging (stg_*): Deduplication, casting, UTC normalization        │
│    • intermediate (int_*): Per-order margins, 4 attribution models     │
│    • marts (mart_*): Unit economics, channel performance, leaks        │
│    • Quality Gate: 132 generic schema tests + Singular invariance test │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 4. Executive Business Intelligence (Looker Studio)                     │
│    • CFO: Unit Economics & Cash Margin Waterfall                       │
│    • CMO: Channel Performance & CM-ROAS vs Platform ROAS               │
│    • CSO: Customer Cohort Retention & 12M Lifetime Value (LTV)         │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Quickstart & Reproducibility

### Prerequisites
- Python 3.11 or 3.12 (via `uv` or system Python)
- Docker & Docker Compose
- Google Cloud Platform account (or local DuckDB execution)

### One-Command Setup & Run
```bash
# 1. Clone repository
git clone <repo-url>
cd automation

# 2. Set up virtualenv and install dependencies
make setup

# 3. Generate 24 months of synthetic data ($40M/yr, Seed=42)
make generate

# 4. Run full test suite (pytest + dbt tests)
make test

# 5. Build dbt transformation layers & marts
make dbt-build
```

### Full Pipeline Commands
| Command | Action |
|---|---|
| `make setup` | Provisions directories, `.env`, virtualenv, and installs dependencies |
| `make generate` | Generates 24 months of synthetic raw data (`Seed=42`) |
| `make test` | Executes unit tests, sanity checks, and 132+ dbt tests |
| `make ingest-gcs` | Uploads date-partitioned raw datasets to GCS bucket |
| `make ingest-bq` | Loads raw datasets into BigQuery `raw` dataset |
| `make dbt-deps` | Installs dbt package dependencies (`dbt_utils`, `dbt_expectations`) |
| `make dbt-build` | Executes all dbt models and schema tests |
| `make dbt-docs` | Builds dbt documentation and dependency DAG |
| `make run` | Runs full automated pipeline (generate -> ingest -> dbt) |
| `make airflow-up` | Launches local Airflow orchestrator (Webserver & Scheduler) |
| `make airflow-down`| Stops Airflow services |

---

## 4. Implementation Status (All Phases Completed)

| Phase | Description | Deliverables | Status |
|---|---|---|---|
| **Phase 1** | Foundations & Scaffolding | `Makefile`, `.env.example`, `docker-compose.yml`, repo layout | **Completed** |
| **Phase 2** | Synthetic Data & Ingestion | `data_gen/generate.py` ($82.5M spend, Seed=42), `load_to_gcs.py`, `load_to_bq.py` | **Completed** |
| **Phase 3** | dbt Staging Layer & Tests | 7 `stg_` models, `sources.yml` freshness, deduplication, 62 tests | **Completed** |
| **Phase 4** | Intermediate & Attribution | `int_order_margin`, 4 attribution models, singular credit invariance test | **Completed** |
| **Phase 5** | Consumption Marts & Leaks | 5 `mart_` tables, CM-ROAS rankings, revenue leak isolation | **Completed** |
| **Phase 6** | Airflow Orchestration | `ingest_daily`, `dbt_build_daily`, SLAs, retries, 7-day backfill test | **Completed** |
| **Phase 7** | Looker Studio Dashboards | 3 executive guides, exact chart specs, SQL reconciliation audit | **Completed** |
| **Phase 8** | Consulting Pitch Deliverables | 5-slide deck, 1-page SOW ($250k fee), Mermaid architecture diagram | **Completed** |

---

## 5. Analytical Discoveries & Planted Patterns

### 1. The Flagship Margin Leak (`Meta_Prospecting_BroadDeal`)
- **Platform View:** Cheap CPCs ($0.55), **$51.20M platform revenue**, glowing **4.10x ROAS**.
- **Financial Reality:** High return rates (18.8%), deep coupons (37.5%), clearance items (COGS ratio > 100%), carrier shipping, and fees.
- **True Return:** **-$487K Contribution Margin (-0.04x CM-ROAS)** destroying **$12.98M** in cash.

### 2. The Attribution Shift (Last-Touch vs. Position-Based 40/20/40)
- **TikTok Top-Funnel (`TikTok_Spark_TopFunnel`):** Undervalued under last-touch ($0 credit); rewarded with **+$1.03M** under multi-touch for upstream discovery assists.
- **Google Brand Search (`Google_Search_Brand`):** Overstated under last-touch ($14.79M) by **+$4.76M (+32.2%)** because it merely converts demand captured upstream by social and display.

---

## 6. Pre-Sales Consulting Pitch Deliverables

Located in [`pitch_folder/`](./pitch_folder/):
1. **[Executive Pitch Deck (`pitch_deck.md`)](./pitch_folder/pitch_deck.md):** 5-slide Situation-Complication-Resolution narrative detailing the **+$4.39M** capital reallocation opportunity.
2. **[Statement of Work (`statement_of_work.md`)](./pitch_folder/statement_of_work.md):** 12-week fixed-fee engagement ($250,000 billed 30/40/30) with clear deliverables, assumptions, and acceptance criteria.
3. **[Architecture Diagram (`architecture_diagram.mermaid`)](./pitch_folder/architecture_diagram.mermaid):** End-to-end modern data stack diagram with security and governance callouts.

---

## 7. Consulting Interview Talking Points

1. **Why Contribution Margin instead of Revenue ROAS?**
   - Revenue ROAS treats all sales equally. It fails to account for COGS, shipping, payment gateway fees, and refunds. As demonstrated by `Meta_Prospecting_BroadDeal`, scaling a high-revenue campaign with thin gross margins and heavy returns destroys enterprise value.
2. **Multi-Touch Attribution as a Heuristic:**
   - Multi-touch attribution (MTA) is a rule-based heuristic that assigns fractional credit. While superior to last-touch, it cannot prove incremental causality. In real-world enterprise engagements, MTA should be paired with **Geo-Holdout Testing** and **Marketing Mix Modeling (MMM)** for true incremental validation.
3. **Why dbt Tests and Freshness Matter for Executive Trust:**
   - The singular test `assert_attribution_credit_sums_to_one.sql` mathematically proves that 100% of conversion credit (and neither more nor less) is conserved across all models. Freshness monitors guarantee that executive dashboards never present stale figures to the board.
4. **Transition to Real Client Data:**
   - Replace synthetic generator with production Fivetran/Airbyte connectors, implement customer identity resolution graphs, and hash email PII (SHA256) for privacy compliance.
5. **Cost and Scaling in BigQuery:**
   - Daily partition filters (`_PARTITIONDATE`) and clustering keys (`platform`, `campaign_id`) reduce query scan costs by up to 90%.
