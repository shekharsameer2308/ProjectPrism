-- Singular Test: assert_attribution_credit_sums_to_one.sql
-- Every converted order under every attribution model must have attributed credit summing to exactly 1.0.

with order_attribution_sums as (

    select
        model_name,
        order_id,
        sum(attributed_weight) as total_order_credit
    from {{ ref('int_attributed_revenue') }}
    group by model_name, order_id

)

select
    model_name,
    order_id,
    total_order_credit
from order_attribution_sums
where abs(total_order_credit - 1.0) > 0.001
