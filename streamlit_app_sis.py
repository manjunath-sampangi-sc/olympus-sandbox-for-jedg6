# streamlit_app_sis.py - Streamlit in Snowflake Version
# Optimized for deployment in Snowflake's native Streamlit environment

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from snowflake.snowpark.context import get_active_session

# Get Snowflake session (automatically available in SiS)
session = get_active_session()

# Page configuration
st.set_page_config(
    page_title="Olympus Analytics - Production",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #4682B4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #fefefe;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #4682B4;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(70, 130, 180, 0.1);
    }
    .sidebar-logo {
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
        color: #4682B4;
        margin-bottom: 2rem;
    }
    .client-branding {
        text-align: center;
        font-size: 0.9rem;
        color: #cccccc;
        margin-bottom: 1rem;
        font-style: italic;
    }
    .stButton > button {
        background-color: #87CEEB;
        color: #ffffff;
        border: none;
        border-radius: 0.5rem;
    }
    .stButton > button:hover {
        background-color: #4682B4;
        color: #ffffff;
    }
    .section-header {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 1px solid #dee2e6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .section-header h3 {
        color: #4682B4;
        margin-bottom: 0;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

def execute_query(query: str) -> pd.DataFrame:
    """Execute SQL query using Snowpark session"""
    try:
        result = session.sql(query)
        return result.to_pandas()
    except Exception as e:
        st.error(f"Query execution failed: {str(e)}")
        return pd.DataFrame()

def show_billing_dashboard():
    """Main billing dashboard with comprehensive analytics"""
    st.markdown('<div class="main-header">💰 Member Billing Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="client-branding">Olympus Analytics - Real-time Billing Insights from Disco LMS</div>', unsafe_allow_html=True)
    
    # Filters section
    st.markdown("""
    <div class="section-header">
        <h3>🔍 Dashboard Filters</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        billing_month = st.selectbox(
            "📅 Billing Month",
            ["2025-09", "2025-08", "2025-07"],
            index=0
        )
    
    with col2:
        billing_bracket = st.selectbox(
            "💰 Billing Bracket",
            ["All Brackets", "$0", "$10", "$50"],
            index=0
        )
    
    with col3:
        company_filter = st.selectbox(
            "🏢 Company",
            ["All Companies", "SimpliSafe", "Crown Roofing Solutions", "Peoples Choice Solar", "Individual"],
            index=0
        )
    
    with col4:
        enrollment_filter = st.selectbox(
            "📚 Enrollment Status",
            ["All Members", "Enrolled Only", "Non-Enrolled Only"],
            index=0
        )
    
    st.divider()
    
    # Build dynamic query based on filters
    base_query = """
    SELECT 
        MEMBER_ID,
        EMAIL,
        MEMBER_NAME,
        COMPANY_NAME,
        BILLING_BRACKET,
        MONTHLY_AMOUNT,
        TOTAL_COURSES_ENROLLED,
        ENROLLED_COURSES,
        BILLING_CATEGORY_DESCRIPTION,
        BILLING_MONTH
    FROM OLYMPUS_ANALYTICS.GOLD.GD_MEMBER_ENROLLMENT_DETAILS
    WHERE 1=1
    """
    
    # Apply filters
    if billing_month != "All Months":
        base_query += f" AND BILLING_MONTH = '{billing_month}'"
    
    if billing_bracket != "All Brackets":
        base_query += f" AND BILLING_BRACKET = '{billing_bracket}'"
    
    if company_filter != "All Companies":
        base_query += f" AND COMPANY_NAME = '{company_filter}'"
    
    if enrollment_filter == "Enrolled Only":
        base_query += " AND TOTAL_COURSES_ENROLLED > 0"
    elif enrollment_filter == "Non-Enrolled Only":
        base_query += " AND TOTAL_COURSES_ENROLLED = 0"
    
    base_query += " ORDER BY TOTAL_COURSES_ENROLLED DESC, MEMBER_NAME"
    
    # Load billing data
    billing_data = execute_query(base_query)
    
    if billing_data.empty:
        st.warning("No data available for the selected filters. Please adjust your filter criteria.")
        return
    
    # Key metrics section
    st.markdown("""
    <div class="section-header">
        <h3>📊 Key Performance Metrics</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Members",
            f"{len(billing_data):,}",
            help="Total number of members in selected period"
        )
    
    with col2:
        total_revenue = billing_data['MONTHLY_AMOUNT'].sum()
        st.metric(
            "Total Revenue",
            f"${total_revenue:,.2f}",
            help="Total monthly revenue from all billing brackets"
        )
    
    with col3:
        enrolled_members = len(billing_data[billing_data['TOTAL_COURSES_ENROLLED'] > 0])
        st.metric(
            "Enrolled Members",
            f"{enrolled_members:,}",
            help="Members with active course enrollments"
        )
    
    with col4:
        avg_revenue = billing_data['MONTHLY_AMOUNT'].mean()
        st.metric(
            "Avg Revenue/Member",
            f"${avg_revenue:.2f}",
            help="Average monthly revenue per member"
        )
    
    st.divider()
    
    # Charts section
    st.markdown("""
    <div class="section-header">
        <h3>📈 Billing Analytics Charts</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Billing Bracket Distribution")
        bracket_counts = billing_data['BILLING_BRACKET'].value_counts()
        
        fig_pie = px.pie(
            values=bracket_counts.values,
            names=bracket_counts.index,
            title="Members by Billing Bracket",
            color_discrete_sequence=['#87CEEB', '#4682B4', '#B0C4DE']
        )
        fig_pie.update_layout(
            font=dict(size=12),
            showlegend=True,
            height=400
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.subheader("🏢 Top Companies by Enrollment")
        company_enrolled = billing_data[billing_data['TOTAL_COURSES_ENROLLED'] > 0]['COMPANY_NAME'].value_counts().head(10)
        
        if not company_enrolled.empty:
            fig_bar = px.bar(
                x=company_enrolled.values,
                y=company_enrolled.index,
                orientation='h',
                title="Enrolled Members by Company",
                color=company_enrolled.values,
                color_continuous_scale='Blues'
            )
            fig_bar.update_layout(
                font=dict(size=12),
                height=400,
                yaxis={'categoryorder': 'total ascending'}
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No enrolled members found for the selected filters.")
    
    # Summary tables
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💰 Billing Bracket Summary")
        bracket_summary = billing_data.groupby('BILLING_BRACKET').agg({
            'MEMBER_ID': 'count',
            'MONTHLY_AMOUNT': ['sum', 'mean']
        }).round(2)
        
        bracket_summary.columns = ['Member Count', 'Total Revenue', 'Avg Revenue']
        bracket_summary['Percentage'] = (bracket_summary['Member Count'] / len(billing_data) * 100).round(1)
        
        st.dataframe(
            bracket_summary,
            use_container_width=True,
            column_config={
                "Total Revenue": st.column_config.NumberColumn(
                    "Total Revenue",
                    format="$%.2f"
                ),
                "Avg Revenue": st.column_config.NumberColumn(
                    "Avg Revenue",
                    format="$%.2f"
                ),
                "Percentage": st.column_config.NumberColumn(
                    "Percentage",
                    format="%.1f%%"
                )
            }
        )
    
    with col2:
        st.subheader("🎯 Course Enrollment Insights")
        enrollment_insights = billing_data.groupby('BILLING_CATEGORY_DESCRIPTION').agg({
            'MEMBER_ID': 'count',
            'MONTHLY_AMOUNT': 'sum'
        }).reset_index()
        enrollment_insights.columns = ['Category', 'Members', 'Revenue']
        enrollment_insights['Avg Revenue'] = (enrollment_insights['Revenue'] / enrollment_insights['Members']).round(2)
        
        st.dataframe(
            enrollment_insights,
            use_container_width=True,
            column_config={
                "Revenue": st.column_config.NumberColumn(
                    "Revenue",
                    format="$%.2f"
                ),
                "Avg Revenue": st.column_config.NumberColumn(
                    "Avg Revenue",
                    format="$%.2f"
                )
            }
        )
    
    st.divider()
    
    # Detailed member data section
    st.markdown("""
    <div class="section-header">
        <h3>📋 Detailed Member Data</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Search functionality
    search_term = st.text_input(
        "🔍 Search members (by name, email, or company)",
        placeholder="Enter member name, email, or company...",
        help="Search through member names, email addresses, or company names"
    )
    
    filtered_data = billing_data.copy()
    if search_term:
        filtered_data = billing_data[
            billing_data['MEMBER_NAME'].str.contains(search_term, case=False, na=False) |
            billing_data['EMAIL'].str.contains(search_term, case=False, na=False) |
            billing_data['COMPANY_NAME'].str.contains(search_term, case=False, na=False)
        ]
    
    # Display data table
    st.dataframe(
        filtered_data[[
            'MEMBER_NAME', 'EMAIL', 'COMPANY_NAME', 'BILLING_BRACKET',
            'MONTHLY_AMOUNT', 'TOTAL_COURSES_ENROLLED', 'ENROLLED_COURSES',
            'BILLING_CATEGORY_DESCRIPTION'
        ]],
        use_container_width=True,
        column_config={
            "MEMBER_NAME": st.column_config.TextColumn(
                "Member Name",
                width="medium"
            ),
            "EMAIL": st.column_config.TextColumn(
                "Email",
                width="medium"
            ),
            "COMPANY_NAME": st.column_config.TextColumn(
                "Company",
                width="medium"
            ),
            "MONTHLY_AMOUNT": st.column_config.NumberColumn(
                "Monthly Amount",
                format="$%.2f"
            ),
            "TOTAL_COURSES_ENROLLED": st.column_config.NumberColumn(
                "Courses Enrolled",
                format="%d"
            ),
            "ENROLLED_COURSES": st.column_config.TextColumn(
                "Enrolled Courses",
                width="large",
                help="Specific courses this member is enrolled in"
            )
        },
        hide_index=True
    )
    
    # Export functionality
    st.markdown("""
    <div class="section-header">
        <h3>📤 Export Data</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col2:
        if st.button("📊 Export Filtered Data", type="primary"):
            csv = filtered_data.to_csv(index=False)
            st.download_button(
                label="⬇️ Download CSV",
                data=csv,
                file_name=f"olympus_billing_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
            st.success("✅ Data ready for download!")
    
    with col3:
        if st.button("📈 Export Summary", type="secondary"):
            summary_csv = bracket_summary.to_csv()
            st.download_button(
                label="⬇️ Download Summary CSV",
                data=summary_csv,
                file_name=f"olympus_billing_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
            st.success("✅ Summary ready for download!")
    
    # Footer
    st.divider()
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                    padding: 1.5rem; border-radius: 10px; margin: 2rem 0; 
                    border: 1px solid #dee2e6; text-align: center;">
            <p style="color: #4682B4; font-weight: 600; margin-bottom: 0.5rem;">💡 Dashboard Information</p>
            <p style="color: #708090; font-size: 0.9em; margin-bottom: 0;">This dashboard provides real-time insights into member billing brackets based on course enrollments.<br>
            Data is automatically updated from the Disco LMS integration.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

def show_analytics_overview():
    """Analytics overview page"""
    st.markdown('<div class="main-header">📊 Analytics Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="client-branding">Olympus Analytics Platform - System Status</div>', unsafe_allow_html=True)
    
    # System status
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Check member count
        member_count_query = "SELECT COUNT(*) as count FROM OLYMPUS_ANALYTICS.GOLD.GD_MEMBER_ENROLLMENT_DETAILS"
        member_result = execute_query(member_count_query)
        member_count = member_result.iloc[0]['COUNT'] if not member_result.empty else 0
        
        st.metric(
            "📊 Total Members",
            f"{member_count:,}",
            help="Total members in the system"
        )
    
    with col2:
        # Check enrolled members
        enrolled_query = "SELECT COUNT(*) as count FROM OLYMPUS_ANALYTICS.GOLD.GD_MEMBER_ENROLLMENT_DETAILS WHERE TOTAL_COURSES_ENROLLED > 0"
        enrolled_result = execute_query(enrolled_query)
        enrolled_count = enrolled_result.iloc[0]['COUNT'] if not enrolled_result.empty else 0
        
        st.metric(
            "🎓 Enrolled Members",
            f"{enrolled_count:,}",
            help="Members with active course enrollments"
        )
    
    with col3:
        # Check total revenue
        revenue_query = "SELECT SUM(MONTHLY_AMOUNT) as revenue FROM OLYMPUS_ANALYTICS.GOLD.GD_MEMBER_ENROLLMENT_DETAILS"
        revenue_result = execute_query(revenue_query)
        total_revenue = revenue_result.iloc[0]['REVENUE'] if not revenue_result.empty else 0
        
        st.metric(
            "💰 Monthly Revenue",
            f"${total_revenue:,.2f}",
            help="Total monthly recurring revenue"
        )
    
    st.divider()
    
    # Platform information
    st.markdown("""
    ### 🏔️ Welcome to Olympus Analytics
    
    This platform provides comprehensive analytics and billing insights for your organization's learning management system.
    
    **Key Features:**
    - **Real-time Data Integration** - Live data from Disco LMS API
    - **Comprehensive Member Tracking** - Detailed enrollment and billing information
    - **Advanced Analytics** - Interactive charts and insights
    - **Export Capabilities** - CSV downloads for further analysis
    - **Responsive Design** - Works on desktop and mobile devices
    
    **Navigation:**
    - Use the sidebar to navigate between different sections
    - The Billing Dashboard provides detailed member and revenue analytics
    - All data is updated in real-time from your integrated systems
    
    **Support:**
    - For technical support, contact your system administrator
    - For feature requests or feedback, use the appropriate channels
    """)
    
    # Data freshness indicator
    st.info("💡 **Tip**: Navigate to the Billing Dashboard to view detailed member enrollment and billing analytics with interactive filters and export capabilities.")

# Main application
def main():
    """Main application function"""
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown('<div class="sidebar-logo">🏔️ Olympus Analytics</div>', unsafe_allow_html=True)
        st.markdown('<div class="client-branding">Analytics Platform</div>', unsafe_allow_html=True)
        
        st.markdown("### Navigation")
        page = st.selectbox(
            "Select Page",
            ["📊 Analytics Overview", "💰 Billing Dashboard"],
            index=1  # Default to Billing Dashboard
        )
        
        st.markdown("---")
        
        # System status indicators
        st.markdown("### System Status")
        st.success("✅ Snowflake Connected")
        st.success("✅ Data Pipeline Active")
        
        # Quick stats
        try:
            quick_stats_query = """
            SELECT 
                COUNT(*) as total_members,
                SUM(CASE WHEN TOTAL_COURSES_ENROLLED > 0 THEN 1 ELSE 0 END) as enrolled_members,
                SUM(MONTHLY_AMOUNT) as total_revenue
            FROM OLYMPUS_ANALYTICS.GOLD.GD_MEMBER_ENROLLMENT_DETAILS
            """
            stats = execute_query(quick_stats_query)
            
            if not stats.empty:
                st.markdown("### Quick Stats")
                st.write(f"👥 Members: {stats.iloc[0]['TOTAL_MEMBERS']:,}")
                st.write(f"🎓 Enrolled: {stats.iloc[0]['ENROLLED_MEMBERS']:,}")
                st.write(f"💰 Revenue: ${stats.iloc[0]['TOTAL_REVENUE']:,.2f}")
        except:
            st.warning("⚠️ Unable to load quick stats")
    
    # Main content area
    if "Billing" in page:
        show_billing_dashboard()
    else:
        show_analytics_overview()

# Run the application
if __name__ == "__main__":
    main()