-- ==============================================================================
-- Looker Studio Reconciliation Queries
-- Reconciles dashboard KPI card numbers directly against BigQuery / Warehouse marts
-- ==============================================================================

-- 1. PAGE 1: CFO UNIT ECONOMICS RECONCILIATION
-- (Model: position_based)
SELECT 
    'Page 1: CFO Unit Economics' AS dashboard_page,
    SUM(total_spend) AS total_acquisition_spend,
    SUM(gross_revenue) AS total_gross_revenue,
    SUM(discount_amount) AS total_discounts,
    SUM(refund_amount) AS total_refunds,
    SUM(net_revenue) AS total_net_revenue,
    SUM(total_cogs) AS total_cogs,
    SUM(shipping_cost) AS total_carrier_shipping_cost,
    SUM(payment_fee) AS total_payment_fees,
    SUM(contribution_margin) AS total_contribution_margin,
    ROUND(SUM(total_spend) / NULLIF(SUM(new_customers), 0), 2) AS blended_cac,
    ROUND(SUM(total_spend) / NULLIF(SUM(total_orders), 0), 2) AS blended_cpa,
    ROUND(SUM(net_revenue) / NULLIF(SUM(total_spend), 0), 2) AS true_revenue_roas,
    ROUND(SUM(contribution_margin) / NULLIF(SUM(total_spend), 0), 2) AS true_cm_roas
FROM marts.mart_unit_economics
WHERE model_name = 'position_based';


-- 2. PAGE 2: CMO CHANNEL PERFORMANCE & LEAK RECONCILIATION
SELECT 
    'Page 2: CMO Channel Performance' AS dashboard_page,
    platform,
    SUM(spend) AS platform_spend,
    SUM(platform_revenue) AS platform_reported_revenue,
    ROUND(SUM(platform_revenue) / NULLIF(SUM(spend), 0), 2) AS platform_roas,
    SUM(attributed_net_revenue) AS attributed_net_revenue,
    SUM(attributed_contribution_margin) AS attributed_contribution_margin,
    ROUND(SUM(attributed_contribution_margin) / NULLIF(SUM(spend), 0), 2) AS true_cm_roas
FROM marts.mart_channel_performance
WHERE model_name = 'position_based'
GROUP BY platform
ORDER BY platform_spend DESC;


-- 3. FLAGSHIP LEAK CAMPAIGN RECONCILIATION (Meta_Prospecting_BroadDeal)
SELECT 
    'Flagship Leak Verification' AS audit_type,
    platform,
    campaign_name,
    total_spend,
    platform_reported_revenue,
    platform_roas,
    net_revenue,
    contribution_margin,
    cm_roas,
    margin_efficiency_segment
FROM marts.mart_campaign_margin_leak
WHERE campaign_name = 'Meta_Prospecting_BroadDeal';


-- 4. PAGE 3: CSO RETENTION & COHORT LTV RECONCILIATION
SELECT 
    'Page 3: CSO Customer Retention' AS dashboard_page,
    acquisition_platform,
    SUM(cohort_size) AS total_acquired_customers,
    ROUND(SUM(retained_customers_d30) * 1.0 / NULLIF(SUM(cohort_size), 0), 4) AS avg_d30_retention_rate,
    ROUND(SUM(retained_customers_d60) * 1.0 / NULLIF(SUM(cohort_size), 0), 4) AS avg_d60_retention_rate,
    ROUND(SUM(retained_customers_d90) * 1.0 / NULLIF(SUM(cohort_size), 0), 4) AS avg_d90_retention_rate,
    ROUND(SUM(total_12m_cm) / NULLIF(SUM(cohort_size), 0), 2) AS avg_12m_cm_ltv_per_customer
FROM marts.mart_customer_retention
GROUP BY acquisition_platform
ORDER BY total_acquired_customers DESC;
