# Looker Studio Page 2: Channel Performance & Margin Leak Discovery (CMO)

> **Primary Audience:** Chief Marketing Officer (CMO), VP Growth, Head of Performance Marketing  
> **Key Data Sources:** `marts.mart_channel_performance`, `marts.mart_campaign_margin_leak`  
> **Takeaway Headline:** *"The 'Platform ROAS' illusion masks that our largest Meta acquisition campaign is destroying -$487K in cash margin."*

---

## 1. Global Page Filters & Controls

| Filter Type | Control Field | Default Selection | Looker Setting |
|---|---|---|---|
| **Date Range Control** | `date` | All Available (24 Months) | Date range picker |
| **Drop-down List** | `model_name` | `position_based` | Single-select (`last_touch`, `linear`, `position_based`, `time_decay`) |
| **Drop-down List** | `platform` | All Platforms | Multi-select (`Google Ads`, `Meta Ads`, `TikTok Ads`, `Programmatic Display`) |

---

## 2. Executive KPI Scorecards (Row 1)

### Scorecard 1: Total Acquisition Spend
- **Metric:** `SUM(spend)`
- **Display Name:** `Total Acquisition Spend`
- **Format:** Currency (`$`, 0 decimal places)

### Scorecard 2: Platform-Reported ROAS (The Misleading Number)
- **Metric:** `SUM(platform_revenue) / SUM(spend)`
- **Display Name:** `Self-Reported Platform ROAS`
- **Format:** Number (`0.00x`)
- **Note:** Inflated by ad platform self-attribution windows.

### Scorecard 3: True Contribution Margin ROAS (The Truth)
- **Metric:** `SUM(attributed_contribution_margin) / SUM(spend)`
- **Display Name:** `True CM-ROAS (Net Profit)`
- **Format:** Number (`0.00x`)
- **Conditional Color:** Red if `< 1.00x`, Green if `>= 1.00x`

### Scorecard 4: Capital Destroyed on Negative Campaigns
- **Metric:** `SUM(CASE WHEN attributed_contribution_margin < spend THEN spend - attributed_contribution_margin ELSE 0 END)`
- **Display Name:** `Negative Margin Destruction`
- **Format:** Currency (`$`, 0 decimal places)
- **Style:** Deep Red badge `#DC2626`

---

## 3. Main Analytical Charts

### Visual 1: The "Aha!" Chart: Platform ROAS vs. True CM-ROAS by Channel
- **Chart Type:** Grouped Column Chart (Side-by-side bars)
- **Dimension:** `platform`
- **Metric 1 (Grey / Blue Bar):** `Platform ROAS` (`SUM(platform_revenue) / SUM(spend)`)
- **Metric 2 (Color-Coded Bar):** `True CM-ROAS` (`SUM(attributed_contribution_margin) / SUM(spend)`)
- **Reference Line:** Horizontal Line at `Y = 1.0` labeled **"Break-Even CM (1.0x)"**
- **The Story:** Google Ads shows high platform ROAS and positive CM; Meta Ads shows ~3.7x platform ROAS but severely depressed CM; TikTok shows low platform ROAS but valuable upstream assist.

### Visual 2: Flagship Campaign Margin Leak Audit Table
- **Chart Type:** Flat Table with Heatmap Formatting
- **Data Source:** `marts.mart_campaign_margin_leak`
- **Dimensions:** `platform`, `campaign_name`, `margin_efficiency_segment`
- **Metrics (Columns):**
  1. `total_spend`
  2. `platform_reported_revenue`
  3. `platform_roas`
  4. `net_revenue`
  5. `total_cogs`
  6. `shipping_cost`
  7. `contribution_margin`
  8. `cm_roas`
  9. `net_margin_destruction_dollars`
- **Sorting:** `cm_roas` ascending (Worst leaks at the top)
- **Conditional Formatting:**
  - `cm_roas < 1.0`: Entire row highlighted in soft Red (`#FEE2E2`).
  - `margin_efficiency_segment == 'CRITICAL REVENUE LEAK'`: Bold Crimson text.

### Visual 3: Channel CPA Trendlines
- **Chart Type:** Multi-Line Time Series Chart
- **Dimension:** `date` (Month)
- **Breakdown Dimension:** `platform`
- **Metric:** `Channel CPA` (`SUM(spend) / SUM(attributed_orders)`)
- **Observation:** Highlights rising cost-per-acquisition across social and search during competitive bidding periods.
