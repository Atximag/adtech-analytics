
    
    

select
    advertiser_id as unique_field,
    count(*) as n_records

from "dev"."main"."stg_advertisers"
where advertiser_id is not null
group by advertiser_id
having count(*) > 1


