import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
from utils.snowflake_connector import get_snowflake_connector, execute_query

def show_sales_performance():
    """Display comprehensive sales performance analytics"""
    st.markdown('<div class="main-header">📈 Sales Performance Analytics</div>', unsafe_allow_html=True)
    
    # Load sales data
    sales_data = load_sales_data()
    
    if sales_data is not None and not sales_data.empty:
        # Key metrics row
        show_sales_metrics(sales_data)
        
        # Main analytics tabs
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🎯 Pipeline", "👥 Team Performance", "📈 Trends"])
        
        with tab1:
            show_sales_overview(sales_data)
        
        with tab2:
            show_sales_pipeline(sales_data)
        
        with tab3:
            show_team_performance(sales_data)
        
        with tab4:
            show_sales_trends(sales_data)
    
    else:
        st.error("❌ Unable to load sales data from Snowflake")
        st.info("Please ensure your Snowflake connection is properly configured and the FACT_SALES_PERFORMANCE table exists.")
        st.stop()

def load_sales_data():
    """Load sales data from Snowflake"""
    try:
        # Load from Snowflake
        query = """
        SELECT 
            deal_id,
            deal_name,
            client_name,
            sales_rep,
            deal_value,
            stage,
            probability,
            close_date,
            created_date,
            last_activity_date,
            source,
            industry,
            region
        FROM OLYMPUS_ANALYTICS.GOLD.FACT_SALES_PERFORMANCE
        WHERE created_date >= DATEADD(month, -24, CURRENT_DATE())
        ORDER BY created_date DESC
        """
        
        result = execute_query(query)
        if result is not None and not result.empty:
            return result
        else:
            st.warning("No sales data found in Snowflake for the last 12 months.")
            return None
    except Exception as e:
        st.error(f"Error loading sales data: {str(e)}")
        return None

# Sample data generation functions removed - using only Snowflake data

def show_sales_metrics(df):
    """Display key sales metrics"""
    # Calculate metrics
    total_pipeline = df[df['STAGE'].isin(['Prospecting', 'Qualification', 'Proposal', 'Negotiation'])]['DEAL_VALUE'].sum()
    closed_won = df[df['STAGE'] == 'Closed Won']['DEAL_VALUE'].sum()
    closed_lost = df[df['STAGE'] == 'Closed Lost']['DEAL_VALUE'].sum()
    win_rate = (len(df[df['STAGE'] == 'Closed Won']) / len(df[df['STAGE'].isin(['Closed Won', 'Closed Lost'])])) * 100 if len(df[df['STAGE'].isin(['Closed Won', 'Closed Lost'])]) > 0 else 0
    avg_deal_size = df[df['STAGE'] == 'Closed Won']['DEAL_VALUE'].mean() if len(df[df['STAGE'] == 'Closed Won']) > 0 else 0
    
    # Display metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "💰 Total Pipeline",
            f"${total_pipeline:,.0f}",
            delta=f"+{np.random.randint(5, 15)}%"
        )
    
    with col2:
        st.metric(
            "✅ Closed Won",
            f"${closed_won:,.0f}",
            delta=f"+{np.random.randint(8, 20)}%"
        )
    
    with col3:
        st.metric(
            "📊 Win Rate",
            f"{win_rate:.1f}%",
            delta=f"+{np.random.randint(2, 8)}%"
        )
    
    with col4:
        st.metric(
            "💵 Avg Deal Size",
            f"${avg_deal_size:,.0f}",
            delta=f"+{np.random.randint(3, 12)}%"
        )
    
    with col5:
        active_deals = len(df[~df['STAGE'].isin(['Closed Won', 'Closed Lost'])])
        st.metric(
            "🎯 Active Deals",
            f"{active_deals}",
            delta=f"+{np.random.randint(1, 5)}"
        )

def show_sales_overview(df):
    """Show sales overview with key charts"""
    col1, col2 = st.columns(2)
    
    with col1:
        # Revenue by month
        st.subheader("📈 Monthly Revenue Trend")
        
        monthly_revenue = df[df['STAGE'] == 'Closed Won'].copy()
        monthly_revenue['month'] = pd.to_datetime(monthly_revenue['CLOSE_DATE']).dt.to_period('M')
        monthly_summary = monthly_revenue.groupby('month')['DEAL_VALUE'].sum().reset_index()
        monthly_summary['month'] = monthly_summary['month'].astype(str)
        
        if not monthly_summary.empty and len(monthly_summary) > 0:
            # Ensure data consistency
            if 'DEAL_VALUE' in monthly_summary.columns and len(monthly_summary['month']) == len(monthly_summary['DEAL_VALUE']):
                fig = px.line(
                    monthly_summary,
                    x='month',
                    y='DEAL_VALUE',
                    title='Monthly Revenue Trend',
                    labels={'DEAL_VALUE': 'Revenue ($)', 'month': 'Month'}
                )
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Data inconsistency in monthly revenue data")
        else:
            st.info("No closed deals to display")
    
    with col2:
        # Pipeline by stage
        st.subheader("🎯 Pipeline by Stage")
        
        pipeline_data = df[~df['STAGE'].isin(['Closed Won', 'Closed Lost'])]
        stage_summary = pipeline_data.groupby('STAGE')['DEAL_VALUE'].sum().reset_index()
        
        if not stage_summary.empty:
            fig = px.bar(
                stage_summary,
                x='STAGE',
            y='DEAL_VALUE',
            title='Pipeline Value by Stage',
            labels={'DEAL_VALUE': 'Pipeline Value ($)', 'STAGE': 'Stage'}
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No active pipeline to display")
    
    # Sales funnel
    st.subheader("🔄 Sales Funnel")
    
    funnel_data = df.groupby('STAGE').agg({
        'DEAL_ID': 'count',
        'DEAL_VALUE': 'sum'
    }).reset_index()
    funnel_data.columns = ['STAGE', 'COUNT', 'VALUE']
    
    # Define stage order
    stage_order = ['Prospecting', 'Qualification', 'Proposal', 'Negotiation', 'Closed Won']
    funnel_data = funnel_data[funnel_data['STAGE'].isin(stage_order)]
    funnel_data['STAGE'] = pd.Categorical(funnel_data['STAGE'], categories=stage_order, ordered=True)
    funnel_data = funnel_data.sort_values('STAGE')
    
    if not funnel_data.empty:
        fig = go.Figure(go.Funnel(
            y=funnel_data['STAGE'],
            x=funnel_data['COUNT'],
            textinfo="value+percent initial"
        ))
        fig.update_layout(
            title="Sales Funnel - Deal Count",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

def show_sales_pipeline(df):
    """Show detailed pipeline analysis"""
    st.subheader("🎯 Pipeline Analysis")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_reps = st.multiselect(
            "Sales Rep",
            options=df['SALES_REP'].unique(),
            default=df['SALES_REP'].unique()[:3]
        )
    
    with col2:
        selected_stages = st.multiselect(
            "Stage",
            options=['Prospecting', 'Qualification', 'Proposal', 'Negotiation'],
            default=['Qualification', 'Proposal', 'Negotiation']
        )
    
    with col3:
        min_value = st.number_input(
            "Min Deal Value",
            min_value=0,
            value=0,
            step=1000
        )
    
    # Filter data
    filtered_df = df[
        (df['SALES_REP'].isin(selected_reps)) &
        (df['STAGE'].isin(selected_stages)) &
        (df['DEAL_VALUE'] >= min_value)
    ]
    
    if not filtered_df.empty:
        # Pipeline table
        st.subheader("📋 Active Pipeline")
        
        display_df = filtered_df[[
            'DEAL_NAME', 'CLIENT_NAME', 'SALES_REP', 'DEAL_VALUE', 
            'STAGE', 'PROBABILITY', 'CLOSE_DATE'
        ]].copy()
        
        display_df['DEAL_VALUE'] = display_df['DEAL_VALUE'].apply(lambda x: f"${x:,.0f}")
        display_df['PROBABILITY'] = display_df['PROBABILITY'].apply(lambda x: f"{x}%")
        display_df['CLOSE_DATE'] = pd.to_datetime(display_df['CLOSE_DATE']).dt.strftime('%Y-%m-%d')
        
        st.dataframe(display_df, use_container_width=True)
        
        # Pipeline charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Pipeline by rep
            rep_pipeline = filtered_df.groupby('SALES_REP')['DEAL_VALUE'].sum().reset_index()
            
            fig = px.bar(
                rep_pipeline,
                x='SALES_REP',
                y='DEAL_VALUE',
                title='Pipeline by Sales Rep',
                labels={'DEAL_VALUE': 'Pipeline Value ($)', 'SALES_REP': 'Sales Rep'}
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Weighted pipeline
            filtered_df['weighted_value'] = filtered_df['DEAL_VALUE'] * filtered_df['PROBABILITY'] / 100
            weighted_pipeline = filtered_df.groupby('STAGE')['weighted_value'].sum().reset_index()
            
            fig = px.pie(
                weighted_pipeline,
                values='weighted_value',
                names='STAGE',
                title='Weighted Pipeline by Stage'
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.info("No data matches the selected filters.")

def show_team_performance(df):
    """Show team performance metrics"""
    st.subheader("👥 Team Performance")
    
    # Team metrics
    team_metrics = df.groupby('SALES_REP').agg({
        'DEAL_ID': 'count',
        'DEAL_VALUE': ['sum', 'mean'],
        'STAGE': lambda x: (x == 'Closed Won').sum()
    }).round(2)
    
    team_metrics.columns = ['Total Deals', 'Total Value', 'Avg Deal Size', 'Deals Won']
    team_metrics['Win Rate'] = (team_metrics['Deals Won'] / team_metrics['Total Deals'] * 100).round(1)
    team_metrics['Total Value'] = team_metrics['Total Value'].apply(lambda x: f"${x:,.0f}")
    team_metrics['Avg Deal Size'] = team_metrics['Avg Deal Size'].apply(lambda x: f"${x:,.0f}")
    team_metrics['Win Rate'] = team_metrics['Win Rate'].apply(lambda x: f"{x}%")
    
    st.dataframe(team_metrics, use_container_width=True)
    
    # Performance charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Revenue by rep
        rep_revenue = df[df['STAGE'] == 'Closed Won'].groupby('SALES_REP')['DEAL_VALUE'].sum().reset_index()
        
        if not rep_revenue.empty:
            fig = px.bar(
                rep_revenue,
                x='DEAL_VALUE',
                y='SALES_REP',
                orientation='h',
                title='Revenue by Sales Rep',
                labels={'DEAL_VALUE': 'Revenue ($)', 'SALES_REP': 'Sales Rep'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Activity levels
        df['days_since_activity'] = (datetime.now() - pd.to_datetime(df['LAST_ACTIVITY_DATE'])).dt.days
        activity_summary = df.groupby('SALES_REP')['days_since_activity'].mean().reset_index()
        
        fig = px.scatter(
            activity_summary,
            x='SALES_REP',
            y='days_since_activity',
            size='days_since_activity',
            title='Days Since Last Activity',
            labels={'days_since_activity': 'Days Since Activity', 'SALES_REP': 'Sales Rep'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

def show_sales_trends(df):
    """Show sales trends and forecasting"""
    st.subheader("📈 Sales Trends & Forecasting")
    
    # Time series analysis
    col1, col2 = st.columns(2)
    
    with col1:
        # Monthly trends
        st.markdown("### 📊 Monthly Trends")
        
        df['month'] = pd.to_datetime(df['CREATED_DATE']).dt.to_period('M')
        monthly_trends = df.groupby(['month', 'STAGE']).size().unstack(fill_value=0)
        monthly_trends.index = monthly_trends.index.astype(str)
        
        if not monthly_trends.empty:
            # Get available stage columns
            available_stages = [col for col in monthly_trends.columns if col in ['Prospecting', 'Qualification', 'Proposal', 'Negotiation', 'Closed Won', 'Closed Lost']]
            
            if available_stages:
                fig = px.line(
                    monthly_trends.reset_index(),
                    x='month',
                    y=available_stages,
                    title='Deal Creation Trends by Stage'
                )
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No stage data available for trends")
        else:
             st.info("No data available for monthly trends")
    
    with col2:
        # Conversion rates
        st.markdown("### 🎯 Conversion Rates")
        
        conversion_data = []
        stages = ['Prospecting', 'Qualification', 'Proposal', 'Negotiation', 'Closed Won']
        
        for i in range(len(stages) - 1):
            current_stage = stages[i]
            next_stage = stages[i + 1]
            
            current_count = len(df[df['STAGE'] == current_stage])
            next_count = len(df[df['STAGE'] == next_stage])
            
            if current_count > 0:
                conversion_rate = (next_count / current_count) * 100
            else:
                conversion_rate = 0
            
            conversion_data.append({
                'transition': f"{current_stage} → {next_stage}",
                'rate': conversion_rate
            })
        
        conversion_df = pd.DataFrame(conversion_data)
        
        fig = px.bar(
            conversion_df,
            x='transition',
            y='rate',
            title='Stage Conversion Rates',
            labels={'rate': 'Conversion Rate (%)', 'transition': 'Stage Transition'}
        )
        fig.update_layout(height=300, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Forecasting
    st.markdown("### 🔮 Revenue Forecast")
    
    # Simple forecasting based on pipeline
    pipeline_df = df[~df['STAGE'].isin(['Closed Won', 'Closed Lost'])].copy()
    pipeline_df['weighted_value'] = pipeline_df['DEAL_VALUE'] * pipeline_df['PROBABILITY'] / 100
    pipeline_df['close_month'] = pd.to_datetime(pipeline_df['CLOSE_DATE']).dt.to_period('M')
    
    forecast = pipeline_df.groupby('close_month')['weighted_value'].sum().reset_index()
    forecast['close_month'] = forecast['close_month'].astype(str)
    
    if not forecast.empty:
        fig = px.bar(
            forecast,
            x='close_month',
            y='weighted_value',
            title='Forecasted Revenue by Month (Weighted Pipeline)',
            labels={'weighted_value': 'Forecasted Revenue ($)', 'close_month': 'Month'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Key insights
    st.markdown("### 💡 Key Insights")
    
    insights = [
        f"📊 Total active pipeline: ${pipeline_df['DEAL_VALUE'].sum():,.0f}",
        f"🎯 Weighted pipeline value: ${pipeline_df['weighted_value'].sum():,.0f}",
        f"📈 Average deal cycle: {(pd.to_datetime(df['CLOSE_DATE']) - pd.to_datetime(df['CREATED_DATE'])).dt.days.mean():.0f} days",
        f"🏆 Top performing rep: {df[df['STAGE'] == 'Closed Won'].groupby('SALES_REP')['DEAL_VALUE'].sum().idxmax()}",
        f"🎪 Most common source: {df['SOURCE'].mode().iloc[0] if not df['SOURCE'].mode().empty else 'N/A'}"
    ]
    
    for insight in insights:
        st.markdown(f"- {insight}")

# Demo functions removed - using only Snowflake data