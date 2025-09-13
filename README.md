# Olympus Analytics - Setup and Deployment Guide

## Overview
Olympus Analytics is a comprehensive data pipeline and dashboard solution that integrates with Disco LMS to provide billing analytics and KPI tracking. The system consists of:

- **dbt Pipeline**: Bronze → Silver → Gold data transformation layers
- **Streamlit Dashboard**: Interactive web application for data visualization
- **Snowflake Integration**: Cloud data warehouse for storage and processing
- **Disco LMS API**: Real-time data ingestion from learning management system

## Prerequisites

### System Requirements
- Python 3.8 or higher
- Git
- Access to Snowflake account
- Disco LMS API credentials

### Required Accounts & Credentials
1. **Snowflake Account**
   - Account identifier
   - Username and password
   - Warehouse, database, and schema access
   - Role with appropriate privileges

2. **Disco LMS API**
   - API key with read access to:
     - Communities
     - Members
     - Courses/Products
     - Enrollments

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd upwork
```

### 2. Set Up Python Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
cd streamlit_app
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:
```bash
# Snowflake Configuration
SNOWFLAKE_ACCOUNT=your_account_identifier
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ROLE=your_role
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=OLYMPUS_ANALYTICS
SNOWFLAKE_SCHEMA=PUBLIC

# Disco API Configuration
DISCO_API_KEY=your_disco_api_key
DISCO_BASE_URL=https://api.disco.co
```

### 4. Configure Streamlit Secrets

Copy the secrets template and configure:
```bash
cd streamlit_app/.streamlit
cp secrets.toml.template secrets.toml
```

Edit `secrets.toml` with your credentials:
```toml
[snowflake]
account = "your_account_identifier"
user = "your_username"
password = "your_password"
role = "your_role"
warehouse = "your_warehouse"
database = "OLYMPUS_ANALYTICS"
schema = "PUBLIC"

[disco]
api_key = "your_disco_api_key"
base_url = "https://api.disco.co"

[app]
debug = false
```

## Database Setup

### 1. Initialize Snowflake Database
```bash
# Run database setup script
python execute_setup.py
```

This script will:
- Create the OLYMPUS_ANALYTICS database
- Set up required schemas (BRONZE, SILVER, GOLD)
- Configure user privileges
- Create initial table structures

### 2. Run dbt Pipeline
```bash
cd ../dbt_olympus_analytics

# Install dbt dependencies
dbt deps

# Test dbt configuration
dbt debug

# Run data pipeline
dbt run

# Run tests
dbt test
```

## Running the Application

### 1. Start Data Ingestion
```bash
# Run Disco API data extraction
python run_disco_pipeline.py
```

### 2. Launch Streamlit Dashboard
```bash
cd streamlit_app
streamlit run app.py
```

The dashboard will be available at: `http://localhost:8501`

## Application Features

### Dashboard Pages
1. **Main Dashboard**: Overview of key metrics and KPIs
2. **Billing Dashboard**: Member billing bracket analysis
3. **Learning Analytics**: Course enrollment and completion tracking
4. **Sales Performance**: Revenue and sales team metrics
5. **AI Chat**: Natural language querying with Snowflake Cortex
6. **Settings**: Configuration and data export options

### Key Functionality
- **Real-time Data**: Live integration with Disco LMS API
- **Billing KPIs**: Automated billing bracket calculations
  - $0: No course enrollments
  - $10: Home course only
  - $50: Multiple courses or non-Home course
- **CSV Export**: Download billing and analytics data
- **Interactive Filters**: Month, community, and member group filtering
- **AI-Powered Chat**: Natural language data queries

## Data Pipeline Architecture

### Bronze Layer (Raw Data)
- `brz_disco_communities`: Community information
- `brz_disco_members`: Member profiles
- `brz_disco_courses`: Course/product catalog
- `brz_disco_enrollments`: Enrollment records

### Silver Layer (Cleaned Data)
- `slv_disco_enrollments`: Processed enrollment data
- `int_learning_analytics`: Learning analytics integration
- `int_users_unified`: Unified user profiles

### Gold Layer (Business KPIs)
- `gd_member_billing_brackets_monthly`: Monthly billing calculations
- `fact_learning_analytics`: Learning performance metrics
- `fact_sales_performance`: Sales team performance
- `dim_users`: User dimension table
- `dim_courses`: Course dimension table

## Troubleshooting

### Common Issues

1. **Snowflake Connection Errors**
   - Verify credentials in `secrets.toml`
   - Check network connectivity
   - Ensure role has required privileges

2. **dbt Compilation Errors**
   - Run `dbt debug` to check configuration
   - Verify model dependencies
   - Check for naming conflicts

3. **API Integration Issues**
   - Validate Disco API key
   - Check API rate limits
   - Verify endpoint accessibility

4. **Streamlit Startup Issues**
   - Ensure virtual environment is activated
   - Check port 8501 availability
   - Verify all dependencies are installed

### Logs and Debugging
- dbt logs: `dbt_olympus_analytics/logs/`
- Streamlit logs: Check terminal output
- Application logs: Available in dashboard settings

## Deployment

### Production Deployment
1. **Environment Configuration**
   - Set production Snowflake credentials
   - Configure production Disco API endpoints
   - Update database and schema names

2. **Security Considerations**
   - Use environment variables for all secrets
   - Enable SSL/TLS for database connections
   - Implement proper access controls
   - Regular credential rotation

3. **Monitoring**
   - Set up data pipeline monitoring
   - Configure alerting for failed runs
   - Monitor API rate limits
   - Track dashboard performance

### Scaling Considerations
- **Data Volume**: Optimize dbt models for large datasets
- **Concurrent Users**: Consider Streamlit scaling options
- **API Limits**: Implement rate limiting and caching
- **Database Performance**: Monitor and optimize queries

## Support and Maintenance

### Regular Tasks
- Monitor data pipeline execution
- Update API credentials as needed
- Review and optimize query performance
- Backup configuration files

### Updates and Upgrades
- Keep dependencies updated
- Monitor dbt and Streamlit releases
- Test changes in development environment
- Document configuration changes

## Contact Information
For technical support or questions about this deployment, please refer to the project documentation or contact the development team.