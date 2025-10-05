"""
FastAPI Backend for Prompt Engineering Training App
Recreating the Streamlit app functionality with modern FastAPI backend
Now with PostgreSQL integration and LDAP ID support
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import asyncio
from datetime import datetime

# Import the existing core functionality
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure Google API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    print("Warning: GOOGLE_API_KEY not found in environment variables")

from prompt_training_app import (
    evaluate_user_prompt_async,
    get_scenarios_by_level,
    get_random_scenario_by_level,
    get_ai_scenario_by_level,
    get_mixed_scenario_by_level,
    get_scenario_statistics,
    CopilotScenarioGenerator
)

# Import PostgreSQL components
from database import create_tables, get_db
from postgres_tracker import PostgreSQLUserProgressTracker
from sqlalchemy.orm import Session

# Initialize FastAPI app
app = FastAPI(
    title="Prompt Engineering Training API",
    description="Backend API for the Gamified Prompt Engineering Training App with PostgreSQL",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],  # Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables"""
    try:
        create_tables()
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error creating database tables: {e}")

# Global tracker instance
tracker = PostgreSQLUserProgressTracker()

# Pydantic models for request/response validation
class UserRequest(BaseModel):
    ldap_id: str
    username: str

class EvaluatePromptRequest(BaseModel):
    user_prompt: str
    scenario: Dict[str, Any]

class ScenarioGenerationRequest(BaseModel):
    level: str
    mode: str  # "preset", "ai", or "mixed"
    ai_probability: Optional[float] = 0.3

class AttemptRecord(BaseModel):
    ldap_id: str
    scenario_id: str
    user_prompt: str
    evaluation: Dict[str, Any]

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat(), "database": "postgresql"}

# User management endpoints
@app.post("/api/users")
async def add_user(request: UserRequest):
    """Add a new user with LDAP ID"""
    try:
        tracker.add_user(request.ldap_id, request.username)
        return {"message": f"User {request.username} with LDAP ID {request.ldap_id} added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/users/{ldap_id}/stats")
async def get_user_stats(ldap_id: str):
    """Get user statistics by LDAP ID"""
    stats = tracker.get_user_stats(ldap_id)
    if stats is None:
        raise HTTPException(status_code=404, detail="User not found")
    return stats

# Scenario management endpoints
@app.get("/api/scenarios/levels/{level}")
async def get_scenarios_by_difficulty(level: str):
    """Get all scenarios for a specific difficulty level"""
    try:
        scenarios = get_scenarios_by_level(level)
        return {"scenarios": scenarios, "level": level}
    except KeyError:
        raise HTTPException(status_code=404, detail="Invalid difficulty level")

@app.get("/api/scenarios/random/{level}")
async def get_random_scenario(level: str):
    """Get a random preset scenario for the specified level"""
    try:
        scenario = get_random_scenario_by_level(level)
        return scenario
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/scenarios/generate")
async def generate_scenario(request: ScenarioGenerationRequest):
    """Generate a scenario based on mode (preset/ai/mixed)"""
    try:
        if request.mode == "preset":
            scenario = get_random_scenario_by_level(request.level)
        elif request.mode == "ai":
            scenario = await get_ai_scenario_by_level(request.level)
        elif request.mode == "mixed":
            ai_prob = request.ai_probability if request.ai_probability is not None else 0.3
            scenario = await get_mixed_scenario_by_level(request.level, ai_prob)
        else:
            raise HTTPException(status_code=400, detail="Invalid generation mode")
        
        return scenario
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/scenarios/statistics")
async def get_scenario_stats():
    """Get statistics about available scenarios"""
    stats = get_scenario_statistics()
    return stats

# Prompt evaluation endpoint
@app.post("/api/evaluate")
async def evaluate_prompt(request: EvaluatePromptRequest):
    """Evaluate a user's prompt against a scenario"""
    try:
        evaluation = await evaluate_user_prompt_async(
            request.user_prompt, 
            request.scenario
        )
        return evaluation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Progress tracking endpoints
@app.post("/api/progress/record")
async def record_attempt(request: AttemptRecord):
    """Record a user's attempt"""
    try:
        tracker.record_attempt(
            request.ldap_id,
            request.scenario_id,
            request.evaluation["total_score"],
            request.evaluation,
            request.user_prompt
        )
        return {"message": "Attempt recorded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/progress/leaderboard")
async def get_leaderboard(top_n: int = 20):
    """Get the leaderboard"""
    leaderboard = tracker.get_leaderboard(top_n=top_n)
    return {"leaderboard": leaderboard}

@app.get("/api/progress/export-summary")
async def get_export_summary():
    """Get export summary statistics"""
    summary = tracker.get_export_summary()
    return summary

@app.post("/api/progress/export-csv")
async def export_to_csv(filename: Optional[str] = None):
    """Export user data to CSV"""
    try:
        exported_filename = tracker.export_to_csv(filename)
        if exported_filename:
            return {"message": "Export successful", "filename": exported_filename}
        else:
            return {"message": "No data to export"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/progress/raw-data")
async def get_raw_data():
    """Get raw JSON data for admin purposes"""
    return tracker.get_raw_data()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
