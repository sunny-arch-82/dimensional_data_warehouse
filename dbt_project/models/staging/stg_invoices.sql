select
    cast(invoice_id as text) as invoice_id,
    cast(customer_id as text) as customer_id,
    cast(invoice_date as date) as invoice_date,
    cast(amount_usd as numeric(18, 2)) as amount_usd,
    lower(trim(status)) as status
from {{ ref('invoices') }}
