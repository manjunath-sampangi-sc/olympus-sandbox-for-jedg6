#!/usr/bin/env python3

from utils.snowflake_connector import SnowflakeConnector

def check_dim_users():
    conn = SnowflakeConnector()
    
    try:
        # Set context
        conn.execute_query('USE ROLE SYSADMIN')
        conn.execute_query('USE WAREHOUSE XS_WAREHOUSE')
        conn.execute_query('USE DATABASE OLYMPUS_ANALYTICS')
        conn.execute_query('USE SCHEMA GOLD')
        
        # Check if DIM_USERS exists
        try:
            result = conn.execute_query('SELECT * FROM DIM_USERS LIMIT 1')
            print('DIM_USERS columns:', list(result.columns))
        except Exception as e:
            print('DIM_USERS error:', e)
            
        # Check what tables exist in GOLD schema
        tables_result = conn.execute_query("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'GOLD'
            ORDER BY table_name
        """)
        
        print('\nAvailable tables in GOLD schema:')
        for _, row in tables_result.iterrows():
            print(f"  - {row['TABLE_NAME']}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_dim_users()