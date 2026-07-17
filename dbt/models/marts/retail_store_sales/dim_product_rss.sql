with natural_members as (
    select
        item,
        max(category) as category
    from {{ ref('stg_retail_store_sales') }}
    where item is not null
    group by item
),
keyed_members as (
    select
        row_number() over (order by item)::integer as product_sk,
        item,
        category
    from natural_members
)

select
    -1::integer as product_sk,
    'UNKNOWN'::text as item,
    'Unknown'::text as category
union all
select product_sk, item, category
from keyed_members
