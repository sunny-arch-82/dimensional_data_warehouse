select
    cast(campaign_id as text) as campaign_id,
    trim(name) as campaign_name,
    lower(trim(channel)) as channel,
    cast(start_date as date) as start_date
from {{ ref('campaigns') }}
