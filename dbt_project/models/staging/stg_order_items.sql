with source as (

    select * from {{ source('raw', 'raw_order_items') }}

),

standardized as (

    select
        trim(order_id) as order_id,
        trim(sku) as sku,
        cast(qty as integer) as quantity,
        cast(unit_price as numeric) as unit_price,
        cast(unit_cogs as numeric) as unit_cogs,
        cast(qty * unit_price as numeric) as line_gross_revenue,
        cast(qty * unit_cogs as numeric) as line_cogs,
        row_number() over (
            partition by order_id, sku
            order by qty desc
        ) as row_num
    from source

),

deduped as (

    select
        {{ dbt_utils.generate_surrogate_key(['order_id', 'sku']) }} as order_item_id,
        order_id,
        sku,
        quantity,
        unit_price,
        unit_cogs,
        line_gross_revenue,
        line_cogs
    from standardized
    where row_num = 1

)

select * from deduped
