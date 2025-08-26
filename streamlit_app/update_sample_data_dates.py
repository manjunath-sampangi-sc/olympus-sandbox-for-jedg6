#!/usr/bin/env python3
"""
Script to update sample data with recent dates so dashboard queries show data.
The dashboard queries filter for recent data (6 months for training, 3 months for engagement).
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.snowflake_connector import SnowflakeConnector
import logging
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def update_sample_data_dates():
    """Update sample data with recent dates so dashboard queries return results."""
    
    connector = SnowflakeConnector()
    
    try:
        # Use SYSADMIN role for table updates
        connector.execute_query("USE ROLE SYSADMIN")
        connector.execute_query("USE WAREHOUSE XS_WAREHOUSE")
        connector.execute_query("USE DATABASE OLYMPUS_ANALYTICS")
        connector.execute_query("USE SCHEMA GOLD")
        
        # Calculate recent dates
        today = datetime.now().date()
        six_months_ago = today - timedelta(days=180)
        three_months_ago = today - timedelta(days=90)
        one_month_ago = today - timedelta(days=30)
        two_weeks_ago = today - timedelta(days=14)
        one_week_ago = today - timedelta(days=7)
        
        logger.info("Updating FACT_LEARNING_ANALYTICS with recent enrollment dates...")
        
        # Update FACT_LEARNING_ANALYTICS with recent enrollment dates
        update_learning_analytics_sql = f"""
        UPDATE OLYMPUS_ANALYTICS.GOLD.FACT_LEARNING_ANALYTICS 
        SET 
            ENROLLMENT_DATE = CASE 
                WHEN LEARNING_ID = 'L001' THEN '{one_month_ago}'
                WHEN LEARNING_ID = 'L002' THEN '{three_months_ago}'
                WHEN LEARNING_ID = 'L003' THEN '{two_weeks_ago}'
                WHEN LEARNING_ID = 'L004' THEN '{one_week_ago}'
                WHEN LEARNING_ID = 'L005' THEN '{six_months_ago}'
                WHEN LEARNING_ID = 'L006' THEN '{one_month_ago}'
                WHEN LEARNING_ID = 'L007' THEN '{two_weeks_ago}'
                WHEN LEARNING_ID = 'L008' THEN '{three_months_ago}'
                WHEN LEARNING_ID = 'L009' THEN '{one_week_ago}'
                WHEN LEARNING_ID = 'L010' THEN '{one_month_ago}'
                ELSE ENROLLMENT_DATE
            END,
            LEARNING_DATE = CASE 
                WHEN LEARNING_ID = 'L001' THEN '{one_month_ago}'
                WHEN LEARNING_ID = 'L002' THEN '{three_months_ago}'
                WHEN LEARNING_ID = 'L003' THEN '{two_weeks_ago}'
                WHEN LEARNING_ID = 'L004' THEN '{one_week_ago}'
                WHEN LEARNING_ID = 'L005' THEN '{six_months_ago}'
                WHEN LEARNING_ID = 'L006' THEN '{one_month_ago}'
                WHEN LEARNING_ID = 'L007' THEN '{two_weeks_ago}'
                WHEN LEARNING_ID = 'L008' THEN '{three_months_ago}'
                WHEN LEARNING_ID = 'L009' THEN '{one_week_ago}'
                WHEN LEARNING_ID = 'L010' THEN '{one_month_ago}'
                ELSE LEARNING_DATE
            END,
            LAST_ACCESSED_DATE = CASE 
                WHEN LEARNING_ID = 'L001' THEN '{today}'
                WHEN LEARNING_ID = 'L002' THEN '{one_week_ago}'
                WHEN LEARNING_ID = 'L003' THEN '{today}'
                WHEN LEARNING_ID = 'L004' THEN '{today}'
                WHEN LEARNING_ID = 'L005' THEN '{two_weeks_ago}'
                WHEN LEARNING_ID = 'L006' THEN '{one_week_ago}'
                WHEN LEARNING_ID = 'L007' THEN '{today}'
                WHEN LEARNING_ID = 'L008' THEN '{today}'
                WHEN LEARNING_ID = 'L009' THEN '{one_week_ago}'
                WHEN LEARNING_ID = 'L010' THEN '{today}'
                ELSE LAST_ACCESSED_DATE
            END
        """
        
        connector.execute_query(update_learning_analytics_sql)
        logger.info("FACT_LEARNING_ANALYTICS updated successfully")
        
        logger.info("Updating DIM_USERS with recent last_login_date...")
        
        # Update DIM_USERS with recent last_login_date
        update_users_sql = f"""
        UPDATE OLYMPUS_ANALYTICS.GOLD.DIM_USERS 
        SET 
            LAST_LOGIN_DATE = CASE 
                WHEN USER_ID = 'U001' THEN '{today}'
                WHEN USER_ID = 'U002' THEN '{one_week_ago}'
                WHEN USER_ID = 'U003' THEN '{today}'
                WHEN USER_ID = 'U004' THEN '{two_weeks_ago}'
                WHEN USER_ID = 'U005' THEN '{today}'
                WHEN USER_ID = 'U006' THEN '{one_week_ago}'
                WHEN USER_ID = 'U007' THEN '{today}'
                WHEN USER_ID = 'U008' THEN '{three_months_ago}'
                WHEN USER_ID = 'U009' THEN '{one_week_ago}'
                WHEN USER_ID = 'U010' THEN '{today}'
                ELSE LAST_LOGIN_DATE
            END
        """
        
        connector.execute_query(update_users_sql)
        logger.info("DIM_USERS updated successfully")
        
        # Skip sales table update for now - focus on learning analytics and user engagement
        
        # Verify the updates
        logger.info("Verifying updates...")
        
        # Check FACT_LEARNING_ANALYTICS
        learning_check = connector.execute_query(
            "SELECT COUNT(*) as count FROM OLYMPUS_ANALYTICS.GOLD.FACT_LEARNING_ANALYTICS WHERE ENROLLMENT_DATE >= DATEADD(month, -6, CURRENT_DATE())"
        )
        logger.info(f"FACT_LEARNING_ANALYTICS records with recent enrollment dates: {learning_check.iloc[0]['COUNT']}")
        
        # Check DIM_USERS
        users_check = connector.execute_query(
            "SELECT COUNT(*) as count FROM OLYMPUS_ANALYTICS.GOLD.DIM_USERS WHERE LAST_LOGIN_DATE >= DATEADD(month, -3, CURRENT_DATE())"
        )
        logger.info(f"DIM_USERS records with recent login dates: {users_check.iloc[0]['COUNT']}")
        
        # Sales data already has recent dates, skipping verification
        
        logger.info("✅ Sample data dates updated successfully!")
        logger.info("Dashboard queries should now return data.")
        
    except Exception as e:
        logger.error(f"❌ Error updating sample data dates: {str(e)}")
        raise
    finally:
        connector.close()

if __name__ == "__main__":
    update_sample_data_dates()