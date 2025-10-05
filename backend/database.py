"""
Database models and configuration for PostgreSQL integration
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, JSON, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/promptquest")

# Create engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    """User model with LDAP ID as primary key"""
    __tablename__ = "users"
    
    ldap_id = Column(String(255), primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    total_score = Column(Integer, default=0)
    attempts = Column(Integer, default=0)
    skill_level = Column(String(50), default="beginner")
    badges = Column(JSON, default=list)  # Store badges as JSON array
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to attempts
    attempts_rel = relationship("UserAttempt", back_populates="user", cascade="all, delete-orphan")

class UserAttempt(Base):
    """User attempt/history model"""
    __tablename__ = "user_attempts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ldap_id = Column(String(255), ForeignKey("users.ldap_id"), nullable=False)
    scenario_id = Column(String(50), nullable=False)
    score = Column(Integer, nullable=False)
    user_prompt = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Evaluation details stored as JSON
    clarity_score = Column(Integer)
    specificity_score = Column(Integer)
    structure_score = Column(Integer)
    task_alignment_score = Column(Integer)
    feedback = Column(Text)
    strengths = Column(JSON)  # Store as JSON array
    improvements = Column(JSON)  # Store as JSON array
    
    # Relationship to user
    user = relationship("User", back_populates="attempts_rel")

class Leaderboard(Base):
    """Leaderboard model for caching leaderboard data"""
    __tablename__ = "leaderboard"
    
    id = Column(Integer, primary_key=True, index=True)
    ldap_id = Column(String(255), ForeignKey("users.ldap_id"), nullable=False)
    username = Column(String(100), nullable=False)
    avg_score = Column(Float, nullable=False)
    total_attempts = Column(Integer, nullable=False)
    skill_level = Column(String(50), nullable=False)
    badges_count = Column(Integer, default=0)
    rank = Column(Integer, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to user
    user = relationship("User")

def create_tables():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Database utility functions
class DatabaseManager:
    """Database operations manager"""
    
    def __init__(self):
        self.db = SessionLocal()
    
    def __enter__(self):
        return self.db
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()
    
    @staticmethod
    def get_session():
        """Get a new database session"""
        return SessionLocal()
