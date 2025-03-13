#!/usr/bin/env python3

"""
Direct fix for string methods topics in app/routes/exercises.py

This file contains a direct fix to ensure each string method topic
maps to its correct JSON file.

Usage:
1. Place this file in the app/ directory
2. Add import in app/routes/exercises.py: from app.string_methods_fix import fix_string_method_topic
3. In get_topic_direct function, add early:
   # Check for string method topics
   string_method_result = fix_string_method_topic(topic_id)
   if string_method_result:
       return string_method_result
4. Remove or comment out any existing string method handlers
"""

import os
import json
import logging

logger = logging.getLogger(__name__)

def fix_string_method_topic(topic_id):
    """
    Maps string method topics to their correct JSON files.
    Returns processed exercises or None if not a string method topic.
    """
    # Check if this is a string method topic
    topic_id_lower = topic_id.lower()
    
    # Map topics to their correct file
    if "capitalize" in topic_id_lower or "05_string_methods_capitalize" in topic_id_lower:
        method = "capitalize"
        filename = "05_string_methods_capitalize.json"
    elif "lower" in topic_id_lower or "05_string_methods_lower" in topic_id_lower:
        method = "lower"
        filename = "05_string_methods_lower.json"
    elif "upper" in topic_id_lower or "05_string_methods_upper" in topic_id_lower:
        method = "upper"
        filename = "05_string_methods_upper.json"
    elif "split" in topic_id_lower or "05_string_methods_split" in topic_id_lower:
        method = "split"
        filename = "05_string_methods_split.json"
    else:
        # Not a string method topic
        return None
    
    # Get the exercises directory path
    exercises_dir = os.getenv("EXERCISES_DIR", "/Users/henry/Desktop/Learning/Projects/Python Learn/python-learning-platform/exercises")
    chapter_dir = os.path.join(exercises_dir, "Chapter1_DataObjects")
    file_path = os.path.join(chapter_dir, filename)
    
    logger.info(f"String method detected: {method}. Using file {filename} for topic {topic_id}")
    
    if os.path.exists(file_path):
        logger.info(f"Found string methods {method} file at: {file_path}")
        try:
            with open(file_path, 'r') as f:
                exercises = json.load(f)
                logger.info(f"Loaded {len(exercises) if isinstance(exercises, list) else 1} string methods {method} exercises")
                
                # Process exercises
                processed_exercises = []
                if isinstance(exercises, list):
                    for ex in exercises:
                        # Add required fields
                        ex_id = ex.get("id", f"string_methods_{method}_{len(processed_exercises) + 1}")
                        ex_title = ex.get("title", f"String Methods {method.capitalize()} Exercise {len(processed_exercises) + 1}")
                        ex_difficulty = ex.get("difficulty", "beginner")
                        ex_chapter_id = ex.get("chapter_id", "Chapter1_DataObjects")
                        
                        ex["id"] = ex_id
                        ex["title"] = ex_title
                        ex["difficulty"] = ex_difficulty
                        ex["chapter_id"] = ex_chapter_id
                        
                        processed_exercises.append(ex)
                
                logger.info(f"Returning {len(processed_exercises)} string methods {method} exercises")
                return processed_exercises
        except Exception as e:
            logger.error(f"Error loading string methods {method}: {str(e)}")
    else:
        logger.error(f"File not found: {file_path}")
    
    return None 