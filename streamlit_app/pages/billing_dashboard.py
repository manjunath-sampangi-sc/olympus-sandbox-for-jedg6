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
    # Initialize components
    @st.cache_resource
    def init_components():
        return BillingCSVExporter()
    
    exporter = init_components()
    
    # Page header with client branding
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0; margin-bottom: 2rem;">
        <h1 style="color: #4682B4; margin-bottom: 0.5rem;">💰 Member Billing Brackets Dashboard</h1>
        <p style="color: #87CEEB; font-style: italic; margin-bottom: 0.5rem;">D2D Experts Billing Analytics</p>
        <p style="color: #708090; font-weight: 500;">Real-time billing insights from Disco LMS data</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Filters section at the top
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                padding: 1.5rem; border-radius: 10px; margin: 1rem 0; 
                border: 1px solid #dee2e6; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <h3 style="color: #4682B4; margin-bottom: 1rem; text-align: center;">🔍 Dashboard Filters</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Filter controls in organized columns
    filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4, gap="medium")
    
    with filter_col1:
        st.subheader("📊 Data Layer")
        data_layer = st.selectbox(
            "Select Data Layer",
            options=["Gold", "Silver", "Bronze"],
            index=0,
            help="Choose data layer: Gold (processed analytics), Silver (transformed), Bronze (raw API data)"
        )
    
    # Update exporter with selected layer
    exporter.set_data_layer(data_layer.lower())
    
    # Data layer indicator in main area
    layer_colors = {"Gold": "🟡", "Silver": "🔘", "Bronze": "🟤"}
    layer_descriptions = {
        "Gold": "Processed analytics with calculated billing brackets",
        "Silver": "Transformed data with real-time billing calculations", 
        "Bronze": "Raw API data with on-the-fly billing logic"
    }
    
    st.info(f"{layer_colors.get(data_layer, '📊')} **Current Data Layer: {data_layer}** - {layer_descriptions.get(data_layer, 'Data layer information')}")
    st.divider()
    
    # Get available data for filters
    available_months = exporter.get_available_months()
    available_communities = exporter.get_available_communities()
    
    if not available_months:
        st.error("No billing data available. Please ensure the data pipeline has been run.")
        st.stop()
    
    with filter_col2:
        st.subheader("📅 Billing Month")
        selected_month = st.selectbox(
            "Select Billing Month",
            options=available_months,
            index=0 if available_months else None,
            help="Choose the billing month to analyze"
        )
    
    with filter_col3:
        st.subheader("🏢 Community")
        community_options = ["All Communities"] + [
            f"{row['GROUP_NAME']} ({row['COMMUNITY_ID']})"
            for _, row in available_communities.iterrows()
        ] if not available_communities.empty else ["All Communities"]
        
        selected_community_display = st.selectbox(
            "Select Community/Group",
            options=community_options,
            index=0,
            help="Filter by specific community or view all"
        )
    
    with filter_col4:
        st.subheader("💰 Billing Bracket")
        billing_bracket_filter = st.selectbox(
            "Filter by Billing Bracket",
            options=["All Brackets", "$0", "$10", "$50"],
            index=0,
            help="Filter by specific billing bracket"
        )
    
    # Extract community ID from selection
    selected_community_id = None
    if selected_community_display != "All Communities" and not available_communities.empty:
        # Extract community ID from the display string
        community_id = selected_community_display.split("(")[-1].replace(")", "")
        selected_community_id = community_id
    
    selected_bracket = None if billing_bracket_filter == "All Brackets" else billing_bracket_filter
    
    # Add spacing after filters
    st.divider()
    
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
        st.warning(f"No data available for the selected filters in the {data_layer} layer.")
        if data_layer.lower() in ['gold', 'silver']:
            st.info("💡 **Tip**: Try running the data sync to populate the database with real data from the Disco API.")
        st.stop()
    
    # Key metrics section with professional styling
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                padding: 1.5rem; border-radius: 10px; margin: 1rem 0; 
                border: 1px solid #dee2e6; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <h3 style="color: #4682B4; margin-bottom: 1rem; text-align: center;">📊 Key Performance Metrics</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Calculate metrics
    total_members = len(billing_data)
    total_revenue = billing_data['MONTHLY_AMOUNT'].sum()
    avg_revenue_per_member = billing_data['MONTHLY_AMOUNT'].mean()
    active_communities = billing_data['COMMUNITY_ID'].nunique()
    
    # Metrics in organized columns with consistent spacing
    col1, col2, col3, col4 = st.columns(4, gap="medium")
    
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
    
    # Charts section with professional header
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                padding: 1.5rem; border-radius: 10px; margin: 1rem 0; 
                border: 1px solid #dee2e6; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <h3 style="color: #4682B4; margin-bottom: 1rem; text-align: center;">📈 Billing Analytics Charts</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Charts in organized columns with consistent spacing
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.subheader("📊 Billing Bracket Distribution")
        
        # Pie chart for billing bracket distribution
        bracket_counts = billing_data['BILLING_BRACKET'].value_counts()
        
        fig_pie = px.pie(
            values=bracket_counts.values,
            names=bracket_counts.index,
            title="Members by Billing Bracket",
            color_discrete_map={
                    '$0': '#87CEEB',
                    '$10': '#4682B4',
                    '$50': '#1e3a8a'
                }
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(
            title_x=0.5,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12)
        )
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
                    '$0': '#87CEEB',
                    '$10': '#4682B4',
                    '$50': '#1e3a8a'
                }
        )
        fig_bar.update_layout(
            showlegend=False,
            title_x=0.5,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12)
        )
        fig_bar.update_yaxes(title="Revenue ($)")
        fig_bar.update_xaxes(title="Billing Bracket")
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Community breakdown section with professional styling
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                padding: 1.5rem; border-radius: 10px; margin: 1rem 0; 
                border: 1px solid #dee2e6; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <h3 style="color: #4682B4; margin-bottom: 1rem; text-align: center;">🏢 Community Breakdown</h3>
    </div>
    """, unsafe_allow_html=True)
    
    community_summary = billing_data.groupby(['GROUP_NAME', 'BILLING_BRACKET']).agg({
        'MEMBER_ID': 'count',
        'MONTHLY_AMOUNT': 'sum'
    }).reset_index()
    community_summary.columns = ['Community', 'Billing Bracket', 'Member Count', 'Revenue']
    
    # Stacked bar chart for community breakdown with improved styling
    fig_community = px.bar(
        community_summary,
        x='Community',
        y='Revenue',
        color='Billing Bracket',
        title="Revenue by Community and Billing Bracket",
        color_discrete_map={
            '$0': '#87CEEB',
            '$10': '#4682B4', 
            '$50': '#1e3a8a'
        }
    )
    fig_community.update_xaxes(tickangle=45)
    fig_community.update_layout(
        title_x=0.5,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_community, use_container_width=True)
    
    st.divider()
    
    # Summary tables section with professional header
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                padding: 1.5rem; border-radius: 10px; margin: 1rem 0; 
                border: 1px solid #dee2e6; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <h3 style="color: #4682B4; margin-bottom: 1rem; text-align: center;">📊 Summary Analytics</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Summary tables in organized columns with consistent spacing
    col1, col2 = st.columns(2, gap="large")
    
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
    
    # Export section with professional styling
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                padding: 1.5rem; border-radius: 10px; margin: 1rem 0; 
                border: 1px solid #dee2e6; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <h3 style="color: #4682B4; margin-bottom: 1rem; text-align: center;">📤 Export Data</h3>
        <p style="text-align: center; color: #708090; margin-bottom: 0;">Export the current filtered data for operations and finance teams</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Export buttons in organized columns
    col1, col2, col3 = st.columns([2, 1, 1], gap="medium")
    
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
    
    # Detailed member data section with professional styling
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                padding: 1.5rem; border-radius: 10px; margin: 1rem 0; 
                border: 1px solid #dee2e6; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <h3 style="color: #4682B4; margin-bottom: 1rem; text-align: center;">📋 Detailed Member Data</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Search functionality with better styling
    search_term = st.text_input(
        "🔍 Search members (by name or email)", 
        placeholder="Enter member name or email...",
        help="Search through member names or email addresses to find specific records"
    )
    
    filtered_data = billing_data.copy()
    if search_term:
        # Search in member name, email, and company name
        search_conditions = []
        
        if 'MEMBER_NAME' in billing_data.columns:
            search_conditions.append(billing_data['MEMBER_NAME'].str.contains(search_term, case=False, na=False))
        
        if 'EMAIL' in billing_data.columns:
            search_conditions.append(billing_data['EMAIL'].str.contains(search_term, case=False, na=False))
            
        if 'COMPANY_NAME' in billing_data.columns:
            search_conditions.append(billing_data['COMPANY_NAME'].str.contains(search_term, case=False, na=False))
        
        if search_conditions:
            # Combine all search conditions with OR logic
            combined_condition = search_conditions[0]
            for condition in search_conditions[1:]:
                combined_condition = combined_condition | condition
            filtered_data = billing_data[combined_condition]
    
    # Display detailed data table with course enrollment information
    display_columns = ['MEMBER_NAME', 'EMAIL', 'COMPANY_NAME', 'BILLING_BRACKET', 
                      'MONTHLY_AMOUNT', 'TOTAL_COURSES_ENROLLED', 'BILLING_CATEGORY_DESCRIPTION']
    
    # Add ENROLLED_COURSES column if it exists in the data
    if 'ENROLLED_COURSES' in filtered_data.columns:
        display_columns.append('ENROLLED_COURSES')
    
    st.dataframe(
        filtered_data[display_columns],
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
    
    # Footer with improved styling
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