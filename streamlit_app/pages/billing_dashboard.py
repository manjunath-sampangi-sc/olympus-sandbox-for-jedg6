import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import os
from utils.csv_export import BillingCSVExporter
from utils.snowflake_connector import SnowflakeConnector

def show_billing_dashboard():
    """Display billing dashboard with member billing brackets analysis"""
    # Page configuration
    st.set_page_config(
        page_title="Billing Dashboard - Olympus Analytics",
        page_icon="💰",
        layout="wide"
    )
    
    # Initialize components
    @st.cache_resource
    def init_components():
        return BillingCSVExporter()
    
    exporter = init_components()
    
    # Page header
    st.title("💰 Member Billing Brackets Dashboard")
    st.markdown("**Real-time billing insights from Disco LMS data**")
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Get available data for filters
    available_months = exporter.get_available_months()
    available_communities = exporter.get_available_communities()
    
    if not available_months:
        st.error("No billing data available. Please ensure the data pipeline has been run.")
        st.stop()
    
    # Month filter
    selected_month = st.sidebar.selectbox(
        "Select Billing Month",
        options=available_months,
        index=0 if available_months else None,
        help="Choose the billing month to analyze"
    )
    
    # Community filter
    community_options = ["All Communities"] + [
        f"{row['GROUP_NAME']} ({row['COMMUNITY_ID']})"
        for _, row in available_communities.iterrows()
    ] if not available_communities.empty else ["All Communities"]
    
    selected_community_display = st.sidebar.selectbox(
        "Select Community/Group",
        options=community_options,
        index=0,
        help="Filter by specific community or view all"
    )
    
    # Extract community ID from selection
    selected_community_id = None
    if selected_community_display != "All Communities" and not available_communities.empty:
        # Extract community ID from the display string
        community_id = selected_community_display.split("(")[-1].replace(")", "")
        selected_community_id = community_id
    
    # Billing bracket filter
    billing_bracket_filter = st.sidebar.selectbox(
        "Filter by Billing Bracket",
        options=["All Brackets", "$0", "$10", "$50"],
        index=0,
        help="Filter by specific billing bracket"
    )
    
    selected_bracket = None if billing_bracket_filter == "All Brackets" else billing_bracket_filter
    
    # Load data
    with st.spinner("Loading billing data..."):
        billing_data = exporter.get_billing_data(
            billing_month=selected_month,
            community_id=selected_community_id,
            billing_bracket=selected_bracket
        )
        
        summary_data = exporter.get_billing_summary(
            billing_month=selected_month,
            community_id=selected_community_id
        )
    
    if billing_data.empty:
        st.warning("No data available for the selected filters.")
        st.stop()
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate metrics
    total_members = len(billing_data)
    total_revenue = billing_data['MONTHLY_AMOUNT'].sum()
    avg_revenue_per_member = billing_data['MONTHLY_AMOUNT'].mean()
    active_communities = billing_data['COMMUNITY_ID'].nunique()
    
    with col1:
        st.metric(
            "Total Members",
            f"{total_members:,}",
            help="Total number of members in selected period"
        )
    
    with col2:
        st.metric(
            "Total Revenue",
            f"${total_revenue:,.2f}",
            help="Total monthly revenue from all billing brackets"
        )
    
    with col3:
        st.metric(
            "Avg Revenue/Member",
            f"${avg_revenue_per_member:.2f}",
            help="Average monthly revenue per member"
        )
    
    with col4:
        st.metric(
            "Active Communities",
            f"{active_communities}",
            help="Number of communities with active members"
        )
    
    st.divider()
    
    # Charts section
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Billing Bracket Distribution")
        
        # Pie chart for billing bracket distribution
        bracket_counts = billing_data['BILLING_BRACKET'].value_counts()
        
        fig_pie = px.pie(
            values=bracket_counts.values,
            names=bracket_counts.index,
            title="Members by Billing Bracket",
            color_discrete_map={
                '$0': '#ff6b6b',
                '$10': '#4ecdc4', 
                '$50': '#45b7d1'
            }
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.subheader("💰 Revenue by Billing Bracket")
        
        # Bar chart for revenue by bracket
        revenue_by_bracket = billing_data.groupby('BILLING_BRACKET')['MONTHLY_AMOUNT'].sum().reset_index()
        
        fig_bar = px.bar(
            revenue_by_bracket,
            x='BILLING_BRACKET',
            y='MONTHLY_AMOUNT',
            title="Total Revenue by Bracket",
            color='BILLING_BRACKET',
            color_discrete_map={
                '$0': '#ff6b6b',
                '$10': '#4ecdc4', 
                '$50': '#45b7d1'
            }
        )
        fig_bar.update_layout(showlegend=False)
        fig_bar.update_yaxes(title="Revenue ($)")
        fig_bar.update_xaxes(title="Billing Bracket")
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Community breakdown (only if viewing all communities)
    if not selected_community_id:  # Only show if viewing all communities
        st.subheader("🏢 Community Breakdown")
        
        community_summary = billing_data.groupby(['GROUP_NAME', 'BILLING_BRACKET']).agg({
            'MEMBER_ID': 'count',
            'MONTHLY_AMOUNT': 'sum'
        }).reset_index()
        community_summary.columns = ['Community', 'Billing Bracket', 'Member Count', 'Revenue']
        
        # Stacked bar chart for community breakdown
        fig_community = px.bar(
            community_summary,
            x='Community',
            y='Revenue',
            color='Billing Bracket',
            title="Revenue by Community and Billing Bracket",
            color_discrete_map={
                '$0': '#ff6b6b',
                '$10': '#4ecdc4', 
                '$50': '#45b7d1'
            }
        )
        fig_community.update_xaxes(tickangle=45)
        st.plotly_chart(fig_community, use_container_width=True)
    
    st.divider()
    
    # Summary tables
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Billing Bracket Summary")
        
        bracket_summary = billing_data.groupby('BILLING_BRACKET').agg({
            'MEMBER_ID': 'count',
            'MONTHLY_AMOUNT': ['sum', 'mean']
        }).round(2)
        
        bracket_summary.columns = ['Member Count', 'Total Revenue', 'Avg Revenue']
        bracket_summary['Percentage'] = (bracket_summary['Member Count'] / total_members * 100).round(1)
        
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
        enrollment_insights['Avg Revenue'] = (enrollment_insights['Revenue'].astype(float) / enrollment_insights['Members'].astype(float)).round(2)
        
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
    
    # Export section
    st.subheader("📤 Export Data")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.write("Export the current filtered data for operations and finance teams.")
    
    with col2:
        if st.button("📊 Export Detailed Data", type="primary"):
            try:
                filename = f"billing_data_{selected_month.replace('-', '')}"
                if selected_community_id:
                    filename += f"_community_{selected_community_id}"
                
                filepath = exporter.export_to_csv(billing_data, filename)
                
                st.success(f"✅ Data exported successfully!")
                st.info(f"📁 File saved: {filepath}")
                
                # Provide download button
                with open(filepath, 'rb') as file:
                    st.download_button(
                        label="⬇️ Download CSV",
                        data=file.read(),
                        file_name=os.path.basename(filepath),
                        mime="text/csv"
                    )
                    
            except Exception as e:
                st.error(f"❌ Export failed: {str(e)}")
    
    with col3:
        if st.button("📈 Export Summary", type="secondary"):
            try:
                filename = f"billing_summary_{selected_month.replace('-', '')}"
                if selected_community_id:
                    filename += f"_community_{selected_community_id}"
                
                filepath = exporter.export_to_csv(summary_data, filename)
                
                st.success(f"✅ Summary exported successfully!")
                st.info(f"📁 File saved: {filepath}")
                
                # Provide download button
                with open(filepath, 'rb') as file:
                    st.download_button(
                        label="⬇️ Download Summary CSV",
                        data=file.read(),
                        file_name=os.path.basename(filepath),
                        mime="text/csv"
                    )
                    
            except Exception as e:
                st.error(f"❌ Export failed: {str(e)}")
    
    # Detailed member data
    st.subheader("📋 Detailed Member Data")
    
    # Search functionality
    search_term = st.text_input("🔍 Search members (by name or email)", placeholder="Enter member name or email...")
    
    filtered_data = billing_data.copy()
    if search_term:
        filtered_data = billing_data[
            billing_data['MEMBER_NAME'].str.contains(search_term, case=False, na=False) |
            billing_data['EMAIL'].str.contains(search_term, case=False, na=False)
        ]
    
    # Display detailed data table
    st.dataframe(
        filtered_data[[
            'MEMBER_NAME', 'EMAIL', 'GROUP_NAME', 'BILLING_BRACKET', 
            'MONTHLY_AMOUNT', 'COURSE_COUNT_ACTIVE', 'HAS_HOME_COURSE',
            'BILLING_CATEGORY_DESCRIPTION', 'ENROLLED_COURSES'
        ]],
        use_container_width=True,
        column_config={
            "MONTHLY_AMOUNT": st.column_config.NumberColumn(
                "Monthly Amount",
                format="$%.2f"
            ),
            "HAS_HOME_COURSE": st.column_config.CheckboxColumn(
                "Has Home Course"
            ),
            "ENROLLED_COURSES": st.column_config.TextColumn(
                "Enrolled Courses",
                width="large"
            )
        },
        hide_index=True
    )
    
    # Footer
    st.divider()
    st.markdown(
        """<div style='text-align: center; color: #666; font-size: 0.8em;'>
        💡 This dashboard provides real-time insights into member billing brackets based on course enrollments.<br>
        Data is automatically updated from the Disco LMS integration.
        </div>""",
        unsafe_allow_html=True
    )