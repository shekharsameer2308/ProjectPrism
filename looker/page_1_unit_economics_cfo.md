# Looker Studio Page 1: Unit Economics & Cash Contribution (CFO)

> **Primary Audience:** Chief Financial Officer (CFO), VP Finance, Corporate Controller  
> **Key Data Source:** `marts.mart_unit_economics`  
> **Takeaway Headline:** *"While gross sales continue to scale, true contribution margin is heavily compressed by post-purchase freight, payment fees, and coupon discounts."*

---

## 1. Global Page Filters & Controls

| Filter Type | Control Field | Default Selection | Looker Setting |
|---|---|---|---|
| **Date Range Control** | `date` | Past 12 Months (Fixed / Rolling) | Auto-applies to all visuals |
| **Drop-down List** | `model_name` | `position_based` | Single-select (`last_touch`, `linear`, `position_based`, `time_decay`) |

---

## 2. Executive KPI Scorecards (Row 1)

### Scorecard 1: Blended CAC (Customer Acquisition Cost)
- **Primary Metric:** `SUM(total_spend) / SUM(new_customers)`
- **Display Name:** `Blended CAC`
- **Format:** Currency (`$`, 2 decimal places)
- **Comparison:** Previous period (Delta % and Arrow)
- **Target Benchmark:** `< $120.00`

### Scorecard 2: Blended CM-ROAS
- **Primary Metric:** `SUM(contribution_margin) / SUM(total_spend)`
- **Display Name:** `Blended CM-ROAS`
- **Format:** Number (`0.00x`)
- **Color Rule:** Green if `>= 1.0x`, Red if `< 1.0x`
- **Benchmark:** Break-even is strictly `1.00x`

### Scorecard 3: LTV : CAC Ratio
- **Calculated Metric:** `AVG(ltv_12m_cm_per_customer) / (SUM(total_spend) / SUM(new_customers))`
- **Display Name:** `12-Month LTV : CAC`
- **Format:** Number (`0.0:1`)
- **Benchmark Line:** `3.0:1` (Industry health standard)

### Scorecard 4: Contribution Margin %
- **Primary Metric:** `SUM(contribution_margin) / SUM(net_revenue)`
- **Display Name:** `Contribution Margin %`
- **Format:** Percent (`0.0%`)

---

## 3. Main Analytical Charts

### Visual 1: Contribution Margin Waterfall (The "Where Did The Margin Go?" Chart)
- **Chart Type:** Waterfall Chart / Bar Breakdown
- **Data Source:** `marts.mart_unit_economics`
- **Categories (Sequential Steps):**
  1. `Gross Revenue` (`+`)
  2. `Coupon Discounts` (`-`)
  3. `Product Refunds` (`-`)
  4. `Net Revenue` (`Subtotal`)
  5. `Cost of Goods Sold (COGS)` (`-`)
  6. `Carrier Freight Shipping` (`-`)
  7. `Payment Processing Fees` (`-`)
  8. `Contribution Margin` (`Final Total`)
- **Style:** Red bars for negative deductions, Blue for revenues, Green for Contribution Margin.

### Visual 2: Blended CAC & CM-ROAS Trend Over Time
- **Chart Type:** Dual-Axis Time Series
- **Dimension:** `date` (Grouped by Month: `YYYY-MM`)
- **Left Axis (Bars):** `Blended CAC` (Currency `$`)
- **Right Axis (Line):** `True CM-ROAS` with reference line at `1.0x`
- **Observation:** Highlights rising acquisition costs during Q4 holiday spikes.

### Visual 3: Cash Flow Summary Table
- **Chart Type:** Pivot / Flat Table
- **Dimensions:** `date` (Month)
- **Metrics:** `total_spend`, `gross_revenue`, `net_revenue`, `total_cogs`, `shipping_cost`, `payment_fee`, `contribution_margin`, `true_cm_roas`
- **Total Row:** Show Summary Row at bottom.
