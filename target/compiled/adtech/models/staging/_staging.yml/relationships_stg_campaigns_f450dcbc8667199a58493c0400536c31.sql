
    
    

with child as (
    select advertiser_id as from_field
    from "dev"."main"."stg_campaigns"
    where advertiser_id is not null
),

parent as (
    select advertiser_id as to_field
    from "dev"."main"."stg_advertisers"
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null


