with natural_members as (
    select distinct customer_id
    from {{ ref('stg_retail_store_sales') }}
    where customer_id is not null
),
keyed_members as (
    select
        row_number() over (order by customer_id)::integer as customer_sk,
        customer_id
    from natural_members
)

select
    -1::integer as customer_sk,
    'UNKNOWN'::text as customer_id
union all
select customer_sk, customer_id
from keyed_members
