#!/usr/bin/env python3
"""
Enhanced AI Chat Integration for Olympus Analytics
This module provides intelligent AI responses using available Snowflake data
and prepares for future Cortex AI Analyst integration
"""

import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd

class OlympusAIChat:
    """Enhanced AI Chat for Olympus Analytics"""
    
    def __init__(self, snowflake_connector):
        self.connector = snowflake_connector
        self.business_context = self._load_business_context()
        self.query_patterns = self._define_query_patterns()
    
    def _load_business_context(self) -> Dict[str, Any]:
        """Load business context and data summaries"""
        try:
            # Get data summaries for context
            sales_summary = self.connector.execute_query("""
                SELECT 
                    COUNT(*) as total_deals,
                    SUM(AMOUNT) as total_revenue,
                    AVG(AMOUNT) as avg_deal_size,
                    COUNT(DISTINCT SALES_REP) as total_reps,
                    COUNT(CASE WHEN STAGE = 'Closed Won' THEN 1 END) as won_deals,
                    COUNT(CASE WHEN STAGE = 'Closed Lost' THEN 1 END) as lost_deals
                FROM FACT_SALES_PERFORMANCE
            """)
            
            learning_summary = self.connector.execute_query("""
                SELECT 
                    COUNT(*) as total_enrollments,
                    COUNT(DISTINCT USER_ID) as total_learners,
                    COUNT(DISTINCT COURSE_ID) as total_courses,
                    AVG(PROGRESS_PERCENTAGE) as avg_progress
                FROM FACT_LEARNING_ANALYTICS
            """)
            
            return {
                'sales': sales_summary.iloc[0].to_dict() if not sales_summary.empty else {},
                'learning': learning_summary.iloc[0].to_dict() if not learning_summary.empty else {},
                'last_updated': datetime.now()
            }
        except Exception as e:
            print(f"Warning: Could not load business context: {e}")
            return {'sales': {}, 'learning': {}, 'last_updated': datetime.now()}
    
    def _define_query_patterns(self) -> List[Dict[str, Any]]:
        """Define patterns for natural language query matching"""
        return [
            {
                'patterns': [r'sales.*performance', r'revenue', r'deals?', r'sales.*rep'],
                'category': 'sales',
                'queries': {
                    'overview': """
                        SELECT 
                            COUNT(*) as total_deals,
                            SUM(AMOUNT) as total_revenue,
                            AVG(AMOUNT) as avg_deal_size,
                            COUNT(DISTINCT SALES_REP) as total_reps
                        FROM FACT_SALES_PERFORMANCE
                    """,
                    'by_rep': """
                        SELECT 
                            SALES_REP,
                            COUNT(*) as deals_count,
                            SUM(AMOUNT) as total_revenue,
                            AVG(AMOUNT) as avg_deal_size,
                            COUNT(CASE WHEN STAGE = 'Closed Won' THEN 1 END) as won_deals
                        FROM FACT_SALES_PERFORMANCE
                        GROUP BY SALES_REP
                        ORDER BY total_revenue DESC
                        LIMIT 10
                    """,
                    'by_stage': """
                        SELECT 
                            STAGE,
                            COUNT(*) as deals_count,
                            SUM(AMOUNT) as total_value,
                            AVG(AMOUNT) as avg_value
                        FROM FACT_SALES_PERFORMANCE
                        GROUP BY STAGE
                        ORDER BY total_value DESC
                    """,
                    'trend': """
                        SELECT 
                            DATE_TRUNC('month', CREATED_AT) as month,
                            SUM(AMOUNT) as monthly_revenue,
                            COUNT(*) as deal_count,
                            AVG(AMOUNT) as avg_deal_size
                        FROM FACT_SALES_PERFORMANCE
                        WHERE CREATED_AT >= DATEADD(month, -12, CURRENT_DATE())
                        GROUP BY DATE_TRUNC('month', CREATED_AT)
                        ORDER BY month
                    """
                }
            },
            {
                'patterns': [r'training', r'course', r'learning', r'completion'],
                'category': 'learning',
                'queries': {
                    'overview': """
                        SELECT 
                            COUNT(*) as total_enrollments,
                            COUNT(DISTINCT USER_ID) as total_learners,
                            COUNT(DISTINCT COURSE_ID) as total_courses,
                            AVG(PROGRESS_PERCENTAGE) as avg_progress
                        FROM FACT_LEARNING_ANALYTICS
                    """,
                    'by_course': """
                        SELECT 
                            COURSE_ID,
                            COUNT(*) as enrollments,
                            AVG(PROGRESS_PERCENTAGE) as avg_progress,
                            COUNT(CASE WHEN COMPLETION_STATUS = 'Completed' THEN 1 END) as completions
                        FROM FACT_LEARNING_ANALYTICS
                        GROUP BY COURSE_ID
                        ORDER BY enrollments DESC
                        LIMIT 10
                    """,
                    'completion_rates': """
                        SELECT 
                            COURSE_ID,
                            COUNT(*) as total_enrollments,
                            COUNT(CASE WHEN COMPLETION_STATUS = 'Completed' THEN 1 END) as completions,
                            ROUND(COUNT(CASE WHEN COMPLETION_STATUS = 'Completed' THEN 1 END) * 100.0 / COUNT(*), 2) as completion_rate
                        FROM FACT_LEARNING_ANALYTICS
                        GROUP BY COURSE_ID
                        HAVING COUNT(*) >= 5
                        ORDER BY completion_rate DESC
                        LIMIT 10
                    """
                }
            },
            {
                'patterns': [r'user', r'employee', r'learner', r'people'],
                'category': 'users',
                'queries': {
                    'overview': """
                        SELECT 
                            COUNT(*) as total_users,
                            COUNT(CASE WHEN STATUS = 'Active' THEN 1 END) as active_users,
                            COUNT(DISTINCT DEPARTMENT) as departments
                        FROM DIM_USERS
                    """,
                    'by_department': """
                        SELECT 
                            DEPARTMENT,
                            COUNT(*) as user_count,
                            COUNT(CASE WHEN STATUS = 'Active' THEN 1 END) as active_count
                        FROM DIM_USERS
                        WHERE DEPARTMENT IS NOT NULL
                        GROUP BY DEPARTMENT
                        ORDER BY user_count DESC
                    """
                }
            }
        ]
    
    def analyze_query(self, user_input: str) -> Dict[str, Any]:
        """Analyze user input and determine appropriate response"""
        user_input_lower = user_input.lower()
        
        # Check for specific query patterns
        for pattern_group in self.query_patterns:
            for pattern in pattern_group['patterns']:
                if re.search(pattern, user_input_lower):
                    return {
                        'category': pattern_group['category'],
                        'queries': pattern_group['queries'],
                        'confidence': 0.8
                    }
        
        # Check for specific keywords
        if any(word in user_input_lower for word in ['overview', 'summary', 'dashboard']):
            return {
                'category': 'overview',
                'queries': {'overview': 'general_overview'},
                'confidence': 0.6
            }
        
        return {
            'category': 'general',
            'queries': {},
            'confidence': 0.3
        }
    
    def generate_intelligent_response(self, user_input: str) -> Dict[str, Any]:
        """Generate intelligent response based on user input"""
        analysis = self.analyze_query(user_input)
        
        if analysis['confidence'] >= 0.6:
            return self._execute_data_query(analysis, user_input)
        else:
            return self._generate_contextual_response(user_input)
    
    def _execute_data_query(self, analysis: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        """Execute data query and format response"""
        category = analysis['category']
        queries = analysis['queries']
        
        try:
            if category == 'sales':
                return self._handle_sales_query(queries, user_input)
            elif category == 'learning':
                return self._handle_learning_query(queries, user_input)
            elif category == 'users':
                return self._handle_users_query(queries, user_input)
            elif category == 'overview':
                return self._handle_overview_query()
            else:
                return self._generate_fallback_response(user_input)
        
        except Exception as e:
            return {
                'role': 'assistant',
                'content': f"I encountered an error while analyzing your data: {str(e)}. Let me provide you with some general insights instead.",
                'data': None,
                'timestamp': datetime.now()
            }
    
    def _handle_sales_query(self, queries: Dict[str, str], user_input: str) -> Dict[str, Any]:
        """Handle sales-related queries"""
        user_lower = user_input.lower()
        
        if 'trend' in user_lower or 'over time' in user_lower or 'monthly' in user_lower:
            query_key = 'trend'
            context = "revenue trend analysis"
        elif 'rep' in user_lower or 'representative' in user_lower:
            query_key = 'by_rep'
            context = "sales representative performance"
        elif 'stage' in user_lower or 'pipeline' in user_lower:
            query_key = 'by_stage'
            context = "sales pipeline stages"
        else:
            query_key = 'overview'
            context = "sales performance overview"
        
        result = self.connector.execute_query(queries[query_key])
        
        if not result.empty:
            response = self._format_sales_response(result, context, query_key)
            chart_type = 'metric'
            if query_key == 'trend':
                chart_type = 'line'
            elif query_key != 'overview':
                chart_type = 'bar'
                
            return {
                'role': 'assistant',
                'content': response,
                'data': result.to_dict('records'),
                'chart_type': chart_type,
                'timestamp': datetime.now()
            }
        else:
            return self._generate_no_data_response('sales')
    
    def _handle_learning_query(self, queries: Dict[str, str], user_input: str) -> Dict[str, Any]:
        """Handle learning-related queries"""
        user_lower = user_input.lower()
        
        if 'completion' in user_lower or 'rate' in user_lower:
            query_key = 'completion_rates'
            context = "course completion rates"
        elif 'course' in user_lower:
            query_key = 'by_course'
            context = "course performance"
        else:
            query_key = 'overview'
            context = "learning analytics overview"
        
        result = self.connector.execute_query(queries[query_key])
        
        if not result.empty:
            response = self._format_learning_response(result, context, query_key)
            return {
                'role': 'assistant',
                'content': response,
                'data': result.to_dict('records'),
                'chart_type': 'bar' if query_key != 'overview' else 'metric',
                'timestamp': datetime.now()
            }
        else:
            return self._generate_no_data_response('learning')
    
    def _handle_users_query(self, queries: Dict[str, str], user_input: str) -> Dict[str, Any]:
        """Handle user-related queries"""
        user_lower = user_input.lower()
        
        if 'department' in user_lower:
            query_key = 'by_department'
            context = "users by department"
        else:
            query_key = 'overview'
            context = "user overview"
        
        result = self.connector.execute_query(queries[query_key])
        
        if not result.empty:
            response = self._format_users_response(result, context, query_key)
            return {
                'role': 'assistant',
                'content': response,
                'data': result.to_dict('records'),
                'chart_type': 'pie' if query_key == 'by_department' else 'metric',
                'timestamp': datetime.now()
            }
        else:
            return self._generate_no_data_response('users')
    
    def _handle_overview_query(self) -> Dict[str, Any]:
        """Handle general overview queries"""
        context = self.business_context
        
        response = f"""📊 **Olympus Analytics Overview**
        
**Sales Performance:**
- Total Deals: {context['sales'].get('TOTAL_DEALS', 'N/A')}
- Total Revenue: ${context['sales'].get('TOTAL_REVENUE', 0):,.2f}
- Average Deal Size: ${context['sales'].get('AVG_DEAL_SIZE', 0):,.2f}
- Sales Representatives: {context['sales'].get('TOTAL_REPS', 'N/A')}

**Learning Analytics:**
- Total Enrollments: {context['learning'].get('TOTAL_ENROLLMENTS', 'N/A')}
- Active Learners: {context['learning'].get('TOTAL_LEARNERS', 'N/A')}
- Available Courses: {context['learning'].get('TOTAL_COURSES', 'N/A')}
- Average Progress: {context['learning'].get('AVG_PROGRESS', 0):.1f}%

💡 **Ask me specific questions like:**
- "Show me sales performance by rep"
- "What are the course completion rates?"
- "How are our sales stages performing?"
        """
        
        return {
            'role': 'assistant',
            'content': response,
            'data': context,
            'chart_type': 'overview',
            'timestamp': datetime.now()
        }
    
    def _format_sales_response(self, data: pd.DataFrame, context: str, query_type: str) -> str:
        """Format sales data response"""
        if query_type == 'overview':
            row = data.iloc[0]
            return f"""📈 **Sales Performance Overview**
            
- **Total Deals:** {row['TOTAL_DEALS']:,}
- **Total Revenue:** ${row['TOTAL_REVENUE']:,.2f}
- **Average Deal Size:** ${row['AVG_DEAL_SIZE']:,.2f}
- **Sales Representatives:** {row['TOTAL_REPS']}
            
💡 This gives you a high-level view of your sales performance. Would you like to see performance by sales rep or pipeline stage?"""
        
        elif query_type == 'by_rep':
            top_rep = data.iloc[0]
            return f"""🏆 **Top Sales Representatives**
            
**Best Performer:** {top_rep['SALES_REP']}
- Revenue: ${top_rep['TOTAL_REVENUE']:,.2f}
- Deals: {top_rep['DEALS_COUNT']}
- Won Deals: {top_rep['WON_DEALS']}
- Avg Deal Size: ${top_rep['AVG_DEAL_SIZE']:,.2f}
            
📊 See the chart below for all representatives' performance."""
        
        elif query_type == 'by_stage':
            return f"""🔄 **Sales Pipeline Analysis**
            
Your deals are distributed across {len(data)} stages. Here's the breakdown by value and count:
            
📊 The chart below shows the distribution across all pipeline stages."""
        
        return f"Here's your {context} data:"
    
    def _format_learning_response(self, data: pd.DataFrame, context: str, query_type: str) -> str:
        """Format learning data response"""
        if query_type == 'overview':
            row = data.iloc[0]
            return f"""📚 **Learning Analytics Overview**
            
- **Total Enrollments:** {row['TOTAL_ENROLLMENTS']:,}
- **Active Learners:** {row['TOTAL_LEARNERS']:,}
- **Available Courses:** {row['TOTAL_COURSES']:,}
- **Average Progress:** {row['AVG_PROGRESS']:.1f}%
            
💡 Your learning platform is actively used! Would you like to see course-specific performance or completion rates?"""
        
        elif query_type == 'by_course':
            top_course = data.iloc[0]
            return f"""📖 **Course Performance Analysis**
            
**Most Popular Course:** {top_course['COURSE_ID']}
- Enrollments: {top_course['ENROLLMENTS']}
- Average Progress: {top_course['AVG_PROGRESS']:.1f}%
- Completions: {top_course['COMPLETIONS']}
            
📊 See the chart below for all course performance metrics."""
        
        elif query_type == 'completion_rates':
            best_course = data.iloc[0]
            return f"""✅ **Course Completion Rates**
            
**Highest Completion Rate:** {best_course['COURSE_ID']}
- Completion Rate: {best_course['COMPLETION_RATE']:.1f}%
- Total Enrollments: {best_course['TOTAL_ENROLLMENTS']}
- Completions: {best_course['COMPLETIONS']}
            
📊 The chart shows completion rates for all courses with sufficient enrollment."""
        
        return f"Here's your {context} data:"
    
    def _format_users_response(self, data: pd.DataFrame, context: str, query_type: str) -> str:
        """Format users data response"""
        if query_type == 'overview':
            row = data.iloc[0]
            return f"""👥 **User Overview**
            
- **Total Users:** {row['TOTAL_USERS']:,}
- **Active Users:** {row['ACTIVE_USERS']:,}
- **Departments:** {row['DEPARTMENTS']}
            
💡 Your organization has a good user base across multiple departments!"""
        
        elif query_type == 'by_department':
            largest_dept = data.iloc[0]
            return f"""🏢 **Users by Department**
            
**Largest Department:** {largest_dept['DEPARTMENT']}
- Total Users: {largest_dept['USER_COUNT']}
- Active Users: {largest_dept['ACTIVE_COUNT']}
            
📊 The chart shows the distribution of users across all departments."""
        
        return f"Here's your {context} data:"
    
    def _generate_contextual_response(self, user_input: str) -> Dict[str, Any]:
        """Generate contextual response for general queries"""
        user_lower = user_input.lower()
        
        # Greeting responses
        if any(greeting in user_lower for greeting in ['hello', 'hi', 'hey', 'good morning', 'good afternoon']):
            return {
                'role': 'assistant',
                'content': """👋 Hello! I'm your Olympus Analytics AI assistant. I can help you analyze your sales and training data.
                
💡 **Try asking me:**
- "Show me our sales performance"
- "What are the course completion rates?"
- "How are our sales reps performing?"
- "Give me an overview of our data"
                
What would you like to know about your business data?""",
                'timestamp': datetime.now()
            }
        
        # Help responses
        elif any(help_word in user_lower for help_word in ['help', 'what can you do', 'capabilities']):
            return {
                'role': 'assistant',
                'content': """🤖 **I can help you with:**
                
📈 **Sales Analytics:**
- Revenue and deal performance
- Sales representative analysis
- Pipeline stage breakdown
- Deal conversion rates
                
📚 **Learning Analytics:**
- Course completion rates
- Training program effectiveness
- Learner engagement metrics
- Popular courses analysis
                
👥 **User Analytics:**
- User demographics
- Department breakdowns
- Activity levels
                
💬 **Just ask me in natural language!** For example:
- "What's our total revenue?"
- "Which courses have the best completion rates?"
- "Show me sales by representative""",
                'timestamp': datetime.now()
            }
        
        # Default response
        else:
            return {
                'role': 'assistant',
                'content': f"""I understand you're asking about: "{user_input}"
                
🤔 I'm not sure how to analyze that specific request, but I can help you with:
                
📊 **Available Analytics:**
- Sales performance and revenue data
- Training and course completion metrics
- User and department analytics
                
💡 **Try rephrasing your question like:**
- "Show me sales data"
- "What are our training metrics?"
- "Give me a business overview"
                
What specific aspect of your business data would you like to explore?""",
                'timestamp': datetime.now()
            }
    
    def _generate_no_data_response(self, category: str) -> Dict[str, Any]:
        """Generate response when no data is available"""
        return {
            'role': 'assistant',
            'content': f"""📊 I don't see any {category} data available right now.
            
🔍 **This could be because:**
- The data hasn't been loaded yet
- There might be a connection issue
- The tables might be empty
            
💡 **You can try:**
- Asking about a different data category
- Checking the data pipeline status
- Refreshing the connection
            
Would you like me to help you with something else?""",
            'timestamp': datetime.now()
        }
    
    def _generate_fallback_response(self, user_input: str) -> Dict[str, Any]:
        """Generate fallback response for unrecognized queries"""
        return {
            'role': 'assistant',
            'content': f"""🤖 I'm still learning to understand complex queries like: "{user_input}"
            
📊 **For now, I work best with questions about:**
- Sales performance and revenue
- Training and course analytics
- User and department data
            
🚀 **Future Enhancement:** Once Cortex AI Analyst is enabled in your Snowflake account, I'll be able to handle much more sophisticated natural language queries!
            
💡 **Try asking:** "Show me our sales overview" or "What are our training metrics?"""
        }

# Integration function for Streamlit
def get_enhanced_ai_response(user_input: str, snowflake_connector) -> Dict[str, Any]:
    """Main function to get enhanced AI response"""
    try:
        ai_chat = OlympusAIChat(snowflake_connector)
        return ai_chat.generate_intelligent_response(user_input)
    except Exception as e:
        return {
            'role': 'assistant',
            'content': f"I encountered an error: {str(e)}. Please try again or contact support.",
            'timestamp': datetime.now()
        }