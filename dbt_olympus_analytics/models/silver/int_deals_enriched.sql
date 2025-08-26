{{ config(
    materialized='table',
    schema='silver'
) }}

-- Silver layer model for enriched deals
-- Combines HubSpot deals with company information for enhanced analytics

with deals as (
    select
        deal_id,
        deal_name,
        deal_stage,
        amount as deal_amount,
        close_date,
        probability,
        deal_type,
        null as owner_id,
        null as contact_id,
        created_at,
        updated_at
    from {{ ref('stg_hubspot_deals') }}
),

contacts as (
    select
        contact_id,
        email as contact_email,
        first_name as contact_first_name,
        last_name as contact_last_name,
        null as contact_job_title
    from {{ ref('stg_hubspot_contacts') }}
),

enriched_deals as (
    select
        d.deal_id,
        d.deal_name,
        d.deal_stage,
        d.deal_amount,
        d.close_date,
        d.probability,
        d.deal_type,
        d.owner_id,
        
        -- Company information (not available)
        null as company_id,
        null as company_name,
        null as industry,
        null as company_size,
        null as annual_revenue,
        null as website,
        null as country,
        null as state,
        null as city,
        
        -- Contact information
        ct.contact_id,
        ct.contact_email,
        ct.contact_first_name,
        ct.contact_last_name,
        ct.contact_job_title,
        
        -- Calculated fields
        case 
            when d.deal_stage in ('Closed Won', 'Closed-Won') then 'Won'
            when d.deal_stage in ('Closed Lost', 'Closed-Lost') then 'Lost'
            else 'Open'
        end as deal_status,
        
        case 
            when d.close_date < current_date() then 'Past Due'
            when d.close_date <= current_date() + interval '30 days' then 'This Month'
            when d.close_date <= current_date() + interval '90 days' then 'This Quarter'
            else 'Future'
        end as close_date_category,
        
        d.deal_amount * (d.probability / 100.0) as weighted_amount,
        
        d.created_at,
        d.updated_at,
        current_timestamp() as processed_at
        
    from deals d
    left join contacts ct on d.contact_id = ct.contact_id
)

select * from enriched_deals