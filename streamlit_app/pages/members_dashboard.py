import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timezone
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.snowflake_connector import get_snowflake_connector

def show_members_dashboard():
    """Display members dashboard with comprehensive member data"""
    
    # Page header with client branding
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0; margin-bottom: 2rem;">
        <h1 style="color: #9a262c; margin-bottom: 0.5rem;">👥 Members Dashboard</h1>
        <p style="color: #cccccc; font-style: italic; margin-bottom: 0.5rem;">D2D Experts Member Analytics</p>
        <p style="color: #666; font-weight: 500;">Comprehensive member data from Disco LMS</p>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        # Get Snowflake connector
        connector = get_snowflake_connector()
        
        # Filters section at the top
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                    padding: 1.5rem; border-radius: 10px; margin: 1rem 0; 
                    border: 1px solid #dee2e6; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h3 style="color: #9a262c; margin-bottom: 1rem; text-align: center;">🔍 Member Filters</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Filter controls
        filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4, gap="medium")
        
        # Get available communities for filter
        communities_query = """
        SELECT DISTINCT 
            COMMUNITY_ID,
            COMMUNITY_NAME
        FROM OLYMPUS_ANALYTICS.GOLD.DISCO_MEMBERS 
        WHERE COMMUNITY_ID IS NOT NULL
        ORDER BY COMMUNITY_NAME
        """
        
        try:
            communities_df = connector.execute_query(communities_query)
            community_options = ["All Communities"] + [
                f"{row['COMMUNITY_NAME']} ({row['COMMUNITY_ID']})"
                for _, row in communities_df.iterrows()
            ] if not communities_df.empty else ["All Communities"]
        except:
            community_options = ["All Communities"]
        
        with filter_col1:
            st.subheader("🏢 Community")
            selected_community = st.selectbox(
                "Select Community",
                options=community_options,
                index=0,
                help="Filter members by community"
            )
        
        with filter_col2:
            st.subheader("👤 Member Status")
            status_filter = st.selectbox(
                "Member Status",
                options=["All Status", "Active", "Inactive"],
                index=0,
                help="Filter by member status"
            )
        
        with filter_col3:
            st.subheader("📧 Email Domain")
            email_domain_filter = st.text_input(
                "Email Domain Filter",
                placeholder="e.g., company.com",
                help="Filter by email domain"
            )
        
        with filter_col4:
            st.subheader("🔍 Search")
            search_term = st.text_input(
                "Search Members",
                placeholder="Name or email...",
                help="Search by name or email"
            )
        
        st.divider()
        
        # Build query with filters
        base_query = """
        SELECT 
            ID as MEMBER_ID,
            FIRST_NAME,
            LAST_NAME,
            EMAIL,
            COMMUNITY_ID,
            COMMUNITY_NAME,
            ROLE,
            STATUS,
            CREATED_AT,
            UPDATED_AT,
            LAST_LOGIN_AT,
            PROFILE_PICTURE_URL,
            BIO,
            LOCATION,
            TIMEZONE
        FROM OLYMPUS_ANALYTICS.GOLD.DISCO_MEMBERS
        WHERE 1=1
        """
        
        # Add filters to query
        query_params = []
        
        # Community filter
        if selected_community != "All Communities":
            community_id = selected_community.split("(")[-1].replace(")", "")
            base_query += " AND COMMUNITY_ID = %s"
            query_params.append(community_id)
        
        # Status filter
        if status_filter != "All Status":
            base_query += " AND UPPER(STATUS) = %s"
            query_params.append(status_filter.upper())
        
        # Email domain filter
        if email_domain_filter:
            base_query += " AND EMAIL LIKE %s"
            query_params.append(f"%{email_domain_filter}%")
        
        # Search filter
        if search_term:
            base_query += " AND (UPPER(FIRST_NAME) LIKE %s OR UPPER(LAST_NAME) LIKE %s OR UPPER(EMAIL) LIKE %s)"
            search_pattern = f"%{search_term.upper()}%"
            query_params.extend([search_pattern, search_pattern, search_pattern])
        
        base_query += " ORDER BY LAST_NAME, FIRST_NAME"
        
        # Execute query
        with st.spinner("Loading member data..."):
            if query_params:
                members_df = connector.execute_query(base_query, query_params)
            else:
                members_df = connector.execute_query(base_query)
        
        if members_df.empty:
            st.warning("No members found matching the selected filters.")
            return
        
        # Key metrics section
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                    padding: 1.5rem; border-radius: 10px; margin: 1rem 0; 
                    border: 1px solid #dee2e6; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h3 style="color: #9a262c; margin-bottom: 1rem; text-align: center;">📊 Member Statistics</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Calculate metrics
        total_members = len(members_df)
        active_members = len(members_df[members_df['STATUS'].str.upper() == 'ACTIVE']) if 'STATUS' in members_df.columns else 0
        unique_communities = members_df['COMMUNITY_ID'].nunique() if 'COMMUNITY_ID' in members_df.columns else 0
        unique_domains = members_df['EMAIL'].str.split('@').str[1].nunique() if 'EMAIL' in members_df.columns else 0
        
        # Metrics display
        col1, col2, col3, col4 = st.columns(4, gap="medium")
        
        with col1:
            st.metric(
                "Total Members",
                f"{total_members:,}",
                help="Total number of members matching filters"
            )
        
        with col2:
            st.metric(
                "Active Members",
                f"{active_members:,}",
                help="Number of active members"
            )
        
        with col3:
            st.metric(
                "Communities",
                f"{unique_communities:,}",
                help="Number of unique communities"
            )
        
        with col4:
            st.metric(
                "Email Domains",
                f"{unique_domains:,}",
                help="Number of unique email domains"
            )
        
        st.divider()
        
        # Charts section
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                    padding: 1.5rem; border-radius: 10px; margin: 1rem 0; 
                    border: 1px solid #dee2e6; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h3 style="color: #9a262c; margin-bottom: 1rem; text-align: center;">📈 Member Analytics</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2, gap="large")
        
        with col1:
            st.subheader("👥 Members by Community")
            
            if 'COMMUNITY_NAME' in members_df.columns:
                community_counts = members_df['COMMUNITY_NAME'].value_counts().reset_index()
                community_counts.columns = ['Community', 'Member Count']
                
                fig_community = px.pie(
                    community_counts,
                    values='Member Count',
                    names='Community',
                    title="Member Distribution by Community",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig_community.update_layout(
                    title_x=0.5,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12)
                )
                st.plotly_chart(fig_community, use_container_width=True)
            else:
                st.info("Community data not available")
        
        with col2:
            st.subheader("📊 Member Status Distribution")
            
            if 'STATUS' in members_df.columns:
                status_counts = members_df['STATUS'].value_counts().reset_index()
                status_counts.columns = ['Status', 'Count']
                
                fig_status = px.bar(
                    status_counts,
                    x='Status',
                    y='Count',
                    title="Members by Status",
                    color='Status',
                    color_discrete_map={
                        'Active': '#28a745',
                        'Inactive': '#dc3545',
                        'Pending': '#ffc107'
                    }
                )
                fig_status.update_layout(
                    title_x=0.5,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12)
                )
                st.plotly_chart(fig_status, use_container_width=True)
            else:
                st.info("Status data not available")
        
        st.divider()
        
        # Member data table
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                    padding: 1.5rem; border-radius: 10px; margin: 1rem 0; 
                    border: 1px solid #dee2e6; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h3 style="color: #9a262c; margin-bottom: 1rem; text-align: center;">📋 Member Directory</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Prepare display dataframe
        display_df = members_df.copy()
        
        # Format dates
        date_columns = ['CREATED_AT', 'UPDATED_AT', 'LAST_LOGIN_AT']
        for col in date_columns:
            if col in display_df.columns:
                display_df[col] = pd.to_datetime(display_df[col], errors='coerce').dt.strftime('%Y-%m-%d %H:%M')
        
        # Create full name column
        if 'FIRST_NAME' in display_df.columns and 'LAST_NAME' in display_df.columns:
            display_df['FULL_NAME'] = display_df['FIRST_NAME'].fillna('') + ' ' + display_df['LAST_NAME'].fillna('')
            display_df['FULL_NAME'] = display_df['FULL_NAME'].str.strip()
        
        # Select and reorder columns for display
        display_columns = []
        if 'FULL_NAME' in display_df.columns:
            display_columns.append('FULL_NAME')
        if 'EMAIL' in display_df.columns:
            display_columns.append('EMAIL')
        if 'COMMUNITY_NAME' in display_df.columns:
            display_columns.append('COMMUNITY_NAME')
        if 'ROLE' in display_df.columns:
            display_columns.append('ROLE')
        if 'STATUS' in display_df.columns:
            display_columns.append('STATUS')
        if 'LOCATION' in display_df.columns:
            display_columns.append('LOCATION')
        if 'LAST_LOGIN_AT' in display_df.columns:
            display_columns.append('LAST_LOGIN_AT')
        if 'CREATED_AT' in display_df.columns:
            display_columns.append('CREATED_AT')
        
        # Filter to available columns
        available_columns = [col for col in display_columns if col in display_df.columns]
        
        if available_columns:
            final_df = display_df[available_columns]
            
            # Display the dataframe
            st.dataframe(
                final_df,
                use_container_width=True,
                column_config={
                    "FULL_NAME": st.column_config.TextColumn(
                        "Full Name",
                        width="medium"
                    ),
                    "EMAIL": st.column_config.TextColumn(
                        "Email",
                        width="medium"
                    ),
                    "COMMUNITY_NAME": st.column_config.TextColumn(
                        "Community",
                        width="medium"
                    ),
                    "ROLE": st.column_config.TextColumn(
                        "Role",
                        width="small"
                    ),
                    "STATUS": st.column_config.TextColumn(
                        "Status",
                        width="small"
                    ),
                    "LOCATION": st.column_config.TextColumn(
                        "Location",
                        width="medium"
                    ),
                    "LAST_LOGIN_AT": st.column_config.TextColumn(
                        "Last Login",
                        width="medium"
                    ),
                    "CREATED_AT": st.column_config.TextColumn(
                        "Created",
                        width="medium"
                    )
                },
                hide_index=True
            )
            
            # Export functionality
            st.divider()
            
            col1, col2, col3 = st.columns([2, 1, 1], gap="medium")
            
            with col1:
                st.markdown("**Export Member Data**")
                st.write(f"Export {len(final_df):,} member records to CSV format")
            
            with col2:
                csv_data = final_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_data,
                    file_name=f"members_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    help="Download member data as CSV file"
                )
            
            with col3:
                if st.button("🔄 Refresh Data", help="Refresh member data"):
                    st.rerun()
        
        else:
            st.error("No displayable columns found in member data")
    
    except Exception as e:
        st.error(f"Error loading member data: {str(e)}")
        st.info("Please ensure the data sync has been run and member data is available in the database.")
    
    # Footer
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                    padding: 1.5rem; border-radius: 10px; margin: 2rem 0; 
                    border: 1px solid #dee2e6; text-align: center;">
            <p style="color: #9a262c; font-weight: 600; margin-bottom: 0.5rem;">👥 Members Dashboard</p>
            <p style="color: #666; font-size: 0.9em; margin-bottom: 0;">Comprehensive member directory and analytics from Disco LMS data.</p>
        </div>
        """,
        unsafe_allow_html=True
    )