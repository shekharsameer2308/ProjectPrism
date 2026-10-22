with orders as (

    select
        order_id,
        customer_id,
        order_timestamp,
        order_date
    from {{ ref('stg_orders') }}

),

touchpoints as (

    select
        touch_id,
        customer_id,
        touch_timestamp,
        touch_date,
        platform,
        campaign_id,
        touch_type
    from {{ ref('stg_touchpoints') }}

),

matched_touches as (

    select
        o.order_id,
        o.customer_id,
        o.order_timestamp,
        t.touch_id,
        t.touch_timestamp,
        t.platform,
        t.campaign_id,
        t.touch_type,
        {{ timestamp_diff_seconds('o.order_timestamp', 't.touch_timestamp') }} as touch_age_seconds
    from orders o
    inner join touchpoints t
        on o.customer_id = t.customer_id
        and t.touch_timestamp < o.order_timestamp
    where (
        -- Click lookback: default 30 days (2,592,000 seconds)
        (t.touch_type = 'click' and {{ timestamp_diff_seconds('o.order_timestamp', 't.touch_timestamp') }} <= {{ var('lookback_days_click', 30) }} * 86400)
        or
        -- Impression lookback: default 24 hours (86,400 seconds)
        (t.touch_type = 'impression' and {{ timestamp_diff_seconds('o.order_timestamp', 't.touch_timestamp') }} <= {{ var('lookback_hours_impression', 24) }} * 3600)
    )

),

-- Fallback touch for orders with zero qualifying paid touches in window
unmatched_orders as (

    select
        o.order_id,
        o.customer_id,
        o.order_timestamp,
        concat('TCH-DIR-', o.order_id) as touch_id,
        o.order_timestamp as touch_timestamp,
        'Direct / Organic' as platform,
        'direct_organic' as campaign_id,
        'click' as touch_type,
        0 as touch_age_seconds
    from orders o
    left join matched_touches m
        on o.order_id = m.order_id
    where m.order_id is null

),

all_touches as (

    select * from matched_touches
    union all
    select * from unmatched_orders

),

sequenced as (

    select
        order_id,
        customer_id,
        order_timestamp,
        touch_id,
        touch_timestamp,
        platform,
        campaign_id,
        touch_type,
        touch_age_seconds,
        row_number() over (
            partition by order_id
            order by touch_timestamp asc, touch_id asc
        ) as touch_order_asc,
        row_number() over (
            partition by order_id
            order by touch_timestamp desc, touch_id desc
        ) as touch_order_desc,
        count(*) over (
            partition by order_id
        ) as total_touches_for_order
    from all_touches

)

select * from sequenced
