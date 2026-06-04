with source as (
    select * from 'data/raw/advertisers.parquet'
)
select 
    advertiser_id,
    advertiser_name,
    country,
    status,
    cast(created_at as date) as created_at
from source