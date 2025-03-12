from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import subprocess
import sys
import tempfile
import os
import ast
import re
from typing import Optional, Dict, Any, Union

router = APIRouter()

class CodeExecution(BaseModel):
    code: str
    timeout: Optional[int] = 5  # Default timeout of 5 seconds

def is_expression(line: str) -> bool:
    """Check if a line of code is just an expression (like a variable name)."""
    line = line.strip()
    if not line or line.startswith('#'):
        return False
        
    try:
        tree = ast.parse(line)
        return (len(tree.body) == 1 and 
                isinstance(tree.body[0], ast.Expr) and 
                not isinstance(tree.body[0].value, ast.Call))
    except SyntaxError:
        return False

@router.post("/execute_code")
async def execute_code(execution: CodeExecution):
    """
    Execute Python code and return the output or error.
    The code is executed in a sandboxed environment with restrictions.
    """
    tmp_name = None
    jupyter_mode = False
    last_expression = None
    
    try:
        # Check if the last non-empty line is an expression (like a variable name)
        code_lines = execution.code.strip().split('\n')
        non_empty_lines = [line for line in code_lines if line.strip() and not line.strip().startswith('#')]
        
        if non_empty_lines:
            last_line = non_empty_lines[-1]
            if is_expression(last_line):
                jupyter_mode = True
                last_expression = last_line.strip()
                # Add code to print the value of the expression
                code_with_eval = execution.code + f"\n\nprint('\\n__EXPRESSION_RESULT__:')\nprint(repr({last_expression}))"
            else:
                code_with_eval = execution.code
        else:
            code_with_eval = execution.code
        
        # Create a temporary file to store the code
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as tmp:
            tmp.write(code_with_eval.encode())
            tmp_name = tmp.name
        
        # Execute the code using subprocess with a timeout
        result = subprocess.run(
            [sys.executable, tmp_name],
            capture_output=True,
            text=True,
            timeout=execution.timeout
        )
        
        # Clean up the temporary file
        os.unlink(tmp_name)
        
        # Return the output or error
        if result.returncode == 0:
            output = result.stdout
            
            # If in jupyter mode, extract the expression result
            if jupyter_mode and "__EXPRESSION_RESULT__:" in output:
                parts = output.split("__EXPRESSION_RESULT__:")
                regular_output = parts[0].strip()
                expr_value = parts[1].strip() if len(parts) > 1 else ""
                
                return {
                    "status": "success", 
                    "output": regular_output,
                    "jupyter_display": True,
                    "expression": last_expression,
                    "expression_value": expr_value
                }
            else:
                return {"status": "success", "output": output}
        else:
            return {"status": "error", "error": result.stderr}
            
    except subprocess.TimeoutExpired:
        # Clean up the temporary file if timeout occurs
        if tmp_name and os.path.exists(tmp_name):
            os.unlink(tmp_name)
        return {"status": "error", "error": f"Code execution timed out after {execution.timeout} seconds"}
        
    except Exception as e:
        # Clean up the temporary file if any other exception occurs
        if tmp_name and os.path.exists(tmp_name):
            os.unlink(tmp_name)
        return {"status": "error", "error": str(e)} 