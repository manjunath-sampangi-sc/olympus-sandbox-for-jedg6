import pandas as pd
import streamlit as st
from datetime import datetime, date
import os
from typing import Optional, Dict, Any
from utils.snowflake_connector import SnowflakeConnector

class BillingCSVExporter:
    """
    Utility class for exporting billing bracket data to CSV format.
    Provides functionality to generate monthly billing snapshots for operations/finance.
    """
    
    def __init__(self):
        self.snowflake_conn = SnowflakeConnector()
    
    def get_billing_data(
        self, 
        billing_month: Optional[str] = None,
        community_id: Optional[str] = None,
        billing_bracket: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Retrieve billing bracket data from Snowflake Gold table.
        
        Args:
            billing_month: Filter by specific billing month (YYYY-MM format)
            community_id: Filter by specific community/group
            billing_bracket: Filter by specific billing bracket ($0, $10, $50)
            
        Returns:
            DataFrame with billing data
        """
        
        base_query = """
        SELECT 
            MEMBER_ID,
            EMAIL,
            MEMBER_NAME,
            COMMUNITY_ID,
            GROUP_NAME,
            BILLING_MONTH,
            COURSE_COUNT_ACTIVE,
            HAS_HOME_COURSE,
            BILLING_BRACKET,
            MONTHLY_AMOUNT,
            ENROLLED_COURSES,
            BILLING_CATEGORY_DESCRIPTION,
            BILLING_RECORD_KEY
        FROM OLYMPUS_ANALYTICS.GOLD.GD_MEMBER_BILLING_BRACKETS_MONTHLY
        WHERE 1=1
        """
        
        conditions = []
        params = {}
        
        if billing_month:
            conditions.append("AND DATE_TRUNC('MONTH', billing_month) = %(billing_month)s")
            params['billing_month'] = f"{billing_month}-01"
        
        if community_id:
            conditions.append("AND community_id = %(community_id)s")
            params['community_id'] = community_id
            
        if billing_bracket:
            conditions.append("AND billing_bracket = %(billing_bracket)s")
            params['billing_bracket'] = billing_bracket
        
        query = base_query + " ".join(conditions) + " ORDER BY BILLING_MONTH DESC, GROUP_NAME, MEMBER_NAME"
        
        try:
            df = self.snowflake_conn.execute_query(query, params)
            return df
        except Exception as e:
            st.error(f"Error retrieving billing data: {str(e)}")
            return pd.DataFrame()
    
    def get_billing_summary(
        self, 
        billing_month: Optional[str] = None,
        community_id: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Get summary statistics for billing brackets.
        
        Args:
            billing_month: Filter by specific billing month (YYYY-MM format)
            community_id: Filter by specific community/group
            
        Returns:
            DataFrame with summary statistics
        """
        
        base_query = """
        SELECT 
            BILLING_MONTH,
            GROUP_NAME,
            BILLING_BRACKET,
            COUNT(*) as MEMBER_COUNT,
            SUM(MONTHLY_AMOUNT) as TOTAL_REVENUE,
            AVG(MONTHLY_AMOUNT) as AVG_AMOUNT_PER_MEMBER,
            COUNT(DISTINCT COMMUNITY_ID) as COMMUNITY_COUNT
        FROM OLYMPUS_ANALYTICS.GOLD.GD_MEMBER_BILLING_BRACKETS_MONTHLY
        WHERE 1=1
        """
        
        conditions = []
        params = {}
        
        if billing_month:
            conditions.append("AND DATE_TRUNC('MONTH', BILLING_MONTH) = %(billing_month)s")
            params['billing_month'] = f"{billing_month}-01"
        
        if community_id:
            conditions.append("AND COMMUNITY_ID = %(community_id)s")
            params['community_id'] = community_id
        
        query = base_query + " ".join(conditions) + """
        GROUP BY BILLING_MONTH, GROUP_NAME, BILLING_BRACKET
        ORDER BY BILLING_MONTH DESC, GROUP_NAME, BILLING_BRACKET
        """
        
        try:
            df = self.snowflake_conn.execute_query(query, params)
            return df
        except Exception as e:
            st.error(f"Error retrieving billing summary: {str(e)}")
            return pd.DataFrame()
    
    def export_to_csv(
        self, 
        df: pd.DataFrame, 
        filename: Optional[str] = None,
        include_timestamp: bool = True
    ) -> str:
        """
        Export DataFrame to CSV file.
        
        Args:
            df: DataFrame to export
            filename: Custom filename (without extension)
            include_timestamp: Whether to include timestamp in filename
            
        Returns:
            Path to the exported CSV file
        """
        
        if df.empty:
            raise ValueError("Cannot export empty DataFrame")
        
        # Generate filename
        if not filename:
            filename = "billing_export"
        
        if include_timestamp:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{filename}_{timestamp}"
        
        filename = f"{filename}.csv"
        
        # Create exports directory if it doesn't exist
        export_dir = "exports"
        os.makedirs(export_dir, exist_ok=True)
        
        filepath = os.path.join(export_dir, filename)
        
        # Export to CSV
        df.to_csv(filepath, index=False)
        
        return filepath
    
    def generate_monthly_billing_snapshot(
        self, 
        billing_month: str,
        community_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a complete monthly billing snapshot with data and summary.
        
        Args:
            billing_month: Billing month in YYYY-MM format
            community_id: Optional community filter
            
        Returns:
            Dictionary containing data, summary, and file paths
        """
        
        # Get detailed billing data
        billing_data = self.get_billing_data(
            billing_month=billing_month,
            community_id=community_id
        )
        
        # Get summary data
        summary_data = self.get_billing_summary(
            billing_month=billing_month,
            community_id=community_id
        )
        
        if billing_data.empty:
            return {
                'success': False,
                'message': f'No billing data found for {billing_month}',
                'data': pd.DataFrame(),
                'summary': pd.DataFrame()
            }
        
        # Generate filenames
        month_str = billing_month.replace('-', '')
        community_suffix = f"_community_{community_id}" if community_id else ""
        
        # Export files
        try:
            data_file = self.export_to_csv(
                billing_data, 
                f"billing_data_{month_str}{community_suffix}"
            )
            
            summary_file = self.export_to_csv(
                summary_data, 
                f"billing_summary_{month_str}{community_suffix}"
            )
            
            # Calculate totals
            total_members = len(billing_data)
            total_revenue = billing_data['monthly_amount'].sum()
            bracket_counts = billing_data['billing_bracket'].value_counts().to_dict()
            
            return {
                'success': True,
                'message': f'Successfully exported billing data for {billing_month}',
                'data': billing_data,
                'summary': summary_data,
                'data_file': data_file,
                'summary_file': summary_file,
                'totals': {
                    'total_members': total_members,
                    'total_revenue': total_revenue,
                    'bracket_counts': bracket_counts
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error exporting data: {str(e)}',
                'data': billing_data,
                'summary': summary_data
            }
    
    def get_available_months(self) -> list:
        """
        Get list of available billing months from the data.
        
        Returns:
            List of available billing months in YYYY-MM format
        """
        
        query = """
        SELECT DISTINCT 
            TO_CHAR(BILLING_MONTH, 'YYYY-MM') as BILLING_MONTH
        FROM OLYMPUS_ANALYTICS.GOLD.GD_MEMBER_BILLING_BRACKETS_MONTHLY
        ORDER BY BILLING_MONTH DESC
        """
        
        try:
            df = self.snowflake_conn.execute_query(query)
            return df['BILLING_MONTH'].tolist() if not df.empty else []
        except Exception as e:
            st.error(f"Error retrieving available months: {str(e)}")
            return []
    
    def get_available_communities(self) -> pd.DataFrame:
        """
        Get list of available communities/groups.
        
        Returns:
            DataFrame with community information
        """
        
        query = """
        SELECT DISTINCT 
            COMMUNITY_ID,
            GROUP_NAME,
            COUNT(DISTINCT MEMBER_ID) as MEMBER_COUNT
        FROM OLYMPUS_ANALYTICS.GOLD.GD_MEMBER_BILLING_BRACKETS_MONTHLY
        GROUP BY COMMUNITY_ID, GROUP_NAME
        ORDER BY GROUP_NAME
        """
        
        try:
            df = self.snowflake_conn.execute_query(query)
            return df
        except Exception as e:
            st.error(f"Error retrieving available communities: {str(e)}")
            return pd.DataFrame()