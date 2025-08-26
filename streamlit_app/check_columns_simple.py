#!/usr/bin/env python3

from utils.snowflake_connector import SnowflakeConnector

def check_columns():
    conn = SnowflakeConnector()
    
    try:
        # Set context
        conn.execute_query('USE ROLE SYSADMIN')
        conn.execute_query('USE WAREHOUSE XS_WAREHOUSE')
        conn.execute_query('USE DATABASE OLYMPUS_ANALYTICS')
        conn.execute_query('USE SCHEMA GOLD')
        
        # Check FACT_SALES_PERFORMANCE columns
        print("FACT_SALES_PERFORMANCE columns:")
        result = conn.execute_query("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'FACT_SALES_PERFORMANCE' 
            AND table_schema = 'GOLD'
            ORDER BY ordinal_position
        """)
        
        for _, row in result.iterrows():
            print(f"  {row['COLUMN_NAME']} ({row['DATA_TYPE']})")
            
        # Test a simple query to see what columns actually exist
        print("\nTesting column access:")
        try:
            test_result = conn.execute_query("SELECT * FROM FACT_SALES_PERFORMANCE LIMIT 1")
            print(f"Available columns: {list(test_result.columns)}")
        except Exception as e:
            print(f"Error accessing table: {e}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_columns()