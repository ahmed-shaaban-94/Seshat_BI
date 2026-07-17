with natural_members as (
    select distinct payment_method
    from {{ ref('stg_retail_store_sales') }}
    where payment_method is not null
),
keyed_members as (
    select
        row_number() over (order by payment_method)::integer as payment_method_sk,
        payment_method
    from natural_members
)

select
    -1::integer as payment_method_sk,
    'UNKNOWN'::text as payment_method
union all
select payment_method_sk, payment_method
from keyed_members
