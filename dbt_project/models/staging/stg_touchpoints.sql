with source as (

    select * from {{ source('raw', 'raw_touchpoints') }}

),

standardized as (

    select
        trim(touch_id) as touch_id,
        trim(customer_id) as customer_id,
        cast(touch_ts as timestamp) as touch_timestamp,
        cast(cast(touch_ts as timestamp) as date) as touch_date,
        trim(platform) as platform,
        coalesce(nullif(trim(campaign_id), ''), 'unattributed') as campaign_id,
        lower(trim(touch_type)) as touch_type,
        row_number() over (
            partition by touch_id
            order by touch_ts asc
        ) as row_num
    from source

),

deduped as (

    select
        touch_id,
        customer_id,
        touch_timestamp,
        touch_date,
        platform,
        campaign_id,
        touch_type
    from standardized
    where row_num = 1

)

select * from deduped
