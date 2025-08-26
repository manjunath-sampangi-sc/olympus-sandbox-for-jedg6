import streamlit as st
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas, pd_writer
import pandas as pd
import os
from typing import Dict, Any, Optional, List
import logging
from contextlib import contextmanager
import time
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SnowflakeConnector:
    """Enhanced Snowflake connector with connection pooling and error handling"""
    
    def __init__(self):
        self.connection = None
        self.connection_params = self._get_connection_params()
        self.last_connection_time = None
        self.connection_timeout = 300  # 5 minutes
        
    def _get_connection_params(self) -> Dict[str, str]:
        """Get connection parameters from Streamlit secrets or environment variables"""
        try:
            # Try Streamlit secrets first
            if hasattr(st, 'secrets') and 'snowflake' in st.secrets:
                return {
                    'account': st.secrets['snowflake']['account'],
                    'user': st.secrets['snowflake']['user'],
                    'password': st.secrets['snowflake'].get('password'),
                    'warehouse': st.secrets['snowflake']['warehouse'],
                    'database': st.secrets['snowflake']['database'],
                    'schema': st.secrets['snowflake']['schema'],
                    'role': st.secrets['snowflake'].get('role', 'OLYMPUS_CONTRACTOR'),
                    'authenticator': st.secrets['snowflake'].get('authenticator', 'snowflake')
                }
            else:
                # Fallback to environment variables
                return {
                    'account': os.getenv('SNOWFLAKE_ACCOUNT', 'KDLCEKW-GPB78424'),
                    'user': os.getenv('SNOWFLAKE_USER', 'MANJANUTH'),
                    'password': os.getenv('SNOWFLAKE_PASSWORD'),
                    'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE', 'XS_WAREHOUSE'),
                    'database': os.getenv('SNOWFLAKE_DATABASE', 'OLYMPUS_ANALYTICS'),
                    'schema': os.getenv('SNOWFLAKE_SCHEMA', 'GOLD'),
                    'role': os.getenv('SNOWFLAKE_ROLE', 'OLYMPUS_CONTRACTOR'),
                    'authenticator': os.getenv('SNOWFLAKE_AUTHENTICATOR', 'snowflake')
                }
        except Exception as e:
            logger.error(f"Error getting connection parameters: {e}")
            raise
    
    def _is_connection_valid(self) -> bool:
        """Check if current connection is valid and not expired"""
        if not self.connection:
            return False
        
        if self.last_connection_time:
            elapsed = time.time() - self.last_connection_time
            if elapsed > self.connection_timeout:
                return False
        
        try:
            # Test connection with a simple query
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            return True
        except Exception:
            return False
    
    def connect(self) -> bool:
        """Establish or refresh connection to Snowflake"""
        try:
            if self._is_connection_valid():
                return True
            
            # Close existing connection if any
            if self.connection:
                try:
                    self.connection.close()
                except Exception:
                    pass
            
            # Create new connection
            # Filter out password if using external browser authentication
            conn_params = self.connection_params.copy()
            if conn_params.get('authenticator') == 'externalbrowser':
                conn_params.pop('password', None)  # Remove password for external auth
            
            self.connection = snowflake.connector.connect(
                **conn_params,
                client_session_keep_alive=True,
                network_timeout=60,
                login_timeout=30
            )
            
            self.last_connection_time = time.time()
            logger.info("Successfully connected to Snowflake")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Snowflake: {e}")
            self.connection = None
            return False
    
    @contextmanager
    def get_cursor(self):
        """Context manager for cursor operations"""
        if not self.connect():
            raise Exception("Failed to establish Snowflake connection")
        
        cursor = self.connection.cursor()
        try:
            yield cursor
        finally:
            cursor.close()
    
    def execute_query(self, query: str, params: Optional[Dict] = None) -> pd.DataFrame:
        """Execute SQL query and return results as DataFrame"""
        try:
            with self.get_cursor() as cursor:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                # Fetch results and column names
                results = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                
                # Create DataFrame
                df = pd.DataFrame(results, columns=columns)
                logger.info(f"Query executed successfully, returned {len(df)} rows")
                return df
                
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            logger.error(f"Query: {query[:200]}...")  # Log first 200 chars of query
            raise
    
    def execute_query_cached(self, query: str, cache_ttl: int = 300) -> pd.DataFrame:
        """Execute query with Streamlit caching"""
        @st.cache_data(ttl=cache_ttl)
        def _cached_query(query_hash: str, query: str) -> pd.DataFrame:
            return self.execute_query(query)
        
        # Create a hash of the query for caching
        query_hash = str(hash(query))
        return _cached_query(query_hash, query)
    
    def write_dataframe(self, df: pd.DataFrame, table_name: str, 
                       schema: Optional[str] = None, if_exists: str = 'append') -> bool:
        """Write DataFrame to Snowflake table"""
        try:
            if not self.connect():
                return False
            
            target_schema = schema or self.connection_params['schema']
            
            success, nchunks, nrows, _ = write_pandas(
                conn=self.connection,
                df=df,
                table_name=table_name,
                schema=target_schema,
                auto_create_table=True,
                overwrite=(if_exists == 'replace')
            )
            
            if success:
                logger.info(f"Successfully wrote {nrows} rows to {target_schema}.{table_name}")
                return True
            else:
                logger.error(f"Failed to write data to {target_schema}.{table_name}")
                return False
                
        except Exception as e:
            logger.error(f"Error writing DataFrame to Snowflake: {e}")
            return False
    
    def get_table_info(self, table_name: str, schema: Optional[str] = None) -> pd.DataFrame:
        """Get table schema information"""
        target_schema = schema or self.connection_params['schema']
        query = f"""
        DESCRIBE TABLE {self.connection_params['database']}.{target_schema}.{table_name}
        """
        return self.execute_query(query)
    
    def list_tables(self, schema: Optional[str] = None) -> List[str]:
        """List all tables in a schema"""
        target_schema = schema or self.connection_params['schema']
        query = f"""
        SHOW TABLES IN SCHEMA {self.connection_params['database']}.{target_schema}
        """
        df = self.execute_query(query)
        return df['name'].tolist() if 'name' in df.columns else []
    
    def test_connection(self) -> Dict[str, Any]:
        """Test connection and return status information"""
        try:
            start_time = time.time()
            
            if not self.connect():
                return {
                    'status': 'failed',
                    'message': 'Failed to establish connection',
                    'response_time': None
                }
            
            # Test with a simple query
            df = self.execute_query("SELECT CURRENT_VERSION(), CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE()")
            
            response_time = time.time() - start_time
            
            if not df.empty:
                return {
                    'status': 'success',
                    'message': 'Connection successful',
                    'response_time': round(response_time, 3),
                    'version': df.iloc[0, 0] if len(df.columns) > 0 else None,
                    'user': df.iloc[0, 1] if len(df.columns) > 1 else None,
                    'role': df.iloc[0, 2] if len(df.columns) > 2 else None,
                    'warehouse': df.iloc[0, 3] if len(df.columns) > 3 else None
                }
            else:
                return {
                    'status': 'failed',
                    'message': 'Query returned no results',
                    'response_time': round(response_time, 3)
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'response_time': None
            }
    
    def close(self):
        """Close Snowflake connection"""
        if self.connection:
            try:
                self.connection.close()
                logger.info("Snowflake connection closed")
            except Exception as e:
                logger.error(f"Error closing connection: {e}")
            finally:
                self.connection = None
                self.last_connection_time = None
    
    def __del__(self):
        """Cleanup on object destruction"""
        self.close()

# Global connector instance
_snowflake_connector = None

def get_snowflake_connector() -> SnowflakeConnector:
    """Get or create global Snowflake connector instance"""
    global _snowflake_connector
    
    if _snowflake_connector is None:
        _snowflake_connector = SnowflakeConnector()
    
    return _snowflake_connector

# Convenience functions
def execute_query(query: str, params: Optional[Dict] = None, use_cache: bool = True) -> pd.DataFrame:
    """Execute query using global connector"""
    connector = get_snowflake_connector()
    if use_cache:
        return connector.execute_query_cached(query)
    else:
        return connector.execute_query(query, params)

def test_snowflake_connection() -> Dict[str, Any]:
    """Test Snowflake connection and return status"""
    connector = get_snowflake_connector()
    return connector.test_connection()

def test_connection() -> bool:
    """Simple test connection function that returns True/False"""
    try:
        result = test_snowflake_connection()
        return result.get('success', False)
    except Exception:
        return False