with windowed_touches as (

    select * from {{ ref('int_touchpoints_windowed') }}

),

calculated as (

    select
        'position_based' as model_name,
        order_id,
        customer_id,
        touch_id,
        platform,
        campaign_id,
        touch_type,
        touch_timestamp,
        order_timestamp,
        case
            -- Single touch: receives 100% credit
            when total_touches_for_order = 1 then 1.0

            -- Two touches: 50% first touch, 50% last touch
            when total_touches_for_order = 2 then 0.50

            -- Three or more touches: 40% first touch, 40% last touch, 20% distributed across middle
            when touch_order_asc = 1 then 0.40
            when touch_order_desc = 1 then 0.40
            else round(0.20 / nullif(total_touches_for_order - 2, 0), 6)
        end as raw_weight
    from windowed_touches

),

final as (

    select
        model_name,
        order_id,
        customer_id,
        touch_id,
        platform,
        campaign_id,
        touch_type,
        touch_timestamp,
        order_timestamp,
        cast(raw_weight as numeric) as attributed_weight
    from calculated

)

select * from final
