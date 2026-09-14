with orders as (
    select * from {{ ref('fct_orders') }}
),
metrics as (
    select
        max(order_date) as metric_as_of_date,
        sum(case when status in ('completed', 'refunded') then revenue_usd else 0 end) as gross_revenue,
        sum(case when status = 'completed' then revenue_usd else 0 end) as net_revenue,
        count(distinct case when status in ('completed', 'refunded') then customer_id end) as active_customers,
        count(*) filter (where status in ('completed', 'refunded')) as transacted_orders,
        count(*) filter (where status = 'refunded') as refunded_orders,
        sum(case when status = 'refunded' then revenue_usd else 0 end) as refund_amount
    from orders
)
select
    metric_as_of_date,
    round(gross_revenue, 2) as gross_revenue,
    round(net_revenue, 2) as net_revenue,
    active_customers,
    transacted_orders,
    refunded_orders,
    round(refund_amount, 2) as refund_amount,
    round(gross_revenue / nullif(transacted_orders, 0), 2) as average_order_value,
    round(100.0 * refunded_orders / nullif(transacted_orders, 0), 2) as refund_rate
from metrics
