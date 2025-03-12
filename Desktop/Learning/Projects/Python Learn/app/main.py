from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Verify OpenAI API key is available
if not os.environ.get("OPENAI_API_KEY"):
    print("WARNING: OPENAI_API_KEY environment variable not set. AI-assisted features will not work.")

# Import routes
from app.routes import code_execution, exercises, notes, feedback, token_tracking

app = FastAPI(
    title="Python Learning Platform API",
    description="Backend API for the interactive Python learning platform",
    version="0.1.0"
)

# CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(code_execution.router, prefix="/api", tags=["Code Execution"])
app.include_router(exercises.router, prefix="/api", tags=["Exercises"])
app.include_router(notes.router, prefix="/api", tags=["Notes"])
app.include_router(feedback.router, prefix="/api", tags=["Feedback"])
app.include_router(token_tracking.router, prefix="/api", tags=["Token Tracking"])

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the Python Learning Platform API"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 