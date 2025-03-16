"""
API routes for token usage tracking.
"""
from fastapi import APIRouter, Request
from typing import Dict, Any

router = APIRouter()

# Simple in-memory token usage storage
token_usage = {
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "total_tokens": 0,
    "requests": 0
}

@router.get("", name="get_token_usage")
async def get_token_usage(request: Request) -> Dict[str, Any]:
    """
    Get current token usage statistics.
    """
    return token_usage

@router.post("", name="update_token_usage")
async def update_token_usage(request: Request, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update token usage statistics.
    """
    if "prompt_tokens" in data:
        token_usage["prompt_tokens"] += data["prompt_tokens"]
    if "completion_tokens" in data:
        token_usage["completion_tokens"] += data["completion_tokens"]
    if "total_tokens" in data:
        token_usage["total_tokens"] += data["total_tokens"]
    
    token_usage["requests"] += 1
    
    return token_usage 