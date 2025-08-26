#!/usr/bin/env python3
"""
Check and create database schemas
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.snowflake_connector import SnowflakeConnector
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    try:
        conn = SnowflakeConnector()
        
        # Check existing schemas
        logger.info("Checking existing schemas...")
        result = conn.execute_query('SHOW SCHEMAS IN DATABASE OLYMPUS_ANALYTICS')
        print("Existing schemas:")
        for row in result:
            print(f"  - {row[1]}")
        
        # Try to create Bronze schema
        logger.info("Creating Bronze schema...")
        conn.execute_query('CREATE SCHEMA IF NOT EXISTS OLYMPUS_ANALYTICS.BRONZE')
        logger.info("Bronze schema created successfully")
        
        # Try to create Silver schema
        logger.info("Creating Silver schema...")
        conn.execute_query('CREATE SCHEMA IF NOT EXISTS OLYMPUS_ANALYTICS.SILVER')
        logger.info("Silver schema created successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)