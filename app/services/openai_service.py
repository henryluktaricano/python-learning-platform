import os
import json
from typing import Dict, Any, Optional
from openai import AsyncOpenAI
from ..database.token_db import save_token_usage

# Initialize OpenAI client
client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

async def get_code_evaluation(
    code: str,
    exercise_id: str,
    expected_output: Optional[str] = None,
    question: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Submit code to OpenAI for evaluation and feedback.
    
    Args:
        code: The user's Python code to evaluate
        exercise_id: The identifier for the exercise
        expected_output: The expected output of the code, if applicable
        question: The exercise question or prompt
        metadata: Additional metadata about the exercise
        
    Returns:
        Dictionary containing feedback, correctness assessment, 
        alternative solutions, and mistake explanations
    """
    try:
        # Create system prompt for code evaluation
        system_prompt = """
        You are an AI Python tutor providing feedback on code exercises. Evaluate the submitted code against the provided requirements and expected output.
        
        Your evaluation should include:
        1. Correctness assessment (Is the code correct? Does it solve the problem?)
        2. Code quality feedback (Is the code well-written, efficient, and following Python best practices?)
        3. Alternative solutions, if applicable (What are other ways to solve this problem?)
        4. Explanations of mistakes, if applicable
        
        Format your response as a JSON object with the following structure:
        {
            "correctness": "CORRECT" or "INCORRECT",
            "overall_feedback": "Overall assessment of the code",
            "detailed_feedback": "Detailed evaluation of the code",
            "alternative_solutions": ["Alternative solution 1", "Alternative solution 2"],
            "mistakes": [{
                "description": "Description of mistake",
                "suggestion": "How to fix it"
            }]
        }
        """
        
        # Build user prompt with exercise details
        user_prompt = f"Exercise ID: {exercise_id}\n\n"
        
        if question:
            user_prompt += f"Question/Prompt: {question}\n\n"
            
        if expected_output:
            user_prompt += f"Expected Output: {expected_output}\n\n"
            
        if metadata:
            user_prompt += f"Additional Information: {json.dumps(metadata)}\n\n"
            
        user_prompt += f"User's Code:\n```python\n{code}\n```\n\n"
        user_prompt += "Please evaluate this code and provide feedback."
        
        # Call OpenAI API
        response = await client.chat.completions.create(
            model="gpt-4",  # Using GPT-4 for best evaluation quality
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,  # Low temperature for more consistent evaluations
            response_format={"type": "json_object"}
        )
        
        # Extract JSON content from response
        content = response.choices[0].message.content
        feedback = json.loads(content)
        
        # Track token usage
        await save_token_usage(
            prompt_tokens=response.usage.prompt_tokens,
            completion_tokens=response.usage.completion_tokens,
            total_tokens=response.usage.total_tokens,
            model="gpt-4",
            endpoint="mark_exercise"
        )
        
        return feedback
        
    except Exception as e:
        print(f"Error in OpenAI service: {str(e)}")
        return {
            "correctness": "ERROR",
            "overall_feedback": f"An error occurred during evaluation: {str(e)}",
            "detailed_feedback": "Please try again or contact support if the issue persists.",
            "alternative_solutions": [],
            "mistakes": []
        } 