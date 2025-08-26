#!/usr/bin/env python3
"""
Script to fix the FACT_LEARNING_ANALYTICS table schema to match application expectations.
The table needs an 'enrollment_date' column instead of 'learning_date'.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.snowflake_connector import SnowflakeConnector
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_learning_analytics_schema():
    """Fix the FACT_LEARNING_ANALYTICS table schema to include enrollment_date."""
    
    connector = SnowflakeConnector()
    
    try:
        # Use SYSADMIN role for table modification
        connector.execute_query("USE ROLE SYSADMIN")
        connector.execute_query("USE WAREHOUSE XS_WAREHOUSE")
        connector.execute_query("USE DATABASE OLYMPUS_ANALYTICS")
        connector.execute_query("USE SCHEMA GOLD")
        
        # Recreate FACT_LEARNING_ANALYTICS table with correct schema
        create_table_sql = """
        CREATE OR REPLACE TABLE OLYMPUS_ANALYTICS.GOLD.FACT_LEARNING_ANALYTICS (
            LEARNING_ID VARCHAR(50) PRIMARY KEY,
            USER_ID VARCHAR(50),
            COURSE_ID VARCHAR(50),
            COMPLETION_STATUS VARCHAR(20),
            PROGRESS_PERCENTAGE NUMBER(5,2),
            TIME_SPENT_MINUTES NUMBER(10,2),
            QUIZ_SCORE NUMBER(5,2),
            CERTIFICATION_EARNED BOOLEAN,
            ENROLLMENT_DATE DATE,
            LEARNING_DATE DATE,
            LAST_ACCESSED_DATE DATE,
            CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            UPDATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
        )
        """
        
        logger.info("Recreating FACT_LEARNING_ANALYTICS table with correct schema...")
        connector.execute_query(create_table_sql)
        logger.info("FACT_LEARNING_ANALYTICS table recreated successfully")
        
        # Insert sample data with enrollment_date
        insert_data_sql = """
        INSERT INTO OLYMPUS_ANALYTICS.GOLD.FACT_LEARNING_ANALYTICS 
        (LEARNING_ID, USER_ID, COURSE_ID, COMPLETION_STATUS, PROGRESS_PERCENTAGE, 
         TIME_SPENT_MINUTES, QUIZ_SCORE, CERTIFICATION_EARNED, ENROLLMENT_DATE, LEARNING_DATE, LAST_ACCESSED_DATE)
        VALUES 
        ('L001', 'U001', 'C001', 'Completed', 100.00, 120.50, 95.00, TRUE, '2024-01-10', '2024-01-15', '2024-01-15'),
        ('L002', 'U002', 'C001', 'In Progress', 75.00, 90.25, 88.50, FALSE, '2024-01-05', '2024-01-10', '2024-01-20'),
        ('L003', 'U003', 'C002', 'Completed', 100.00, 180.75, 92.00, TRUE, '2024-01-08', '2024-01-12', '2024-01-12'),
        ('L004', 'U001', 'C002', 'In Progress', 60.00, 85.00, 78.00, FALSE, '2024-01-15', '2024-01-18', '2024-01-25'),
        ('L005', 'U004', 'C003', 'Completed', 100.00, 150.25, 96.50, TRUE, '2024-01-03', '2024-01-08', '2024-01-08'),
        ('L006', 'U002', 'C003', 'Not Started', 0.00, 0.00, 0.00, FALSE, '2024-01-18', '2024-01-20', '2024-01-20'),
        ('L007', 'U005', 'C001', 'Completed', 100.00, 110.00, 89.00, TRUE, '2024-01-12', '2024-01-14', '2024-01-14'),
        ('L008', 'U003', 'C004', 'In Progress', 45.00, 65.50, 82.00, FALSE, '2024-01-14', '2024-01-16', '2024-01-28'),
        ('L009', 'U006', 'C002', 'Completed', 100.00, 175.25, 94.50, TRUE, '2024-01-09', '2024-01-11', '2024-01-11'),
        ('L010', 'U004', 'C004', 'In Progress', 80.00, 95.75, 91.00, FALSE, '2024-01-17', '2024-01-19', '2024-01-30'),
        ('L011', 'U007', 'C001', 'Completed', 100.00, 135.00, 93.50, TRUE, '2024-11-01', '2024-11-05', '2024-11-05'),
        ('L012', 'U008', 'C002', 'In Progress', 85.00, 105.25, 87.00, FALSE, '2024-11-15', '2024-11-18', '2024-12-01'),
        ('L013', 'U009', 'C003', 'Completed', 100.00, 160.75, 96.00, TRUE, '2024-12-01', '2024-12-05', '2024-12-05'),
        ('L014', 'U010', 'C004', 'In Progress', 70.00, 88.50, 84.00, FALSE, '2024-12-10', '2024-12-12', '2024-12-20')
        """
        
        logger.info("Inserting sample data into FACT_LEARNING_ANALYTICS...")
        connector.execute_query(insert_data_sql)
        logger.info("Sample data inserted successfully")
        
        # Grant permissions to OLYMPUS_CONTRACTOR
        grant_sql = """
        GRANT SELECT, INSERT, UPDATE, DELETE ON OLYMPUS_ANALYTICS.GOLD.FACT_LEARNING_ANALYTICS 
        TO ROLE OLYMPUS_CONTRACTOR
        """
        
        logger.info("Granting permissions to OLYMPUS_CONTRACTOR...")
        connector.execute_query(grant_sql)
        logger.info("Permissions granted successfully")
        
        logger.info("FACT_LEARNING_ANALYTICS table schema fix completed successfully!")
        
    except Exception as e:
        logger.error(f"Error fixing FACT_LEARNING_ANALYTICS table schema: {str(e)}")
        raise
    finally:
        connector.close()

if __name__ == "__main__":
    fix_learning_analytics_schema()