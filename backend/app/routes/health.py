"""
Health check endpoint for the backend.
"""
from fastapi import APIRouter, Request

router = APIRouter()

@router.get("", name="health_check")
async def health_check(request: Request):
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": "python-learning-platform-backend"
    } 