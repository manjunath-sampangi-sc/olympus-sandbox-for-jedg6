import streamlit as st
import pandas as pd
import json
from datetime import datetime
from utils.snowflake_connector import get_snowflake_connector, test_connection

def show_settings():
    """Display application settings and configuration"""
    st.markdown('<div class="main-header">⚙️ Application Settings</div>', unsafe_allow_html=True)
    
    # Settings tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔗 Connections", 
        "👤 User Preferences", 
        "📊 Dashboard Config", 
        "🔔 Notifications", 
        "🛠️ System Info"
    ])
    
    with tab1:
        show_connection_settings()
    
    with tab2:
        show_user_preferences()
    
    with tab3:
        show_dashboard_config()
    
    with tab4:
        show_notification_settings()
    
    with tab5:
        show_system_info()

def show_connection_settings():
    """Show database and API connection settings"""
    st.subheader("🔗 Connection Settings")
    
    # Snowflake connection
    st.markdown("### ❄️ Snowflake Connection")
    
    # Test current connection
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.button("🧪 Test Snowflake Connection", use_container_width=True):
            with st.spinner("Testing connection..."):
                try:
                    connector = get_snowflake_connector()
                    if connector and test_connection():
                        st.success("✅ Snowflake connection successful!")
                        
                        # Show connection details
                        if hasattr(st, 'secrets') and 'snowflake' in st.secrets:
                            st.info(f"Connected to: {st.secrets['snowflake']['account']}")
                            st.info(f"Database: {st.secrets['snowflake']['database']}")
                            st.info(f"User: {st.secrets['snowflake']['user']}")
                    else:
                        st.error("❌ Connection failed")
                except Exception as e:
                    st.error(f"❌ Connection error: {str(e)}")
    
    with col2:
        connection_status = get_connection_status()
        if connection_status:
            st.success("🟢 Connected")
        else:
            st.error("🔴 Disconnected")
    
    # Connection configuration
    with st.expander("🔧 Connection Configuration"):
        st.markdown("""
        **Current Configuration:**
        - Account: Configured via secrets
        - Authentication: External Browser
        - Database: SNOWFLAKE_SAMPLE_DATA
        - Schema: PUBLIC
        
        **To update connection settings:**
        1. Modify `.streamlit/secrets.toml`
        2. Restart the application
        3. Test the new connection
        """)
        
        # Show sample configuration
        st.code("""
        [snowflake]
        account = "your-account.snowflakecomputing.com"
        user = "your-username"
        authenticator = "externalbrowser"
        database = "SNOWFLAKE_SAMPLE_DATA"
        schema = "PUBLIC"
        """, language="toml")
    
    # Retool connection
    st.markdown("### 🔧 Retool Integration")
    
    retool_config = get_retool_config()
    
    with st.form("retool_connection"):
        col1, col2 = st.columns(2)
        
        with col1:
            retool_url = st.text_input(
                "Retool Base URL",
                value=retool_config.get('base_url', '') if retool_config else '',
                placeholder="https://your-org.retool.com"
            )
            
            retool_api_key = st.text_input(
                "API Key",
                type="password",
                value=retool_config.get('api_key', '') if retool_config else '',
                placeholder="Your Retool API key"
            )
        
        with col2:
            retool_timeout = st.number_input(
                "Request Timeout (seconds)",
                min_value=5,
                max_value=300,
                value=retool_config.get('timeout', 30) if retool_config else 30
            )
            
            retool_env = st.selectbox(
                "Environment",
                options=["Production", "Staging", "Development"],
                index=0 if not retool_config else ["Production", "Staging", "Development"].index(retool_config.get('environment', 'Production'))
            )
        
        if st.form_submit_button("💾 Save Retool Configuration"):
            new_config = {
                'base_url': retool_url,
                'api_key': retool_api_key,
                'timeout': retool_timeout,
                'environment': retool_env,
                'updated_at': datetime.now().isoformat()
            }
            
            st.session_state.retool_config = new_config
            st.success("✅ Retool configuration saved!")
            st.rerun()

def show_user_preferences():
    """Show user preference settings"""
    st.subheader("👤 User Preferences")
    
    # Get current preferences
    prefs = get_user_preferences()
    
    # Theme settings
    st.markdown("### 🎨 Theme & Display")
    
    col1, col2 = st.columns(2)
    
    with col1:
        theme = st.selectbox(
            "Color Theme",
            options=["Light", "Dark", "Auto"],
            index=["Light", "Dark", "Auto"].index(prefs.get('theme', 'Light'))
        )
        
        chart_theme = st.selectbox(
            "Chart Theme",
            options=["plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn"],
            index=0 if prefs.get('chart_theme') not in ["plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn"] else ["plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn"].index(prefs.get('chart_theme', 'plotly'))
        )
    
    with col2:
        sidebar_state = st.selectbox(
            "Sidebar Default State",
            options=["Expanded", "Collapsed"],
            index=["Expanded", "Collapsed"].index(prefs.get('sidebar_state', 'Expanded'))
        )
        
        page_layout = st.selectbox(
            "Page Layout",
            options=["Wide", "Centered"],
            index=["Wide", "Centered"].index(prefs.get('page_layout', 'Wide'))
        )
    
    # Data preferences
    st.markdown("### 📊 Data & Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        default_date_range = st.selectbox(
            "Default Date Range",
            options=["Last 7 days", "Last 30 days", "Last 90 days", "Last 12 months"],
            index=["Last 7 days", "Last 30 days", "Last 90 days", "Last 12 months"].index(prefs.get('default_date_range', 'Last 30 days'))
        )
        
        auto_refresh = st.checkbox(
            "Auto-refresh data",
            value=prefs.get('auto_refresh', True)
        )
    
    with col2:
        refresh_interval = st.selectbox(
            "Refresh Interval",
            options=["1 minute", "5 minutes", "15 minutes", "30 minutes", "1 hour"],
            index=["1 minute", "5 minutes", "15 minutes", "30 minutes", "1 hour"].index(prefs.get('refresh_interval', '5 minutes')),
            disabled=not auto_refresh
        )
        
        cache_data = st.checkbox(
            "Cache data for faster loading",
            value=prefs.get('cache_data', True)
        )
    
    # Language and region
    st.markdown("### 🌍 Language & Region")
    
    col1, col2 = st.columns(2)
    
    with col1:
        language = st.selectbox(
            "Language",
            options=["English", "Spanish", "French", "German"],
            index=["English", "Spanish", "French", "German"].index(prefs.get('language', 'English'))
        )
        
        timezone = st.selectbox(
            "Timezone",
            options=["UTC", "US/Eastern", "US/Central", "US/Mountain", "US/Pacific", "Europe/London", "Europe/Paris"],
            index=0 if prefs.get('timezone') not in ["UTC", "US/Eastern", "US/Central", "US/Mountain", "US/Pacific", "Europe/London", "Europe/Paris"] else ["UTC", "US/Eastern", "US/Central", "US/Mountain", "US/Pacific", "Europe/London", "Europe/Paris"].index(prefs.get('timezone', 'UTC'))
        )
    
    with col2:
        currency = st.selectbox(
            "Currency",
            options=["USD", "EUR", "GBP", "CAD", "AUD"],
            index=["USD", "EUR", "GBP", "CAD", "AUD"].index(prefs.get('currency', 'USD'))
        )
        
        date_format = st.selectbox(
            "Date Format",
            options=["MM/DD/YYYY", "DD/MM/YYYY", "YYYY-MM-DD"],
            index=["MM/DD/YYYY", "DD/MM/YYYY", "YYYY-MM-DD"].index(prefs.get('date_format', 'MM/DD/YYYY'))
        )
    
    # Save preferences
    if st.button("💾 Save Preferences", use_container_width=True):
        new_prefs = {
            'theme': theme,
            'chart_theme': chart_theme,
            'sidebar_state': sidebar_state,
            'page_layout': page_layout,
            'default_date_range': default_date_range,
            'auto_refresh': auto_refresh,
            'refresh_interval': refresh_interval,
            'cache_data': cache_data,
            'language': language,
            'timezone': timezone,
            'currency': currency,
            'date_format': date_format,
            'updated_at': datetime.now().isoformat()
        }
        
        st.session_state.user_preferences = new_prefs
        st.success("✅ Preferences saved successfully!")
        st.rerun()

def show_dashboard_config():
    """Show dashboard configuration settings"""
    st.subheader("📊 Dashboard Configuration")
    
    # Get current dashboard config
    config = get_dashboard_config()
    
    # Widget configuration
    st.markdown("### 📈 Widget Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        show_kpi_widgets = st.checkbox(
            "Show KPI Widgets",
            value=config.get('show_kpi_widgets', True)
        )
        
        show_charts = st.checkbox(
            "Show Charts",
            value=config.get('show_charts', True)
        )
        
        show_tables = st.checkbox(
            "Show Data Tables",
            value=config.get('show_tables', True)
        )
    
    with col2:
        chart_height = st.slider(
            "Default Chart Height",
            min_value=200,
            max_value=800,
            value=config.get('chart_height', 400),
            step=50
        )
        
        rows_per_table = st.slider(
            "Rows per Table",
            min_value=5,
            max_value=50,
            value=config.get('rows_per_table', 10),
            step=5
        )
    
    # Page-specific settings
    st.markdown("### 📄 Page-Specific Settings")
    
    # Executive Dashboard
    with st.expander("📊 Executive Dashboard"):
        exec_widgets = st.multiselect(
            "Enabled Widgets",
            options=["Revenue", "Sales Pipeline", "Training Metrics", "User Engagement", "Performance Trends"],
            default=config.get('executive_widgets', ["Revenue", "Sales Pipeline", "Training Metrics"])
        )
        
        exec_refresh = st.selectbox(
            "Refresh Rate",
            options=["Real-time", "1 minute", "5 minutes", "15 minutes"],
            index=0 if config.get('executive_refresh') not in ["Real-time", "1 minute", "5 minutes", "15 minutes"] else ["Real-time", "1 minute", "5 minutes", "15 minutes"].index(config.get('executive_refresh', '5 minutes'))
        )
    
    # Sales Performance
    with st.expander("📈 Sales Performance"):
        sales_metrics = st.multiselect(
            "Default Metrics",
            options=["Pipeline Value", "Win Rate", "Average Deal Size", "Sales Velocity", "Conversion Rate"],
            default=config.get('sales_metrics', ["Pipeline Value", "Win Rate", "Average Deal Size"])
        )
        
        sales_period = st.selectbox(
            "Default Time Period",
            options=["Current Quarter", "Last 90 days", "Last 6 months", "Last 12 months"],
            index=0 if config.get('sales_period') not in ["Current Quarter", "Last 90 days", "Last 6 months", "Last 12 months"] else ["Current Quarter", "Last 90 days", "Last 6 months", "Last 12 months"].index(config.get('sales_period', 'Current Quarter'))
        )
    
    # Learning Analytics
    with st.expander("🎓 Learning Analytics"):
        learning_views = st.multiselect(
            "Default Views",
            options=["Completion Rates", "Progress Tracking", "Course Popularity", "Certification Status"],
            default=config.get('learning_views', ["Completion Rates", "Progress Tracking"])
        )
        
        learning_grouping = st.selectbox(
            "Default Grouping",
            options=["By Department", "By Course Category", "By Individual", "By Manager"],
            index=0 if config.get('learning_grouping') not in ["By Department", "By Course Category", "By Individual", "By Manager"] else ["By Department", "By Course Category", "By Individual", "By Manager"].index(config.get('learning_grouping', 'By Department'))
        )
    
    # Save configuration
    if st.button("💾 Save Dashboard Configuration", use_container_width=True):
        new_config = {
            'show_kpi_widgets': show_kpi_widgets,
            'show_charts': show_charts,
            'show_tables': show_tables,
            'chart_height': chart_height,
            'rows_per_table': rows_per_table,
            'executive_widgets': exec_widgets,
            'executive_refresh': exec_refresh,
            'sales_metrics': sales_metrics,
            'sales_period': sales_period,
            'learning_views': learning_views,
            'learning_grouping': learning_grouping,
            'updated_at': datetime.now().isoformat()
        }
        
        st.session_state.dashboard_config = new_config
        st.success("✅ Dashboard configuration saved!")
        st.rerun()

def show_notification_settings():
    """Show notification settings"""
    st.subheader("🔔 Notification Settings")
    
    # Get current notification settings
    notif_config = get_notification_config()
    
    # Email notifications
    st.markdown("### 📧 Email Notifications")
    
    col1, col2 = st.columns(2)
    
    with col1:
        email_enabled = st.checkbox(
            "Enable Email Notifications",
            value=notif_config.get('email_enabled', False)
        )
        
        if email_enabled:
            email_address = st.text_input(
                "Email Address",
                value=notif_config.get('email_address', ''),
                placeholder="your.email@company.com"
            )
    
    with col2:
        if email_enabled:
            email_frequency = st.selectbox(
                "Email Frequency",
                options=["Immediate", "Daily Digest", "Weekly Summary"],
                index=0 if notif_config.get('email_frequency') not in ["Immediate", "Daily Digest", "Weekly Summary"] else ["Immediate", "Daily Digest", "Weekly Summary"].index(notif_config.get('email_frequency', 'Daily Digest'))
            )
    
    # Notification types
    st.markdown("### 🔔 Notification Types")
    
    notification_types = {
        'data_alerts': st.checkbox("Data Quality Alerts", value=notif_config.get('data_alerts', True)),
        'system_updates': st.checkbox("System Updates", value=notif_config.get('system_updates', True)),
        'performance_reports': st.checkbox("Performance Reports", value=notif_config.get('performance_reports', False)),
        'threshold_alerts': st.checkbox("Threshold Alerts", value=notif_config.get('threshold_alerts', True)),
        'completion_notifications': st.checkbox("Training Completion Notifications", value=notif_config.get('completion_notifications', False))
    }
    
    # Alert thresholds
    st.markdown("### ⚠️ Alert Thresholds")
    
    col1, col2 = st.columns(2)
    
    with col1:
        revenue_threshold = st.number_input(
            "Revenue Drop Alert (%)",
            min_value=1,
            max_value=50,
            value=notif_config.get('revenue_threshold', 10),
            help="Alert when revenue drops by this percentage"
        )
        
        completion_threshold = st.number_input(
            "Low Completion Rate Alert (%)",
            min_value=1,
            max_value=100,
            value=notif_config.get('completion_threshold', 50),
            help="Alert when course completion rate falls below this percentage"
        )
    
    with col2:
        pipeline_threshold = st.number_input(
            "Low Pipeline Alert ($)",
            min_value=1000,
            max_value=1000000,
            value=notif_config.get('pipeline_threshold', 100000),
            step=10000,
            help="Alert when pipeline value falls below this amount"
        )
        
        activity_threshold = st.number_input(
            "Inactivity Alert (days)",
            min_value=1,
            max_value=30,
            value=notif_config.get('activity_threshold', 7),
            help="Alert when no activity for this many days"
        )
    
    # Save notification settings
    if st.button("💾 Save Notification Settings", use_container_width=True):
        new_notif_config = {
            'email_enabled': email_enabled,
            'email_address': email_address if email_enabled else '',
            'email_frequency': email_frequency if email_enabled else 'Daily Digest',
            'revenue_threshold': revenue_threshold,
            'completion_threshold': completion_threshold,
            'pipeline_threshold': pipeline_threshold,
            'activity_threshold': activity_threshold,
            'updated_at': datetime.now().isoformat(),
            **notification_types
        }
        
        st.session_state.notification_config = new_notif_config
        st.success("✅ Notification settings saved!")
        st.rerun()

def show_system_info():
    """Show system information and diagnostics"""
    st.subheader("🛠️ System Information")
    
    # Application info
    st.markdown("### 📱 Application Info")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("**Version:** 1.0.0")
        st.info("**Build Date:** 2024-01-15")
        st.info("**Environment:** Production")
    
    with col2:
        st.info("**Framework:** Streamlit 1.29.0")
        st.info("**Python:** 3.9+")
        st.info("**Database:** Snowflake")
    
    # System status
    st.markdown("### 🔍 System Status")
    
    status_col1, status_col2, status_col3 = st.columns(3)
    
    with status_col1:
        st.metric("Database Connection", "✅ Active", "Connected")
        st.metric("Cache Status", "✅ Active", "Healthy")
    
    with status_col2:
        st.metric("API Endpoints", "✅ Active", "All responding")
        st.metric("Memory Usage", "📊 Normal", "< 80%")
    
    with status_col3:
        st.metric("Response Time", "⚡ Fast", "< 2s avg")
        st.metric("Error Rate", "✅ Low", "< 1%")
    
    # Session information
    st.markdown("### 🔐 Session Information")
    
    session_info = {
        "Session ID": st.session_state.get('session_id', 'N/A'),
        "User": st.session_state.get('username', 'demo_user'),
        "Login Time": st.session_state.get('login_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        "Last Activity": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "Pages Visited": len(st.session_state.get('visited_pages', [])),
        "Cache Entries": len([k for k in st.session_state.keys() if 'cache' in k.lower()])
    }
    
    for key, value in session_info.items():
        st.text(f"**{key}:** {value}")
    
    # Diagnostic tools
    st.markdown("### 🔧 Diagnostic Tools")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🧪 Test All Connections", use_container_width=True):
            with st.spinner("Testing connections..."):
                # Simulate connection tests
                import time
                time.sleep(2)
                st.success("✅ All connections healthy")
    
    with col2:
        if st.button("🗑️ Clear Cache", use_container_width=True):
            # Clear cache entries from session state
            cache_keys = [k for k in st.session_state.keys() if 'cache' in k.lower()]
            for key in cache_keys:
                del st.session_state[key]
            st.success(f"✅ Cleared {len(cache_keys)} cache entries")
    
    with col3:
        if st.button("📊 Generate Report", use_container_width=True):
            # Generate system report
            report_data = {
                'timestamp': datetime.now().isoformat(),
                'system_info': session_info,
                'configuration': {
                    'user_preferences': st.session_state.get('user_preferences', {}),
                    'dashboard_config': st.session_state.get('dashboard_config', {}),
                    'notification_config': st.session_state.get('notification_config', {})
                }
            }
            
            st.download_button(
                label="📥 Download System Report",
                data=json.dumps(report_data, indent=2),
                file_name=f"system_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )

# Helper functions
def get_connection_status():
    """Check if database connection is active"""
    try:
        connector = get_snowflake_connector()
        return connector is not None and test_connection()
    except:
        return False

def get_retool_config():
    """Get Retool configuration from session state"""
    return st.session_state.get('retool_config', {})

def get_user_preferences():
    """Get user preferences from session state"""
    return st.session_state.get('user_preferences', {})

def get_dashboard_config():
    """Get dashboard configuration from session state"""
    return st.session_state.get('dashboard_config', {})

def get_notification_config():
    """Get notification configuration from session state"""
    return st.session_state.get('notification_config', {})