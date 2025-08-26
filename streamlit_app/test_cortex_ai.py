#!/usr/bin/env python3
"""
Snowflake Cortex AI Configuration and Testing Script
This script tests the Cortex AI setup for Olympus Analytics
"""

import sys
import os
import pandas as pd
from datetime import datetime
import time

# Add the current directory to the path to import utils
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.snowflake_connector import get_snowflake_connector, execute_query

def test_cortex_availability():
    """Test if Cortex AI is available in the Snowflake account"""
    print("\n🔍 Testing Cortex AI Availability...")
    
    try:
        # Test basic Cortex availability
        query = "SELECT SYSTEM$GET_CORTEX_MODELS() as available_models;"
        result = execute_query(query)
        
        if not result.empty:
            models = result.iloc[0]['AVAILABLE_MODELS']
            print(f"✅ Cortex AI is available! Models: {models}")
            return True, models
        else:
            print("❌ No Cortex models found")
            return False, None
            
    except Exception as e:
        print(f"❌ Cortex AI not available: {str(e)}")
        return False, str(e)

def test_basic_cortex_functions():
    """Test basic Cortex AI functions"""
    print("\n🧪 Testing Basic Cortex Functions...")
    
    tests = [
        {
            'name': 'Text Completion',
            'query': """
                SELECT SNOWFLAKE.CORTEX.COMPLETE(
                    'mixtral-8x7b',
                    'Hello! Please respond with "Cortex AI is working" to confirm functionality.'
                ) as response
            """
        },
        {
            'name': 'Sentiment Analysis',
            'query': """
                SELECT SNOWFLAKE.CORTEX.SENTIMENT(
                    'I love using Snowflake for analytics!'
                ) as sentiment
            """
        },
        {
            'name': 'Text Summarization',
            'query': """
                SELECT SNOWFLAKE.CORTEX.SUMMARIZE(
                    'Olympus Analytics provides comprehensive business intelligence with sales tracking and learning analytics.'
                ) as summary
            """
        }
    ]
    
    results = {}
    
    for test in tests:
        try:
            print(f"  Testing {test['name']}...")
            start_time = time.time()
            result = execute_query(test['query'])
            end_time = time.time()
            
            if not result.empty:
                response = result.iloc[0].iloc[0]  # Get first column of first row
                response_time = round(end_time - start_time, 2)
                print(f"    ✅ Success ({response_time}s): {str(response)[:100]}...")
                results[test['name']] = {
                    'status': 'success',
                    'response': response,
                    'response_time': response_time
                }
            else:
                print(f"    ❌ No response received")
                results[test['name']] = {'status': 'no_response'}
                
        except Exception as e:
            print(f"    ❌ Failed: {str(e)}")
            results[test['name']] = {'status': 'error', 'error': str(e)}
    
    return results

def test_analytics_integration():
    """Test Cortex AI integration with analytics data"""
    print("\n📊 Testing Analytics Integration...")
    
    try:
        # Get data summary for context
        sales_count_query = "SELECT COUNT(*) as count FROM OLYMPUS_ANALYTICS.GOLD.FACT_SALES_PERFORMANCE"
        sales_count = execute_query(sales_count_query).iloc[0]['COUNT']
        
        learning_count_query = "SELECT COUNT(*) as count FROM OLYMPUS_ANALYTICS.GOLD.FACT_LEARNING_ANALYTICS"
        learning_count = execute_query(learning_count_query).iloc[0]['COUNT']
        
        print(f"  📈 Sales records: {sales_count}")
        print(f"  📚 Learning records: {learning_count}")
        
        # Test AI analysis of data
        analysis_query = f"""
            SELECT SNOWFLAKE.CORTEX.COMPLETE(
                'mixtral-8x7b',
                'Based on a dataset with {sales_count} sales records and {learning_count} learning records, what are 3 key questions a business analyst might ask? Provide a brief, numbered list.'
            ) as analysis
        """
        
        print("  🤖 Generating AI analysis...")
        start_time = time.time()
        result = execute_query(analysis_query)
        end_time = time.time()
        
        if not result.empty:
            analysis = result.iloc[0]['ANALYSIS']
            response_time = round(end_time - start_time, 2)
            print(f"  ✅ AI Analysis completed ({response_time}s):")
            print(f"     {analysis}")
            return True, analysis
        else:
            print("  ❌ No analysis generated")
            return False, None
            
    except Exception as e:
        print(f"  ❌ Analytics integration failed: {str(e)}")
        return False, str(e)

def test_app_simulation():
    """Simulate the actual app queries"""
    print("\n🎯 Simulating App Queries...")
    
    app_queries = [
        "What's our revenue trend this quarter?",
        "Which courses have the highest completion rates?",
        "Show me top performing sales reps"
    ]
    
    results = []
    
    for query in app_queries:
        try:
            print(f"  Testing: '{query}'")
            
            # Simulate the app's Cortex query
            cortex_query = f"""
                SELECT SNOWFLAKE.CORTEX.COMPLETE(
                    'mixtral-8x7b',
                    'You are an AI assistant for Olympus Analytics. A user asks: "{query}" Provide a helpful response about what analysis you can perform with sales and training data.'
                ) as response
            """
            
            start_time = time.time()
            result = execute_query(cortex_query)
            end_time = time.time()
            
            if not result.empty:
                response = result.iloc[0]['RESPONSE']
                response_time = round(end_time - start_time, 2)
                print(f"    ✅ Response ({response_time}s): {response[:150]}...")
                results.append({
                    'query': query,
                    'status': 'success',
                    'response': response,
                    'response_time': response_time
                })
            else:
                print(f"    ❌ No response")
                results.append({'query': query, 'status': 'no_response'})
                
        except Exception as e:
            print(f"    ❌ Failed: {str(e)}")
            results.append({'query': query, 'status': 'error', 'error': str(e)})
    
    return results

def check_permissions():
    """Check if the current role has necessary permissions"""
    print("\n🔐 Checking Permissions...")
    
    try:
        # Check current role and context
        context_query = "SELECT CURRENT_ROLE(), CURRENT_USER(), CURRENT_WAREHOUSE(), CURRENT_DATABASE()"
        context = execute_query(context_query)
        
        if not context.empty:
            role = context.iloc[0].iloc[0]
            user = context.iloc[0].iloc[1]
            warehouse = context.iloc[0].iloc[2]
            database = context.iloc[0].iloc[3]
            
            print(f"  👤 User: {user}")
            print(f"  🎭 Role: {role}")
            print(f"  🏭 Warehouse: {warehouse}")
            print(f"  🗄️ Database: {database}")
            
            return True, {'role': role, 'user': user, 'warehouse': warehouse, 'database': database}
        else:
            print("  ❌ Could not retrieve context")
            return False, None
            
    except Exception as e:
        print(f"  ❌ Permission check failed: {str(e)}")
        return False, str(e)

def generate_configuration_report(test_results):
    """Generate a comprehensive configuration report"""
    print("\n📋 CORTEX AI CONFIGURATION REPORT")
    print("=" * 50)
    
    # Overall status
    cortex_available = test_results.get('cortex_available', False)
    basic_functions = test_results.get('basic_functions', {})
    analytics_integration = test_results.get('analytics_integration', False)
    app_simulation = test_results.get('app_simulation', [])
    
    print(f"\n🎯 OVERALL STATUS")
    if cortex_available and analytics_integration and len([r for r in app_simulation if r.get('status') == 'success']) > 0:
        print("   ✅ CORTEX AI FULLY CONFIGURED AND READY")
        status = "READY"
    elif cortex_available:
        print("   ⚠️  CORTEX AI PARTIALLY CONFIGURED")
        status = "PARTIAL"
    else:
        print("   ❌ CORTEX AI NOT CONFIGURED")
        status = "NOT_READY"
    
    print(f"\n📊 DETAILED RESULTS")
    print(f"   Cortex Available: {'✅' if cortex_available else '❌'}")
    print(f"   Basic Functions: {len([f for f in basic_functions.values() if f.get('status') == 'success'])}/{len(basic_functions)} working")
    print(f"   Analytics Integration: {'✅' if analytics_integration else '❌'}")
    print(f"   App Simulation: {len([r for r in app_simulation if r.get('status') == 'success'])}/{len(app_simulation)} queries working")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS")
    if status == "READY":
        print("   🎉 Your Cortex AI is fully configured!")
        print("   🚀 The AI Chat feature should work perfectly")
        print("   📱 Test the chat interface in your Streamlit app")
    elif status == "PARTIAL":
        print("   🔧 Some Cortex functions need attention")
        print("   👨‍💼 Contact your Snowflake admin to grant missing permissions")
        print("   🔄 Re-run this test after permission updates")
    else:
        print("   🚨 Cortex AI needs to be enabled in your Snowflake account")
        print("   📞 Contact Snowflake support to enable Cortex AI")
        print("   🔐 Ensure your role has Cortex permissions")
    
    return status

def main():
    """Main testing function"""
    print("🤖 SNOWFLAKE CORTEX AI CONFIGURATION TEST")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize results
    test_results = {}
    
    # Test 1: Check permissions
    permissions_ok, permissions_info = check_permissions()
    test_results['permissions'] = permissions_info
    
    if not permissions_ok:
        print("\n❌ Cannot proceed without proper permissions")
        return
    
    # Test 2: Check Cortex availability
    cortex_available, models_info = test_cortex_availability()
    test_results['cortex_available'] = cortex_available
    test_results['models'] = models_info
    
    if not cortex_available:
        print("\n⚠️ Cortex AI not available - generating recommendations...")
        generate_configuration_report(test_results)
        return
    
    # Test 3: Basic functions
    basic_results = test_basic_cortex_functions()
    test_results['basic_functions'] = basic_results
    
    # Test 4: Analytics integration
    analytics_ok, analytics_result = test_analytics_integration()
    test_results['analytics_integration'] = analytics_ok
    test_results['analytics_result'] = analytics_result
    
    # Test 5: App simulation
    app_results = test_app_simulation()
    test_results['app_simulation'] = app_results
    
    # Generate final report
    final_status = generate_configuration_report(test_results)
    
    print(f"\n✅ Testing completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Final Status: {final_status}")
    
    return test_results

if __name__ == "__main__":
    try:
        results = main()
    except KeyboardInterrupt:
        print("\n\n⏹️ Testing interrupted by user")
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()