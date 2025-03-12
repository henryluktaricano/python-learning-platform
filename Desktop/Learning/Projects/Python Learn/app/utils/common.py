import os
import json
from typing import Dict, Any, List, Optional

def load_json_file(file_path: str) -> Dict[str, Any]:
    """
    Load and parse a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Parsed JSON content as a dictionary
    """
    with open(file_path, "r") as f:
        return json.load(f)

def get_exercise_path(exercise_id: str) -> str:
    """
    Get the full path to an exercise file.
    
    Args:
        exercise_id: Exercise identifier (filename without extension)
        
    Returns:
        Full path to the exercise JSON file
    """
    # Base directory for exercises
    exercises_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "exercises"
    )
    
    # Ensure the filename has a .json extension
    if not exercise_id.endswith('.json'):
        exercise_id += '.json'
        
    return os.path.join(exercises_dir, exercise_id)

def get_notebook_path(notebook_name: str) -> str:
    """
    Get the full path to a notebook file.
    
    Args:
        notebook_name: Notebook name (filename without extension)
        
    Returns:
        Full path to the notebook file
    """
    # Base directory for notebooks
    notebooks_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "notebooks"
    )
    
    # Ensure the filename has a .ipynb extension
    if not notebook_name.endswith('.ipynb'):
        notebook_name += '.ipynb'
        
    return os.path.join(notebooks_dir, notebook_name)

def find_exercise_by_id(exercise_id: str) -> Optional[Dict[str, Any]]:
    """
    Find an exercise by its ID from the index.
    
    Args:
        exercise_id: Exercise identifier
        
    Returns:
        Exercise data or None if not found
    """
    # Get the index
    index_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "exercises",
        "index.json"
    )
    
    try:
        index_data = load_json_file(index_path)
        
        # Search through all chapters and notebooks
        for chapter in index_data.values():
            if not isinstance(chapter, dict) or "notebooks" not in chapter:
                continue
                
            for notebook in chapter.get("notebooks", {}).values():
                if not isinstance(notebook, dict) or "exercises" not in notebook:
                    continue
                    
                exercises = notebook.get("exercises", [])
                if isinstance(exercises, str):
                    exercises = [exercises]
                    
                for ex_file in exercises:
                    if ex_file == exercise_id or ex_file == f"{exercise_id}.json":
                        # Found the exercise, load its data
                        exercise_path = get_exercise_path(ex_file)
                        return load_json_file(exercise_path)
        
        return None
    except (FileNotFoundError, json.JSONDecodeError):
        return None 