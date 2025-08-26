#!/usr/bin/env python3
"""
Script to create missing DIM_USERS table and fix the course_name column issue.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.snowflake_connector import SnowflakeConnector
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_missing_tables():
    """Create missing DIM_USERS table and add course_name to DIM_COURSES if needed."""
    
    connector = SnowflakeConnector()
    
    try:
        # Use SYSADMIN role for table creation
        connector.execute_query("USE ROLE SYSADMIN")
        connector.execute_query("USE WAREHOUSE XS_WAREHOUSE")
        connector.execute_query("USE DATABASE OLYMPUS_ANALYTICS")
        connector.execute_query("USE SCHEMA GOLD")
        
        # Create DIM_USERS table
        create_dim_users_sql = """
        CREATE OR REPLACE TABLE OLYMPUS_ANALYTICS.GOLD.DIM_USERS (
            USER_ID VARCHAR(50) PRIMARY KEY,
            FIRST_NAME VARCHAR(100),
            LAST_NAME VARCHAR(100),
            EMAIL VARCHAR(255),
            DEPARTMENT VARCHAR(100),
            JOB_TITLE VARCHAR(100),
            MANAGER_ID VARCHAR(50),
            HIRE_DATE DATE,
            STATUS VARCHAR(20),
            LAST_LOGIN_DATE DATE,
            CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            UPDATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
        )
        """
        
        logger.info("Creating DIM_USERS table...")
        connector.execute_query(create_dim_users_sql)
        logger.info("DIM_USERS table created successfully")
        
        # Insert sample data into DIM_USERS
        insert_users_sql = """
        INSERT INTO OLYMPUS_ANALYTICS.GOLD.DIM_USERS 
        (USER_ID, FIRST_NAME, LAST_NAME, EMAIL, DEPARTMENT, JOB_TITLE, MANAGER_ID, HIRE_DATE, STATUS, LAST_LOGIN_DATE)
        VALUES 
        ('U001', 'John', 'Smith', 'john.smith@company.com', 'Sales', 'Sales Representative', 'M001', '2023-01-15', 'Active', '2024-12-20'),
        ('U002', 'Sarah', 'Johnson', 'sarah.johnson@company.com', 'Marketing', 'Marketing Specialist', 'M002', '2023-03-10', 'Active', '2024-12-19'),
        ('U003', 'Mike', 'Davis', 'mike.davis@company.com', 'Engineering', 'Software Engineer', 'M003', '2023-02-20', 'Active', '2024-12-21'),
        ('U004', 'Emily', 'Brown', 'emily.brown@company.com', 'HR', 'HR Coordinator', 'M004', '2023-04-05', 'Active', '2024-12-18'),
        ('U005', 'David', 'Wilson', 'david.wilson@company.com', 'Sales', 'Senior Sales Rep', 'M001', '2022-11-12', 'Active', '2024-12-20'),
        ('U006', 'Lisa', 'Anderson', 'lisa.anderson@company.com', 'Marketing', 'Content Manager', 'M002', '2023-05-18', 'Active', '2024-12-17'),
        ('U007', 'James', 'Taylor', 'james.taylor@company.com', 'Engineering', 'DevOps Engineer', 'M003', '2023-06-22', 'Active', '2024-12-21'),
        ('U008', 'Anna', 'Martinez', 'anna.martinez@company.com', 'Finance', 'Financial Analyst', 'M005', '2023-07-30', 'Active', '2024-12-19'),
        ('U009', 'Robert', 'Garcia', 'robert.garcia@company.com', 'Sales', 'Account Manager', 'M001', '2023-08-14', 'Active', '2024-12-20'),
        ('U010', 'Jennifer', 'Lee', 'jennifer.lee@company.com', 'Engineering', 'Senior Developer', 'M003', '2022-09-05', 'Active', '2024-12-18')
        """
        
        logger.info("Inserting sample data into DIM_USERS...")
        connector.execute_query(insert_users_sql)
        logger.info("Sample data inserted into DIM_USERS successfully")
        
        # Check if DIM_COURSES already has course_name column
        check_courses_sql = "DESCRIBE TABLE OLYMPUS_ANALYTICS.GOLD.DIM_COURSES"
        courses_desc = connector.execute_query(check_courses_sql)
        
        has_course_name = any(row['name'].upper() == 'COURSE_NAME' for _, row in courses_desc.iterrows())
        
        if not has_course_name:
            logger.info("Adding course_name column to DIM_COURSES...")
            # Add course_name column to DIM_COURSES
            alter_courses_sql = """
            ALTER TABLE OLYMPUS_ANALYTICS.GOLD.DIM_COURSES 
            ADD COLUMN COURSE_NAME VARCHAR(255)
            """
            connector.execute_query(alter_courses_sql)
            
            # Update course_name based on course_id
            update_courses_sql = """
            UPDATE OLYMPUS_ANALYTICS.GOLD.DIM_COURSES 
            SET COURSE_NAME = CASE 
                WHEN COURSE_ID = 'C001' THEN 'Python Programming Fundamentals'
                WHEN COURSE_ID = 'C002' THEN 'Advanced SQL and Data Analysis'
                WHEN COURSE_ID = 'C003' THEN 'Leadership and Team Management'
                WHEN COURSE_ID = 'C004' THEN 'Digital Marketing Strategies'
                WHEN COURSE_ID = 'C005' THEN 'Project Management Essentials'
                ELSE 'General Course'
            END
            """
            connector.execute_query(update_courses_sql)
            logger.info("course_name column added and updated successfully")
        else:
            logger.info("course_name column already exists in DIM_COURSES")
        
        # Grant permissions to OLYMPUS_CONTRACTOR
        grant_users_sql = """
        GRANT SELECT, INSERT, UPDATE, DELETE ON OLYMPUS_ANALYTICS.GOLD.DIM_USERS 
        TO ROLE OLYMPUS_CONTRACTOR
        """
        
        grant_courses_sql = """
        GRANT SELECT, INSERT, UPDATE, DELETE ON OLYMPUS_ANALYTICS.GOLD.DIM_COURSES 
        TO ROLE OLYMPUS_CONTRACTOR
        """
        
        logger.info("Granting permissions to OLYMPUS_CONTRACTOR...")
        connector.execute_query(grant_users_sql)
        connector.execute_query(grant_courses_sql)
        logger.info("Permissions granted successfully")
        
        logger.info("Missing tables and columns setup completed successfully!")
        
    except Exception as e:
        logger.error(f"Error creating missing tables: {str(e)}")
        raise
    finally:
        connector.close()

if __name__ == "__main__":
    create_missing_tables()