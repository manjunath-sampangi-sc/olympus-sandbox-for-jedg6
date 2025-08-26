{{ config(
    materialized='table',
    schema='silver'
) }}

-- Silver layer model for learning analytics
-- Enriches enrollment data with course and user information for comprehensive learning insights

with enrollments as (
    select
        enrollment_id,
        user_id,
        course_id,
        enrollment_date,
        completion_date,
        progress_percentage,
        status,
        last_accessed_date,
        time_spent_minutes,
        grade,
        certificate_issued,
        enrollment_source,
        instructor_id,
        cohort_id,
        created_at,
        updated_at
    from {{ ref('stg_disco_enrollments') }}
),

courses as (
    select
        course_id,
        course_name,
        category,
        null as subcategory,
        difficulty_level,
        duration_hours,
        null as course_instructor_id,
        null as course_format,
        null as language,
        null as course_status
    from {{ ref('stg_disco_courses') }}
),

users as (
    select
        user_id,
        email,
        first_name,
        last_name,
        department,
        null as job_title,
        manager_id,
        skill_level,
        location
    from {{ ref('stg_disco_users') }}
),

learning_analytics as (
    select
        e.enrollment_id,
        e.user_id,
        e.course_id,
        e.enrollment_date,
        e.completion_date,
        e.progress_percentage,
        e.status as enrollment_status,
        e.last_accessed_date,
        e.time_spent_minutes,
        e.grade,
        e.certificate_issued,
        e.enrollment_source,
        e.instructor_id,
        e.cohort_id,
        
        -- Course information
        c.course_name,
        c.category,
        c.subcategory,
        c.difficulty_level,
        c.duration_hours,
        c.course_format,
        c.language as course_language,
        c.course_status,
        
        -- User information
        u.email,
        u.first_name,
        u.last_name,
        u.first_name || ' ' || u.last_name as full_name,
        u.department,
        u.job_title,
        u.manager_id,
        u.skill_level,
        u.location,
        
        -- Calculated fields
        case 
            when e.completion_date is not null then 'Completed'
            when e.progress_percentage >= 80 then 'Near Completion'
            when e.progress_percentage >= 50 then 'In Progress'
            when e.progress_percentage > 0 then 'Started'
            else 'Not Started'
        end as learning_status,
        
        case 
            when e.completion_date is not null then 
                datediff('day', e.enrollment_date, e.completion_date)
            else 
                datediff('day', e.enrollment_date, current_date())
        end as days_since_enrollment,
        
        case 
            when e.completion_date is not null and c.duration_hours > 0 then
                (e.time_spent_minutes / 60.0) / c.duration_hours * 100
            else null
        end as time_efficiency_percentage,
        
        case 
            when e.last_accessed_date < current_date() - interval '7 days' then 'Inactive'
            when e.last_accessed_date < current_date() - interval '3 days' then 'Low Activity'
            else 'Active'
        end as engagement_level,
        
        e.created_at,
        e.updated_at,
        current_timestamp() as processed_at
        
    from enrollments e
    left join courses c on e.course_id = c.course_id
    left join users u on e.user_id = u.user_id
)

select * from learning_analytics