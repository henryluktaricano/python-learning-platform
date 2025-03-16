from fastapi import APIRouter, HTTPException
import os
import json
from typing import Dict, Any

router = APIRouter()

# Directory where notebooks are stored
NOTEBOOKS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "notebooks")

@router.get("/notes/{notebook_name}")
async def get_notes(notebook_name: str):
    """
    Get the markdown content from a Jupyter notebook.
    """
    try:
        # Ensure the filename has a .ipynb extension
        if not notebook_name.endswith('.ipynb'):
            notebook_name += '.ipynb'
            
        # Prevent path traversal attacks
        if '..' in notebook_name or '/' in notebook_name:
            raise HTTPException(status_code=400, detail="Invalid notebook name")
            
        notebook_path = os.path.join(NOTEBOOKS_DIR, notebook_name)
        
        # Check if the notebook exists
        if not os.path.exists(notebook_path):
            raise HTTPException(status_code=404, detail=f"Notebook {notebook_name} not found")
            
        # Parse the notebook and extract markdown and code cells
        with open(notebook_path, "r") as f:
            notebook = json.load(f)
            
        markdown_content = []
        
        # Process each cell
        for cell in notebook.get("cells", []):
            cell_type = cell.get("cell_type")
            
            if cell_type == "markdown":
                # Add markdown cells directly
                markdown_content.append("".join(cell.get("source", [])))
                
            elif cell_type == "code":
                # Add code cells with proper formatting
                code = "".join(cell.get("source", []))
                markdown_content.append(f"```python\n{code}\n```")
        
        # Combine all markdown content
        result = "\n\n".join(markdown_content)
        return {"markdown": result}
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Notebook {notebook_name} not found")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail=f"Invalid JSON in notebook {notebook_name}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 