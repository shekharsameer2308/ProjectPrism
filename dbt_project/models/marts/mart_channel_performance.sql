with campaign_metadata as (

    select distinct
        platform,
        campaign_id,
        campaign_name
    from {{ ref('stg_ad_spend') }}

),

campaign_spend_daily as (

    select
        spend_date as date,
        platform,
        campaign_id,
        campaign_name,
        sum(spend_amount) as spend,
        sum(impressions) as impressions,
        sum(clicks) as clicks,
        sum(platform_conversions) as platform_conversions,
        sum(platform_revenue) as platform_revenue
    from {{ ref('stg_ad_spend') }}
    group by spend_date, platform, campaign_id, campaign_name

),

attributed_daily as (

    select
        order_date as date,
        model_name,
        platform,
        campaign_id,
        sum(attributed_orders) as attributed_orders,
        sum(attributed_new_customers) as attributed_new_customers,
        sum(attributed_gross_revenue) as attributed_gross_revenue,
        sum(attributed_discount) as attributed_discount,
        sum(attributed_refunds) as attributed_refunds,
        sum(attributed_net_revenue) as attributed_net_revenue,
        sum(attributed_cogs) as attributed_cogs,
        sum(attributed_gross_margin) as attributed_gross_margin,
        sum(attributed_shipping_cost) as attributed_shipping_cost,
        sum(attributed_payment_fee) as attributed_payment_fee,
        sum(attributed_contribution_margin) as attributed_contribution_margin
    from {{ ref('int_attributed_revenue') }}
    group by order_date, model_name, platform, campaign_id

),

distinct_models as (

    select distinct model_name from {{ ref('int_attributed_revenue') }}

),

spend_by_model as (

    select
        s.date,
        m.model_name,
        s.platform,
        s.campaign_id,
        s.campaign_name,
        s.spend,
        s.impressions,
        s.clicks,
        s.platform_conversions,
        s.platform_revenue
    from campaign_spend_daily s
    cross join distinct_models m

),

combined as (

    select
        {{ dbt_utils.generate_surrogate_key(['coalesce(s.date, a.date)', 'coalesce(s.model_name, a.model_name)', 'coalesce(s.platform, a.platform)', 'coalesce(s.campaign_id, a.campaign_id)']) }} as channel_perf_id,
        coalesce(s.date, a.date) as date,
        coalesce(s.model_name, a.model_name) as model_name,
        coalesce(s.platform, a.platform) as platform,
        coalesce(s.campaign_id, a.campaign_id) as campaign_id,
        coalesce(s.campaign_name, meta.campaign_name, a.campaign_id) as campaign_name,

        -- Spend & Ad Network Signals
        coalesce(s.spend, 0) as spend,
        coalesce(s.impressions, 0) as impressions,
        coalesce(s.clicks, 0) as clicks,
        coalesce(s.platform_conversions, 0) as platform_conversions,
        coalesce(s.platform_revenue, 0) as platform_revenue,
        cast(round(coalesce(s.platform_revenue, 0) / nullif(s.spend, 0), 2) as numeric) as platform_roas,

        -- True Attributed Outcomes
        coalesce(a.attributed_orders, 0) as attributed_orders,
        coalesce(a.attributed_new_customers, 0) as attributed_new_customers,
        coalesce(a.attributed_gross_revenue, 0) as attributed_gross_revenue,
        coalesce(a.attributed_net_revenue, 0) as attributed_net_revenue,
        coalesce(a.attributed_cogs, 0) as attributed_cogs,
        coalesce(a.attributed_gross_margin, 0) as attributed_gross_margin,
        coalesce(a.attributed_shipping_cost, 0) as attributed_shipping_cost,
        coalesce(a.attributed_payment_fee, 0) as attributed_payment_fee,
        coalesce(a.attributed_contribution_margin, 0) as attributed_contribution_margin,

        -- Channel Unit Economics & True ROAS
        cast(round(coalesce(s.spend, 0) / nullif(a.attributed_new_customers, 0), 2) as numeric) as channel_cac,
        cast(round(coalesce(s.spend, 0) / nullif(a.attributed_orders, 0), 2) as numeric) as channel_cpa,
        cast(round(coalesce(a.attributed_net_revenue, 0) / nullif(s.spend, 0), 2) as numeric) as true_revenue_roas,
        cast(round(coalesce(a.attributed_contribution_margin, 0) / nullif(s.spend, 0), 2) as numeric) as true_cm_roas,

        -- Margin Health Flag
        case
            when coalesce(a.attributed_contribution_margin, 0) < coalesce(s.spend, 0) then true
            else false
        end as is_negative_contribution_margin

    from spend_by_model s
    full outer join attributed_daily a
        on s.date = a.date
        and s.model_name = a.model_name
        and s.platform = a.platform
        and s.campaign_id = a.campaign_id
    left join campaign_metadata meta
        on coalesce(s.platform, a.platform) = meta.platform
        and coalesce(s.campaign_id, a.campaign_id) = meta.campaign_id

)

select * from combined
