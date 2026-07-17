with parity_values as (
    select
        'fact_row_count'::text as assertion_id,
        'fact_row_count'::text as assertion_class,
        'fct_sales_rss'::text as subject,
        (select count(*)::numeric from {{ source('migration_gold', 'fct_sales_rss') }})
            as expected_value,
        (select count(*)::numeric from {{ ref('fct_sales_rss') }})
            as actual_value,
        0::numeric as tolerance_value

    union all

    select
        'fact_distinct_transaction_id',
        'business_key_count',
        'fct_sales_rss.transaction_id',
        (select count(distinct transaction_id)::numeric
         from {{ source('migration_gold', 'fct_sales_rss') }}),
        (select count(distinct transaction_id)::numeric
         from {{ ref('fct_sales_rss') }}),
        0::numeric

    union all

    select
        'fact_total_spent_sum',
        'additive_money_total',
        'fct_sales_rss.total_spent',
        (select coalesce(sum(total_spent), 0)::numeric
         from {{ source('migration_gold', 'fct_sales_rss') }}),
        (select coalesce(sum(total_spent), 0)::numeric
         from {{ ref('fct_sales_rss') }}),
        0.01::numeric

    union all

    select
        'dim_customer_member_count',
        'dimension_member_count',
        'dim_customer_rss',
        (select count(*)::numeric
         from {{ source('migration_gold', 'dim_customer_rss') }}),
        (select count(*)::numeric from {{ ref('dim_customer_rss') }}),
        0::numeric

    union all

    select
        'dim_product_member_count',
        'dimension_member_count',
        'dim_product_rss',
        (select count(*)::numeric
         from {{ source('migration_gold', 'dim_product_rss') }}),
        (select count(*)::numeric from {{ ref('dim_product_rss') }}),
        0::numeric

    union all

    select
        'dim_payment_method_member_count',
        'dimension_member_count',
        'dim_payment_method_rss',
        (select count(*)::numeric
         from {{ source('migration_gold', 'dim_payment_method_rss') }}),
        (select count(*)::numeric from {{ ref('dim_payment_method_rss') }}),
        0::numeric

    union all

    select
        'dim_location_member_count',
        'dimension_member_count',
        'dim_location_rss',
        (select count(*)::numeric
         from {{ source('migration_gold', 'dim_location_rss') }}),
        (select count(*)::numeric from {{ ref('dim_location_rss') }}),
        0::numeric

    union all

    select
        'dim_date_member_count',
        'dimension_member_count',
        'dim_date_rss',
        (select count(*)::numeric
         from {{ source('migration_gold', 'dim_date_rss') }}),
        (select count(*)::numeric from {{ ref('dim_date_rss') }}),
        0::numeric
)

select
    assertion_id,
    assertion_class,
    subject,
    expected_value::text as expected,
    actual_value::text as actual,
    abs(expected_value - actual_value)::text as delta,
    tolerance_value::text as tolerance,
    abs(expected_value - actual_value) <= tolerance_value as passed
from parity_values
order by assertion_id
