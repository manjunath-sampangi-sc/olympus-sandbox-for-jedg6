import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
import os
from typing import Dict, Any

# Import page modules
from pages import dashboard, sales_performance, learning_analytics, ai_chat, retool_integration, settings, billing_dashboard

# Page configuration
st.set_page_config(
    page_title="Olympus Analytics - Demo POC",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f4e79;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f4e79;
        margin: 0.5rem 0;
    }
    .sidebar-logo {
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
        color: #1f4e79;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

class SnowflakeConnection:
    """Handles Snowflake database connections and queries"""
    
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        """Establish connection to Snowflake"""
        try:
            self.connection = snowflake.connector.connect(
                account=st.secrets.get("snowflake_account", os.getenv("SNOWFLAKE_ACCOUNT")),
                user=st.secrets.get("snowflake_user", os.getenv("SNOWFLAKE_USER")),
                password=st.secrets.get("snowflake_password", os.getenv("SNOWFLAKE_PASSWORD")),
                warehouse=st.secrets.get("snowflake_warehouse", os.getenv("SNOWFLAKE_WAREHOUSE", "XS_WAREHOUSE")),
                database=st.secrets.get("snowflake_database", os.getenv("SNOWFLAKE_DATABASE", "OLYMPUS_ANALYTICS")),
                schema=st.secrets.get("snowflake_schema", os.getenv("SNOWFLAKE_SCHEMA", "GOLD"))
            )
            return True
        except Exception as e:
            st.error(f"Failed to connect to Snowflake: {str(e)}")
            return False
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute SQL query and return results as DataFrame"""
        try:
            if not self.connection:
                self.connect()
            
            cursor = self.connection.cursor()
            cursor.execute(query)
            
            # Fetch results and column names
            results = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            # Create DataFrame
            df = pd.DataFrame(results, columns=columns)
            cursor.close()
            
            return df
        except Exception as e:
            st.error(f"Query execution failed: {str(e)}")
            return pd.DataFrame()
    
    def close(self):
        """Close Snowflake connection"""
        if self.connection:
            self.connection.close()

def initialize_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'snowflake_conn' not in st.session_state:
        st.session_state.snowflake_conn = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Dashboard"

def authenticate_user():
    """Simple authentication for demo purposes"""
    st.markdown('<div class="main-header">🏔️ Olympus Analytics</div>', unsafe_allow_html=True)
    st.markdown("### Welcome to the Olympus Analytics Demo")
    
    with st.form("login_form"):
        st.markdown("**Demo Credentials:**")
        username = st.text_input("Username", value="demo_user")
        password = st.text_input("Password", type="password", value="olympus2024")
        
        if st.form_submit_button("Login", use_container_width=True):
            if username == "demo_user" and password == "olympus2024":
                st.session_state.authenticated = True
                st.session_state.snowflake_conn = SnowflakeConnection()
                st.rerun()
            else:
                st.error("Invalid credentials. Use demo_user / olympus2024")

def create_sidebar():
    """Create navigation sidebar"""
    with st.sidebar:
        st.markdown('<div class="sidebar-logo">🏔️ Olympus Analytics</div>', unsafe_allow_html=True)
        
        # Navigation menu
        pages = {
            "📊 Executive Dashboard": "dashboard",
            "💼 Sales Performance": "sales",
            "🎓 Learning Analytics": "learning",
            "💰 Billing Dashboard": "billing",
            "🤖 AI Chat Assistant": "ai_chat",
            "🔧 Retool Integration": "retool",
            "⚙️ Settings": "settings"
        }
        
        st.markdown("### Navigation")
        for page_name, page_key in pages.items():
            if st.button(page_name, use_container_width=True):
                st.session_state.current_page = page_key
                st.rerun()
        
        st.markdown("---")
        
        # Connection status
        if st.session_state.snowflake_conn:
            st.success("✅ Snowflake Connected")
        else:
            st.error("❌ Snowflake Disconnected")
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.snowflake_conn = None
            st.rerun()

def main():
    """Main application function"""
    initialize_session_state()
    
    # Authentication check
    if not st.session_state.authenticated:
        authenticate_user()
        return
    
    # Create sidebar navigation
    create_sidebar()
    
    # Main content area
    current_page = st.session_state.get('current_page', 'dashboard')
    
    if current_page == 'dashboard':
        show_executive_dashboard()
    elif current_page == 'sales':
        show_sales_performance()
    elif current_page == 'learning':
        show_learning_analytics()
    elif current_page == 'billing':
        show_billing_dashboard()
    elif current_page == 'ai_chat':
        show_ai_chat()
    elif current_page == 'retool':
        show_retool_integration()
    elif current_page == 'settings':
        show_settings()
    else:
        show_executive_dashboard()

def show_executive_dashboard():
    """Display executive dashboard"""
    dashboard.show_executive_dashboard()

def show_sales_performance():
    """Display sales performance analytics"""
    sales_performance.show_sales_performance()

def show_learning_analytics():
    """Display learning analytics"""
    learning_analytics.show_learning_analytics()

def show_ai_chat():
    """Display AI chat interface"""
    ai_chat.show_ai_chat()

def show_retool_integration():
    """Display Retool integration"""
    retool_integration.show_retool_integration()

def show_billing_dashboard():
    """Display billing dashboard"""
    billing_dashboard.show_billing_dashboard()

def show_settings():
    """Display settings page"""
    settings.show_settings()

if __name__ == "__main__":
    main()