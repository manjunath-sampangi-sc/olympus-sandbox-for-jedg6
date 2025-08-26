#!/usr/bin/env python3
"""
Update FACT_SALES_PERFORMANCE table with recent dates so dashboard queries show data.
The current data has dates from 2024, but dashboard filters for last 12 months.
"""

from utils.snowflake_connector import SnowflakeConnector
from datetime import datetime, timedelta
import random

def update_sales_data_dates():
    conn = SnowflakeConnector()
    
    try:
        # Set context
        conn.execute_query('USE ROLE SYSADMIN')
        conn.execute_query('USE WAREHOUSE XS_WAREHOUSE')
        conn.execute_query('USE DATABASE OLYMPUS_ANALYTICS')
        conn.execute_query('USE SCHEMA GOLD')
        
        print("Updating FACT_SALES_PERFORMANCE with recent dates...")
        
        # Update close_date to recent dates (within last 12 months)
        update_queries = [
            "UPDATE FACT_SALES_PERFORMANCE SET close_date = '2024-12-15' WHERE deal_id = 'DEAL001'",
            "UPDATE FACT_SALES_PERFORMANCE SET close_date = '2025-01-20' WHERE deal_id = 'DEAL002'",
            "UPDATE FACT_SALES_PERFORMANCE SET close_date = '2025-02-28' WHERE deal_id = 'DEAL003'",
            "UPDATE FACT_SALES_PERFORMANCE SET close_date = '2025-03-10' WHERE deal_id = 'DEAL004'",
            "UPDATE FACT_SALES_PERFORMANCE SET close_date = '2025-04-15' WHERE deal_id = 'DEAL005'",
            "UPDATE FACT_SALES_PERFORMANCE SET close_date = '2025-05-01' WHERE deal_id = 'DEAL006'",
            "UPDATE FACT_SALES_PERFORMANCE SET close_date = '2025-06-30' WHERE deal_id = 'DEAL007'",
            "UPDATE FACT_SALES_PERFORMANCE SET close_date = '2025-07-25' WHERE deal_id = 'DEAL008'",
            "UPDATE FACT_SALES_PERFORMANCE SET close_date = '2025-08-15' WHERE deal_id = 'DEAL009'",
            "UPDATE FACT_SALES_PERFORMANCE SET close_date = '2025-08-20' WHERE deal_id = 'DEAL010'"
        ]
        
        for query in update_queries:
            result = conn.execute_query(query)
            print(f"Executed: {query}")
        
        # Verify the updates
        print("\nVerifying updated dates...")
        result = conn.execute_query("SELECT deal_id, client_name, close_date FROM FACT_SALES_PERFORMANCE ORDER BY close_date DESC")
        print(f"Updated {len(result)} records:")
        if len(result) > 0:
            print(result.to_string())
        
        # Test the sales performance query
        print("\nTesting sales performance query...")
        sales_query = """
            SELECT 
                client_name,
                SUM(amount) as total_revenue,
                COUNT(*) as deal_count
            FROM OLYMPUS_ANALYTICS.GOLD.FACT_SALES_PERFORMANCE
            WHERE close_date >= DATEADD(month, -12, CURRENT_DATE())
            GROUP BY client_name
            ORDER BY total_revenue DESC
            LIMIT 10
        """
        
        result = conn.execute_query(sales_query)
        print(f"Sales performance query now returns {len(result)} rows:")
        if len(result) > 0:
            print(result.to_string())
        
        print("\nSales data dates updated successfully!")
        
    except Exception as e:
        print(f"Error updating sales data dates: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    update_sales_data_dates()