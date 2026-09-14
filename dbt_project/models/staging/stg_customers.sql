select
    cast(customer_id as text) as customer_id,
    cast(first_seen_date as date) as first_seen_date,
    lower(trim(segment)) as segment
from {{ ref('customers') }}
