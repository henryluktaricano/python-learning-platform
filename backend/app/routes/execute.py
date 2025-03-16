from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import subprocess
import tempfile
import os
import uuid
import logging

router = APIRouter()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CodeExecution(BaseModel):
    code: str

@router.post("/execute-code")
async def execute_code(code_execution: CodeExecution):
    """
    Execute Python code and return the output.
    
    This endpoint creates a temporary file with the provided code,
    executes it in a subprocess with a timeout, and returns the output.
    """
    try:
        # Generate a unique filename to avoid collisions
        file_id = str(uuid.uuid4())
        
        # Create a temporary file with the code
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as temp_file:
            temp_file_path = temp_file.name
            temp_file.write(code_execution.code.encode('utf-8'))
        
        logger.info(f"Executing code in temporary file: {temp_file_path}")
        
        # Execute the code with a timeout
        try:
            # Run the Python code in a subprocess
            process = subprocess.run(
                ['python', temp_file_path],
                capture_output=True,
                text=True,
                timeout=5  # 5 second timeout to prevent long-running code
            )
            
            # Check if there was an error
            if process.returncode != 0:
                return {"error": process.stderr}
            
            # Return the output
            return {"output": process.stdout}
            
        except subprocess.TimeoutExpired:
            return {"error": "Code execution timed out. Please optimize your code or reduce the input size."}
        except Exception as e:
            logger.error(f"Error executing code: {str(e)}")
            return {"error": f"Error executing code: {str(e)}"}
        
    except Exception as e:
        logger.error(f"Error in execute_code endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path) 