"""
Email notifications for validation results.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv

load_dotenv()


def send_results_email(user_input: str, sql: str, df_results: pd.DataFrame, 
                       user_email: str = None):
    """
    Send validation results via email.
    
    Args:
        user_input: The original validation request
        sql: The generated SQL query
        df_results: DataFrame with query results
        user_email: Optional specific email to send to (defaults to EMAIL_RECEIVER from env)
    """
    # Get email configuration
    sender_email = os.getenv("EMAIL_SENDER")
    sender_password = os.getenv("EMAIL_PASSWORD")
    receiver_email = user_email or os.getenv("EMAIL_RECEIVER")
    
    if not all([sender_email, sender_password, receiver_email]):
        raise ValueError("Missing email configuration. Please check .env file.")
    
    # Prepare timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Calculate summary statistics
    total_rows = len(df_results)
    mismatch_count = 0
    
    # Check for status column to count mismatches
    if 'status' in df_results.columns:
        mismatch_count = len(df_results[df_results['status'] == 'MISMATCH'])
    
    # Build HTML table from results
    if not df_results.empty:
        html_table = df_results.to_html(index=False, classes='dataframe')
    else:
        html_table = "<p>No results to display.</p>"
    
    # Build email body
    email_body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .summary {{ background-color: #f0f0f0; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
            .summary-item {{ margin: 5px 0; }}
            .dataframe {{ border-collapse: collapse; width: 100%; font-size: 12px; }}
            .dataframe th {{ background-color: #4CAF50; color: white; padding: 8px; text-align: left; }}
            .dataframe td {{ border: 1px solid #ddd; padding: 8px; }}
            .dataframe tr:nth-child(even) {{ background-color: #f2f2f2; }}
            .sql-block {{ background-color: #f5f5f5; padding: 10px; border-left: 4px solid #2196F3; margin-top: 20px; font-family: monospace; }}
            .mismatch {{ color: red; font-weight: bold; }}
            .ok {{ color: green; font-weight: bold; }}
        </style>
    </head>
    <body>
        <h2>DataDoctor Validation Results</h2>
        
        <div class="summary">
            <h3>Summary</h3>
            <div class="summary-item"><strong>Validation Request:</strong> {user_input}</div>
            <div class="summary-item"><strong>Timestamp:</strong> {timestamp}</div>
            <div class="summary-item"><strong>Total Records:</strong> {total_rows}</div>
            {"<div class='summary-item'><strong>Mismatches Found:</strong> " + str(mismatch_count) + "</div>" if 'status' in df_results.columns else ""}
        </div>
        
        <h3>Results</h3>
        {html_table}
        
        <div class="sql-block">
            <h4>Generated SQL:</h4>
            <pre>{sql}</pre>
        </div>
        
        <p style="color: #666; font-size: 12px; margin-top: 20px;">
            This is an automated message from DataDoctor - Master Data Validation.<br>
            Wieland Group Internal Use Only.
        </p>
    </body>
    </html>
    """
    
    # Create message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"DataDoctor Validation Results - {timestamp}"
    msg['From'] = sender_email
    msg['To'] = receiver_email
    
    # Attach HTML body
    html_part = MIMEText(email_body, 'html')
    msg.attach(html_part)
    
    # Send email
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        return True
        
    except Exception as e:
        raise Exception(f"Failed to send email: {str(e)}")
