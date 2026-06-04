with source as (
    select * from {{ source('raw', 'campaigns') }}
)
select 
    campaign_id,
    advertiser_id,
    campaign_name,
    channel,
    bid_cpm,
    daily_budget,
    start_date
from source
