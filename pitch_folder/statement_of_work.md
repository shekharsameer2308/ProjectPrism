# Statement of Work (SOW)
## Omnichannel Marketing ROI & Attribution Engine Implementation

**Client:** GlobalRetail Co.  
**Consulting Practice:** Analytics Engineering & Data Strategy  
**Engagement Duration:** 12 Weeks  
**Contract Type:** Fixed-Fee Milestone Engagement ($250,000 USD)  
**Effective Date:** November 1, 2026  

---

### 1. Executive Summary & Objectives
GlobalRetail Co. seeks to replace platform-reported ad metrics with an enterprise data engine that calculates true **Contribution-Margin ROAS (CM-ROAS)** and **Blended Customer Acquisition Cost (CAC)** across all digital marketing channels.

The objective is to establish an automated, reproducible modern data stack (GCS $\to$ BigQuery $\to$ dbt $\to$ Airflow $\to$ Looker Studio) that exposes unprofitable acquisition campaigns and empowers leadership to optimize $40M in annual media spend.

---

### 2. Scope of Services & Key Deliverables

#### In-Scope Deliverables
1. **Data Ingestion & Landing Lake (GCS):** Automated pipelines landing date-partitioned daily extracts from Google Ads, Meta Ads, TikTok Ads, Display DSPs, and ERP/Shopify order systems into Google Cloud Storage.
2. **Data Warehouse & Transformation Pipeline (BigQuery & dbt):**
   - Cleaned staging layer handling deduplication, UTC normalization, and missing campaign attributes.
   - Intermediate business logic computing per-order contribution margin after COGS, discounts, returns, carrier freight, and merchant gateway fees.
   - Four multi-touch attribution algorithms: **Last-Touch**, **Linear**, **Position-Based (40/20/40)**, and **Time-Decay (7-day half-life)**.
   - Production consumption marts: `mart_unit_economics`, `mart_channel_performance`, `mart_customer_retention`, `mart_attribution_comparison`, and `mart_campaign_margin_leak`.
   - Comprehensive testing suite: primary key uniqueness, referential integrity foreign keys, accepted values, source freshness checks, and attribution credit conservation (sum to 1.0).
3. **Orchestration & Data Quality (Airflow):** Containerized daily ingestion and transformation DAGs with 2-hour SLAs, automated retry policies, and backfill capabilities.
4. **Executive BI Dashboards (Looker Studio):** Three tailored executive views for the CFO, CMO, and CSO with cross-filtering by date, channel, and attribution methodology.
5. **Technical Documentation & Enablement:** Lineage documentation site, KPI data dictionary, runbooks, and handover training.

#### Out-of-Scope
- Media buying execution or creative copywriting.
- Direct operational ERP inventory adjustments or warehouse physical logistics.
- Marketing Mix Modeling (MMM) and matched-market geo-holdout experiments (available as Phase 2 add-on).

---

### 3. Project Schedule & Milestones (12-Week Roadmap)

| Phase | Timeline | Core Focus & Milestones |
|---|---|---|
| **Phase 1: Discovery & Architecture** | Weeks 1–3 | Source system access, API authentication, schema audit, identity resolution logic, and Architecture Design Document signoff. |
| **Phase 2: Data Engineering & Modeling** | Weeks 4–9 | GCS landing lake setup, BigQuery datasets, dbt transformations, multi-touch attribution engine, automated testing, and Airflow orchestration. |
| **Phase 3: Executive BI & Handover** | Weeks 10–12 | Looker Studio dashboard build, data reconciliation audit, executive stakeholder training, runbook delivery, and final signoff. |

---

### 4. Commercial Terms & Payment Schedule

Total engagement fee is **$250,000 USD**, billed upon completion of verified milestones:

| Milestone | Deliverable Trigger | Percentage | Amount |
|---|---|---|---|
| **M1: Kickoff & Blueprint** | Delivery and client signoff of Architecture Design Blueprint | 30% | $75,000 |
| **M2: Pipeline Completion** | Successful run of dbt build, attribution engine, and Airflow DAGs | 40% | $100,000 |
| **M3: BI Rollout & Handover** | Looker Studio dashboards deployed, reconciled, and team trained | 30% | $75,000 |

---

### 5. Client Responsibilities & Assumptions
- Client will provide timely API credentials, BigQuery IAM access, and Shopify/ERP export access within 5 business days of contract execution.
- Multi-touch attribution is understood as an algorithmic heuristic; formal incrementality validation via geo-holdout testing is recommended as a subsequent engagement.
- Work will adhere to SOC 2 and GDPR privacy standards with all customer emails hashed (SHA256).

---

### 6. Acceptance Criteria & Risk Mitigations

- **Acceptance:** Deliverables must pass 100% of dbt tests, exhibit zero data reconciliation discrepancies between Looker Studio and BigQuery, and demonstrate idempotent backfill execution.
- **Risk Mitigation:** Strict staging deduplication window functions guard against duplicate order records; automated source freshness alerts detect upstream API stalls before model building.

---

**Authorized Signatures:**

_______________________________________  
*For GlobalRetail Co.*  
**Date:** ______________________________  

_______________________________________  
*For Analytics Consulting Practice*  
**Date:** ______________________________  
