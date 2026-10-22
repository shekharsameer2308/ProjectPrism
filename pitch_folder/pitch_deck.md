# Omnichannel Marketing ROI & Attribution Engine
## Executive Presentation & Strategic Reallocation Proposal

**Prepared for:** Executive Leadership Team, GlobalRetail Co.  
**Presented by:** Senior Analytics Engineering & Growth Advisory Practice  
**Date:** October 2026  

---

### Slide 1: The Situation — $40M Annual Spend in Platform Silos

#### Context & Business Setting
- **Scale:** GlobalRetail Co. deploys **$40M annually** in acquisition capital across Google Ads, Meta Ads, TikTok Ads, and Programmatic Display.
- **The Data Disconnect:**
  - Ad platforms report clicks, conversions, and self-attributed revenue within their walled gardens.
  - Actual financial truth—product returns, coupon discounts, unit COGS, carrier shipping, and payment gateway fees—lives in ERP and eCommerce order stores.
- **The Core Problem:** Leadership lacks a single source of truth for **Blended Customer Acquisition Cost (CAC)** and **Contribution-Margin ROAS (CM-ROAS)**. Decisions are made on vanity metrics that disguise unprofitable customer acquisition.

```text
       Ad Platform Reported World                    True Enterprise Reality
┌──────────────────────────────────────┐       ┌──────────────────────────────────────┐
│ Gross Ad Revenue:    $142.3M         │  vs   │ Net Cash Realized:     $24.2M        │
│ Reported Blended ROAS:  3.45x        │       │ True CM-ROAS:           0.15x        │
│ "All campaigns look profitable"      │       │ Capital destroyed on discounted SKUs │
└──────────────────────────────────────┘       └──────────────────────────────────────┘
```

---

### Slide 2: The Complication — The $12.98M Margin Leak

#### The Vanity Metric Trap
Marketing leadership scaled **`Meta_Prospecting_BroadDeal`** because Meta Ad Manager reported an attractive **4.10x ROAS** with cheap CPCs ($0.55).

#### The Analytical Truth Behind the Numbers
When joining touchpoints to itemized gross margin, post-purchase returns, and carrier fees:
- **Discounts:** 37.5% average coupon markdown ($470K).
- **Product Returns:** 18.8% return rate on deal buyers ($147K refunded).
- **Unit COGS:** Buyers disproportionately selected low-margin clearance SKUs ($920K COGS).
- **Carrier Shipping:** 100% free shipping offered ($224K absorbed carrier freight).

```text
========================================================================================
CAMPAIGN AUDIT: Meta_Prospecting_BroadDeal (24-Month Total)
========================================================================================
Ad Network Spend:               $12,487,826.46
Platform-Reported Gross Sales:  $51,204,098.24  ──> Reported ROAS: 4.10x (Looks Efficient!)
----------------------------------------------------------------------------------------
Realized Net Revenue:           $   653,794.09
Less: Unit COGS:               -$   919,988.85
Less: Carrier Freight Shipping: -$   223,859.76
Less: Merchant Gateway Fees:    -$    31,703.04
----------------------------------------------------------------------------------------
True Contribution Margin:      -$   487,199.22  ──> True CM-ROAS: -0.04x (NEGATIVE CASH MARGIN)
Net Capital Destroyed:          $12,975,025.68
========================================================================================
```

> **Takeaway:** Every dollar spent on this campaign actively destroys cash margin.

---

### Slide 3: The Resolution — Modern Analytics Architecture & Executive BI

We deployed a modern, production-grade analytics platform that unifies ad spend and transaction logs through an automated pipeline:

#### 1. Unified Cloud Data Pipeline
- **Landing Lake (GCS):** Date-partitioned landing for marketing API extracts and order tables.
- **Transformation Engine (BigQuery + dbt):**
  - **Staging Layer (`stg_`):** Cleanses noise, deduplicates ~2% duplicate records, maps missing campaign IDs, and normalizes timestamps to UTC.
  - **Intermediate Layer (`int_`):** Computes per-order contribution margin and runs 4 multi-touch attribution models (**Last-Touch, Linear, Position-Based 40/20/40, Time-Decay**).
  - **Singular Quality Gate:** Validates that attributed conversion credit per order strictly sums to **1.0000**.
  - **Marts Layer (`mart_`):** Pre-aggregated consumption tables for business intelligence.
- **Orchestration (Airflow):** Automated daily DAGs with 2-hour SLAs, retries, and idempotent backfills.

#### 2. Three Dedicated Executive Dashboards
1. **CFO Dashboard:** Blended CAC, LTV:CAC benchmarking, and complete contribution margin waterfall.
2. **CMO Dashboard:** Side-by-side Platform ROAS vs CM-ROAS, CPA trendlines, and automated campaign leak detection table.
3. **CSO Dashboard:** D30/D60/D90 retention heatmap matrix and 12-month cohort CM LTV curves.

---

### Slide 4: Business Impact — The Capital Reallocation Opportunity

*(Illustrative, derived directly from the simulated enterprise dataset)*

#### Strategic Capital Optimization
By terminating the **`Meta_Prospecting_BroadDeal`** leak and reallocating its **$12.49M** spend toward proven, positive-margin acquisition channels (**Google Brand Search, Google Non-Brand Generic, and Meta Lookalike Prospecting**):

```text
========================================================================================
STRATEGIC REALLOCATION WATERFALL
========================================================================================
1. Reallocated Acquisition Capital:             $12,487,826.46
2. Eliminate Current Margin Loss:              +$   487,199.22
3. Reallocated Yield @ 0.312x Benchmark CM:    +$ 3,901,911.40
----------------------------------------------------------------------------------------
NET INCREMENTAL CONTRIBUTION MARGIN:           +$ 4,389,110.62  (+$4.39M Cash Contribution)
========================================================================================
```

#### SQL Derivation Used
```sql
WITH leak_stats AS (
    SELECT total_spend, contribution_margin 
    FROM marts.mart_campaign_margin_leak 
    WHERE campaign_name = 'Meta_Prospecting_BroadDeal'
),
healthy_stats AS (
    SELECT 
        SUM(contribution_margin) / NULLIF(SUM(total_spend), 0) as benchmark_cm_roas
    FROM marts.mart_campaign_margin_leak
    WHERE campaign_name IN ('Google_Search_Brand', 'Google_Search_NonBrand_Generic', 'Meta_Prospecting_Lookalike')
)
SELECT 
    ROUND(l.total_spend, 2) as reallocated_spend,
    ROUND(l.contribution_margin, 2) as current_leak_cm,
    ROUND(h.benchmark_cm_roas, 3) as target_reallocation_cm_roas,
    ROUND(l.total_spend * h.benchmark_cm_roas, 2) as potential_new_cm,
    ROUND((l.total_spend * h.benchmark_cm_roas) - l.contribution_margin, 2) as net_incremental_cm_opportunity
FROM leak_stats l, healthy_stats h;
```

---

### Slide 5: Roadmap & Engagement Investment

#### 12-Week Implementation Timeline
- **Weeks 1–3: Discovery & Data Architecture Audit**
  - Ad network API authentication & Shopify/ERP schema mapping.
  - Identity resolution definition and PII compliance audit.
- **Weeks 4–6: Ingestion & Data Warehouse Modeling**
  - GCS lake landing and BigQuery partitioned tables.
  - dbt staging layer and automated source freshness monitors.
- **Weeks 7–9: Attribution Engine & Airflow Orchestration**
  - Multi-touch attribution models and unit economics business logic.
  - Airflow DAG deployment, retry policies, SLAs, and backfill test.
- **Weeks 10–12: Looker Studio BI Rollout, Training & Handover**
  - CFO, CMO, and CSO dashboard implementation.
  - Executive enablement, KPI glossary signoff, and operational handover.

#### Commercial Terms
- **Engagement Fee:** **$250,000** fixed fee.
- **Milestone Billing:**
  - **30% ($75,000)** upon kickoff and architecture blueprint approval.
  - **40% ($100,000)** upon completion of dbt pipeline & attribution validation.
  - **30% ($75,000)** upon Looker Studio dashboard rollout and executive handover.
- **ROI Payback:** Expected incremental margin of **$4.39M** yields an engagement ROI of **17.5x**.
