
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select advertiser_id
from "dev"."main"."stg_advertisers"
where advertiser_id is null



  
  
      
    ) dbt_internal_test