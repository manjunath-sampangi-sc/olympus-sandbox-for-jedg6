#!/usr/bin/env python3
"""
Script to create the missing GOLD layer tables for Olympus Analytics
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.snowflake_connector import get_snowflake_connector
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_gold_tables(connector):
    """Create the GOLD layer tables"""
    
    # SQL statements to create GOLD tables
    gold_tables_sql = [
        """
        CREATE OR REPLACE TABLE OLYMPUS_ANALYTICS.GOLD.FACT_SALES_PERFORMANCE (
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
        CREATE OR REPLACE TABLE OLYMPUS_ANALYTICS.GOLD.DIM_CONTACTS (
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
        CREATE OR REPLACE TABLE OLYMPUS_ANALYTICS.GOLD.FACT_LEARNING_PERFORMANCE (
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
        CREATE OR REPLACE TABLE OLYMPUS_ANALYTICS.GOLD.DIM_COURSES (
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
    
    # Sample data insertion statements
    sample_data_sql = [
        """
        INSERT INTO OLYMPUS_ANALYTICS.GOLD.FACT_SALES_PERFORMANCE VALUES
        ('DEAL001', 'CONT001', 'Enterprise Software License', 50000.00, 'Closed Won', 100.00, '2024-03-15', '2024-01-10 09:00:00', 'John Smith', 'TechCorp Inc', 'Website', 'New Business', 'North America', 'Technology'),
        ('DEAL002', 'CONT002', 'Consulting Services', 25000.00, 'Proposal', 75.00, '2024-04-20', '2024-02-05 14:30:00', 'Sarah Johnson', 'HealthPlus', 'Referral', 'Expansion', 'Europe', 'Healthcare'),
        ('DEAL003', 'CONT003', 'Training Package', 15000.00, 'Closed Won', 100.00, '2024-02-28', '2024-01-20 11:15:00', 'Mike Davis', 'EduLearn', 'Cold Call', 'New Business', 'Asia Pacific', 'Education'),
        ('DEAL004', 'CONT004', 'Support Contract', 35000.00, 'Negotiation', 60.00, '2024-05-10', '2024-03-01 16:45:00', 'Lisa Chen', 'ManufacturePro', 'Trade Show', 'Renewal', 'North America', 'Manufacturing'),
        ('DEAL005', 'CONT005', 'Custom Development', 75000.00, 'Qualified', 40.00, '2024-06-15', '2024-03-15 10:20:00', 'David Wilson', 'FinanceFirst', 'LinkedIn', 'New Business', 'North America', 'Financial Services')
        """,
        
        """
        INSERT INTO OLYMPUS_ANALYTICS.GOLD.DIM_CONTACTS VALUES
        ('CONT001', 'john.doe@techcorp.com', 'John', 'Doe', 'John Doe', 'TechCorp Inc', 'CTO', '+1-555-0101', 'Customer', 'Customer', '2024-01-10 09:00:00', '2024-03-15 12:00:00', 'Website', 'North America', 'Technology'),
        ('CONT002', 'sarah.smith@healthplus.com', 'Sarah', 'Smith', 'Sarah Smith', 'HealthPlus', 'VP Operations', '+1-555-0102', 'Opportunity', 'Opportunity', '2024-02-05 14:30:00', '2024-04-10 16:20:00', 'Referral', 'Europe', 'Healthcare'),
        ('CONT003', 'mike.johnson@edulearn.com', 'Mike', 'Johnson', 'Mike Johnson', 'EduLearn', 'Training Director', '+1-555-0103', 'Customer', 'Customer', '2024-01-20 11:15:00', '2024-02-28 09:45:00', 'Cold Call', 'Asia Pacific', 'Education'),
        ('CONT004', 'lisa.brown@manufacturepro.com', 'Lisa', 'Brown', 'Lisa Brown', 'ManufacturePro', 'IT Manager', '+1-555-0104', 'Qualified Lead', 'SQL', '2024-03-01 16:45:00', '2024-04-15 14:10:00', 'Trade Show', 'North America', 'Manufacturing'),
        ('CONT005', 'david.wilson@financefirst.com', 'David', 'Wilson', 'David Wilson', 'FinanceFirst', 'Head of Technology', '+1-555-0105', 'Marketing Qualified Lead', 'MQL', '2024-03-15 10:20:00', '2024-04-20 11:30:00', 'LinkedIn', 'North America', 'Financial Services')
        """,
        
        """
        INSERT INTO OLYMPUS_ANALYTICS.GOLD.FACT_LEARNING_PERFORMANCE VALUES
        ('ENR001', 'USER001', 'COURSE001', 'Data Analytics Fundamentals', 'Analytics', '2024-01-15', '2024-02-15', 100.00, 480, 92.5, TRUE, '2024-02-15', 'IT', 'Senior', 'New York'),
        ('ENR002', 'USER002', 'COURSE002', 'Leadership Excellence', 'Leadership', '2024-01-20', '2024-02-20', 85.00, 360, 88.0, TRUE, '2024-02-18', 'Sales', 'Manager', 'London'),
        ('ENR003', 'USER003', 'COURSE003', 'Project Management Basics', 'Management', '2024-02-01', NULL, 65.00, 240, 75.5, FALSE, '2024-03-10', 'Operations', 'Associate', 'Tokyo'),
        ('ENR004', 'USER004', 'COURSE001', 'Data Analytics Fundamentals', 'Analytics', '2024-02-10', '2024-03-10', 100.00, 450, 95.0, TRUE, '2024-03-10', 'Marketing', 'Senior', 'Sydney'),
        ('ENR005', 'USER005', 'COURSE004', 'Customer Service Excellence', 'Customer Service', '2024-02-15', '2024-03-01', 90.00, 300, 87.5, TRUE, '2024-03-01', 'Support', 'Associate', 'Toronto')
        """,
        
        """
        INSERT INTO OLYMPUS_ANALYTICS.GOLD.DIM_COURSES VALUES
        ('COURSE001', 'Data Analytics Fundamentals', 'Analytics', 'Learn the basics of data analysis and visualization', 480, 'Intermediate', 'Dr. Jane Smith', '2024-01-01 00:00:00', '2024-01-01 00:00:00', TRUE),
        ('COURSE002', 'Leadership Excellence', 'Leadership', 'Develop essential leadership skills for modern managers', 360, 'Advanced', 'Prof. John Davis', '2024-01-01 00:00:00', '2024-01-01 00:00:00', TRUE),
        ('COURSE003', 'Project Management Basics', 'Management', 'Introduction to project management methodologies', 300, 'Beginner', 'Sarah Wilson', '2024-01-01 00:00:00', '2024-01-01 00:00:00', TRUE),
        ('COURSE004', 'Customer Service Excellence', 'Customer Service', 'Master customer service best practices', 240, 'Intermediate', 'Mike Johnson', '2024-01-01 00:00:00', '2024-01-01 00:00:00', TRUE),
        ('COURSE005', 'Digital Marketing Strategy', 'Marketing', 'Comprehensive digital marketing course', 420, 'Advanced', 'Lisa Chen', '2024-01-01 00:00:00', '2024-01-01 00:00:00', TRUE)
        """
    ]
    
    success_count = 0
    error_count = 0
    
    # Create tables
    logger.info("Creating GOLD layer tables...")
    for i, sql in enumerate(gold_tables_sql, 1):
        try:
            with connector.get_cursor() as cursor:
                cursor.execute(sql)
            logger.info(f"✓ Created table {i}/{len(gold_tables_sql)}")
            success_count += 1
        except Exception as e:
            logger.error(f"✗ Error creating table {i}: {str(e)}")
            error_count += 1
    
    # Insert sample data
    logger.info("Inserting sample data...")
    for i, sql in enumerate(sample_data_sql, 1):
        try:
            with connector.get_cursor() as cursor:
                cursor.execute(sql)
            logger.info(f"✓ Inserted sample data {i}/{len(sample_data_sql)}")
            success_count += 1
        except Exception as e:
            logger.error(f"✗ Error inserting data {i}: {str(e)}")
            error_count += 1
    
    return success_count, error_count

def main():
    """Main execution function"""
    logger.info("Creating GOLD layer tables for Olympus Analytics...")
    
    try:
        connector = get_snowflake_connector()
        if not connector.connect():
            logger.error("Failed to connect to Snowflake")
            return False
        
        logger.info("✓ Connected to Snowflake successfully")
        
        # Create GOLD tables and insert data
        success_count, error_count = create_gold_tables(connector)
        
        # Summary
        logger.info(f"\n=== EXECUTION SUMMARY ===")
        logger.info(f"✓ Successful operations: {success_count}")
        logger.info(f"✗ Failed operations: {error_count}")
        
        if error_count == 0:
            logger.info("🎉 GOLD layer setup completed successfully!")
            return True
        else:
            logger.warning(f"⚠️  GOLD layer setup completed with {error_count} errors")
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