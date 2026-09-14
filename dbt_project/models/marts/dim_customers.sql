with customers as (
    select * from {{ ref('stg_customers') }}
),
order_rollup as (
    select
        customer_id,
        min(case when status in ('completed', 'refunded') then order_date end) as first_transaction_date,
        max(case when status in ('completed', 'refunded') then order_date end) as last_transaction_date,
        count(*) filter (where status in ('completed', 'refunded')) as transacted_orders,
        sum(case when status in ('completed', 'refunded') then revenue_usd else 0 end) as lifetime_gross_revenue,
        sum(case when status = 'completed' then revenue_usd else 0 end) as lifetime_net_revenue
    from {{ ref('stg_orders') }}
    group by customer_id
)
select
    c.customer_id,
    c.first_seen_date,
    c.segment,
    r.first_transaction_date,
    r.last_transaction_date,
    coalesce(r.transacted_orders, 0) as transacted_orders,
    coalesce(r.lifetime_gross_revenue, 0)::numeric(18,2) as lifetime_gross_revenue,
    coalesce(r.lifetime_net_revenue, 0)::numeric(18,2) as lifetime_net_revenue,
    (coalesce(r.transacted_orders, 0) > 1) as is_repeat_customer
from customers c
left join order_rollup r using (customer_id)
