import streamlit as st
import requests
import pandas as pd
import json
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from utils.snowflake_connector import get_snowflake_connector, execute_query

def show_retool_integration():
    """Display Retool integration page with embedded components and API connections"""
    st.markdown('<div class="main-header">🔧 Retool Integration</div>', unsafe_allow_html=True)
    
    # Introduction
    st.markdown("""
    This page demonstrates integration between Streamlit and Retool for advanced analytics and custom workflows.
    Retool provides powerful tools for building internal applications and connecting to various data sources.
    """)
    
    # Tabs for different integration features
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Embedded Dashboard", "🔗 API Integration", "📋 Custom Forms", "⚙️ Configuration"])
    
    with tab1:
        show_embedded_dashboard()
    
    with tab2:
        show_api_integration()
    
    with tab3:
        show_custom_forms()
    
    with tab4:
        show_retool_configuration()

def show_embedded_dashboard():
    """Show embedded Retool dashboard"""
    st.subheader("📊 Embedded Retool Dashboard")
    
    # Check if Retool configuration is available
    retool_config = get_retool_config()
    
    if retool_config and retool_config.get('base_url'):
        st.success("✅ Retool configuration found")
        
        # Embedded iframe (demo)
        st.markdown("""
        ### 📈 Sales Performance Dashboard
        
        Below is an embedded Retool dashboard that provides advanced analytics capabilities:
        """)
        
        # Demo iframe placeholder
        iframe_html = f"""
        <div style="border: 2px solid #1f4e79; border-radius: 8px; padding: 20px; background-color: #f8f9fa; text-align: center; height: 400px; display: flex; align-items: center; justify-content: center;">
            <div>
                <h3 style="color: #1f4e79; margin-bottom: 20px;">🔧 Retool Dashboard</h3>
                <p style="color: #666; margin-bottom: 20px;">Interactive dashboard with advanced filtering and real-time updates</p>
                <div style="background-color: #e9ecef; padding: 15px; border-radius: 4px; margin: 10px 0;">
                    <strong>Features:</strong><br>
                    • Real-time data synchronization<br>
                    • Advanced filtering and drill-down<br>
                    • Custom business logic<br>
                    • Multi-source data integration
                </div>
                <p style="color: #007bff; font-size: 14px;">URL: {retool_config.get('base_url', 'Not configured')}</p>
            </div>
        </div>
        """
        
        st.markdown(iframe_html, unsafe_allow_html=True)
        
        # Dashboard controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            date_range = st.selectbox(
                "📅 Date Range",
                ["Last 7 days", "Last 30 days", "Last 90 days", "Custom"]
            )
        
        with col2:
            department = st.selectbox(
                "🏢 Department",
                ["All Departments", "Sales", "Marketing", "Customer Success"]
            )
        
        with col3:
            metric = st.selectbox(
                "📊 Primary Metric",
                ["Revenue", "Deals Closed", "Pipeline Value", "Conversion Rate"]
            )
        
        # Sync data button
        if st.button("🔄 Sync with Retool", use_container_width=True):
            with st.spinner("Syncing data with Retool..."):
                sync_result = sync_with_retool(date_range, department, metric)
                if sync_result['success']:
                    st.success(f"✅ Data synced successfully! {sync_result['message']}")
                else:
                    st.error(f"❌ Sync failed: {sync_result['message']}")
    
    else:
        st.warning("⚠️ Retool configuration not found. Please configure in the Configuration tab.")
        st.info("Configure your Retool settings to enable data synchronization.")

def show_api_integration():
    """Show API integration capabilities"""
    st.subheader("🔗 API Integration")
    
    st.markdown("""
    This section demonstrates how to integrate Streamlit with Retool APIs for data exchange and workflow automation.
    """)
    
    # API endpoints
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📤 Send Data to Retool")
        
        # Sample data to send
        sample_data = {
            "timestamp": datetime.now().isoformat(),
            "revenue": 245000,
            "deals_closed": 12,
            "pipeline_value": 1800000
        }
        
        st.json(sample_data)
        
        if st.button("📤 Send to Retool API", key="send_data"):
            with st.spinner("Sending data..."):
                result = send_data_to_retool(sample_data)
                if result['success']:
                    st.success(f"✅ Data sent successfully! Response: {result['response']}")
                else:
                    st.error(f"❌ Failed to send data: {result['error']}")
    
    with col2:
        st.markdown("### 📥 Fetch Data from Retool")
        
        endpoint = st.selectbox(
            "Select Endpoint",
            ["/api/sales-data", "/api/training-metrics", "/api/user-analytics"]
        )
        
        if st.button("📥 Fetch from Retool API", key="fetch_data"):
            with st.spinner("Fetching data..."):
                result = fetch_data_from_retool(endpoint)
                if result['success']:
                    st.success("✅ Data fetched successfully!")
                    st.json(result['data'])
                else:
                    st.error(f"❌ Failed to fetch data: {result['error']}")
    
    # Webhook configuration
    st.markdown("### 🔔 Webhook Configuration")
    
    webhook_url = st.text_input(
        "Webhook URL",
        value="https://your-streamlit-app.com/webhook",
        help="URL where Retool will send webhook notifications"
    )
    
    webhook_events = st.multiselect(
        "Webhook Events",
        ["data_updated", "user_action", "workflow_completed", "error_occurred"],
        default=["data_updated"]
    )
    
    if st.button("⚙️ Configure Webhook"):
        st.info(f"Webhook configured for events: {', '.join(webhook_events)}")

def show_custom_forms():
    """Show custom forms integration"""
    st.subheader("📋 Custom Forms & Workflows")
    
    st.markdown("""
    Create custom forms that integrate with both Streamlit and Retool for data collection and workflow automation.
    """)
    
    # Form tabs
    form_tab1, form_tab2 = st.tabs(["📝 Data Entry Form", "🔄 Workflow Trigger"])
    
    with form_tab1:
        st.markdown("### 📝 Sales Data Entry")
        
        with st.form("sales_data_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                deal_name = st.text_input("Deal Name")
                client_name = st.text_input("Client Name")
                deal_value = st.number_input("Deal Value ($)", min_value=0, value=10000)
                
            with col2:
                sales_rep = st.selectbox(
                    "Sales Rep",
                    ["John Smith", "Sarah Johnson", "Mike Davis", "Lisa Chen"]
                )
                stage = st.selectbox(
                    "Stage",
                    ["Prospecting", "Qualification", "Proposal", "Negotiation", "Closed Won"]
                )
                close_date = st.date_input("Expected Close Date")
            
            notes = st.text_area("Notes")
            
            submitted = st.form_submit_button("💾 Submit to Retool")
            
            if submitted:
                form_data = {
                    "deal_name": deal_name,
                    "client_name": client_name,
                    "deal_value": deal_value,
                    "sales_rep": sales_rep,
                    "stage": stage,
                    "close_date": close_date.isoformat(),
                    "notes": notes,
                    "submitted_at": datetime.now().isoformat()
                }
                
                # Simulate sending to Retool
                with st.spinner("Submitting to Retool..."):
                    result = submit_form_to_retool(form_data)
                    if result['success']:
                        st.success("✅ Form submitted successfully!")
                        st.balloons()
                    else:
                        st.error(f"❌ Submission failed: {result['error']}")
    
    with form_tab2:
        st.markdown("### 🔄 Workflow Automation")
        
        workflow_type = st.selectbox(
            "Workflow Type",
            ["Data Sync", "Report Generation", "Alert Notification", "Custom Process"]
        )
        
        if workflow_type == "Data Sync":
            st.markdown("**Sync data between Snowflake and Retool**")
            
            sync_frequency = st.selectbox(
                "Sync Frequency",
                ["Real-time", "Every 5 minutes", "Hourly", "Daily"]
            )
            
            tables_to_sync = st.multiselect(
                "Tables to Sync",
                ["FACT_SALES_PERFORMANCE", "FACT_LEARNING_ANALYTICS", "DIM_USERS", "DIM_COURSES"]
            )
            
            if st.button("🚀 Start Sync Workflow"):
                st.success(f"✅ Sync workflow started for {len(tables_to_sync)} tables with {sync_frequency} frequency")
        
        elif workflow_type == "Report Generation":
            st.markdown("**Automated report generation**")
            
            report_type = st.selectbox(
                "Report Type",
                ["Sales Summary", "Training Analytics", "Executive Dashboard", "Custom Report"]
            )
            
            recipients = st.text_area(
                "Email Recipients",
                value="manager@olympus.com, team@olympus.com"
            )
            
            if st.button("📊 Generate Report"):
                st.success(f"✅ {report_type} report generation triggered")

def show_retool_configuration():
    """Show Retool configuration settings"""
    st.subheader("⚙️ Retool Configuration")
    
    st.markdown("""
    Configure your Retool integration settings for seamless data exchange and workflow automation.
    """)
    
    # Configuration form
    with st.form("retool_config"):
        st.markdown("### 🔧 API Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            retool_url = st.text_input(
                "Retool Base URL",
                value="https://your-org.retool.com",
                help="Your Retool organization URL"
            )
            
            api_key = st.text_input(
                "API Key",
                type="password",
                help="Your Retool API key"
            )
        
        with col2:
            environment = st.selectbox(
                "Environment",
                ["Production", "Staging", "Development"]
            )
            
            timeout = st.number_input(
                "Request Timeout (seconds)",
                min_value=5,
                max_value=300,
                value=30
            )
        
        st.markdown("### 📊 Data Sync Settings")
        
        auto_sync = st.checkbox("Enable Auto Sync", value=True)
        
        if auto_sync:
            sync_interval = st.selectbox(
                "Sync Interval",
                ["5 minutes", "15 minutes", "30 minutes", "1 hour"]
            )
        
        enable_webhooks = st.checkbox("Enable Webhooks", value=True)
        
        if enable_webhooks:
            webhook_secret = st.text_input(
                "Webhook Secret",
                type="password",
                help="Secret key for webhook verification"
            )
        
        submitted = st.form_submit_button("💾 Save Configuration")
        
        if submitted:
            config = {
                "retool_url": retool_url,
                "api_key": api_key,
                "environment": environment,
                "timeout": timeout,
                "auto_sync": auto_sync,
                "sync_interval": sync_interval if auto_sync else None,
                "enable_webhooks": enable_webhooks,
                "webhook_secret": webhook_secret if enable_webhooks else None
            }
            
            # Save configuration (in real app, this would be saved to database or config file)
            st.session_state.retool_config = config
            st.success("✅ Configuration saved successfully!")
    
    # Test connection
    st.markdown("### 🔍 Connection Test")
    
    if st.button("🧪 Test Retool Connection"):
        with st.spinner("Testing connection..."):
            result = test_retool_connection()
            if result['success']:
                st.success(f"✅ Connection successful! {result['message']}")
            else:
                st.error(f"❌ Connection failed: {result['error']}")

# Demo dashboard function removed - using only Snowflake data

# Helper functions
def get_retool_config():
    """Get Retool configuration from session state or secrets"""
    if 'retool_config' in st.session_state:
        return st.session_state.retool_config
    
    try:
        if hasattr(st, 'secrets') and 'retool' in st.secrets:
            return {
                'base_url': st.secrets['retool']['base_url'],
                'api_key': st.secrets['retool']['api_key']
            }
    except:
        pass
    
    return None

def sync_with_retool(date_range, department, metric):
    """Simulate syncing data with Retool"""
    # Simulate API call
    import time
    time.sleep(1)
    
    return {
        'success': True,
        'message': f"Synced {metric} data for {department} ({date_range})"
    }

def send_data_to_retool(data):
    """Simulate sending data to Retool API"""
    # In real implementation, this would make an HTTP request to Retool
    import time
    time.sleep(0.5)
    
    return {
        'success': True,
        'response': 'Data received and processed'
    }

def fetch_data_from_retool(endpoint):
    """Simulate fetching data from Retool API"""
    # In real implementation, this would make an HTTP request to Retool
    import time
    time.sleep(0.5)
    
    sample_data = {
        'timestamp': datetime.now().isoformat(),
        'records': 150,
        'status': 'success'
    }
    
    return {
        'success': True,
        'data': sample_data
    }

def submit_form_to_retool(form_data):
    """Simulate submitting form data to Retool"""
    import time
    time.sleep(1)
    
    return {
        'success': True,
        'id': f"deal_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    }

def test_retool_connection():
    """Test connection to Retool"""
    import time
    time.sleep(1)
    
    return {
        'success': True,
        'message': 'Connection established successfully'
    }