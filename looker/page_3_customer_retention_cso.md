# Looker Studio Page 3: Customer Retention & Cohort LTV (CSO)

> **Primary Audience:** Chief Strategy Officer (CSO), Head of Retention / CRM, VP Customer Success  
> **Key Data Source:** `marts.mart_customer_retention`  
> **Takeaway Headline:** *"Google Non-Brand and Organic cohorts exhibit 3.2x higher D90 retention compared to deal-seeking Meta BroadDeal cohorts."*

---

## 1. Global Page Filters & Controls

| Filter Type | Control Field | Default Selection | Looker Setting |
|---|---|---|---|
| **Date Range Control** | `cohort_month` | Past 18 Months | Date range picker |
| **Drop-down List** | `acquisition_platform` | All Platforms | Multi-select (`Google Ads`, `Meta Ads`, `TikTok Ads`, `Programmatic Display`, `Direct / Organic`) |

---

## 2. Executive KPI Scorecards (Row 1)

### Scorecard 1: Total Acquired Customers
- **Metric:** `SUM(cohort_size)`
- **Display Name:** `Total Cohort Acquisitions`
- **Format:** Number (comma formatted, 0 decimals)

### Scorecard 2: 30-Day Repeat Retention Rate (D30)
- **Metric:** `SUM(retained_customers_d30) / SUM(cohort_size)`
- **Display Name:** `D30 Retention Rate`
- **Format:** Percent (`0.0%`)

### Scorecard 3: 90-Day Repeat Retention Rate (D90)
- **Metric:** `SUM(retained_customers_d90) / SUM(cohort_size)`
- **Display Name:** `D90 Retention Rate`
- **Format:** Percent (`0.0%`)

### Scorecard 4: 12-Month Contribution Margin LTV
- **Metric:** `SUM(total_12m_cm) / SUM(cohort_size)`
- **Display Name:** `Avg 12M Cohort LTV (CM)`
- **Format:** Currency (`$`, 2 decimal places)

---

## 3. Main Analytical Charts

### Visual 1: Retention Heatmap Matrix (D30 / D60 / D90 Retention by Acquisition Channel)
- **Chart Type:** Pivot Table with Color Scale / Heatmap
- **Row Dimension:** `acquisition_campaign_name`
- **Column Metric 1:** `d30_retention_rate` (Green gradient for high retention, White/Red for low)
- **Column Metric 2:** `d60_retention_rate`
- **Column Metric 3:** `d90_retention_rate`
- **Column Metric 4:** `repeat_orders_per_customer`
- **Key Finding:**
  - `Google_Search_NonBrand_Generic`: D90 Retention ~ `24.0%`
  - `Google_Search_Brand`: D90 Retention ~ `28.5%`
  - `Meta_Prospecting_BroadDeal`: D90 Retention ~ `3.1%` (Deal-seeking churn trap)

### Visual 2: 12-Month Cumulative Cohort LTV Curves
- **Chart Type:** Multi-Line Chart
- **Dimension:** `cohort_month`
- **Breakdown Dimension:** `acquisition_platform`
- **Metric:** `ltv_12m_cm_per_customer` (`SUM(total_12m_cm) / SUM(cohort_size)`)
- **Observation:** Visualizes how customer cohorts acquired via intent-driven channels compound lifetime profit, while discount-driven cohorts remain flat.

### Visual 3: Repeat Purchase Frequency Distribution
- **Chart Type:** Horizontal Bar Chart
- **Dimension:** `acquisition_platform`
- **Metric:** `repeat_orders_per_customer` (`SUM(total_repeat_orders) / SUM(cohort_size)`)
- **Sorting:** Descending by repeat frequency
- **Style:** Clean solid bars with value data labels.
