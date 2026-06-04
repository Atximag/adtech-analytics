
  
  create view "dev"."main"."stg_campaigns__dbt_tmp" as (
    with source as (
    select * from 'data/raw/campaigns.parquet'
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
  );
