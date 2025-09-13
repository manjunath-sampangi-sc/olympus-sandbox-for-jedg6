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
        self.data_layer = 'gold'  # Default to gold layer
        self.layer_config = {
            'gold': {
                'schema': 'GOLD',
                'table': 'GD_MEMBER_ENROLLMENT_DETAILS',
                'columns': {
                    'member_id': 'MEMBER_ID',
                    'email': 'EMAIL',
                    'member_name': 'MEMBER_NAME',
                    'first_name': 'FIRST_NAME',
                    'last_name': 'LAST_NAME',
                    'community_id': 'COMMUNITY_ID',
                    'group_name': 'GROUP_NAME',
                    'company_name': 'COMPANY_NAME',
                    'billing_month': 'BILLING_MONTH',
                    'billing_bracket': 'BILLING_BRACKET',
                    'monthly_amount': 'MONTHLY_AMOUNT',
                    'total_enrollments': 'TOTAL_COURSES_ENROLLED',
                    'home_enrollments': 'HOME_COURSES_COUNT',
                    'non_home_enrollments': 'NON_HOME_COURSES_COUNT',
                    'billing_description': 'BILLING_CATEGORY_DESCRIPTION',
                    'enrolled_courses': 'ENROLLED_COURSES',
                    'member_role': 'MEMBER_ROLE',
                    'member_status': 'MEMBER_STATUS'
                }
            },
            'silver': {
                'schema': 'GOLD',  # Using Gold schema where Silver tables are created
                'table': 'SV_ENROLLMENTS',
                'join_tables': {
                    'members': 'OLYMPUS_ANALYTICS.GOLD.SV_MEMBERS',
                    'courses': 'OLYMPUS_ANALYTICS.GOLD.SV_COURSES'
                },
                'is_aggregated': True
            },
            'bronze': {
                'schema': 'BRONZE',
                'table': 'DISCO_ENROLLMENTS',
                'join_tables': {
                    'members': 'OLYMPUS_ANALYTICS.BRONZE.DISCO_USERS',
                    'courses': 'OLYMPUS_ANALYTICS.BRONZE.DISCO_COURSES'
                },
                'is_aggregated': True
            }
        }
    
    def set_data_layer(self, layer: str):
        """Set the data layer to query from (gold, silver, bronze)"""
        if layer.lower() in self.layer_config:
            self.data_layer = layer.lower()
        else:
            raise ValueError(f"Invalid data layer: {layer}. Must be one of: gold, silver, bronze")
        return self
    
    def get_billing_data(
        self, 
        billing_month: Optional[str] = None,
        community_id: Optional[str] = None,
        billing_bracket: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Retrieve billing bracket data from selected Snowflake layer.
        
        Args:
            billing_month: Filter by specific billing month (YYYY-MM format)
            community_id: Filter by specific community/group
            billing_bracket: Filter by specific billing bracket ($0, $10, $50)
            
        Returns:
            DataFrame with billing data
        """
        
        config = self.layer_config[self.data_layer]
        
        if self.data_layer == 'gold':
            # Use the comprehensive Gold enrollment details table
            cols = config['columns']
            base_query = f"""
            SELECT 
                {cols['member_id']} as MEMBER_ID,
                {cols['email']} as EMAIL,
                {cols['member_name']} as MEMBER_NAME,
                {cols['first_name']} as FIRST_NAME,
                {cols['last_name']} as LAST_NAME,
                {cols['community_id']} as COMMUNITY_ID,
                {cols['group_name']} as GROUP_NAME,
                {cols['company_name']} as COMPANY_NAME,
                {cols['billing_month']} as BILLING_MONTH,
                {cols['total_enrollments']} as TOTAL_COURSES_ENROLLED,
                {cols['total_enrollments']} as COURSE_COUNT_ACTIVE,
                CASE WHEN {cols['home_enrollments']} > 0 THEN TRUE ELSE FALSE END as HAS_HOME_COURSE,
                {cols['billing_bracket']} as BILLING_BRACKET,
                {cols['monthly_amount']} as MONTHLY_AMOUNT,
                {cols['enrolled_courses']} as ENROLLED_COURSES,
                {cols['billing_description']} as BILLING_CATEGORY_DESCRIPTION,
                {cols['member_role']} as MEMBER_ROLE,
                {cols['member_status']} as MEMBER_STATUS,
                CONCAT({cols['member_id']}, '_', {cols['billing_month']}) as BILLING_RECORD_KEY
            FROM OLYMPUS_ANALYTICS.{config['schema']}.{config['table']}
            WHERE 1=1
            """
        else:
            # For Silver and Bronze layers, build billing data from enrollments
            if self.data_layer == 'bronze':
                # Bronze layer uses different column names
                base_query = f"""
                WITH member_enrollments AS (
                    SELECT 
                        e.USER_ID as MEMBER_ID,
                        m.EMAIL,
                        CONCAT(m.FIRST_NAME, ' ', m.LAST_NAME) as MEMBER_NAME,
                        'DEFAULT' as COMMUNITY_ID,
                        'Default Community' as GROUP_NAME,
                        DATE_TRUNC('MONTH', e.ENROLLMENT_DATE) as BILLING_MONTH,
                        COUNT(DISTINCT e.COURSE_ID) as COURSE_COUNT_ACTIVE,
                        CASE WHEN COUNT(DISTINCT e.COURSE_ID) > 0 THEN TRUE ELSE FALSE END as HAS_HOME_COURSE,
                        LISTAGG(DISTINCT c.COURSE_NAME, ', ') as ENROLLED_COURSES,
                        COUNT(DISTINCT e.COURSE_ID) as TOTAL_ENROLLMENTS
                    FROM OLYMPUS_ANALYTICS.{config['schema']}.{config['table']} e
                    LEFT JOIN {config['join_tables']['members']} m ON e.USER_ID = m.USER_ID
                    LEFT JOIN {config['join_tables']['courses']} c ON e.COURSE_ID = c.COURSE_ID
                    GROUP BY e.USER_ID, m.EMAIL, m.FIRST_NAME, m.LAST_NAME, DATE_TRUNC('MONTH', e.ENROLLMENT_DATE)
                 )
                 SELECT 
                     MEMBER_ID,
                     EMAIL,
                     MEMBER_NAME,
                     COMMUNITY_ID,
                     GROUP_NAME,
                     BILLING_MONTH,
                     COURSE_COUNT_ACTIVE,
                     HAS_HOME_COURSE,
                     CASE 
                         WHEN TOTAL_ENROLLMENTS = 0 THEN '$0'
                         WHEN TOTAL_ENROLLMENTS <= 3 THEN '$10'
                         ELSE '$50'
                     END as BILLING_BRACKET,
                     CASE 
                         WHEN TOTAL_ENROLLMENTS = 0 THEN 0
                         WHEN TOTAL_ENROLLMENTS <= 3 THEN 10
                         ELSE 50
                     END as MONTHLY_AMOUNT,
                     ENROLLED_COURSES,
                     '{self.data_layer.title()} Layer Data' as BILLING_CATEGORY_DESCRIPTION,
                     CONCAT(MEMBER_ID, '-', BILLING_MONTH) as BILLING_RECORD_KEY
                 FROM member_enrollments
                 WHERE 1=1
                 """
            else:
                 # Silver layer uses Silver tables with correct column names
                 base_query = f"""
                 WITH member_enrollments AS (
                     SELECT 
                         e.MEMBER_ID,
                         m.EMAIL,
                         CONCAT(m.FIRST_NAME, ' ', m.LAST_NAME) as MEMBER_NAME,
                         m.COMMUNITY_ID,
                         'Community ' || m.COMMUNITY_ID as GROUP_NAME,
                         DATE_TRUNC('MONTH', e.ENROLLED_AT) as BILLING_MONTH,
                         COUNT(DISTINCT e.COURSE_ID) as COURSE_COUNT_ACTIVE,
                         CASE WHEN COUNT(DISTINCT e.COURSE_ID) > 0 THEN TRUE ELSE FALSE END as HAS_HOME_COURSE,
                         LISTAGG(DISTINCT c.COURSE_NAME, ', ') as ENROLLED_COURSES,
                         COUNT(DISTINCT e.COURSE_ID) as TOTAL_ENROLLMENTS
                     FROM OLYMPUS_ANALYTICS.{config['schema']}.{config['table']} e
                     LEFT JOIN {config['join_tables']['members']} m ON e.MEMBER_ID = m.MEMBER_ID
                     LEFT JOIN {config['join_tables']['courses']} c ON e.COURSE_ID = c.COURSE_ID
                     GROUP BY e.MEMBER_ID, m.EMAIL, m.FIRST_NAME, m.LAST_NAME, m.COMMUNITY_ID, DATE_TRUNC('MONTH', e.ENROLLED_AT)
                 )
                 SELECT 
                     MEMBER_ID,
                     EMAIL,
                     MEMBER_NAME,
                     COMMUNITY_ID,
                     GROUP_NAME,
                     BILLING_MONTH,
                     COURSE_COUNT_ACTIVE,
                     HAS_HOME_COURSE,
                     CASE 
                         WHEN TOTAL_ENROLLMENTS = 0 THEN '$0'
                         WHEN TOTAL_ENROLLMENTS <= 3 THEN '$10'
                         ELSE '$50'
                     END as BILLING_BRACKET,
                     CASE 
                         WHEN TOTAL_ENROLLMENTS = 0 THEN 0
                         WHEN TOTAL_ENROLLMENTS <= 3 THEN 10
                         ELSE 50
                     END as MONTHLY_AMOUNT,
                     ENROLLED_COURSES,
                     '{self.data_layer.title()} Layer Data' as BILLING_CATEGORY_DESCRIPTION,
                     CONCAT(MEMBER_ID, '-', BILLING_MONTH) as BILLING_RECORD_KEY
                 FROM member_enrollments
                 WHERE 1=1
                  """
        
        conditions = []
        params = {}
        
        if billing_month:
            if self.data_layer == 'gold':
                conditions.append("AND billing_month = %(billing_month)s")
                params['billing_month'] = billing_month
            else:
                # For Silver and Bronze layers, compare with DATE_TRUNC result
                conditions.append("AND TO_VARCHAR(BILLING_MONTH, 'YYYY-MM') = %(billing_month)s")
                params['billing_month'] = billing_month
        
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
            conditions.append("AND BILLING_MONTH = %(billing_month)s")
            params['billing_month'] = billing_month
        
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
        Get list of available billing months from the selected data layer.
        
        Returns:
            List of available billing months in YYYY-MM format
        """
        
        config = self.layer_config[self.data_layer]
        
        if self.data_layer == 'gold':
            query = f"""
            SELECT DISTINCT 
                BILLING_MONTH
            FROM OLYMPUS_ANALYTICS.{config['schema']}.{config['table']}
            ORDER BY BILLING_MONTH DESC
            """
        else:
            # For Silver and Bronze layers, use appropriate date column
            date_column = 'ENROLLED_AT' if self.data_layer == 'silver' else 'ENROLLMENT_DATE'
            query = f"""
            SELECT DISTINCT 
                TO_VARCHAR(DATE_TRUNC('MONTH', {date_column}), 'YYYY-MM') as BILLING_MONTH
            FROM OLYMPUS_ANALYTICS.{config['schema']}.{config['table']}
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
        Get list of available communities/groups from the selected data layer.
        
        Returns:
            DataFrame with community information
        """
        
        config = self.layer_config[self.data_layer]
        
        if self.data_layer == 'gold':
            query = f"""
            SELECT DISTINCT 
                COMMUNITY_ID,
                GROUP_NAME,
                COUNT(DISTINCT MEMBER_ID) as MEMBER_COUNT
            FROM OLYMPUS_ANALYTICS.{config['schema']}.{config['table']}
            GROUP BY COMMUNITY_ID, GROUP_NAME
            ORDER BY GROUP_NAME
            """
        else:
            if self.data_layer == 'bronze':
                # Bronze layer doesn't have COMMUNITY_ID, return default community
                query = f"""
                SELECT DISTINCT 
                    'DEFAULT' as COMMUNITY_ID,
                    'Default Community' as GROUP_NAME,
                    COUNT(DISTINCT USER_ID) as MEMBER_COUNT
                FROM OLYMPUS_ANALYTICS.{config['schema']}.{config['table']}
                GROUP BY 'DEFAULT', 'Default Community'
                """
            else:
                # Silver layer
                query = f"""
                SELECT DISTINCT 
                    m.COMMUNITY_ID,
                    'Community ' || m.COMMUNITY_ID as GROUP_NAME,
                    COUNT(DISTINCT e.MEMBER_ID) as MEMBER_COUNT
                FROM OLYMPUS_ANALYTICS.{config['schema']}.{config['table']} e
                LEFT JOIN {config['join_tables']['members']} m ON e.MEMBER_ID = m.MEMBER_ID
                GROUP BY m.COMMUNITY_ID
                ORDER BY m.COMMUNITY_ID
                """
        
        try:
            df = self.snowflake_conn.execute_query(query)
            return df
        except Exception as e:
            st.error(f"Error retrieving available communities: {str(e)}")
            return pd.DataFrame()