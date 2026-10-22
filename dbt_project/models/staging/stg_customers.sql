with source as (

    select * from {{ source('raw', 'raw_customers') }}

),

standardized as (

    select
        trim(customer_id) as customer_id,
        cast(first_order_date as date) as first_order_date,
        trim(region) as customer_region,
        trim(email_hash) as email_hash,
        row_number() over (
            partition by customer_id
            order by first_order_date asc
        ) as row_num
    from source

),

deduped as (

    select
        customer_id,
        first_order_date,
        customer_region,
        email_hash
    from standardized
    where row_num = 1

)

select * from deduped
