#!/usr/bin/env python3
"""
Script to run the Python Learning Platform backend server.
"""
import os
import sys
import uvicorn
from dotenv import load_dotenv

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Load environment variables
load_dotenv()

# Get the port from environment variables or use default
port = int(os.getenv("PORT", "8000"))

if __name__ == "__main__":
    print(f"Starting Python Learning Platform Backend on port {port}")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True) 