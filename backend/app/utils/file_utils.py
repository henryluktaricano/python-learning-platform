"""
Utilities for working with JSON exercise files.
"""
import os
import json
from typing import Dict, List, Any, Optional

from .mappings import ALL_TOPIC_MAPPINGS, CHAPTER_TITLES, TOPIC_TITLES
from .mappings import CHAPTER1_MAPPINGS, CHAPTER2_MAPPINGS, CHAPTER3_MAPPINGS, CHAPTER4_MAPPINGS

def load_json_file(file_path: str) -> Optional[List[Dict[str, Any]]]:
    """
    Load a JSON file and return the contents as a list of dictionaries.
    
    Args:
        file_path (str): Path to the JSON file
        
    Returns:
        Optional[List[Dict[str, Any]]]: The loaded JSON content or None if loading fails
    """
    try:
        if not os.path.exists(file_path):
            print(f"WARNING: File does not exist: {file_path}")
            return None
        
        with open(file_path, 'r') as f:
            data = json.load(f)
            print(f"Loaded {len(data)} exercises from {file_path}")
            return data
    except Exception as e:
        print(f"ERROR loading file {file_path}: {str(e)}")
        return None

def enrich_exercise_data(exercises: List[Dict[str, Any]], topic_id: str) -> List[Dict[str, Any]]:
    """
    Enrich exercise data with additional fields for better UI presentation.
    
    Args:
        exercises (List[Dict[str, Any]]): List of exercise dictionaries
        topic_id (str): ID of the topic these exercises belong to
        
    Returns:
        List[Dict[str, Any]]: Enriched exercise data
    """
    enriched_exercises = []
    
    for i, exercise in enumerate(exercises):
        # Create a copy of the exercise to avoid modifying the original
        enriched = dict(exercise)
        
        # Add ID if missing
        if "id" not in enriched:
            enriched["id"] = f"{topic_id}_{i+1:03d}"
            
        # Add title if missing (from exercise number if possible)
        if "title" not in enriched:
            if "exercise_number" in enriched:
                enriched["title"] = f"Exercise {enriched['exercise_number']}"
            else:
                enriched["title"] = f"Exercise {i+1}"
                
        # Add exercise number if missing
        if "exercise_number" not in enriched:
            enriched["exercise_number"] = i + 1
            
        # Add difficulty if missing
        if "difficulty" not in enriched:
            enriched["difficulty"] = "beginner"
            
        # Add topic information
        enriched["topic_id"] = topic_id
        enriched["topic_title"] = TOPIC_TITLES.get(topic_id, topic_id)
        
        # Extract chapter from file path
        file_path = ALL_TOPIC_MAPPINGS.get(topic_id, "")
        if file_path:
            # Extract chapter directory from path
            path_parts = file_path.split('/')
            for part in path_parts:
                if part.startswith("Chapter"):
                    enriched["chapter_id"] = part
                    enriched["chapter_title"] = CHAPTER_TITLES.get(part, part)
                    break
                    
        # Standardize/clean up fields
        if "exercise" in enriched and "description" not in enriched:
            enriched["description"] = enriched["exercise"]
            
        if "exercise" in enriched and "instructions" not in enriched:
            enriched["instructions"] = enriched["exercise"]
            
        if "notebook" in enriched and "file_name" not in enriched:
            enriched["file_name"] = enriched["notebook"]
            
        # Add a default starter code if missing
        if "starterCode" not in enriched:
            enriched["starterCode"] = "# Your code here\n\n"
            
        enriched_exercises.append(enriched)
        
    return enriched_exercises

def get_all_chapters() -> List[Dict[str, Any]]:
    """
    Get information about all chapters and their topics.
    
    Returns:
        List[Dict[str, Any]]: List of chapter dictionaries with their topics
    """
    chapters = []
    
    # Chapter 1
    chapter1_topics = []
    for topic_id in CHAPTER1_MAPPINGS.keys():
        chapter1_topics.append({
            "id": topic_id,
            "title": TOPIC_TITLES.get(topic_id, topic_id)
        })
    chapters.append({
        "id": "Chapter1_DataObjects",
        "title": CHAPTER_TITLES["Chapter1_DataObjects"],
        "topics": chapter1_topics
    })
    
    # Chapter 2
    chapter2_topics = []
    for topic_id in CHAPTER2_MAPPINGS.keys():
        chapter2_topics.append({
            "id": topic_id,
            "title": TOPIC_TITLES.get(topic_id, topic_id)
        })
    chapters.append({
        "id": "Chapter2_Operators",
        "title": CHAPTER_TITLES["Chapter2_Operators"],
        "topics": chapter2_topics
    })
    
    # Chapter 3
    chapter3_topics = []
    for topic_id in CHAPTER3_MAPPINGS.keys():
        chapter3_topics.append({
            "id": topic_id,
            "title": TOPIC_TITLES.get(topic_id, topic_id)
        })
    chapters.append({
        "id": "Chapter3_Statements",
        "title": CHAPTER_TITLES["Chapter3_Statements"],
        "topics": chapter3_topics
    })
    
    # Chapter 4
    chapter4_topics = []
    for topic_id in CHAPTER4_MAPPINGS.keys():
        chapter4_topics.append({
            "id": topic_id,
            "title": TOPIC_TITLES.get(topic_id, topic_id)
        })
    chapters.append({
        "id": "Chapter4_MethodsFunctions",
        "title": CHAPTER_TITLES["Chapter4_MethodsFunctions"],
        "topics": chapter4_topics
    })
    
    return chapters

def get_chapter_info(chapter_id: str) -> Optional[Dict[str, Any]]:
    """
    Get information about a specific chapter.
    
    Args:
        chapter_id (str): ID of the chapter
        
    Returns:
        Optional[Dict[str, Any]]: Chapter information or None if not found
    """
    chapters = get_all_chapters()
    for chapter in chapters:
        if chapter["id"] == chapter_id:
            return chapter
    return None

def get_exercises_for_topic(topic_id: str) -> List[Dict[str, Any]]:
    """
    Get all exercises for a specific topic.
    
    Args:
        topic_id (str): ID of the topic
        
    Returns:
        List[Dict[str, Any]]: List of exercise dictionaries
    """
    # Get the file path for this topic
    file_path = ALL_TOPIC_MAPPINGS.get(topic_id)
    if not file_path:
        print(f"ERROR: No mapping found for topic {topic_id}")
        return []
    
    # Load exercises from JSON file
    exercises = load_json_file(file_path)
    if not exercises:
        print(f"ERROR: Failed to load exercises for topic {topic_id}")
        return []
    
    # Enrich the exercise data
    return enrich_exercise_data(exercises, topic_id)

def get_exercises_for_chapter(chapter_id: str) -> List[Dict[str, Any]]:
    """
    Get all exercises for a specific chapter.
    
    Args:
        chapter_id (str): ID of the chapter
        
    Returns:
        List[Dict[str, Any]]: List of exercise dictionaries
    """
    chapter = get_chapter_info(chapter_id)
    if not chapter:
        return []
    
    all_exercises = []
    for topic in chapter["topics"]:
        topic_exercises = get_exercises_for_topic(topic["id"])
        all_exercises.extend(topic_exercises)
    
    return all_exercises

def get_exercise_by_id(exercise_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a specific exercise by ID.
    
    Args:
        exercise_id (str): ID of the exercise
        
    Returns:
        Optional[Dict[str, Any]]: Exercise data or None if not found
    """
    # Try to extract topic ID from exercise ID
    parts = exercise_id.split('_')
    if len(parts) >= 2 and parts[-1].isdigit():
        topic_id = '_'.join(parts[:-1])
        topic_exercises = get_exercises_for_topic(topic_id)
        
        for exercise in topic_exercises:
            if exercise.get("id") == exercise_id:
                return exercise
    
    # If not found by topic extraction, search all chapters
    for chapter_id in CHAPTER_TITLES.keys():
        chapter_exercises = get_exercises_for_chapter(chapter_id)
        for exercise in chapter_exercises:
            if exercise.get("id") == exercise_id or str(exercise.get("exercise_number")) == exercise_id:
                return exercise
    
    return None 