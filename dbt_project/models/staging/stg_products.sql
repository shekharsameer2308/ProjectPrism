with source as (

    select * from {{ source('raw', 'raw_products') }}

),

standardized as (

    select
        trim(sku) as sku,
        trim(category) as product_category,
        cast(list_price as numeric) as list_price,
        cast(unit_cogs as numeric) as unit_cogs,
        cast(list_price - unit_cogs as numeric) as unit_gross_margin,
        cast(round((list_price - unit_cogs) / nullif(list_price, 0), 4) as numeric) as gross_margin_rate,
        row_number() over (
            partition by sku
            order by list_price desc
        ) as row_num
    from source

),

deduped as (

    select
        sku,
        product_category,
        list_price,
        unit_cogs,
        unit_gross_margin,
        gross_margin_rate
    from standardized
    where row_num = 1

)

select * from deduped
