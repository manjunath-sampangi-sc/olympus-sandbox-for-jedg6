#!/usr/bin/env python3
"""
Create Gold billing table with mock data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.snowflake_connector import SnowflakeConnector
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_billing_table():
    try:
        conn = SnowflakeConnector()
        
        # Check existing tables
        logger.info("Checking existing tables in GOLD schema...")
        result = conn.execute_query('SHOW TABLES IN SCHEMA OLYMPUS_ANALYTICS.GOLD')
        existing_tables = [row[1] for row in result]
        logger.info(f"Found {len(existing_tables)} existing tables")
        
        # Create the billing table
        logger.info("Creating GD_MEMBER_BILLING_BRACKETS_MONTHLY table...")
        
        create_table_sql = """
        CREATE OR REPLACE TABLE OLYMPUS_ANALYTICS.GOLD.GD_MEMBER_BILLING_BRACKETS_MONTHLY (
            MEMBER_ID VARCHAR(50),
            EMAIL VARCHAR(255),
            MEMBER_NAME VARCHAR(255),
            COMMUNITY_ID VARCHAR(50),
            GROUP_NAME VARCHAR(255),
            BILLING_MONTH DATE,
            COURSE_COUNT_ACTIVE INTEGER,
            HAS_HOME_COURSE BOOLEAN,
            BILLING_BRACKET VARCHAR(10),
            MONTHLY_AMOUNT DECIMAL(10,2),
            ENROLLED_COURSES VARCHAR(1000),
            BILLING_CATEGORY_DESCRIPTION VARCHAR(500),
            BILLING_RECORD_KEY VARCHAR(255),
            CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
        )
        """
        
        conn.execute_query(create_table_sql)
        logger.info("Table created successfully")
        
        # Insert mock data for current month and previous months
        logger.info("Inserting mock billing data...")
        
        # Generate data for last 6 months
        current_date = datetime.now().replace(day=1)  # First day of current month
        
        for month_offset in range(6):
            billing_month = current_date - timedelta(days=month_offset * 30)
            billing_month_str = billing_month.strftime('%Y-%m-01')
            
            # Mock data for different billing scenarios
            mock_data = [
                # $0 bracket - no enrollments
                ("M001", "alice.johnson@email.com", "Alice Johnson", "C001", "Leadership Academy", billing_month_str, 0, False, "$0", 0.00, "", "No active enrollments", f"M001_C001_{billing_month.strftime('%Y-%m')}"),
                ("M002", "bob.smith@email.com", "Bob Smith", "C002", "Tech Innovation Hub", billing_month_str, 0, False, "$0", 0.00, "", "No active enrollments", f"M002_C002_{billing_month.strftime('%Y-%m')}"),
                ("M003", "carol.davis@email.com", "Carol Davis", "C003", "Marketing Experts", billing_month_str, 0, False, "$0", 0.00, "", "No active enrollments", f"M003_C003_{billing_month.strftime('%Y-%m')}"),
                
                # $10 bracket - Home course only
                ("M004", "david.wilson@email.com", "David Wilson", "C001", "Leadership Academy", billing_month_str, 1, True, "$10", 10.00, "Home Course", "Home course only", f"M004_C001_{billing_month.strftime('%Y-%m')}"),
                ("M005", "eva.brown@email.com", "Eva Brown", "C002", "Tech Innovation Hub", billing_month_str, 1, True, "$10", 10.00, "Home Course", "Home course only", f"M005_C002_{billing_month.strftime('%Y-%m')}"),
                ("M006", "frank.miller@email.com", "Frank Miller", "C003", "Marketing Experts", billing_month_str, 1, True, "$10", 10.00, "Home Course", "Home course only", f"M006_C003_{billing_month.strftime('%Y-%m')}"),
                ("M007", "grace.taylor@email.com", "Grace Taylor", "C001", "Leadership Academy", billing_month_str, 1, True, "$10", 10.00, "Home Course", "Home course only", f"M007_C001_{billing_month.strftime('%Y-%m')}"),
                ("M008", "henry.anderson@email.com", "Henry Anderson", "C002", "Tech Innovation Hub", billing_month_str, 1, True, "$10", 10.00, "Home Course", "Home course only", f"M008_C002_{billing_month.strftime('%Y-%m')}"),
                
                # $50 bracket - 2+ courses or Home + others
                ("M009", "iris.thomas@email.com", "Iris Thomas", "C001", "Leadership Academy", billing_month_str, 3, True, "$50", 50.00, "Home Course, Advanced Leadership, Team Management", "Multiple courses including Home", f"M009_C001_{billing_month.strftime('%Y-%m')}"),
                ("M010", "jack.jackson@email.com", "Jack Jackson", "C002", "Tech Innovation Hub", billing_month_str, 2, False, "$50", 50.00, "Python Programming, Data Science", "Two or more courses", f"M010_C002_{billing_month.strftime('%Y-%m')}"),
                ("M011", "karen.white@email.com", "Karen White", "C003", "Marketing Experts", billing_month_str, 4, True, "$50", 50.00, "Home Course, Sales Fundamentals, Customer Relations, Negotiation Skills", "Multiple courses including Home", f"M011_C003_{billing_month.strftime('%Y-%m')}"),
                ("M012", "liam.harris@email.com", "Liam Harris", "C001", "Leadership Academy", billing_month_str, 2, True, "$50", 50.00, "Home Course, Strategic Planning", "Home plus additional course", f"M012_C001_{billing_month.strftime('%Y-%m')}"),
                ("M013", "mia.clark@email.com", "Mia Clark", "C002", "Tech Innovation Hub", billing_month_str, 5, False, "$50", 50.00, "Machine Learning, AI Ethics, Cloud Computing, DevOps, Cybersecurity", "Five courses without Home", f"M013_C002_{billing_month.strftime('%Y-%m')}"),
                ("M014", "noah.lewis@email.com", "Noah Lewis", "C003", "Marketing Experts", billing_month_str, 2, False, "$50", 50.00, "Executive Coaching, Change Management", "Two courses without Home", f"M014_C003_{billing_month.strftime('%Y-%m')}"),
                ("M015", "olivia.walker@email.com", "Olivia Walker", "C001", "Leadership Academy", billing_month_str, 3, True, "$50", 50.00, "Home Course, Leadership Skills, Project Management", "Multiple courses including Home", f"M015_C001_{billing_month.strftime('%Y-%m')}"),
            ]
            
            # Insert data for this month
            for data_row in mock_data:
                insert_sql = """
                INSERT INTO OLYMPUS_ANALYTICS.GOLD.GD_MEMBER_BILLING_BRACKETS_MONTHLY 
                (MEMBER_ID, EMAIL, MEMBER_NAME, COMMUNITY_ID, GROUP_NAME, 
                 BILLING_MONTH, COURSE_COUNT_ACTIVE, HAS_HOME_COURSE, BILLING_BRACKET, 
                 MONTHLY_AMOUNT, ENROLLED_COURSES, BILLING_CATEGORY_DESCRIPTION, BILLING_RECORD_KEY)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                conn.execute_query(insert_sql, data_row)
        
        logger.info("Mock billing data inserted successfully")
        
        # Verify data
        result = conn.execute_query("""
            SELECT BILLING_MONTH, BILLING_BRACKET, COUNT(*) as MEMBER_COUNT, SUM(MONTHLY_AMOUNT) as TOTAL_REVENUE
            FROM OLYMPUS_ANALYTICS.GOLD.GD_MEMBER_BILLING_BRACKETS_MONTHLY 
            GROUP BY BILLING_MONTH, BILLING_BRACKET 
            ORDER BY BILLING_MONTH DESC, BILLING_BRACKET
        """)
        
        logger.info("Billing data summary:")
        for row in result:
            logger.info(f"  {row[0]} - {row[1]}: {row[2]} members, ${row[3]} revenue")
        
        return True
        
    except Exception as e:
        logger.error(f"Error creating billing table: {e}")
        return False

if __name__ == "__main__":
    success = create_billing_table()
    sys.exit(0 if success else 1)