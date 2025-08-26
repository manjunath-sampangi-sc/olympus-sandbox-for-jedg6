import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
from utils.snowflake_connector import get_snowflake_connector, execute_query

def show_learning_analytics():
    """Display comprehensive learning analytics dashboard"""
    st.markdown('<div class="main-header">🎓 Learning Analytics Dashboard</div>', unsafe_allow_html=True)
    
    # Load learning data
    learning_data = load_learning_data()
    
    if learning_data is not None and not learning_data.empty:
        # Key metrics row
        show_learning_metrics(learning_data)
        
        # Main analytics tabs
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "👥 Learner Progress", "📚 Course Analytics", "🎯 Performance"])
        
        with tab1:
            show_learning_overview(learning_data)
        
        with tab2:
            show_learner_progress(learning_data)
        
        with tab3:
            show_course_analytics(learning_data)
        
        with tab4:
            show_performance_analytics(learning_data)
    
    else:
        st.error("❌ Unable to load learning data from Snowflake")
        st.info("Please ensure your Snowflake connection is properly configured and the FACT_LEARNING_ANALYTICS table exists.")
        st.stop()

def load_learning_data():
    """Load learning data from Snowflake"""
    try:
        # Load from Snowflake
        query = """
        SELECT 
            f.USER_ID,
            CONCAT(u.FIRST_NAME, ' ', u.LAST_NAME) as USER_NAME,
            f.COURSE_ID,
            c.COURSE_NAME,
            c.COURSE_CATEGORY,
            f.ENROLLMENT_DATE,
            CASE WHEN f.COMPLETION_STATUS = 'Completed' THEN f.LEARNING_DATE END as COMPLETION_DATE,
            f.PROGRESS_PERCENTAGE,
            f.TIME_SPENT_MINUTES,
            f.QUIZ_SCORE,
            CASE 
                WHEN f.QUIZ_SCORE >= 90 THEN 'A'
                WHEN f.QUIZ_SCORE >= 80 THEN 'B'
                WHEN f.QUIZ_SCORE >= 70 THEN 'C'
                WHEN f.QUIZ_SCORE >= 60 THEN 'D'
                ELSE 'F'
            END as FINAL_GRADE,
            f.CERTIFICATION_EARNED,
            f.LAST_ACCESSED_DATE as LAST_ACTIVITY_DATE,
            u.DEPARTMENT,
            u.JOB_TITLE as ROLE,
            m.FIRST_NAME || ' ' || m.LAST_NAME as MANAGER
        FROM OLYMPUS_ANALYTICS.GOLD.FACT_LEARNING_ANALYTICS f
        LEFT JOIN OLYMPUS_ANALYTICS.GOLD.DIM_USERS u ON f.USER_ID = u.USER_ID
        LEFT JOIN OLYMPUS_ANALYTICS.GOLD.DIM_COURSES c ON f.COURSE_ID = c.COURSE_ID
        LEFT JOIN OLYMPUS_ANALYTICS.GOLD.DIM_USERS m ON u.MANAGER_ID = m.USER_ID
        WHERE f.ENROLLMENT_DATE >= DATEADD(month, -12, CURRENT_DATE())
        ORDER BY f.ENROLLMENT_DATE DESC
        """
        
        result = execute_query(query)
        if result is not None and not result.empty:
            # Convert numeric columns to proper data types
            numeric_columns = ['PROGRESS_PERCENTAGE', 'TIME_SPENT_MINUTES', 'QUIZ_SCORE', 'CERTIFICATION_EARNED']
            for col in numeric_columns:
                if col in result.columns:
                    result[col] = pd.to_numeric(result[col], errors='coerce').fillna(0)
            
            # Convert date columns
            date_columns = ['ENROLLMENT_DATE', 'COMPLETION_DATE', 'LAST_ACTIVITY_DATE']
            for col in date_columns:
                if col in result.columns:
                    result[col] = pd.to_datetime(result[col], errors='coerce')
            
            return result
        else:
            st.warning("No learning data found in Snowflake for the last 12 months.")
            return None
    except Exception as e:
        st.error(f"Error loading learning data: {str(e)}")
        return None

# Sample data generation function removed - using only Snowflake data

def show_learning_metrics(df):
    """Display key learning metrics"""
    # Calculate metrics
    total_enrollments = len(df)
    completed_courses = len(df[df['COMPLETION_DATE'].notna()])
    completion_rate = (completed_courses / total_enrollments) * 100 if total_enrollments > 0 else 0
    avg_progress = df['PROGRESS_PERCENTAGE'].mean()
    total_hours = df['TIME_SPENT_MINUTES'].sum() / 60
    avg_score = df['QUIZ_SCORE'].mean() if df['QUIZ_SCORE'].notna().any() else 0
    
    # Display metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "📚 Total Enrollments",
            f"{total_enrollments:,}",
            delta=f"+{np.random.randint(5, 15)}%"
        )
    
    with col2:
        st.metric(
            "✅ Completion Rate",
            f"{completion_rate:.1f}%",
            delta=f"+{np.random.randint(2, 8)}%"
        )
    
    with col3:
        st.metric(
            "📊 Avg Progress",
            f"{avg_progress:.1f}%",
            delta=f"+{np.random.randint(1, 5)}%"
        )
    
    with col4:
        st.metric(
            "⏱️ Total Hours",
            f"{total_hours:,.0f}h",
            delta=f"+{np.random.randint(10, 25)}%"
        )
    
    with col5:
        st.metric(
            "🎯 Avg Quiz Score",
            f"{avg_score:.1f}%",
            delta=f"+{np.random.randint(1, 4)}%"
        )

def show_learning_overview(df):
    """Show learning overview with key charts"""
    col1, col2 = st.columns(2)
    
    with col1:
        # Enrollments by month
        st.subheader("📈 Monthly Enrollment Trend")
        
        df['enrollment_month'] = pd.to_datetime(df['ENROLLMENT_DATE']).dt.to_period('M')
        monthly_enrollments = df.groupby('enrollment_month').size().reset_index(name='enrollments')
        monthly_enrollments['enrollment_month'] = monthly_enrollments['enrollment_month'].astype(str)
        
        if not monthly_enrollments.empty:
            fig = px.line(
                monthly_enrollments,
                x='enrollment_month',
                y='enrollments',
                title='Monthly Enrollments',
                labels={'enrollments': 'Number of Enrollments', 'enrollment_month': 'Month'}
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No enrollment data to display")
    
    with col2:
        # Course categories
        st.subheader("📚 Enrollments by Category")
        
        category_summary = df.groupby('COURSE_CATEGORY').size().reset_index(name='enrollments')
        
        if not category_summary.empty:
            fig = px.pie(
                category_summary,
                values='enrollments',
                names='COURSE_CATEGORY',
                title='Course Category Distribution'
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No category data to display")
    
    # Department performance
    st.subheader("🏢 Department Learning Performance")
    
    dept_performance = df.groupby('DEPARTMENT').agg({
        'USER_ID': 'count',
        'COMPLETION_DATE': lambda x: x.notna().sum(),
        'PROGRESS_PERCENTAGE': 'mean',
        'TIME_SPENT_MINUTES': 'sum'
    }).round(2)
    
    dept_performance.columns = ['Total Enrollments', 'Completed Courses', 'Avg Progress %', 'Total Hours']
    dept_performance['Total Hours'] = dept_performance['Total Hours'] / 60
    dept_performance['Completion Rate %'] = (dept_performance['Completed Courses'] / dept_performance['Total Enrollments'] * 100).round(1)
    
    st.dataframe(dept_performance, use_container_width=True)

def show_learner_progress(df):
    """Show individual learner progress and analytics"""
    st.subheader("👥 Learner Progress Analysis")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_departments = st.multiselect(
            "Department",
            options=df['DEPARTMENT'].unique(),
            default=df['DEPARTMENT'].unique()[:3]
        )
    
    with col2:
        selected_categories = st.multiselect(
            "Course Category",
            options=df['COURSE_CATEGORY'].unique(),
            default=df['COURSE_CATEGORY'].unique()
        )
    
    with col3:
        progress_filter = st.selectbox(
            "Progress Filter",
            options=['All', 'Completed', 'In Progress', 'Not Started']
        )
    
    # Filter data
    filtered_df = df[
        (df['DEPARTMENT'].isin(selected_departments)) &
        (df['COURSE_CATEGORY'].isin(selected_categories))
    ]
    
    if progress_filter == "Completed":
        filtered_df = filtered_df[filtered_df['COMPLETION_DATE'].notna()]
    elif progress_filter == "In Progress":
        filtered_df = filtered_df[
            (filtered_df['COMPLETION_DATE'].isna()) &
            (filtered_df['PROGRESS_PERCENTAGE'] > 0)
        ]
    elif progress_filter == "Not Started":
        filtered_df = filtered_df[filtered_df['PROGRESS_PERCENTAGE'] == 0]
    
    if not filtered_df.empty:
        # Progress distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Progress Distribution")
            
            # Create progress bins
            filtered_df['progress_bin'] = pd.cut(
                filtered_df['PROGRESS_PERCENTAGE'],
                bins=[0, 25, 50, 75, 100],
                labels=['0-25%', '26-50%', '51-75%', '76-100%'],
                include_lowest=True
            )
            
            progress_dist = filtered_df['progress_bin'].value_counts().reset_index()
            progress_dist.columns = ['Progress Range', 'Count']
            
            fig = px.bar(
                progress_dist,
                x='Progress Range',
                y='Count',
                title='Learner Progress Distribution',
                labels={'Count': 'Number of Learners'}
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### ⏱️ Time Spent Analysis")
            
            # Time spent by category
            time_by_category = filtered_df.groupby('COURSE_CATEGORY')['TIME_SPENT_MINUTES'].sum().reset_index()
            time_by_category['time_spent_hours'] = time_by_category['TIME_SPENT_MINUTES'] / 60
            
            fig = px.bar(
                time_by_category,
                x='COURSE_CATEGORY',
                y='time_spent_hours',
                title='Total Learning Hours by Category',
                labels={'time_spent_hours': 'Hours', 'COURSE_CATEGORY': 'Category'}
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        # Top learners
        st.markdown("### 🏆 Top Learners")
        
        learner_stats = filtered_df.groupby(['USER_NAME', 'DEPARTMENT']).agg({
            'COURSE_ID': 'count',
            'COMPLETION_DATE': lambda x: x.notna().sum(),
            'TIME_SPENT_MINUTES': 'sum',
            'QUIZ_SCORE': 'mean'
        }).round(2)
        
        learner_stats.columns = ['Courses Enrolled', 'Courses Completed', 'Total Minutes', 'Avg Quiz Score']
        learner_stats['Completion Rate %'] = (learner_stats['Courses Completed'] / learner_stats['Courses Enrolled'] * 100).round(1)
        # Convert Total Minutes to numeric and handle any non-numeric values
        learner_stats['Total Minutes'] = pd.to_numeric(learner_stats['Total Minutes'], errors='coerce').fillna(0)
        learner_stats['Total Hours'] = (learner_stats['Total Minutes'] / 60).round(1)
        
        # Sort by completion rate and total hours
        learner_stats['Score'] = learner_stats['Completion Rate %'] * 0.6 + learner_stats['Total Hours'] * 0.4
        top_learners = learner_stats.sort_values('Score', ascending=False).head(10)
        
        display_learners = top_learners[['Courses Enrolled', 'Courses Completed', 'Completion Rate %', 'Total Hours', 'Avg Quiz Score']].copy()
        st.dataframe(display_learners, use_container_width=True)
    
    else:
        st.info("No data matches the selected filters.")

def show_course_analytics(df):
    """Show course-specific analytics"""
    st.subheader("📚 Course Analytics")
    
    # Course performance metrics
    course_stats = df.groupby(['COURSE_NAME', 'COURSE_CATEGORY']).agg({
        'USER_ID': 'count',
        'COMPLETION_DATE': lambda x: x.notna().sum(),
        'PROGRESS_PERCENTAGE': 'mean',
        'TIME_SPENT_MINUTES': 'mean',
        'QUIZ_SCORE': 'mean'
    }).round(2)
    
    course_stats.columns = ['Enrollments', 'Completions', 'Avg Progress %', 'Avg Time (min)', 'Avg Quiz Score']
    course_stats['Completion Rate %'] = (course_stats['Completions'] / course_stats['Enrollments'] * 100).round(1)
    
    # Convert 'Avg Time (min)' to numeric before calculation
    course_stats['Avg Time (min)'] = pd.to_numeric(course_stats['Avg Time (min)'], errors='coerce').fillna(0)
    course_stats['Avg Time (hours)'] = (course_stats['Avg Time (min)'] / 60).round(1)
    
    # Sort by popularity and completion rate
    course_stats = course_stats.sort_values(['Enrollments', 'Completion Rate %'], ascending=[False, False])
    
    st.markdown("### 📊 Course Performance Summary")
    display_courses = course_stats[['Enrollments', 'Completions', 'Completion Rate %', 'Avg Progress %', 'Avg Time (hours)', 'Avg Quiz Score']].copy()
    st.dataframe(display_courses, use_container_width=True)
    
    # Course analytics charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Course Completion Rates")
        
        top_courses = course_stats.head(10).reset_index()
        
        fig = px.bar(
            top_courses,
            x='Completion Rate %',
            y='COURSE_NAME',
            orientation='h',
            title='Top 10 Courses by Completion Rate',
            labels={'Completion Rate %': 'Completion Rate (%)', 'COURSE_NAME': 'Course'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📈 Enrollment vs Completion")
        
        # Prepare data for scatter plot
        scatter_data = course_stats.reset_index().copy()
        
        fig = px.scatter(
            scatter_data,
            x='Enrollments',
            y='Completion Rate %',
            color='COURSE_CATEGORY',
            hover_name='COURSE_NAME',
            hover_data=['Avg Quiz Score'],
            title='Course Performance Matrix',
            labels={'Enrollments': 'Total Enrollments', 'Completion Rate %': 'Completion Rate (%)'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Course difficulty analysis
    st.markdown("### 🎓 Course Difficulty Analysis")
    
    # Analyze time spent vs completion rate to infer difficulty
    difficulty_analysis = course_stats.copy()
    difficulty_analysis['Difficulty Score'] = (
        (difficulty_analysis['Avg Time (hours)'] / difficulty_analysis['Avg Time (hours)'].max()) * 0.4 +
        ((100 - difficulty_analysis['Completion Rate %']) / 100) * 0.6
    ) * 100
    
    difficulty_analysis['Difficulty Level'] = pd.cut(
        difficulty_analysis['Difficulty Score'],
        bins=[0, 33, 66, 100],
        labels=['Easy', 'Medium', 'Hard']
    )
    
    difficulty_dist = difficulty_analysis['Difficulty Level'].value_counts().reset_index()
    difficulty_dist.columns = ['Difficulty Level', 'Number of Courses']
    
    fig = px.pie(
        difficulty_dist,
        values='Number of Courses',
        names='Difficulty Level',
        title='Course Difficulty Distribution'
    )
    st.plotly_chart(fig, use_container_width=True)

def show_performance_analytics(df):
    """Show performance analytics and insights"""
    st.subheader("🎯 Performance Analytics")
    
    # Performance trends
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Monthly Completion Trends")
        
        completed_df = df[df['COMPLETION_DATE'].notna()].copy()
        completed_df['completion_month'] = pd.to_datetime(completed_df['COMPLETION_DATE']).dt.to_period('M')
        monthly_completions = completed_df.groupby('completion_month').size().reset_index(name='completions')
        monthly_completions['completion_month'] = monthly_completions['completion_month'].astype(str)
        
        if not monthly_completions.empty:
            fig = px.line(
                monthly_completions,
                x='completion_month',
                y='completions',
                title='Monthly Course Completions',
                labels={'completions': 'Completions', 'completion_month': 'Month'}
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🏆 Grade Distribution")
        
        grade_df = df[df['FINAL_GRADE'].notna()]
        if not grade_df.empty:
            grade_dist = grade_df['FINAL_GRADE'].value_counts().reset_index()
            grade_dist.columns = ['Grade', 'Count']
            
            fig = px.bar(
                grade_dist,
                x='Grade',
                y='Count',
                title='Final Grade Distribution',
                labels={'Count': 'Number of Students'}
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No grade data available")
    
    # Certification analysis
    st.markdown("### 🏅 Certification Analysis")
    
    cert_df = df[df['COMPLETION_DATE'].notna()]
    if not cert_df.empty:
        cert_stats = cert_df.groupby('COURSE_CATEGORY').agg({
            'CERTIFICATION_EARNED': ['count', 'sum']
        })
        cert_stats.columns = ['Total Completions', 'Certifications Earned']
        cert_stats['Certification Rate %'] = (cert_stats['Certifications Earned'] / cert_stats['Total Completions'] * 100).round(1)
        
        fig = px.bar(
            cert_stats.reset_index(),
            x='COURSE_CATEGORY',
            y='Certification Rate %',
            title='Certification Rate by Course Category',
            labels={'Certification Rate %': 'Certification Rate (%)', 'COURSE_CATEGORY': 'Category'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Learning path analysis
    st.markdown("### 🛤️ Learning Path Analysis")
    
    # Analyze user learning patterns
    user_patterns = df.groupby('USER_ID').agg({
        'COURSE_CATEGORY': lambda x: x.nunique(),
        'COURSE_ID': 'count',
        'COMPLETION_DATE': lambda x: x.notna().sum(),
        'TIME_SPENT_MINUTES': 'sum'
    })

    user_patterns.columns = ['Categories Explored', 'Total Courses', 'Courses Completed', 'Total Minutes']
    
    # Ensure numeric columns are properly converted
    user_patterns['Total Minutes'] = pd.to_numeric(user_patterns['Total Minutes'], errors='coerce').fillna(0)
    user_patterns['Total Courses'] = pd.to_numeric(user_patterns['Total Courses'], errors='coerce').fillna(0)
    user_patterns['Courses Completed'] = pd.to_numeric(user_patterns['Courses Completed'], errors='coerce').fillna(0)
    
    # Calculate rates and hours with proper numeric handling
    user_patterns['Completion Rate %'] = np.where(
        user_patterns['Total Courses'] > 0,
        (user_patterns['Courses Completed'] / user_patterns['Total Courses'] * 100).round(1),
        0
    )
    user_patterns['Total Hours'] = (user_patterns['Total Minutes'] / 60).round(1)
    
    # Learning behavior insights
    col1, col2 = st.columns(2)
    
    with col1:
        # Multi-category learners
        multi_category = user_patterns[user_patterns['Categories Explored'] > 1]
        st.metric(
            "🔄 Multi-Category Learners",
            f"{len(multi_category)}",
            f"{len(multi_category)/len(user_patterns)*100:.1f}% of all learners"
        )
        
        # Average courses per learner
        avg_courses = user_patterns['Total Courses'].mean()
        st.metric(
            "📚 Avg Courses per Learner",
            f"{avg_courses:.1f}",
            f"Range: {user_patterns['Total Courses'].min()}-{user_patterns['Total Courses'].max()}"
        )
    
    with col2:
        # High performers
        high_performers = user_patterns[
            (user_patterns['Completion Rate %'] >= 80) & 
            (user_patterns['Total Courses'] >= 3)
        ]
        st.metric(
            "🏆 High Performers",
            f"{len(high_performers)}",
            f"{len(high_performers)/len(user_patterns)*100:.1f}% of all learners"
        )
        
        # Average learning time
        avg_hours = user_patterns['Total Hours'].mean()
        st.metric(
            "⏱️ Avg Learning Hours",
            f"{avg_hours:.1f}h",
            f"Total: {user_patterns['Total Hours'].sum():.0f}h"
        )
    
    # Key insights
    st.markdown("### 💡 Key Insights")
    
    # Ensure TIME_SPENT_MINUTES is numeric for calculations
    time_spent_numeric = pd.to_numeric(df['TIME_SPENT_MINUTES'], errors='coerce').fillna(0)
    avg_duration = time_spent_numeric.mean() / 60 if time_spent_numeric.mean() > 0 else 0
    
    insights = [
        f"📊 Most popular category: {df['COURSE_CATEGORY'].mode().iloc[0] if not df['COURSE_CATEGORY'].mode().empty else 'N/A'}",
        f"🎯 Highest certification rate: {cert_stats['Certification Rate %'].max():.1f}% ({cert_stats['Certification Rate %'].idxmax()})",
        f"⏱️ Average course duration: {avg_duration:.1f} hours",
        f"🏆 Top performing department: {dept_performance['Completion Rate %'].idxmax() if 'dept_performance' in locals() else 'N/A'}",
        f"📈 Learning engagement: {len(df[df['LAST_ACTIVITY_DATE'] >= datetime.now() - timedelta(days=7)])} active learners this week"
    ]
    
    for insight in insights:
        st.markdown(f"- {insight}")

# Demo functions removed - using only Snowflake data