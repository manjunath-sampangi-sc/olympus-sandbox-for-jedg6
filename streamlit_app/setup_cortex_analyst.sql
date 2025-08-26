-- =====================================================
-- Snowflake Cortex AI Analyst Configuration Script
-- =====================================================
-- This script sets up Cortex AI Analyst for Olympus Analytics
-- Cortex Analyst provides natural language querying capabilities
-- over your data with semantic understanding

-- =====================================================
-- STEP 1: Check Cortex AI Analyst Availability
-- =====================================================

-- Check if Cortex AI Analyst is available
-- Note: This requires Cortex AI to be enabled in your account
SELECT SYSTEM$CORTEX_ANALYST_AVAILABLE() as analyst_available;

-- Check available Cortex models (including Analyst)
SELECT SYSTEM$GET_CORTEX_MODELS() as available_models;

-- Check current account and role
SELECT 
    CURRENT_ACCOUNT() as account_id,
    CURRENT_ROLE() as current_role,
    CURRENT_USER() as current_user,
    CURRENT_WAREHOUSE() as current_warehouse;

-- =====================================================
-- STEP 2: Enable Cortex AI Analyst (ACCOUNTADMIN Required)
-- =====================================================

-- Switch to ACCOUNTADMIN role
USE ROLE ACCOUNTADMIN;

-- Enable Cortex AI Analyst for the account
-- Note: This may require contacting Snowflake support first
ALTER ACCOUNT SET CORTEX_ANALYST_ENABLED = TRUE;

-- Grant Cortex Analyst permissions to roles
GRANT USAGE ON INTEGRATION SNOWFLAKE.CORTEX TO ROLE OLYMPUS_CONTRACTOR;
GRANT USAGE ON INTEGRATION SNOWFLAKE.CORTEX TO ROLE SYSADMIN;

-- Grant specific Cortex Analyst functions
GRANT EXECUTE ON FUNCTION SNOWFLAKE.CORTEX.ANALYST TO ROLE OLYMPUS_CONTRACTOR;
GRANT EXECUTE ON FUNCTION SNOWFLAKE.CORTEX.ANALYST TO ROLE SYSADMIN;

-- Switch back to working role
USE ROLE SYSADMIN;
USE DATABASE OLYMPUS_ANALYTICS;
USE SCHEMA GOLD;
USE WAREHOUSE XS_WAREHOUSE;

-- =====================================================
-- STEP 3: Create Semantic Model for Cortex Analyst
-- =====================================================

-- Create a semantic model that describes our data structure
-- This helps Cortex Analyst understand the business context

CREATE OR REPLACE SEMANTIC MODEL olympus_analytics_model
AS (
    -- Sales Performance Facts
    SELECT 
        'sales_performance' as entity_type,
        'FACT_SALES_PERFORMANCE' as table_name,
        'Sales deals and performance metrics' as description,
        OBJECT_CONSTRUCT(
            'deal_id', 'Unique identifier for each sales deal',
            'sales_rep', 'Name of the sales representative',
            'client_name', 'Name of the client or prospect',
            'deal_name', 'Name or title of the deal',
            'amount', 'Deal value in USD',
            'stage', 'Current stage of the deal (Prospecting, Qualification, Proposal, Negotiation, Closed Won, Closed Lost)',
            'probability', 'Probability of closing the deal (0-100%)',
            'close_date', 'Expected or actual close date',
            'created_date', 'Date when the deal was created'
        ) as column_descriptions
    
    UNION ALL
    
    -- Learning Analytics Facts
    SELECT 
        'learning_analytics' as entity_type,
        'FACT_LEARNING_ANALYTICS' as table_name,
        'Training and course completion data' as description,
        OBJECT_CONSTRUCT(
            'enrollment_id', 'Unique identifier for each course enrollment',
            'user_id', 'Identifier for the learner',
            'course_id', 'Identifier for the course',
            'enrollment_date', 'Date when user enrolled in the course',
            'completion_date', 'Date when user completed the course',
            'status', 'Enrollment status (Enrolled, In Progress, Completed, Dropped)',
            'progress_percentage', 'Completion progress (0-100%)',
            'score', 'Final score or grade achieved'
        ) as column_descriptions
    
    UNION ALL
    
    -- User Dimension
    SELECT 
        'users' as entity_type,
        'DIM_USERS' as table_name,
        'User profiles and demographics' as description,
        OBJECT_CONSTRUCT(
            'user_id', 'Unique identifier for each user',
            'user_name', 'Full name of the user',
            'email', 'Email address',
            'department', 'Department or team',
            'role', 'Job role or title',
            'hire_date', 'Date when user was hired',
            'status', 'Employment status (Active, Inactive)'
        ) as column_descriptions
    
    UNION ALL
    
    -- Course Dimension
    SELECT 
        'courses' as entity_type,
        'DIM_COURSES' as table_name,
        'Course catalog and details' as description,
        OBJECT_CONSTRUCT(
            'course_id', 'Unique identifier for each course',
            'course_name', 'Name of the course',
            'category', 'Course category or subject area',
            'duration_hours', 'Expected duration in hours',
            'difficulty_level', 'Difficulty level (Beginner, Intermediate, Advanced)',
            'created_date', 'Date when course was created'
        ) as column_descriptions
);

-- =====================================================
-- STEP 4: Create Business Context for Cortex Analyst
-- =====================================================

-- Create a view that provides business context
CREATE OR REPLACE VIEW CORTEX_ANALYST_CONTEXT AS
SELECT 
    'Olympus Analytics Business Context' as context_name,
    'This is a sales and training analytics platform that tracks:' ||
    '\n- Sales performance: deals, revenue, sales rep performance' ||
    '\n- Training analytics: course completions, user progress, learning outcomes' ||
    '\n- Key metrics: conversion rates, completion rates, revenue trends' ||
    '\n- Time periods: data spans from 2023 to current date' ||
    '\n- Users: sales representatives, learners, managers' as business_description,
    
    'Common questions include:' ||
    '\n- What is our sales performance this quarter?' ||
    '\n- Which courses have the highest completion rates?' ||
    '\n- How are our sales reps performing?' ||
    '\n- What is the correlation between training and sales performance?' ||
    '\n- Show me revenue trends over time' as common_queries,
    
    'Key business rules:' ||
    '\n- Deal stages: Prospecting → Qualification → Proposal → Negotiation → Closed Won/Lost' ||
    '\n- Course status: Enrolled → In Progress → Completed/Dropped' ||
    '\n- Revenue is measured in USD' ||
    '\n- Completion rates are calculated as percentage of enrolled users who completed' as business_rules;

-- =====================================================
-- STEP 5: Test Cortex Analyst Functionality
-- =====================================================

-- Test 1: Basic Analyst availability
SELECT SNOWFLAKE.CORTEX.ANALYST(
    'What tables are available in this database?',
    'OLYMPUS_ANALYTICS.GOLD'
) as analyst_response;

-- Test 2: Sales performance query
SELECT SNOWFLAKE.CORTEX.ANALYST(
    'What is our total sales revenue and how many deals do we have?',
    'OLYMPUS_ANALYTICS.GOLD',
    OBJECT_CONSTRUCT(
        'semantic_model', 'olympus_analytics_model',
        'context', 'Sales performance analysis for Olympus Analytics'
    )
) as sales_analysis;

-- Test 3: Training analytics query
SELECT SNOWFLAKE.CORTEX.ANALYST(
    'What is the average course completion rate and which courses are most popular?',
    'OLYMPUS_ANALYTICS.GOLD',
    OBJECT_CONSTRUCT(
        'semantic_model', 'olympus_analytics_model',
        'context', 'Learning analytics for training programs'
    )
) as training_analysis;

-- Test 4: Complex business question
SELECT SNOWFLAKE.CORTEX.ANALYST(
    'Show me the top performing sales reps and their deal conversion rates',
    'OLYMPUS_ANALYTICS.GOLD',
    OBJECT_CONSTRUCT(
        'semantic_model', 'olympus_analytics_model',
        'context', 'Sales rep performance analysis'
    )
) as performance_analysis;

-- =====================================================
-- STEP 6: Create Helper Functions for Streamlit Integration
-- =====================================================

-- Create a stored procedure for easy Analyst queries from Streamlit
CREATE OR REPLACE PROCEDURE ASK_CORTEX_ANALYST(
    QUESTION STRING,
    CONTEXT STRING DEFAULT 'General business analytics query'
)
RETURNS STRING
LANGUAGE SQL
AS
$$
DECLARE
    result STRING;
BEGIN
    SELECT SNOWFLAKE.CORTEX.ANALYST(
        :QUESTION,
        'OLYMPUS_ANALYTICS.GOLD',
        OBJECT_CONSTRUCT(
            'semantic_model', 'olympus_analytics_model',
            'context', :CONTEXT
        )
    ) INTO :result;
    
    RETURN result;
END;
$$;

-- Test the stored procedure
CALL ASK_CORTEX_ANALYST(
    'What is our sales performance this month?',
    'Monthly sales performance review'
);

-- =====================================================
-- STEP 7: Validation and Verification
-- =====================================================

-- Check that semantic model was created
SHOW SEMANTIC MODELS;

-- Verify permissions
SHOW GRANTS TO ROLE OLYMPUS_CONTRACTOR;
SHOW GRANTS TO ROLE SYSADMIN;

-- Check available Cortex functions
SHOW FUNCTIONS LIKE '%CORTEX%';

-- Verify data availability for Analyst
SELECT 
    'FACT_SALES_PERFORMANCE' as table_name,
    COUNT(*) as row_count,
    MIN(CREATED_DATE) as earliest_date,
    MAX(CREATED_DATE) as latest_date
FROM FACT_SALES_PERFORMANCE
UNION ALL
SELECT 
    'FACT_LEARNING_ANALYTICS' as table_name,
    COUNT(*) as row_count,
    MIN(ENROLLMENT_DATE) as earliest_date,
    MAX(ENROLLMENT_DATE) as latest_date
FROM FACT_LEARNING_ANALYTICS;

-- =====================================================
-- STEP 8: Sample Business Questions for Testing
-- =====================================================

/*
Once Cortex Analyst is working, test these business questions:

1. "What is our total revenue this quarter?"
2. "Which sales rep has the highest conversion rate?"
3. "What are the top 5 courses by completion rate?"
4. "Show me deals that are likely to close this month"
5. "What is the average time to complete training programs?"
6. "Which department has the most active learners?"
7. "What is the correlation between training completion and sales performance?"
8. "Show me revenue trends over the last 6 months"
9. "Which deals are at risk of not closing?"
10. "What training programs should we prioritize based on completion rates?"
*/

-- =====================================================
-- COMPLETION STATUS
-- =====================================================

SELECT 
    'Cortex AI Analyst setup completed!' as status,
    'Next steps:' ||
    '\n1. Verify Cortex AI is enabled in your account' ||
    '\n2. Test the sample queries above' ||
    '\n3. Integrate with Streamlit application' ||
    '\n4. Train users on natural language querying' as next_steps;