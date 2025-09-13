import os
import sys
import time
import logging
import threading
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
import schedule
import streamlit as st
from dataclasses import dataclass

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from disco_api_integration import DiscoAPIClient, DiscoGoldLoader
from utils.snowflake_connector import get_snowflake_connector, execute_query

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class SyncStatus:
    """Data class to track sync status"""
    last_sync: Optional[datetime] = None
    is_running: bool = False
    last_error: Optional[str] = None
    records_synced: int = 0
    sync_type: str = "manual"  # manual, scheduled
    duration_seconds: float = 0.0

class DataSyncManager:
    """Manages data synchronization between Disco API and Snowflake"""
    
    def __init__(self):
        self.sync_status = SyncStatus()
        self.scheduler_thread = None
        self.scheduler_running = False
        self.api_client = None
        self.gold_loader = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize API client and data loader"""
        try:
            # Get API key from environment or Streamlit secrets
            api_key = os.getenv('DISCO_API_KEY')
            if not api_key:
                try:
                    api_key = st.secrets.get('disco', {}).get('api_key')
                except:
                    pass
            
            if api_key:
                self.api_client = DiscoAPIClient(api_key)
                self.gold_loader = DiscoGoldLoader()
                logger.info("Data sync clients initialized successfully")
            else:
                logger.warning("Disco API key not found - sync functionality limited")
        except Exception as e:
            logger.error(f"Failed to initialize sync clients: {str(e)}")
    
    def sync_data_now(self, sync_type: str = "manual") -> Dict[str, Any]:
        """Perform immediate data synchronization"""
        if self.sync_status.is_running:
            return {
                "success": False,
                "message": "Sync already in progress",
                "status": self.sync_status
            }
        
        if not self.api_client or not self.gold_loader:
            return {
                "success": False,
                "message": "API client not initialized - check API key configuration",
                "status": self.sync_status
            }
        
        # Start sync process
        self.sync_status.is_running = True
        self.sync_status.sync_type = sync_type
        self.sync_status.last_error = None
        start_time = time.time()
        
        try:
            logger.info(f"Starting {sync_type} data sync...")
            
            # Create/update Gold tables
            self.gold_loader.create_gold_tables()
            
            # Fetch and sync all data
            total_records = 0
            
            # 1. Sync Communities
            logger.info("Syncing communities...")
            communities = self.api_client.get_communities()
            if communities:
                self._upsert_communities(communities)
                total_records += len(communities)
                logger.info(f"Synced {len(communities)} communities")
            
            # 2. Process each community for members, products, and enrollments
            all_members = []
            all_products = []
            all_enrollments = []
            
            for community in communities:
                community_id = community.get('id')
                community_name = community.get('name', 'Unknown')
                logger.info(f"Processing community: {community_name}")
                
                # Fetch members
                members = self.api_client.get_members()
                for member in members:
                    member['community_id'] = community_id
                all_members.extend(members)
                
                # Fetch products
                products = self.api_client.get_products()
                for product in products:
                    product['community_id'] = community_id
                all_products.extend(products)
                
                # Fetch enrollments
                enrollments = self.api_client.get_enrollments_for_community(community_id)
                all_enrollments.extend(enrollments)
            
            # 3. Upsert all data
            if all_members:
                self._upsert_members(all_members)
                total_records += len(all_members)
                logger.info(f"Synced {len(all_members)} members")
            
            if all_products:
                self._upsert_products(all_products)
                total_records += len(all_products)
                logger.info(f"Synced {len(all_products)} products")
            
            if all_enrollments:
                self._upsert_enrollments(all_enrollments)
                total_records += len(all_enrollments)
                logger.info(f"Synced {len(all_enrollments)} enrollments")
            
            # Update sync status
            end_time = time.time()
            self.sync_status.last_sync = datetime.now(timezone.utc)
            self.sync_status.records_synced = total_records
            self.sync_status.duration_seconds = end_time - start_time
            self.sync_status.is_running = False
            
            logger.info(f"Data sync completed successfully! Synced {total_records} records in {self.sync_status.duration_seconds:.2f} seconds")
            
            return {
                "success": True,
                "message": f"Successfully synced {total_records} records",
                "status": self.sync_status
            }
            
        except Exception as e:
            self.sync_status.is_running = False
            self.sync_status.last_error = str(e)
            logger.error(f"Data sync failed: {str(e)}")
            
            return {
                "success": False,
                "message": f"Sync failed: {str(e)}",
                "status": self.sync_status
            }
    
    def _upsert_communities(self, communities: List[Dict]):
        """Upsert communities data with conflict resolution"""
        try:
            # Use the existing load_communities method which handles upserts
            self.gold_loader.load_communities(communities)
        except Exception as e:
            logger.error(f"Failed to upsert communities: {str(e)}")
            raise
    
    def _upsert_members(self, members: List[Dict]):
        """Upsert members data with conflict resolution"""
        try:
            # Use the existing load_users method which handles upserts
            self.gold_loader.load_users(members)
        except Exception as e:
            logger.error(f"Failed to upsert members: {str(e)}")
            raise
    
    def _upsert_products(self, products: List[Dict]):
        """Upsert products data with conflict resolution"""
        try:
            # Use the existing load_courses method which handles upserts
            self.gold_loader.load_courses(products)
        except Exception as e:
            logger.error(f"Failed to upsert products: {str(e)}")
            raise
    
    def _upsert_enrollments(self, enrollments: List[Dict]):
        """Upsert enrollments data with conflict resolution"""
        try:
            # Use the existing load_enrollments method which handles upserts
            self.gold_loader.load_enrollments(enrollments)
        except Exception as e:
            logger.error(f"Failed to upsert enrollments: {str(e)}")
            raise
    
    def start_scheduler(self):
        """Start the hourly sync scheduler"""
        if self.scheduler_running:
            logger.info("Scheduler already running")
            return
        
        # Schedule hourly sync
        schedule.clear()
        schedule.every().hour.do(self._scheduled_sync)
        
        self.scheduler_running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        logger.info("Data sync scheduler started - will run every hour")
    
    def stop_scheduler(self):
        """Stop the sync scheduler"""
        self.scheduler_running = False
        schedule.clear()
        logger.info("Data sync scheduler stopped")
    
    def _scheduled_sync(self):
        """Perform scheduled sync"""
        logger.info("Running scheduled data sync...")
        result = self.sync_data_now(sync_type="scheduled")
        if result["success"]:
            logger.info(f"Scheduled sync completed: {result['message']}")
        else:
            logger.error(f"Scheduled sync failed: {result['message']}")
    
    def _run_scheduler(self):
        """Run the scheduler in a separate thread"""
        while self.scheduler_running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get current sync status"""
        return {
            "last_sync": self.sync_status.last_sync.isoformat() if self.sync_status.last_sync else None,
            "is_running": self.sync_status.is_running,
            "last_error": self.sync_status.last_error,
            "records_synced": self.sync_status.records_synced,
            "sync_type": self.sync_status.sync_type,
            "duration_seconds": self.sync_status.duration_seconds,
            "scheduler_running": self.scheduler_running,
            "api_client_ready": self.api_client is not None
        }
    
    def get_last_sync_summary(self) -> str:
        """Get a human-readable summary of the last sync"""
        if not self.sync_status.last_sync:
            return "No sync performed yet"
        
        time_ago = datetime.now(timezone.utc) - self.sync_status.last_sync
        hours_ago = int(time_ago.total_seconds() / 3600)
        minutes_ago = int((time_ago.total_seconds() % 3600) / 60)
        
        if hours_ago > 0:
            time_str = f"{hours_ago}h {minutes_ago}m ago"
        else:
            time_str = f"{minutes_ago}m ago"
        
        return f"Last {self.sync_status.sync_type} sync: {time_str} ({self.sync_status.records_synced} records, {self.sync_status.duration_seconds:.1f}s)"

# Global sync manager instance
_sync_manager = None

def get_sync_manager() -> DataSyncManager:
    """Get or create the global sync manager instance"""
    global _sync_manager
    if _sync_manager is None:
        _sync_manager = DataSyncManager()
    return _sync_manager