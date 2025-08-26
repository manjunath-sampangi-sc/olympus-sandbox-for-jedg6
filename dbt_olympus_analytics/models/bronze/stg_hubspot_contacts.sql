{{ config(materialized='table') }}

with source_data as (
    select
        contact_id,
        trim(lower(email)) as email,
        trim(first_name) as first_name,
        trim(last_name) as last_name,
        trim(company) as company,
        trim(lower(lifecycle_stage)) as lifecycle_stage,
        cast(created_date as timestamp) as created_date,
        cast(last_modified_date as timestamp) as last_activity_date,
        current_timestamp() as loaded_at
    from {{ source('hubspot', 'hubspot_contacts') }}
)

select *
from source_data
where contact_id is not null
  and email is not null
  and email like '%@%'  -- Basic email validation