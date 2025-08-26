{{ config(
    materialized='table',
    schema='gold'
) }}

-- Gold layer fact table for learning analytics
-- Business-ready learning metrics and KPIs

with learning_data as (
    select
        enrollment_id,
        user_id,
        course_id,
        enrollment_date,
        completion_date,
        progress_percentage,
        enrollment_status,
        last_accessed_date,
        time_spent_minutes,
        grade,
        certificate_issued,
        enrollment_source,
        instructor_id,
        cohort_id,
        course_name,
        category,
        subcategory,
        difficulty_level,
        duration_hours,
        course_format,
        course_language,
        course_status,
        email,
        first_name,
        last_name,
        full_name,
        department,
        job_title,
        manager_id,
        skill_level,
        location,
        learning_status,
        days_since_enrollment,
        time_efficiency_percentage,
        engagement_level,
        created_at,
        updated_at,
        processed_at
    from {{ ref('int_learning_analytics') }}
),

fact_learning as (
    select
        enrollment_id,
        user_id,
        course_id,
        enrollment_date,
        completion_date,
        progress_percentage,
        enrollment_status,
        last_accessed_date,
        time_spent_minutes,
        coalesce(time_spent_minutes, 0) / 60.0 as time_spent_hours,
        grade,
        certificate_issued,
        enrollment_source,
        instructor_id,
        cohort_id,
        course_name,
        category,
        subcategory,
        difficulty_level,
        duration_hours,
        course_format,
        course_language,
        course_status,
        email,
        first_name,
        last_name,
        full_name,
        department,
        job_title,
        manager_id,
        skill_level,
        location,
        learning_status,
        days_since_enrollment,
        time_efficiency_percentage,
        engagement_level,
        
        -- Key business metrics
        case when completion_date is not null then 1 else 0 end as is_completed,
        case when certificate_issued then 1 else 0 end as is_certified,
        case when progress_percentage >= 80 then 1 else 0 end as is_near_completion,
        case when last_accessed_date >= current_date() - interval '7 days' then 1 else 0 end as is_recently_active,
        
        -- Time-based metrics
        case 
            when completion_date is not null then 
                datediff('day', enrollment_date, completion_date)
            else null
        end as completion_time_days,
        
        case 
            when completion_date is not null and duration_hours > 0 then
                (time_spent_minutes / 60.0) / duration_hours
            else null
        end as time_efficiency_ratio,
        
        -- Performance scoring
        case 
            when grade >= 90 then 'Excellent'
            when grade >= 80 then 'Good'
            when grade >= 70 then 'Satisfactory'
            when grade >= 60 then 'Needs Improvement'
            when grade is not null then 'Poor'
            else 'Not Graded'
        end as performance_tier,
        
        -- Engagement scoring
        case 
            when time_spent_minutes >= duration_hours * 60 * 1.2 then 'High Engagement'
            when time_spent_minutes >= duration_hours * 60 * 0.8 then 'Normal Engagement'
            when time_spent_minutes >= duration_hours * 60 * 0.5 then 'Low Engagement'
            when time_spent_minutes > 0 then 'Minimal Engagement'
            else 'No Engagement'
        end as engagement_tier,
        
        -- Date dimensions for reporting
        date_trunc('month', enrollment_date) as enrollment_month,
        date_trunc('quarter', enrollment_date) as enrollment_quarter,
        date_trunc('year', enrollment_date) as enrollment_year,
        
        case 
            when completion_date is not null then date_trunc('month', completion_date)
            else null
        end as completion_month,
        
        created_at,
        updated_at,
        processed_at,
        current_timestamp() as dw_created_at,
        current_timestamp() as dw_updated_at
        
    from learning_data
)

select * from fact_learning