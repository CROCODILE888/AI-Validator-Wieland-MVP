"""
Groq LLM for natural language to SQL translation.
"""

import os
import re
from dotenv import load_dotenv

try:
    from groq import Groq
except ImportError:
    Groq = None

from schema import SCHEMA_CONTEXT

load_dotenv()


def get_client():
    """Create and return a Groq client."""
    if Groq is None:
        raise ImportError("groq is not installed. Run: pip install groq")
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("Missing GROQ_API_KEY environment variable. Please check .env file.")
    
    return Groq(api_key=api_key)


def translate_to_sql(user_input: str) -> str:
    """
    Translate natural language input to SQL query using Groq LLM.
    
    Args:
        user_input: Plain English description of the validation request
        
    Returns:
        Generated SQL query (cleaned of markdown formatting)
        
    Raises:
        Exception: If LLM fails to generate valid SQL
    """
    client = get_client()
    
    system_prompt = f"""{SCHEMA_CONTEXT}

IMPORTANT INSTRUCTIONS:
1. Return ONLY valid SQL query, no explanation, no markdown code blocks, no backticks
2. Always target workspace.default.* tables (use fully qualified names like workspace.default.wieland_routing_ca03)
3. When comparing values between tables (e.g., worker counts), always include a human-readable status column:
   - Use 'MISMATCH' when values don't match
   - Use 'OK' when values match
4. Always LIMIT results to 500 rows maximum
5. Write clean, valid Databricks SQL syntax

Now translate this user request to SQL:"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0.1,
            max_tokens=1000
        )
        
        # Extract SQL from response
        sql_query = response.choices[0].message.content.strip()
        
        # Clean up markdown formatting
        sql_query = sql_query.strip()
        
        # Remove markdown code blocks (```sql or ```)
        sql_query = re.sub(r'^```sql\s*', '', sql_query, flags=re.IGNORECASE)
        sql_query = re.sub(r'^```\s*', '', sql_query)
        sql_query = re.sub(r'\s*```$', '', sql_query)
        
        # Remove any leading/trailing whitespace
        sql_query = sql_query.strip()
        
        # Validate that we have a SQL query (basic check)
        if not sql_query.upper().startswith(('SELECT', 'WITH', 'WITH ')):
            raise ValueError(f"Generated SQL does not appear to be a valid SELECT query: {sql_query[:100]}")
        
        return sql_query
        
    except Exception as e:
        raise Exception(f"LLM translation failed: {str(e)}")
