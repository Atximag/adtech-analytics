with events as (
    select * from {{ ref('stg_ad_events') }}
),

campaigns as (
    select * from {{ ref('stg_campaigns') }}
),

daily as (
    select
        e.event_date,
        e.campaign_id,
        c.channel,
        c.advertiser_id,
        count(case when e.event_type = 'impression' then 1 end) as impressions,
        count(case when e.event_type = 'click'      then 1 end) as clicks,
        count(case when e.event_type = 'conversion' then 1 end) as conversions,
        sum(e.revenue) as revenue
    from events e
    left join campaigns c on e.campaign_id = c.campaign_id
    group by 1, 2, 3, 4
)

select
    event_date,
    campaign_id,
    channel,
    advertiser_id,
    impressions,
    clicks,
    conversions,
    round(revenue, 2) as revenue,
    clicks / impressions as ctr,
    revenue / impressions * 1000 as ecpm,
    conversions / clicks as cvr

from daily