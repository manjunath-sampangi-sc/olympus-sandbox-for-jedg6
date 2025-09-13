{{ config(
    materialized='table',
    schema='gold'
) }}

-- Gold layer KPI table for member billing brackets
-- This model implements the billing bracket logic:
-- $0 = No course enrollments
-- $10 = Only course is "Home"
-- $50 = 2+ courses OR one course including "Home"

with members as (
    select
        member_id,
        email,
        full_name,
        community_id,
        is_active,
        joined_at
    from {{ ref('stg_disco_members') }}
    where is_active = true
),

communities as (
    select
        community_id,
        community_name
    from {{ ref('stg_disco_communities') }}
    where is_active = true
),

products as (
    select
        product_id,
        product_name,
        is_home_course,
        is_active
    from {{ ref('stg_disco_products') }}
    where is_active = true
),

active_enrollments as (
    select
        e.member_id,
        e.product_id,
        e.community_id,
        e.enrolled_at,
        e.is_currently_enrolled,
        e.is_completed,
        p.product_name,
        p.is_home_course,
        -- Generate monthly billing periods
        date_trunc('month', e.enrolled_at) as billing_month
    from {{ ref('slv_disco_enrollments') }} e
    inner join products p on e.product_id = p.product_id
    where e.is_currently_enrolled = true
       or e.is_completed = true
),

member_course_summary as (
    select
        member_id,
        community_id,
        billing_month,
        count(distinct product_id) as course_count_active,
        max(case when is_home_course then 1 else 0 end) as has_home_course,
        listagg(distinct product_name, ', ') within group (order by product_name) as enrolled_courses
    from active_enrollments
    group by member_id, community_id, billing_month
),

billing_logic as (
    select
        mcs.*,
        case
            when course_count_active = 0 then '$0'
            when course_count_active = 1 and has_home_course = 1 then '$10'
            when course_count_active >= 2 then '$50'
            when course_count_active = 1 and has_home_course = 0 then '$50'
            else '$0'
        end as billing_bracket,
        
        case
            when course_count_active = 0 then 0.00
            when course_count_active = 1 and has_home_course = 1 then 10.00
            when course_count_active >= 2 then 50.00
            when course_count_active = 1 and has_home_course = 0 then 50.00
            else 0.00
        end as monthly_amount
    from member_course_summary mcs
),

-- Generate all members for all billing months (to capture $0 brackets)
all_member_months as (
    select distinct
        m.member_id,
        m.community_id,
        billing_months.billing_month
    from members m
    cross join (
        select distinct billing_month
        from active_enrollments
        where billing_month >= dateadd(month, -12, current_date())
    ) billing_months
    where m.joined_at <= last_day(billing_months.billing_month)
),

final_billing_data as (
    select
        amm.member_id,
        amm.community_id,
        amm.billing_month,
        coalesce(bl.course_count_active, 0) as course_count_active,
        coalesce(bl.has_home_course, 0) as has_home_course,
        coalesce(bl.billing_bracket, '$0') as billing_bracket,
        coalesce(bl.monthly_amount, 0.00) as monthly_amount,
        coalesce(bl.enrolled_courses, 'No active enrollments') as enrolled_courses
    from all_member_months amm
    left join billing_logic bl on amm.member_id = bl.member_id 
                               and amm.community_id = bl.community_id
                               and amm.billing_month = bl.billing_month
)

select
    fbd.member_id,
    m.email,
    m.full_name as member_name,
    fbd.community_id,
    c.community_name as group_name,
    fbd.billing_month,
    fbd.course_count_active,
    case when fbd.has_home_course = 1 then true else false end as has_home_course,
    fbd.billing_bracket,
    fbd.monthly_amount,
    fbd.enrolled_courses,
    
    -- Additional metadata
    case
        when fbd.course_count_active = 0 then 'No Enrollments'
        when fbd.course_count_active = 1 and fbd.has_home_course = 1 then 'Home Course Only'
        when fbd.course_count_active = 1 and fbd.has_home_course = 0 then 'Single Non-Home Course'
        when fbd.course_count_active >= 2 and fbd.has_home_course = 1 then 'Multiple Courses (with Home)'
        when fbd.course_count_active >= 2 and fbd.has_home_course = 0 then 'Multiple Courses (no Home)'
        else 'Unknown'
    end as billing_category_description,
    
    current_timestamp() as dbt_updated_at,
    
    -- Generate unique key for the record
    concat(fbd.member_id, '_', fbd.community_id, '_', fbd.billing_month) as billing_record_key
    
from final_billing_data fbd
left join members m on fbd.member_id = m.member_id
left join communities c on fbd.community_id = c.community_id
where fbd.billing_month >= dateadd(month, -12, current_date())
order by fbd.billing_month desc, c.community_name, m.full_name