with natural_members as (
    select distinct location
    from {{ ref('stg_retail_store_sales') }}
    where location is not null
),
keyed_members as (
    select
        row_number() over (order by location)::integer as location_sk,
        location
    from natural_members
)

select
    -1::integer as location_sk,
    'UNKNOWN'::text as location
union all
select location_sk, location
from keyed_members
