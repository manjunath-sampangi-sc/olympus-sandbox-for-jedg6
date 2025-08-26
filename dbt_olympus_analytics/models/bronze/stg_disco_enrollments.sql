{{ config(
    materialized='table',
    schema='bronze'
) }}

-- Staging model for Disco LMS enrollments data
-- This model pulls raw enrollment data and applies basic cleaning

with source_data as (
    select
        enrollment_id,
        user_id,
        course_id,
        enrollment_date,
        completion_date,
        progress_percentage,
        status,
        last_accessed,
        null as time_spent_minutes,
        null as grade,
        null as certificate_issued,
        null as enrollment_source,
        null as instructor_id,
        null as cohort_id,
        null as created_at,
        null as updated_at
    from {{ source('disco', 'disco_enrollments') }}
),

cleaned_data as (
    select
        enrollment_id,
        user_id,
        course_id,
        enrollment_date::date as enrollment_date,
        completion_date::date as completion_date,
        progress_percentage,
        trim(status) as status,
        last_accessed::date as last_accessed_date,
        time_spent_minutes,
        grade,
        certificate_issued::boolean as certificate_issued,
        trim(enrollment_source) as enrollment_source,
        instructor_id,
        cohort_id,
        created_at::timestamp as created_at,
        updated_at::timestamp as updated_at
    from source_data
    where enrollment_id is not null
      and user_id is not null
      and course_id is not null
      and enrollment_date is not null
)

select * from cleaned_data