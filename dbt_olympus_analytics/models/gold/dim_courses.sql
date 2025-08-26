{{ config(
    materialized='table',
    schema='gold'
) }}

-- Gold layer dimension table for courses
-- Business-ready course dimension for analytics

with courses as (
    select
        course_id,
        course_name,
        course_description,
        category,
        difficulty_level,
        duration_hours,
        instructor_name,
        created_date,
        last_updated,
        is_active,
        course_price
    from {{ ref('stg_disco_courses') }}
),

final_courses as (
    select
        course_id,
        course_name,
        course_description,
        category,
        difficulty_level,
        duration_hours,
        instructor_name,
        created_date,
        last_updated,
        is_active,
        course_price,
        
        -- Business classifications
        case 
            when is_active = true then 'Active'
            when is_active = false then 'Inactive'
            else 'Unknown'
        end as course_status_category,
        
        case 
            when difficulty_level = 'Beginner' then 1
            when difficulty_level = 'Intermediate' then 2
            when difficulty_level = 'Advanced' then 3
            else 0
        end as difficulty_level_numeric,
        
        case 
            when duration_hours <= 2 then 'Short (≤2h)'
            when duration_hours <= 8 then 'Medium (2-8h)'
            when duration_hours <= 20 then 'Long (8-20h)'
            else 'Extended (>20h)'
        end as duration_category,
        
        'Not Available' as completion_rate_tier,
        
        'Not Rated' as rating_tier,
        
        'Not Available' as popularity_tier,
        
        null as created_at,
        null as updated_at,
        current_timestamp() as dw_created_at,
        current_timestamp() as dw_updated_at
        
    from courses
)

select * from final_courses