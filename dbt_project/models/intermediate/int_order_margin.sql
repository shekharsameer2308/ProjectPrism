with orders as (

    select * from {{ ref('stg_orders') }}

),

order_items_aggregated as (

    select
        order_id,
        sum(quantity) as total_items_count,
        sum(line_cogs) as total_cogs
    from {{ ref('stg_order_items') }}
    group by order_id

),

returns_aggregated as (

    select
        order_id,
        sum(refund_amount) as total_refunds
    from {{ ref('stg_returns') }}
    group by order_id

),

order_economics as (

    select
        o.order_id,
        o.customer_id,
        o.order_timestamp,
        o.order_date,
        o.order_status,
        coalesce(items.total_items_count, 0) as total_items_count,
        o.gross_revenue,
        o.discount_amount,
        coalesce(ret.total_refunds, 0) as total_refunds,
        cast(o.gross_revenue - o.discount_amount - coalesce(ret.total_refunds, 0) as numeric) as net_revenue,
        coalesce(items.total_cogs, 0) as total_cogs,
        cast((o.gross_revenue - o.discount_amount - coalesce(ret.total_refunds, 0)) - coalesce(items.total_cogs, 0) as numeric) as gross_margin,
        o.shipping_charged,
        o.shipping_cost,
        cast(o.shipping_charged - o.shipping_cost as numeric) as shipping_margin,
        o.payment_fee,
        o.tax_amount,
        -- Contribution Margin (CM) = Net Revenue - COGS - Shipping Cost - Payment Fees
        cast(
            (o.gross_revenue - o.discount_amount - coalesce(ret.total_refunds, 0))
            - coalesce(items.total_cogs, 0)
            - o.shipping_cost
            - o.payment_fee
            as numeric
        ) as contribution_margin
    from orders o
    left join order_items_aggregated items
        on o.order_id = items.order_id
    left join returns_aggregated ret
        on o.order_id = ret.order_id

),

final as (

    select
        *,
        cast(
            round(contribution_margin / nullif(net_revenue, 0), 4)
            as numeric
        ) as contribution_margin_pct
    from order_economics

)

select * from final
