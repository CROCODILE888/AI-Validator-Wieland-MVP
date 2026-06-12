"""
Databricks connection and query execution.
"""

import os
import pandas as pd
from dotenv import load_dotenv

try:
    from databricks import sql
except ImportError:
    sql = None

load_dotenv()


def get_connection():
    """Create and return a Databricks SQL connection."""
    if sql is None:
        raise ImportError("databricks-sql-connector is not installed. Run: pip install databricks-sql-connector")
    
    host = os.getenv("DATABRICKS_HOST")
    token = os.getenv("DATABRICKS_TOKEN")
    http_path = os.getenv("DATABRICKS_HTTP_PATH")
    
    if not all([host, token, http_path]):
        raise ValueError("Missing required Databricks environment variables. Please check .env file.")
    
    connection = sql.connect(
        server_hostname=host,
        http_path=http_path,
        access_token=token
    )
    return connection


def run_query(sql_query: str) -> pd.DataFrame:
    """
    Execute a SQL query against Databricks and return results as a DataFrame.
    
    Args:
        sql_query: The SQL query to execute
        
    Returns:
        pandas DataFrame with query results
        
    Raises:
        Exception: If connection fails or query errors
    """
    connection = None
    cursor = None
    
    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        cursor.execute(sql_query)
        
        # Get column names
        columns = [desc[0] for desc in cursor.description]
        
        # Fetch all results
        results = cursor.fetchall()
        
        # Convert to DataFrame
        df = pd.DataFrame(results, columns=columns)
        
        return df
        
    except Exception as e:
        raise Exception(f"Databricks query failed: {str(e)}")
        
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
