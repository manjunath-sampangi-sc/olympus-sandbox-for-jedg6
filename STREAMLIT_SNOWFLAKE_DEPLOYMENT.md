# Streamlit in Snowflake (SiS) Deployment Guide

## 🚀 Deploying Olympus Analytics to Streamlit in Snowflake

### Overview
This guide walks you through deploying the Olympus Analytics dashboard to Streamlit in Snowflake (SiS), Snowflake's native Streamlit environment.

---

## 📋 Prerequisites

### 1. Snowflake Account Requirements
- **Snowflake Account** with Streamlit in Snowflake enabled
- **ACCOUNTADMIN** or **SYSADMIN** privileges
- **Database and Schema** already created (`OLYMPUS_ANALYTICS`)
- **Warehouse** configured (`XS_WAREHOUSE` or larger)

### 2. Data Requirements
- ✅ **DISCO_MEMBERS** table populated (943 members)
- ✅ **DISCO_PRODUCTS** table populated (25 products)
- ✅ **DISCO_ENROLLMENTS** table populated (160 enrollments)
- ✅ **GD_MEMBER_ENROLLMENT_DETAILS** Gold table created

---

## 🛠️ Step 1: Prepare Code for SiS

### A. Create SiS-Compatible App File

Create a new file `streamlit_app_sis.py` optimized for Streamlit in Snowflake:

```python
# streamlit_app_sis.py - Streamlit in Snowflake Version
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

# Custom CSS (same as local version)
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #4682B4;
        text-align: center;
        margin-bottom: 2rem;
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
    """Main billing dashboard"""
    st.markdown('<div class="main-header">💰 Member Billing Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="client-branding">Olympus Analytics - Real-time Billing Insights</div>', unsafe_allow_html=True)
    
    # Load billing data
    query = """
    SELECT 
        MEMBER_ID,
        EMAIL,
        MEMBER_NAME,
        COMPANY_NAME,
        BILLING_BRACKET,
        MONTHLY_AMOUNT,
        TOTAL_COURSES_ENROLLED,
        ENROLLED_COURSES,
        BILLING_CATEGORY_DESCRIPTION
    FROM OLYMPUS_ANALYTICS.GOLD.GD_MEMBER_ENROLLMENT_DETAILS
    ORDER BY TOTAL_COURSES_ENROLLED DESC, MEMBER_NAME
    """
    
    billing_data = execute_query(query)
    
    if billing_data.empty:
        st.warning("No billing data available. Please ensure the data pipeline has been run.")
        return
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Members", f"{len(billing_data):,}")
    
    with col2:
        total_revenue = billing_data['MONTHLY_AMOUNT'].sum()
        st.metric("Total Revenue", f"${total_revenue:,.2f}")
    
    with col3:
        enrolled_members = len(billing_data[billing_data['TOTAL_COURSES_ENROLLED'] > 0])
        st.metric("Enrolled Members", f"{enrolled_members:,}")
    
    with col4:
        avg_revenue = billing_data['MONTHLY_AMOUNT'].mean()
        st.metric("Avg Revenue/Member", f"${avg_revenue:.2f}")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Billing Bracket Distribution")
        bracket_counts = billing_data['BILLING_BRACKET'].value_counts()
        fig_pie = px.pie(
            values=bracket_counts.values,
            names=bracket_counts.index,
            title="Members by Billing Bracket"
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.subheader("🏢 Top Companies by Enrollment")
        company_enrolled = billing_data[billing_data['TOTAL_COURSES_ENROLLED'] > 0]['COMPANY_NAME'].value_counts().head(10)
        fig_bar = px.bar(
            x=company_enrolled.values,
            y=company_enrolled.index,
            orientation='h',
            title="Enrolled Members by Company"
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Data table
    st.subheader("📋 Detailed Member Data")
    
    # Search functionality
    search_term = st.text_input("🔍 Search members (by name, email, or company)")
    
    filtered_data = billing_data.copy()
    if search_term:
        filtered_data = billing_data[
            billing_data['MEMBER_NAME'].str.contains(search_term, case=False, na=False) |
            billing_data['EMAIL'].str.contains(search_term, case=False, na=False) |
            billing_data['COMPANY_NAME'].str.contains(search_term, case=False, na=False)
        ]
    
    st.dataframe(
        filtered_data[[
            'MEMBER_NAME', 'EMAIL', 'COMPANY_NAME', 'BILLING_BRACKET',
            'MONTHLY_AMOUNT', 'TOTAL_COURSES_ENROLLED', 'ENROLLED_COURSES'
        ]],
        use_container_width=True,
        column_config={
            "MONTHLY_AMOUNT": st.column_config.NumberColumn(
                "Monthly Amount",
                format="$%.2f"
            ),
            "ENROLLED_COURSES": st.column_config.TextColumn(
                "Enrolled Courses",
                width="large"
            )
        }
    )

# Main app
def main():
    # Sidebar
    with st.sidebar:
        st.markdown('<div class="sidebar-logo">🏔️ Olympus Analytics</div>', unsafe_allow_html=True)
        st.markdown('<div class="client-branding">Analytics Platform</div>', unsafe_allow_html=True)
        
        st.markdown("### Navigation")
        page = st.selectbox(
            "Select Page",
            ["💰 Billing Dashboard", "📊 Analytics Overview"]
        )
    
    # Main content
    if "Billing" in page:
        show_billing_dashboard()
    else:
        st.markdown('<div class="main-header">🏔️ Olympus Analytics</div>', unsafe_allow_html=True)
        st.markdown('<div class="client-branding">Welcome to the Analytics Platform</div>', unsafe_allow_html=True)
        st.markdown("### Platform Overview")
        st.info("Navigate to the Billing Dashboard to view member enrollment and billing analytics.")

if __name__ == "__main__":
    main()
```

---

## 🚀 Step 2: Deploy to Streamlit in Snowflake

### A. Access Snowflake Web Interface

1. **Login to Snowflake**
   - Go to your Snowflake account URL
   - Login with your credentials

2. **Navigate to Streamlit**
   - Click on "Streamlit" in the left navigation menu
   - Or go to: `https://<your-account>.snowflakecomputing.com/streamlit`

### B. Create New Streamlit App

1. **Click "+ Streamlit App"**

2. **Configure App Settings:**
   ```
   App Name: olympus-analytics-dashboard
   Warehouse: XS_WAREHOUSE (or your preferred warehouse)
   App Location: 
     - Database: OLYMPUS_ANALYTICS
     - Schema: PUBLIC (or STREAMLIT)
   ```

3. **Upload App Code:**
   - Copy the content from `streamlit_app_sis.py`
   - Paste into the Streamlit editor
   - Or upload the file directly

### C. Configure Environment

1. **Set Required Packages** (in `environment.yml`):
   ```yaml
   name: olympus_analytics
   channels:
     - snowflake
     - conda-forge
   dependencies:
     - python=3.9
     - streamlit
     - pandas
     - plotly
     - snowflake-snowpark-python
   ```

2. **Grant Permissions:**
   ```sql
   -- Run these commands in Snowflake worksheet
   USE ROLE ACCOUNTADMIN;
   
   -- Grant usage on database and schema
   GRANT USAGE ON DATABASE OLYMPUS_ANALYTICS TO ROLE STREAMLIT_ROLE;
   GRANT USAGE ON SCHEMA OLYMPUS_ANALYTICS.GOLD TO ROLE STREAMLIT_ROLE;
   
   -- Grant select on tables
   GRANT SELECT ON ALL TABLES IN SCHEMA OLYMPUS_ANALYTICS.GOLD TO ROLE STREAMLIT_ROLE;
   
   -- Grant usage on warehouse
   GRANT USAGE ON WAREHOUSE XS_WAREHOUSE TO ROLE STREAMLIT_ROLE;
   ```

---

## ⚙️ Step 3: Configuration & Testing

### A. Test Database Connection

1. **Run Test Query:**
   ```python
   # Add this to your app for testing
   test_query = "SELECT COUNT(*) as member_count FROM OLYMPUS_ANALYTICS.GOLD.GD_MEMBER_ENROLLMENT_DETAILS"
   result = session.sql(test_query).collect()
   st.write(f"Total members in database: {result[0]['MEMBER_COUNT']}")
   ```

### B. Deploy and Share

1. **Click "Deploy"** in the Streamlit interface

2. **Get Shareable URL:**
   - Format: `https://<account>.snowflakecomputing.com/streamlit/apps/<app-name>`
   - Share this URL with stakeholders

3. **Set Permissions:**
   ```sql
   -- Grant access to specific users/roles
   GRANT USAGE ON STREAMLIT OLYMPUS_ANALYTICS.PUBLIC.OLYMPUS_ANALYTICS_DASHBOARD TO ROLE <USER_ROLE>;
   ```

---

## 🔧 Step 4: Advanced Configuration

### A. Custom Domain (Enterprise)

1. **Configure Custom Domain:**
   - Contact Snowflake support for custom domain setup
   - Example: `analytics.yourcompany.com`

### B. Authentication & Security

1. **SSO Integration:**
   - Configure SAML/OAuth through Snowflake
   - Integrate with your organization's identity provider

2. **Row-Level Security:**
   ```sql
   -- Example: Restrict data by user context
   CREATE OR REPLACE ROW ACCESS POLICY member_access_policy AS (user_email) RETURNS BOOLEAN ->
     CURRENT_USER() = 'ADMIN' OR 
     user_email = CURRENT_USER();
   
   ALTER TABLE OLYMPUS_ANALYTICS.GOLD.GD_MEMBER_ENROLLMENT_DETAILS 
   ADD ROW ACCESS POLICY member_access_policy ON (email);
   ```

### C. Performance Optimization

1. **Warehouse Sizing:**
   ```sql
   -- Scale warehouse for better performance
   ALTER WAREHOUSE XS_WAREHOUSE SET WAREHOUSE_SIZE = 'SMALL';
   ```

2. **Query Optimization:**
   - Add indexes on frequently queried columns
   - Use clustering keys for large tables
   - Implement result caching

---

## 📊 Step 5: Monitoring & Maintenance

### A. Monitor Usage

1. **Query History:**
   ```sql
   SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY 
   WHERE USER_NAME = 'STREAMLIT_USER'
   ORDER BY START_TIME DESC;
   ```

2. **Warehouse Usage:**
   ```sql
   SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY 
   WHERE WAREHOUSE_NAME = 'XS_WAREHOUSE'
   ORDER BY START_TIME DESC;
   ```

### B. Data Refresh

1. **Automated Data Pipeline:**
   ```sql
   -- Create task for data refresh
   CREATE OR REPLACE TASK refresh_member_data
   WAREHOUSE = XS_WAREHOUSE
   SCHEDULE = 'USING CRON 0 6 * * * UTC'  -- Daily at 6 AM UTC
   AS
   CALL refresh_disco_data_procedure();
   
   ALTER TASK refresh_member_data RESUME;
   ```

---

## 🎯 Step 6: Go Live Checklist

### Pre-Launch
- [ ] **Data Validation:** Verify all 943 members are loaded
- [ ] **Permissions:** Test access with different user roles
- [ ] **Performance:** Test with expected user load
- [ ] **Backup:** Ensure data backup procedures are in place

### Launch
- [ ] **Deploy:** Push to production Streamlit environment
- [ ] **Monitor:** Watch for errors and performance issues
- [ ] **Document:** Share user guide with stakeholders
- [ ] **Support:** Establish support procedures

### Post-Launch
- [ ] **Feedback:** Collect user feedback for improvements
- [ ] **Optimize:** Fine-tune based on usage patterns
- [ ] **Scale:** Adjust warehouse size based on demand
- [ ] **Maintain:** Regular data refreshes and updates

---

## 🔗 Useful Resources

- **Streamlit in Snowflake Documentation:** [docs.snowflake.com/streamlit](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit)
- **Snowpark Python Guide:** [docs.snowflake.com/snowpark-python](https://docs.snowflake.com/en/developer-guide/snowpark/python/index)
- **Streamlit Documentation:** [docs.streamlit.io](https://docs.streamlit.io/)

---

## 💡 Tips for Success

1. **Start Simple:** Deploy basic version first, then add features
2. **Test Thoroughly:** Use development environment before production
3. **Monitor Costs:** Watch warehouse usage and optimize accordingly
4. **User Training:** Provide training materials for end users
5. **Iterative Improvement:** Continuously improve based on feedback

---

**Your Olympus Analytics dashboard is now ready for production deployment in Streamlit in Snowflake!** 🚀