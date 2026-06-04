with source as (
    select * from {{ source('raw', 'advertisers') }}
)
select 
    advertiser_id,
    advertiser_name,
    country,
    status,
    cast(created_at as date) as created_at
from source