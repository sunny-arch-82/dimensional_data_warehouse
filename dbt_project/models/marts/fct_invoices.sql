select
    i.invoice_id,
    i.customer_id,
    i.invoice_date,
    i.amount_usd,
    i.status,
    c.segment,
    (i.status = 'paid') as is_paid,
    (i.status = 'overdue') as is_overdue
from {{ ref('stg_invoices') }} i
left join {{ ref('stg_customers') }} c using (customer_id)
