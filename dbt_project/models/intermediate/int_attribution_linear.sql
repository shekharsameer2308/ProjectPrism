with windowed_touches as (

    select * from {{ ref('int_touchpoints_windowed') }}

),

final as (

    select
        'linear' as model_name,
        order_id,
        customer_id,
        touch_id,
        platform,
        campaign_id,
        touch_type,
        touch_timestamp,
        order_timestamp,
        cast(round(1.0 / total_touches_for_order, 6) as numeric) as attributed_weight
    from windowed_touches

)

select * from final
