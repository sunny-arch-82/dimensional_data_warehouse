select
    cast(order_id as text) as order_id,
    cast(customer_id as text) as customer_id,
    cast(order_date as date) as order_date,
    cast(revenue_usd as numeric(18, 2)) as revenue_usd,
    lower(trim(status)) as status
from {{ ref('orders') }}
