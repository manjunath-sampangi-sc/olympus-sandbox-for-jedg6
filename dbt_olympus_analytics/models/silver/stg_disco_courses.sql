{{ config(
    materialized='table',
    schema='bronze'
) }}

-- Staging model for Disco LMS courses data
-- This model pulls raw course data and applies basic cleaning

with source_data as (
    select
        course_id,
        course_name,
        course_description,
        course_category,
        duration_hours,
        difficulty_level,
        created_date,
        last_updated,
        is_active,
        course_price,
        instructor_name
    from {{ source('disco', 'disco_courses') }}
),

cleaned_data as (
    select
        course_id,
        trim(course_name) as course_name,
        trim(course_description) as course_description,
        trim(course_category) as category,
        trim(difficulty_level) as difficulty_level,
        duration_hours,
        trim(instructor_name) as instructor_name,
        created_date,
        last_updated,
        is_active,
        course_price
    from source_data
    where course_id is not null
      and course_name is not null
)

select * from cleaned_data