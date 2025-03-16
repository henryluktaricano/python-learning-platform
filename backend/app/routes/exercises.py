"""
API routes for exercises.
"""
from fastapi import APIRouter, Request, HTTPException
from typing import List, Dict, Any, Optional

from ..utils.file_utils import (
    get_exercises_for_topic,
    get_exercises_for_chapter,
    get_exercise_by_id
)

router = APIRouter()

@router.get("/exercises/topics/{topic_id}", name="get_exercises_by_topic")
async def get_topic_exercises(request: Request, topic_id: str) -> List[Dict[str, Any]]:
    """
    Get all exercises for a specific topic.
    """
    exercises = get_exercises_for_topic(topic_id)
    if not exercises:
        print(f"No exercises found for topic: {topic_id}")
    return exercises

@router.get("/v1/exercises/topics/{topic_id}", name="get_exercises_by_topic_v1")
async def get_topic_exercises_v1(request: Request, topic_id: str) -> List[Dict[str, Any]]:
    """
    Compatibility route for v1 API.
    """
    return await get_topic_exercises(request, topic_id)

@router.get("/exercises/topic/direct/{topic_id}", name="get_topic_direct")
async def get_topic_direct(request: Request, topic_id: str) -> List[Dict[str, Any]]:
    """
    Direct access to topic exercises (alternative endpoint).
    """
    return await get_topic_exercises(request, topic_id)

@router.get("/exercises/chapter/{chapter_id}", name="get_exercises_by_chapter")
async def get_chapter_exercises(request: Request, chapter_id: str) -> List[Dict[str, Any]]:
    """
    Get all exercises for a specific chapter.
    """
    exercises = get_exercises_for_chapter(chapter_id)
    if not exercises:
        print(f"No exercises found for chapter: {chapter_id}")
    return exercises

@router.get("/exercises/exercise/{exercise_id}", name="get_exercise")
async def get_exercise(request: Request, exercise_id: str) -> Dict[str, Any]:
    """
    Get a specific exercise by ID.
    """
    exercise = get_exercise_by_id(exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail=f"Exercise not found: {exercise_id}")
    return exercise

@router.get("/exercises/raw/{path:path}", name="get_raw_exercise")
async def get_raw_exercise(request: Request, path: str) -> Dict[str, Any]:
    """
    Get exercises by raw path.
    """
    # Extract topic or chapter from path
    parts = path.split('/')
    if len(parts) >= 2:
        chapter_id = parts[0]
        topic_id = parts[1].replace('.json', '')
        
        # Try to get exercises for this topic
        exercises = get_exercises_for_topic(topic_id)
        if exercises:
            return exercises
            
        # If not found, try to get exercises for the chapter
        exercises = get_exercises_for_chapter(chapter_id)
        if exercises:
            return exercises
    
    # Fallback to empty list
    return []

@router.get("/exercises", name="get_all_exercises")
async def get_all_exercises(request: Request) -> List[Dict[str, Any]]:
    """
    Get a sample list of exercises (placeholder).
    """
    # This is a placeholder - would be too much to return all exercises
    return [
        {
            "id": "sample_001",
            "title": "Sample Exercise",
            "description": "This is a sample exercise. Use the topic-specific endpoints to get real exercises.",
            "instructions": "Browse topics to find actual exercises",
            "difficulty": "beginner"
        }
    ]

@router.get("", name="root_get_all_exercises")
@router.get("/", name="root_get_all_exercises_slash")
async def root_get_all_exercises(request: Request) -> List[Dict[str, Any]]:
    """
    Root endpoint returning sample exercises.
    """
    return await get_all_exercises(request)

@router.post("/execute", name="execute_code")
async def execute_code(request: Request, code_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute Python code (stub implementation).
    """
    # This is a placeholder - in a real implementation, this would execute code in a sandbox
    code = code_data.get("code", "")
    return {
        "success": True,
        "output": f"Code execution result would appear here.\nCode length: {len(code)} characters",
        "error": None
    } 