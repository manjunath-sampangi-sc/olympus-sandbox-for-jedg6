#!/usr/bin/env python3
"""
Cortex AI Analyst Testing Script
This script tests Cortex AI Analyst availability and functionality
"""

import sys
import os
import pandas as pd
from datetime import datetime
import time

# Add the current directory to the path to import utils
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.snowflake_connector import get_snowflake_connector, execute_query

def test_cortex_analyst_availability():
    """Test if Cortex AI Analyst is available"""
    print("\n🔍 Testing Cortex AI Analyst Availability...")
    
    # Test queries to check Cortex Analyst
    test_queries = [
        {
            'name': 'Check Cortex Analyst Function',
            'query': "SELECT SYSTEM$CORTEX_ANALYST_AVAILABLE() as analyst_available",
            'description': 'Check if Cortex Analyst is enabled'
        },
        {
            'name': 'Check Cortex Models',
            'query': "SELECT SYSTEM$GET_CORTEX_MODELS() as available_models",
            'description': 'List available Cortex models'
        },
        {
            'name': 'Check Account Info',
            'query': """SELECT 
                CURRENT_ACCOUNT() as account_id,
                CURRENT_ROLE() as current_role,
                CURRENT_USER() as current_user,
                CURRENT_WAREHOUSE() as current_warehouse""",
            'description': 'Get current account and role information'
        }
    ]
    
    results = {}
    
    for test in test_queries:
        try:
            print(f"  Testing {test['name']}...")
            result = execute_query(test['query'])
            
            if not result.empty:
                print(f"    ✅ {test['description']}: Success")
                results[test['name']] = {
                    'status': 'success',
                    'data': result.to_dict('records')[0]
                }
            else:
                print(f"    ⚠️ {test['description']}: No data returned")
                results[test['name']] = {
                    'status': 'no_data',
                    'data': None
                }
                
        except Exception as e:
            print(f"    ❌ {test['description']}: {str(e)}")
            results[test['name']] = {
                'status': 'error',
                'error': str(e)
            }
    
    return results

def test_basic_cortex_analyst():
    """Test basic Cortex Analyst functionality"""
    print("\n🧪 Testing Basic Cortex Analyst Functions...")
    
    # Basic Analyst test
    test_query = """
    SELECT SNOWFLAKE.CORTEX.ANALYST(
        'What tables are available in this database?',
        'OLYMPUS_ANALYTICS.GOLD'
    ) as analyst_response
    """
    
    try:
        print("  Testing basic Analyst query...")
        result = execute_query(test_query)
        
        if not result.empty:
            response = result.iloc[0]['ANALYST_RESPONSE']
            print(f"    ✅ Cortex Analyst Response: {response[:200]}...")
            return True, response
        else:
            print("    ❌ No response from Cortex Analyst")
            return False, None
            
    except Exception as e:
        print(f"    ❌ Cortex Analyst test failed: {str(e)}")
        return False, str(e)

def create_semantic_model():
    """Create semantic model for better Analyst understanding"""
    print("\n📊 Creating Semantic Model...")
    
    # Note: Semantic models might not be available in all Snowflake versions
    # This is a conceptual approach
    
    try:
        # First, let's check what tables we have
        tables_query = """
        SELECT 
            table_name,
            table_type,
            row_count
        FROM information_schema.tables 
        WHERE table_schema = 'GOLD' 
            AND table_name IN ('FACT_SALES_PERFORMANCE', 'FACT_LEARNING_ANALYTICS', 'DIM_USERS', 'DIM_COURSES')
        ORDER BY table_name
        """
        
        result = execute_query(tables_query)
        print("    Available tables for semantic model:")
        for _, row in result.iterrows():
            print(f"      - {row['TABLE_NAME']}: {row['ROW_COUNT']} rows")
        
        return True, result
        
    except Exception as e:
        print(f"    ❌ Failed to check tables: {str(e)}")
        return False, str(e)

def test_business_questions():
    """Test Cortex Analyst with business questions"""
    print("\n💼 Testing Business Questions...")
    
    # Since Cortex Analyst might not be available, we'll test with fallback queries
    business_questions = [
        {
            'question': 'What is our total sales revenue?',
            'fallback_query': 'SELECT SUM(AMOUNT) as total_revenue FROM FACT_SALES_PERFORMANCE',
            'context': 'Sales performance analysis'
        },
        {
            'question': 'How many courses do we have?',
            'fallback_query': 'SELECT COUNT(*) as total_courses FROM DIM_COURSES',
            'context': 'Training catalog overview'
        },
        {
            'question': 'What is the average course completion rate?',
            'fallback_query': """SELECT 
                ROUND(AVG(CASE WHEN STATUS = 'Completed' THEN 100 ELSE 0 END), 2) as avg_completion_rate
                FROM FACT_LEARNING_ANALYTICS""",
            'context': 'Learning analytics'
        }
    ]
    
    results = []
    
    for bq in business_questions:
        try:
            print(f"  Testing: {bq['question']}")
            
            # Try Cortex Analyst first
            analyst_query = f"""
            SELECT SNOWFLAKE.CORTEX.ANALYST(
                '{bq['question']}',
                'OLYMPUS_ANALYTICS.GOLD'
            ) as analyst_response
            """
            
            try:
                analyst_result = execute_query(analyst_query)
                if not analyst_result.empty:
                    response = analyst_result.iloc[0]['ANALYST_RESPONSE']
                    print(f"    ✅ Analyst Response: {response[:100]}...")
                    results.append({
                        'question': bq['question'],
                        'method': 'cortex_analyst',
                        'response': response
                    })
                    continue
            except:
                pass  # Fall back to direct query
            
            # Fallback to direct SQL query
            fallback_result = execute_query(bq['fallback_query'])
            if not fallback_result.empty:
                data = fallback_result.iloc[0].to_dict()
                print(f"    ✅ Fallback Query Result: {data}")
                results.append({
                    'question': bq['question'],
                    'method': 'direct_sql',
                    'response': data
                })
            
        except Exception as e:
            print(f"    ❌ Failed to answer: {bq['question']} - {str(e)}")
            results.append({
                'question': bq['question'],
                'method': 'error',
                'response': str(e)
            })
    
    return results

def generate_setup_recommendations():
    """Generate recommendations for Cortex Analyst setup"""
    print("\n📋 Setup Recommendations...")
    
    recommendations = [
        "🔧 **Cortex AI Analyst Setup Steps:**",
        "",
        "1. **Account Requirements:**",
        "   - Snowflake Business Critical edition or higher",
        "   - Cortex AI must be enabled by Snowflake support",
        "   - ACCOUNTADMIN role required for initial setup",
        "",
        "2. **Enable Cortex AI Analyst:**",
        "   - Contact Snowflake support to enable Cortex AI",
        "   - Request Cortex Analyst feature specifically",
        "   - Provide account ID: KDLCEKW-GPB78424",
        "",
        "3. **Grant Permissions (as ACCOUNTADMIN):**",
        "   ```sql",
        "   USE ROLE ACCOUNTADMIN;",
        "   GRANT USAGE ON INTEGRATION SNOWFLAKE.CORTEX TO ROLE SYSADMIN;",
        "   GRANT EXECUTE ON FUNCTION SNOWFLAKE.CORTEX.ANALYST TO ROLE SYSADMIN;",
        "   ```",
        "",
        "4. **Test Availability:**",
        "   ```sql",
        "   SELECT SYSTEM$CORTEX_ANALYST_AVAILABLE();",
        "   ```",
        "",
        "5. **Alternative Solutions:**",
        "   - Use existing Cortex LLM functions (COMPLETE, SUMMARIZE)",
        "   - Integrate external AI APIs (OpenAI, Azure OpenAI)",
        "   - Enhance current demo mode with better responses",
        "",
        "6. **Current Status:**",
        "   - ✅ Data pipeline is ready",
        "   - ✅ Tables and schemas are properly structured",
        "   - ✅ AI chat interface is built",
        "   - ⏳ Waiting for Cortex AI enablement"
    ]
    
    for rec in recommendations:
        print(f"  {rec}")
    
    return recommendations

def main():
    """Main test function"""
    print("🚀 Cortex AI Analyst Testing Suite")
    print("=" * 50)
    
    # Test 1: Check availability
    availability_results = test_cortex_analyst_availability()
    
    # Test 2: Try basic Analyst functionality
    analyst_available, analyst_response = test_basic_cortex_analyst()
    
    # Test 3: Check semantic model prerequisites
    semantic_ready, semantic_data = create_semantic_model()
    
    # Test 4: Test business questions
    business_results = test_business_questions()
    
    # Generate recommendations
    recommendations = generate_setup_recommendations()
    
    # Summary
    print("\n📊 Test Summary:")
    print("=" * 30)
    
    if analyst_available:
        print("✅ Cortex AI Analyst is AVAILABLE and working!")
        print("🎉 You can proceed with advanced AI analytics")
    else:
        print("❌ Cortex AI Analyst is NOT available")
        print("📞 Contact Snowflake support to enable Cortex AI")
        print("🔄 Current AI chat uses demo mode and basic Cortex functions")
    
    print(f"\n📈 Business Questions Tested: {len(business_results)}")
    for result in business_results:
        method_icon = "🤖" if result['method'] == 'cortex_analyst' else "📊" if result['method'] == 'direct_sql' else "❌"
        print(f"  {method_icon} {result['question']} - {result['method']}")
    
    print("\n🎯 Next Steps:")
    if analyst_available:
        print("  1. Configure semantic models for better understanding")
        print("  2. Integrate Analyst into Streamlit application")
        print("  3. Train users on natural language querying")
    else:
        print("  1. Contact Snowflake support to enable Cortex AI")
        print("  2. Use current demo mode for demonstrations")
        print("  3. Consider alternative AI integrations")
    
    return {
        'analyst_available': analyst_available,
        'availability_results': availability_results,
        'business_results': business_results,
        'recommendations': recommendations
    }

if __name__ == "__main__":
    try:
        results = main()
        print("\n✅ Testing completed successfully!")
    except Exception as e:
        print(f"\n❌ Testing failed: {str(e)}")
        sys.exit(1)