#!/usr/bin/env python3
"""
Script to fix privileges and create tables with proper permissions
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.snowflake_connector import get_snowflake_connector
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_and_fix_privileges(connector):
    """Check current privileges and try to fix them"""
    
    # Check current role and privileges
    check_queries = [
        "SELECT CURRENT_ROLE()",
        "SELECT CURRENT_USER()",
        "SELECT CURRENT_WAREHOUSE()",
        "SELECT CURRENT_DATABASE()",
        "SELECT CURRENT_SCHEMA()",
        "SHOW GRANTS TO ROLE OLYMPUS_CONTRACTOR",
        "USE ROLE SYSADMIN",
        "USE DATABASE OLYMPUS_ANALYTICS",
        "USE SCHEMA GOLD"
    ]
    
    for query in check_queries:
        try:
            if query.startswith("SHOW") or query.startswith("SELECT"):
                result = connector.execute_query(query)
                logger.info(f"✓ {query}: {result.iloc[0, 0] if len(result) > 0 else 'No results'}")
            else:
                with connector.get_cursor() as cursor:
                    cursor.execute(query)
                logger.info(f"✓ {query}: Success")
        except Exception as e:
            logger.error(f"✗ {query}: {str(e)}")
    
    # Try to grant necessary privileges
    privilege_queries = [
        "USE ROLE SYSADMIN",
        "GRANT USAGE ON DATABASE OLYMPUS_ANALYTICS TO ROLE OLYMPUS_CONTRACTOR",
        "GRANT USAGE ON SCHEMA OLYMPUS_ANALYTICS.GOLD TO ROLE OLYMPUS_CONTRACTOR",
        "GRANT CREATE TABLE ON SCHEMA OLYMPUS_ANALYTICS.GOLD TO ROLE OLYMPUS_CONTRACTOR",
        "GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA OLYMPUS_ANALYTICS.GOLD TO ROLE OLYMPUS_CONTRACTOR",
        "GRANT SELECT, INSERT, UPDATE, DELETE ON FUTURE TABLES IN SCHEMA OLYMPUS_ANALYTICS.GOLD TO ROLE OLYMPUS_CONTRACTOR",
        "USE ROLE OLYMPUS_CONTRACTOR"
    ]
    
    logger.info("\nAttempting to fix privileges...")
    for query in privilege_queries:
        try:
            with connector.get_cursor() as cursor:
                cursor.execute(query)
            logger.info(f"✓ {query}: Success")
        except Exception as e:
            logger.error(f"✗ {query}: {str(e)}")

def create_tables_as_sysadmin(connector):
    """Create tables using SYSADMIN role"""
    
    # Switch to SYSADMIN role
    try:
        with connector.get_cursor() as cursor:
            cursor.execute("USE ROLE SYSADMIN")
            cursor.execute("USE DATABASE OLYMPUS_ANALYTICS")
            cursor.execute("USE SCHEMA GOLD")
        logger.info("✓ Switched to SYSADMIN role")
    except Exception as e:
        logger.error(f"✗ Error switching to SYSADMIN: {str(e)}")
        return False
    
    # Create tables
    create_table_queries = [
        """
        CREATE OR REPLACE TABLE FACT_SALES_PERFORMANCE (
            deal_id VARCHAR(50),
            contact_id VARCHAR(50),
            deal_name VARCHAR(255),
            amount DECIMAL(15,2),
            stage VARCHAR(100),
            probability DECIMAL(5,2),
            close_date DATE,
            created_date TIMESTAMP,
            owner_name VARCHAR(255),
            company VARCHAR(255),
            source VARCHAR(100),
            deal_type VARCHAR(100),
            region VARCHAR(100),
            industry VARCHAR(100)
        )
        """,
        
        """
        CREATE OR REPLACE TABLE DIM_CONTACTS (
            contact_id VARCHAR(50),
            email VARCHAR(255),
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            full_name VARCHAR(255),
            company VARCHAR(255),
            job_title VARCHAR(255),
            phone VARCHAR(50),
            lead_status VARCHAR(50),
            lifecycle_stage VARCHAR(50),
            created_date TIMESTAMP,
            last_modified_date TIMESTAMP,
            source VARCHAR(100),
            region VARCHAR(100),
            industry VARCHAR(100)
        )
        """,
        
        """
        CREATE OR REPLACE TABLE FACT_LEARNING_PERFORMANCE (
            enrollment_id VARCHAR(50),
            user_id VARCHAR(50),
            course_id VARCHAR(50),
            course_name VARCHAR(255),
            course_category VARCHAR(100),
            enrollment_date DATE,
            completion_date DATE,
            progress_percentage DECIMAL(5,2),
            time_spent_minutes INTEGER,
            quiz_score DECIMAL(5,2),
            certification_earned BOOLEAN,
            last_activity_date DATE,
            department VARCHAR(100),
            job_level VARCHAR(100),
            location VARCHAR(100)
        )
        """,
        
        """
        CREATE OR REPLACE TABLE DIM_COURSES (
            course_id VARCHAR(50),
            course_name VARCHAR(255),
            course_category VARCHAR(100),
            course_description TEXT,
            duration_minutes INTEGER,
            difficulty_level VARCHAR(50),
            instructor VARCHAR(255),
            created_date TIMESTAMP,
            last_updated TIMESTAMP,
            is_active BOOLEAN
        )
        """
    ]
    
    success_count = 0
    for i, query in enumerate(create_table_queries, 1):
        try:
            with connector.get_cursor() as cursor:
                cursor.execute(query)
            logger.info(f"✓ Created table {i}/{len(create_table_queries)}")
            success_count += 1
        except Exception as e:
            logger.error(f"✗ Error creating table {i}: {str(e)}")
    
    # Insert sample data
    insert_queries = [
        """
        INSERT INTO FACT_SALES_PERFORMANCE VALUES
        ('DEAL001', 'CONT001', 'Enterprise Software License', 50000.00, 'Closed Won', 100.00, '2024-03-15', '2024-01-10 09:00:00', 'John Smith', 'TechCorp Inc', 'Website', 'New Business', 'North America', 'Technology'),
        ('DEAL002', 'CONT002', 'Consulting Services', 25000.00, 'Proposal', 75.00, '2024-04-20', '2024-02-05 14:30:00', 'Sarah Johnson', 'HealthPlus', 'Referral', 'Expansion', 'Europe', 'Healthcare'),
        ('DEAL003', 'CONT003', 'Training Package', 15000.00, 'Closed Won', 100.00, '2024-02-28', '2024-01-20 11:15:00', 'Mike Davis', 'EduLearn', 'Cold Call', 'New Business', 'Asia Pacific', 'Education'),
        ('DEAL004', 'CONT004', 'Support Contract', 35000.00, 'Negotiation', 60.00, '2024-05-10', '2024-03-01 16:45:00', 'Lisa Chen', 'ManufacturePro', 'Trade Show', 'Renewal', 'North America', 'Manufacturing'),
        ('DEAL005', 'CONT005', 'Custom Development', 75000.00, 'Qualified', 40.00, '2024-06-15', '2024-03-15 10:20:00', 'David Wilson', 'FinanceFirst', 'LinkedIn', 'New Business', 'North America', 'Financial Services')
        """,
        
        """
        INSERT INTO DIM_CONTACTS VALUES
        ('CONT001', 'john.doe@techcorp.com', 'John', 'Doe', 'John Doe', 'TechCorp Inc', 'CTO', '+1-555-0101', 'Customer', 'Customer', '2024-01-10 09:00:00', '2024-03-15 12:00:00', 'Website', 'North America', 'Technology'),
        ('CONT002', 'sarah.smith@healthplus.com', 'Sarah', 'Smith', 'Sarah Smith', 'HealthPlus', 'VP Operations', '+1-555-0102', 'Opportunity', 'Opportunity', '2024-02-05 14:30:00', '2024-04-10 16:20:00', 'Referral', 'Europe', 'Healthcare'),
        ('CONT003', 'mike.johnson@edulearn.com', 'Mike', 'Johnson', 'Mike Johnson', 'EduLearn', 'Training Director', '+1-555-0103', 'Customer', 'Customer', '2024-01-20 11:15:00', '2024-02-28 09:45:00', 'Cold Call', 'Asia Pacific', 'Education'),
        ('CONT004', 'lisa.brown@manufacturepro.com', 'Lisa', 'Brown', 'Lisa Brown', 'ManufacturePro', 'IT Manager', '+1-555-0104', 'Qualified Lead', 'SQL', '2024-03-01 16:45:00', '2024-04-15 14:10:00', 'Trade Show', 'North America', 'Manufacturing'),
        ('CONT005', 'david.wilson@financefirst.com', 'David', 'Wilson', 'David Wilson', 'FinanceFirst', 'Head of Technology', '+1-555-0105', 'Marketing Qualified Lead', 'MQL', '2024-03-15 10:20:00', '2024-04-20 11:30:00', 'LinkedIn', 'North America', 'Financial Services')
        """,
        
        """
        INSERT INTO FACT_LEARNING_PERFORMANCE VALUES
        ('ENR001', 'USER001', 'COURSE001', 'Data Analytics Fundamentals', 'Analytics', '2024-01-15', '2024-02-15', 100.00, 480, 92.5, TRUE, '2024-02-15', 'IT', 'Senior', 'New York'),
        ('ENR002', 'USER002', 'COURSE002', 'Leadership Excellence', 'Leadership', '2024-01-20', '2024-02-20', 85.00, 360, 88.0, TRUE, '2024-02-18', 'Sales', 'Manager', 'London'),
        ('ENR003', 'USER003', 'COURSE003', 'Project Management Basics', 'Management', '2024-02-01', NULL, 65.00, 240, 75.5, FALSE, '2024-03-10', 'Operations', 'Associate', 'Tokyo'),
        ('ENR004', 'USER004', 'COURSE001', 'Data Analytics Fundamentals', 'Analytics', '2024-02-10', '2024-03-10', 100.00, 450, 95.0, TRUE, '2024-03-10', 'Marketing', 'Senior', 'Sydney'),
        ('ENR005', 'USER005', 'COURSE004', 'Customer Service Excellence', 'Customer Service', '2024-02-15', '2024-03-01', 90.00, 300, 87.5, TRUE, '2024-03-01', 'Support', 'Associate', 'Toronto')
        """,
        
        """
        INSERT INTO DIM_COURSES VALUES
        ('COURSE001', 'Data Analytics Fundamentals', 'Analytics', 'Learn the basics of data analysis and visualization', 480, 'Intermediate', 'Dr. Jane Smith', '2024-01-01 00:00:00', '2024-01-01 00:00:00', TRUE),
        ('COURSE002', 'Leadership Excellence', 'Leadership', 'Develop essential leadership skills for modern managers', 360, 'Advanced', 'Prof. John Davis', '2024-01-01 00:00:00', '2024-01-01 00:00:00', TRUE),
        ('COURSE003', 'Project Management Basics', 'Management', 'Introduction to project management methodologies', 300, 'Beginner', 'Sarah Wilson', '2024-01-01 00:00:00', '2024-01-01 00:00:00', TRUE),
        ('COURSE004', 'Customer Service Excellence', 'Customer Service', 'Master customer service best practices', 240, 'Intermediate', 'Mike Johnson', '2024-01-01 00:00:00', '2024-01-01 00:00:00', TRUE),
        ('COURSE005', 'Digital Marketing Strategy', 'Marketing', 'Comprehensive digital marketing course', 420, 'Advanced', 'Lisa Chen', '2024-01-01 00:00:00', '2024-01-01 00:00:00', TRUE)
        """
    ]
    
    for i, query in enumerate(insert_queries, 1):
        try:
            with connector.get_cursor() as cursor:
                cursor.execute(query)
            logger.info(f"✓ Inserted sample data {i}/{len(insert_queries)}")
            success_count += 1
        except Exception as e:
            logger.error(f"✗ Error inserting data {i}: {str(e)}")
    
    # Grant permissions to OLYMPUS_CONTRACTOR
    try:
        with connector.get_cursor() as cursor:
            cursor.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA OLYMPUS_ANALYTICS.GOLD TO ROLE OLYMPUS_CONTRACTOR")
        logger.info("✓ Granted permissions to OLYMPUS_CONTRACTOR")
    except Exception as e:
        logger.error(f"✗ Error granting permissions: {str(e)}")
    
    return success_count

def main():
    """Main execution function"""
    logger.info("Fixing privileges and creating GOLD layer tables...")
    
    try:
        connector = get_snowflake_connector()
        if not connector.connect():
            logger.error("Failed to connect to Snowflake")
            return False
        
        logger.info("✓ Connected to Snowflake successfully")
        
        # Check and fix privileges
        check_and_fix_privileges(connector)
        
        # Create tables as SYSADMIN
        success_count = create_tables_as_sysadmin(connector)
        
        logger.info(f"\n=== EXECUTION SUMMARY ===")
        logger.info(f"✓ Successful operations: {success_count}")
        
        if success_count > 0:
            logger.info("🎉 Database setup completed successfully!")
            return True
        else:
            logger.warning("⚠️  Database setup had issues")
            return False
            
    except Exception as e:
        logger.error(f"Fatal error during setup: {str(e)}")
        return False
    
    finally:
        if 'connector' in locals():
            connector.close()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)