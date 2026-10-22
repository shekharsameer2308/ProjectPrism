with source as (

    select * from {{ source('raw', 'raw_returns') }}

),

standardized as (

    select
        trim(order_id) as order_id,
        trim(sku) as sku,
        cast(return_ts as timestamp) as return_timestamp,
        cast(cast(return_ts as timestamp) as date) as return_date,
        cast(refund_amount as numeric) as refund_amount,
        row_number() over (
            partition by order_id, sku
            order by return_ts asc
        ) as row_num
    from source

),

deduped as (

    select
        {{ dbt_utils.generate_surrogate_key(['order_id', 'sku']) }} as return_id,
        order_id,
        sku,
        return_timestamp,
        return_date,
        refund_amount
    from standardized
    where row_num = 1

)

select * from deduped
