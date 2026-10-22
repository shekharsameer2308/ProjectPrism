with windowed_touches as (

    select * from {{ ref('int_touchpoints_windowed') }}

),

final as (

    select
        'last_touch' as model_name,
        order_id,
        customer_id,
        touch_id,
        platform,
        campaign_id,
        touch_type,
        touch_timestamp,
        order_timestamp,
        cast(1.0 as numeric) as attributed_weight
    from windowed_touches
    where touch_order_desc = 1

)

select * from final
