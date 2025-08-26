#!/usr/bin/env python3
"""
Test script to verify that sales rep queries work correctly with the proper column names.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.snowflake_connector import SnowflakeConnector
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_sales_rep_queries():
    """Test various sales rep queries to ensure they work correctly."""
    
    connector = SnowflakeConnector()
    
    try:
        # Set context
        connector.execute_query("USE ROLE SYSADMIN")
        connector.execute_query("USE WAREHOUSE XS_WAREHOUSE")
        connector.execute_query("USE DATABASE OLYMPUS_ANALYTICS")
        connector.execute_query("USE SCHEMA GOLD")
        
        # Test 1: Basic sales rep query
        logger.info("Testing basic sales rep query...")
        query1 = """
        SELECT 
            SALES_REP as sales_rep,
            SUM(CASE WHEN STAGE = 'Closed Won' THEN AMOUNT ELSE 0 END) as total_revenue,
            COUNT(CASE WHEN STAGE = 'Closed Won' THEN 1 END) as deals_won,
            COUNT(*) as total_deals
        FROM OLYMPUS_ANALYTICS.GOLD.FACT_SALES_PERFORMANCE
        GROUP BY SALES_REP
        ORDER BY total_revenue DESC
        LIMIT 5
        """
        
        result1 = connector.execute_query(query1)
        logger.info(f"Basic sales rep query returned {len(result1)} rows")
        if len(result1) > 0:
            logger.info("Top sales rep results:")
            print(result1.to_string())
        
        # Test 2: Sales rep performance with time filter
        logger.info("\nTesting sales rep query with time filter...")
        query2 = """
        SELECT 
            SALES_REP as sales_rep,
            SUM(CASE WHEN STAGE = 'Closed Won' THEN AMOUNT ELSE 0 END) as total_revenue,
            COUNT(CASE WHEN STAGE = 'Closed Won' THEN 1 END) as deals_won,
            COUNT(*) as total_deals,
            ROUND(COUNT(CASE WHEN STAGE = 'Closed Won' THEN 1 END) * 100.0 / COUNT(*), 1) as win_rate
        FROM OLYMPUS_ANALYTICS.GOLD.FACT_SALES_PERFORMANCE
        WHERE created_at >= DATEADD(month, -12, CURRENT_DATE())
        GROUP BY SALES_REP
        ORDER BY total_revenue DESC
        LIMIT 10
        """
        
        result2 = connector.execute_query(query2)
        logger.info(f"Time-filtered sales rep query returned {len(result2)} rows")
        if len(result2) > 0:
            logger.info("Sales rep performance with time filter:")
            print(result2.to_string())
        
        # Test 3: Verify table schema
        logger.info("\nVerifying table schema...")
        schema_query = """
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'FACT_SALES_PERFORMANCE' 
        AND table_schema = 'GOLD'
        AND column_name LIKE '%REP%'
        ORDER BY ordinal_position
        """
        
        schema_result = connector.execute_query(schema_query)
        logger.info("Sales rep related columns:")
        if len(schema_result) > 0:
            print(schema_result.to_string())
        else:
            logger.warning("No sales rep columns found!")
        
        logger.info("\nAll sales rep queries completed successfully!")
        
    except Exception as e:
        logger.error(f"Error testing sales rep queries: {str(e)}")
        raise
    finally:
        connector.close()

if __name__ == "__main__":
    test_sales_rep_queries()
    print("Sales rep query testing completed!")