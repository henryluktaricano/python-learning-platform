import sqlite3
import os
import json
from typing import List, Dict, Any
from datetime import datetime

# Database file path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "database", "feedback.db")

# Ensure database directory exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

async def init_db():
    """Initialize the database with required tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create feedback table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exercise_id TEXT NOT NULL,
        code TEXT NOT NULL,
        feedback TEXT NOT NULL,
        timestamp TEXT NOT NULL
    )
    ''')
    
    conn.commit()
    conn.close()

async def save_feedback_to_db(
    exercise_id: str,
    code: str,
    feedback: Dict[str, Any]
) -> int:
    """
    Save feedback to the database.
    
    Args:
        exercise_id: Identifier for the exercise
        code: User's submitted code
        feedback: Feedback from the AI
    
    Returns:
        ID of the inserted record
    """
    # Ensure database is initialized
    await init_db()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    timestamp = datetime.now().isoformat()
    feedback_json = json.dumps(feedback)
    
    cursor.execute(
        '''
        INSERT INTO feedback
        (exercise_id, code, feedback, timestamp)
        VALUES (?, ?, ?, ?)
        ''',
        (exercise_id, code, feedback_json, timestamp)
    )
    
    # Get the ID of the inserted record
    feedback_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    
    return feedback_id

async def get_feedback_from_db(exercise_id: str) -> List[Dict[str, Any]]:
    """
    Get all feedback for a specific exercise.
    
    Args:
        exercise_id: Identifier for the exercise
    
    Returns:
        List of feedback records
    """
    # Ensure database is initialized
    await init_db()
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable row factory to get column names
    cursor = conn.cursor()
    
    cursor.execute(
        'SELECT * FROM feedback WHERE exercise_id = ? ORDER BY timestamp DESC',
        (exercise_id,)
    )
    rows = cursor.fetchall()
    
    # Convert rows to dictionaries and parse JSON feedback
    result = []
    for row in rows:
        record = dict(row)
        record['feedback'] = json.loads(record['feedback'])
        result.append(record)
    
    conn.close()
    
    return result 