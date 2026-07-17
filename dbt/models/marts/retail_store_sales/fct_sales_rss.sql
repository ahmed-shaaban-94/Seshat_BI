with sales as (
    select *
    from {{ ref('stg_retail_store_sales') }}
)

select
    row_number() over (order by s.transaction_id)::integer as fct_sales_rss_sk,
    s.transaction_id,
    s.discount_applied,
    coalesce(dc.customer_sk, -1) as customer_sk,
    coalesce(dp.product_sk, -1) as product_sk,
    coalesce(dpm.payment_method_sk, -1) as payment_method_sk,
    coalesce(dl.location_sk, -1) as location_sk,
    dd.date_sk,
    s.price_per_unit,
    s.quantity,
    s.total_spent
from sales as s
left join {{ ref('dim_customer_rss') }} as dc
    on dc.customer_id = s.customer_id
left join {{ ref('dim_product_rss') }} as dp
    on dp.item = s.item
left join {{ ref('dim_payment_method_rss') }} as dpm
    on dpm.payment_method = s.payment_method
left join {{ ref('dim_location_rss') }} as dl
    on dl.location = s.location
left join {{ ref('dim_date_rss') }} as dd
    on dd.full_date = s.transaction_date
