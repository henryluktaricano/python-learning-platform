import sqlite3
import os
import json
from typing import List, Dict, Any
from datetime import datetime

# Database file path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "database", "token_usage.db")

# Ensure database directory exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

async def init_db():
    """Initialize the database with required tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create token usage table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS token_usage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prompt_tokens INTEGER NOT NULL,
        completion_tokens INTEGER NOT NULL,
        total_tokens INTEGER NOT NULL,
        model TEXT NOT NULL,
        endpoint TEXT,
        timestamp TEXT NOT NULL
    )
    ''')
    
    conn.commit()
    conn.close()

async def save_token_usage(
    prompt_tokens: int,
    completion_tokens: int,
    total_tokens: int,
    model: str,
    endpoint: str = None
) -> int:
    """
    Save token usage to the database.
    
    Args:
        prompt_tokens: Number of tokens in the prompt
        completion_tokens: Number of tokens in the completion
        total_tokens: Total tokens used
        model: OpenAI model used
        endpoint: API endpoint that was called
    
    Returns:
        ID of the inserted record
    """
    # Ensure database is initialized
    await init_db()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    timestamp = datetime.now().isoformat()
    
    cursor.execute(
        '''
        INSERT INTO token_usage 
        (prompt_tokens, completion_tokens, total_tokens, model, endpoint, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
        ''',
        (prompt_tokens, completion_tokens, total_tokens, model, endpoint, timestamp)
    )
    
    # Get the ID of the inserted record
    usage_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    
    return usage_id

async def get_token_usage() -> List[Dict[str, Any]]:
    """
    Get all token usage records from the database.
    
    Returns:
        List of token usage records
    """
    # Ensure database is initialized
    await init_db()
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable row factory to get column names
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM token_usage ORDER BY timestamp DESC')
    rows = cursor.fetchall()
    
    # Convert rows to dictionaries
    result = [dict(row) for row in rows]
    
    conn.close()
    
    return result

async def get_total_tokens() -> int:
    """
    Get the total number of tokens used across all records.
    
    Returns:
        Total token count
    """
    # Ensure database is initialized
    await init_db()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT SUM(total_tokens) FROM token_usage')
    total = cursor.fetchone()[0] or 0
    
    conn.close()
    
    return total 