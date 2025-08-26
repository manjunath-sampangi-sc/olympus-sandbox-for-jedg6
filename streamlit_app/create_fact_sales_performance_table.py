#!/usr/bin/env python3
"""
Script to create the missing FACT_SALES_PERFORMANCE table that the sales dashboard expects.
This table needs to include all columns referenced in the sales_performance.py query.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.snowflake_connector import SnowflakeConnector
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_fact_sales_performance_table():
    """Create the FACT_SALES_PERFORMANCE table with all required columns."""
    
    connector = SnowflakeConnector()
    
    try:
        # Use SYSADMIN role for table creation
        connector.execute_query("USE ROLE SYSADMIN")
        connector.execute_query("USE WAREHOUSE XS_WAREHOUSE")
        connector.execute_query("USE DATABASE OLYMPUS_ANALYTICS")
        connector.execute_query("USE SCHEMA GOLD")
        
        # Create FACT_SALES_PERFORMANCE table with all required columns
        create_table_sql = """
        CREATE OR REPLACE TABLE OLYMPUS_ANALYTICS.GOLD.FACT_SALES_PERFORMANCE (
            DEAL_ID VARCHAR(50) PRIMARY KEY,
            DEAL_NAME VARCHAR(255),
            CLIENT_NAME VARCHAR(255),
            SALES_REP VARCHAR(255),
            DEAL_VALUE NUMBER(15,2),
            STAGE VARCHAR(100),
            PROBABILITY NUMBER(5,2),
            CLOSE_DATE DATE,
            CREATED_DATE TIMESTAMP_NTZ,
            LAST_ACTIVITY_DATE TIMESTAMP_NTZ,
            SOURCE VARCHAR(100),
            INDUSTRY VARCHAR(100),
            REGION VARCHAR(100),
            AMOUNT NUMBER(15,2),
            CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            UPDATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
        )
        """
        
        logger.info("Creating FACT_SALES_PERFORMANCE table...")
        connector.execute_query(create_table_sql)
        logger.info("FACT_SALES_PERFORMANCE table created successfully")
        
        # Insert sample data
        insert_data_sql = """
        INSERT INTO OLYMPUS_ANALYTICS.GOLD.FACT_SALES_PERFORMANCE 
        (DEAL_ID, DEAL_NAME, CLIENT_NAME, SALES_REP, DEAL_VALUE, STAGE, PROBABILITY, CLOSE_DATE, CREATED_DATE, LAST_ACTIVITY_DATE, SOURCE, INDUSTRY, REGION, AMOUNT)
        VALUES 
        ('DEAL001', 'Enterprise Software License', 'TechCorp Inc', 'John Smith', 50000.00, 'Closed Won', 100.00, '2024-03-15', '2024-01-10 09:00:00', '2024-03-14 16:30:00', 'Website', 'Technology', 'North America', 50000.00),
        ('DEAL002', 'Consulting Services Package', 'HealthPlus Solutions', 'Sarah Johnson', 25000.00, 'Proposal', 75.00, '2024-04-20', '2024-02-05 14:30:00', '2024-04-18 11:15:00', 'Referral', 'Healthcare', 'Europe', 25000.00),
        ('DEAL003', 'Training & Development Program', 'EduLearn Academy', 'Mike Davis', 15000.00, 'Closed Won', 100.00, '2024-02-28', '2024-01-20 11:15:00', '2024-02-27 14:45:00', 'Cold Call', 'Education', 'Asia Pacific', 15000.00),
        ('DEAL004', 'Annual Support Contract', 'ManufacturePro Corp', 'Lisa Chen', 35000.00, 'Negotiation', 60.00, '2024-05-10', '2024-03-01 16:45:00', '2024-05-08 10:20:00', 'Trade Show', 'Manufacturing', 'North America', 35000.00),
        ('DEAL005', 'Custom Development Project', 'FinanceFirst Bank', 'David Wilson', 75000.00, 'Qualified', 40.00, '2024-06-15', '2024-03-15 10:20:00', '2024-06-12 15:30:00', 'LinkedIn', 'Financial Services', 'North America', 75000.00),
        ('DEAL006', 'Cloud Migration Services', 'RetailMax Group', 'Emily Rodriguez', 45000.00, 'Discovery', 25.00, '2024-07-01', '2024-04-10 13:45:00', '2024-06-28 09:15:00', 'Partner', 'Retail', 'Europe', 45000.00),
        ('DEAL007', 'Security Audit Package', 'SecureData Inc', 'Tom Anderson', 20000.00, 'Closed Won', 100.00, '2024-01-30', '2023-12-15 08:30:00', '2024-01-29 17:00:00', 'Webinar', 'Technology', 'North America', 20000.00),
        ('DEAL008', 'Analytics Platform License', 'DataDriven LLC', 'Maria Garcia', 60000.00, 'Proposal', 80.00, '2024-05-25', '2024-03-20 12:00:00', '2024-05-23 14:20:00', 'Website', 'Technology', 'North America', 60000.00),
        ('DEAL009', 'Training Workshop Series', 'SkillBuilder Co', 'James Taylor', 18000.00, 'Negotiation', 70.00, '2024-04-15', '2024-02-28 15:15:00', '2024-04-13 11:45:00', 'Referral', 'Education', 'Europe', 18000.00),
        ('DEAL010', 'Integration Services', 'ConnectAll Systems', 'Anna White', 40000.00, 'Discovery', 30.00, '2024-06-30', '2024-04-05 09:30:00', '2024-06-27 16:10:00', 'Cold Call', 'Technology', 'Asia Pacific', 40000.00)
        """
        
        logger.info("Inserting sample data into FACT_SALES_PERFORMANCE table...")
        connector.execute_query(insert_data_sql)
        logger.info("Sample data inserted successfully")
        
        # Grant permissions to OLYMPUS_CONTRACTOR
        grant_permissions_sql = """
        GRANT SELECT, INSERT, UPDATE, DELETE ON OLYMPUS_ANALYTICS.GOLD.FACT_SALES_PERFORMANCE TO ROLE OLYMPUS_CONTRACTOR
        """
        
        logger.info("Granting permissions to OLYMPUS_CONTRACTOR...")
        connector.execute_query(grant_permissions_sql)
        logger.info("Permissions granted successfully")
        
        # Verify the table creation
        verify_sql = "SELECT COUNT(*) as record_count FROM OLYMPUS_ANALYTICS.GOLD.FACT_SALES_PERFORMANCE"
        result = connector.execute_query(verify_sql)
        
        if result is not None and not result.empty:
            record_count = result.iloc[0]['RECORD_COUNT']
            logger.info(f"FACT_SALES_PERFORMANCE table created successfully with {record_count} records")
        else:
            logger.warning("Could not verify table creation")
            
    except Exception as e:
        logger.error(f"Error creating FACT_SALES_PERFORMANCE table: {str(e)}")
        raise
    finally:
        connector.close()

if __name__ == "__main__":
    create_fact_sales_performance_table()
    print("FACT_SALES_PERFORMANCE table creation completed!")