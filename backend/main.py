from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
import importlib.util
import logging
from typing import Dict, Any, List, Optional

# Add parent directory to path to allow importing from app directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Python Learning Platform API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create a simple monitor module
class Monitor:
    def register_heartbeat(self):
        return {"status": "ok"}
    
    def shutdown_server(self):
        return {"status": "ok"}

monitor = Monitor()

# Monitor endpoints for browser connection tracking
@app.get("/api/monitor/heartbeat")
def heartbeat():
    """Register a heartbeat from the client to track browser connection"""
    return monitor.register_heartbeat()

@app.get("/api/monitor/shutdown")
def shutdown():
    """Shutdown the server (triggered when browser closed)"""
    return monitor.shutdown_server()

# Root endpoint
@app.get("/")
def read_root():
    """Root endpoint that returns basic API information"""
    return {
        "name": "Python Learning Platform API",
        "version": "1.0.0",
        "description": "API for the Python Learning Platform"
    }

# Health check endpoint
@app.get("/api/health")
def health_check():
    """Health check endpoint to verify the API is running"""
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
