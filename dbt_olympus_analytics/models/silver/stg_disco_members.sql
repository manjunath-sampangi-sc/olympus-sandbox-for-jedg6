{{ config(
    materialized='table',
    schema='silver'
) }}

-- Silver model for Disco LMS members data
-- This model cleans and standardizes member data from Bronze layer

with source_data as (
    select
        member_id,
        email,
        first_name,
        last_name,
        username,
        community_id,
        role,
        status,
        joined_at,
        last_active_at,
        profile_data,
        _loaded_at,
        _source
    from {{ source('disco', 'disco_members') }}
),

cleaned_data as (
    select
        member_id,
        lower(trim(email)) as email,
        trim(first_name) as first_name,
        trim(last_name) as last_name,
        trim(username) as username,
        community_id,
        lower(trim(role)) as role,
        lower(trim(status)) as status,
        joined_at::timestamp as joined_at,
        last_active_at::timestamp as last_active_at,
        profile_data,
        _loaded_at::timestamp as loaded_at,
        _source
    from source_data
    where member_id is not null
      and email is not null
      and email != ''
      and email like '%@%'
)

select
    member_id,
    email,
    first_name,
    last_name,
    username,
    community_id,
    role,
    status,
    joined_at,
    last_active_at,
    profile_data,
    loaded_at,
    _source,
    
    -- Derived fields
    concat(trim(first_name), ' ', trim(last_name)) as full_name,
    
    case 
        when status = 'active' then true
        else false
    end as is_active,
    
    case
        when last_active_at >= dateadd(day, -7, current_date()) then 'Active'
        when last_active_at >= dateadd(day, -30, current_date()) then 'Recent'
        when last_active_at >= dateadd(day, -90, current_date()) then 'Inactive'
        else 'Dormant'
    end as activity_status,
    
    datediff(day, joined_at, current_date()) as days_since_joined,
    
    case
        when datediff(day, joined_at, current_date()) <= 7 then 'New'
        when datediff(day, joined_at, current_date()) <= 30 then 'Recent'
        when datediff(day, joined_at, current_date()) <= 90 then 'Established'
        else 'Veteran'
    end as member_tenure_category,
    
    current_timestamp() as dbt_updated_at
    
from cleaned_data