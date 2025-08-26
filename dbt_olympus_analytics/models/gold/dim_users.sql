{{ config(
    materialized='table',
    schema='gold'
) }}

-- Gold layer dimension table for users
-- Business-ready user dimension combining all user sources

with unified_users as (
    select
        user_key,
        source_user_id,
        source_system,
        email,
        first_name,
        last_name,
        full_name,
        company_name,
        job_title,
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
        processed_at
    from {{ ref('int_users_unified') }}
),

-- Deduplicate users based on email, preferring Disco data over HubSpot
deduped_users as (
    select
        user_key,
        source_user_id,
        source_system,
        email,
        first_name,
        last_name,
        full_name,
        company_name,
        job_title,
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
        processed_at,
        row_number() over (
            partition by lower(email) 
            order by 
                case when source_system = 'disco' then 1 else 2 end,
                updated_at desc
        ) as rn
    from unified_users
    where email is not null
),

final_users as (
    select
        user_key,
        source_user_id,
        source_system,
        email,
        first_name,
        last_name,
        full_name,
        company_name,
        job_title,
        department,
        manager_id,
        hire_date,
        status,
        last_activity_date,
        coalesce(total_courses_completed, 0) as total_courses_completed,
        coalesce(total_learning_hours, 0) as total_learning_hours,
        skill_level,
        location,
        time_zone,
        language_preference,
        
        -- Business classifications
        case 
            when status in ('Active', 'active') then 'Active'
            when status in ('Inactive', 'inactive') then 'Inactive'
            else 'Unknown'
        end as user_status_category,
        
        case 
            when total_learning_hours >= 40 then 'High Engagement'
            when total_learning_hours >= 10 then 'Medium Engagement'
            when total_learning_hours > 0 then 'Low Engagement'
            else 'No Engagement'
        end as learning_engagement_tier,
        
        case 
            when job_title ilike '%manager%' or job_title ilike '%director%' or job_title ilike '%vp%' then 'Management'
            when job_title ilike '%senior%' or job_title ilike '%lead%' then 'Senior'
            when job_title ilike '%junior%' or job_title ilike '%associate%' then 'Junior'
            else 'Individual Contributor'
        end as job_level,
        
        created_at,
        updated_at,
        processed_at,
        current_timestamp() as dw_created_at,
        current_timestamp() as dw_updated_at
        
    from deduped_users
    where rn = 1
)

select * from final_users