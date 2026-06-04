{% snapshot snap_advertisers %}

{{ config(
    target_schema='snapshots',
    unique_key='advertiser_id',
    strategy='check',
    check_cols=['status']
) }}

select * from {{ ref('stg_advertisers') }}

{% endsnapshot %}
