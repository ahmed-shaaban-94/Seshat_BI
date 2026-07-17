with source_rows as (
    select
        trim(transaction_id) as transaction_id,
        trim(customer_id) as customer_id,
        trim(category) as category,
        trim(item) as item,
        trim(price_per_unit) as price_per_unit,
        trim(quantity) as quantity,
        trim(total_spent) as total_spent,
        trim(payment_method) as payment_method,
        trim(location) as location,
        trim(transaction_date) as transaction_date,
        trim(discount_applied) as discount_applied
    from {{ source('bronze', 'retail_store_sales') }}
)

select
    nullif(transaction_id, '') as transaction_id,
    nullif(customer_id, '') as customer_id,
    nullif(item, '') as item,
    nullif(category, '') as category,
    nullif(price_per_unit, '')::numeric(12, 2) as price_per_unit,
    nullif(quantity, '')::numeric(12, 2) as quantity,
    nullif(total_spent, '')::numeric(12, 2) as total_spent,
    nullif(payment_method, '') as payment_method,
    nullif(location, '') as location,
    nullif(transaction_date, '')::date as transaction_date,
    case lower(nullif(discount_applied, ''))
        when 'true' then true
        when 'false' then false
        else null
    end as discount_applied
from source_rows
