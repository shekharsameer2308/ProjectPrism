# Enterprise Data Dictionary
> **GlobalRetail Co. Omnichannel Marketing ROI & Attribution Engine**

This document details the field-level specifications, primary keys, and data types for all staging and consumption entities.

---

## 1. Staging Layer (`staging`)

### `stg_ad_spend`
| Column | Type | Nullable | Description |
|---|---|---|---|
| `spend_id` | STRING (MD5) | No (PK) | Surrogate key: `md5(spend_date || platform || campaign_id)` |
| `spend_date` | DATE | No | Date of ad delivery |
| `platform` | STRING | No | Ad network (`Google Ads`, `Meta Ads`, `TikTok Ads`, `Programmatic Display`) |
| `campaign_id` | STRING | No | Campaign code (`CMP-*` or `'unattributed'`) |
| `campaign_name` | STRING | No | Descriptive campaign name |
| `impressions` | INT64 | No | Ad impressions |
| `clicks` | INT64 | No | Ad clicks |
| `spend_amount` | NUMERIC | No | Daily spend in USD |
| `platform_conversions` | INT64 | Yes | Self-reported conversions |
| `platform_revenue` | NUMERIC | Yes | Self-reported gross revenue |

### `stg_orders`
| Column | Type | Nullable | Description |
|---|---|---|---|
| `order_id` | STRING | No (PK) | Order identifier (`ORD-*`) |
| `customer_id` | STRING | No (FK) | Foreign key referencing `stg_customers` |
| `order_timestamp` | TIMESTAMP | No | Order timestamp in UTC |
| `order_date` | DATE | No | Order date in UTC |
| `gross_revenue` | NUMERIC | No | Order gross revenue |
| `discount_amount` | NUMERIC | No | Coupon/promotional discount |
| `shipping_charged` | NUMERIC | No | Shipping charged to customer |
| `shipping_cost` | NUMERIC | No | Actual freight cost absorbed |
| `payment_fee` | NUMERIC | No | Payment processing fee |
| `tax_amount` | NUMERIC | No | Sales tax charged |
| `order_status` | STRING | No | Fulfillment status (`completed`, `cancelled`) |

---

## 2. Marts Layer (`marts`)

### `mart_unit_economics`
| Column | Type | Description |
|---|---|---|
| `unit_econ_id` | STRING (PK) | Surrogate key: `md5(date || model_name)` |
| `date` | DATE | Calendar date |
| `model_name` | STRING | Attribution methodology |
| `total_spend` | NUMERIC | Total ad spend |
| `total_orders` | NUMERIC | Total attributed orders |
| `new_customers` | NUMERIC | Attributed first-time buyers |
| `gross_revenue` | NUMERIC | Gross sales |
| `discount_amount` | NUMERIC | Customer promotional discounts |
| `refund_amount` | NUMERIC | Product returns and refunds |
| `net_revenue` | NUMERIC | Realized net revenue (`gross - discount - refunds`) |
| `total_cogs` | NUMERIC | Cost of goods sold |
| `shipping_cost` | NUMERIC | Carrier shipping costs |
| `payment_fee` | NUMERIC | Merchant processing fees |
| `contribution_margin` | NUMERIC | Net realized contribution margin |
| `blended_cac` | NUMERIC | Spend / new customers |
| `blended_cpa` | NUMERIC | Spend / total orders |
| `true_cm_roas` | NUMERIC | Contribution margin / spend |

### `mart_campaign_margin_leak`
| Column | Type | Description |
|---|---|---|
| `leak_id` | STRING (PK) | Surrogate key: `md5(platform || campaign_id)` |
| `platform` | STRING | Advertising platform |
| `campaign_id` | STRING | Campaign code |
| `campaign_name` | STRING | Campaign name |
| `total_spend` | NUMERIC | Total ad spend |
| `platform_roas` | NUMERIC | Self-reported platform ROAS |
| `net_revenue` | NUMERIC | Attributed net revenue |
| `contribution_margin` | NUMERIC | Attributed contribution margin |
| `cm_roas` | NUMERIC | True Contribution Margin ROAS |
| `net_margin_destruction_dollars` | NUMERIC | Dollars destroyed when CM < spend |
| `margin_efficiency_segment` | STRING | Classification (`CRITICAL REVENUE LEAK`, `MARGIN DESTRUCTIVE`, `HEALTHY`) |
