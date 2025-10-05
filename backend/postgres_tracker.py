"""
PostgreSQL-based User Progress Tracker
Replaces the JSON-based tracker with database persistence
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from database import User, UserAttempt, Leaderboard, DatabaseManager
import json

class PostgreSQLUserProgressTracker:
    """PostgreSQL-based user progress tracker"""
    
    def __init__(self):
        self.db_session = None
    
    def _get_session(self) -> Session:
        """Get database session"""
        if self.db_session is None:
            self.db_session = DatabaseManager.get_session()
        return self.db_session
    
    def add_user(self, ldap_id: str, username: str):
        """Add a new user with LDAP ID"""
        db = self._get_session()
        try:
            # Check if user already exists
            existing_user = db.query(User).filter(User.ldap_id == ldap_id).first()
            if existing_user:
                return  # User already exists
            
            # Create new user
            new_user = User(
                ldap_id=ldap_id,
                username=username,
                total_score=0,
                attempts=0,
                skill_level="beginner",
                badges=[]
            )
            db.add(new_user)
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
    
    def record_attempt(self, ldap_id: str, scenario_id: str, score: int, evaluation: Dict, user_prompt: str = ""):
        """Record a user's attempt"""
        db = self._get_session()
        try:
            # Get user
            user = db.query(User).filter(User.ldap_id == ldap_id).first()
            if not user:
                raise ValueError(f"User with LDAP ID {ldap_id} not found")
            
            # Create attempt record
            attempt = UserAttempt(
                ldap_id=ldap_id,
                scenario_id=scenario_id,
                score=score,
                user_prompt=user_prompt,
                clarity_score=evaluation.get("clarity_score"),
                specificity_score=evaluation.get("specificity_score"),
                structure_score=evaluation.get("structure_score"),
                task_alignment_score=evaluation.get("task_alignment_score"),
                feedback=evaluation.get("feedback"),
                strengths=evaluation.get("strengths", []),
                improvements=evaluation.get("improvements", [])
            )
            db.add(attempt)
            
            # Update user stats
            user.total_score += score
            user.attempts += 1
            
            # Update skill level based on average score
            avg_score = user.total_score / user.attempts
            if avg_score >= 90:
                user.skill_level = "expert"
            elif avg_score >= 75:
                user.skill_level = "advanced"
            elif avg_score >= 60:
                user.skill_level = "intermediate"
            else:
                user.skill_level = "beginner"
            
            # Award badges based on performance
            self._update_badges(user, score, user.attempts)
            
            user.updated_at = datetime.utcnow()
            db.commit()
            
            # Update leaderboard
            self._update_leaderboard()
            
        except Exception as e:
            db.rollback()
            raise e
    
    def _update_badges(self, user: User, score: int, attempts: int):
        """Update user badges based on performance"""
        badges = user.badges or []
        
        # Consistent Performer badge
        if attempts >= 5 and score >= 80:
            if "Consistent Performer" not in badges:
                badges.append("Consistent Performer")
        
        # Dedicated Learner badge
        if attempts >= 10:
            if "Dedicated Learner" not in badges:
                badges.append("Dedicated Learner")
        
        # High Achiever badge
        if score >= 95:
            if "High Achiever" not in badges:
                badges.append("High Achiever")
        
        # Quick Learner badge
        if attempts >= 3 and user.skill_level in ["advanced", "expert"]:
            if "Quick Learner" not in badges:
                badges.append("Quick Learner")
        
        user.badges = badges
    
    def _update_leaderboard(self):
        """Update leaderboard cache"""
        db = self._get_session()
        try:
            # Clear existing leaderboard
            db.query(Leaderboard).delete()
            
            # Get users with their stats
            users_with_stats = db.query(
                User.ldap_id,
                User.username,
                User.total_score,
                User.attempts,
                User.skill_level,
                User.badges
            ).filter(User.attempts > 0).all()
            
            # Calculate average scores and create leaderboard entries
            leaderboard_entries = []
            for i, user_stat in enumerate(users_with_stats):
                avg_score = user_stat.total_score / user_stat.attempts if user_stat.attempts > 0 else 0
                
                badges_count = len(user_stat.badges) if user_stat.badges else 0
                leaderboard_entry = Leaderboard(
                    ldap_id=user_stat.ldap_id,
                    username=user_stat.username,
                    avg_score=avg_score,
                    total_attempts=user_stat.attempts,
                    skill_level=user_stat.skill_level,
                    badges_count=badges_count,
                    rank=i + 1
                )
                leaderboard_entries.append(leaderboard_entry)
            
            # Sort by average score descending
            leaderboard_entries.sort(key=lambda x: x.avg_score, reverse=True)
            
            # Update ranks
            for i, entry in enumerate(leaderboard_entries):
                entry.rank = i + 1
            
            # Add to database
            for entry in leaderboard_entries:
                db.add(entry)
            
            db.commit()
            
        except Exception as e:
            db.rollback()
            raise e
    
    def get_user_stats(self, ldap_id: str) -> Optional[Dict]:
        """Get user statistics"""
        db = self._get_session()
        try:
            user = db.query(User).filter(User.ldap_id == ldap_id).first()
            if not user:
                return None
            
            # Get recent attempts
            recent_attempts = db.query(UserAttempt).filter(
                UserAttempt.ldap_id == ldap_id
            ).order_by(desc(UserAttempt.timestamp)).limit(10).all()
            
            # Convert attempts to dict format
            history = []
            for attempt in recent_attempts:
                history.append({
                    "timestamp": attempt.timestamp.isoformat(),
                    "scenario_id": attempt.scenario_id,
                    "score": attempt.score,
                    "evaluation": {
                        "clarity_score": attempt.clarity_score,
                        "specificity_score": attempt.specificity_score,
                        "structure_score": attempt.structure_score,
                        "task_alignment_score": attempt.task_alignment_score,
                        "total_score": attempt.score,
                        "feedback": attempt.feedback,
                        "strengths": attempt.strengths or [],
                        "improvements": attempt.improvements or []
                    },
                    "user_prompt": attempt.user_prompt
                })
            
            return {
                "ldap_id": user.ldap_id,
                "username": user.username,
                "total_score": user.total_score,
                "attempts": user.attempts,
                "skill_level": user.skill_level,
                "badges": user.badges or [],
                "history": history
            }
        except Exception as e:
            raise e
    
    def get_leaderboard(self, top_n: int = 20) -> List[Dict]:
        """Get leaderboard"""
        db = self._get_session()
        try:
            leaderboard_entries = db.query(Leaderboard).order_by(
                desc(Leaderboard.avg_score)
            ).limit(top_n).all()
            
            return [
                {
                    "ldap_id": entry.ldap_id,
                    "username": entry.username,
                    "avg_score": round(entry.avg_score, 1),
                    "total_attempts": entry.total_attempts,
                    "skill_level": entry.skill_level,
                    "badges": entry.badges_count
                }
                for entry in leaderboard_entries
            ]
        except Exception as e:
            raise e
    
    def get_export_summary(self) -> Dict:
        """Get export summary statistics"""
        db = self._get_session()
        try:
            total_users = db.query(User).count()
            total_attempts = db.query(UserAttempt).count()
            avg_score = db.query(func.avg(UserAttempt.score)).scalar() or 0
            
            # Calculate active users (users with attempts in last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            active_users = db.query(func.count(func.distinct(User.ldap_id))).join(UserAttempt).filter(
                UserAttempt.timestamp >= thirty_days_ago
            ).scalar() or 0
            
            # Calculate skill distribution
            skill_distribution = {}
            users_by_skill = db.query(User.skill_level, func.count(User.ldap_id)).group_by(User.skill_level).all()
            for skill_level, count in users_by_skill:
                skill_distribution[skill_level] = count
            
            # Calculate recent activity (attempts in last 7 days)
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            recent_activity = db.query(UserAttempt).filter(
                UserAttempt.timestamp >= seven_days_ago
            ).count()
            
            return {
                "total_users": total_users,
                "total_attempts": total_attempts,
                "avg_score": round(avg_score, 2),
                "avg_score_all_users": round(avg_score, 2),  # Frontend expects this field
                "active_users": active_users,
                "skill_distribution": skill_distribution,
                "recent_activity": recent_activity,
                "export_timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            raise e
    
    def export_to_csv(self, filename: Optional[str] = None) -> Optional[str]:
        """Export user data to CSV"""
        import pandas as pd
        import os
        
        db = self._get_session()
        try:
            # Get all users with their attempts
            users = db.query(User).all()
            
            if not users:
                return None
            
            # Prepare data for export
            export_data = []
            for user in users:
                attempts = db.query(UserAttempt).filter(
                    UserAttempt.ldap_id == user.ldap_id
                ).order_by(UserAttempt.timestamp).all()
                
                for attempt in attempts:
                    export_data.append({
                        "ldap_id": user.ldap_id,
                        "username": user.username,
                        "timestamp": attempt.timestamp.isoformat(),
                        "scenario_id": attempt.scenario_id,
                        "score": attempt.score,
                        "clarity_score": attempt.clarity_score,
                        "specificity_score": attempt.specificity_score,
                        "structure_score": attempt.structure_score,
                        "task_alignment_score": attempt.task_alignment_score,
                        "feedback": attempt.feedback,
                        "user_prompt": attempt.user_prompt,
                        "skill_level": user.skill_level,
                        "total_user_score": user.total_score,
                        "total_user_attempts": user.attempts,
                        "badges": json.dumps(user.badges or [])
                    })
            
            # Create DataFrame and export
            df = pd.DataFrame(export_data)
            
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"user_progress_export_{timestamp}.csv"
            
            # Ensure filename has .csv extension
            if not filename.endswith('.csv'):
                filename += '.csv'
            
            # Save to backend directory
            filepath = os.path.join(os.path.dirname(__file__), filename)
            df.to_csv(filepath, index=False)
            
            return filename
            
        except Exception as e:
            raise e
    
    def get_raw_data(self) -> Dict:
        """Get raw data for admin purposes (compatible with old API)"""
        db = self._get_session()
        try:
            users = {}
            leaderboard = []
            
            # Get all users
            all_users = db.query(User).all()
            for user in all_users:
                attempts = db.query(UserAttempt).filter(
                    UserAttempt.ldap_id == user.ldap_id
                ).order_by(UserAttempt.timestamp).all()
                
                history = []
                for attempt in attempts:
                    history.append({
                        "timestamp": attempt.timestamp.isoformat(),
                        "scenario_id": attempt.scenario_id,
                        "score": attempt.score,
                        "evaluation": {
                            "clarity_score": attempt.clarity_score,
                            "specificity_score": attempt.specificity_score,
                            "structure_score": attempt.structure_score,
                            "task_alignment_score": attempt.task_alignment_score,
                            "total_score": attempt.score,
                            "feedback": attempt.feedback,
                            "strengths": attempt.strengths or [],
                            "improvements": attempt.improvements or []
                        },
                        "user_prompt": attempt.user_prompt
                    })
                
                users[user.username] = {
                    "ldap_id": user.ldap_id,
                    "total_score": user.total_score,
                    "attempts": user.attempts,
                    "skill_level": user.skill_level,
                    "badges": user.badges or [],
                    "history": history
                }
            
            # Get leaderboard
            leaderboard_entries = db.query(Leaderboard).order_by(
                desc(Leaderboard.avg_score)
            ).all()
            
            for entry in leaderboard_entries:
                leaderboard.append({
                    "ldap_id": entry.ldap_id,
                    "username": entry.username,
                    "avg_score": entry.avg_score,
                    "total_attempts": entry.total_attempts,
                    "skill_level": entry.skill_level,
                    "badges": entry.badges_count
                })
            
            return {
                "users": users,
                "leaderboard": leaderboard
            }
            
        except Exception as e:
            raise e
    
    def close(self):
        """Close database session"""
        if self.db_session:
            self.db_session.close()
            self.db_session = None
