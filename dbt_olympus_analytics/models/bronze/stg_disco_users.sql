{{ config(
    materialized='table',
    schema='bronze'
) }}

-- Staging model for Disco LMS members data from live API
-- This model pulls raw member data from Bronze layer and applies basic cleaning

with source_data as (
    select
        member_id as user_id,
        email,
        first_name,
        last_name,
        username,
        role,
        null as department,
        null as manager_id,
        null as hire_date,
        status,
        last_active_at as last_login_date,
        null as total_courses_completed,
        null as total_learning_hours,
        null as skill_level,
        null as location,
        null as time_zone,
        null as language_preference,
        joined_at as created_at,
        _loaded_at as updated_at,
        community_id,
        profile_data
    from {{ source('disco', 'disco_members') }}
),

cleaned_data as (
    select
        user_id,
        lower(trim(email)) as email,
        trim(first_name) as first_name,
        trim(last_name) as last_name,

        trim(role) as role,
        trim(department) as department,
        manager_id,
        hire_date::date as hire_date,
        trim(status) as status,
        last_login_date::date as last_login_date,
        total_courses_completed,
        total_learning_hours,
        trim(skill_level) as skill_level,
        trim(location) as location,
        trim(time_zone) as time_zone,
        trim(language_preference) as language_preference,
        created_at::timestamp as created_at,
        updated_at::timestamp as updated_at
    from source_data
    where user_id is not null
      and email is not null
      and email like '%@%'
)

select * from cleaned_data