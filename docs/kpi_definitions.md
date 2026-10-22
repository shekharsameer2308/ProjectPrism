# Core Business Logic & KPI Definitions

This document defines the mathematical formulas, accounting principles, and business logic implemented across the **Omnichannel Marketing ROI & Attribution Engine** for GlobalRetail Co.

---

## 1. Unit Economics & Profitability Metrics

| Metric | Formula | Description |
|---|---|---|
| **Gross Revenue** | `SUM(unit_price * qty)` | Total transaction value before discounts and deductions |
| **Discounts** | `SUM(discount_amount)` | Promotional markdowns and coupon incentives |
| **Refunds** | `SUM(refund_amount)` | Total value returned to customers upon product return |
| **Net Revenue** | `Gross Revenue - Discounts - Refunds` | Realized revenue retained by the business |
| **COGS (Cost of Goods Sold)** | `SUM(unit_cogs * qty)` | Direct cost to manufacture/source goods sold |
| **Shipping Margin** | `Shipping Charged - Shipping Cost` | Direct freight net cost (often negative for free shipping) |
| **Payment Gateway Fees** | `SUM(payment_fee)` | Credit card processing fees (e.g. 2.9% + $0.30 per transaction) |
| **Contribution Margin (CM)** | `Net Revenue - COGS - Shipping Cost - Payment Fees` | Dollar contribution left over to cover fixed overhead and marketing |
| **Contribution Margin %** | `Contribution Margin / Net Revenue` | Percentage of net sales converted to contribution margin |

---

## 2. Marketing Efficiency & Acquisition Metrics

| Metric | Formula | Description |
|---|---|---|
| **Platform Reported ROAS** | `Platform Reported Revenue / Platform Spend` | Self-reported, non-deduplicated ROAS shown in ad network dashboards (frequently overstated) |
| **True Revenue ROAS** | `Attributed Net Revenue / Platform Spend` | ROAS calculated against deduplicated, attributed net revenue |
| **Contribution Margin ROAS (CM-ROAS)** | `Attributed Contribution Margin / Platform Spend` | **True profitability indicator.** Break-even is exactly 1.0. A value < 1.0 means each acquisition dollar destroys margin. |
| **Blended CAC** | `Total Acquisition Spend / Total New Customers` | Overall cost to acquire a net new customer across all paid channels |
| **Channel CAC** | `Channel Spend / Attributed First-Time Customers` | Fully loaded marketing cost per first-time customer by channel |
| **Blended CPA** | `Total Spend / Attributed Orders` | Cost per order acquisition regardless of customer newness |
| **Burn Rate** | `MTD Spend / Monthly Budget` vs `% of Month Elapsed` | Pacing metric to alert on over/under-spending against target |

---

## 3. Customer Lifetime Value (LTV) & Retention Metrics

| Metric | Formula | Description |
|---|---|---|
| **12-Month Cohort LTV (CM)** | `Cumulative 12-month CM of Cohort / Initial Cohort Size` | Realized cumulative contribution margin per customer over 365 days from first purchase |
| **LTV to CAC Ratio** | `12-Month Cohort CM LTV / Channel CAC` | Ratio of customer lifetime margin to acquisition cost. Healthy benchmark is **>= 3.0:1**. |
| **CAC Payback Period (Months)** | Smallest `M` where `Cumulative CM at Month M >= CAC` | Months required for a customer cohort's gross profit to fully recoup acquisition CAC |
| **D30 / D60 / D90 Retention Rate** | `Active Cohort Customers at Day N / Cohort Size` | % of customer cohort placing a repeat order within 30, 60, or 90 days of first order |

---

## 4. Multi-Touch Attribution Methodology

Multi-touch attribution models distribute fractional credit across customer touchpoints within an established lookback window:
- **Click Lookback Window:** 30 days prior to order timestamp.
- **Impression Lookback Window:** 1 day (24 hours) prior to order timestamp.

### Models Implemented
1. **Last-Touch (Last Non-Direct Click):** 100% credit assigned to the final paid interaction prior to purchase.
2. **Linear Attribution:** Uniform credit (`1 / N`) across all `N` touchpoints in the lookback window.
3. **Position-Based (U-Shaped / 40-20-40):** 40% credit to the first touch (discovery), 40% credit to the last touch (conversion), and the remaining 20% distributed evenly across middle assists. (If single touch, 100%; if two touches, 50%/50%).
4. **Time-Decay Attribution:** Exponentially decaying weights with a 7-day half-life: `Weight(t) = 2^(-(t_conversion - t_touch) / 7 days)`. Normalized to sum to 1.0 per order.

> [!NOTE]
> **Attribution Integrity Rule:** The sum of attributed fractional credit across all touchpoints for any single order must equal exactly **1.0**. This is validated by singular dbt test `assert_attribution_credit_sums_to_one.sql`.
