#!/usr/bin/env python3

import snowflake.connector
import pandas as pd
import os

def check_table_structures():
    """Check the actual structure of raw tables in Snowflake"""
    
    # Connection parameters
    conn_params = {
        'account': 'KDLCEKW-GPB78424',
        'user': 'MANJANUTH',
    'password': os.getenv('SNOWFLAKE_PASSWORD'),
        'warehouse': 'XS_WAREHOUSE',
        'database': 'OLYMPUS_ANALYTICS',
        'schema': 'BRONZE',
        'role': 'OLYMPUS_CONTRACTOR'
    }
    
    try:
        conn = snowflake.connector.connect(**conn_params)
        cursor = conn.cursor()
    except Exception as e:
        print(f"Failed to connect to Snowflake: {e}")
        return
    
    # First, let's see what tables actually exist
    print("=== CHECKING EXISTING TABLES ===")
    try:
        cursor.execute("SHOW TABLES IN OLYMPUS_ANALYTICS.BRONZE")
        tables = cursor.fetchall()
        print("Existing tables in BRONZE schema:")
        for table in tables:
            print(f"  - {table[1]}")
    except Exception as e:
        print(f"Error listing tables: {e}")
    
    # Check specific table structures
    tables_to_check = ['HUBSPOT_DEALS', 'DISCO_COURSES']
    
    for table_name in tables_to_check:
        print(f"\n=== CHECKING {table_name} COLUMNS ===")
        try:
            cursor.execute(f"DESCRIBE TABLE OLYMPUS_ANALYTICS.BRONZE.{table_name}")
            columns = cursor.fetchall()
            print(f"Columns in {table_name}:")
            for col in columns:
                print(f"  - {col[0]} ({col[1]})")
        except Exception as e:
            print(f"Error describing {table_name}: {e}")
    
    # Check other schemas too
    for schema in ['GOLD', 'SILVER', 'STAGING']:
        print(f"\n=== CHECKING {schema} SCHEMA ===")
        try:
            cursor.execute(f"SHOW TABLES IN OLYMPUS_ANALYTICS.{schema}")
            tables = cursor.fetchall()
            print(f"Existing tables in {schema} schema:")
            for table in tables:
                print(f"  - {table[1]}")
        except Exception as e:
            print(f"Error listing tables in {schema}: {e}")
    
    # Check what tables actually exist in Bronze
    existing_tables = []
    
    for schema, table in existing_tables:
        print(f"\n=== {schema}.{table} ===")
        try:
            # Get table structure
            query = f"DESCRIBE TABLE OLYMPUS_ANALYTICS.{schema}.{table}"
            cursor.execute(query)
            result = cursor.fetchall()
            print("Columns:")
            for row in result:
                print(f"  - {row[0]} ({row[1]})")
                
            # Get sample data
            sample_query = f"SELECT * FROM OLYMPUS_ANALYTICS.{schema}.{table} LIMIT 2"
            cursor.execute(sample_query)
            sample_data = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            print(f"\nSample data ({len(sample_data)} rows):")
            print(f"Columns: {', '.join(columns)}")
            for i, row in enumerate(sample_data):
                print(f"Row {i+1}: {dict(zip(columns, row))}")
            
        except Exception as e:
            print(f"Error checking {schema}.{table}: {str(e)}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    check_table_structures()