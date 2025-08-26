{{ config(
    materialized='table',
    schema='silver'
) }}

-- Silver model for Disco LMS communities data
-- This model cleans and standardizes community data from Bronze layer

with source_data as (
    select
        community_id,
        community_name,
        description,
        created_at,
        updated_at,
        status,
        member_count,
        settings,
        _loaded_at,
        _source
    from {{ source('disco', 'disco_communities') }}
),

cleaned_data as (
    select
        community_id,
        trim(community_name) as community_name,
        trim(description) as description,
        created_at::timestamp as created_at,
        updated_at::timestamp as updated_at,
        lower(trim(status)) as status,
        coalesce(member_count, 0) as member_count,
        settings,
        _loaded_at::timestamp as loaded_at,
        _source
    from source_data
    where community_id is not null
      and community_name is not null
      and community_name != ''
)

select
    community_id,
    community_name,
    description,
    created_at,
    updated_at,
    status,
    member_count,
    settings,
    loaded_at,
    _source,
    
    -- Derived fields
    case 
        when status = 'active' then true
        else false
    end as is_active,
    
    case
        when member_count = 0 then 'Empty'
        when member_count <= 10 then 'Small'
        when member_count <= 50 then 'Medium'
        when member_count <= 200 then 'Large'
        else 'Enterprise'
    end as community_size_category,
    
    current_timestamp() as dbt_updated_at
    
from cleaned_data