"""
Gamified Prompt Engineering Training App using Google ADK, Vertex AI, and PostgreSQL
This version includes PostgreSQL integration for user management and progress tracking.
"""

import os
import json
import asyncio
import hashlib
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from google.adk.agents import Agent
from dotenv import load_dotenv

# Import our database services
from database.service import (
    UserService, ProgressService, BadgeService, LeaderboardService,
    UserData, ProgressData, BadgeData, LeaderboardEntry
)
from database.config import init_database, close_database

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
        
        # Use Google Gemini directly via the genai library
        try:
            import google.genai as genai
            from google.genai.types import GenerateContentConfig
            import os
            
            # Check which authentication method to use
            use_vertex_ai = os.getenv('GOOGLE_GENAI_USE_VERTEXAI', 'false').lower() == 'true'
            llm_model = os.getenv('LLM_MODEL', 'gemini-2.5-flash')
            
            if use_vertex_ai:
                # Vertex AI configuration
                project = os.getenv('GOOGLE_CLOUD_PROJECT')
                location = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')
                
                if not project:
                    raise ValueError("GOOGLE_CLOUD_PROJECT environment variable is required for Vertex AI")
                
                # Initialize the client for Vertex AI
                client = genai.Client(vertexai=True, project=project, location=location)
            else:
                # Google AI Studio configuration
                api_key = os.getenv('GOOGLE_API_KEY')
                
                if not api_key:
                    raise ValueError("GOOGLE_API_KEY environment variable is required for Google AI Studio")
                
                # Initialize the client for Google AI Studio
                client = genai.Client(api_key=api_key)
            
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
            # If direct Gemini call fails, return a helpful fallback evaluation
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
            
            # Check which authentication method to use
            use_vertex_ai = os.getenv('GOOGLE_GENAI_USE_VERTEXAI', 'false').lower() == 'true'
            llm_model = os.getenv('LLM_MODEL', 'gemini-2.5-flash')
            
            if use_vertex_ai:
                # Vertex AI configuration
                project = os.getenv('GOOGLE_CLOUD_PROJECT')
                location = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')
                
                if not project:
                    raise ValueError("GOOGLE_CLOUD_PROJECT environment variable is required for Vertex AI")
                
                # Initialize the client for Vertex AI
                client = genai.Client(vertexai=True, project=project, location=location)
            else:
                # Google AI Studio configuration
                api_key = os.getenv('GOOGLE_API_KEY')
                
                if not api_key:
                    raise ValueError("GOOGLE_API_KEY environment variable is required for Google AI Studio")
                
                # Initialize the client for Google AI Studio
                client = genai.Client(api_key=api_key)

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


class UserProgressTrackerDB:
    """Tracks user progress and scores using PostgreSQL database"""
    
    def __init__(self):
        self.user_service = UserService()
        self.progress_service = ProgressService()
        self.badge_service = BadgeService()
        self.leaderboard_service = LeaderboardService()
        self.current_session = {}  # Track current session users
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256 (in production, use more secure hashing)"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    async def authenticate_user(self, ldap_id: str, password: str) -> Optional[UserData]:
        """Authenticate user with LDAP ID and password"""
        try:
            user = await self.user_service.get_user_by_ldap_id(ldap_id)
            if user and user.password_hash == self._hash_password(password):
                # Update last login
                await self.user_service.update_user_last_login(user.id)
                self.current_session[user.ldap_id] = user
                return user
        except Exception as e:
            print(f"Authentication error: {e}")
        return None
    
    async def register_user(self, ldap_id: str, username: str, password: str, email: str, group: str) -> Optional[UserData]:
        """Register a new user"""
        try:
            # Check if user already exists
            existing_user = await self.user_service.get_user_by_ldap_id(ldap_id)
            if existing_user:
                print(f"User with LDAP ID {ldap_id} already exists")
                return None
            
            user_data = UserData(
                ldap_id=ldap_id,
                username=username,
                password_hash=self._hash_password(password),
                email_address=email,
                user_group=group
            )
            
            user = await self.user_service.create_user(user_data)
            print(f"User {username} registered successfully")
            return user
            
        except Exception as e:
            print(f"Registration error: {e}")
            return None
    
    async def record_attempt(self, ldap_id: str, scenario_id: str, score: int, evaluation: Dict, user_prompt: str = ""):
        """Record a user's attempt with automatic batch processing"""
        try:
            # Get user
            user = await self.user_service.get_user_by_ldap_id(ldap_id)
            if not user:
                print(f"User {ldap_id} not found")
                return
            
            # Get current attempt number
            progress_summary = await self.progress_service.get_user_progress_summary(ldap_id)
            attempt_number = 1 if not progress_summary else progress_summary['total_attempts'] + 1
            
            # Create progress entry
            progress_data = ProgressData(
                ldap_id=ldap_id,
                attempt_number=attempt_number,
                scenario_id=scenario_id,
                user_prompt=user_prompt,
                total_score=evaluation['total_score'],
                clarity_score=evaluation.get('clarity_score', 0),
                specificity_score=evaluation.get('specificity_score', 0),
                structure_score=evaluation.get('structure_score', 0),
                task_alignment_score=evaluation.get('task_alignment_score', 0),
                skill_level="beginner",  # Will be updated by database trigger
                feedback=evaluation.get('feedback', ''),
                strengths=evaluation.get('strengths', []),
                improvements=evaluation.get('improvements', [])
            )
            
            # For immediate recording (as requested), create the entry directly
            await self.progress_service.create_progress_entry(progress_data)
            
            # Check and award badges
            await self.badge_service.check_and_award_badges(ldap_id, progress_data)
            
            print(f"Recorded attempt #{attempt_number} for {ldap_id}: Score {score}")
            
        except Exception as e:
            print(f"Error recording attempt: {e}")
    
    async def get_user_stats(self, ldap_id: str) -> Optional[Dict]:
        """Get user statistics"""
        try:
            return await self.progress_service.get_user_progress_summary(ldap_id)
        except Exception as e:
            print(f"Error getting user stats: {e}")
            return None
    
    async def get_leaderboard(self, top_n: int = 10, group: str = None) -> List[LeaderboardEntry]:
        """Get leaderboard data"""
        try:
            return await self.leaderboard_service.get_leaderboard(limit=top_n, group=group)
        except Exception as e:
            print(f"Error getting leaderboard: {e}")
            return []
    
    async def get_multi_group_leaderboard(self, limit_per_group: int = 20) -> Dict[str, List[LeaderboardEntry]]:
        """Get leaderboard data organized by groups plus overall"""
        try:
            return await self.leaderboard_service.get_multi_group_leaderboard(limit_per_group)
        except Exception as e:
            print(f"Error getting multi-group leaderboard: {e}")
            return {}
    
    async def export_user_data(self, ldap_id: str = None) -> Dict[str, Any]:
        """Export user data (single user or all users)"""
        try:
            if ldap_id:
                # Single user export
                user_stats = await self.get_user_stats(ldap_id)
                recent_attempts = await self.progress_service.get_user_recent_attempts(ldap_id, limit=50)
                badges = []
                if user_stats:
                    user = await self.user_service.get_user_by_ldap_id(ldap_id)
                    if user:
                        badges = await self.badge_service.get_user_badges(user.id)
                
                return {
                    "user_stats": user_stats,
                    "recent_attempts": recent_attempts,
                    "badges": badges,
                    "export_timestamp": datetime.now(timezone.utc).isoformat()
                }
            else:
                # All users export
                leaderboard_data = await self.get_leaderboard(limit=1000)
                return {
                    "leaderboard": leaderboard_data,
                    "export_timestamp": datetime.now(timezone.utc).isoformat(),
                    "total_users": len(leaderboard_data)
                }
                
        except Exception as e:
            print(f"Error exporting data: {e}")
            return {}


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


# Initialize database services
async def init_app():
    """Initialize the application"""
    await init_database()
    print("Application initialized with PostgreSQL database")


async def cleanup_app():
    """Cleanup the application"""
    await close_database()
    print("Application cleaned up")


if __name__ == "__main__":
    async def test_app():
        """Test the application"""
        await init_app()
        
        # Test database services
        try:
            tracker = UserProgressTrackerDB()
            
            # Test user registration
            print("Testing user registration...")
            test_user = await tracker.register_user(
                ldap_id="test001",
                username="testuser", 
                password="testpass",
                email="test@company.com",
                group="test"
            )
            
            if test_user:
                print(f"✓ User created: {test_user.username}")
            
            # Test authentication
            print("Testing authentication...")
            auth_user = await tracker.authenticate_user("test001", "testpass")
            if auth_user:
                print(f"✓ User authenticated: {auth_user.username}")
            
            print("Application test completed successfully")
            
        except Exception as e:
            print(f"Application test failed: {e}")
        
        await cleanup_app()
    
    asyncio.run(test_app())
