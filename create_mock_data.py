#!/usr/bin/env python3
"""
Create Mock Data for Disco LMS Integration

This script creates sample data in the Bronze tables to demonstrate
the billing dashboard functionality when real API data is not available.
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import logging

# Add the streamlit_app directory to Python path
streamlit_app_path = Path(__file__).parent / "streamlit_app"
sys.path.insert(0, str(streamlit_app_path))

from streamlit_app.disco_api_integration import DiscoBronzeLoader
from streamlit_app.utils.snowflake_connector import SnowflakeConnector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_mock_data():
    """Create mock data for testing the billing dashboard"""
    logger.info("Creating mock data for Disco LMS integration...")
    
    try:
        # Initialize loader
        bronze_loader = DiscoBronzeLoader()
        
        # Create Bronze tables first
        logger.info("Creating Bronze tables...")
        bronze_loader.create_bronze_tables()
        
        # Create mock communities
        communities_data = [
            {
                'id': 'comm_001',
                'name': 'Tech Professionals',
                'description': 'Community for technology professionals',
                'created_at': '2024-01-01T00:00:00Z',
                'status': 'active',
                'member_count': 150
            },
            {
                'id': 'comm_002', 
                'name': 'Marketing Experts',
                'description': 'Community for marketing professionals',
                'created_at': '2024-01-15T00:00:00Z',
                'status': 'active',
                'member_count': 85
            }
        ]
        
        # Create mock members
        members_data = []
        for i in range(1, 51):  # 50 members
            community_id = 'comm_001' if i <= 30 else 'comm_002'
            members_data.append({
                'id': f'member_{i:03d}',
                'email': f'user{i}@example.com',
                'first_name': f'User{i}',
                'last_name': f'Test{i}',
                'username': f'user{i}',
                'community_id': community_id,
                'role': 'member',
                'status': 'active',
                'joined_at': (datetime.now() - timedelta(days=i*2)).isoformat() + 'Z'
            })
        
        # Create mock products/courses
        products_data = [
            {
                'id': 'prod_home',
                'name': 'Home Course',
                'description': 'Basic home course for all members',
                'type': 'course',
                'price': 0,
                'status': 'active',
                'created_at': '2024-01-01T00:00:00Z'
            },
            {
                'id': 'prod_advanced_tech',
                'name': 'Advanced Technology',
                'description': 'Advanced technology course',
                'type': 'course', 
                'price': 299,
                'status': 'active',
                'created_at': '2024-01-10T00:00:00Z'
            },
            {
                'id': 'prod_marketing_basics',
                'name': 'Marketing Basics',
                'description': 'Basic marketing principles',
                'type': 'course',
                'price': 199,
                'status': 'active',
                'created_at': '2024-01-15T00:00:00Z'
            },
            {
                'id': 'prod_leadership',
                'name': 'Leadership Skills',
                'description': 'Leadership development course',
                'type': 'course',
                'price': 399,
                'status': 'active',
                'created_at': '2024-02-01T00:00:00Z'
            }
        ]
        
        # Create mock enrollments with different billing scenarios
        enrollments_data = []
        enrollment_id = 1
        
        # Scenario 1: Members with no enrollments ($0 billing)
        for i in range(1, 6):  # 5 members with no enrollments
            pass  # No enrollments for these members
        
        # Scenario 2: Members with only Home course ($10 billing)
        for i in range(6, 21):  # 15 members with only Home
            enrollments_data.append({
                'id': f'enroll_{enrollment_id:03d}',
                'member_id': f'member_{i:03d}',
                'product_id': 'prod_home',
                'enrolled_at': (datetime.now() - timedelta(days=i)).isoformat() + 'Z',
                'status': 'active',
                'completion_status': 'in_progress'
            })
            enrollment_id += 1
        
        # Scenario 3: Members with 2+ courses or Home + others ($50 billing)
        for i in range(21, 51):  # 30 members with multiple courses
            # Everyone gets Home course
            enrollments_data.append({
                'id': f'enroll_{enrollment_id:03d}',
                'member_id': f'member_{i:03d}',
                'product_id': 'prod_home',
                'enrolled_at': (datetime.now() - timedelta(days=i)).isoformat() + 'Z',
                'status': 'active',
                'completion_status': 'completed'
            })
            enrollment_id += 1
            
            # Add additional courses based on member number
            if i % 3 == 0:  # Every 3rd member gets Advanced Tech
                enrollments_data.append({
                    'id': f'enroll_{enrollment_id:03d}',
                    'member_id': f'member_{i:03d}',
                    'product_id': 'prod_advanced_tech',
                    'enrolled_at': (datetime.now() - timedelta(days=i-5)).isoformat() + 'Z',
                    'status': 'active',
                    'completion_status': 'in_progress'
                })
                enrollment_id += 1
            elif i % 4 == 0:  # Every 4th member gets Marketing
                enrollments_data.append({
                    'id': f'enroll_{enrollment_id:03d}',
                    'member_id': f'member_{i:03d}',
                    'product_id': 'prod_marketing_basics',
                    'enrolled_at': (datetime.now() - timedelta(days=i-3)).isoformat() + 'Z',
                    'status': 'active',
                    'completion_status': 'completed'
                })
                enrollment_id += 1
            else:  # Others get Leadership
                enrollments_data.append({
                    'id': f'enroll_{enrollment_id:03d}',
                    'member_id': f'member_{i:03d}',
                    'product_id': 'prod_leadership',
                    'enrolled_at': (datetime.now() - timedelta(days=i-7)).isoformat() + 'Z',
                    'status': 'active',
                    'completion_status': 'in_progress'
                })
                enrollment_id += 1
        
        # Load data into Bronze tables
        logger.info("Loading communities data...")
        bronze_loader.load_communities(communities_data)
        
        logger.info("Loading members data...")
        bronze_loader.load_members(members_data)
        
        logger.info("Loading products data...")
        bronze_loader.load_products(products_data)
        
        logger.info("Loading enrollments data...")
        bronze_loader.load_enrollments(enrollments_data)
        
        logger.info("Mock data creation completed successfully!")
        logger.info(f"Created:")
        logger.info(f"  - {len(communities_data)} communities")
        logger.info(f"  - {len(members_data)} members")
        logger.info(f"  - {len(products_data)} products")
        logger.info(f"  - {len(enrollments_data)} enrollments")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to create mock data: {str(e)}")
        return False

if __name__ == "__main__":
    success = create_mock_data()
    sys.exit(0 if success else 1)