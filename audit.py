"""
SQLite audit logging for query execution tracking.
"""

import sqlite3
import pandas as pd
from datetime import datetime
import os

DATABASE_FILE = "audit_log.db"


def init_db():
    """Initialize the audit log database and create table if not exists."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            user_name TEXT NOT NULL,
            user_input TEXT NOT NULL,
            generated_sql TEXT NOT NULL,
            rows_returned INTEGER NOT NULL,
            status TEXT NOT NULL,
            error_message TEXT
        )
    """)
    
    conn.commit()
    conn.close()


def log_query(user_name: str, user_input: str, generated_sql: str, 
              rows_returned: int, status: str, error_message: str = None):
    """
    Log a query execution to the audit database.
    
    Args:
        user_name: Name of the user running the query
        user_input: The original natural language input
        generated_sql: The translated SQL query
        rows_returned: Number of rows returned by the query
        status: 'success' or 'error'
        error_message: Error message if status is 'error'
    """
    # Initialize database on first run
    if not os.path.exists(DATABASE_FILE):
        init_db()
    else:
        init_db()  # Ensure table exists
    
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
        INSERT INTO audit_log (timestamp, user_name, user_input, generated_sql, 
                             rows_returned, status, error_message)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (timestamp, user_name, user_input, generated_sql, rows_returned, 
          status, error_message))
    
    conn.commit()
    conn.close()


def get_audit_log(limit: int = 20) -> pd.DataFrame:
    """
    Retrieve the audit log entries, most recent first.
    
    Args:
        limit: Maximum number of entries to return (default: 20)
        
    Returns:
        DataFrame with audit log entries
    """
    # Initialize database if needed
    if not os.path.exists(DATABASE_FILE):
        init_db()
    
    conn = sqlite3.connect(DATABASE_FILE)
    
    df = pd.read_sql_query(f"""
        SELECT id, timestamp, user_name, user_input, generated_sql, 
               rows_returned, status, error_message
        FROM audit_log
        ORDER BY timestamp DESC
        LIMIT {limit}
    """, conn)
    
    conn.close()
    
    return df


# Initialize database on module import
init_db()
