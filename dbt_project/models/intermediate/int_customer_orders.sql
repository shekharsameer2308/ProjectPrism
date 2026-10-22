with orders as (

    select * from {{ ref('int_order_margin') }}

),

customers as (

    select * from {{ ref('stg_customers') }}

),

sequenced_orders as (

    select
        o.order_id,
        o.customer_id,
        c.first_order_date,
        c.customer_region,
        o.order_timestamp,
        o.order_date,
        o.order_status,
        o.gross_revenue,
        o.net_revenue,
        o.total_cogs,
        o.contribution_margin,
        row_number() over (
            partition by o.customer_id
            order by o.order_timestamp asc, o.order_id asc
        ) as customer_order_sequence,
        lag(o.order_date) over (
            partition by o.customer_id
            order by o.order_timestamp asc, o.order_id asc
        ) as previous_order_date
    from orders o
    inner join customers c
        on o.customer_id = c.customer_id

),

final as (

    select
        order_id,
        customer_id,
        first_order_date,
        customer_region,
        order_timestamp,
        order_date,
        order_status,
        customer_order_sequence,
        case when customer_order_sequence = 1 then true else false end as is_first_order,
        case when customer_order_sequence > 1 then true else false end as is_repeat_order,
        {{ date_diff_days('order_date', 'first_order_date') }} as days_since_first_order,
        case
            when previous_order_date is not null
            then {{ date_diff_days('order_date', 'previous_order_date') }}
            else null
        end as days_since_previous_order,
        gross_revenue,
        net_revenue,
        total_cogs,
        contribution_margin
    from sequenced_orders

)

select * from final
