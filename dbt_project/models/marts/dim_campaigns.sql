select
    campaign_id,
    campaign_name,
    channel,
    start_date
from {{ ref('stg_campaigns') }}
