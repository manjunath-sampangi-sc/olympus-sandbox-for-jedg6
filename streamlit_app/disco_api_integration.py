#!/usr/bin/env python3
"""
Disco LMS API Integration for Olympus Analytics
This script fetches live data from Disco LMS API and loads it into Snowflake Bronze tables

API Documentation:
- Base URL: https://api.disco.co
- Endpoints: /v1/community.get, /v1/members.list, /v1/products.list, /v1/enrollments.list
- Authentication: API key via Authorization header
"""

import os
import sys
import requests
import pandas as pd
import json
from datetime import datetime, timezone
import logging
from typing import Dict, List, Any, Optional
import time

# Add utils to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils.snowflake_connector import get_snowflake_connector, execute_query

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DiscoAPIClient:
    """Client for interacting with Disco LMS API"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.disco.co"):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'Olympus-Analytics/1.0'
        })
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make authenticated request to Disco API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            logger.info(f"Making request to: {endpoint}")
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Successfully fetched data from {endpoint}")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed for {endpoint}: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response body: {e.response.text}")
            raise
    
    def get_communities(self) -> List[Dict]:
        """Fetch communities (groups) data"""
        try:
            data = self._make_request('/v1/community.get')
            # Handle different response structures
            if isinstance(data, dict):
                if 'communities' in data:
                    return data['communities']
                elif 'data' in data:
                    return data['data'] if isinstance(data['data'], list) else [data['data']]
                else:
                    return [data]  # Single community object
            elif isinstance(data, list):
                return data
            else:
                logger.warning(f"Unexpected communities response format: {type(data)}")
                return []
        except Exception as e:
            logger.error(f"Failed to fetch communities: {str(e)}")
            return []
    
    def get_members(self) -> List[Dict]:
        """Fetch members data"""
        try:
            data = self._make_request('/v1/members.list')
            # Handle different response structures
            if isinstance(data, dict):
                if 'members' in data:
                    return data['members']
                elif 'data' in data:
                    return data['data'] if isinstance(data['data'], list) else [data['data']]
                elif 'users' in data:
                    return data['users']
                else:
                    return [data]  # Single member object
            elif isinstance(data, list):
                return data
            else:
                logger.warning(f"Unexpected members response format: {type(data)}")
                return []
        except Exception as e:
            logger.error(f"Failed to fetch members: {str(e)}")
            return []
    
    def get_products(self) -> List[Dict]:
        """Fetch products/courses data"""
        try:
            data = self._make_request('/v1/products.list')
            # Handle different response structures
            if isinstance(data, dict):
                if 'products' in data:
                    return data['products']
                elif 'courses' in data:
                    return data['courses']
                elif 'data' in data:
                    return data['data'] if isinstance(data['data'], list) else [data['data']]
                else:
                    return [data]  # Single product object
            elif isinstance(data, list):
                return data
            else:
                logger.warning(f"Unexpected products response format: {type(data)}")
                return []
        except Exception as e:
            logger.error(f"Failed to fetch products: {str(e)}")
            return []
    
    def get_enrollments(self) -> List[Dict]:
        """Fetch enrollments data"""
        try:
            data = self._make_request('/v1/enrollments.list')
            # Handle different response structures
            if isinstance(data, dict):
                if 'enrollments' in data:
                    return data['enrollments']
                elif 'data' in data:
                    return data['data'] if isinstance(data['data'], list) else [data['data']]
                else:
                    return [data]  # Single enrollment object
            elif isinstance(data, list):
                return data
            else:
                logger.warning(f"Unexpected enrollments response format: {type(data)}")
                return []
        except Exception as e:
            logger.error(f"Failed to fetch enrollments: {str(e)}")
            return []

class DiscoBronzeLoader:
    """Loads Disco API data into Snowflake Bronze tables"""
    
    def __init__(self):
        self.conn = get_snowflake_connector()
    
    def create_bronze_tables(self):
        """Create Bronze tables for Disco data if they don't exist"""
        
        # Communities table
        communities_ddl = """
        CREATE TABLE IF NOT EXISTS OLYMPUS_ANALYTICS.BRONZE.DISCO_COMMUNITIES (
            COMMUNITY_ID VARCHAR(255) PRIMARY KEY,
            COMMUNITY_NAME VARCHAR(500),
            DESCRIPTION TEXT,
            CREATED_AT TIMESTAMP_NTZ,
            UPDATED_AT TIMESTAMP_NTZ,
            STATUS VARCHAR(100),
            MEMBER_COUNT INTEGER,
            SETTINGS VARIANT,
            _LOADED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            _SOURCE VARCHAR(50) DEFAULT 'disco_api'
        )
        """
        
        # Members table
        members_ddl = """
        CREATE TABLE IF NOT EXISTS OLYMPUS_ANALYTICS.BRONZE.DISCO_MEMBERS (
            MEMBER_ID VARCHAR(255) PRIMARY KEY,
            EMAIL VARCHAR(500),
            FIRST_NAME VARCHAR(255),
            LAST_NAME VARCHAR(255),
            USERNAME VARCHAR(255),
            COMMUNITY_ID VARCHAR(255),
            ROLE VARCHAR(100),
            STATUS VARCHAR(100),
            JOINED_AT TIMESTAMP_NTZ,
            LAST_ACTIVE_AT TIMESTAMP_NTZ,
            PROFILE_DATA VARIANT,
            _LOADED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            _SOURCE VARCHAR(50) DEFAULT 'disco_api'
        )
        """
        
        # Products/Courses table
        products_ddl = """
        CREATE TABLE IF NOT EXISTS OLYMPUS_ANALYTICS.BRONZE.DISCO_PRODUCTS (
            PRODUCT_ID VARCHAR(255) PRIMARY KEY,
            PRODUCT_NAME VARCHAR(500),
            PRODUCT_TYPE VARCHAR(100),
            DESCRIPTION TEXT,
            PRICE DECIMAL(10,2),
            CURRENCY VARCHAR(10),
            CREATED_AT TIMESTAMP_NTZ,
            UPDATED_AT TIMESTAMP_NTZ,
            STATUS VARCHAR(100),
            METADATA VARIANT,
            _LOADED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            _SOURCE VARCHAR(50) DEFAULT 'disco_api'
        )
        """
        
        # Enrollments table
        enrollments_ddl = """
        CREATE TABLE IF NOT EXISTS OLYMPUS_ANALYTICS.BRONZE.DISCO_ENROLLMENTS (
            ENROLLMENT_ID VARCHAR(255) PRIMARY KEY,
            MEMBER_ID VARCHAR(255),
            PRODUCT_ID VARCHAR(255),
            COMMUNITY_ID VARCHAR(255),
            ENROLLED_AT TIMESTAMP_NTZ,
            UNENROLLED_AT TIMESTAMP_NTZ,
            STATUS VARCHAR(100),
            PROGRESS_PERCENTAGE DECIMAL(5,2),
            COMPLETION_DATE TIMESTAMP_NTZ,
            ENROLLMENT_DATA VARIANT,
            _LOADED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            _SOURCE VARCHAR(50) DEFAULT 'disco_api'
        )
        """
        
        tables = [
            ("DISCO_COMMUNITIES", communities_ddl),
            ("DISCO_MEMBERS", members_ddl),
            ("DISCO_PRODUCTS", products_ddl),
            ("DISCO_ENROLLMENTS", enrollments_ddl)
        ]
        
        for table_name, ddl in tables:
            try:
                execute_query(ddl)
                logger.info(f"Created/verified Bronze table: {table_name}")
            except Exception as e:
                logger.error(f"Failed to create table {table_name}: {str(e)}")
                raise
    
    def load_communities(self, communities_data: List[Dict]):
        """Load communities data into Bronze table"""
        if not communities_data:
            logger.warning("No communities data to load")
            return
        
        # Transform data for Snowflake
        df_data = []
        for community in communities_data:
            row = {
                'COMMUNITY_ID': str(community.get('id', community.get('community_id', ''))),
                'COMMUNITY_NAME': community.get('name', community.get('title', '')),
                'DESCRIPTION': community.get('description', ''),
                'CREATED_AT': self._parse_timestamp(community.get('created_at')),
                'UPDATED_AT': self._parse_timestamp(community.get('updated_at')),
                'STATUS': community.get('status', 'active'),
                'MEMBER_COUNT': community.get('member_count', 0),
                'SETTINGS': json.dumps(community) if community else '{}'
            }
            df_data.append(row)
        
        df = pd.DataFrame(df_data)
        self._load_dataframe_to_table(df, 'DISCO_COMMUNITIES')
    
    def load_members(self, members_data: List[Dict]):
        """Load members data into Bronze table"""
        if not members_data:
            logger.warning("No members data to load")
            return
        
        # Transform data for Snowflake
        df_data = []
        for member in members_data:
            row = {
                'MEMBER_ID': str(member.get('id', member.get('user_id', member.get('member_id', '')))),
                'EMAIL': member.get('email', ''),
                'FIRST_NAME': member.get('first_name', member.get('firstName', '')),
                'LAST_NAME': member.get('last_name', member.get('lastName', '')),
                'USERNAME': member.get('username', member.get('handle', '')),
                'COMMUNITY_ID': str(member.get('community_id', member.get('group_id', ''))),
                'ROLE': member.get('role', member.get('user_type', 'member')),
                'STATUS': member.get('status', 'active'),
                'JOINED_AT': self._parse_timestamp(member.get('joined_at', member.get('created_at'))),
                'LAST_ACTIVE_AT': self._parse_timestamp(member.get('last_active_at', member.get('last_seen_at'))),
                'PROFILE_DATA': json.dumps(member) if member else '{}'
            }
            df_data.append(row)
        
        df = pd.DataFrame(df_data)
        self._load_dataframe_to_table(df, 'DISCO_MEMBERS')
    
    def load_products(self, products_data: List[Dict]):
        """Load products/courses data into Bronze table"""
        if not products_data:
            logger.warning("No products data to load")
            return
        
        # Transform data for Snowflake
        df_data = []
        for product in products_data:
            row = {
                'PRODUCT_ID': str(product.get('id', product.get('product_id', product.get('course_id', '')))),
                'PRODUCT_NAME': product.get('name', product.get('title', '')),
                'PRODUCT_TYPE': product.get('type', product.get('product_type', 'course')),
                'DESCRIPTION': product.get('description', ''),
                'PRICE': float(product.get('price', 0)) if product.get('price') else 0.0,
                'CURRENCY': product.get('currency', 'USD'),
                'CREATED_AT': self._parse_timestamp(product.get('created_at')),
                'UPDATED_AT': self._parse_timestamp(product.get('updated_at')),
                'STATUS': product.get('status', 'active'),
                'METADATA': json.dumps(product) if product else '{}'
            }
            df_data.append(row)
        
        df = pd.DataFrame(df_data)
        self._load_dataframe_to_table(df, 'DISCO_PRODUCTS')
    
    def load_enrollments(self, enrollments_data: List[Dict]):
        """Load enrollments data into Bronze table"""
        if not enrollments_data:
            logger.warning("No enrollments data to load")
            return
        
        # Transform data for Snowflake
        df_data = []
        for enrollment in enrollments_data:
            row = {
                'ENROLLMENT_ID': str(enrollment.get('id', enrollment.get('enrollment_id', ''))),
                'MEMBER_ID': str(enrollment.get('user_id', enrollment.get('member_id', ''))),
                'PRODUCT_ID': str(enrollment.get('product_id', enrollment.get('course_id', ''))),
                'COMMUNITY_ID': str(enrollment.get('community_id', enrollment.get('group_id', ''))),
                'ENROLLED_AT': self._parse_timestamp(enrollment.get('enrolled_at', enrollment.get('created_at'))),
                'UNENROLLED_AT': self._parse_timestamp(enrollment.get('unenrolled_at')),
                'STATUS': enrollment.get('status', 'active'),
                'PROGRESS_PERCENTAGE': float(enrollment.get('progress', enrollment.get('progress_percentage', 0))),
                'COMPLETION_DATE': self._parse_timestamp(enrollment.get('completed_at', enrollment.get('completion_date'))),
                'ENROLLMENT_DATA': json.dumps(enrollment) if enrollment else '{}'
            }
            df_data.append(row)
        
        df = pd.DataFrame(df_data)
        self._load_dataframe_to_table(df, 'DISCO_ENROLLMENTS')
    
    def _parse_timestamp(self, timestamp_str: Any) -> Optional[str]:
        """Parse timestamp string to Snowflake format"""
        if not timestamp_str:
            return None
        
        try:
            if isinstance(timestamp_str, str):
                # Try different timestamp formats
                for fmt in ['%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%d %H:%M:%S']:
                    try:
                        dt = datetime.strptime(timestamp_str, fmt)
                        return dt.strftime('%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        continue
            return str(timestamp_str)
        except Exception:
            return None
    
    def _load_dataframe_to_table(self, df: pd.DataFrame, table_name: str):
        """Load DataFrame to Snowflake table"""
        if df.empty:
            logger.warning(f"No data to load for table {table_name}")
            return
        
        try:
            # Clear existing data (full refresh for Bronze layer)
            truncate_query = f"TRUNCATE TABLE OLYMPUS_ANALYTICS.BRONZE.{table_name}"
            execute_query(truncate_query)
            
            # Load new data
            from snowflake.connector.pandas_tools import write_pandas
            
            success, nchunks, nrows, _ = write_pandas(
                conn=self.conn,
                df=df,
                table_name=table_name,
                database='OLYMPUS_ANALYTICS',
                schema='BRONZE',
                auto_create_table=False,
                overwrite=False
            )
            
            if success:
                logger.info(f"Successfully loaded {nrows} rows into {table_name}")
            else:
                logger.error(f"Failed to load data into {table_name}")
                
        except Exception as e:
            logger.error(f"Error loading data to {table_name}: {str(e)}")
            raise

def main():
    """Main function to run Disco API integration"""
    logger.info("Starting Disco API integration...")
    
    # Get API key from environment or Streamlit secrets
    api_key = os.getenv('DISCO_API_KEY')
    if not api_key:
        try:
            import streamlit as st
            api_key = st.secrets.get('disco', {}).get('api_key')
        except:
            pass
    
    if not api_key:
        logger.error("Disco API key not found. Please set DISCO_API_KEY environment variable or add to Streamlit secrets.")
        return False
    
    try:
        # Initialize clients
        disco_client = DiscoAPIClient(api_key)
        bronze_loader = DiscoBronzeLoader()
        
        # Create Bronze tables
        logger.info("Creating Bronze tables...")
        bronze_loader.create_bronze_tables()
        
        # Fetch and load data
        logger.info("Fetching communities data...")
        communities = disco_client.get_communities()
        bronze_loader.load_communities(communities)
        
        logger.info("Fetching members data...")
        members = disco_client.get_members()
        bronze_loader.load_members(members)
        
        logger.info("Fetching products data...")
        products = disco_client.get_products()
        bronze_loader.load_products(products)
        
        logger.info("Fetching enrollments data...")
        enrollments = disco_client.get_enrollments()
        bronze_loader.load_enrollments(enrollments)
        
        logger.info("Disco API integration completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Disco API integration failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)