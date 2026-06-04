with source as (
    select * from {{ source('raw', 'ad_events') }}
)
select
    event_id,
    event_ts,
    cast(event_date as date)        as event_date,
    campaign_id,
    device,
    country,
    event_type,
    revenue
from source
