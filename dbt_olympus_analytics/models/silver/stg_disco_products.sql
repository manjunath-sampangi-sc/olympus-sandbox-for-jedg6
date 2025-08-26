{{ config(
    materialized='table',
    schema='silver'
) }}

-- Silver model for Disco LMS products/courses data
-- This model cleans and standardizes product data from Bronze layer

with source_data as (
    select
        product_id,
        product_name,
        product_type,
        description,
        price,
        currency,
        created_at,
        updated_at,
        status,
        metadata,
        _loaded_at,
        _source
    from {{ source('disco', 'disco_products') }}
),

cleaned_data as (
    select
        product_id,
        trim(product_name) as product_name,
        lower(trim(product_type)) as product_type,
        trim(description) as description,
        coalesce(price, 0.0) as price,
        upper(trim(currency)) as currency,
        created_at::timestamp as created_at,
        updated_at::timestamp as updated_at,
        lower(trim(status)) as status,
        metadata,
        _loaded_at::timestamp as loaded_at,
        _source
    from source_data
    where product_id is not null
      and product_name is not null
      and product_name != ''
)

select
    product_id,
    product_name,
    product_type,
    description,
    price,
    currency,
    created_at,
    updated_at,
    status,
    metadata,
    loaded_at,
    _source,
    
    -- Derived fields
    case 
        when status = 'active' then true
        else false
    end as is_active,
    
    case
        when price = 0 then 'Free'
        when price <= 50 then 'Low Cost'
        when price <= 200 then 'Medium Cost'
        else 'Premium'
    end as price_category,
    
    case
        when lower(product_name) like '%home%' then true
        else false
    end as is_home_course,
    
    case
        when lower(product_name) like '%basic%' or lower(product_name) like '%intro%' then 'Beginner'
        when lower(product_name) like '%advanced%' or lower(product_name) like '%expert%' then 'Advanced'
        else 'Intermediate'
    end as difficulty_level,
    
    current_timestamp() as dbt_updated_at
    
from cleaned_data