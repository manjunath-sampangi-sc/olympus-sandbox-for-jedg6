#!/usr/bin/env python3

from utils.snowflake_connector import SnowflakeConnector

def check_table_columns():
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
        
        for row in result:
            print(f"  {row[0]} ({row[1]})")
        
        print("\nFACT_LEARNING_ANALYTICS columns:")
        result2 = conn.execute_query("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'FACT_LEARNING_ANALYTICS' 
            AND table_schema = 'GOLD'
            ORDER BY ordinal_position
        """)
        
        for row in result2:
            print(f"  {row[0]} ({row[1]})")
            
        # Test a simple query to see what works
        print("\nTesting simple queries:")
        try:
            result3 = conn.execute_query("SELECT COUNT(*) FROM FACT_SALES_PERFORMANCE")
            print(f"FACT_SALES_PERFORMANCE has {result3[0][0]} rows")
        except Exception as e:
            print(f"Error querying FACT_SALES_PERFORMANCE: {e}")
            
        try:
            result4 = conn.execute_query("SELECT COUNT(*) FROM FACT_LEARNING_ANALYTICS")
            print(f"FACT_LEARNING_ANALYTICS has {result4[0][0]} rows")
        except Exception as e:
            print(f"Error querying FACT_LEARNING_ANALYTICS: {e}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_table_columns()