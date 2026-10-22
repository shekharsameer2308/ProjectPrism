with unioned_attributions as (

    select * from {{ ref('int_attribution_last_click') }}
    union all
    select * from {{ ref('int_attribution_linear') }}
    union all
    select * from {{ ref('int_attribution_position_based') }}
    union all
    select * from {{ ref('int_attribution_time_decay') }}

),

order_margins as (

    select * from {{ ref('int_order_margin') }}

),

customer_orders as (

    select
        order_id,
        is_first_order,
        is_repeat_order,
        customer_region,
        first_order_date
    from {{ ref('int_customer_orders') }}

),

final as (

    select
        {{ dbt_utils.generate_surrogate_key(['a.model_name', 'a.order_id', 'a.touch_id']) }} as attribution_id,
        a.model_name,
        a.order_id,
        a.customer_id,
        a.touch_id,
        a.platform,
        a.campaign_id,
        a.touch_type,
        a.touch_timestamp,
        a.order_timestamp,
        cast(cast(a.order_timestamp as date) as date) as order_date,
        co.first_order_date,
        co.customer_region,
        co.is_first_order,
        co.is_repeat_order,
        a.attributed_weight,

        -- Attributed Volume Metrics
        cast(1.0 * a.attributed_weight as numeric) as attributed_orders,
        cast((case when co.is_first_order then 1.0 else 0.0 end) * a.attributed_weight as numeric) as attributed_new_customers,

        -- Attributed Financial & Margin Metrics
        cast(round(om.gross_revenue * a.attributed_weight, 4) as numeric) as attributed_gross_revenue,
        cast(round(om.discount_amount * a.attributed_weight, 4) as numeric) as attributed_discount,
        cast(round(om.total_refunds * a.attributed_weight, 4) as numeric) as attributed_refunds,
        cast(round(om.net_revenue * a.attributed_weight, 4) as numeric) as attributed_net_revenue,
        cast(round(om.total_cogs * a.attributed_weight, 4) as numeric) as attributed_cogs,
        cast(round(om.gross_margin * a.attributed_weight, 4) as numeric) as attributed_gross_margin,
        cast(round(om.shipping_cost * a.attributed_weight, 4) as numeric) as attributed_shipping_cost,
        cast(round(om.payment_fee * a.attributed_weight, 4) as numeric) as attributed_payment_fee,
        cast(round(om.contribution_margin * a.attributed_weight, 4) as numeric) as attributed_contribution_margin

    from unioned_attributions a
    inner join order_margins om
        on a.order_id = om.order_id
    inner join customer_orders co
        on a.order_id = co.order_id

)

select * from final
