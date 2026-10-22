# Looker Studio Executive Dashboard Implementation Guide
> **GlobalRetail Co. — Omnichannel Marketing ROI & Attribution Suite**

This guide provides end-to-end specifications for creating the three executive dashboards in Google Looker Studio connected exclusively to the `mart_` consumption layer.

---

## 1. Connection Architecture

```text
Google BigQuery (or DuckDB Dev)
  ├── marts.mart_unit_economics           ──> Page 1: CFO Unit Economics
  ├── marts.mart_channel_performance      ──> Page 2: CMO Channel Performance
  ├── marts.mart_campaign_margin_leak     ──> Page 2: CMO Campaign Leak Table
  ├── marts.mart_attribution_comparison   ──> Page 2: CMO Model Comparison
  └── marts.mart_customer_retention       ──> Page 3: CSO Retention & LTV
```

### Data Source Credentials & Connector
- **Connector:** Google BigQuery (Official Native Connector)
- **Billing Project:** `globalretail-analytics-prod`
- **Dataset:** `marts`
- **Data Freshness:** 12 hours (aligns with daily Airflow orchestration)

---

## 2. Global Styling & Palette Standards

To maintain an enterprise-grade consulting aesthetic:
- **Background:** Clean White / Light Canvas `#F8F9FA`
- **Card Panels:** Pure White `#FFFFFF` with subtle 1px border `#E9ECEF` and 4px border radius.
- **Typography:** Google Fonts: `Inter` or `Roboto`
  - Headlines (Takeaway titles): 18pt Semi-Bold `#1A202C`
  - Scorecard Numbers: 28pt Bold `#0F172A`
  - Axis Labels & Captions: 10pt Regular `#64748B`
- **Semantic Color Palette:**
  - **Healthy / Profit:** Emerald Green `#10B981` (for CM-ROAS >= 1.5, LTV:CAC >= 3.0)
  - **Moderate / Neutral:** Slate Blue `#3B82F6` (for stable baseline metrics)
  - **Destructive / Alert:** Crimson Red `#EF4444` (for CM-ROAS < 1.0, high returns, margin loss)

---

## 3. Executive Pages Overview

1. **[Page 1: Unit Economics & Cash Contribution (CFO)](./page_1_unit_economics_cfo.md)**
   - **Takeaway Headline:** *"While gross sales continue to scale, true contribution margin is heavily compressed by post-purchase freight, payment fees, and coupon discounts."*
   - Scorecards for Blended CAC, LTV:CAC, Payback Months, and Contribution Margin Waterfall.

2. **[Page 2: Channel Performance & Margin Leak Discovery (CMO)](./page_2_channel_performance_cmo.md)**
   - **Takeaway Headline:** *"The 'Platform ROAS' illusion masks that our largest Meta acquisition campaign is destroying -$487K in cash margin."*
   - Side-by-side bar chart of Platform ROAS vs CM-ROAS, Campaign Margin Leak Table, and Multi-Touch Model Selector.

3. **[Page 3: Customer Retention & Cohort LTV (CSO)](./page_3_customer_retention_cso.md)**
   - **Takeaway Headline:** *"Google Non-Brand and Organic cohorts exhibit 3.2x higher D90 retention compared to deal-seeking Meta BroadDeal cohorts."*
   - D30/D60/D90 retention heatmap, 12-month cohort CM LTV curves, and repeat purchase frequency.

---

## 4. Verification & Query Reconciliation

All KPI cards and chart figures reconcile directly against BigQuery SQL queries. See [`looker/reconciliation_query.sql`](./reconciliation_query.sql) and run `python looker/verify_reconciliation.py`.
