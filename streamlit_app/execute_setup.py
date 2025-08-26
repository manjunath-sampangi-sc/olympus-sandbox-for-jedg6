#!/usr/bin/env python3
"""
Script to execute the Olympus Analytics database setup
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.snowflake_connector import get_snowflake_connector
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def read_sql_file(file_path):
    """Read and return SQL file content"""
    with open(file_path, 'r') as file:
        return file.read()

def execute_sql_statements(connector, sql_content):
    """Execute SQL statements from the setup file"""
    # Split SQL content by semicolons and filter out empty statements
    statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
    
    success_count = 0
    error_count = 0
    
    for i, statement in enumerate(statements, 1):
        if not statement or statement.startswith('--'):
            continue
            
        try:
            logger.info(f"Executing statement {i}/{len(statements)}...")
            # For DDL statements, we don't expect return data
            if any(keyword in statement.upper() for keyword in ['CREATE', 'DROP', 'ALTER', 'USE']):
                with connector.get_cursor() as cursor:
                    cursor.execute(statement)
                logger.info(f"✓ Statement {i} executed successfully")
            else:
                # For DML statements like INSERT
                result = connector.execute_query(statement)
                logger.info(f"✓ Statement {i} executed successfully - {len(result) if result is not None else 0} rows affected")
            
            success_count += 1
            
        except Exception as e:
            logger.error(f"✗ Error executing statement {i}: {str(e)}")
            logger.error(f"Statement: {statement[:100]}...")
            error_count += 1
            # Continue with next statement instead of stopping
            continue
    
    return success_count, error_count

def main():
    """Main execution function"""
    logger.info("Starting Olympus Analytics database setup...")
    
    # Initialize Snowflake connector
    try:
        connector = get_snowflake_connector()
        if not connector.connect():
            logger.error("Failed to connect to Snowflake")
            return False
        
        logger.info("✓ Connected to Snowflake successfully")
        
        # Read SQL setup file
        sql_file_path = 'setup_olympus_database.sql'
        if not os.path.exists(sql_file_path):
            logger.error(f"SQL file not found: {sql_file_path}")
            return False
        
        logger.info(f"Reading SQL file: {sql_file_path}")
        sql_content = read_sql_file(sql_file_path)
        
        # Execute SQL statements
        logger.info("Executing SQL statements...")
        success_count, error_count = execute_sql_statements(connector, sql_content)
        
        # Summary
        logger.info(f"\n=== EXECUTION SUMMARY ===")
        logger.info(f"✓ Successful statements: {success_count}")
        logger.info(f"✗ Failed statements: {error_count}")
        
        if error_count == 0:
            logger.info("🎉 Database setup completed successfully!")
            return True
        else:
            logger.warning(f"⚠️  Database setup completed with {error_count} errors")
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