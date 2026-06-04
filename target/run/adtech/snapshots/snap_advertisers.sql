
      update "dev"."snapshots"."snap_advertisers" as DBT_INTERNAL_TARGET
    set dbt_valid_to = DBT_INTERNAL_SOURCE.dbt_valid_to
    from "snap_advertisers__dbt_tmp20260604162125900734" as DBT_INTERNAL_SOURCE
    where DBT_INTERNAL_SOURCE.dbt_scd_id::text = DBT_INTERNAL_TARGET.dbt_scd_id::text
      and DBT_INTERNAL_SOURCE.dbt_change_type::text in ('update'::text, 'delete'::text)
      
        and DBT_INTERNAL_TARGET.dbt_valid_to is null;
      

    insert into "dev"."snapshots"."snap_advertisers" ("advertiser_id", "advertiser_name", "country", "status", "created_at", "dbt_updated_at", "dbt_valid_from", "dbt_valid_to", "dbt_scd_id")
    select DBT_INTERNAL_SOURCE."advertiser_id",DBT_INTERNAL_SOURCE."advertiser_name",DBT_INTERNAL_SOURCE."country",DBT_INTERNAL_SOURCE."status",DBT_INTERNAL_SOURCE."created_at",DBT_INTERNAL_SOURCE."dbt_updated_at",DBT_INTERNAL_SOURCE."dbt_valid_from",DBT_INTERNAL_SOURCE."dbt_valid_to",DBT_INTERNAL_SOURCE."dbt_scd_id"
    from "snap_advertisers__dbt_tmp20260604162125900734" as DBT_INTERNAL_SOURCE
    where DBT_INTERNAL_SOURCE.dbt_change_type::text = 'insert'::text;


  