-- Snowflake Cortex AI Configuration Script
-- This script sets up the necessary permissions and tests Cortex AI functionality
-- for the Olympus Analytics project

-- =====================================================
-- STEP 1: Check Current Cortex AI Availability
-- =====================================================

-- Check if Cortex AI is available in your account
SELECT SYSTEM$GET_CORTEX_MODELS() as available_models;

-- Check current role and privileges
SELECT CURRENT_ROLE(), CURRENT_USER(), CURRENT_WAREHOUSE();

-- =====================================================
-- STEP 2: Grant Cortex AI Permissions
-- =====================================================

-- Switch to ACCOUNTADMIN role (required for granting Cortex permissions)
-- Note: You may need to run this as ACCOUNTADMIN
USE ROLE ACCOUNTADMIN;

-- Grant CORTEX usage to the OLYMPUS_CONTRACTOR role
GRANT USAGE ON INTEGRATION SNOWFLAKE.CORTEX TO ROLE OLYMPUS_CONTRACTOR;

-- Grant access to specific Cortex functions
GRANT EXECUTE ON FUNCTION SNOWFLAKE.CORTEX.COMPLETE TO ROLE OLYMPUS_CONTRACTOR;
GRANT EXECUTE ON FUNCTION SNOWFLAKE.CORTEX.EXTRACT_ANSWER TO ROLE OLYMPUS_CONTRACTOR;
GRANT EXECUTE ON FUNCTION SNOWFLAKE.CORTEX.SENTIMENT TO ROLE OLYMPUS_CONTRACTOR;
GRANT EXECUTE ON FUNCTION SNOWFLAKE.CORTEX.SUMMARIZE TO ROLE OLYMPUS_CONTRACTOR;
GRANT EXECUTE ON FUNCTION SNOWFLAKE.CORTEX.TRANSLATE TO ROLE OLYMPUS_CONTRACTOR;

-- Switch back to the working role
USE ROLE OLYMPUS_CONTRACTOR;
USE WAREHOUSE XS_WAREHOUSE;
USE DATABASE OLYMPUS_ANALYTICS;
USE SCHEMA GOLD;

-- =====================================================
-- STEP 3: Test Basic Cortex AI Functionality
-- =====================================================

-- Test 1: Basic text completion
SELECT SNOWFLAKE.CORTEX.COMPLETE(
    'mixtral-8x7b',
    'Hello, I am testing Snowflake Cortex AI. Please respond with a brief confirmation that you are working.'
) as test_response;

-- Test 2: Sentiment analysis
SELECT SNOWFLAKE.CORTEX.SENTIMENT(
    'I love using Snowflake Cortex AI for analytics!'
) as sentiment_score;

-- Test 3: Text summarization
SELECT SNOWFLAKE.CORTEX.SUMMARIZE(
    'Olympus Analytics is a comprehensive business intelligence platform that combines sales performance tracking with learning management system analytics. The platform provides real-time dashboards, AI-powered insights, and data-driven recommendations to help organizations optimize their sales processes and training programs.'
) as summary_text;

-- =====================================================
-- STEP 4: Test Analytics-Specific Queries
-- =====================================================

-- Test 4: Generate insights from sales data
SELECT SNOWFLAKE.CORTEX.COMPLETE(
    'mixtral-8x7b',
    CONCAT(
        'Based on this sales data summary: We have ',
        (SELECT COUNT(*) FROM FACT_SALES_PERFORMANCE),
        ' sales records with an average deal value of $',
        (SELECT ROUND(AVG(DEAL_VALUE), 2) FROM FACT_SALES_PERFORMANCE),
        '. Please provide 3 key insights about this sales performance.'
    )
) as sales_insights;

-- Test 5: Generate training recommendations
SELECT SNOWFLAKE.CORTEX.COMPLETE(
    'mixtral-8x7b',
    CONCAT(
        'Based on this learning data: We have ',
        (SELECT COUNT(*) FROM FACT_LEARNING_ANALYTICS),
        ' learning records with an average completion rate of ',
        (SELECT ROUND(AVG(CASE WHEN STATUS = 'Completed' THEN 100 ELSE 0 END), 1) FROM FACT_LEARNING_ANALYTICS),
        '%. Please suggest 3 ways to improve training effectiveness.'
    )
) as training_recommendations;

-- =====================================================
-- STEP 5: Test Error Handling
-- =====================================================

-- Test 6: Handle invalid model name (should fail gracefully)
SELECT 
    TRY_CAST(
        SNOWFLAKE.CORTEX.COMPLETE(
            'invalid-model',
            'This should fail'
        ) AS STRING
    ) as error_test;

-- =====================================================
-- STEP 6: Performance and Limits Testing
-- =====================================================

-- Test 7: Check response time for typical queries
SELECT 
    CURRENT_TIMESTAMP() as start_time,
    SNOWFLAKE.CORTEX.COMPLETE(
        'mixtral-8x7b',
        'What are the key benefits of using AI in business analytics? Please provide a concise answer.'
    ) as ai_response,
    CURRENT_TIMESTAMP() as end_time;

-- =====================================================
-- STEP 7: Validation Queries
-- =====================================================

-- Check if all required tables exist for AI queries
SELECT 
    table_name,
    row_count
FROM information_schema.tables 
WHERE table_schema = 'GOLD' 
    AND table_name IN ('FACT_SALES_PERFORMANCE', 'FACT_LEARNING_ANALYTICS', 'DIM_USERS', 'DIM_COURSES')
ORDER BY table_name;

-- Verify data freshness for AI context
SELECT 
    'FACT_SALES_PERFORMANCE' as table_name,
    MIN(CREATED_DATE) as oldest_record,
    MAX(CREATED_DATE) as newest_record,
    COUNT(*) as total_records
FROM FACT_SALES_PERFORMANCE
UNION ALL
SELECT 
    'FACT_LEARNING_ANALYTICS' as table_name,
    MIN(ENROLLMENT_DATE) as oldest_record,
    MAX(ENROLLMENT_DATE) as newest_record,
    COUNT(*) as total_records
FROM FACT_LEARNING_ANALYTICS;

-- =====================================================
-- STEP 8: Final Configuration Check
-- =====================================================

-- Verify all permissions are correctly set
SHOW GRANTS TO ROLE OLYMPUS_CONTRACTOR;

-- Test final integration query (similar to what the app will use)
SELECT SNOWFLAKE.CORTEX.COMPLETE(
    'mixtral-8x7b',
    'You are an AI assistant for Olympus Analytics. A user asks: "What is our current sales performance?" Based on the context that we have sales and training data available, provide a helpful response about what kind of analysis you can perform.'
) as final_test_response;

-- =====================================================
-- COMPLETION MESSAGE
-- =====================================================

SELECT 'Cortex AI configuration and testing completed successfully!' as status_message;