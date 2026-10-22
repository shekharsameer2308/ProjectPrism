with daily_spend as (

    select
        spend_date as date,
        sum(spend_amount) as total_spend,
        sum(impressions) as total_impressions,
        sum(clicks) as total_clicks
    from {{ ref('stg_ad_spend') }}
    group by spend_date

),

attributed_daily as (

    select
        order_date as date,
        model_name,
        sum(attributed_orders) as total_orders,
        sum(attributed_new_customers) as new_customers,
        sum(case when is_repeat_order then attributed_orders else 0 end) as repeat_orders,
        sum(attributed_gross_revenue) as gross_revenue,
        sum(attributed_discount) as discount_amount,
        sum(attributed_refunds) as refund_amount,
        sum(attributed_net_revenue) as net_revenue,
        sum(attributed_cogs) as total_cogs,
        sum(attributed_gross_margin) as gross_margin,
        sum(attributed_shipping_cost) as shipping_cost,
        sum(attributed_payment_fee) as payment_fee,
        sum(attributed_contribution_margin) as contribution_margin
    from {{ ref('int_attributed_revenue') }}
    group by order_date, model_name

),

combined as (

    select
        {{ dbt_utils.generate_surrogate_key(['a.date', 'a.model_name']) }} as unit_econ_id,
        a.date,
        a.model_name,
        coalesce(s.total_spend, 0) as total_spend,
        coalesce(s.total_impressions, 0) as total_impressions,
        coalesce(s.total_clicks, 0) as total_clicks,
        a.total_orders,
        a.new_customers,
        a.repeat_orders,
        a.gross_revenue,
        a.discount_amount,
        a.refund_amount,
        a.net_revenue,
        a.total_cogs,
        a.gross_margin,
        a.shipping_cost,
        a.payment_fee,
        a.contribution_margin,

        -- Unit Economics & Margins
        cast(round(a.contribution_margin / nullif(a.net_revenue, 0), 4) as numeric) as contribution_margin_pct,
        cast(round(a.gross_margin / nullif(a.net_revenue, 0), 4) as numeric) as gross_margin_pct,

        -- Acquisition Metrics
        cast(round(coalesce(s.total_spend, 0) / nullif(a.new_customers, 0), 2) as numeric) as blended_cac,
        cast(round(coalesce(s.total_spend, 0) / nullif(a.total_orders, 0), 2) as numeric) as blended_cpa,
        cast(round(a.net_revenue / nullif(coalesce(s.total_spend, 0), 0), 2) as numeric) as true_revenue_roas,
        cast(round(a.contribution_margin / nullif(coalesce(s.total_spend, 0), 0), 2) as numeric) as true_cm_roas

    from attributed_daily a
    left join daily_spend s
        on a.date = s.date

)

select * from combined
