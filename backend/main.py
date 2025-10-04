"""
FastAPI Backend for Prompt Training Application
Modern async backend replacing Streamlit with proper database integration
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from typing import List, Optional, Dict, Any
import uvicorn
import logging
from datetime import datetime, timezone
import asyncio

# Import our database services
from database.service import (
    UserService, ProgressService, BadgeService, LeaderboardService,
    UserData, ProgressData, LeaderboardEntry
)
from database.config import init_database_services, close_database_services

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Prompt Training API",
    description="FastAPI backend for gamified prompt engineering training",
    version="1.0.0"
)

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Global services
user_service = UserService()
progress_service = ProgressService()
badge_service = BadgeService()
leaderboard_service = LeaderboardService()

@app.on_event("startup")
async def startup_event():
    """Initialize database services on startup"""
    try:
        await init_database_services()
        logger.info("✅ FastAPI backend started successfully")
    except Exception as e:
        logger.error(f"❌ Failed to start backend: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connections on shutdown"""
    await close_database_services()
    logger.info("✅ FastAPI backend shutdown complete")

# Dependency to get current user
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token"""
    # TODO: Implement JWT token validation
    # For now, return a mock user for development
    return {"ldap_id": "dev_user", "username": "Developer", "email": "dev@example.com"}

# Authentication endpoints
@app.post("/api/auth/login")
async def login(credentials: Dict[str, str]):
    """Authenticate user login"""
    try:
        ldap_id = credentials.get("ldap_id")
        password = credentials.get("password")
        
        # Validate credentials
        user = await user_service.get_user_by_ldap_id(ldap_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # TODO: Implement password verification
        # For now, accept any password for development
        
        # Update last login
        await user_service.update_user_last_login(user.id)
        
        # TODO: Generate JWT token
        token = "mock_jwt_token_" + str(datetime.now().timestamp())
        
        return {
            "token": token,
            "user": {
                "ldap_id": user.ldap_id,
                "username": user.username,
                "email": user.email_address,
                "group": user.user_group
            }
        }
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@app.post("/api/auth/register")
async def register(user_data: Dict[str, str]):
    """Register new user"""
    try:
        # Create user data
        new_user = UserData(
            ldap_id=user_data["ldap_id"],
            username=user_data["username"],
            password_hash=user_data["password"],  # TODO: Hash password
            email_address=user_data["email"],
            user_group=user_data.get("group", "default")
        )
        
        # Check if user already exists
        existing_user = await user_service.get_user_by_ldap_id(new_user.ldap_id)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists"
            )
        
        # Create user
        created_user = await user_service.create_user(new_user)
        
        return {
            "message": "User created successfully",
            "user": {
                "ldap_id": created_user.ldap_id,
                "username": created_user.username,
                "email": created_user.email_address
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

# User endpoints
@app.get("/api/user/profile")
async def get_user_profile(current_user: Dict = Depends(get_current_user)):
    """Get current user profile"""
    try:
        user = await user_service.get_user_by_ldap_id(current_user["ldap_id"])
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {
            "ldap_id": user.ldap_id,
            "username": user.username,
            "email": user.email_address,
            "group": user.user_group
        }
        
    except HTTPException:
        raise
    except Exception as o:
        logger.error(f"Profile error: {o}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get profile"
        )

@app.get("/api/user/stats")
async def get_user_stats(current_user: Dict = Depends(get_current_user)):
    """Get user progress statistics"""
    try:
        stats = await progress_service.get_user_progress_summary(current_user["ldap_id"])
        
        if not stats:
            # Return empty stats for new users
            return {
                "attempts": 0,
                "total_score": 0,
                "avg_score": 0,
                "current_skill_level": "beginner",
                "total_badges": 0,
                "last_activity": None,
                "badges": []
            }
        
        return {
            "attempts": stats["total_attempts"],
            "total_score": stats["total_score_cumaulative"],
            "avg_score": float(stats["avg_score"]),
            "current_skill_level": stats["current_skill_level"],
            "total_badges": stats["total_badges"],
            "last_activity": stats["last_activity"],
            "badges": stats["badges"] or []
        }
        
    except Exception as o:
        logger.error(f"Stats error: {o}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user stats"
        )

# Practice endpoints
@app.post("/api/practice/evaluate")
async def evaluate_prompt(
    evaluation_data: Dict[str, str],
    current_user: Dict = Depends(get_current_user)
):
    """Evaluate user's prompt against a scenario"""
    try:
        # Create a simple evaluation function using Google AI Studio
        from .ai_evaluator import evaluate_prompt_simple
        
        user_prompt = evaluation_data["prompt"]
        scenario = evaluation_data["scenario"]
        
        # Evaluate the prompt
        evaluation_result = await evaluate_prompt_simple(user_prompt, scenario)
        
        # Record progress
        progress_data = ProgressData(
            ldap_id=current_user["ldap_id"],
            attempt_number=1,  # TODO: Calculate actual attempt number
            scenario_id=scenario["id"],
            user_prompt=user_prompt,
            total_score=evaluation_result["total_score"],
            clarity_score=evaluation_result["clarity_score"],
            specificity_score=evaluation_result["specificity_score"],
            structure_score=evaluation_result["structure_score"],
            task_alignment_score=evaluation_result["task_alignment_score"],
            skill_level=current_user.get("skill_level", "beginner"),
            feedback=evaluation_result["feedback"],
            strengths=evaluation_result["strengths"],
            improvements=evaluation_result["improvements"]
        )
        
        # Save progress
        await progress_service.create_progress_entry(progress_data)
        
        # Check for new badges
        new_badges = await badge_service.check_and_award_badges(
            current_user["ldap_id"], 
            progress_data
        )
        
        return {
            "evaluation": evaluation_result,
            "new_badges": new_badges,
            "message": f"You earned {' and '.join(new_badges)}!" if new_badges else "Great work!"
        }
        
    except Exception as o:
        logger.error(f"Evaluation error: {o}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Evaluation failed"
        )

@app.get("/api/practice/scenarios")
async def get_scenarios(level: str = "beginner"):
    """Get scenarios for practice"""
    try:
        # Use built-in scenarios for now
        scenarios = {
            "beginner": [
                {
                    "id": "b1",
                    "title": "Email Summarization in Outlook",
                    "description": "You need to catch up on a long email thread about the Q4 marketing campaign.",
                    "goal": "Get a concise summary of the key decisions and action items",
                    "context": "You've been out of office for a week and there's a 15-email thread in your inbox",
                    "product": "Outlook Copilot"
                }
            ],
            "intermediate": [
                {
                    "id": "i1",
                    "title": "Data Analysis in Excel",
                    "description": "You have sales data for Q1-Q3 and need to identify trends.",
                    "goal": "Generate insights about sales performance and create visualizations",
                    "context": "Dataset includes sales by region, product category, and month",
                    "product": "Excel Copilot"
                }
            ],
            "advanced": [
                {
                    "id": "a1",
                    "title": "Strategic Analysis",
                    "description": "Senior leadership wants competitive analysis for strategic planning.",
                    "goal": "Generate comprehensive competitive intelligence report",
                    "context": "Need to analyze competitors, market trends, and strategic recommendations",
                    "product": "Microsoft 365 Copilot (Business Chat)"
                }
            ]
        }
        
        return scenarios.get(level, [])
        
    except Exception as o:
        logger.error(f"Scenarios error: {o}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get scenarios"
        )

@app.post("/api/practice/ai-scenario")
async def generate_ai_scenario(level_data: Dict[str, str]):
    """Generate AI scenario for practice"""
    try:
        from .ai_evaluator import generate_ai_scenario_simple
        
        level = level_data["level"]
        scenario = await generate_ai_scenario_simple(level)
        
        return scenario
        
    except Exception as o:
        logger.error(f"AI scenario error: {o}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate AI scenario"
        )

# Leaderboard endpoints
@app.get("/api/leaderboard")
async def get_leaderboard(limit: int = 10, group: Optional[str] = None):
    """Get leaderboard data"""
    try:
        if group:
            leaderboard = await leaderboard_service.get_leaderboard(limit, group)
        else:
            leaderboard = await leaderboard_service.get_leaderboard(limit)
        
        return [entry.__dict__ for entry in leaderboard]
        
    except Exception as o:
        logger.error(f"Leaderboard error: {o}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get leaderboard"
        )

@app.get("/api/leaderboard/multi-group")
async def get_multi_group_leaderboard(limit_per_group: int = 20):
    """Get leaderboard organized by groups"""
    try:
        leaderboard_data = await leaderboard_service.get_multi_group_leaderboard(limit_per_group)
        
        # Convert to dictionaries
        result = {}
        for group, entries in leaderboard_data.items():
            result[group] = [entry.__dict__ for entry in entries]
        
        return result
        
    except Exception as o:
        logger.error(f"Multi-group leaderboard error: {o}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get grouped leaderboard"
        )

# Progress endpoints
@app.get("/api/progress/history")
async def get_progress_history(
    limit: int = 10,
    current_user: Dict = Depends(get_current_user)
):
    """Get user's progress history"""
    try:
        attempts = await progress_service.get_user_recent_attempts(
            current_user["ldap_id"], 
            limit
        )
        
        return [attempt.__dict__ for attempt in attempts]
        
    except Exception as o:
        logger.error(f"Progress history error: {o}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get progress history"
        )

# Admin endpoints
@app.get("/api/admin/stats")
async def get_admin_stats(current_user: Dict = Depends(get_current_user)):
    """Get admin statistics"""
    try:
        # TODO: Implement admin authorization check
        
        # Get basic stats
        scenario_stats = {
            "beginner_count": 1,
            "intermediate_count": 1,
            "advanced_count": 1,
            "total_scenarios": 3
        }
        
        # Get user count and other admin data
        # This would require additional queries
        
        return {
            "scenario_stats": scenario_stats,
            "total_users": 0,  # TODO: Implement
            "active_users": 0,  # TODO: Implement
            "total_attempts": 0  # TODO: Implement
        }
        
    except Exception as o:
        logger.error(f"Admin stats error: {o}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get admin stats"
        )

# Health check
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
