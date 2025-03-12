from fastapi import APIRouter, HTTPException
import json
import os
from typing import Dict, Any, List

router = APIRouter()

# Directory where exercise JSON files are stored
EXERCISES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "python-learning-platform", "exercises")

@router.get("/exercises/index")
async def get_exercise_index():
    """
    Get the index of all available exercises.
    """
    try:
        index_path = os.path.join(EXERCISES_DIR, "index.json")
        with open(index_path, "r") as f:
            index_data = json.load(f)
        return index_data
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Exercise index not found")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON in exercise index")

@router.get("/exercises/{exercise_file}")
async def get_exercise(exercise_file: str):
    """
    Get the details of a specific exercise from its JSON file.
    """
    try:
        # Ensure the filename has a .json extension
        if not exercise_file.endswith('.json'):
            exercise_file += '.json'
            
        # Prevent path traversal attacks
        if '..' in exercise_file or '/' in exercise_file:
            raise HTTPException(status_code=400, detail="Invalid exercise file")
            
        exercise_path = os.path.join(EXERCISES_DIR, exercise_file)
        with open(exercise_path, "r") as f:
            exercise_data = json.load(f)
        return exercise_data
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Exercise {exercise_file} not found")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail=f"Invalid JSON in exercise {exercise_file}")

@router.get("/exercises/chapter/{chapter_number}")
async def get_chapter_exercises(chapter_number: str):
    """
    Get all exercises for a specific chapter.
    """
    try:
        index_path = os.path.join(EXERCISES_DIR, "index.json")
        with open(index_path, "r") as f:
            index_data = json.load(f)
            
        chapter_key = f"chapter{chapter_number}"
        if chapter_key not in index_data:
            raise HTTPException(status_code=404, detail=f"Chapter {chapter_number} not found")
            
        chapter_data = index_data[chapter_key]
        
        # Get all exercise files for the chapter
        exercises = []
        for notebook in chapter_data.get("notebooks", {}).values():
            exercise_files = notebook.get("exercises", [])
            if isinstance(exercise_files, str):
                exercise_files = [exercise_files]
                
            for ex_file in exercise_files:
                exercise_path = os.path.join(EXERCISES_DIR, ex_file)
                if os.path.exists(exercise_path):
                    with open(exercise_path, "r") as f:
                        exercise_data = json.load(f)
                        exercises.append(exercise_data)
        
        return {"chapter": chapter_data["title"], "exercises": exercises}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Exercise index not found")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON in exercise files") 