from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from ..database.token_db import save_token_usage, get_token_usage, get_total_tokens

router = APIRouter()

class TokenUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    model: str
    endpoint: Optional[str] = None

@router.post("/track_tokens")
async def track_tokens(token_usage: TokenUsage):
    """
    Record token usage from OpenAI API calls.
    """
    try:
        # Save token usage to database
        usage_id = await save_token_usage(
            prompt_tokens=token_usage.prompt_tokens,
            completion_tokens=token_usage.completion_tokens,
            total_tokens=token_usage.total_tokens,
            model=token_usage.model,
            endpoint=token_usage.endpoint
        )
        return {"id": usage_id, "message": "Token usage recorded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/token_usage")
async def get_token_usage_stats():
    """
    Get statistics about token usage.
    """
    try:
        # Get token usage from database
        usage_data = await get_token_usage()
        total = await get_total_tokens()
        
        return {
            "total_tokens": total,
            "usage_history": usage_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/token_usage/summary")
async def get_token_usage_summary():
    """
    Get a summary of token usage statistics.
    """
    try:
        # Get token usage from database
        usage_data = await get_token_usage()
        total = await get_total_tokens()
        
        # Calculate summary statistics
        model_usage = {}
        for entry in usage_data:
            model = entry.get("model", "unknown")
            if model not in model_usage:
                model_usage[model] = 0
            model_usage[model] += entry.get("total_tokens", 0)
            
        # Calculate rough cost estimate (approximate, not exact)
        # Pricing as of 2023 - this would need updates as OpenAI changes pricing
        cost_estimate = 0
        for model, tokens in model_usage.items():
            if "gpt-4" in model:
                # Approx $0.03 per 1K tokens for GPT-4
                cost_estimate += (tokens / 1000) * 0.03
            elif "gpt-3.5" in model:
                # Approx $0.002 per 1K tokens for GPT-3.5
                cost_estimate += (tokens / 1000) * 0.002
                
        return {
            "total_tokens": total,
            "model_breakdown": model_usage,
            "estimated_cost_usd": round(cost_estimate, 4)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 