{{ config(
    materialized='table',
    schema='silver'
) }}

-- Silver layer model for unified users
-- Combines HubSpot contacts and Disco LMS users into a single user view

with hubspot_contacts as (
    select
        contact_id as source_user_id,
        'hubspot' as source_system,
        email,
        first_name,
        last_name,
        null as company_name,
        null as job_title,
        null as department,
        null as manager_id,
        null as hire_date,
        lifecycle_stage as status,
        last_activity_date,
        null as total_courses_completed,
        null as total_learning_hours,
        null as skill_level,
        null as location,
        null as time_zone,
        null as language_preference,
        null as created_at,
        null as updated_at
    from {{ ref('stg_hubspot_contacts') }}
),

disco_users as (
    select
        user_id as source_user_id,
        'disco' as source_system,
        email,
        first_name,
        last_name,
        null as company_name,
        null as job_title,
        department,
        manager_id,
        hire_date,
        status,
        last_login_date as last_activity_date,
        total_courses_completed,
        total_learning_hours,
        skill_level,
        location,
        time_zone,
        language_preference,
        created_at,
        updated_at
    from {{ ref('stg_disco_users') }}
),

unified_users as (
    select
        {{ dbt_utils.generate_surrogate_key(['source_system', 'source_user_id']) }} as user_key,
        source_user_id,
        source_system,
        email,
        first_name,
        last_name,
        coalesce(first_name, '') || ' ' || coalesce(last_name, '') as full_name,
        company_name,
        null as job_title,
        department,
        manager_id,
        hire_date,
        status,
        last_activity_date,
        total_courses_completed,
        total_learning_hours,
        skill_level,
        location,
        time_zone,
        language_preference,
        created_at,
        updated_at,
        current_timestamp() as processed_at
    from hubspot_contacts
    
    union all
    
    select
        {{ dbt_utils.generate_surrogate_key(['source_system', 'source_user_id']) }} as user_key,
        source_user_id,
        source_system,
        email,
        first_name,
        last_name,
        coalesce(first_name, '') || ' ' || coalesce(last_name, '') as full_name,
        company_name,
        null as job_title,
        department,
        manager_id,
        hire_date,
        status,
        last_activity_date,
        total_courses_completed,
        total_learning_hours,
        skill_level,
        location,
        time_zone,
        language_preference,
        created_at,
        updated_at,
        current_timestamp() as processed_at
    from disco_users
)

select * from unified_users