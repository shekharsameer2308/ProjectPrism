with windowed_touches as (

    select * from {{ ref('int_touchpoints_windowed') }}

),

decay_weights as (

    select
        order_id,
        customer_id,
        touch_id,
        platform,
        campaign_id,
        touch_type,
        touch_timestamp,
        order_timestamp,
        -- Exponential decay: 2^(-age_seconds / half_life_seconds)
        power(
            2.0,
            - (touch_age_seconds / ({{ var('half_life_days_time_decay', 7.0) }} * 86400.0))
        ) as raw_decay_weight
    from windowed_touches

),

normalized as (

    select
        'time_decay' as model_name,
        order_id,
        customer_id,
        touch_id,
        platform,
        campaign_id,
        touch_type,
        touch_timestamp,
        order_timestamp,
        cast(
            round(
                raw_decay_weight / nullif(sum(raw_decay_weight) over (partition by order_id), 0),
                6
            ) as numeric
        ) as attributed_weight
    from decay_weights

)

select * from normalized
