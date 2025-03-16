from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import os
import json
from datetime import datetime
import sqlite3
from ..services.openai_service import get_code_evaluation
from ..database.feedback_db import save_feedback_to_db, get_feedback_from_db

router = APIRouter()

class ExerciseFeedbackRequest(BaseModel):
    exercise_id: str
    code: str
    expected_output: Optional[str] = None
    question: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@router.post("/mark_exercise")
async def mark_exercise(request: ExerciseFeedbackRequest):
    """
    Submit user code to OpenAI for qualitative feedback and evaluation.
    """
    try:
        # Get AI evaluation from OpenAI
        feedback = await get_code_evaluation(
            code=request.code,
            exercise_id=request.exercise_id,
            expected_output=request.expected_output,
            question=request.question,
            metadata=request.metadata
        )
        
        # Save feedback to database for future reference
        feedback_id = await save_feedback_to_db(
            exercise_id=request.exercise_id,
            code=request.code,
            feedback=feedback
        )
        
        return {
            "id": feedback_id,
            "exercise_id": request.exercise_id,
            "feedback": feedback,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/feedback/{exercise_id}")
async def get_feedback(exercise_id: str):
    """
    Get all feedback history for a specific exercise.
    """
    try:
        feedback_history = await get_feedback_from_db(exercise_id)
        return {"exercise_id": exercise_id, "feedback_history": feedback_history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/feedback/{exercise_id}/{feedback_id}")
async def get_specific_feedback(exercise_id: str, feedback_id: int):
    """
    Get a specific feedback entry for an exercise.
    """
    try:
        feedback_history = await get_feedback_from_db(exercise_id)
        for feedback in feedback_history:
            if feedback.get("id") == feedback_id:
                return feedback
        raise HTTPException(status_code=404, detail=f"Feedback with ID {feedback_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 