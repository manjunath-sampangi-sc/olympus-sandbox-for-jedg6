{{ config(
    materialized='table',
    schema='silver'
) }}

-- Silver model for Disco LMS enrollments data
-- This model cleans and standardizes enrollment data from Bronze layer

with source_data as (
    select
        enrollment_id,
        member_id,
        product_id,
        community_id,
        enrolled_at,
        unenrolled_at,
        status,
        progress_percentage,
        completion_date,
        enrollment_data,
        _loaded_at,
        _source
    from {{ source('disco', 'disco_enrollments') }}
),

cleaned_data as (
    select
        enrollment_id,
        member_id,
        product_id,
        community_id,
        enrolled_at::timestamp as enrolled_at,
        unenrolled_at::timestamp as unenrolled_at,
        lower(trim(status)) as status,
        coalesce(progress_percentage, 0.0) as progress_percentage,
        completion_date::timestamp as completion_date,
        enrollment_data,
        _loaded_at::timestamp as loaded_at,
        _source
    from source_data
    where enrollment_id is not null
      and member_id is not null
      and product_id is not null
)

select
    enrollment_id,
    member_id,
    product_id,
    community_id,
    enrolled_at,
    unenrolled_at,
    status,
    progress_percentage,
    completion_date,
    enrollment_data,
    loaded_at,
    _source,
    
    -- Derived fields
    case 
        when status = 'active' and unenrolled_at is null then true
        else false
    end as is_currently_enrolled,
    
    case
        when completion_date is not null then true
        when progress_percentage >= 100 then true
        else false
    end as is_completed,
    
    case
        when completion_date is not null or progress_percentage >= 100 then 'Completed'
        when progress_percentage >= 75 then 'Near Completion'
        when progress_percentage >= 25 then 'In Progress'
        when progress_percentage > 0 then 'Started'
        else 'Not Started'
    end as enrollment_status_category,
    
    case
        when enrolled_at >= dateadd(month, -1, current_date()) then 'This Month'
        when enrolled_at >= dateadd(month, -3, current_date()) then 'Last 3 Months'
        when enrolled_at >= dateadd(month, -6, current_date()) then 'Last 6 Months'
        when enrolled_at >= dateadd(year, -1, current_date()) then 'This Year'
        else 'Older'
    end as enrollment_recency,
    
    datediff(day, enrolled_at, coalesce(completion_date, current_date())) as days_to_completion,
    
    case
        when completion_date is not null then
            datediff(day, enrolled_at, completion_date)
        else null
    end as actual_completion_days,
    
    current_timestamp() as dbt_updated_at
    
from cleaned_data