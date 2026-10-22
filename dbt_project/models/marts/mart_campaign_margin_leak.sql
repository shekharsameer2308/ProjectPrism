with campaign_spend as (

    select
        platform,
        campaign_id,
        campaign_name,
        sum(spend_amount) as total_spend,
        sum(impressions) as total_impressions,
        sum(clicks) as total_clicks,
        sum(platform_conversions) as platform_reported_conversions,
        sum(platform_revenue) as platform_reported_revenue
    from {{ ref('stg_ad_spend') }}
    group by platform, campaign_id, campaign_name

),

attributed_economics as (

    select
        platform,
        campaign_id,
        sum(attributed_orders) as attributed_orders,
        sum(attributed_new_customers) as attributed_new_customers,
        sum(attributed_gross_revenue) as gross_revenue,
        sum(attributed_discount) as discount_amount,
        sum(attributed_refunds) as refund_amount,
        sum(attributed_net_revenue) as net_revenue,
        sum(attributed_cogs) as total_cogs,
        sum(attributed_shipping_cost) as shipping_cost,
        sum(attributed_payment_fee) as payment_fee,
        sum(attributed_contribution_margin) as contribution_margin
    from {{ ref('int_attributed_revenue') }}
    where model_name = 'position_based'
    group by platform, campaign_id

),

ranked_campaigns as (

    select
        {{ dbt_utils.generate_surrogate_key(['cs.platform', 'cs.campaign_id']) }} as leak_id,
        cs.platform,
        cs.campaign_id,
        cs.campaign_name,
        cs.total_spend,
        cs.platform_reported_revenue,
        cast(round(cs.platform_reported_revenue / nullif(cs.total_spend, 0), 2) as numeric) as platform_roas,
        coalesce(ae.attributed_orders, 0) as attributed_orders,
        coalesce(ae.attributed_new_customers, 0) as attributed_new_customers,
        coalesce(ae.gross_revenue, 0) as gross_revenue,
        coalesce(ae.discount_amount, 0) as discount_amount,
        coalesce(ae.refund_amount, 0) as refund_amount,
        coalesce(ae.net_revenue, 0) as net_revenue,
        coalesce(ae.total_cogs, 0) as total_cogs,
        coalesce(ae.shipping_cost, 0) as shipping_cost,
        coalesce(ae.payment_fee, 0) as payment_fee,
        coalesce(ae.contribution_margin, 0) as contribution_margin,

        -- True Financial Returns
        cast(round(coalesce(ae.net_revenue, 0) / nullif(cs.total_spend, 0), 2) as numeric) as true_revenue_roas,
        cast(round(coalesce(ae.contribution_margin, 0) / nullif(cs.total_spend, 0), 2) as numeric) as cm_roas,

        -- Return Rate and Discount Intensity
        cast(round(coalesce(ae.refund_amount, 0) / nullif(ae.gross_revenue - ae.discount_amount, 0), 4) as numeric) as return_rate,
        cast(round(coalesce(ae.discount_amount, 0) / nullif(ae.gross_revenue, 0), 4) as numeric) as discount_rate,
        cast(round(coalesce(ae.total_cogs, 0) / nullif(ae.net_revenue, 0), 4) as numeric) as cogs_to_net_rev_ratio

    from campaign_spend cs
    left join attributed_economics ae
        on cs.platform = ae.platform
        and cs.campaign_id = ae.campaign_id

),

classified as (

    select
        *,
        -- Margin Destruction Quantification: Dollars lost when CM < Spend
        case
            when contribution_margin < total_spend
            then round(total_spend - contribution_margin, 2)
            else 0.0
        end as net_margin_destruction_dollars,

        -- Strategic Executive Classification
        case
            when platform_roas >= 3.0 and cm_roas < 1.0 then 'CRITICAL REVENUE LEAK'
            when cm_roas < 1.0 then 'MARGIN DESTRUCTIVE'
            when cm_roas between 1.0 and 1.5 then 'MODERATE EFFICIENCY'
            else 'HIGH CONTRIBUTION MARGIN'
        end as margin_efficiency_segment

    from ranked_campaigns

)

select * from classified
order by cm_roas asc
