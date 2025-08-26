{{ config(
    materialized='table',
    schema='gold'
) }}

-- Gold layer fact table for sales performance
-- Business-ready sales metrics and KPIs

with deals_data as (
    select
        deal_id,
        deal_name,
        deal_stage,
        deal_amount,
        close_date,
        probability,
        deal_type,
        null as lead_source,
        owner_id,
        null as company_id,
        company_name,
        industry,
        company_size,
        annual_revenue,
        website,
        country,
        state,
        city,
        contact_id,
        contact_email,
        contact_first_name,
        contact_last_name,
        contact_job_title,
        deal_status,
        close_date_category,
        weighted_amount,
        created_at,
        updated_at,
        processed_at
    from {{ ref('int_deals_enriched') }}
),

fact_sales as (
    select
        deal_id,
        deal_name,
        deal_stage,
        deal_amount,
        close_date,
        probability,
        deal_type,
        null as lead_source,
        owner_id,
        null as company_id,
        company_name,
        industry,
        company_size,
        annual_revenue,
        website,
        country,
        state,
        city,
        contact_id,
        contact_email,
        contact_first_name,
        contact_last_name,
        contact_job_title,
        deal_status,
        close_date_category,
        weighted_amount,
        
        -- Key business metrics
        case when deal_status = 'Won' then 1 else 0 end as is_won,
        case when deal_status = 'Lost' then 1 else 0 end as is_lost,
        case when deal_status = 'Open' then 1 else 0 end as is_open,
        
        case when deal_status = 'Won' then deal_amount else 0 end as won_amount,
        case when deal_status = 'Lost' then deal_amount else 0 end as lost_amount,
        case when deal_status = 'Open' then deal_amount else 0 end as pipeline_amount,
        
        -- Time-based metrics
        datediff('day', created_at::date, coalesce(close_date, current_date())) as sales_cycle_days,
        
        case 
            when close_date < current_date() and deal_status = 'Open' then 1 
            else 0 
        end as is_overdue,
        
        -- Deal size categorization
        case 
            when deal_amount >= 100000 then 'Enterprise (≥$100K)'
            when deal_amount >= 50000 then 'Large ($50K-$100K)'
            when deal_amount >= 25000 then 'Medium ($25K-$50K)'
            when deal_amount >= 10000 then 'Small ($10K-$25K)'
            else 'Micro (<$10K)'
        end as deal_size_tier,
        
        -- Probability tiers
        case 
            when probability >= 90 then 'Very High (90%+)'
            when probability >= 75 then 'High (75-90%)'
            when probability >= 50 then 'Medium (50-75%)'
            when probability >= 25 then 'Low (25-50%)'
            else 'Very Low (<25%)'
        end as probability_tier,
        
        -- Company size standardization
        case 
            when company_size ilike '%enterprise%' or company_size ilike '%large%' then 'Enterprise'
            when company_size ilike '%medium%' or company_size ilike '%mid%' then 'Mid-Market'
            when company_size ilike '%small%' or company_size ilike '%startup%' then 'Small Business'
            else 'Unknown'
        end as company_size_category,
        
        -- Revenue tiers
        case 
            when annual_revenue >= 1000000000 then 'Billion+ ($1B+)'
            when annual_revenue >= 100000000 then 'Large ($100M-$1B)'
            when annual_revenue >= 10000000 then 'Medium ($10M-$100M)'
            when annual_revenue >= 1000000 then 'Small ($1M-$10M)'
            when annual_revenue > 0 then 'Micro (<$1M)'
            else 'Unknown'
        end as revenue_tier,
        
        -- Date dimensions for reporting
        date_trunc('month', close_date) as close_month,
        date_trunc('quarter', close_date) as close_quarter,
        date_trunc('year', close_date) as close_year,
        
        date_trunc('month', created_at::date) as created_month,
        date_trunc('quarter', created_at::date) as created_quarter,
        date_trunc('year', created_at::date) as created_year,
        
        -- Sales stage progression
        case 
            when deal_stage ilike '%prospect%' or deal_stage ilike '%lead%' then 1
            when deal_stage ilike '%qualify%' or deal_stage ilike '%discovery%' then 2
            when deal_stage ilike '%demo%' or deal_stage ilike '%presentation%' then 3
            when deal_stage ilike '%proposal%' or deal_stage ilike '%negotiation%' then 4
            when deal_stage ilike '%contract%' or deal_stage ilike '%decision%' then 5
            when deal_stage ilike '%closed%' then 6
            else 0
        end as stage_order,
        
        created_at,
        updated_at,
        processed_at,
        current_timestamp() as dw_created_at,
        current_timestamp() as dw_updated_at
        
    from deals_data
)

select * from fact_sales