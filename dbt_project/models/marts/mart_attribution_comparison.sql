with campaign_spend as (

    select
        platform,
        campaign_id,
        campaign_name,
        sum(spend_amount) as total_spend
    from {{ ref('stg_ad_spend') }}
    group by platform, campaign_id, campaign_name

),

attributed_by_model as (

    select
        platform,
        campaign_id,
        -- Last Touch Metrics
        sum(case when model_name = 'last_touch' then attributed_orders else 0 end) as last_touch_orders,
        sum(case when model_name = 'last_touch' then attributed_net_revenue else 0 end) as last_touch_net_revenue,
        sum(case when model_name = 'last_touch' then attributed_contribution_margin else 0 end) as last_touch_cm,

        -- Linear Metrics
        sum(case when model_name = 'linear' then attributed_orders else 0 end) as linear_orders,
        sum(case when model_name = 'linear' then attributed_net_revenue else 0 end) as linear_net_revenue,
        sum(case when model_name = 'linear' then attributed_contribution_margin else 0 end) as linear_cm,

        -- Position Based Metrics
        sum(case when model_name = 'position_based' then attributed_orders else 0 end) as position_based_orders,
        sum(case when model_name = 'position_based' then attributed_net_revenue else 0 end) as position_based_net_revenue,
        sum(case when model_name = 'position_based' then attributed_contribution_margin else 0 end) as position_based_cm,

        -- Time Decay Metrics
        sum(case when model_name = 'time_decay' then attributed_orders else 0 end) as time_decay_orders,
        sum(case when model_name = 'time_decay' then attributed_net_revenue else 0 end) as time_decay_net_revenue,
        sum(case when model_name = 'time_decay' then attributed_contribution_margin else 0 end) as time_decay_cm

    from {{ ref('int_attributed_revenue') }}
    group by platform, campaign_id

),

combined as (

    select
        {{ dbt_utils.generate_surrogate_key(['cs.platform', 'cs.campaign_id']) }} as comparison_id,
        cs.platform,
        cs.campaign_id,
        cs.campaign_name,
        cs.total_spend,

        -- 1. Last Touch
        coalesce(a.last_touch_orders, 0) as last_touch_orders,
        coalesce(a.last_touch_net_revenue, 0) as last_touch_net_revenue,
        coalesce(a.last_touch_cm, 0) as last_touch_cm,
        cast(round(coalesce(a.last_touch_net_revenue, 0) / nullif(cs.total_spend, 0), 2) as numeric) as last_touch_revenue_roas,
        cast(round(coalesce(a.last_touch_cm, 0) / nullif(cs.total_spend, 0), 2) as numeric) as last_touch_cm_roas,

        -- 2. Linear
        coalesce(a.linear_orders, 0) as linear_orders,
        coalesce(a.linear_net_revenue, 0) as linear_net_revenue,
        coalesce(a.linear_cm, 0) as linear_cm,
        cast(round(coalesce(a.linear_net_revenue, 0) / nullif(cs.total_spend, 0), 2) as numeric) as linear_revenue_roas,
        cast(round(coalesce(a.linear_cm, 0) / nullif(cs.total_spend, 0), 2) as numeric) as linear_cm_roas,

        -- 3. Position Based
        coalesce(a.position_based_orders, 0) as position_based_orders,
        coalesce(a.position_based_net_revenue, 0) as position_based_net_revenue,
        coalesce(a.position_based_cm, 0) as position_based_cm,
        cast(round(coalesce(a.position_based_net_revenue, 0) / nullif(cs.total_spend, 0), 2) as numeric) as position_based_revenue_roas,
        cast(round(coalesce(a.position_based_cm, 0) / nullif(cs.total_spend, 0), 2) as numeric) as position_based_cm_roas,

        -- 4. Time Decay
        coalesce(a.time_decay_orders, 0) as time_decay_orders,
        coalesce(a.time_decay_net_revenue, 0) as time_decay_net_revenue,
        coalesce(a.time_decay_cm, 0) as time_decay_cm,
        cast(round(coalesce(a.time_decay_net_revenue, 0) / nullif(cs.total_spend, 0), 2) as numeric) as time_decay_revenue_roas,
        cast(round(coalesce(a.time_decay_cm, 0) / nullif(cs.total_spend, 0), 2) as numeric) as time_decay_cm_roas,

        -- Multi-Touch Variance vs Last-Touch (The "Attribution Shift")
        cast(round(coalesce(a.position_based_net_revenue, 0) - coalesce(a.last_touch_net_revenue, 0), 2) as numeric) as position_vs_last_touch_revenue_delta,
        cast(round((coalesce(a.position_based_net_revenue, 0) - coalesce(a.last_touch_net_revenue, 0)) / nullif(a.last_touch_net_revenue, 0), 4) as numeric) as position_vs_last_touch_pct_shift

    from campaign_spend cs
    left join attributed_by_model a
        on cs.platform = a.platform
        and cs.campaign_id = a.campaign_id

)

select * from combined
