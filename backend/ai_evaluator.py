"""
Simplified AI Evaluator using Google AI Studio (free API)
"""

import os
import json
import google.genai as genai
from google.genai.types import GenerateContentConfig
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class PromptEvaluatorAgent:
    """Agent that evaluates prompt quality using Google AI Studio"""
    
    def __init__(self):
        # Use Google AI Studio (free API)
        self.api_key = os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        
        # Initialize client for Google AI Studio
        self.client = genai.Client(api_key=self.api_key)
        self.model = os.getenv('LLM_MODEL', 'gemini-2.0-flash-exp')
    
    async def evaluate_prompt(self, user_prompt: str, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a user's prompt against a scenario"""
        
        evaluation_request = f"""
        SCENARIO:
        {scenario.get('title', 'Prompt Engineering Scenario')}
        {scenario.get('description', '')}
        Goal: {scenario.get('goal', '')}
        Context: {scenario.get('context', '')}
        
        USER'S PROMPT:
        {user_prompt}
        
        Evaluate this prompt and return ONLY a valid JSON object with your evaluation.
        Use this EXACT format with these EXACT field names:
        {{
            "clarity_score": <number 0-25>,
            "specificity_score": <number 0-25>,
            "structure_score": <number 0-25>,
            "task_alignment_score": <number 0-25>,
            "total_score": <sum of above scores>,
            "feedback": "<detailed constructive feedback>",
            "strengths": ["<strength1>", "<strength2>"],
            "improvements": ["<improvement1>", "<improvement2>"]
        }}
        
        Do not include any text before or after the JSON. Do not use markdown code blocks.
        """
        
        try:
            # Generate content using the model
            response = self.client.models.generate_content(
                model=self.model,
                contents=evaluation_request,
                config=GenerateContentConfig(
                    temperature=0.4,
                    max_output_tokens=3072
                )
            )
            
            # Extract the response text
            response_text = ""
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    for part in candidate.content.parts:
                        if hasattr(part, 'text') and part.text:
                            response_text += part.text
            
            # Parse the JSON response
            try:
                # Clean up response (remove markdown code blocks if present)
                response_text = response_text.strip()
                if response_text.startswith("```json"):
                    response_text = response_text[7:]
                if response_text.startswith("```"):
                    response_text = response_text[3:]
                if response_text.endswith("```"):
                    response_text = response_text[:-3]
                response_text = response_text.strip()
                
                evaluation = json.loads(response_text)
                return evaluation
            except json.JSONDecodeError as e:
                # Fallback if JSON parsing fails
                return {
                    "clarity_score": 0,
                    "specificity_score": 0,
                    "structure_score": 0,
                    "task_alignment_score": 0,
                    "total_score": 0,
                    "feedback": f"Evaluation parsing failed. Raw response: {response_text[:200]}..." if response_text else "Unable to parse LLM evaluation response",
                    "strengths": [],
                    "improvements": ["Ensure prompt is clear and specific", "Try rephrasing your prompt", "Contact support if issue persists"]
                }
        
        except Exception as e:
            # If API call fails, return a helpful fallback evaluation
            error_str = str(e).lower()
            is_api_key_error = "api_key" in error_str or "invalid_argument" in error_str or "authentication" in error_str
            
            if is_api_key_error:
                return {
                    "clarity_score": 0,
                    "specificity_score": 0,
                    "structure_score": 0,
                    "task_alignment_score": 0,
                    "total_score": 0,
                    "feedback": "Configuration Error: Invalid API key. Please contact your administrator to update the Google API key configuration.",
                    "strengths": [],
                    "improvements": ["Check API key configuration", "Verify authentication credentials", "Contact system administrator"]
                }
            else:
                return {
                    "clarity_score": 0,
                    "specificity_score": 0,
                    "structure_score": 0,
                    "task_alignment_score": 0,
                    "total_score": 0,
                    "feedback": f"Evaluation service temporarily unavailable. Error: {str(e)}",
                    "strengths": [],
                    "improvements": ["Try again in a few minutes", "Check internet connection", "Contact technical support if issue persists"]
                }


class ScenarioGenerator:
    """Generate scenarios using Google AI Studio"""
    
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        
        self.client = genai.Client(api_key=self.api_key)
        self.model = os.getenv('LLM_MODEL', 'gemini-2.0-flash-exp')
    
    async def generate_scenario(self, level: str) -> Dict[str, Any]:
        """Generate a new scenario for the specified level"""
        
        level_descriptions = {
            "beginner": "Simple, single-task scenarios requiring basic prompts. Focus on one Microsoft 365 product with straightforward goals.",
            "intermediate": "Multi-step scenarios requiring more detailed prompts. May involve data analysis, content creation, or coordination across products.",
            "advanced": "Complex scenarios requiring sophisticated prompts. Often involve strategic thinking, multiple products, automation, or enterprise-level challenges."
        }
        
        generation_request = f"""
        Generate a NEW Microsoft 365 Copilot training scenario for {level.upper()} level.
        
        Level Requirements:
        {level_descriptions.get(level, level_descriptions["beginner"])}
        
        Create a unique scenario that:
        1. Matches the {level} difficulty level
        2. Uses a Microsoft 365 product appropriately
        3. Represents a realistic workplace challenge
        4. Follows the exact JSON structure required
        
        Generate the scenario and return ONLY the JSON object with no additional text.
        Use id prefix: "{level[0]}" followed by a number (e.g., "b4", "i4", "a4").
        
        REQUIRED JSON FORMAT:
        {{
            "id": "<level_prefix><number>",
            "title": "<Clear, specific title>",
            "description": "<2-3 sentence scenario description>",
            "goal": "<What the.user needs to accomplish>",
            "context": "<Relevant background information>",
            "product": "<Microsoft 365 product (e.g., 'Excel Copilot', 'Teams Copilot', etc.)>",
            "hints": ["<hint1>", "<hint2>", "<hint3>"],
            "example_good": "<Example of a well-crafted prompt for this scenario>"
        }}
        """
        
        try:
            # Generate content using the model
            response = self.client.models.generate_content(
                model=self.model,
                contents=generation_request,
                config=GenerateContentConfig(
                    temperature=0.7,  # Higher creativity for scenario generation
                    max_output_tokens=2048
                )
            )
            
            # Extract the response text
            response_text = ""
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    for part in candidate.content.parts:
                        if hasattr(part, 'text') and part.text:
                            response_text += part.text
            
            # Parse the JSON response
            try:
                # Clean up response (remove markdown code blocks if present)
                response_text = response_text.strip()
                if response_text.startswith("```json"):
                    response_text = response_text[7:]
                if response_text.startswith("```"):
                    response_text = response_text[3:]
                if response_text.endswith("```"):
                    response_text = response_text[:-3]
                response_text = response_text.strip()
                
                scenario = json.loads(response_text)
                
                # Validate required fields
                required_fields = ["id", "title", "description", "goal", "context", "product", "hints", "example_good"]
                if all(field in scenario for field in required_fields):
                    return scenario
                else:
                    raise ValueError("Missing required fields in generated scenario")
            
            except (json.JSONDecodeError, ValueError) as e:
                # Fallback scenario if generation fails
                fallback_id = f"{level[0]}99"
                return {
                    "id": fallback_id,
                    "title": f"Custom {level.title()} Challenge",
                    "description": f"A {level} level Microsoft 365 Copilot scenario has been generated for your practice.",
                    "goal": "Practice your prompt engineering skills",
                    "context": "You need to create an effective prompt for this scenario",
                    "product": "Microsoft 365 Copilot",
                    "hints": ["Be specific in your request", "Provide clear context", "Include desired output format"],
                    "example_good": "Please help me create an effective prompt for this Microsoft 365 Copilot scenario"
                }
        
        except Exception as e:
            # Fallback scenario if API call fails
            fallback_id = f"{level[0]}99"
            return {
                "id": fallback_id,
                "title": f"Fallback {level.title()} Scenario",
                "description": f"Generate a prompt for a {level} level Microsoft 365 Copilot task.",
                "goal": "Create an effective prompt",
                "context": "Service temporarily unavailable",
                "product": "Microsoft 365 Copilot",
                "hints": ["Be specific", "Provide context", "Include format requirements"],
                "example_good": f"Create a {level} level prompt for Microsoft 365 Copilot that includes specific context and clear objectives"
            }


# Convenience functions for FastAPI
async def evaluate_prompt_simple(user_prompt: str, scenario: Dict[str, Any]) -> Dict[str, Any]:
    """Async function to evaluate user prompt using simplified evaluator"""
    evaluator = PromptEvaluatorAgent()
    return await evaluator.evaluate_prompt(user_prompt, scenario)


async def generate_ai_scenario_simple(level: str) -> Dict[str, Any]:
    """Generate AI scenario using simplified generator"""
    generator = ScenarioGenerator()
    return await generator.generate_scenario(level)
