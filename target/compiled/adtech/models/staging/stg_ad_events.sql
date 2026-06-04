with source as (
    select * from read_parquet('data/raw/ad_events/*/part.parquet', hive_partitioning=true)
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