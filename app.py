"""
DataDoctor - Master Data Validation
Streamlit application for Wieland Group
Proof-of-concept for validating SAP master data using natural language
"""

import streamlit as st
import os
import pandas as pd
from datetime import datetime
import traceback

# Import local modules
import llm
import db
import audit
import notifier
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    layout="wide",
    page_title="DataDoctor",
    page_icon="🩺"
)

# Example queries for quick start
EXAMPLE_QUERIES = [
    "Show all routing operations where the number of workers in SAP does not match the machine master",
    "List all workstations in workshop Z1-3 with their SAP worker count and expected worker count",
    "Show operations where SAP has 0 workers assigned"
]


def main():
    # ============================================
    # SIDEBAR
    # ============================================
    st.sidebar.title("🩺 DataDoctor")
    st.sidebar.markdown("### Master Data Validation")
    
    # User configuration
    user_name = st.sidebar.text_input("User Name", value="Data Manager")
    enable_email = st.sidebar.checkbox("Enable Email Notifications", value=False)
    
    user_email = None
    if enable_email:
        default_email = os.getenv("EMAIL_RECEIVER", "")
        user_email = st.sidebar.text_input("Email Address", value=default_email)
    
    st.sidebar.divider()
    
    # Audit Log expander in sidebar
    with st.sidebar.expander("📋 Audit Log (Last 20)", expanded=False):
        try:
            audit_df = audit.get_audit_log(20)
            if not audit_df.empty:
                # Show a subset of columns for display
                display_cols = ['timestamp', 'user_name', 'rows_returned', 'status']
                st.dataframe(audit_df[display_cols], hide_index=True, use_container_width=True)
            else:
                st.info("No audit entries yet.")
        except Exception as e:
            st.warning(f"Could not load audit log: {e}")
    
    # ============================================
    # MAIN AREA
    # ============================================
    st.title("🏭 Wieland Master Data Validation")
    st.markdown("""
    Validate your SAP master data using plain English — no SQL or coding required.
    Simply describe what you want to check, and DataDoctor will generate the query and execute it against Databricks.
    """)
    
    st.divider()
    
    # Example queries section
    st.subheader("💡 Example Queries")
    st.markdown("Click an example to populate the input field:")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Find worker count mismatches", use_container_width=True):
            st.session_state['query_input'] = EXAMPLE_QUERIES[0]
    with col2:
        if st.button("Workstations in Z1-3", use_container_width=True):
            st.session_state['query_input'] = EXAMPLE_QUERIES[1]
    with col3:
        if st.button("Operations with 0 workers", use_container_width=True):
            st.session_state['query_input'] = EXAMPLE_QUERIES[2]
    
    st.divider()
    
    # Main input area
    st.subheader("🔍 Run Your Validation")
    
    # Initialize session state for query input
    if 'query_input' not in st.session_state:
        st.session_state['query_input'] = ""
    
    user_query = st.text_area(
        "Describe your validation in plain English:",
        value=st.session_state.get('query_input', ''),
        height=100,
        placeholder="e.g., Show all routing operations where the number of workers in SAP does not match the machine master"
    )
    
    # Clear the session state after using it
    if user_query and st.session_state.get('query_input'):
        st.session_state['query_input'] = ""
    
    # Run button
    if st.button("▶️ Run Validation", type="primary", use_container_width=True):
        if not user_query.strip():
            st.error("Please enter a validation request.")
            return
        
        # Clear previous results
        if 'results_df' in st.session_state:
            del st.session_state['results_df']
        if 'generated_sql' in st.session_state:
            del st.session_state['generated_sql']
        
        # ============================================
        # STEP 1: Translate to SQL
        # ============================================
        with st.spinner("🔄 Translating your request to SQL..."):
            try:
                generated_sql = llm.translate_to_sql(user_query)
                st.session_state['generated_sql'] = generated_sql
            except Exception as e:
                error_msg = f"SQL Translation Error: {str(e)}"
                st.error(error_msg)
                # Log the error
                audit.log_query(
                    user_name=user_name,
                    user_input=user_query,
                    generated_sql="",
                    rows_returned=0,
                    status="error",
                    error_message=error_msg
                )
                return
        
        # Show generated SQL in expander
        with st.expander("📝 Generated SQL (click to inspect)", expanded=True):
            st.code(st.session_state['generated_sql'], language="sql")
        
        # ============================================
        # STEP 2: Execute Query
        # ============================================
        with st.spinner("⚡ Running validation against Databricks..."):
            try:
                results_df = db.run_query(st.session_state['generated_sql'])
                st.session_state['results_df'] = results_df
            except Exception as e:
                error_msg = f"Databricks Execution Error: {str(e)}"
                st.error(error_msg)
                st.markdown("""
                **Troubleshooting Tips:**
                - Verify Databricks credentials in .env file
                - Check that the SQL Warehouse is running
                - Ensure the tables exist in the workspace.default schema
                """)
                # Log the error
                audit.log_query(
                    user_name=user_name,
                    user_input=user_query,
                    generated_sql=st.session_state.get('generated_sql', ''),
                    rows_returned=0,
                    status="error",
                    error_message=error_msg
                )
                return
        
        # ============================================
        # STEP 3: Display Results
        # ============================================
        st.divider()
        st.subheader("📊 Validation Results")
        
        # Calculate metrics
        total_records = len(results_df)
        mismatch_count = 0
        has_status = 'status' in results_df.columns
        
        if has_status:
            mismatch_count = len(results_df[results_df['status'] == 'MISMATCH'])
        
        # Metrics row
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Total Records", total_records)
        with m2:
            if has_status:
                st.metric("Mismatches Found", mismatch_count, delta_color="inverse")
            else:
                st.metric("Records Returned", total_records)
        with m3:
            st.metric("Timestamp", datetime.now().strftime("%H:%M:%S"))
        
        # Display results with colored status
        if not results_df.empty:
            if has_status:
                # Create a styled dataframe with colors
                st.markdown("### Results Table")
                
                # Apply color styling based on status column
                def style_status_column(row):
                    if row['status'] == 'MISMATCH':
                        return ['background-color: #ffcccc; color: #cc0000'] * len(row)
                    elif row['status'] == 'OK':
                        return ['background-color: #ccffcc; color: #006600'] * len(row)
                    return [''] * len(row)
                
                styled_df = results_df.style.apply(style_status_column, axis=1)
                st.dataframe(styled_df, use_container_width=True, hide_index=True)
            else:
                st.dataframe(results_df, use_container_width=True, hide_index=True)
        else:
            st.info("No results returned from the query.")
        
        # ============================================
        # STEP 4: Send Email (if enabled)
        # ============================================
        email_sent = False
        if enable_email and user_email:
            try:
                with st.spinner("📧 Sending email notification..."):
                    notifier.send_results_email(
                        user_input=user_query,
                        sql=st.session_state['generated_sql'],
                        df_results=results_df,
                        user_email=user_email
                    )
                    email_sent = True
            except Exception as e:
                st.warning(f"⚠️ Email could not be sent: {str(e)}")
        
        # ============================================
        # STEP 5: Log to Audit
        # ============================================
        try:
            audit.log_query(
                user_name=user_name,
                user_input=user_query,
                generated_sql=st.session_state['generated_sql'],
                rows_returned=total_records,
                status="success",
                error_message=None
            )
        except Exception as e:
            st.warning(f"⚠️ Could not log to audit: {str(e)}")
        
        # ============================================
        # SUCCESS MESSAGE
        # ============================================
        st.success(f"✅ Validation completed successfully! {total_records} records processed.")
        if email_sent:
            st.info(f"📧 Results sent to: {user_email}")


if __name__ == "__main__":
    main()
