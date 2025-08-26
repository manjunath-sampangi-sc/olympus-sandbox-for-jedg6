import streamlit as st
import pandas as pd
from datetime import datetime
import json
from utils.snowflake_connector import get_snowflake_connector, execute_query
from enhanced_ai_chat import get_enhanced_ai_response
import plotly.express as px
import plotly.graph_objects as go
import re

def show_ai_chat():
    """Display AI chat interface with Snowflake Cortex integration"""
    st.markdown('<div class="main-header">🤖 AI Chat Assistant</div>', unsafe_allow_html=True)
    
    # Initialize chat history
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {
                "role": "assistant",
                "content": "Hello! I'm your Olympus Analytics AI assistant. I can help you analyze your sales and training data. Ask me questions like:\n\n• What's our revenue trend this quarter?\n• Which courses have the highest completion rates?\n• Show me top performing sales reps\n• What's our pipeline conversion rate?",
                "timestamp": datetime.now()
            }
        ]
    
    # Connection status
    connector = get_snowflake_connector()
    connection_status = connector.test_connection()
    
    if connection_status['status'] == 'success':
        st.success(f"✅ Connected to Snowflake (Response: {connection_status['response_time']}s)")
        ai_mode = "snowflake_cortex"
    else:
        st.warning("⚠️ Snowflake not connected - Using demo mode")
        ai_mode = "demo"
    
    # Chat interface
    st.subheader("💬 Chat with Your Data")
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
                if "data" in message:
                    st.dataframe(message["data"], use_container_width=True)
                if "chart" in message:
                    st.plotly_chart(message["chart"], use_container_width=True)
    
    # Chat input
    if prompt := st.chat_input("Ask me about your sales and training data..."):
        # Add user message to chat history
        st.session_state.chat_messages.append({
            "role": "user",
            "content": prompt,
            "timestamp": datetime.now()
        })
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing your data..."):
                if ai_mode == "snowflake_cortex":
                    # Try enhanced AI first, fallback to Cortex
                    try:
                        response = get_enhanced_ai_response(prompt, connector)
                    except Exception as e:
                        response = generate_cortex_response(prompt)
                else:
                    response = generate_demo_response(prompt)
                
                st.write(response["content"])
                
                # Display data if available
                if "data" in response and response["data"] is not None:
                    if isinstance(response["data"], list) and len(response["data"]) > 0:
                        # Convert list of dicts to DataFrame
                        df = pd.DataFrame(response["data"])
                        st.dataframe(df, use_container_width=True)
                        
                        # Auto-generate chart based on chart_type
                        if "chart_type" in response:
                            chart = generate_chart_from_data(df, response["chart_type"])
                            if chart:
                                st.plotly_chart(chart, use_container_width=True)
                    elif isinstance(response["data"], pd.DataFrame) and not response["data"].empty:
                        st.dataframe(response["data"], use_container_width=True)
                
                # Display chart if available
                if "chart" in response:
                    st.plotly_chart(response["chart"], use_container_width=True)
        
        # Add assistant response to chat history
        st.session_state.chat_messages.append(response)
    
    # Sidebar with suggested questions
    with st.sidebar:
        st.subheader("💡 Suggested Questions")
        
        suggested_questions = [
            "What's our total revenue this year?",
            "Show me the top 5 sales reps by performance",
            "Which training courses are most popular?",
            "What's our sales pipeline conversion rate?",
            "How many deals did we close this month?",
            "Show me training completion rates by department",
            "What's the average deal size?",
            "Which customers have the highest value?"
        ]
        
        for question in suggested_questions:
            if st.button(question, key=f"suggest_{hash(question)}", use_container_width=True):
                # Simulate clicking the question
                st.session_state.chat_messages.append({
                    "role": "user",
                    "content": question,
                    "timestamp": datetime.now()
                })
                st.rerun()
        
        st.markdown("---")
        
        # Clear chat button
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_messages = [
                {
                    "role": "assistant",
                    "content": "Chat cleared! How can I help you analyze your data?",
                    "timestamp": datetime.now()
                }
            ]
            st.rerun()

def generate_cortex_response(prompt: str) -> dict:
    """Generate response using Snowflake Cortex AI"""
    try:
        # Analyze the prompt to determine intent
        intent = analyze_prompt_intent(prompt)
        
        if intent["type"] == "sql_query":
            # Generate and execute SQL query
            sql_query = generate_sql_from_prompt(prompt, intent)
            
            if sql_query:
                try:
                    # Execute the generated query
                    data = execute_query(sql_query)
                    
                    # Use Snowflake Cortex to generate natural language response
                    # Escape single quotes in the prompt to prevent SQL syntax errors
                    escaped_prompt = prompt.replace("'", "''")
                    cortex_prompt = f"Based on this data analysis query: {escaped_prompt} and the results showing {len(data)} rows, provide a brief, insightful summary of the findings. Be specific about the numbers and trends you see."
                    cortex_query = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('mixtral-8x7b', '{cortex_prompt}') as response"
                    
                    cortex_result = execute_query(cortex_query)
                    ai_response = cortex_result.iloc[0]['RESPONSE'] if not cortex_result.empty else "Here are your query results:"
                    
                    return {
                        "role": "assistant",
                        "content": ai_response,
                        "data": data,
                        "timestamp": datetime.now(),
                        "sql_query": sql_query
                    }
                    
                except Exception as e:
                    return {
                        "role": "assistant",
                        "content": f"I encountered an error executing your query: {str(e)}. Let me try a different approach.",
                        "timestamp": datetime.now()
                    }
            else:
                return {
                    "role": "assistant",
                    "content": "I'm not sure how to query that data. Could you rephrase your question or try one of the suggested questions?",
                    "timestamp": datetime.now()
                }
        
        else:
            # General conversation using Cortex
            escaped_prompt = prompt.replace("'", "''")
            cortex_prompt = f"You are an AI assistant for Olympus Analytics, a sales and training analytics platform. Available data includes: Sales data (SALES_REP, AMOUNT, STAGE, CLIENT_NAME, DEAL_ID, DEAL_NAME, DEAL_VALUE, PROBABILITY, CLOSE_DATE) and Training data (course_name, user_id, progress_percentage, completion_status). The user asked: {escaped_prompt}. Provide a helpful response about sales analytics, training data, or business intelligence. If they ask about data analysis, mention what insights are available. Keep it concise and professional."
            cortex_query = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('mixtral-8x7b', '{cortex_prompt}') as response"
            
            try:
                cortex_result = execute_query(cortex_query)
                ai_response = cortex_result.iloc[0]['RESPONSE'] if not cortex_result.empty else "I'm here to help with your analytics questions!"
                
                return {
                    "role": "assistant",
                    "content": ai_response,
                    "timestamp": datetime.now()
                }
            except Exception as e:
                return generate_demo_response(prompt)
    
    except Exception as e:
        return {
            "role": "assistant",
            "content": f"I encountered an error: {str(e)}. Let me provide a demo response instead.",
            "timestamp": datetime.now()
        }

def analyze_prompt_intent(prompt: str) -> dict:
    """Analyze user prompt to determine intent and extract key information"""
    prompt_lower = prompt.lower()
    
    # Keywords for different types of queries
    revenue_keywords = ['revenue', 'sales', 'money', 'income', 'earnings']
    training_keywords = ['training', 'course', 'learning', 'completion', 'education']
    user_keywords = ['user', 'employee', 'rep', 'person', 'people']
    time_keywords = ['month', 'quarter', 'year', 'week', 'today', 'yesterday']
    
    intent = {
        "type": "sql_query",
        "category": "general",
        "time_filter": None,
        "metrics": []
    }
    
    # Determine category
    if any(keyword in prompt_lower for keyword in revenue_keywords):
        intent["category"] = "revenue"
    elif any(keyword in prompt_lower for keyword in training_keywords):
        intent["category"] = "training"
    elif any(keyword in prompt_lower for keyword in user_keywords):
        intent["category"] = "users"
    
    # Extract time filters
    if 'this month' in prompt_lower:
        intent["time_filter"] = "current_month"
    elif 'this quarter' in prompt_lower:
        intent["time_filter"] = "current_quarter"
    elif 'this year' in prompt_lower:
        intent["time_filter"] = "current_year"
    
    return intent

def generate_sql_from_prompt(prompt: str, intent: dict) -> str:
    """Generate SQL query based on prompt intent"""
    
    # Extract time filter from prompt
    time_filter = ""
    if "12 months" in prompt.lower() or "last year" in prompt.lower():
        time_filter = "WHERE created_at >= DATEADD(month, -12, CURRENT_DATE())"
    elif "6 months" in prompt.lower():
        time_filter = "WHERE created_at >= DATEADD(month, -6, CURRENT_DATE())"
    elif "3 months" in prompt.lower() or "quarter" in prompt.lower():
        time_filter = "WHERE created_at >= DATEADD(month, -3, CURRENT_DATE())"
    elif "month" in prompt.lower():
        time_filter = "WHERE created_at >= DATEADD(month, -1, CURRENT_DATE())"
    
    # Handle sales rep queries specifically
    if "sales rep" in prompt.lower() or "rep performance" in prompt.lower() or "top rep" in prompt.lower():
        query = f"""
        SELECT 
            SALES_REP as sales_rep,
            SUM(CASE WHEN STAGE = 'Closed Won' THEN AMOUNT ELSE 0 END) as total_revenue,
            COUNT(CASE WHEN STAGE = 'Closed Won' THEN 1 END) as deals_won,
            COUNT(*) as total_deals,
            ROUND(COUNT(CASE WHEN STAGE = 'Closed Won' THEN 1 END) * 100.0 / COUNT(*), 1) as win_rate
        FROM OLYMPUS_ANALYTICS.GOLD.FACT_SALES_PERFORMANCE
        {time_filter}
        GROUP BY SALES_REP
        ORDER BY total_revenue DESC
        LIMIT 10
        """
        return query
    
    if intent["category"] == "revenue":
        if "total" in prompt.lower() or "sum" in prompt.lower():
            query = f"""
            SELECT 
                SUM(AMOUNT) as total_revenue,
                COUNT(*) as total_deals,
                AVG(AMOUNT) as avg_deal_size
            FROM OLYMPUS_ANALYTICS.GOLD.FACT_SALES_PERFORMANCE
            {time_filter}
            """
        elif "trend" in prompt.lower():
            query = f"""
            SELECT 
                DATE_TRUNC('month', created_at) as month,
                SUM(AMOUNT) as monthly_revenue,
                COUNT(*) as deal_count
            FROM OLYMPUS_ANALYTICS.GOLD.FACT_SALES_PERFORMANCE
            {time_filter or "WHERE created_at >= DATEADD(month, -12, CURRENT_DATE())"}
            GROUP BY DATE_TRUNC('month', created_at)
            ORDER BY month
            """
        else:
            query = f"""
            SELECT 
                STAGE,
                SUM(AMOUNT) as total_sales,
                COUNT(*) as deals_count,
                AVG(AMOUNT) as avg_deal_size
            FROM OLYMPUS_ANALYTICS.GOLD.FACT_SALES_PERFORMANCE
            {time_filter}
            GROUP BY STAGE
            ORDER BY total_sales DESC
            LIMIT 10
            """
    
    elif intent["category"] == "training":
        learning_time_filter = time_filter.replace("created_at", "enrollment_date") if time_filter else ""
        if "completion" in prompt.lower():
            query = f"""
            SELECT 
                course_id,
                AVG(progress_percentage) as avg_completion,
                COUNT(*) as enrollments,
                SUM(CASE WHEN progress_percentage = 100 THEN 1 ELSE 0 END) as completed_count
            FROM OLYMPUS_ANALYTICS.GOLD.FACT_LEARNING_ANALYTICS
            {learning_time_filter}
            GROUP BY course_id
            ORDER BY avg_completion DESC
            LIMIT 10
            """
        else:
            query = f"""
            SELECT 
                course_id,
                COUNT(*) as total_enrollments,
                AVG(progress_percentage) as avg_progress,
                AVG(time_spent_minutes) as avg_time_spent
            FROM OLYMPUS_ANALYTICS.GOLD.FACT_LEARNING_ANALYTICS
            {learning_time_filter}
            GROUP BY course_id
            ORDER BY total_enrollments DESC
            LIMIT 10
            """
    
    else:
        # Default query - show both sales and learning metrics
        query = f"""
        SELECT 
            'Total Revenue' as metric,
            SUM(AMOUNT) as value
        FROM OLYMPUS_ANALYTICS.GOLD.FACT_SALES_PERFORMANCE
        {time_filter}
        UNION ALL
        SELECT 
            'Total Deals' as metric,
            COUNT(*) as value
        FROM OLYMPUS_ANALYTICS.GOLD.FACT_SALES_PERFORMANCE
        {time_filter}
        UNION ALL
        SELECT 
            'Total Enrollments' as metric,
            COUNT(*) as value
        FROM OLYMPUS_ANALYTICS.GOLD.FACT_LEARNING_ANALYTICS
        {time_filter.replace('created_at', 'enrollment_date') if time_filter else ''}
        """
    
    return query

def generate_chart_from_data(df: pd.DataFrame, chart_type: str):
    """Generate appropriate chart based on data and chart type"""
    try:
        if chart_type == 'bar' and len(df.columns) >= 2:
            # Create bar chart with first column as x-axis and second as y-axis
            x_col = df.columns[0]
            y_col = df.columns[1]
            
            # Find numeric column for y-axis
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                y_col = numeric_cols[0]
            
            fig = px.bar(df, x=x_col, y=y_col, title=f"{y_col} by {x_col}")
            fig.update_layout(height=400)
            return fig
            
        elif chart_type == 'pie' and len(df.columns) >= 2:
            # Create pie chart
            names_col = df.columns[0]
            values_col = df.columns[1]
            
            # Find numeric column for values
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                values_col = numeric_cols[0]
            
            fig = px.pie(df, names=names_col, values=values_col, title=f"Distribution of {values_col}")
            fig.update_layout(height=400)
            return fig
            
        elif chart_type == 'metric':
            # Create metric cards
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                # Create a simple metric display
                fig = go.Figure()
                
                for i, col in enumerate(numeric_cols[:4]):  # Limit to 4 metrics
                    value = df[col].iloc[0] if len(df) > 0 else 0
                    fig.add_trace(go.Indicator(
                        mode="number",
                        value=value,
                        title={"text": col.replace('_', ' ').title()},
                        domain={'row': 0, 'column': i}
                    ))
                
                fig.update_layout(
                    grid={'rows': 1, 'columns': len(numeric_cols[:4]), 'pattern': "independent"},
                    height=200
                )
                return fig
                
    except Exception as e:
        print(f"Chart generation error: {e}")
        return None
    
    return None

def generate_demo_response(prompt: str) -> dict:
    """Generate demo response when Snowflake is not available"""
    prompt_lower = prompt.lower()
    
    # Sample responses based on keywords
    if 'revenue' in prompt_lower:
        return {
            "role": "assistant",
            "content": "Based on our demo data, here's your revenue analysis:\n\n📊 **Total Revenue (YTD):** $2.4M\n📈 **Growth Rate:** +12.5% vs last year\n💰 **Average Deal Size:** $15.4K\n🎯 **Top Month:** November with $245K",
            "timestamp": datetime.now()
        }
    
    elif 'training' in prompt_lower or 'course' in prompt_lower:
        return {
            "role": "assistant",
            "content": "Here's your training analytics summary:\n\n🎓 **Overall Completion Rate:** 87%\n📚 **Most Popular Course:** Sales Fundamentals (156 enrollments)\n⭐ **Highest Rated:** Customer Success Training (4.8/5)\n📈 **Completion Trend:** +5.2% this quarter",
            "timestamp": datetime.now()
        }
    
    elif 'pipeline' in prompt_lower:
        return {
            "role": "assistant",
            "content": "Sales Pipeline Analysis:\n\n🔄 **Total Pipeline Value:** $1.8M\n📊 **Conversion Rate:** 23%\n⏱️ **Average Sales Cycle:** 45 days\n🎯 **Deals in Negotiation:** 15 ($340K value)",
            "timestamp": datetime.now()
        }
    
    else:
        return {
            "role": "assistant",
            "content": "I'm here to help you analyze your sales and training data! Try asking about:\n\n• Revenue trends and performance\n• Training completion rates\n• Sales pipeline analysis\n• Top performing reps or courses\n\nWhat would you like to explore?",
            "timestamp": datetime.now()
        }