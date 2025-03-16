"""
Script to verify that all required packages are installed correctly.
"""
import sys
import importlib
import os

def check_import(module_name):
    try:
        module = importlib.import_module(module_name)
        version = getattr(module, "__version__", "unknown")
        print(f"✅ {module_name} imported successfully (version: {version})")
        return True
    except ImportError as e:
        print(f"❌ Failed to import {module_name}: {e}")
        return False

def main():
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print("\nChecking imports:")
    
    # List of packages to check
    packages = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "starlette",
        "typing_extensions",
        "openai"
    ]
    
    # Check each package
    all_successful = True
    for package in packages:
        if not check_import(package):
            all_successful = False
    
    # Print Python path
    print("\nPython path:")
    for path in sys.path:
        print(f"  - {path}")
    
    # Print virtual environment info
    print("\nVirtual environment:")
    venv_path = os.environ.get("VIRTUAL_ENV")
    if venv_path:
        print(f"  - Active: Yes")
        print(f"  - Path: {venv_path}")
    else:
        print(f"  - Active: No")
    
    return 0 if all_successful else 1

if __name__ == "__main__":
    sys.exit(main()) 