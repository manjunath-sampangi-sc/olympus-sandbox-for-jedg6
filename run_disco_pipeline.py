#!/usr/bin/env python3
"""
Disco LMS Data Pipeline Runner

This script orchestrates the complete data pipeline:
1. Fetch data from Disco LMS API
2. Load into Snowflake Bronze tables
3. Run dbt models to create Silver and Gold tables
4. Validate data quality and billing calculations

Usage:
    python run_disco_pipeline.py [--test-mode] [--skip-api] [--skip-dbt]
"""

import os
import sys
import argparse
import logging
from datetime import datetime
from pathlib import Path

# Add the streamlit_app directory to Python path
streamlit_app_path = Path(__file__).parent / "streamlit_app"
sys.path.insert(0, str(streamlit_app_path))

from streamlit_app.disco_api_integration import DiscoAPIClient, DiscoGoldLoader
from streamlit_app.utils.snowflake_connector import SnowflakeConnector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('disco_pipeline.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DiscoPipelineRunner:
    """
    Orchestrates the complete Disco LMS data pipeline.
    """
    
    def __init__(self, test_mode: bool = False):
        self.test_mode = test_mode
        self.snowflake_conn = SnowflakeConnector()
        
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
            raise ValueError("Disco API key not found")
        
        # Initialize API client and loader
        try:
            self.api_client = DiscoAPIClient(api_key)
            self.bronze_loader = DiscoGoldLoader()
            logger.info("Pipeline components initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize pipeline components: {e}")
            raise
    
    def run_api_ingestion(self) -> bool:
        """
        Run the API data ingestion process.
        
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info("Starting Disco API data ingestion...")
        
        try:
            # Test API connectivity first
            logger.info("Testing API connectivity...")
            communities = self.api_client.get_communities()
            if not communities:
                logger.warning("No communities found or API connection failed")
                return False
            
            logger.info(f"Found {len(communities)} communities")
            
            # Create Gold tables
            logger.info("Creating Gold tables...")
            self.bronze_loader.create_gold_tables()
            
            # Load data for each community
            total_records = 0
            
            for community in communities:
                community_id = community.get('id')
                community_name = community.get('name', 'Unknown')
                
                logger.info(f"Processing community: {community_name} (ID: {community_id})")
                
                try:
                    # Load communities data
                    communities_df = self.bronze_loader.load_communities([community])
                    total_records += len(communities_df)
                    
                    # Load members data
                    members = self.api_client.get_members(community_id)
                    if members:
                        members_df = self.bronze_loader.load_members(members)
                        total_records += len(members_df)
                        logger.info(f"Loaded {len(members)} members for {community_name}")
                    
                    # Load products data
                    products = self.api_client.get_products(community_id)
                    if products:
                        products_df = self.bronze_loader.load_products(products)
                        total_records += len(products_df)
                        logger.info(f"Loaded {len(products)} products for {community_name}")
                    
                    # Load enrollments data
                    enrollments = self.api_client.get_enrollments(community_id)
                    if enrollments:
                        enrollments_df = self.bronze_loader.load_enrollments(enrollments)
                        total_records += len(enrollments_df)
                        logger.info(f"Loaded {len(enrollments)} enrollments for {community_name}")
                    
                    if self.test_mode:
                        logger.info("Test mode: Processing only first community")
                        break
                        
                except Exception as e:
                    logger.error(f"Error processing community {community_name}: {e}")
                    continue
            
            logger.info(f"API ingestion completed. Total records loaded: {total_records}")
            return True
            
        except Exception as e:
            logger.error(f"API ingestion failed: {e}")
            return False
    
    def run_dbt_models(self) -> bool:
        """
        Run dbt models to transform data from Bronze to Silver to Gold.
        
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info("Running dbt models...")
        
        try:
            # Change to dbt project directory
            dbt_project_path = Path(__file__).parent / "dbt_olympus_analytics"
            original_cwd = os.getcwd()
            
            try:
                os.chdir(dbt_project_path)
                
                # Run dbt models in order
                commands = [
                    "dbt deps",  # Install dependencies
                    "dbt run --models tag:bronze",  # Run Bronze models
                    "dbt run --models tag:silver",  # Run Silver models  
                    "dbt run --models tag:gold",    # Run Gold models
                    "dbt test"  # Run tests
                ]
                
                for cmd in commands:
                    logger.info(f"Executing: {cmd}")
                    result = os.system(cmd)
                    
                    if result != 0:
                        logger.error(f"Command failed: {cmd}")
                        if not self.test_mode:
                            return False
                        else:
                            logger.warning("Test mode: Continuing despite dbt errors")
                
                logger.info("dbt models completed successfully")
                return True
                
            finally:
                os.chdir(original_cwd)
                
        except Exception as e:
            logger.error(f"dbt execution failed: {e}")
            return False
    
    def validate_data_quality(self) -> bool:
        """
        Validate data quality and billing calculations.
        
        Returns:
            bool: True if validation passes, False otherwise
        """
        logger.info("Validating data quality...")
        
        try:
            # Check if Gold table exists and has data
            query = """
            SELECT COUNT(*) as record_count,
                   COUNT(DISTINCT member_id) as unique_members,
                   COUNT(DISTINCT community_id) as unique_communities,
                   SUM(monthly_amount) as total_revenue
            FROM OLYMPUS_ANALYTICS.GOLD.GD_MEMBER_BILLING_BRACKETS_MONTHLY
            WHERE billing_month >= DATEADD(month, -3, CURRENT_DATE())
            """
            
            result = self.snowflake_conn.execute_query(query)
            
            if result.empty:
                logger.error("No data found in Gold table")
                return False
            
            record_count = result.iloc[0]['RECORD_COUNT']
            unique_members = result.iloc[0]['UNIQUE_MEMBERS']
            unique_communities = result.iloc[0]['UNIQUE_COMMUNITIES']
            total_revenue = result.iloc[0]['TOTAL_REVENUE']
            
            logger.info(f"Data validation results:")
            logger.info(f"  - Total records: {record_count}")
            logger.info(f"  - Unique members: {unique_members}")
            logger.info(f"  - Unique communities: {unique_communities}")
            logger.info(f"  - Total revenue: ${total_revenue:.2f}")
            
            # Validate billing bracket logic
            bracket_validation_query = """
            SELECT billing_bracket,
                   COUNT(*) as count,
                   AVG(course_count_active) as avg_courses,
                   AVG(CASE WHEN has_home_course THEN 1 ELSE 0 END) as home_course_rate
            FROM OLYMPUS_ANALYTICS.GOLD.GD_MEMBER_BILLING_BRACKETS_MONTHLY
            WHERE billing_month >= DATEADD(month, -1, CURRENT_DATE())
            GROUP BY billing_bracket
            ORDER BY billing_bracket
            """
            
            bracket_results = self.snowflake_conn.execute_query(bracket_validation_query)
            
            logger.info("Billing bracket validation:")
            for _, row in bracket_results.iterrows():
                bracket = row['BILLING_BRACKET']
                count = row['COUNT']
                avg_courses = row['AVG_COURSES']
                home_rate = row['HOME_COURSE_RATE']
                
                logger.info(f"  - {bracket}: {count} members, avg {avg_courses:.1f} courses, {home_rate:.1%} have home course")
            
            # Basic validation checks
            if record_count == 0:
                logger.error("No records found in Gold table")
                return False
            
            if unique_members == 0:
                logger.error("No unique members found")
                return False
            
            logger.info("Data quality validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Data validation failed: {e}")
            return False
    
    def run_full_pipeline(self, skip_api: bool = False, skip_dbt: bool = False) -> bool:
        """
        Run the complete data pipeline.
        
        Args:
            skip_api: Skip API ingestion step
            skip_dbt: Skip dbt model execution
            
        Returns:
            bool: True if pipeline completed successfully
        """
        logger.info("Starting Disco LMS data pipeline...")
        start_time = datetime.now()
        
        success = True
        
        try:
            # Step 1: API Ingestion
            if not skip_api:
                if not self.run_api_ingestion():
                    logger.error("API ingestion failed")
                    success = False
                    if not self.test_mode:
                        return False
            else:
                logger.info("Skipping API ingestion")
            
            # Step 2: dbt Models
            if not skip_dbt:
                if not self.run_dbt_models():
                    logger.error("dbt models failed")
                    success = False
                    if not self.test_mode:
                        return False
            else:
                logger.info("Skipping dbt models")
            
            # Step 3: Data Validation
            if not self.validate_data_quality():
                logger.error("Data validation failed")
                success = False
                if not self.test_mode:
                    return False
            
            end_time = datetime.now()
            duration = end_time - start_time
            
            if success:
                logger.info(f"Pipeline completed successfully in {duration}")
            else:
                logger.warning(f"Pipeline completed with errors in {duration}")
            
            return success
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description="Run Disco LMS data pipeline")
    parser.add_argument("--test-mode", action="store_true", help="Run in test mode (process limited data)")
    parser.add_argument("--skip-api", action="store_true", help="Skip API data ingestion")
    parser.add_argument("--skip-dbt", action="store_true", help="Skip dbt model execution")
    
    args = parser.parse_args()
    
    # Initialize and run pipeline
    try:
        runner = DiscoPipelineRunner(test_mode=args.test_mode)
        success = runner.run_full_pipeline(
            skip_api=args.skip_api,
            skip_dbt=args.skip_dbt
        )
        
        if success:
            print("\n✅ Pipeline completed successfully!")
            print("\n📊 You can now view the billing dashboard at:")
            print("   http://localhost:8501/billing_dashboard")
            sys.exit(0)
        else:
            print("\n❌ Pipeline completed with errors. Check logs for details.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Pipeline failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()