with customer_acquisition as (

    -- Find the acquisition touchpoint for each customer's first order
    select
        co.customer_id,
        co.first_order_date,
        cast(cast(date_trunc('month', co.first_order_date) as date) as date) as cohort_month,
        co.customer_region,
        w.platform as acquisition_platform,
        w.campaign_id as acquisition_campaign_id
    from {{ ref('int_customer_orders') }} co
    inner join {{ ref('int_touchpoints_windowed') }} w
        on co.order_id = w.order_id
        and w.touch_order_asc = 1
    where co.is_first_order = true

),

campaign_names as (

    select distinct
        platform,
        campaign_id,
        campaign_name
    from {{ ref('stg_ad_spend') }}

),

customer_orders_agg as (

    select
        co.customer_id,
        count(distinct co.order_id) as total_orders_lifetime,
        count(distinct case when co.is_repeat_order and co.days_since_first_order <= 30 then co.order_id end) as repeat_orders_d30,
        count(distinct case when co.is_repeat_order and co.days_since_first_order <= 60 then co.order_id end) as repeat_orders_d60,
        count(distinct case when co.is_repeat_order and co.days_since_first_order <= 90 then co.order_id end) as repeat_orders_d90,
        sum(case when co.days_since_first_order <= 365 then co.contribution_margin else 0 end) as cm_12m_per_cust
    from {{ ref('int_customer_orders') }} co
    group by co.customer_id

),

customer_joined as (

    select
        ca.cohort_month,
        ca.acquisition_platform,
        ca.acquisition_campaign_id,
        coalesce(cn.campaign_name, ca.acquisition_campaign_id) as acquisition_campaign_name,
        ca.customer_id,
        case when coa.repeat_orders_d30 > 0 then 1 else 0 end as is_retained_d30,
        case when coa.repeat_orders_d60 > 0 then 1 else 0 end as is_retained_d60,
        case when coa.repeat_orders_d90 > 0 then 1 else 0 end as is_retained_d90,
        coa.total_orders_lifetime - 1 as repeat_orders_count,
        coa.cm_12m_per_cust
    from customer_acquisition ca
    left join campaign_names cn
        on ca.acquisition_platform = cn.platform
        and ca.acquisition_campaign_id = cn.campaign_id
    left join customer_orders_agg coa
        on ca.customer_id = coa.customer_id

),

cohort_summary as (

    select
        cohort_month,
        acquisition_platform,
        acquisition_campaign_id,
        acquisition_campaign_name,
        count(distinct customer_id) as cohort_size,
        sum(is_retained_d30) as retained_customers_d30,
        sum(is_retained_d60) as retained_customers_d60,
        sum(is_retained_d90) as retained_customers_d90,
        sum(repeat_orders_count) as total_repeat_orders,
        sum(cm_12m_per_cust) as total_12m_cm
    from customer_joined
    group by cohort_month, acquisition_platform, acquisition_campaign_id, acquisition_campaign_name

),

final as (

    select
        {{ dbt_utils.generate_surrogate_key(['cohort_month', 'acquisition_platform', 'acquisition_campaign_id']) }} as cohort_id,
        cohort_month,
        acquisition_platform,
        acquisition_campaign_id,
        acquisition_campaign_name,
        cohort_size,
        retained_customers_d30,
        retained_customers_d60,
        retained_customers_d90,
        cast(round(retained_customers_d30 * 1.0 / nullif(cohort_size, 0), 4) as numeric) as d30_retention_rate,
        cast(round(retained_customers_d60 * 1.0 / nullif(cohort_size, 0), 4) as numeric) as d60_retention_rate,
        cast(round(retained_customers_d90 * 1.0 / nullif(cohort_size, 0), 4) as numeric) as d90_retention_rate,
        total_repeat_orders,
        cast(round(total_repeat_orders * 1.0 / nullif(cohort_size, 0), 2) as numeric) as repeat_orders_per_customer,
        total_12m_cm,
        cast(round(total_12m_cm / nullif(cohort_size, 0), 2) as numeric) as ltv_12m_cm_per_customer
    from cohort_summary

)

select * from final
