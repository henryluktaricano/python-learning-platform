#!/usr/bin/env python3

"""
Script to apply the string methods fix to the app/routes/exercises.py file.

This script:
1. Copies the string_methods_fix.py file to the app/ directory
2. Modifies the app/routes/exercises.py file to use the fix
3. Removes the redundant individual string method handlers

Usage:
python3 apply_fix.py
"""

import os
import re
import shutil
import sys

def main():
    print("Applying string methods fix...")
    
    # 1. Check if app directory exists
    if not os.path.exists("app"):
        print("Error: 'app' directory not found.")
        print("Please run this script from the root directory of your project.")
        return False
    
    # 2. Copy the string_methods_fix.py file to app/ directory
    source_fix = "app/string_methods_fix.py"
    if not os.path.exists(source_fix):
        print(f"Error: Source fix file '{source_fix}' not found.")
        return False
    
    # 3. Check if exercises.py file exists
    exercises_file = "app/routes/exercises.py"
    if not os.path.exists(exercises_file):
        print(f"Error: Exercises file '{exercises_file}' not found.")
        return False
    
    # 4. Read the exercises.py file
    try:
        with open(exercises_file, 'r') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {exercises_file}: {str(e)}")
        return False
    
    # 5. Check if the fix is already applied
    if "from app.string_methods_fix import fix_string_method_topic" in content:
        print("The fix appears to already be applied.")
        return True
    
    # 6. Create a backup of the original file
    backup_file = f"{exercises_file}.bak"
    try:
        shutil.copy2(exercises_file, backup_file)
        print(f"Created backup file: {backup_file}")
    except Exception as e:
        print(f"Warning: Failed to create backup file: {str(e)}")
        
    # 7. Add the import statement - Try multiple patterns
    import_statement = "from app.string_methods_fix import fix_string_method_topic"
    
    # Try different patterns for finding the import section
    import_patterns = [
        r'(import.*\n+)(?=@router)',
        r'(from.*import.*\n+)(?=@router)',
        r'(import.*\n+|from.*import.*\n+)+',
        r'(from app\.routes.*\n)'
    ]
    
    import_added = False
    for pattern in import_patterns:
        match = re.search(pattern, content)
        if match:
            import_position = match.end()
            content = content[:import_position] + "\n" + import_statement + "\n" + content[import_position:]
            import_added = True
            print("Added import statement.")
            break
    
    if not import_added:
        # Last resort: add at the top of the file
        content = import_statement + "\n\n" + content
        print("Added import statement at the top of the file.")
    
    # 8. Find the get_topic_direct function
    function_patterns = [
        r'async def get_topic_direct\(topic_id: str\):.*?\n\s+try:',
        r'def get_topic_direct\(.*?\):.*?\n\s+try:',
        r'async def get_topic_direct\(.*?\):.*?\n',
    ]
    
    # Add the fix code to the get_topic_direct function
    fix_code = """
        # Check for string method topics
        string_method_result = fix_string_method_topic(topic_id)
        if string_method_result:
            return string_method_result
    """
    
    function_found = False
    for pattern in function_patterns:
        function_match = re.search(pattern, content, re.DOTALL)
        if function_match:
            function_found = True
            
            # Try to insert after "try:" if it exists
            if "try:" in function_match.group(0):
                content = content.replace(function_match.group(0), 
                                     f"{function_match.group(0)}\n{fix_code}")
            else:
                # Insert after the function definition line
                function_def_end = content.find("\n", function_match.start()) + 1
                content = content[:function_def_end] + fix_code + content[function_def_end:]
            
            print("Added fix code to get_topic_direct function.")
            break
    
    if not function_found:
        # Manual search for any get_topic_direct function
        position = content.find("def get_topic_direct")
        if position == -1:
            position = content.find("async def get_topic_direct")
        
        if position != -1:
            # Find the end of the line
            line_end = content.find("\n", position) + 1
            # Add the fix code
            content = content[:line_end] + fix_code + content[line_end:]
            function_found = True
            print("Added fix code after get_topic_direct function definition.")
    
    if not function_found:
        print("Error: Could not locate the get_topic_direct function.")
        print("Please manually add the fix code:")
        print(fix_code)
        return False
    
    # 9. Write the modified content back to the file
    try:
        with open(exercises_file, 'w') as f:
            f.write(content)
        print(f"Successfully updated {exercises_file}")
    except Exception as e:
        print(f"Error writing to {exercises_file}: {str(e)}")
        return False
    
    print("""
Fix applied successfully!

Next steps:
1. You should comment out or remove the individual string method handlers
   in the get_topic_direct function (search for "string_methods_capitalize" etc.)
2. Restart your application using:
   python3 run_backend.py

After these changes, each string method topic (capitalize, lower, split, upper)
should correctly map to its corresponding JSON file.
""")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 