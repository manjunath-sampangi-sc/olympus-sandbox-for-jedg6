#!/usr/bin/env python3
"""
Fix course ID mismatch between FACT_LEARNING_ANALYTICS and DIM_COURSES tables.
The fact table uses 'C001', 'C002', etc. while the dimension table uses 'COURSE001', 'COURSE002', etc.
"""

from utils.snowflake_connector import SnowflakeConnector

def fix_course_id_mismatch():
    conn = SnowflakeConnector()
    
    try:
        # Set context
        conn.execute_query('USE ROLE SYSADMIN')
        conn.execute_query('USE WAREHOUSE XS_WAREHOUSE')
        conn.execute_query('USE DATABASE OLYMPUS_ANALYTICS')
        conn.execute_query('USE SCHEMA GOLD')
        
        print("Updating FACT_LEARNING_ANALYTICS course_id values to match DIM_COURSES...")
        
        # Update course IDs in FACT_LEARNING_ANALYTICS to match DIM_COURSES format
        update_queries = [
            "UPDATE FACT_LEARNING_ANALYTICS SET course_id = 'COURSE001' WHERE course_id = 'C001'",
            "UPDATE FACT_LEARNING_ANALYTICS SET course_id = 'COURSE002' WHERE course_id = 'C002'",
            "UPDATE FACT_LEARNING_ANALYTICS SET course_id = 'COURSE003' WHERE course_id = 'C003'",
            "UPDATE FACT_LEARNING_ANALYTICS SET course_id = 'COURSE004' WHERE course_id = 'C004'",
            "UPDATE FACT_LEARNING_ANALYTICS SET course_id = 'COURSE005' WHERE course_id = 'C005'"
        ]
        
        for query in update_queries:
            result = conn.execute_query(query)
            print(f"Executed: {query}")
        
        # Verify the fix
        print("\nVerifying the fix...")
        result = conn.execute_query("""
            SELECT 
                f.course_id as fact_course_id, 
                c.course_id as dim_course_id, 
                c.course_name 
            FROM FACT_LEARNING_ANALYTICS f 
            JOIN DIM_COURSES c ON f.course_id = c.course_id 
            LIMIT 5
        """)
        
        print(f"Join now returns {len(result)} rows:")
        if len(result) > 0:
            print(result.to_string())
        
        # Test the training performance query
        print("\nTesting training performance query...")
        training_query = """
            SELECT 
                c.course_name,
                AVG(f.progress_percentage) as avg_progress,
                COUNT(*) as enrollments
            FROM OLYMPUS_ANALYTICS.GOLD.FACT_LEARNING_ANALYTICS f
            JOIN OLYMPUS_ANALYTICS.GOLD.DIM_COURSES c ON f.course_id = c.course_id
            WHERE f.enrollment_date >= DATEADD(month, -6, CURRENT_DATE())
            GROUP BY c.course_name
            ORDER BY avg_progress DESC
            LIMIT 10
        """
        
        result = conn.execute_query(training_query)
        print(f"Training performance query now returns {len(result)} rows:")
        if len(result) > 0:
            print(result.to_string())
        
        print("\nCourse ID mismatch fixed successfully!")
        
    except Exception as e:
        print(f"Error fixing course ID mismatch: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    fix_course_id_mismatch()