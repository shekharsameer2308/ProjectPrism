with source as (

    select * from {{ source('raw', 'raw_ad_spend') }}

),

standardized as (

    select
        cast(date as date) as spend_date,
        trim(platform) as platform,
        coalesce(nullif(trim(campaign_id), ''), 'unattributed') as campaign_id,
        case
            when nullif(trim(campaign_id), '') is null then 'Unattributed'
            else coalesce(nullif(trim(campaign_name), ''), 'Unattributed')
        end as campaign_name,
        cast(impressions as integer) as impressions,
        cast(clicks as integer) as clicks,
        cast(spend as numeric) as spend_amount,
        cast(platform_reported_conversions as integer) as platform_conversions,
        cast(platform_reported_revenue as numeric) as platform_revenue,
        row_number() over (
            partition by date, platform, coalesce(nullif(trim(campaign_id), ''), 'unattributed')
            order by spend desc
        ) as row_num
    from source

),

deduped as (

    select
        {{ dbt_utils.generate_surrogate_key(['spend_date', 'platform', 'campaign_id']) }} as spend_id,
        spend_date,
        platform,
        campaign_id,
        campaign_name,
        impressions,
        clicks,
        spend_amount,
        platform_conversions,
        platform_revenue
    from standardized
    where row_num = 1

)

select * from deduped
