import uvicorn
import asyncio
from app.database.token_db import init_db as init_token_db
from app.database.feedback_db import init_db as init_feedback_db

async def init_databases():
    """Initialize all databases."""
    await init_token_db()
    await init_feedback_db()
    print("Databases initialized successfully.")

if __name__ == "__main__":
    # Initialize databases
    asyncio.run(init_databases())
    
    # Run the FastAPI server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 