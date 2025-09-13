import streamlit as st
import pandas as pd
from datetime import datetime, timezone
import time
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_sync_manager import get_sync_manager

def show_data_sync():
    """Display data synchronization dashboard"""
    
    # Page header with client branding
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0; margin-bottom: 2rem;">
        <h1 style="color: #9a262c; margin-bottom: 0.5rem;">🔄 Data Synchronization</h1>
        <p style="color: #cccccc; font-style: italic; margin-bottom: 0.5rem;">D2D Experts Data Management</p>
        <p style="color: #666; font-weight: 500;">Real-time sync control and monitoring for Disco LMS data</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get sync manager
    sync_manager = get_sync_manager()
    
    # Sync Status Section
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                padding: 1.5rem; border-radius: 10px; margin: 1rem 0; 
                border: 1px solid #dee2e6; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <h3 style="color: #9a262c; margin-bottom: 1rem; text-align: center;">📊 Sync Status</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Get current status
    status = sync_manager.get_sync_status()
    
    # Status metrics
    col1, col2, col3, col4 = st.columns(4, gap="medium")
    
    with col1:
        if status["is_running"]:
            st.metric("Sync Status", "🔄 Running", help="Data sync is currently in progress")
        else:
            st.metric("Sync Status", "✅ Ready", help="Ready for next sync operation")
    
    with col2:
        scheduler_status = "🟢 Active" if status["scheduler_running"] else "🔴 Stopped"
        st.metric("Scheduler", scheduler_status, help="Hourly automatic sync scheduler status")
    
    with col3:
        api_status = "🟢 Ready" if status["api_client_ready"] else "🔴 Not Ready"
        st.metric("API Client", api_status, help="Disco API client connection status")
    
    with col4:
        last_records = status.get("records_synced", 0)
        st.metric("Last Sync Records", f"{last_records:,}", help="Number of records synced in last operation")
    
    # Last sync summary
    if status["last_sync"]:
        last_sync_time = datetime.fromisoformat(status["last_sync"].replace('Z', '+00:00'))
        time_ago = datetime.now(timezone.utc) - last_sync_time
        hours_ago = int(time_ago.total_seconds() / 3600)
        minutes_ago = int((time_ago.total_seconds() % 3600) / 60)
        
        if hours_ago > 0:
            time_str = f"{hours_ago}h {minutes_ago}m ago"
        else:
            time_str = f"{minutes_ago}m ago"
        
        sync_type = status.get("sync_type", "unknown")
        duration = status.get("duration_seconds", 0)
        
        st.info(f"📅 Last {sync_type} sync: {time_str} • {last_records:,} records • {duration:.1f}s duration")
    else:
        st.info("📅 No sync performed yet")
    
    # Error display
    if status["last_error"]:
        st.error(f"❌ Last sync error: {status['last_error']}")
    
    st.divider()
    
    # Manual Sync Controls
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                padding: 1.5rem; border-radius: 10px; margin: 1rem 0; 
                border: 1px solid #dee2e6; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <h3 style="color: #9a262c; margin-bottom: 1rem; text-align: center;">🎮 Manual Sync Controls</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1, 1], gap="medium")
    
    with col1:
        st.markdown("""
        **On-Demand Data Sync**
        
        Manually trigger a complete data synchronization from the Disco API. This will:
        - Fetch all communities, members, products, and enrollments
        - Update existing records and add new ones (upsert)
        - Refresh billing calculations and analytics
        """)
    
    with col2:
        sync_disabled = status["is_running"] or not status["api_client_ready"]
        
        if st.button(
            "🔄 Sync Now", 
            type="primary", 
            disabled=sync_disabled,
            help="Trigger immediate data synchronization" if not sync_disabled else "Sync in progress or API not ready"
        ):
            with st.spinner("Starting data synchronization..."):
                result = sync_manager.sync_data_now(sync_type="manual")
                
                if result["success"]:
                    st.success(f"✅ {result['message']}")
                    st.balloons()
                else:
                    st.error(f"❌ {result['message']}")
                
                # Refresh the page to show updated status
                time.sleep(2)
                st.rerun()
    
    with col3:
        if st.button(
            "📊 Refresh Status", 
            help="Refresh sync status display"
        ):
            st.rerun()
    
    st.divider()
    
    # Scheduler Controls
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                padding: 1.5rem; border-radius: 10px; margin: 1rem 0; 
                border: 1px solid #dee2e6; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <h3 style="color: #9a262c; margin-bottom: 1rem; text-align: center;">⏰ Automated Scheduler</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1, 1], gap="medium")
    
    with col1:
        st.markdown("""
        **Hourly Automatic Sync**
        
        Enable automatic data synchronization every hour to keep your data up-to-date:
        - Runs in the background without user intervention
        - Maintains data freshness for real-time analytics
        - Can be started/stopped as needed
        """)
    
    with col2:
        if status["scheduler_running"]:
            if st.button(
                "⏹️ Stop Scheduler", 
                type="secondary",
                help="Stop the hourly automatic sync"
            ):
                sync_manager.stop_scheduler()
                st.success("🛑 Scheduler stopped")
                time.sleep(1)
                st.rerun()
        else:
            scheduler_disabled = not status["api_client_ready"]
            if st.button(
                "▶️ Start Scheduler", 
                type="primary",
                disabled=scheduler_disabled,
                help="Start hourly automatic sync" if not scheduler_disabled else "API client not ready"
            ):
                sync_manager.start_scheduler()
                st.success("🚀 Scheduler started - will sync every hour")
                time.sleep(1)
                st.rerun()
    
    with col3:
        next_sync_info = "Next sync: Top of next hour" if status["scheduler_running"] else "Scheduler not running"
        st.info(next_sync_info)
    
    st.divider()
    
    # Data Overview
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                padding: 1.5rem; border-radius: 10px; margin: 1rem 0; 
                border: 1px solid #dee2e6; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <h3 style="color: #9a262c; margin-bottom: 1rem; text-align: center;">📈 Data Overview</h3>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        # Get data counts from Snowflake
        from utils.snowflake_connector import get_snowflake_connector
        
        connector = get_snowflake_connector()
        
        # Query data counts
        queries = {
            "Communities": "SELECT COUNT(*) as count FROM OLYMPUS_ANALYTICS.GOLD.DISCO_COMMUNITIES",
            "Members": "SELECT COUNT(*) as count FROM OLYMPUS_ANALYTICS.GOLD.DISCO_MEMBERS", 
            "Products": "SELECT COUNT(*) as count FROM OLYMPUS_ANALYTICS.GOLD.DISCO_PRODUCTS",
            "Enrollments": "SELECT COUNT(*) as count FROM OLYMPUS_ANALYTICS.GOLD.DISCO_ENROLLMENTS"
        }
        
        col1, col2, col3, col4 = st.columns(4, gap="medium")
        
        for i, (table_name, query) in enumerate(queries.items()):
            try:
                result = connector.execute_query(query)
                count = result.iloc[0]['COUNT'] if not result.empty else 0
                
                with [col1, col2, col3, col4][i]:
                    st.metric(
                        table_name,
                        f"{count:,}",
                        help=f"Total number of {table_name.lower()} in the database"
                    )
            except Exception as e:
                with [col1, col2, col3, col4][i]:
                    st.metric(table_name, "Error", help=f"Could not fetch count: {str(e)}")
    
    except Exception as e:
        st.warning(f"Could not fetch data overview: {str(e)}")
    
    # Configuration Info
    st.divider()
    
    with st.expander("🔧 Configuration & Help"):
        st.markdown("""
        ### Data Sync Configuration
        
        **API Configuration:**
        - Disco API key must be configured in Streamlit secrets or environment variables
        - API endpoint: `https://api.production.services.disco.co`
        
        **Sync Process:**
        1. **Communities**: Fetches all available communities
        2. **Members**: Gets user data from each community
        3. **Products**: Retrieves courses/products from each community  
        4. **Enrollments**: Collects enrollment data linking users to products
        
        **Upsert Logic:**
        - Existing records are updated with new data
        - New records are inserted
        - No data is deleted during sync operations
        
        **Scheduling:**
        - Hourly sync runs at the top of each hour
        - Manual sync can be triggered anytime
        - Scheduler runs in background thread
        
        **Troubleshooting:**
        - Check API key configuration if client shows "Not Ready"
        - Review Snowflake connection if data counts show errors
        - Manual sync can help resolve temporary API issues
        """)
    
    # Footer
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                    padding: 1.5rem; border-radius: 10px; margin: 2rem 0; 
                    border: 1px solid #dee2e6; text-align: center;">
            <p style="color: #9a262c; font-weight: 600; margin-bottom: 0.5rem;">🔄 Data Sync Manager</p>
            <p style="color: #666; font-size: 0.9em; margin-bottom: 0;">Keep your Disco LMS data synchronized and up-to-date with automated and on-demand sync capabilities.</p>
        </div>
        """,
        unsafe_allow_html=True
    )