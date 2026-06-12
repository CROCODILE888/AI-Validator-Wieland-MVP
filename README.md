# DataDoctor - Master Data Validation

A Streamlit proof-of-concept application for Wieland Group that allows non-technical business users to validate SAP master data stored in Databricks using plain English — no SQL or coding required.

## Project Structure

```
wieland-mvp/
├── app.py              # Main Streamlit application
├── db.py               # Databricks connection and query execution
├── llm.py              # Groq LLM for NL to SQL translation
├── audit.py            # SQLite audit logging
├── notifier.py         # Email notifications
├── schema.py           # Table schema definitions for LLM context
├── requirements.txt    # Python dependencies
├── .gitignore         # Git ignore patterns
├── .env               # Environment variables (create your own)
└── venv/              # Virtual environment (do not commit)
```

## Prerequisites

- Python 3.10 or higher
- Valid Databricks credentials
- Groq API key
- Gmail account for email notifications

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd wieland-mvp
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv

# macOS/Linux
python3 -m venv venv
```

### 3. Activate Virtual Environment
```bash
# Windows (Command Prompt)
venv\Scripts\activate

# Windows (PowerShell)
venv\Scripts\Activate.ps1

# macOS/Linux
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Databricks Configuration
DATABRICKS_HOST=your_databricks_host
DATABRICKS_TOKEN=your_databricks_token
DATABRICKS_HTTP_path=/sql/1.0/warehouses/your_warehouse_id

# Groq LLM Configuration
GROQ_API_KEY=your_groq_api_key

# Email Configuration (Gmail)
EMAIL_SENDER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_RECEIVER=recipient_email@gmail.com
```

**Note:** For Gmail, you need to use an App Password, not your regular password. Generate one at: https://myaccount.google.com/apppasswords

### 6. Run the Application
```bash
streamlit run app.py
```

The app will open in your browser at: http://localhost:8501

## Features

- **Plain English Queries**: Describe your validation needs in natural language
- **Automatic SQL Generation**: Groq LLM translates your requests to SQL
- **Databricks Integration**: Query SAP master data directly from Databricks
- **Visual Results**: Color-coded results (red for MISMATCH, green for OK)
- **Email Notifications**: Send results via email (optional)
- **Audit Logging**: Full audit trail of all queries and results

## Example Queries

1. "Show all routing operations where the number of workers in SAP does not match the machine master"
2. "List all workstations in workshop Z1-3 with their SAP worker count and expected worker count"
3. "Show operations where SAP has 0 workers assigned"

## Troubleshooting

### Databricks Connection Issues
- Verify your DATABRICKS_TOKEN is valid
- Ensure the SQL Warehouse is running in Databricks
- Check that the HTTP path is correct

### Email Not Sending
- For Gmail, ensure you're using an App Password
- Enable 2-Factor Authentication on your Google account
- Check that EMAIL_SENDER matches your Gmail address

### LLM Errors
- Verify GROQ_API_KEY is correct
- Check your Groq account has available credits

## Security Notes

- Never commit the `.env` file to version control
- The `.gitignore` file already excludes `.env` and `audit_log.db`
- Review and rotate API keys periodically
