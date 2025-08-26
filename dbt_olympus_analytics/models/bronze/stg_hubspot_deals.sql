{{ config(
    materialized='table',
    schema='bronze'
) }}

-- Staging model for HubSpot deals data
-- This model pulls raw deal data and applies basic cleaning

with source_data as (
    select
        deal_id,
        deal_name,
        deal_stage,
        deal_amount,
        close_date,
        probability,
        deal_type,
        null as lead_source,
        null as owner_id,
        null as company_id,
        null as contact_id,
        null as created_at,
        null as updated_at
    from {{ source('hubspot', 'hubspot_deals') }}
),

cleaned_data as (
    select
        deal_id,
        trim(deal_name) as deal_name,
        trim(deal_stage) as deal_stage,
        trim(deal_type) as deal_type,

        deal_amount as amount,
        close_date::date as close_date,
        null as created_date,
        null as last_activity_date,
        probability,
        null as deal_owner,
        null as contact_id,
        null as currency,
        null as forecast_category,
        null as next_step,
        null as created_at,
        null as updated_at
    from source_data
    where deal_id is not null
      and deal_name is not null
)

select * from cleaned_data