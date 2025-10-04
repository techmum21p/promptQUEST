"""
Gamified Prompt Engineering Training App using Google ADK and Vertex AI
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Any
from google.adk.agents import Agent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get configuration from environment variables
llm_model = os.getenv('LLM_MODEL', 'gemini-2.5-flash')

class PromptEvaluatorAgent:
    """Agent that evaluates prompt quality using Gemini"""
    
    def __init__(self):
        # Initialize the ADK Agent with Gemini
        self.agent = Agent(
            name="prompt_evaluator",
            model=llm_model,
            description="Expert agent that evaluates prompt engineering quality",
            instruction="""You are an expert prompt engineering evaluator. 
            Your job is to assess user prompts based on:
            1. Clarity (25 points): Is the prompt clear and unambiguous?
            2. Specificity (25 points): Does it provide enough context and details?
            3. Structure (25 points): Is it well-organized with proper formatting?
            4. Task Alignment (25 points): Does it align with the given scenario/goal?
            
            You MUST return your evaluation as a JSON object with this EXACT structure (no additional text):
            {
                "clarity_score": <number 0-25>,
                "specificity_score": <number 0-25>,
                "structure_score": <number 0-25>,
                "task_alignment_score": <number 0-25>,
                "total_score": <number 0-100>,
                "feedback": "<detailed constructive feedback string>",
                "strengths": ["<strength1>", "<strength2>"],
                "improvements": ["<improvement1>", "<improvement2>"]
            }
            
            Be constructive but honest. Provide specific examples of what works and what could be improved.
            IMPORTANT: Only return valid JSON with the exact field names shown above. Do not include markdown code blocks or any other text.
            """
        )
    
    async def evaluate_prompt(self, user_prompt: str, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a user's prompt against a scenario"""
        
        evaluation_request = f"""
        SCENARIO:
        {scenario['title']}
        {scenario['description']}
        Goal: {scenario['goal']}
        Context: {scenario['context']}
        
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
        
        # Use Google Gemini directly via the genai library for Vertex AI
        try:
            import google.genai as genai
            from google.genai.types import GenerateContentConfig
            import os
            
            # Get Vertex AI configuration from environment
            project = os.getenv('GOOGLE_CLOUD_PROJECT')
            location = os.getenv('GOOGLE_CLOUD_LOCATION')
            llm_model = os.getenv('LLM_MODEL', 'gemini-2.5-flash')
            
            # Initialize the client for Vertex AI
            client = genai.Client(vertexai=True, project=project, location=location)
            
            # Generate content using the model
            response = client.models.generate_content(
                model=llm_model,
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
                    "clarity_score": 15,
                    "specificity_score": 15,
                    "structure_score": 15,
                    "task_alignment_score": 15,
                    "total_score": 60,
                    "feedback": response_text if response_text else "Unable to parse evaluation",
                    "strengths": ["Prompt submitted"],
                    "improvements": ["Try again with more detail"]
                }
        
        except Exception as e:
            # If direct Gemini call fails, return a fallback evaluation
            return {
                "clarity_score": 15,
                "specificity_score": 15,
                "structure_score": 15,
                "task_alignment_score": 15,
                "total_score": 60,
                "feedback": f"Evaluation service unavailable: {str(e)}",
                "strengths": ["Prompt submitted"],
                "improvements": ["Try again later"]
            }


class AIScenarioGenerator:
    """AI Agent that generates new scenarios dynamically based on level"""
    
    def __init__(self):
        # Initialize the ADK Agent for scenario generation
        self.agent = Agent(
            name="scenario_generator",
            model=llm_model,
            description="Expert agent that generates Microsoft 365 Copilot training scenarios",
            instruction="""You are an expert Microsoft 365 Copilot trainer and scenario designer. 
            Your job is to generate realistic, practical training scenarios for prompt engineering practice.
            
            You MUST return your scenario as a JSON object with this EXACT structure:
            {
                "id": "<level_prefix><number>",
                "title": "<Clear, specific title>",
                "description": "<2-3 sentence scenario description>",
                "goal": "<What the user needs to accomplish>",
                "context": "<Relevant background information>",
                "product": "<Microsoft 365 product (e.g., 'Excel Copilot', 'Teams Copilot', etc.)>",
                "hints": ["<hint1>", "<hint2>", "<hint3>"],
                "example_good": "<Example of a well-crafted prompt for this scenario>"
            }
            
            Guidelines:
            - Make scenarios realistic and business-relevant
            - Ensure difficulty matches the requested level
            - Include specific Microsoft 365 products
            - Provide actionable hints
            - Create diverse scenarios (avoid repetition)
            - Focus on real workplace challenges
            
            IMPORTANT: Only return valid JSON with the exact field names shown above. Do not include markdown code blocks or any other text.
            """
        )
    
    async def generate_scenario(self, level: str, existing_scenarios: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate a new scenario for the specified level"""
        
        # Create few-shot examples from existing scenarios
        examples_text = ""
        if existing_scenarios:
            examples_text = "\n\nHere are examples of well-crafted scenarios for this level:\n"
            for i, scenario in enumerate(existing_scenarios[:2]):  # Use first 2 as examples
                examples_text += f"\nExample {i+1}:\n{json.dumps(scenario, indent=2)}\n"
        
        level_descriptions = {
            "beginner": "Simple, single-task scenarios requiring basic prompts. Focus on one Microsoft 365 product with straightforward goals.",
            "intermediate": "Multi-step scenarios requiring more detailed prompts. May involve data analysis, content creation, or coordination across products.",
            "advanced": "Complex scenarios requiring sophisticated prompts. Often involve strategic thinking, multiple products, automation, or enterprise-level challenges."
        }
        
        generation_request = f"""
        Generate a NEW Microsoft 365 Copilot training scenario for {level.upper()} level.
        
        Level Requirements:
        {level_descriptions.get(level, level_descriptions["beginner"])}
        
        {examples_text}
        
        Create a unique scenario that:
        1. Is different from the examples above
        2. Matches the {level} difficulty level
        3. Uses a Microsoft 365 product appropriately
        4. Represents a realistic workplace challenge
        5. Follows the exact JSON structure required
        
        Generate the scenario and return ONLY the JSON object with no additional text.
        Use id prefix: "{level[0]}" followed by a number (e.g., "b4", "i4", "a4").
        """
        
        try:
            import google.genai as genai
            from google.genai.types import GenerateContentConfig
            import os
            
            # Get Vertex AI configuration from environment
            project = os.getenv('GOOGLE_CLOUD_PROJECT')
            location = os.getenv('GOOGLE_CLOUD_LOCATION')
            llm_model = os.getenv('LLM_MODEL', 'gemini-2.5-flash')
            
            # Initialize the client for Vertex AI
            client = genai.Client(vertexai=True, project=project, location=location)
            
            # Generate content using the model
            response = client.models.generate_content(
                model=llm_model,
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


class CopilotScenarioGenerator:
    """Generates Microsoft 365 Copilot specific scenarios"""
    
    def __init__(self):
        self.ai_generator = AIScenarioGenerator()
    
    @staticmethod
    def get_scenarios() -> Dict[str, List[Dict[str, Any]]]:
        """Returns preset scenarios organized by difficulty level (for few-shot prompting)"""
        
        scenarios = {
            "beginner": [
                {
                    "id": "b1",
                    "title": "Email Summarization in Outlook",
                    "description": "You need to catch up on a long email thread about the Q4 marketing campaign.",
                    "goal": "Get a concise summary of the key decisions and action items",
                    "context": "You've been out of office for a week and there's a 15-email thread in your inbox",
                    "product": "Outlook Copilot",
                    "hints": ["Be specific about what you want summarized", "Mention action items", "Consider timeframe"],
                    "example_good": "Summarize the key decisions and action items from the Q4 marketing campaign email thread from the past week"
                },
                {
                    "id": "b2",
                    "title": "Document Formatting in Word",
                    "description": "You have a 10-page report that needs professional formatting.",
                    "goal": "Apply consistent formatting throughout the document",
                    "context": "The document has inconsistent fonts, spacing, and heading styles",
                    "product": "Word Copilot",
                    "hints": ["Specify what elements to format", "Mention consistency", "Be clear about style preferences"],
                    "example_good": "Apply consistent professional formatting to this report: use Arial 11pt for body text, Arial 14pt bold for headings, 1.15 line spacing, and ensure uniform margins"
                },
                {
                    "id": "b3",
                    "title": "Meeting Preparation in Teams",
                    "description": "You have an upcoming team meeting about project status.",
                    "goal": "Create a meeting agenda based on recent discussions",
                    "context": "You need to prepare for a 1-hour weekly sync meeting",
                    "product": "Teams Copilot",
                    "hints": ["Mention the meeting purpose", "Reference past discussions", "Specify time allocation"],
                    "example_good": "Create a 1-hour meeting agenda for our weekly project sync, including status updates, blockers, and next steps based on last week's action items"
                }
            ],
            "intermediate": [
                {
                    "id": "i1",
                    "title": "Data Analysis in Excel",
                    "description": "You have sales data for Q1-Q3 and need to identify trends.",
                    "goal": "Generate insights about sales performance and create visualizations",
                    "context": "Dataset includes sales by region, product category, and month",
                    "product": "Excel Copilot",
                    "hints": ["Specify what insights you need", "Mention visualization preferences", "Include comparative analysis"],
                    "example_good": "Analyze Q1-Q3 sales data to identify top-performing regions and product categories. Create a pivot table showing monthly trends and a chart comparing regional performance. Highlight any concerning patterns."
                },
                {
                    "id": "i2",
                    "title": "Presentation Creation in PowerPoint",
                    "description": "You need to create a presentation for executive stakeholders.",
                    "goal": "Generate a compelling deck about project ROI",
                    "context": "You have project metrics, budget data, and timeline information",
                    "product": "PowerPoint Copilot",
                    "hints": ["Define your audience", "Specify content structure", "Mention data sources", "Include visual requirements"],
                    "example_good": "Create a 10-slide executive presentation on Project Phoenix's ROI. Include: executive summary, problem statement, solution overview, key metrics (cost savings, efficiency gains), timeline, risks, and next steps. Use our corporate template with data visualizations. Target audience: C-suite executives."
                },
                {
                    "id": "i3",
                    "title": "Cross-Product Workflow",
                    "description": "You need to compile information from multiple sources.",
                    "goal": "Create a comprehensive status report using data from Teams, Outlook, and SharePoint",
                    "context": "Weekly status report due to management",
                    "product": "Microsoft 365 Copilot",
                    "hints": ["Mention all data sources", "Specify output format", "Include time range", "Define key sections"],
                    "example_good": "Create a weekly status report for the Data Migration project by synthesizing information from: Teams channel discussions, email threads with 'Data Migration' in subject from past week, and updates from the SharePoint project site. Include sections: accomplishments, challenges, metrics, and next week's priorities. Format as a Word document."
                }
            ],
            "advanced": [
                {
                    "id": "a1",
                    "title": "Strategic Analysis in Business Chat",
                    "description": "Senior leadership wants competitive analysis for strategic planning.",
                    "goal": "Generate comprehensive competitive intelligence report",
                    "context": "Need to analyze competitors, market trends, and strategic recommendations",
                    "product": "Microsoft 365 Copilot (Business Chat)",
                    "hints": ["Define scope clearly", "Specify analysis framework", "Mention multiple data sources", "Include strategic recommendations", "Define output structure"],
                    "example_good": "Conduct a competitive analysis for our SaaS product in the CRM space. Analyze: 1) Top 5 competitors' feature sets, pricing, and market positioning (search recent industry reports in SharePoint 'Market Research' folder). 2) Our differentiation opportunities based on customer feedback from past 6 months (Outlook and Teams). 3) Market trends from analyst reports. 4) Strategic recommendations with 3-year roadmap implications. Deliverable: 5-page Word report with executive summary, SWOT analysis, competitive matrix, and prioritized recommendations."
                },
                {
                    "id": "a2",
                    "title": "Complex Automation Workflow",
                    "description": "Automate a multi-step business process across Microsoft 365.",
                    "goal": "Design and document an automated workflow for customer onboarding",
                    "context": "Process involves Forms, SharePoint, Teams, and Outlook",
                    "product": "Power Automate + Copilot",
                    "hints": ["Map entire process", "Specify each integration point", "Include error handling", "Define success metrics", "Consider security/compliance"],
                    "example_good": "Design an automated customer onboarding workflow: 1) When Microsoft Forms 'New Customer' is submitted, create SharePoint folder with customer name. 2) Auto-generate welcome email via Outlook with onboarding checklist. 3) Create Teams channel for customer project and invite relevant team members based on service tier. 4) Set up recurring check-in reminders in Teams for account manager. Include error notifications to admin team, compliance checks for data fields, and dashboard showing onboarding completion rates. Document each step with trigger conditions and fallback procedures."
                },
                {
                    "id": "a3",
                    "title": "Enterprise Knowledge Synthesis",
                    "description": "Create a comprehensive knowledge base article from scattered information.",
                    "goal": "Synthesize tribal knowledge into structured documentation",
                    "context": "Information is spread across Teams chats, emails, SharePoint docs, and meeting transcripts",
                    "product": "Microsoft 365 Copilot",
                    "hints": ["Define knowledge domain", "Specify all sources", "Include structure requirements", "Mention verification needs", "Consider audience and accessibility"],
                    "example_good": "Create a comprehensive 'Cloud Migration Best Practices' knowledge base article by synthesizing information from: 1) Past 12 months Teams 'Cloud Engineering' channel discussions tagged 'migration'. 2) Email threads from cloudops@company.com with subject containing 'migration lessons'. 3) SharePoint 'Post-Mortem' folder documents. 4) Recorded meeting transcripts from monthly architecture reviews. Structure: Executive Summary, Prerequisites, Step-by-step Process, Common Pitfalls & Solutions, Tooling Recommendations, Security Checklist, Case Studies (2-3 internal examples), FAQs. Include inline code examples, architecture diagrams descriptions, and cross-references to related docs. Target audience: intermediate-to-advanced cloud engineers. Verify all technical recommendations with the latest internal standards from SharePoint 'Governance' site."
                }
            ]
        }
        
        return scenarios
    
    @staticmethod
    def get_random_scenario(level: str) -> Dict[str, Any]:
        """Get a random scenario from specified difficulty level (preset only)"""
        import random
        scenarios = CopilotScenarioGenerator.get_scenarios()
        return random.choice(scenarios.get(level, scenarios["beginner"]))
    
    async def get_ai_generated_scenario(self, level: str) -> Dict[str, Any]:
        """Get an AI-generated scenario for the specified level"""
        # Use preset scenarios as few-shot examples
        preset_scenarios = self.get_scenarios().get(level, [])
        return await self.ai_generator.generate_scenario(level, preset_scenarios)
    
    async def get_mixed_scenario(self, level: str, ai_probability: float = 0.3) -> Dict[str, Any]:
        """Get either a preset or AI-generated scenario based on probability"""
        import random
        
        if random.random() < ai_probability:
            # Generate new AI scenario
            return await self.get_ai_generated_scenario(level)
        else:
            # Use preset scenario
            return self.get_random_scenario(level)
    
    def get_scenario_stats(self) -> Dict[str, int]:
        """Get statistics about available scenarios"""
        scenarios = self.get_scenarios()
        return {
            "beginner_count": len(scenarios["beginner"]),
            "intermediate_count": len(scenarios["intermediate"]),
            "advanced_count": len(scenarios["advanced"]),
            "total_preset": sum(len(scenarios[level]) for level in scenarios)
        }


class UserProgressTracker:
    """Tracks user progress and scores"""
    
    def __init__(self, storage_file: str = "user_progress.json"):
        self.storage_file = storage_file
        self.data = self._load_data()
    
    def _load_data(self) -> Dict:
        """Load user progress from file"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    # Validate the structure
                    if not isinstance(data, dict) or 'users' not in data or 'leaderboard' not in data:
                        print(f"Warning: Invalid JSON structure in {self.storage_file}, creating new file")
                        return {"users": {}, "leaderboard": []}
                    return data
            except json.JSONDecodeError as e:
                print(f"Error: Corrupted JSON file {self.storage_file}: {e}")
                print("Creating backup and initializing new data...")
                # Create backup of corrupted file
                backup_name = f"{self.storage_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                try:
                    import shutil
                    shutil.copy2(self.storage_file, backup_name)
                    print(f"Backup created: {backup_name}")
                except Exception as backup_error:
                    print(f"Could not create backup: {backup_error}")
                # Return fresh data structure
                return {"users": {}, "leaderboard": []}
            except Exception as e:
                print(f"Unexpected error loading {self.storage_file}: {e}")
                return {"users": {}, "leaderboard": []}
        return {"users": {}, "leaderboard": []}
    
    def _save_data(self):
        """Save user progress to file"""
        try:
            # Create a temporary file first to avoid corruption
            temp_file = f"{self.storage_file}.tmp"
            with open(temp_file, 'w') as f:
                json.dump(self.data, f, indent=2)
            
            # If write was successful, replace the original file
            import shutil
            shutil.move(temp_file, self.storage_file)
        except Exception as e:
            print(f"Error saving data to {self.storage_file}: {e}")
            # Clean up temp file if it exists
            temp_file = f"{self.storage_file}.tmp"
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
    
    def add_user(self, username: str):
        """Add a new user"""
        if username not in self.data["users"]:
            self.data["users"][username] = {
                "total_score": 0,
                "attempts": 0,
                "skill_level": "beginner",
                "badges": [],
                "history": []
            }
            self._save_data()
    
    def record_attempt(self, username: str, scenario_id: str, score: int, evaluation: Dict, user_prompt: str = ""):
        """Record a user's attempt"""
        if username not in self.data["users"]:
            self.add_user(username)
        
        user = self.data["users"][username]
        user["attempts"] += 1
        user["total_score"] += score
        user["history"].append({
            "timestamp": datetime.now().isoformat(),
            "scenario_id": scenario_id,
            "score": score,
            "evaluation": evaluation,
            "user_prompt": user_prompt
        })
        
        # Update skill level based on performance
        avg_score = user["total_score"] / user["attempts"]
        if avg_score >= 85 and user["attempts"] >= 5:
            user["skill_level"] = "advanced"
        elif avg_score >= 70 and user["attempts"] >= 3:
            user["skill_level"] = "intermediate"
        
        # Award badges
        self._check_and_award_badges(username)
        
        # Update leaderboard
        self._update_leaderboard(username)
        
        # Auto-backup every few users
        self.auto_backup_to_csv()
        
        self._save_data()
    
    def _check_and_award_badges(self, username: str):
        """Check and award badges based on performance"""
        user = self.data["users"][username]
        badges = user["badges"]
        
        # Perfect Score badge
        if any(h["score"] == 100 for h in user["history"]) and "Perfect Score" not in badges:
            badges.append("Perfect Score")
        
        # Consistent Performer badge (3 attempts with score > 80)
        high_scores = [h for h in user["history"] if h["score"] > 80]
        if len(high_scores) >= 3 and "Consistent Performer" not in badges:
            badges.append("Consistent Performer")
        
        # Dedicated Learner badge (10 attempts)
        if user["attempts"] >= 10 and "Dedicated Learner" not in badges:
            badges.append("Dedicated Learner")
        
        # Advanced Master badge (5 advanced scenarios with avg > 85)
        advanced_attempts = [h for h in user["history"] if h["scenario_id"].startswith("a")]
        if len(advanced_attempts) >= 5:
            avg_advanced = sum(h["score"] for h in advanced_attempts) / len(advanced_attempts)
            if avg_advanced > 85 and "Advanced Master" not in badges:
                badges.append("Advanced Master")
    
    def _update_leaderboard(self, username: str):
        """Update the leaderboard"""
        user = self.data["users"][username]
        avg_score = user["total_score"] / user["attempts"] if user["attempts"] > 0 else 0
        
        # Remove existing entry
        self.data["leaderboard"] = [
            entry for entry in self.data["leaderboard"] 
            if entry["username"] != username
        ]
        
        # Add new entry
        self.data["leaderboard"].append({
            "username": username,
            "avg_score": round(avg_score, 2),
            "total_attempts": user["attempts"],
            "skill_level": user["skill_level"],
            "badges": len(user["badges"])
        })
        
        # Sort by average score
        self.data["leaderboard"].sort(key=lambda x: x["avg_score"], reverse=True)
    
    def get_user_stats(self, username: str) -> Dict:
        """Get user statistics"""
        if username not in self.data["users"]:
            return None
        return self.data["users"][username]
    
    def get_leaderboard(self, top_n: int = 10) -> List[Dict]:
        """Get top N users from leaderboard"""
        return self.data["leaderboard"][:top_n]
    
    def export_to_csv(self, filename: str = None) -> str:
        """Export user data to CSV for analysis"""
        import pandas as pd
        
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"user_progress_export_{timestamp}.csv"
        
        # Flatten data for CSV
        rows = []
        for username, data in self.data["users"].items():
            if data["history"]:  # Only include users with attempts
                for attempt in data["history"]:
                    eval_data = attempt.get('evaluation', {})
                    user_prompt = attempt.get('user_prompt', '')
                    strengths = eval_data.get('strengths', [])
                    improvements = eval_data.get('improvements', [])
                    rows.append({
                        'username': username,
                        'timestamp': attempt['timestamp'],
                        'scenario_id': attempt['scenario_id'],
                        'total_score': attempt['score'],
                        'clarity_score': eval_data.get('clarity_score', 0),
                        'specificity_score': eval_data.get('specificity_score', 0),
                        'structure_score': eval_data.get('structure_score', 0),
                        'task_alignment_score': eval_data.get('task_alignment_score', 0),
                        'skill_level': data['skill_level'],
                        'total_attempts': data['attempts'],
                        'cumulative_score': data['total_score'],
                        'avg_score': round(data['total_score'] / data['attempts'], 2) if data['attempts'] > 0 else 0,
                        'badges_count': len(data['badges']),
                        'badges': ', '.join(data['badges']) if data['badges'] else '',
                        'user_prompt': user_prompt,
                        'strengths': '; '.join(strengths) if strengths else '',
                        'improvements': '; '.join(improvements) if improvements else '',
                        'feedback_summary': eval_data.get('feedback', '')[:100] + '...' if len(eval_data.get('feedback', '')) > 100 else eval_data.get('feedback', '')
                    })
            else:  # Include users without attempts for completeness
                rows.append({
                    'username': username,
                    'timestamp': '',
                    'scenario_id': '',
                    'total_score': 0,
                    'clarity_score': 0,
                    'specificity_score': 0,
                    'structure_score': 0,
                    'task_alignment_score': 0,
                    'skill_level': data['skill_level'],
                    'total_attempts': data['attempts'],
                    'cumulative_score': data['total_score'],
                    'avg_score': 0,
                    'badges_count': len(data['badges']),
                    'badges': ', '.join(data['badges']) if data['badges'] else '',
                    'user_prompt': '',
                    'strengths': '',
                    'improvements': '',
                    'feedback_summary': 'No attempts yet'
                })
        
        if rows:
            df = pd.DataFrame(rows)
            # Sort by username and timestamp for better organization
            df = df.sort_values(['username', 'timestamp'], na_position='last')
            df.to_csv(filename, index=False)
            return filename
        else:
            return None
    
    def auto_backup_to_csv(self):
        """Automatically backup data to CSV periodically"""
        total_users = len(self.data["users"])
        if total_users > 0 and total_users % 5 == 0:  # Every 5 users
            filename = self.export_to_csv()
            if filename:
                print(f"Auto-backup created: {filename}")
    
    def get_export_summary(self) -> Dict:
        """Get summary statistics for export"""
        total_users = len(self.data["users"])
        total_attempts = sum(user["attempts"] for user in self.data["users"].values())
        active_users = len([u for u in self.data["users"].values() if u["attempts"] > 0])
        
        avg_score_all = 0
        if total_attempts > 0:
            total_score_all = sum(user["total_score"] for user in self.data["users"].values())
            avg_score_all = round(total_score_all / total_attempts, 2)
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "total_attempts": total_attempts,
            "avg_score_all_users": avg_score_all,
            "leaderboard_size": len(self.data["leaderboard"])
        }


# Main execution functions for integration with Streamlit
async def evaluate_user_prompt_async(user_prompt: str, scenario: Dict[str, Any]) -> Dict[str, Any]:
    """Async function to evaluate user prompt"""
    evaluator = PromptEvaluatorAgent()
    return await evaluator.evaluate_prompt(user_prompt, scenario)


def get_scenarios_by_level(level: str) -> List[Dict[str, Any]]:
    """Get all preset scenarios for a skill level"""
    return CopilotScenarioGenerator.get_scenarios()[level]


def get_random_scenario_by_level(level: str) -> Dict[str, Any]:
    """Get random preset scenario by level"""
    return CopilotScenarioGenerator.get_random_scenario(level)


async def get_ai_scenario_by_level(level: str) -> Dict[str, Any]:
    """Get AI-generated scenario by level"""
    generator = CopilotScenarioGenerator()
    return await generator.get_ai_generated_scenario(level)


async def get_mixed_scenario_by_level(level: str, ai_probability: float = 0.3) -> Dict[str, Any]:
    """Get either preset or AI-generated scenario based on probability"""
    generator = CopilotScenarioGenerator()
    return await generator.get_mixed_scenario(level, ai_probability)


def get_scenario_statistics() -> Dict[str, int]:
    """Get statistics about available scenarios"""
    generator = CopilotScenarioGenerator()
    return generator.get_scenario_stats()