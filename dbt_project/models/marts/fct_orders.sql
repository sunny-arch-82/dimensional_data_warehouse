select
    o.order_id,
    o.customer_id,
    o.order_date,
    o.revenue_usd,
    o.status,
    c.segment,
    c.first_seen_date,
    (o.status in ('completed', 'refunded')) as is_transacted,
    (o.status = 'refunded') as is_refunded
from {{ ref('stg_orders') }} o
left join {{ ref('stg_customers') }} c using (customer_id)
