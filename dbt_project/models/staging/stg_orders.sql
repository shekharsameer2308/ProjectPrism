with source as (

    select * from {{ source('raw', 'raw_orders') }}

),

standardized as (

    select
        trim(order_id) as order_id,
        trim(customer_id) as customer_id,
        cast(order_ts as timestamp) as order_timestamp,
        cast(cast(order_ts as timestamp) as date) as order_date,
        cast(gross_revenue as numeric) as gross_revenue,
        cast(discount as numeric) as discount_amount,
        cast(shipping_charged as numeric) as shipping_charged,
        cast(shipping_cost as numeric) as shipping_cost,
        cast(payment_fee as numeric) as payment_fee,
        cast(tax as numeric) as tax_amount,
        lower(trim(status)) as order_status,
        row_number() over (
            partition by order_id
            order by order_ts asc
        ) as row_num
    from source

),

deduped as (

    select
        order_id,
        customer_id,
        order_timestamp,
        order_date,
        gross_revenue,
        discount_amount,
        shipping_charged,
        shipping_cost,
        payment_fee,
        tax_amount,
        order_status
    from standardized
    where row_num = 1

)

select * from deduped
