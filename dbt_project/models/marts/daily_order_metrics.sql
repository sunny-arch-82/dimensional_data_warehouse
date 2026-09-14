select
    order_date,
    round(sum(case when status in ('completed', 'refunded') then revenue_usd else 0 end), 2) as gross_revenue,
    round(sum(case when status = 'completed' then revenue_usd else 0 end), 2) as net_revenue,
    count(distinct case when status in ('completed', 'refunded') then customer_id end) as active_customers,
    count(*) filter (where status in ('completed', 'refunded')) as transacted_orders,
    count(*) filter (where status = 'refunded') as refunded_orders
from {{ ref('fct_orders') }}
group by order_date
