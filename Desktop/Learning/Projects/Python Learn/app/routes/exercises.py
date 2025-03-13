from fastapi import APIRouter, HTTPException, status, Query
import json
import os
import logging
from typing import Dict, Any, List, Optional, Union
import glob
import re


from app.string_methods_fix import fix_string_method_topic
# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Directory where exercise JSON files are stored
EXERCISES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "python-learning-platform", "exercises")

# Print the EXERCISES_DIR for debugging
logger.info(f"EXERCISES_DIR is set to: {EXERCISES_DIR}")

# Define the chapters directory
CHAPTERS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "python-learning-platform", "chapters")

@router.get("/exercises/index")
async def get_exercise_index():
    """
    Get the index of all available exercises.
    """
    try:
        index_path = os.path.join(EXERCISES_DIR, "index.json")
        
        # Check if the index file exists
        if os.path.exists(index_path):
            with open(index_path, "r") as f:
                try:
                    index_data = json.load(f)
                    return index_data
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON in exercise index: {str(e)}")
                    # If index file is invalid, we'll generate it dynamically below
        
        # If index file doesn't exist or is invalid, generate it dynamically
        logger.info("Generating exercise index dynamically")
        
        # Get all chapter directories
        chapter_dirs = [d for d in os.listdir(EXERCISES_DIR) 
                       if os.path.isdir(os.path.join(EXERCISES_DIR, d)) and d.startswith("Chapter")]
        
        # Create a dynamic index
        dynamic_index = {}
        
        for chapter_dir in chapter_dirs:
            # Format chapter name for display
            chapter_name = chapter_dir.replace("_", " ")
            
            # Extract chapter number if present
            chapter_num = ''.join(filter(str.isdigit, chapter_dir.split("_")[0]))
            chapter_title = f"Chapter {chapter_num}"
            
            # Get chapter description from the rest of the name
            if "_" in chapter_dir:
                topic = chapter_dir.split("_", 1)[1]
                chapter_title = f"Chapter {chapter_num}: {topic.replace('_', ' ')}"
            
            # Find exercise files in this chapter directory
            exercise_files = glob.glob(os.path.join(EXERCISES_DIR, chapter_dir, "*.json"))
            
            if exercise_files:
                exercise_file = os.path.basename(exercise_files[0])
                
                # Add to dynamic index
                dynamic_index[chapter_dir] = {
                    "title": chapter_title,
                    "description": f"Python exercises for {chapter_title}",
                    "exercises": exercise_file
                }
        
        # Write the generated index to file for future use
        try:
            with open(index_path, 'w') as f:
                json.dump(dynamic_index, f, indent=2)
        except Exception as e:
            logger.error(f"Error writing index file: {str(e)}")
        
        return dynamic_index
            
    except Exception as e:
        logger.error(f"Unexpected error in get_exercise_index: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.get("/exercises/{exercise_file}")
async def get_exercise(exercise_file: str):
    """
    Get a specific exercise by filename.
    """
    try:
        # First check if the exercise filename includes chapter directory
        if "/" in exercise_file:
            parts = exercise_file.split("/")
            if len(parts) == 2:
                chapter_id, exercise_id = parts
                
                # Check for file extension
                if not exercise_id.endswith('.json'):
                    exercise_id += '.json'
                
                # Try to find in chapter directory
                exercise_path = os.path.join(EXERCISES_DIR, chapter_id, exercise_id)
                if os.path.exists(exercise_path):
                    with open(exercise_path, 'r') as f:
                        exercise_data = json.load(f)
                    
                    # If it's an array of exercises, find the requested one by ID or number
                    if isinstance(exercise_data, list):
                        # Extract the exercise number or ID from the filename if present
                        exercise_num = None
                        if '_' in exercise_id:
                            try:
                                exercise_num = int(''.join(filter(str.isdigit, exercise_id.split('_')[0])))
                            except:
                                pass
                        
                        # Try to find the specific exercise by number or simply return the first one
                        if exercise_num is not None:
                            for ex in exercise_data:
                                if "exercise_number" in ex and ex["exercise_number"] == exercise_num:
                                    return ex
                        
                        # If no specific exercise found, return the first one
                        if exercise_data:
                            return exercise_data[0]
                    
                    # If it's a single exercise, return it directly
                    return exercise_data
        
        # If not found as chapter/exercise, check the new chapter-based structure
        index_data = await get_exercise_index()
        
        # Search in all chapters
        for chapter_id, chapter_info in index_data.items():
            exercise_filename = chapter_info.get("exercises")
            if exercise_filename:
                exercise_path = os.path.join(EXERCISES_DIR, chapter_id, exercise_filename)
                
                if os.path.exists(exercise_path):
                    with open(exercise_path, 'r') as f:
                        exercises_data = json.load(f)
                    
                    # If we're looking for this specific file
                    if exercise_file == exercise_filename or exercise_file + ".json" == exercise_filename:
                        return exercises_data
                    
                    # Otherwise look for a specific exercise by source_file
                    if isinstance(exercises_data, list):
                        for ex in exercises_data:
                            if "source_file" in ex and (ex["source_file"] == exercise_file or ex["source_file"] == exercise_file + ".json"):
                                return ex
                            
                            # Also try by exercise ID or number
                            exercise_id = None
                            try:
                                exercise_id = int(''.join(filter(str.isdigit, exercise_file.split('_')[0])))
                            except:
                                pass
                                
                            if exercise_id is not None and "exercise_number" in ex and ex["exercise_number"] == exercise_id:
                                return ex
        
        # If still not found, check the backup directory
        backup_dir = os.path.join(EXERCISES_DIR, "original_files_backup")
        if os.path.exists(backup_dir):
            # Ensure the filename has .json extension
            if not exercise_file.endswith('.json'):
                exercise_file += '.json'
                
            backup_path = os.path.join(backup_dir, exercise_file)
            if os.path.exists(backup_path):
                with open(backup_path, 'r') as f:
                    return json.load(f)
        
        # If exercise still not found, return 404
        raise HTTPException(status_code=404, detail=f"Exercise {exercise_file} not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving exercise {exercise_file}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving exercise {exercise_file}: {str(e)}")

@router.get("/exercises/chapter/{chapter_id}")
async def get_chapter(chapter_id: str):
    """
    Get all exercises for a specific chapter.
    """
    try:
        # Get the index to find the chapter
        index_data = await get_exercise_index()
        
        # Check if the chapter exists in the index
        if chapter_id not in index_data:
            raise HTTPException(status_code=404, detail=f"Chapter {chapter_id} not found")
        
        chapter_data = index_data[chapter_id]
        
        # Get the exercise file for this chapter
        exercise_file = chapter_data.get("exercises")
        if not exercise_file:
            raise HTTPException(status_code=404, detail=f"No exercises found for chapter {chapter_id}")
        
        # Load the exercises
        exercise_path = os.path.join(EXERCISES_DIR, chapter_id, exercise_file)
        if not os.path.exists(exercise_path):
            raise HTTPException(status_code=404, detail=f"Exercise file {exercise_file} not found")
        
        with open(exercise_path, 'r') as f:
            try:
                exercises = json.load(f)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in exercise file {exercise_file}: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Invalid JSON in exercise file {exercise_file}")
        
        # Add exercises to chapter data
        chapter_data["exercises_data"] = exercises
        
        return chapter_data
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving chapter {chapter_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving chapter {chapter_id}: {str(e)}")

@router.get("/exercises/list/chapters")
async def list_chapters():
    """
    List all available chapters.
    """
    try:
        # Get all chapter files
        chapter_files = glob.glob(os.path.join(CHAPTERS_DIR, "*.json"))
        
        # If no dedicated chapter files, look in exercises directory
        if not chapter_files:
            chapter_files = glob.glob(os.path.join(EXERCISES_DIR, "*.json"))
        
        chapters = []
        for file in chapter_files:
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                
                chapter_id = os.path.basename(file).replace('.json', '')
                
                # If it's a chapter file
                if isinstance(data, dict) and ('title' in data or 'description' in data):
                    chapters.append({
                        "id": chapter_id,
                        "title": data.get('title', chapter_id.replace('_', ' ').title()),
                        "description": data.get('description', 'Python exercises')
                    })
            except:
                # Skip files that can't be parsed
                continue
        
        # If no chapters found, create a default one
        if not chapters:
            chapters.append({
                "id": "python_basics",
                "title": "Python Basics",
                "description": "Introduction to Python programming"
            })
        
        return chapters
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing chapters: {str(e)}")

@router.get("/exercises/list/exercises")
async def list_exercises(
    chapter: Optional[str] = None,
    difficulty: Optional[str] = None,
    topic: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500)
):
    """
    List all available exercises with optional filtering.
    """
    try:
        exercise_files = glob.glob(os.path.join(EXERCISES_DIR, "*.json"))
        exercise_files = [f for f in exercise_files if os.path.basename(f) != "index.json"]
        
        exercises = []
        for file in exercise_files:
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                
                file_id = os.path.basename(file).replace('.json', '')
                
                # Process the exercise data
                if isinstance(data, list):
                    # If it's a list of exercises
                    for idx, ex in enumerate(data):
                        # Determine the chapter ID
                        ex_chapter_id = None
                        if 'chapter_id' in ex:
                            ex_chapter_id = ex['chapter_id']
                        elif 'chapter_index' in ex:
                            # Try to extract chapter number from chapter_index
                            if 'chapter' in file_id.lower():
                                parts = file_id.split('_')
                                if parts[0].startswith('chapter'):
                                    ex_chapter_id = parts[0]
                        
                        # If we still don't have a chapter_id, try to extract from filename
                        if not ex_chapter_id and 'chapter' in file_id.lower():
                            parts = file_id.split('_')
                            if parts[0].startswith('chapter'):
                                ex_chapter_id = parts[0]
                        
                        # If no chapter_id found, default to chapter1
                        if not ex_chapter_id:
                            ex_chapter_id = 'chapter1'
                        
                        # Check if this exercise matches the requested chapter
                        if chapter is None or ex_chapter_id == chapter or (
                            chapter and ex_chapter_id and 
                            (chapter.lower() in ex_chapter_id.lower() or ex_chapter_id.lower() in chapter.lower())
                        ):
                            exercises.append({
                                "id": f"{file_id}#{idx+1}",
                                "title": ex.get('title', f"Exercise {idx+1}"),
                                "chapter_id": ex_chapter_id,
                                "difficulty": ex.get('difficulty', 'medium')
                            })
                elif isinstance(data, dict):
                    # If it's a single exercise
                    # Determine the chapter ID
                    ex_chapter_id = data.get('chapter_id', None)
                    if not ex_chapter_id and 'chapter_index' in data:
                        # Try to extract chapter number from chapter_index
                        if 'chapter' in file_id.lower():
                            parts = file_id.split('_')
                            if parts[0].startswith('chapter'):
                                ex_chapter_id = parts[0]
                    
                    # If we still don't have a chapter_id, try to extract from filename
                    if not ex_chapter_id and 'chapter' in file_id.lower():
                        parts = file_id.split('_')
                        if parts[0].startswith('chapter'):
                            ex_chapter_id = parts[0]
                    
                    # If no chapter_id found, default to chapter1
                    if not ex_chapter_id:
                        ex_chapter_id = 'chapter1'
                    
                    # Check if this exercise matches the requested chapter
                    if chapter is None or ex_chapter_id == chapter or (
                        chapter and ex_chapter_id and 
                        (chapter.lower() in ex_chapter_id.lower() or ex_chapter_id.lower() in chapter.lower())
                    ):
                        exercises.append({
                            "id": file_id,
                            "title": data.get('title', "Exercise"),
                            "chapter_id": ex_chapter_id,
                            "difficulty": data.get('difficulty', 'medium')
                        })
            except Exception as e:
                logger.error(f"Error processing file {file}: {str(e)}")
                continue
        
        return exercises
    except Exception as e:
        logger.error(f"Error listing exercises: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing exercises: {str(e)}")

@router.get("/exercises/topic/{topic_name}")
async def get_topic_exercises(topic_name: str, chapter_id: Optional[str] = None):
    """
    Get all exercises for a specific topic, optionally filtered by chapter.
    
    Args:
        topic_name: The topic name (from notebook/file name)
        chapter_id: Optional chapter ID to filter by
    """
    try:
        # Find all exercise files that match this topic
        exercise_files = glob.glob(os.path.join(EXERCISES_DIR, "*.json"))
        matching_files = []
        
        for file_path in exercise_files:
            file_name = os.path.basename(file_path)
            # Skip the index file
            if file_name == "index.json":
                continue
                
            # Check if the file name contains the topic
            if topic_name.lower() in file_name.lower():
                # Extract file's chapter id if needed for filtering
                file_chapter_id = None
                if chapter_id:
                    if file_name.startswith("chapter"):
                        # Extract chapter number from filename
                        parts = file_name.split('_', 1)
                        if len(parts) > 0:
                            file_chapter_id = parts[0]
                
                # Add file if no chapter filter or if chapter matches
                if not chapter_id or (file_chapter_id and file_chapter_id.lower() == chapter_id.lower()):
                    matching_files.append(file_path)
        
        # If no matching files, return empty list
        if not matching_files:
            return {"topic": topic_name, "exercises": []}
        
        # Process each matching file to extract exercises
        topic_exercises = []
        
        for file_path in matching_files:
            try:
                with open(file_path, 'r') as f:
                    file_data = json.load(f)
                
                file_name = os.path.basename(file_path)
                file_id = file_name.replace('.json', '')
                
                # Handle different file formats
                if isinstance(file_data, list):
                    # For list of exercises
                    for idx, exercise in enumerate(file_data):
                        exercise_id = f"{file_id}_{idx+1}"
                        # Copy exercise data and add metadata
                        exercise_copy = exercise.copy()
                        exercise_copy["id"] = exercise_id
                        exercise_copy["file_name"] = file_name
                        # Extract chapter ID
                        if "chapter_id" not in exercise_copy:
                            if file_name.startswith("chapter"):
                                chapter_part = file_name.split('_', 1)[0]
                                exercise_copy["chapter_id"] = chapter_part
                        topic_exercises.append(exercise_copy)
                elif isinstance(file_data, dict):
                    # For single exercise
                    exercise_copy = file_data.copy()
                    exercise_copy["id"] = file_id
                    exercise_copy["file_name"] = file_name
                    # Extract chapter ID
                    if "chapter_id" not in exercise_copy:
                        if file_name.startswith("chapter"):
                            chapter_part = file_name.split('_', 1)[0]
                            exercise_copy["chapter_id"] = chapter_part
                    topic_exercises.append(exercise_copy)
            except Exception as e:
                logger.error(f"Error processing topic file {file_path}: {str(e)}")
                continue
        
        # Sort exercises by exercise_number if available
        topic_exercises.sort(key=lambda x: x.get("exercise_number", 999))
        
        return {
            "topic": topic_name,
            "exercises": topic_exercises,
            "total": len(topic_exercises)
        }
    
    except Exception as e:
        logger.error(f"Error retrieving topic exercises: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving topic exercises: {str(e)}")

@router.get("/exercises/list/reorganized-chapters")
async def list_reorganized_chapters():
    """
    List all reorganized chapter directories with their topics.
    This endpoint specifically looks in the exercises directory for Chapter* folders.
    """
    try:
        # Find all chapter directories starting with "Chapter"
        chapter_dirs = []
        if os.path.exists(EXERCISES_DIR):
            chapter_dirs = [d for d in os.listdir(EXERCISES_DIR) 
                           if os.path.isdir(os.path.join(EXERCISES_DIR, d)) and d.startswith("Chapter")]
        
        # If no directories found, return empty list
        if not chapter_dirs:
            return []
        
        # Process each chapter directory
        chapters = []
        for chapter_dir in chapter_dirs:
            # Parse chapter info from directory name
            chapter_id = chapter_dir
            chapter_num = ''.join(filter(str.isdigit, chapter_dir.split("_")[0]))
            
            # Generate chapter title
            if "_" in chapter_dir:
                topic = chapter_dir.split("_", 1)[1]
                chapter_title = f"Chapter {chapter_num}: {topic.replace('_', ' ')}"
            else:
                chapter_title = f"Chapter {chapter_num}"
            
            # Look for exercise files in this chapter directory
            chapter_path = os.path.join(EXERCISES_DIR, chapter_dir)
            exercise_files = glob.glob(os.path.join(chapter_path, "*.json"))
            
            # Skip directories without exercise files
            if not exercise_files:
                continue
            
            # Group files by topic based on numeric prefix
            topic_groups = {}
            for file_path in exercise_files:
                file_name = os.path.basename(file_path)
                
                # Skip backup directory and any files we shouldn't process
                if "backup" in file_name or file_name.startswith("chapter") or file_name.endswith("_exercises.json"):
                    continue
                
                # Extract topic information
                topic_match = file_name.split('.')[0]  # Remove extension
                
                # Parse the numeric prefix if it exists
                prefix_match = topic_match.split('_')[0] if '_' in topic_match else None
                if prefix_match and prefix_match.isdigit():
                    topic_num = prefix_match
                    topic_name = '_'.join(topic_match.split('_')[1:])
                else:
                    topic_num = "00"
                    topic_name = topic_match
                
                # Format topic name for display
                display_name = topic_name.replace('_', ' ').title()
                
                # Count exercises in the file
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    
                    if isinstance(data, list):
                        exercise_count = len(data)
                    elif isinstance(data, dict) and "exercises" in data and isinstance(data["exercises"], list):
                        exercise_count = len(data["exercises"])
                    else:
                        exercise_count = 1
                except Exception as e:
                    logger.error(f"Error reading file {file_path}: {str(e)}")
                    exercise_count = 0
                
                # Add to topic groups
                if topic_num not in topic_groups:
                    topic_groups[topic_num] = {
                        "id": f"{topic_num}_{topic_name}",
                        "title": display_name,
                        "files": [file_name],
                        "exerciseCount": exercise_count
                    }
                else:
                    topic_groups[topic_num]["files"].append(file_name)
                    topic_groups[topic_num]["exerciseCount"] += exercise_count
            
            # Convert topic groups to list and sort by number
            topics = [topic_data for _, topic_data in sorted(topic_groups.items())]
            
            # Special case to add missing Strings Part1 and Part2 topics if in Chapter1_DataObjects
            if chapter_dir == "Chapter1_DataObjects":
                # Check if we need to add a combined Strings entry and remove part1/part2 entries
                combined_strings_exists = any(topic.get('id') == "04_strings" for topic in topics)
                string_concatenation_exists = any(topic.get('id') == "05_string_concatenation" for topic in topics)
                
                # First remove individual parts
                topics = [topic for topic in topics if topic.get('id') not in ["04_strings_part1", "04_strings_part2"]]
                logger.info(f"Removed individual Strings Part1 and Part2 topics")
                
                # Fix incorrect exercise counts for specific topics
                for topic in topics:
                    # Fix String Immutability count - should be 20 instead of 100
                    if topic.get('id') == "05_string_immutability":
                        topic['exerciseCount'] = 20
                        logger.info(f"Fixed String Immutability exercise count to 20")
                    
                    # Fix String Formatting count - should be 60 instead of 100
                    if topic.get('id') == "06_string_formatting":
                        topic['exerciseCount'] = 60
                        logger.info(f"Fixed String Formatting exercise count to 60")
                
                # Extract String Methods topics (capitalize, lower, split, upper)
                # Get the String Immutability topic to extract method files from it
                string_immutability_topic = next((t for t in topics if t.get('id') == "05_string_immutability"), None)
                
                if string_immutability_topic:
                    # Define the method files we want to extract
                    method_files = {
                        "05_string_methods_capitalize.json": "String Methods Capitalize",
                        "05_string_methods_lower.json": "String Methods Lower",
                        "05_string_methods_split.json": "String Methods Split",
                        "05_string_methods_upper.json": "String Methods Upper"
                    }
                    
                    # Save the original files list before modifying it
                    original_files = string_immutability_topic.get('files', []).copy()
                    
                    # Create a filtered list of files that should remain in String Immutability
                    string_immutability_topic['files'] = [
                        f for f in string_immutability_topic.get('files', []) 
                        if f not in method_files and f != "05_string_concatenation.json"
                    ]
                    
                    # Find the position to insert method topics
                    string_immutability_index = next((i for i, t in enumerate(topics) if t.get('id') == "05_string_immutability"), None)
                    insert_position = string_immutability_index + 1 if string_immutability_index is not None else 0
                    
                    # Create and insert each method topic
                    for method_file, method_title in method_files.items():
                        # Only add if the file was in the original immutability topic's files
                        if method_file in original_files:
                            method_id = method_file.split('.')[0]  # Remove .json extension
                            method_topic = {
                                "id": method_id,
                                "title": method_title,
                                "files": [method_file],
                                "exerciseCount": 20  # Each method file has 20 exercises
                            }
                            
                            # Insert this method topic after String Immutability
                            topics.insert(insert_position, method_topic)
                            insert_position += 1  # Increment position for next insert
                            logger.info(f"Added {method_title} topic at position {insert_position}")
                
                # Extract String Concatenation as a separate topic
                if not string_concatenation_exists:
                    # First, find the String Immutability topic
                    for topic in topics:
                        if topic.get('id') == "05_string_immutability":
                            # Check if string_concatenation.json is in its files
                            if "05_string_concatenation.json" in topic.get('files', []):
                                # Create a new topic for String Concatenation
                                string_concatenation_topic = {
                                    "id": "05_string_concatenation",
                                    "title": "String Concatenation",
                                    "files": ["05_string_concatenation.json"],
                                    "exerciseCount": 20
                                }
                                
                                # Remove the file from String Immutability topic
                                topic['files'] = [f for f in topic['files'] if f != "05_string_concatenation.json"]
                                
                                # Adjust the exercise count for String Immutability
                                if topic.get('exerciseCount', 0) > 20:
                                    topic['exerciseCount'] = topic.get('exerciseCount', 120) - 20
                                
                                # Find where to insert - after String Immutability
                                string_immutability_index = next((i for i, t in enumerate(topics) if t.get('id') == "05_string_immutability"), None)
                                if string_immutability_index is not None:
                                    topics.insert(string_immutability_index + 1, string_concatenation_topic)
                                    logger.info(f"Added String Concatenation topic after String Immutability")
                                else:
                                    # Insert after Strings
                                    strings_index = next((i for i, t in enumerate(topics) if t.get('id') == "04_strings"), None)
                                    if strings_index is not None:
                                        topics.insert(strings_index + 1, string_concatenation_topic)
                                        logger.info(f"Added String Concatenation topic after Strings")
                                    else:
                                        topics.append(string_concatenation_topic)
                                        logger.info(f"Added String Concatenation topic at the end of list")
                                break
                
                # Then add the combined entry if it doesn't exist
                if not combined_strings_exists:
                    combined_strings_topic = {
                        "id": "04_strings",
                        "title": "Strings",
                        "files": ["04_strings_part1.json", "04_strings_part2.json"],
                        "exerciseCount": 70
                    }
                    
                    # Find where to insert - after variables (03)
                    strings_index = next((i for i, topic in enumerate(topics) if topic['id'].startswith('05_')), None)
                    if strings_index is not None:
                        topics.insert(strings_index, combined_strings_topic)
                        logger.info(f"Added combined Strings topic at index {strings_index}")
                    else:
                        # Try to insert after variables
                        variables_index = next((i for i, topic in enumerate(topics) if topic['id'].startswith('03_')), None)
                        if variables_index is not None:
                            topics.insert(variables_index + 1, combined_strings_topic)
                            logger.info(f"Added combined Strings topic after Variables")
                        else:
                            topics.append(combined_strings_topic)
                            logger.info(f"Added combined Strings topic at the end of list")
                
                logger.info(f"Current topics: {[t['title'] for t in topics]}")
            
            # Create chapter info
            chapter_info = {
                "id": chapter_id,
                "title": chapter_title.split(": ", 1)[1] if ": " in chapter_title else chapter_title,
                "number": int(chapter_num),
                "description": f"Python exercises for {chapter_title}",
                "topics": topics
            }
            
            chapters.append(chapter_info)
        
        # Sort chapters by number
        chapters.sort(key=lambda x: x["number"])
        
        return chapters
    
    except Exception as e:
        logger.error(f"Error listing reorganized chapters: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing reorganized chapters: {str(e)}")

@router.get("/exercises/object_types")
async def get_object_types():
    """
    Get exercises for object types.
    """
    try:
        # Try to load from JSON file first
        object_types_file = os.path.join(EXERCISES_DIR, "Chapter1_DataObjects", "01_object_types.json")
        logger.info(f"Attempting to load object types exercises from: {object_types_file}")
        
        if os.path.exists(object_types_file):
            with open(object_types_file, 'r') as f:
                try:
                    data = json.load(f)
                    logger.info(f"Successfully loaded JSON data from {object_types_file}, found {len(data) if isinstance(data, list) else 1} entries")
                    
                    # Process exercises to ensure they have required fields
                    processed_exercises = []
                    if isinstance(data, list):
                        for ex in data:
                            # Ensure each exercise has id, title, and chapter_id
                            ex_id = ex.get("id", f"object_types_{len(processed_exercises) + 1}")
                            ex_title = ex.get("title", f"Object Types Exercise {len(processed_exercises) + 1}")
                            ex_difficulty = ex.get("difficulty", "beginner")
                            ex_chapter_id = ex.get("chapter_id", "Chapter1_DataObjects")
                            
                            ex["id"] = ex_id
                            ex["title"] = ex_title
                            ex["difficulty"] = ex_difficulty
                            ex["chapter_id"] = ex_chapter_id
                            
                            processed_exercises.append(ex)
                    elif isinstance(data, dict):
                        # Single exercise
                        ex_id = data.get("id", "object_types_1")
                        ex_title = data.get("title", "Object Types Exercise")
                        ex_difficulty = data.get("difficulty", "beginner")
                        ex_chapter_id = data.get("chapter_id", "Chapter1_DataObjects")
                        
                        data["id"] = ex_id
                        data["title"] = ex_title
                        data["difficulty"] = ex_difficulty
                        data["chapter_id"] = ex_chapter_id
                        
                        processed_exercises.append(data)
                    
                    logger.info(f"Returning {len(processed_exercises)} processed object types exercises")
                    
                    # Return mock exercises as well if no exercises were processed
                    if not processed_exercises:
                        logger.warning("No valid exercises found in file, adding mock exercises")
                        processed_exercises = get_mock_object_types_exercises()
                    
                    return processed_exercises
                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing JSON from {object_types_file}: {str(e)}")
        else:
            logger.warning(f"Object types file not found at: {object_types_file}")
        
        # Try to find an alternative file
        pattern = os.path.join(EXERCISES_DIR, "Chapter1_DataObjects", "*object*type*.json")
        alternative_files = glob.glob(pattern)
        
        if alternative_files:
            alternative_file = alternative_files[0]
            logger.info(f"Found alternative object types file: {alternative_file}")
            
            try:
                with open(alternative_file, 'r') as f:
                    data = json.load(f)
                    
                    processed_exercises = []
                    if isinstance(data, list):
                        for ex in data:
                            # Process each exercise
                            ex_id = ex.get("id", f"object_types_{len(processed_exercises) + 1}")
                            ex_title = ex.get("title", f"Object Types Exercise {len(processed_exercises) + 1}")
                            ex_difficulty = ex.get("difficulty", "beginner")
                            ex_chapter_id = ex.get("chapter_id", "Chapter1_DataObjects")
                            
                            ex["id"] = ex_id
                            ex["title"] = ex_title
                            ex["difficulty"] = ex_difficulty
                            ex["chapter_id"] = ex_chapter_id
                            
                            processed_exercises.append(ex)
                    elif isinstance(data, dict):
                        # Single exercise
                        ex_id = data.get("id", "object_types_1")
                        ex_title = data.get("title", "Object Types Exercise")
                        ex_difficulty = data.get("difficulty", "beginner")
                        ex_chapter_id = data.get("chapter_id", "Chapter1_DataObjects")
                        
                        data["id"] = ex_id
                        data["title"] = ex_title
                        data["difficulty"] = ex_difficulty
                        data["chapter_id"] = ex_chapter_id
                        
                        processed_exercises.append(data)
                    
                    logger.info(f"Returning {len(processed_exercises)} object types exercises from alternative file")
                    
                    # Return mock exercises as well if no exercises were processed
                    if not processed_exercises:
                        logger.warning("No valid exercises found in alternative file, adding mock exercises")
                        processed_exercises = get_mock_object_types_exercises()
                    
                    return processed_exercises
            except Exception as e:
                logger.error(f"Error reading alternative file {alternative_file}: {str(e)}")
        
        # If we get here, file not found or invalid
        logger.info("Returning mock object types exercises")
        return get_mock_object_types_exercises()
    except Exception as e:
        logger.error(f"Error fetching object types exercises: {str(e)}")
        return get_mock_object_types_exercises()

def get_mock_object_types_exercises():
    """Helper function to return mock object types exercises."""
    return [
        {
            "id": "object_types_1",
            "title": "Python Object Types (Integers)",
            "difficulty": "beginner",
            "chapter_id": "Chapter1_DataObjects",
            "description": "Learn about Python's fundamental data types.",
            "instructions": "Experiment with Python's integer type. Try arithmetic operations with integers.",
            "starterCode": "# Integer operations\na = 5\nb = 10\n\n# Addition\nprint(a + b)  # 15\n\n# Subtraction\nprint(b - a)  # 5\n\n# Multiplication\nprint(a * b)  # 50\n\n# Division (returns float)\nprint(b / a)  # 2.0\n\n# Integer division (returns integer)\nprint(b // a)  # 2\n\n# Modulo (remainder)\nprint(b % a)  # 0\n\n# Exponentiation\nprint(a ** 2)  # 25"
        },
        {
            "id": "object_types_2",
            "title": "Python Object Types (Floats)",
            "difficulty": "beginner",
            "chapter_id": "Chapter1_DataObjects",
            "description": "Learn about Python's floating-point numbers.",
            "instructions": "Experiment with Python's float type. Observe the precision of floating-point arithmetic.",
            "starterCode": "# Float operations\nx = 3.14\ny = 2.5\n\nprint(x + y)  # 5.64\nprint(x - y)  # 0.64\nprint(x * y)  # 7.85\nprint(x / y)  # 1.256\n\n# Floating point precision\nprint(0.1 + 0.2)  # 0.30000000000000004\nprint(0.1 + 0.2 == 0.3)  # False\n\n# Using round to handle precision issues\nprint(round(0.1 + 0.2, 1) == 0.3)  # True"
        },
        {
            "id": "object_types_3",
            "title": "Python Object Types (Strings)",
            "difficulty": "beginner",
            "chapter_id": "Chapter1_DataObjects",
            "description": "Learn about Python's string type.",
            "instructions": "Experiment with Python's string type and common string operations.",
            "starterCode": "# String operations\nname = \"Python\"\n\n# Length of string\nprint(len(name))  # 6\n\n# Accessing characters (indexing)\nprint(name[0])  # 'P'\nprint(name[-1])  # 'n'\n\n# Slicing\nprint(name[0:2])  # 'Py'\nprint(name[2:])  # 'thon'\n\n# Concatenation\nprint(name + \" Programming\")  # 'Python Programming'\n\n# Repetition\nprint(name * 3)  # 'PythonPythonPython'\n\n# Methods\nprint(name.upper())  # 'PYTHON'\nprint(name.lower())  # 'python'\nprint(\"  whitespace  \".strip())  # 'whitespace'"
        }
    ]

@router.get("/exercises/topic/direct/{topic_id}")
async def get_topic_direct(topic_id: str):
    """
    Get exercises for a specific topic directly by searching for matching files.
    """
    try:

        # Check for string method topics
        string_method_result = fix_string_method_topic(topic_id)
        if string_method_result:
            return string_method_result
    
        logger.info(f"Getting exercises for topic: {topic_id}")
        
        # Special case handlers
        if topic_id.lower() == "object_types" or topic_id.lower() == "01_object_types":
            # Use the dedicated object_types endpoint
            result = await get_object_types()
            logger.info(f"Retrieved {len(result) if isinstance(result, list) else 'unknown'} object types exercises from dedicated endpoint")
            return result
        
        # Special case for string methods capitalize
        if topic_id.lower() == "string_methods_capitalize" or topic_id.lower() == "05_string_methods_capitalize":
            logger.info("Using direct handler for string_methods_capitalize")
            chapter_dir = os.path.join(EXERCISES_DIR, "Chapter1_DataObjects")
            file_path = os.path.join(chapter_dir, "05_string_methods_capitalize.json")
            
            if os.path.exists(file_path):
                logger.info(f"Found string_methods_capitalize file at: {file_path}")
                with open(file_path, 'r') as f:
                    try:
                        exercises = json.load(f)
                        logger.info(f"Loaded {len(exercises) if isinstance(exercises, list) else 1} string_methods_capitalize exercises")
                        
                        # Process exercises to ensure they have required fields
                        processed_exercises = []
                        if isinstance(exercises, list):
                            for ex in exercises:
                                # Ensure each exercise has id, title, and chapter_id
                                ex_id = ex.get("id", f"string_methods_capitalize_{len(processed_exercises) + 1}")
                                ex_title = ex.get("title", f"String Methods Capitalize Exercise {len(processed_exercises) + 1}")
                                ex_difficulty = ex.get("difficulty", "beginner")
                                ex_chapter_id = ex.get("chapter_id", "Chapter1_DataObjects")
                                
                                ex["id"] = ex_id
                                ex["title"] = ex_title
                                ex["difficulty"] = ex_difficulty
                                ex["chapter_id"] = ex_chapter_id
                                
                                processed_exercises.append(ex)
                        elif isinstance(exercises, dict):
                            # Single exercise
                            ex_id = exercises.get("id", "string_methods_capitalize_1")
                            ex_title = exercises.get("title", "String Methods Capitalize Exercise")
                            ex_difficulty = exercises.get("difficulty", "beginner")
                            ex_chapter_id = exercises.get("chapter_id", "Chapter1_DataObjects")
                            
                            exercises["id"] = ex_id
                            exercises["title"] = ex_title
                            exercises["difficulty"] = ex_difficulty
                            exercises["chapter_id"] = ex_chapter_id
                            
                            processed_exercises.append(exercises)
                        
                        logger.info(f"Returning {len(processed_exercises)} string_methods_capitalize exercises")
                        return processed_exercises
                    except json.JSONDecodeError as e:
                        logger.error(f"Error parsing JSON from {file_path}: {str(e)}")
                    except Exception as e:
                        logger.error(f"Unexpected error processing {file_path}: {str(e)}")
            
            # If file not found or invalid, return a mock exercise
            logger.warning("No valid string_methods_capitalize exercises found, returning mock")
            return [{
                "id": "string_methods_capitalize_1",
                "title": "String Methods - capitalize()",
                "difficulty": "beginner",
                "chapter_id": "Chapter1_DataObjects",
                "description": "Learn about Python's string capitalize() method.",
                "instructions": "Create a program that uses the capitalize() method on different strings.",
                "starterCode": "# String capitalize() method in Python\n\n# Basic usage\nname = 'john'\ncapitalized_name = name.capitalize()\nprint(f\"Original: {name}\")\nprint(f\"Capitalized: {capitalized_name}\")\n\n# Try with a sentence\nsentence = 'hello world. how are you?'\ncapitalized_sentence = sentence.capitalize()\nprint(f\"Original: {sentence}\")\nprint(f\"Capitalized: {capitalized_sentence}\")\n\n# Note that capitalize() only affects the first character\n# and makes all other characters lowercase\nweird_text = 'hELLO wORLD'\nprint(f\"Original: {weird_text}\")\nprint(f\"Capitalized: {weird_text.capitalize()}\")"
            }]
        
        # Special case for string methods lower
        if topic_id.lower() == "string_methods_lower" or topic_id.lower() == "05_string_methods_lower":
            logger.info("Using direct handler for string_methods_lower")
            chapter_dir = os.path.join(EXERCISES_DIR, "Chapter1_DataObjects")
            file_path = os.path.join(chapter_dir, "05_string_methods_lower.json")
            
            if os.path.exists(file_path):
                logger.info(f"Found string_methods_lower file at: {file_path}")
                with open(file_path, 'r') as f:
                    try:
                        exercises = json.load(f)
                        logger.info(f"Loaded {len(exercises) if isinstance(exercises, list) else 1} string_methods_lower exercises")
                        
                        # Process exercises to ensure they have required fields
                        processed_exercises = []
                        if isinstance(exercises, list):
                            for ex in exercises:
                                # Ensure each exercise has id, title, and chapter_id
                                ex_id = ex.get("id", f"string_methods_lower_{len(processed_exercises) + 1}")
                                ex_title = ex.get("title", f"String Methods Lower Exercise {len(processed_exercises) + 1}")
                                ex_difficulty = ex.get("difficulty", "beginner")
                                ex_chapter_id = ex.get("chapter_id", "Chapter1_DataObjects")
                                
                                ex["id"] = ex_id
                                ex["title"] = ex_title
                                ex["difficulty"] = ex_difficulty
                                ex["chapter_id"] = ex_chapter_id
                                
                                processed_exercises.append(ex)
                        elif isinstance(exercises, dict):
                            # Single exercise
                            ex_id = exercises.get("id", "string_methods_lower_1")
                            ex_title = exercises.get("title", "String Methods Lower Exercise")
                            ex_difficulty = exercises.get("difficulty", "beginner")
                            ex_chapter_id = exercises.get("chapter_id", "Chapter1_DataObjects")
                            
                            exercises["id"] = ex_id
                            exercises["title"] = ex_title
                            exercises["difficulty"] = ex_difficulty
                            exercises["chapter_id"] = ex_chapter_id
                            
                            processed_exercises.append(exercises)
                        
                        logger.info(f"Returning {len(processed_exercises)} string_methods_lower exercises")
                        return processed_exercises
                    except json.JSONDecodeError as e:
                        logger.error(f"Error parsing JSON from {file_path}: {str(e)}")
                    except Exception as e:
                        logger.error(f"Unexpected error processing {file_path}: {str(e)}")
            
            # If file not found or invalid, return a mock exercise
            logger.warning("No valid string_methods_lower exercises found, returning mock")
            return [{
                "id": "string_methods_lower_1",
                "title": "String Methods - lower()",
                "difficulty": "beginner",
                "chapter_id": "Chapter1_DataObjects",
                "description": "Learn about Python's string lower() method.",
                "instructions": "Create a program that uses the lower() method on different strings.",
                "starterCode": "# String lower() method in Python\n\n# Basic usage\nname = 'JOHN'\nlowered_name = name.lower()\nprint(f\"Original: {name}\")\nprint(f\"Lowered: {lowered_name}\")\n\n# Try with a sentence\nsentence = 'Hello World. How Are You?'\nlowered_sentence = sentence.lower()\nprint(f\"Original: {sentence}\")\nprint(f\"Lowered: {lowered_sentence}\")\n\n# Useful for case-insensitive comparisons\nuser_input = 'YES'\nif user_input.lower() == 'yes':\n    print(\"User said yes!\")"
            }]
        
        # Special case for string methods split
        if topic_id.lower() == "string_methods_split" or topic_id.lower() == "05_string_methods_split":
            logger.info("Using direct handler for string_methods_split")
            chapter_dir = os.path.join(EXERCISES_DIR, "Chapter1_DataObjects")
            file_path = os.path.join(chapter_dir, "05_string_methods_split.json")
            
            if os.path.exists(file_path):
                logger.info(f"Found string_methods_split file at: {file_path}")
                with open(file_path, 'r') as f:
                    try:
                        exercises = json.load(f)
                        logger.info(f"Loaded {len(exercises) if isinstance(exercises, list) else 1} string_methods_split exercises")
                        
                        # Process exercises to ensure they have required fields
                        processed_exercises = []
                        if isinstance(exercises, list):
                            for ex in exercises:
                                # Ensure each exercise has id, title, and chapter_id
                                ex_id = ex.get("id", f"string_methods_split_{len(processed_exercises) + 1}")
                                ex_title = ex.get("title", f"String Methods Split Exercise {len(processed_exercises) + 1}")
                                ex_difficulty = ex.get("difficulty", "beginner")
                                ex_chapter_id = ex.get("chapter_id", "Chapter1_DataObjects")
                                
                                ex["id"] = ex_id
                                ex["title"] = ex_title
                                ex["difficulty"] = ex_difficulty
                                ex["chapter_id"] = ex_chapter_id
                                
                                processed_exercises.append(ex)
                        elif isinstance(exercises, dict):
                            # Single exercise
                            ex_id = exercises.get("id", "string_methods_split_1")
                            ex_title = exercises.get("title", "String Methods Split Exercise")
                            ex_difficulty = exercises.get("difficulty", "beginner")
                            ex_chapter_id = exercises.get("chapter_id", "Chapter1_DataObjects")
                            
                            exercises["id"] = ex_id
                            exercises["title"] = ex_title
                            exercises["difficulty"] = ex_difficulty
                            exercises["chapter_id"] = ex_chapter_id
                            
                            processed_exercises.append(exercises)
                        
                        logger.info(f"Returning {len(processed_exercises)} string_methods_split exercises")
                        return processed_exercises
                    except json.JSONDecodeError as e:
                        logger.error(f"Error parsing JSON from {file_path}: {str(e)}")
                    except Exception as e:
                        logger.error(f"Unexpected error processing {file_path}: {str(e)}")
            
            # If file not found or invalid, return a mock exercise
            logger.warning("No valid string_methods_split exercises found, returning mock")
            return [{
                "id": "string_methods_split_1",
                "title": "String Methods - split()",
                "difficulty": "beginner",
                "chapter_id": "Chapter1_DataObjects",
                "description": "Learn about Python's string split() method.",
                "instructions": "Create a program that uses the split() method on different strings.",
                "starterCode": "# String split() method in Python\n\n# Basic usage\nsentence = 'apple banana cherry'\nwords = sentence.split()\nprint(f\"Original: {sentence}\")\nprint(f\"Split: {words}\")\n\n# Split with a specific delimiter\ncsv_data = 'John,Doe,30,New York'\nparts = csv_data.split(',')\nprint(f\"Original: {csv_data}\")\nprint(f\"Split: {parts}\")\n\n# Limit the number of splits\ntext = 'one-two-three-four-five'\nparts_limited = text.split('-', 2)  # Split only at the first 2 occurrences\nprint(f\"Original: {text}\")\nprint(f\"Limited split: {parts_limited}\")"
            }]
        
        # Special case for string methods upper
        if topic_id.lower() == "string_methods_upper" or topic_id.lower() == "05_string_methods_upper":
            logger.info("Using direct handler for string_methods_upper")
            chapter_dir = os.path.join(EXERCISES_DIR, "Chapter1_DataObjects")
            file_path = os.path.join(chapter_dir, "05_string_methods_upper.json")
            
            if os.path.exists(file_path):
                logger.info(f"Found string_methods_upper file at: {file_path}")
                with open(file_path, 'r') as f:
                    try:
                        exercises = json.load(f)
                        logger.info(f"Loaded {len(exercises) if isinstance(exercises, list) else 1} string_methods_upper exercises")
                        
                        # Process exercises to ensure they have required fields
                        processed_exercises = []
                        if isinstance(exercises, list):
                            for ex in exercises:
                                # Ensure each exercise has id, title, and chapter_id
                                ex_id = ex.get("id", f"string_methods_upper_{len(processed_exercises) + 1}")
                                ex_title = ex.get("title", f"String Methods Upper Exercise {len(processed_exercises) + 1}")
                                ex_difficulty = ex.get("difficulty", "beginner")
                                ex_chapter_id = ex.get("chapter_id", "Chapter1_DataObjects")
                                
                                ex["id"] = ex_id
                                ex["title"] = ex_title
                                ex["difficulty"] = ex_difficulty
                                ex["chapter_id"] = ex_chapter_id
                                
                                processed_exercises.append(ex)
                        elif isinstance(exercises, dict):
                            # Single exercise
                            ex_id = exercises.get("id", "string_methods_upper_1")
                            ex_title = exercises.get("title", "String Methods Upper Exercise")
                            ex_difficulty = exercises.get("difficulty", "beginner")
                            ex_chapter_id = exercises.get("chapter_id", "Chapter1_DataObjects")
                            
                            exercises["id"] = ex_id
                            exercises["title"] = ex_title
                            exercises["difficulty"] = ex_difficulty
                            exercises["chapter_id"] = ex_chapter_id
                            
                            processed_exercises.append(exercises)
                        
                        logger.info(f"Returning {len(processed_exercises)} string_methods_upper exercises")
                        return processed_exercises
                    except json.JSONDecodeError as e:
                        logger.error(f"Error parsing JSON from {file_path}: {str(e)}")
                    except Exception as e:
                        logger.error(f"Unexpected error processing {file_path}: {str(e)}")
            
            # If file not found or invalid, return a mock exercise
            logger.warning("No valid string_methods_upper exercises found, returning mock")
            return [{
                "id": "string_methods_upper_1",
                "title": "String Methods - upper()",
                "difficulty": "beginner",
                "chapter_id": "Chapter1_DataObjects",
                "description": "Learn about Python's string upper() method.",
                "instructions": "Create a program that uses the upper() method on different strings.",
                "starterCode": "# String upper() method in Python\n\n# Basic usage\nname = 'john'\nuppered_name = name.upper()\nprint(f\"Original: {name}\")\nprint(f\"Uppered: {uppered_name}\")\n\n# Try with a sentence\nsentence = 'Hello World. How Are You?'\nuppered_sentence = sentence.upper()\nprint(f\"Original: {sentence}\")\nprint(f\"Uppered: {uppered_sentence}\")\n\n# Useful for emphasis or displaying warnings\nwarning = 'caution: hot surface'\nprint(f\"Warning: {warning.upper()}\")"
            }]
        
        # Special case for combined Strings (04_strings)    
        if topic_id.lower() == "strings" or topic_id.lower() == "04_strings":
            logger.info("Using direct handler for combined Strings (both part1 and part2)")
            combined_exercises = []
            
            # Load part1
            chapter_dir = os.path.join(EXERCISES_DIR, "Chapter1_DataObjects")
            file_path_part1 = os.path.join(chapter_dir, "04_strings_part1.json")
            
            if os.path.exists(file_path_part1):
                logger.info(f"Found strings part1 file at: {file_path_part1}")
                try:
                    with open(file_path_part1, 'r') as f:
                        exercises_part1 = json.load(f)
                        logger.info(f"Loaded {len(exercises_part1) if isinstance(exercises_part1, list) else 1} strings part1 exercises")
                        
                        if isinstance(exercises_part1, list):
                            for ex in exercises_part1:
                                # Ensure each exercise has required fields
                                ex_id = ex.get("id", f"strings_part1_{len(combined_exercises) + 1}")
                                ex_title = ex.get("title", f"Strings Part 1 Exercise {len(combined_exercises) + 1}")
                                ex_difficulty = ex.get("difficulty", "beginner")
                                ex_chapter_id = ex.get("chapter_id", "Chapter1_DataObjects")
                                
                                ex["id"] = ex_id
                                ex["title"] = ex_title
                                ex["difficulty"] = ex_difficulty
                                ex["chapter_id"] = ex_chapter_id
                                
                                combined_exercises.append(ex)
                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing part1 JSON: {str(e)}")
                except Exception as e:
                    logger.error(f"Unexpected error processing part1: {str(e)}")
            
            # Load part2
            file_path_part2 = os.path.join(chapter_dir, "04_strings_part2.json")
            if os.path.exists(file_path_part2):
                logger.info(f"Found strings part2 file at: {file_path_part2}")
                try:
                    with open(file_path_part2, 'r') as f:
                        exercises_part2 = json.load(f)
                        logger.info(f"Loaded {len(exercises_part2) if isinstance(exercises_part2, list) else 1} strings part2 exercises")
                        
                        if isinstance(exercises_part2, list):
                            for ex in exercises_part2:
                                # Ensure each exercise has required fields
                                ex_id = ex.get("id", f"strings_part2_{len(combined_exercises) + 1}")
                                ex_title = ex.get("title", f"Strings Part 2 Exercise {len(combined_exercises) + 1}")
                                ex_difficulty = ex.get("difficulty", "beginner")
                                ex_chapter_id = ex.get("chapter_id", "Chapter1_DataObjects")
                                
                                ex["id"] = ex_id
                                ex["title"] = ex_title
                                ex["difficulty"] = ex_difficulty
                                ex["chapter_id"] = ex_chapter_id
                                
                                combined_exercises.append(ex)
                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing part2 JSON: {str(e)}")
                except Exception as e:
                    logger.error(f"Unexpected error processing part2: {str(e)}")
            
            logger.info(f"Returning {len(combined_exercises)} combined string exercises")
            if combined_exercises:
                return combined_exercises
            
            # If we couldn't load the exercises, return a mock
            logger.warning("No valid string exercises found, returning mock")
            return [{
                "id": "strings_1",
                "title": "Python Strings",
                "difficulty": "beginner",
                "chapter_id": "Chapter1_DataObjects",
                "description": "Learn about Python's string data type.",
                "instructions": "Explore and practice using strings in Python.",
                "starterCode": "# String operations\nname = \"Python\"\n\n# Length of string\nprint(len(name))  # 6\n\n# Accessing characters (indexing)\nprint(name[0])  # 'P'\nprint(name[-1])  # 'n'\n\n# Slicing\nprint(name[0:2])  # 'Py'\nprint(name[2:])  # 'thon'\n\n# Concatenation\nprint(name + \" Programming\")  # 'Python Programming'\n\n# Repetition\nprint(name * 3)  # 'PythonPythonPython'\n\n# Methods\nprint(name.upper())  # 'PYTHON'\nprint(name.lower())  # 'python'\nprint(\"  whitespace  \".strip())  # 'whitespace'"
            }]
            
        # Special case for String Concatenation
        if topic_id.lower() == "string_concatenation" or topic_id.lower() == "05_string_concatenation":
            logger.info("Using direct handler for String Concatenation")
            chapter_dir = os.path.join(EXERCISES_DIR, "Chapter1_DataObjects")
            file_path = os.path.join(chapter_dir, "05_string_concatenation.json")
            
            if os.path.exists(file_path):
                logger.info(f"Found string concatenation file at: {file_path}")
                try:
                    with open(file_path, 'r') as f:
                        exercises = json.load(f)
                        logger.info(f"Loaded {len(exercises) if isinstance(exercises, list) else 1} string concatenation exercises")
                        
                        # Process exercises to ensure they have required fields
                        processed_exercises = []
                        if isinstance(exercises, list):
                            for ex in exercises:
                                # Ensure each exercise has id, title, and chapter_id
                                ex_id = ex.get("id", f"string_concatenation_{len(processed_exercises) + 1}")
                                ex_title = ex.get("title", f"String Concatenation Exercise {len(processed_exercises) + 1}")
                                ex_difficulty = ex.get("difficulty", "beginner")
                                ex_chapter_id = ex.get("chapter_id", "Chapter1_DataObjects")
                                
                                ex["id"] = ex_id
                                ex["title"] = ex_title
                                ex["difficulty"] = ex_difficulty
                                ex["chapter_id"] = ex_chapter_id
                                
                                processed_exercises.append(ex)
                        elif isinstance(exercises, dict):
                            # Single exercise
                            ex_id = exercises.get("id", "string_concatenation_1")
                            ex_title = exercises.get("title", "String Concatenation Exercise")
                            ex_difficulty = exercises.get("difficulty", "beginner")
                            ex_chapter_id = exercises.get("chapter_id", "Chapter1_DataObjects")
                            
                            exercises["id"] = ex_id
                            exercises["title"] = ex_title
                            exercises["difficulty"] = ex_difficulty
                            exercises["chapter_id"] = ex_chapter_id
                            
                            processed_exercises.append(exercises)
                        
                        logger.info(f"Returning {len(processed_exercises)} string concatenation exercises")
                        return processed_exercises
                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing JSON from {file_path}: {str(e)}")
                except Exception as e:
                    logger.error(f"Unexpected error processing {file_path}: {str(e)}")
            
            # If file not found or invalid, return a mock exercise
            logger.warning("No valid string concatenation exercises found, returning mock")
            return [{
                "id": "string_concatenation_1",
                "title": "String Concatenation",
                "difficulty": "beginner",
                "chapter_id": "Chapter1_DataObjects",
                "description": "Learn about Python's string concatenation operations.",
                "instructions": "Create a program that concatenates different strings using various methods.",
                "starterCode": "# String concatenation in Python\n\n# Using the + operator\nfirst_name = \"John\"\nlast_name = \"Doe\"\nfull_name = first_name + \" \" + last_name\nprint(full_name)  # John Doe\n\n# Using join() method\nwords = [\"Python\", \"is\", \"awesome\"]\nsentence = \" \".join(words)\nprint(sentence)  # Python is awesome\n\n# Using f-strings (Python 3.6+)\nage = 30\nmessage = f\"{full_name} is {age} years old\"\nprint(message)  # John Doe is 30 years old\n\n# String multiplication\ndivider = \"-\" * 20\nprint(divider)  # --------------------"
            }]
            
        # Special case for strings_part2
        if topic_id.lower() == "strings_part2" or topic_id.lower() == "04_strings_part2":
            logger.info("Using direct handler for strings_part2")
            chapter_dir = os.path.join(EXERCISES_DIR, "Chapter1_DataObjects")
            file_path = os.path.join(chapter_dir, "04_strings_part2.json")
            
            if os.path.exists(file_path):
                logger.info(f"Found strings_part2 file at: {file_path}")
                with open(file_path, 'r') as f:
                    try:
                        exercises = json.load(f)
                        logger.info(f"Loaded {len(exercises) if isinstance(exercises, list) else 1} strings_part2 exercises")
                        
                        # Process exercises to ensure they have required fields
                        processed_exercises = []
                        if isinstance(exercises, list):
                            for ex in exercises:
                                # Ensure each exercise has id, title, and chapter_id
                                ex_id = ex.get("id", f"strings_part2_{len(processed_exercises) + 1}")
                                ex_title = ex.get("title", f"Strings Part 2 Exercise {len(processed_exercises) + 1}")
                                ex_difficulty = ex.get("difficulty", "beginner")
                                ex_chapter_id = ex.get("chapter_id", "Chapter1_DataObjects")
                                
                                ex["id"] = ex_id
                                ex["title"] = ex_title
                                ex["difficulty"] = ex_difficulty
                                ex["chapter_id"] = ex_chapter_id
                                
                                processed_exercises.append(ex)
                        elif isinstance(exercises, dict):
                            # Single exercise
                            ex_id = exercises.get("id", "strings_part2_1")
                            ex_title = exercises.get("title", "Strings Part 2 Exercise")
                            ex_difficulty = exercises.get("difficulty", "beginner")
                            ex_chapter_id = exercises.get("chapter_id", "Chapter1_DataObjects")
                            
                            exercises["id"] = ex_id
                            exercises["title"] = ex_title
                            exercises["difficulty"] = ex_difficulty
                            exercises["chapter_id"] = ex_chapter_id
                            
                            processed_exercises.append(exercises)
                        
                        return processed_exercises
                    except json.JSONDecodeError as e:
                        logger.error(f"Error parsing JSON from {file_path}: {str(e)}")
        
        # Special case for strings_part1
        if topic_id.lower() == "strings_part1" or topic_id.lower() == "04_strings_part1":
            logger.info("Using direct handler for strings_part1")
            chapter_dir = os.path.join(EXERCISES_DIR, "Chapter1_DataObjects")
            file_path = os.path.join(chapter_dir, "04_strings_part1.json")
            
            if os.path.exists(file_path):
                logger.info(f"Found strings_part1 file at: {file_path}")
                with open(file_path, 'r') as f:
                    try:
                        exercises = json.load(f)
                        logger.info(f"Loaded {len(exercises) if isinstance(exercises, list) else 1} strings_part1 exercises")
                        
                        # Process exercises to ensure they have required fields
                        processed_exercises = []
                        if isinstance(exercises, list):
                            for ex in exercises:
                                # Ensure each exercise has id, title, and chapter_id
                                ex_id = ex.get("id", f"strings_part1_{len(processed_exercises) + 1}")
                                ex_title = ex.get("title", f"Strings Part 1 Exercise {len(processed_exercises) + 1}")
                                ex_difficulty = ex.get("difficulty", "beginner")
                                ex_chapter_id = ex.get("chapter_id", "Chapter1_DataObjects")
                                
                                ex["id"] = ex_id
                                ex["title"] = ex_title
                                ex["difficulty"] = ex_difficulty
                                ex["chapter_id"] = ex_chapter_id
                                
                                processed_exercises.append(ex)
                        elif isinstance(exercises, dict):
                            # Single exercise
                            ex_id = exercises.get("id", "strings_part1_1")
                            ex_title = exercises.get("title", "Strings Part 1 Exercise")
                            ex_difficulty = exercises.get("difficulty", "beginner")
                            ex_chapter_id = exercises.get("chapter_id", "Chapter1_DataObjects")
                            
                            exercises["id"] = ex_id
                            exercises["title"] = ex_title
                            exercises["difficulty"] = ex_difficulty
                            exercises["chapter_id"] = ex_chapter_id
                            
                            processed_exercises.append(exercises)
                        
                        return processed_exercises
                    except json.JSONDecodeError as e:
                        logger.error(f"Error parsing JSON from {file_path}: {str(e)}")
        
        if topic_id.lower() == "if_statements" or topic_id.lower() == "03_if_statements" or topic_id.lower() == "01_if":
            # Direct handler for if statements (Chapter 3)
            logger.info("Using direct handler for if statements")
            chapter_dir = os.path.join(EXERCISES_DIR, "Chapter3_Statements")
            if_statement_files = [
                "03_if_statements.json",
                "03_if_statement.json",
                "01_if_statements.json",
                "01_if_statement.json",
                "01_if.json",
                "if_statements.json",
                "if_statement.json",
                "if.json"
            ]
            
            for filename in if_statement_files:
                file_path = os.path.join(chapter_dir, filename)
                if os.path.exists(file_path):
                    logger.info(f"Found if statements file at: {file_path}")
                    with open(file_path, 'r') as f:
                        try:
                            exercises = json.load(f)
                            logger.info(f"Loaded {len(exercises) if isinstance(exercises, list) else 1} if statement exercises")
                            
                            # Process exercises to ensure they have required fields
                            processed_exercises = []
                            if isinstance(exercises, list):
                                for ex in exercises:
                                    # Ensure each exercise has id, title, and chapter_id
                                    ex_id = ex.get("id", f"if_statement_{len(processed_exercises) + 1}")
                                    ex_title = ex.get("title", f"If Statement Exercise {len(processed_exercises) + 1}")
                                    ex_difficulty = ex.get("difficulty", "beginner")
                                    ex_chapter_id = ex.get("chapter_id", "Chapter3_Statements")
                                    
                                    ex["id"] = ex_id
                                    ex["title"] = ex_title
                                    ex["difficulty"] = ex_difficulty
                                    ex["chapter_id"] = ex_chapter_id
                                    
                                    processed_exercises.append(ex)
                            elif isinstance(exercises, dict):
                                # Single exercise
                                ex_id = exercises.get("id", "if_statement_1")
                                ex_title = exercises.get("title", "If Statement Exercise")
                                ex_difficulty = exercises.get("difficulty", "beginner")
                                ex_chapter_id = exercises.get("chapter_id", "Chapter3_Statements")
                                
                                exercises["id"] = ex_id
                                exercises["title"] = ex_title
                                exercises["difficulty"] = ex_difficulty
                                exercises["chapter_id"] = ex_chapter_id
                                
                                processed_exercises.append(exercises)
                            
                            return processed_exercises
                        except json.JSONDecodeError as e:
                            logger.error(f"Error parsing JSON from {file_path}: {str(e)}")
        
        # Special case for numbers
        if topic_id.lower() == "numbers" or topic_id.lower() == "02_numbers":
            logger.info("Using direct handler for numbers")
            chapter_dir = os.path.join(EXERCISES_DIR, "Chapter1_DataObjects")
            numbers_files = [
                "02_numbers.json",
                "numbers.json"
            ]
            
            for filename in numbers_files:
                file_path = os.path.join(chapter_dir, filename)
                if os.path.exists(file_path):
                    logger.info(f"Found numbers file at: {file_path}")
                    with open(file_path, 'r') as f:
                        try:
                            exercises = json.load(f)
                            logger.info(f"Loaded {len(exercises) if isinstance(exercises, list) else 1} numbers exercises")
                            
                            # Process exercises
                            processed_exercises = []
                            if isinstance(exercises, list):
                                for ex in exercises:
                                    ex_id = ex.get("id", f"numbers_{len(processed_exercises) + 1}")
                                    ex_title = ex.get("title", f"Numbers Exercise {len(processed_exercises) + 1}")
                                    ex_difficulty = ex.get("difficulty", "beginner")
                                    ex_chapter_id = ex.get("chapter_id", "Chapter1_DataObjects")
                                    
                                    ex["id"] = ex_id
                                    ex["title"] = ex_title
                                    ex["difficulty"] = ex_difficulty
                                    ex["chapter_id"] = ex_chapter_id
                                    
                                    processed_exercises.append(ex)
                            elif isinstance(exercises, dict):
                                ex_id = exercises.get("id", "numbers_1")
                                ex_title = exercises.get("title", "Numbers Exercise")
                                ex_difficulty = exercises.get("difficulty", "beginner")
                                ex_chapter_id = exercises.get("chapter_id", "Chapter1_DataObjects")
                                
                                exercises["id"] = ex_id
                                exercises["title"] = ex_title
                                exercises["difficulty"] = ex_difficulty
                                exercises["chapter_id"] = ex_chapter_id
                                
                                processed_exercises.append(exercises)
                            
                            return processed_exercises
                        except json.JSONDecodeError as e:
                            logger.error(f"Error parsing JSON from {file_path}: {str(e)}")
            
        # For other topics, search through all chapter directories
        found_exercises = []
        for chapter_dir in ["Chapter1_DataObjects", "Chapter2_Operators", "Chapter3_Statements", 
                           "Chapter4_MethodsFunctions", "Chapter5_OOP", "Chapter6_ModulesPackages"]:
            full_chapter_dir = os.path.join(EXERCISES_DIR, chapter_dir)
            if not os.path.exists(full_chapter_dir):
                logger.warning(f"Chapter directory does not exist: {full_chapter_dir}")
                continue
            
            # Look for files that match the topic_id
            for filename in os.listdir(full_chapter_dir):
                if filename.endswith('.json'):
                    # Check if topic is in filename (ignoring numbering)
                    topic_pattern = topic_id.lower().replace("_", "").replace("-", "")
                    clean_filename = filename.lower().replace("_", "").replace("-", "")
                    
                    # Skip numbering prefix for matching
                    if re.search(r'^\d+', clean_filename):
                        clean_filename = re.sub(r'^\d+', '', clean_filename)
                    
                    # Also check for partial matches (e.g., "numbers" should match "number")
                    is_match = False
                    if topic_pattern in clean_filename:
                        is_match = True
                    elif clean_filename in topic_pattern:
                        is_match = True
                    # Handle plurals (e.g., "tuples" should match "tuple")
                    elif topic_pattern.rstrip('s') == clean_filename.rstrip('s'):
                        is_match = True
                        
                    if is_match:
                        logger.info(f"Found potential match: {filename}")
                        file_path = os.path.join(full_chapter_dir, filename)
                        try:
                            with open(file_path, 'r') as f:
                                exercises = json.load(f)
                                logger.info(f"Loaded {len(exercises) if isinstance(exercises, list) else 1} exercises from {filename}")
                                
                                # Process exercises to ensure they have required fields
                                if isinstance(exercises, list):
                                    for ex in exercises:
                                        # Ensure each exercise has id, title, and chapter_id
                                        if not ex.get('id'):
                                            ex['id'] = f"{topic_id}_{len(found_exercises) + 1}"
                                        if not ex.get('title'):
                                            ex['title'] = f"{topic_id.replace('_', ' ').title()} Exercise {len(found_exercises) + 1}"
                                        if not ex.get('difficulty'):
                                            ex['difficulty'] = "beginner"
                                        if not ex.get('chapter_id'):
                                            ex['chapter_id'] = chapter_dir
                                        
                                        found_exercises.append(ex)
                                elif isinstance(exercises, dict):
                                    # Single exercise
                                    if not exercises.get('id'):
                                        exercises['id'] = f"{topic_id}_1"
                                    if not exercises.get('title'):
                                        exercises['title'] = f"{topic_id.replace('_', ' ').title()} Exercise"
                                    if not exercises.get('difficulty'):
                                        exercises['difficulty'] = "beginner" 
                                    if not exercises.get('chapter_id'):
                                        exercises['chapter_id'] = chapter_dir
                                    
                                    found_exercises.append(exercises)
                        except (json.JSONDecodeError, Exception) as e:
                            logger.error(f"Error loading exercises from {file_path}: {str(e)}")
        
        # If direct searches failed, try pattern matching on filenames
        if not found_exercises:
            logger.info(f"No direct matches found for {topic_id}, trying pattern matching")
            
            # Extract topic number if it exists (e.g., "02_numbers" -> "02")
            topic_prefix = re.match(r'^(\d+)_', topic_id)
            if topic_prefix:
                prefix = topic_prefix.group(1)
                topic_base = topic_id.replace(f"{prefix}_", "")
                
                # Search all chapter directories for files with the same prefix or topic base
                for chapter_dir in ["Chapter1_DataObjects", "Chapter2_Operators", "Chapter3_Statements", 
                                   "Chapter4_MethodsFunctions", "Chapter5_OOP", "Chapter6_ModulesPackages"]:
                    full_chapter_dir = os.path.join(EXERCISES_DIR, chapter_dir)
                    if not os.path.exists(full_chapter_dir):
                        continue
                    
                    for filename in os.listdir(full_chapter_dir):
                        if filename.endswith('.json'):
                            file_prefix = re.match(r'^(\d+)_', filename)
                            if file_prefix and file_prefix.group(1) == prefix:
                                logger.info(f"Found prefix match: {filename}")
                                file_path = os.path.join(full_chapter_dir, filename)
                                try:
                                    with open(file_path, 'r') as f:
                                        exercises = json.load(f)
                                        if isinstance(exercises, list):
                                            for ex in exercises:
                                                # Set required fields
                                                if not ex.get('id'):
                                                    ex['id'] = f"{topic_id}_{len(found_exercises) + 1}"
                                                if not ex.get('title'):
                                                    ex['title'] = f"{topic_id.replace('_', ' ').title()} Exercise {len(found_exercises) + 1}"
                                                if not ex.get('difficulty'):
                                                    ex['difficulty'] = "beginner"
                                                if not ex.get('chapter_id'):
                                                    ex['chapter_id'] = chapter_dir
                                                
                                                found_exercises.append(ex)
                                        elif isinstance(exercises, dict):
                                            # Single exercise
                                            if not exercises.get('id'):
                                                exercises['id'] = f"{topic_id}_1"
                                            if not exercises.get('title'):
                                                exercises['title'] = f"{topic_id.replace('_', ' ').title()} Exercise"
                                            if not exercises.get('difficulty'):
                                                exercises['difficulty'] = "beginner"
                                            if not exercises.get('chapter_id'):
                                                exercises['chapter_id'] = chapter_dir
                                            
                                            found_exercises.append(exercises)
                                except Exception as e:
                                    logger.error(f"Error reading pattern-matched file {file_path}: {str(e)}")
        
        if found_exercises:
            logger.info(f"Found {len(found_exercises)} exercises for topic {topic_id}")
            return found_exercises
        
        # If we get here, no exercises were found, create a comprehensive mock exercise
        logger.warning(f"No exercises found for topic {topic_id}, returning mock exercise")
        return [{
            "id": f"{topic_id}_1",
            "title": f"Python {topic_id.replace('_', ' ').title()}",
            "difficulty": "beginner",
            "chapter_id": "Unknown",
            "description": f"Learn about Python's {topic_id.replace('_', ' ')}.",
            "instructions": f"Explore and practice using {topic_id.replace('_', ' ')} in Python.",
            "starterCode": create_mock_starter_code(topic_id)
        }]
    except Exception as e:
        logger.error(f"Error in get_topic_direct for {topic_id}: {str(e)}")
        return [{
            "id": f"error_{topic_id}",
            "title": f"Python {topic_id.replace('_', ' ').title()}",
            "difficulty": "beginner",
            "chapter_id": "Unknown",
            "description": f"Learn about Python's {topic_id.replace('_', ' ')}.",
            "instructions": f"Explore and practice using {topic_id.replace('_', ' ')} in Python. (Note: There was an error loading the actual exercise)",
            "starterCode": create_mock_starter_code(topic_id)
        }]

def create_mock_starter_code(topic_id: str) -> str:
    """Create appropriate starter code based on the topic."""
    topic = topic_id.replace('_', ' ').lower()
    
    if 'number' in topic:
        return "# Working with numbers in Python\n\n# Integer operations\na = 10\nb = 3\n\nprint(f\"a + b = {a + b}\")\nprint(f\"a - b = {a - b}\")\nprint(f\"a * b = {a * b}\")\nprint(f\"a / b = {a / b}\")\nprint(f\"a // b = {a // b}\")\nprint(f\"a % b = {a % b}\")\nprint(f\"a ** b = {a ** b}\")"
    elif 'string' in topic:
        return "# Working with strings in Python\n\nmessage = \"Hello, Python!\"\n\nprint(message)\nprint(f\"Length: {len(message)}\")\nprint(f\"Uppercase: {message.upper()}\")\nprint(f\"Lowercase: {message.lower()}\")\nprint(f\"Replace: {message.replace('Python', 'World')}\")"
    elif 'list' in topic:
        return "# Working with lists in Python\n\nmy_list = [1, 2, 3, 4, 5]\n\nprint(my_list)\nprint(f\"Length: {len(my_list)}\")\nprint(f\"First item: {my_list[0]}\")\nprint(f\"Last item: {my_list[-1]}\")\nprint(f\"Sliced: {my_list[1:3]}\")\n\n# Adding items\nmy_list.append(6)\nprint(f\"After append: {my_list}\")"
    elif 'dict' in topic:
        return "# Working with dictionaries in Python\n\nmy_dict = {'name': 'Alice', 'age': 25, 'city': 'New York'}\n\nprint(my_dict)\nprint(f\"Keys: {my_dict.keys()}\")\nprint(f\"Values: {my_dict.values()}\")\nprint(f\"Items: {my_dict.items()}\")\nprint(f\"Name: {my_dict['name']}\")\n\n# Adding a new key-value pair\nmy_dict['job'] = 'Engineer'\nprint(f\"Updated dictionary: {my_dict}\")"
    elif 'tuple' in topic:
        return "# Working with tuples in Python\n\nmy_tuple = (1, 2, 3, 'a', 'b')\n\nprint(my_tuple)\nprint(f\"Length: {len(my_tuple)}\")\nprint(f\"First item: {my_tuple[0]}\")\nprint(f\"Last item: {my_tuple[-1]}\")\nprint(f\"Sliced: {my_tuple[1:3]}\")"
    elif 'set' in topic:
        return "# Working with sets in Python\n\nset_a = {1, 2, 3, 4, 5}\nset_b = {4, 5, 6, 7, 8}\n\nprint(f\"Set A: {set_a}\")\nprint(f\"Set B: {set_b}\")\nprint(f\"Union: {set_a | set_b}\")\nprint(f\"Intersection: {set_a & set_b}\")\nprint(f\"Difference (A-B): {set_a - set_b}\")\nprint(f\"Symmetric Difference: {set_a ^ set_b}\")"
    elif 'if' in topic or 'condition' in topic:
        return "# Working with if statements in Python\n\nx = 10\n\nif x > 0:\n    print(\"x is positive\")\nelif x < 0:\n    print(\"x is negative\")\nelse:\n    print(\"x is zero\")\n\n# Try changing the value of x"
    elif 'loop' in topic or 'for' in topic:
        return "# Working with loops in Python\n\n# For loop\nprint(\"For loop:\")\nfor i in range(5):\n    print(f\"Item {i}\")\n\n# While loop\nprint(\"\\nWhile loop:\")\ncount = 0\nwhile count < 5:\n    print(f\"Count: {count}\")\n    count += 1"
    elif 'function' in topic:
        return "# Working with functions in Python\n\ndef greet(name):\n    return f\"Hello, {name}!\"\n\ndef add(a, b):\n    return a + b\n\n# Call the functions\nprint(greet(\"Alice\"))\nprint(f\"Sum: {add(5, 3)}\")"
    else:
        return f"# This is a starter code for {topic_id}\n\n# Try experimenting with this topic\nprint('Learning about {topic}')"

@router.get("/exercises/if_statements")
async def get_if_statements():
    """
    Get all if statement exercises directly.
    This is a special case to handle common access issues.
    """
    try:
        all_if_exercises = []
        if_files = [
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                        "python-learning-platform", "exercises", 
                        "Chapter3_Statements", "01_if_else_basics.json"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                        "python-learning-platform", "exercises", 
                        "Chapter3_Statements", "01_if_elif_else_chains.json"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                        "python-learning-platform", "exercises", 
                        "Chapter3_Statements", "01_complex_conditionals.json")
        ]
        
        base_id_counter = 1
        
        # Try to load each file
        for file_path in if_files:
            if os.path.exists(file_path):
                logger.info(f"Loading if exercises from: {file_path}")
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        
                        # Log the data type and length
                        logger.info(f"Loaded data type: {type(data)}, Length if list: {len(data) if isinstance(data, list) else 'N/A'}")
                        
                        if isinstance(data, list):
                            logger.info(f"Found {len(data)} exercises in {os.path.basename(file_path)}")
                            
                            # Process each exercise
                            for exercise in data:
                                # Create a copy to avoid modifying the original
                                ex = dict(exercise)
                                
                                # Add ID if missing
                                if "id" not in ex:
                                    ex["id"] = f"if_statements_{base_id_counter}"
                                    base_id_counter += 1
                                
                                # Add chapter_id if not present
                                if "chapter_id" not in ex:
                                    ex["chapter_id"] = "Chapter3_Statements"
                                
                                # Copy exercise to instructions if instructions is missing
                                if "instructions" not in ex and "exercise" in ex:
                                    ex["instructions"] = ex["exercise"]
                                
                                # Add a title if missing
                                if "title" not in ex:
                                    file_name = os.path.basename(file_path).replace(".json", "")
                                    if "chapter_index" in ex:
                                        ex["title"] = f"If Statements: {ex['chapter_index']}"
                                    elif "if_else_basics" in file_name:
                                        ex["title"] = f"Basic If-Else (Exercise {base_id_counter-1})"
                                    elif "if_elif_else_chains" in file_name:
                                        ex["title"] = f"If-Elif-Else Chains (Exercise {base_id_counter-1})"
                                    elif "complex_conditionals" in file_name:
                                        ex["title"] = f"Complex Conditionals (Exercise {base_id_counter-1})"
                                    else:
                                        ex["title"] = f"If Statements (Exercise {base_id_counter-1})"
                                
                                all_if_exercises.append(ex)
                        else:
                            logger.info(f"Found single exercise in {os.path.basename(file_path)}")
                            
                            # Process the single exercise
                            ex = dict(data)
                            
                            # Add ID if missing
                            if "id" not in ex:
                                ex["id"] = f"if_statements_{base_id_counter}"
                                base_id_counter += 1
                            
                            # Add chapter_id if not present
                            if "chapter_id" not in ex:
                                ex["chapter_id"] = "Chapter3_Statements"
                            
                            # Copy exercise to instructions if instructions is missing
                            if "instructions" not in ex and "exercise" in ex:
                                ex["instructions"] = ex["exercise"]
                            
                            # Add a title if missing
                            if "title" not in ex:
                                file_name = os.path.basename(file_path).replace(".json", "")
                                if "chapter_index" in ex:
                                    ex["title"] = f"If Statements: {ex['chapter_index']}"
                                else:
                                    ex["title"] = f"If Statements (Exercise {base_id_counter-1})"
                            
                            all_if_exercises.append(ex)
                except Exception as e:
                    logger.error(f"Error loading {file_path}: {str(e)}")
        
        # If we found any exercises, return them
        if all_if_exercises:
            logger.info(f"Returning {len(all_if_exercises)} if statement exercises")
            return all_if_exercises
        
        # If no files found, return mock data
        logger.warning("No if statement files found, returning mock data")
        return [
            {
                "id": "mock_if_statements_1",
                "title": "Basic If-Else Statements",
                "difficulty": "beginner",
                "chapter_id": "Chapter3_Statements",
                "description": "Conditional statements let your program make decisions.",
                "instructions": "Write an if-else statement that checks if a number is positive, negative, or zero.",
                "starterCode": "# Test the if-else statement with different values\nnum = 10\n\n# Your code here\nif num > 0:\n    print(f\"{num} is positive\")\nelif num < 0:\n    print(f\"{num} is negative\")\nelse:\n    print(f\"{num} is zero\")\n\n# Try changing the value of num and see what happens"
            },
            {
                "id": "mock_if_statements_2",
                "title": "Nested If Statements",
                "difficulty": "intermediate",
                "chapter_id": "Chapter3_Statements",
                "description": "If statements can be nested inside other if statements.",
                "instructions": "Create a nested if structure to check age groups and gender.",
                "starterCode": "# Nested if statements\nage = 25\ngender = \"female\"\n\nif age < 18:\n    print(\"Under 18\")\n    if gender == \"male\":\n        print(\"Boy\")\n    else:\n        print(\"Girl\")\nelse:\n    print(\"Adult\")\n    if gender == \"male\":\n        print(\"Man\")\n    else:\n        print(\"Woman\")\n\n# Try with different ages and genders"
            },
            {
                "id": "mock_if_statements_3",
                "title": "If-Elif Chain",
                "difficulty": "intermediate",
                "chapter_id": "Chapter3_Statements",
                "description": "Use elif to check multiple conditions in sequence.",
                "instructions": "Create an if-elif-else chain to assign letter grades based on a score.",
                "starterCode": "# Grade calculator\nscore = 85\n\nif score >= 90:\n    grade = \"A\"\nelif score >= 80:\n    grade = \"B\"\nelif score >= 70:\n    grade = \"C\"\nelif score >= 60:\n    grade = \"D\"\nelse:\n    grade = \"F\"\n\nprint(f\"Score: {score}, Grade: {grade}\")\n\n# Try with different scores"
            }
        ]
    except Exception as e:
        logger.error(f"Error fetching if statements: {str(e)}")
        # Return mock exercises rather than an error
        logger.warning(f"Returning mock if statements due to error: {str(e)}")
        return [
            {
                "id": "mock_if_error",
                "title": "If Statements (Error Fallback)",
                "difficulty": "beginner",
                "chapter_id": "Chapter3_Statements",
                "description": f"This is a mock exercise created due to an error: {str(e)}",
                "instructions": "Write a simple if-else statement to determine if a number is even or odd.",
                "starterCode": "# Check if a number is even or odd\nnum = 7\n\n# Your code here\nif num % 2 == 0:\n    print(f\"{num} is even\")\nelse:\n    print(f\"{num} is odd\")"
            }
        ]

@router.get("/exercises/raw/{file_path:path}")
async def get_raw_file(file_path: str):
    """
    Get the raw contents of a file for debugging purposes.
    """
    try:
        # Special case for combined strings file
        if file_path.endswith("04_strings.json") or file_path.endswith("strings.json"):
            logger.info(f"Special handling for combined strings file: {file_path}")
            
            # Get the chapter directory from file_path if it exists
            path_parts = file_path.split('/')
            chapter_dir = "Chapter1_DataObjects"  # Default
            
            if len(path_parts) > 1:
                # If a chapter directory is specified in the path, use it
                for part in path_parts:
                    if part.startswith("Chapter"):
                        chapter_dir = part
                        break
            
            # Construct paths for part1 and part2
            part1_path = os.path.join(EXERCISES_DIR, chapter_dir, "04_strings_part1.json")
            part2_path = os.path.join(EXERCISES_DIR, chapter_dir, "04_strings_part2.json")
            
            combined_exercises = []
            
            # Load part1
            if os.path.exists(part1_path):
                logger.info(f"Found strings part1 file at: {part1_path}")
                with open(part1_path, 'r') as f:
                    try:
                        part1_exercises = json.load(f)
                        logger.info(f"Loaded {len(part1_exercises) if isinstance(part1_exercises, list) else 1} exercises from part1")
                        if isinstance(part1_exercises, list):
                            combined_exercises.extend(part1_exercises)
                        else:
                            combined_exercises.append(part1_exercises)
                    except json.JSONDecodeError as e:
                        logger.error(f"Error parsing part1 JSON: {str(e)}")
            
            # Load part2
            if os.path.exists(part2_path):
                logger.info(f"Found strings part2 file at: {part2_path}")
                with open(part2_path, 'r') as f:
                    try:
                        part2_exercises = json.load(f)
                        logger.info(f"Loaded {len(part2_exercises) if isinstance(part2_exercises, list) else 1} exercises from part2")
                        if isinstance(part2_exercises, list):
                            combined_exercises.extend(part2_exercises)
                        else:
                            combined_exercises.append(part2_exercises)
                    except json.JSONDecodeError as e:
                        logger.error(f"Error parsing part2 JSON: {str(e)}")
            
            logger.info(f"Returning {len(combined_exercises)} combined string exercises")
            return combined_exercises
        
        # Special case for strings_part2 file
        if file_path.endswith("04_strings_part2.json") or file_path.endswith("strings_part2.json"):
            logger.info(f"Special handling for strings_part2 file: {file_path}")
            
            # Construct the full path
            full_path = os.path.join(EXERCISES_DIR, file_path)
            if os.path.exists(full_path):
                logger.info(f"Found strings_part2 file at: {full_path}")
                with open(full_path, 'r') as f:
                    try:
                        data = json.load(f)
                        logger.info(f"Successfully loaded {len(data) if isinstance(data, list) else 1} exercises from strings_part2 file")
                        return data
                    except json.JSONDecodeError as e:
                        logger.error(f"Error parsing strings_part2 JSON: {str(e)}")
        
        # Special case for strings_part1 file
        if file_path.endswith("04_strings_part1.json") or file_path.endswith("strings_part1.json"):
            logger.info(f"Special handling for strings_part1 file: {file_path}")
            
            # Construct the full path
            full_path = os.path.join(EXERCISES_DIR, file_path)
            if os.path.exists(full_path):
                logger.info(f"Found strings_part1 file at: {full_path}")
                with open(full_path, 'r') as f:
                    try:
                        data = json.load(f)
                        logger.info(f"Successfully loaded {len(data) if isinstance(data, list) else 1} exercises from strings_part1 file")
                        return data
                    except json.JSONDecodeError as e:
                        logger.error(f"Error parsing strings_part1 JSON: {str(e)}")
        
        # Special case for string_methods_capitalize file
        if file_path.endswith("05_string_methods_capitalize.json") or file_path.endswith("string_methods_capitalize.json"):
            logger.info(f"Special handling for string_methods_capitalize file: {file_path}")
            
            # Construct the full path
            full_path = os.path.join(EXERCISES_DIR, file_path)
            if os.path.exists(full_path):
                logger.info(f"Found string_methods_capitalize file at: {full_path}")
                with open(full_path, 'r') as f:
                    try:
                        data = json.load(f)
                        logger.info(f"Successfully loaded {len(data) if isinstance(data, list) else 1} exercises from string_methods_capitalize file")
                        return data
                    except json.JSONDecodeError as e:
                        logger.error(f"Error parsing string_methods_capitalize JSON: {str(e)}")
        
        # Special case for string_methods_lower file
        if file_path.endswith("05_string_methods_lower.json") or file_path.endswith("string_methods_lower.json"):
            logger.info(f"Special handling for string_methods_lower file: {file_path}")
            
            # Construct the full path
            full_path = os.path.join(EXERCISES_DIR, file_path)
            if os.path.exists(full_path):
                logger.info(f"Found string_methods_lower file at: {full_path}")
                with open(full_path, 'r') as f:
                    try:
                        data = json.load(f)
                        logger.info(f"Successfully loaded {len(data) if isinstance(data, list) else 1} exercises from string_methods_lower file")
                        return data
                    except json.JSONDecodeError as e:
                        logger.error(f"Error parsing string_methods_lower JSON: {str(e)}")
        
        # Special case for string_methods_split file
        if file_path.endswith("05_string_methods_split.json") or file_path.endswith("string_methods_split.json"):
            logger.info(f"Special handling for string_methods_split file: {file_path}")
            
            # Construct the full path
            full_path = os.path.join(EXERCISES_DIR, file_path)
            if os.path.exists(full_path):
                logger.info(f"Found string_methods_split file at: {full_path}")
                with open(full_path, 'r') as f:
                    try:
                        data = json.load(f)
                        logger.info(f"Successfully loaded {len(data) if isinstance(data, list) else 1} exercises from string_methods_split file")
                        return data
                    except json.JSONDecodeError as e:
                        logger.error(f"Error parsing string_methods_split JSON: {str(e)}")
        
        # Special case for string_methods_upper file
        if file_path.endswith("05_string_methods_upper.json") or file_path.endswith("string_methods_upper.json"):
            logger.info(f"Special handling for string_methods_upper file: {file_path}")
            
            # Construct the full path
            full_path = os.path.join(EXERCISES_DIR, file_path)
            if os.path.exists(full_path):
                logger.info(f"Found string_methods_upper file at: {full_path}")
                with open(full_path, 'r') as f:
                    try:
                        data = json.load(f)
                        logger.info(f"Successfully loaded {len(data) if isinstance(data, list) else 1} exercises from string_methods_upper file")
                        return data
                    except json.JSONDecodeError as e:
                        logger.error(f"Error parsing string_methods_upper JSON: {str(e)}")
        
        # Construct the full path
        full_path = os.path.join(EXERCISES_DIR, file_path)
        logger.info(f"Attempting to load raw file from: {full_path}")
        
        # Check if the file exists
        if os.path.exists(full_path):
            logger.info(f"Found file at: {full_path}")
            with open(full_path, 'r') as f:
                content = f.read()
                try:
                    # Try to parse as JSON
                    data = json.loads(content)
                    logger.info(f"Successfully loaded JSON data from {file_path}")
                    return data
                except json.JSONDecodeError:
                    # If not valid JSON, return as text
                    logger.warning(f"File {file_path} is not valid JSON, returning as text")
                    return {"content": content, "is_text": True}
        else:
            # Try to find a similar file
            logger.warning(f"File not found at: {full_path}")
            
            # Get the directory and filename
            dir_path = os.path.dirname(full_path)
            file_name = os.path.basename(full_path)
            
            # First check - exact match in any chapter directory
            additional_search_paths = []
            
            # Add standard chapter directories
            for chapter_dir in ["Chapter1_DataObjects", "Chapter2_Operators", "Chapter3_Statements", 
                               "Chapter4_MethodsFunctions", "Chapter5_OOP", "Chapter6_ModulesPackages"]:
                additional_search_paths.append(os.path.join(EXERCISES_DIR, chapter_dir))
            
            # Also search in raw exercises directory
            for search_dir in additional_search_paths:
                if os.path.exists(search_dir):
                    candidate_path = os.path.join(search_dir, file_name)
                    logger.info(f"Checking for file at: {candidate_path}")
                    if os.path.exists(candidate_path):
                        logger.info(f"Found file at alternate location: {candidate_path}")
                        with open(candidate_path, 'r') as f:
                            content = f.read()
                            try:
                                # Try to parse as JSON
                                data = json.loads(content)
                                logger.info(f"Successfully loaded JSON data from alternate location {candidate_path}")
                                return data
                            except json.JSONDecodeError:
                                # If not valid JSON, return as text
                                logger.warning(f"File at alternate location {candidate_path} is not valid JSON, returning as text")
                                return {"content": content, "is_text": True}
            
            # If still not found, try fuzzy search in each directory
            logger.info("Trying fuzzy search for similar filenames")
            for search_dir in additional_search_paths:
                if not os.path.exists(search_dir):
                    continue
                    
                files = os.listdir(search_dir)
                logger.info(f"Files in directory {search_dir}: {files}")
                
                # Try to find a similar file
                topic_pattern = re.sub(r'^\d+_', '', os.path.splitext(file_name)[0])
                similar_files = [f for f in files if topic_pattern.lower() in f.lower()]
                
                if similar_files:
                    logger.info(f"Found similar files in {search_dir}: {similar_files}")
                    # Use the first similar file
                    similar_file = os.path.join(search_dir, similar_files[0])
                    logger.info(f"Using similar file: {similar_file}")
                    with open(similar_file, 'r') as f:
                        content = f.read()
                        try:
                            # Try to parse as JSON
                            data = json.loads(content)
                            logger.info(f"Successfully loaded JSON data from similar file {similar_files[0]}")
                            return data
                        except json.JSONDecodeError:
                            # If not valid JSON, return as text
                            logger.warning(f"Similar file {similar_files[0]} is not valid JSON, returning as text")
                            return {"content": content, "is_text": True}
            
            # If we get here, we couldn't find the file or a similar one
            logger.error(f"File not found and no similar files found: {file_path}")
            
            # Return mock data for common paths
            if "object_types" in file_path.lower():
                logger.info("Returning mock object_types exercises")
                return [
                    {
                        "id": "mock_object_types_1",
                        "title": "Python Object Types (Integers)",
                        "difficulty": "beginner",
                        "chapter_id": "Chapter1_DataObjects",
                        "description": "Learn about Python's fundamental data types.",
                        "instructions": "Experiment with Python's integer type. Try arithmetic operations with integers.",
                        "starterCode": "# Integer operations\na = 5\nb = 10\n\n# Addition\nprint(a + b)  # 15\n\n# Subtraction\nprint(b - a)  # 5\n\n# Multiplication\nprint(a * b)  # 50\n\n# Division (returns float)\nprint(b / a)  # 2.0\n\n# Integer division (returns integer)\nprint(b // a)  # 2\n\n# Modulo (remainder)\nprint(b % a)  # 0\n\n# Exponentiation\nprint(a ** 2)  # 25"
                    },
                    {
                        "id": "mock_object_types_2",
                        "title": "Python Object Types (Floats)",
                        "difficulty": "beginner",
                        "chapter_id": "Chapter1_DataObjects",
                        "description": "Learn about Python's floating-point numbers.",
                        "instructions": "Experiment with Python's float type. Observe the precision of floating-point arithmetic.",
                        "starterCode": "# Float operations\nx = 3.14\ny = 2.5\n\nprint(x + y)  # 5.64\nprint(x - y)  # 0.64\nprint(x * y)  # 7.85\nprint(x / y)  # 1.256\n\n# Floating point precision\nprint(0.1 + 0.2)  # 0.30000000000000004\nprint(0.1 + 0.2 == 0.3)  # False\n\n# Using round to handle precision issues\nprint(round(0.1 + 0.2, 1) == 0.3)  # True"
                    },
                    {
                        "id": "mock_object_types_3",
                        "title": "Python Object Types (Strings)",
                        "difficulty": "beginner",
                        "chapter_id": "Chapter1_DataObjects",
                        "description": "Learn about Python's string type.",
                        "instructions": "Experiment with Python's string type and common string operations.",
                        "starterCode": "# String operations\nname = \"Python\"\n\n# Length of string\nprint(len(name))  # 6\n\n# Accessing characters (indexing)\nprint(name[0])  # 'P'\nprint(name[-1])  # 'n'\n\n# Slicing\nprint(name[0:2])  # 'Py'\nprint(name[2:])  # 'thon'\n\n# Concatenation\nprint(name + \" Programming\")  # 'Python Programming'\n\n# Repetition\nprint(name * 3)  # 'PythonPythonPython'\n\n# Methods\nprint(name.upper())  # 'PYTHON'\nprint(name.lower())  # 'python'\nprint(\"  whitespace  \".strip())  # 'whitespace'"
                    }
                ]
            elif "comparison_operators" in file_path.lower():
                logger.info("Returning mock comparison_operators exercise")
                return [{
                    "id": "mock_comparison_operators",
                    "title": "Comparison Operators in Python",
                    "difficulty": "beginner",
                    "description": "Learn about Python's comparison operators.",
                    "instructions": "Try out different comparison operators and observe the results",
                    "starterCode": "# Equal to (==)\nx = 5\ny = 10\nprint(f\"x == y: {x == y}\")\n\n# Not equal to (!=)\nprint(f\"x != y: {x != y}\")\n\n# Greater than (>)\nprint(f\"x > y: {x > y}\")\n\n# Less than (<)\nprint(f\"x < y: {x < y}\")\n\n# Greater than or equal to (>=)\nprint(f\"x >= y: {x >= y}\")\n\n# Less than or equal to (<=)\nprint(f\"x <= y: {x <= y}\")"
                }]
            elif "if_statements" in file_path.lower():
                logger.info("Returning mock if_statements exercise")
                return [{
                    "id": "mock_if_statements",
                    "title": "Python If Statements",
                    "difficulty": "beginner",
                    "description": "Learn about conditional execution with if statements.",
                    "instructions": "Try out if-elif-else statements to handle different conditions",
                    "starterCode": "# Basic if statement\nx = 10\n\nif x > 0:\n    print(\"x is positive\")\n\n# if-else statement\ny = -5\n\nif y > 0:\n    print(\"y is positive\")\nelse:\n    print(\"y is negative or zero\")\n\n# if-elif-else chain\nz = 0\n\nif z > 0:\n    print(\"z is positive\")\nelif z < 0:\n    print(\"z is negative\")\nelse:\n    print(\"z is zero\")"
                }]
            
            raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    except Exception as e:
        logger.error(f"Error fetching raw file {file_path}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching file: {str(e)}")

@router.get("/exercises/topic-map")
async def get_topic_map():
    """
    Get a mapping of topic names to file paths to help troubleshoot missing exercises.
    """
    try:
        logger.info("Getting topic map")
        result = {}
        
        # Recursively walk through the exercises directory
        for root, dirs, files in os.walk(EXERCISES_DIR):
            for file in files:
                if file.endswith('.json'):
                    # Get the relative path from EXERCISES_DIR
                    rel_path = os.path.relpath(os.path.join(root, file), EXERCISES_DIR)
                    
                    # Extract topic name from filename (remove extension and numbering)
                    topic_name = os.path.splitext(file)[0]
                    # Remove any leading digits and underscores (e.g., "01_object_types" -> "object_types")
                    topic_name = re.sub(r'^\d+_', '', topic_name)
                    
                    # Group by topic name
                    if topic_name not in result:
                        result[topic_name] = []
                    
                    result[topic_name].append(rel_path)
        
        logger.info(f"Found {len(result)} topics")
        return {"topics": result}
    except Exception as e:
        logger.error(f"Error getting topic map: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting topic map: {str(e)}")
        