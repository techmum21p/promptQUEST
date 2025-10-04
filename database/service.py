"""
Database service layer for prompt training application
Provides CRUD operations and business logic for user management and progress tracking
"""

import asyncio
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID, uuid4
from datetime import datetime, timezone
import logging
from dataclasses import dataclass, asdict
import json

from .config import db_connection

logger = logging.getLogger(__name__)


@dataclass
class UserData:
    """User data structure"""
    id: Optional[str] = None
    ldap_id: str = ""
    username: str = ""
    password_hash: str = ""
    email_address: str = ""
    user_group: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    is_active: bool = True


@dataclass
class ProgressData:
    """Progress data structure"""
    id: Optional[str] = None
    user_id: Optional[str] = None
    ldap_id: str = ""
    attempt_number: int = 0
    timestamp: datetime = None
    scenario_id: str = ""
    user_prompt: str = ""
    total_score: int = 0
    clarity_score: int = 0
    specificity_score: int = 0
    structure_score: int = 0
    task_alignment_score: int = 0
    skill_level: str = "beginner"
    feedback: str = ""
    strengths: List[str] = None
    improvements: List[str] = None
    session_id: Optional[str] = None


@dataclass
class BadgeData:
    """Badge data structure"""
    id: Optional[str] = None
    user_id: str = ""
    badge_name: str = ""
    awarded_at: Optional[datetime] = None
    scenario_id: Optional[str] = None


@dataclass
class LeaderboardEntry:
    """Leaderboard entry structure"""
    ldap_id: str
    username: str
    user_group: str
    total_attempts: int
    avg_score: float
    current_skill_level: str
    total_badges: int
    last_activity: Optional[datetime]
    badges: List[str]


class UserService:
    """Service for user management operations"""
    
    async def create_user(self, user_data: UserData) -> UserData:
        """Create a new user"""
        try:
            query = """
            INSERT INTO users (id, ldap_id, username, password_hash, email_address, user_group)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING *
            """
            
            user_id = str(uuid4())
            async with db_connection.get_connection() as conn:
                result = await conn.fetchrow(
                    query, 
                    user_id,
                    user_data.ldap_id,
                    user_data.username,
                    user_data.password_hash,
                    user_data.email_address,
                    user_data.user_group
                )
                
                # Convert result to UserData
                return UserData(**dict(result))
                
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise
    
    async def get_user_by_ldap_id(self, ldap_id: str) -> Optional[UserData]:
        """Get user by LDAP ID"""
        try:
            query = "SELECT * FROM users WHERE ldap_id = $1 AND is_active = TRUE"
            async with db_connection.get_connection() as conn:
                result = await conn.fetchrow(query, ldap_id)
                return UserData(**dict(result)) if result else None
        except Exception as e:
            logger.error(f"Error getting user by LDAP ID: {e}")
            raise
    
    async def get_user_by_username(self, username: str) -> Optional[UserData]:
        """Get user by username"""
        try:
            query = "SELECT * FROM users WHERE username = $1 AND is_active = TRUE"
            async with db_connection.get_connection() as conn:
                result = await conn.fetchrow(query, username)
                return UserData(**dict(result)) if result else None
        except Exception as e:
            logger.error(f"Error getting user by username: {e}")
            raise
    
    async def get_user_by_email(self, email: str) -> Optional[UserData]:
        """Get user by email"""
        try:
            query = "SELECT * FROM users WHERE email_address = $1 AND is_active = TRUE"
            async with db_connection.get_connection() as conn:
                result = await conn.fetchrow(query, email)
                return UserData(**dict(result)) if result else None
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            raise
    
    async def update_user_last_login(self, user_id: str) -> bool:
        """Update user's last login timestamp"""
        try:
            query = "UPDATE users SET last_login = $1 WHERE id = $2"
            async with db_connection.get_connection() as conn:
                await conn.execute(query, datetime.now(timezone.utc), user_id)
                return True
        except Exception as e:
            logger.error(f"Error updating last login: {e}")
            return False
    
    async def get_users_by_group(self, group: str) -> List[UserData]:
        """Get all users in a specific group"""
        try:
            query = "SELECT * FROM users WHERE user_group = $1 AND is_active = TRUE ORDER BY username"
            async with db_connection.get_connection() as conn:
                results = await conn.fetch(query, group)
                return [UserData(**dict(row)) for row in results]
        except Exception as e:
            logger.error(f"Error getting users by group: {e}")
            raise


class ProgressService:
    """Service for user progress tracking"""
    
    def __init__(self):
        self.user_service = UserService()
        self.session_buffer = {}  # Temporary storage for session data
    
    async def create_progress_entry(self, progress_data: ProgressData) -> ProgressData:
        """Create a new progress entry"""
        try:
            # Get user ID if not provided
            if not progress_data.user_id:
                user = await self.user_service.get_user_by_ldap_id(progress_data.ldap_id)
                if not user:
                    raise ValueError(f"User with LDAP ID {progress_data.ldap_id} not found")
                progress_data.user_id = user.id
            
            # Generate session ID if not provided
            if not progress_data.session_id:
                progress_data.session_id = str(uuid4())
            
            query = """
            INSERT INTO user_progress (
                id, user_id, ldap_id, attempt_number, timestamp, scenario_id,
                user_prompt, total_score, clarity_score, specificity_score,
                structure_score, task_alignment_score, skill_level,
                feedback, strengths, improvements, session_id
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17
            )
            RETURNING *
            """
            
            progress_id = str(uuid4())
            timestamp = progress_data.timestamp or datetime.now(timezone.utc)
            
            async with db_connection.get_connection() as conn:
                result = await conn.fetchrow(
                    query,
                    progress_id,
                    progress_data.user_id,
                    progress_data.ldap_id,
                    progress_data.attempt_number,
                    timestamp,
                    progress_data.scenario_id,
                    progress_data.user_prompt,
                    progress_data.total_score,
                    progress_data.clarity_score,
                    progress_data.specificity_score,
                    progress_data.structure_score,
                    progress_data.task_alignment_score,
                    progress_data.skill_level,
                    progress_data.feedback,
                    progress_data.strengths or [],
                    progress_data.improvements or [],
                    progress_data.session_id
                )
                
                return ProgressData(**dict(result))
                
        except Exception as e:
            logger.error(f"Error creating progress entry: {e}")
            raise
    
    async def batch_create_progress_entries(self, progress_entries: List[ProgressData]) -> List[ProgressData]:
        """Create multiple progress entries in a single transaction"""
        try:
            async with db_connection.get_connection() as conn:
                async with conn.transaction():
                    results = []
                    for progress_data in progress_entries:
                        # Get user ID if not provided
                        if not progress_data.user_id:
                            user = await self.user_service.get_user_by_ldap_id(progress_data.ldap_id)
                            if not user:
                                logger.error(f"User with LDAP ID {progress_data.ldap_id} not found")
                                continue
                            progress_data.user_id = user.id
                        
                        if not progress_data.session_id:
                            progress_data.session_id = str(uuid4())
                        
                        progress_id = str(uuid4())
                        timestamp = progress_data.timestamp or datetime.now(timezone.utc)
                        
                        query = """
                        INSERT INTO user_progress (
                            id, user_id, ldap_id, attempt_number, timestamp, scenario_id,
                            user_prompt, total_score, clarity_score, specificity_score,
                            structure_score, task_alignment_score, skill_level,
                            feedback, strengths, improvements, session_id
                        ) VALUES (
                            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17
                        )
                        RETURNING *
                        """
                        
                        result = await conn.fetchrow(
                            query,
                            progress_id,
                            progress_data.user_id,
                            progress_data.ldap_id,
                            progress_data.attempt_number,
                            timestamp,
                            progress_data.scenario_id,
                            progress_data.user_prompt,
                            progress_data.total_score,
                            progress_data.clarity_score,
                            progress_data.specificity_score,
                            progress_data.structure_score,
                            progress_data.task_alignment_score,
                            progress_data.skill_level,
                            progress_data.feedback,
                            progress_data.strengths or [],
                            progress_data.improvements or [],
                            progress_data.session_id
                        )
                        
                        results.append(ProgressData(**dict(result)))
                    
                    logger.info(f"Batch created {len(results)} progress entries")
                    return results
                    
        except Exception as e:
            logger.error(f"Error batch creating progress entries: {e}")
            raise
    
    async def get_user_progress_summary(self, ldap_id: str) -> Dict[str, Any]:
        """Get comprehensive user progress summary"""
        try:
            query = """
            SELECT 
                u.username,
                u.user_group,
                COUNT(up.id) as total_attempts,
                CASE 
                    WHEN COUNT(up.id) = 0 THEN 0
                    ELSE ROUND(AVG(up.total_score)::NUMERIC, 2)
                END as avg_score,
                MAX(up.skill_level) as current_skill_level,
                COUNT(ub.id) as total_badges,
                MAX(up.timestamp) as last_activity,
                ARRAY_AGG(ub.badge_name ORDER BY ub.badge_name) FILTER (WHERE ub.badge_name IS NOT NULL) as badges,
                SUM(up.total_score) as total_score_cumulative
            FROM users u
            LEFT JOIN user_progress up ON u.id = up.user_id
            LEFT JOIN user_badges ub ON u.id = ub.user_id
            WHERE u.ldap_id = $1 AND u.is_active = TRUE
            GROUP BY u.id, u.username, u.user_group
            """
            
            async with db_connection.get_connection() as conn:
                result = await conn.fetchrow(query, ldap_id)
                return dict(result) if result else None
                
        except Exception as e:
            logger.error(f"Error getting user progress summary: {e}")
            raise
    
    async def get_user_recent_attempts(self, ldap_id: str, limit: int = 10) -> List[ProgressData]:
        """Get user's recent attempts"""
        try:
            query = """
            SELECT up.* FROM user_progress up
            JOIN users u ON up.user_id = u.id
            WHERE u.ldap_id = $1
            ORDER BY up.timestamp DESC
            LIMIT $2
            """
            
            async with db_connection.get_connection() as conn:
                results = await conn.fetch(query, ldap_id, limit)
                return [ProgressData(**dict(row)) for row in results]
                
        except Exception as e:
            logger.error(f"Error getting user recent attempts: {e}")
            raise
    
    async def store_session_data(self, ldap_id: str, session_data: List[ProgressData]) -> bool:
        """Store session data in memory buffer (for batch processing)"""
        try:
            self.session_buffer[ldap_id] = session_data
            logger.info(f"Stored {len(session_data)} entries for session {ldap_id}")
            return True
        except Exception as e:
            logger.error(f"Error storing session data: {e}")
            return False
    
    async def flush_session_data(self, ldap_id: str) -> bool:
        """Flush batched session data to database"""
        try:
            if ldap_id not in self.session_buffer:
                return True
            
            session_data = self.session_buffer[ldap_id]
            if not session_data:
                return True
            
            await self.batch_create_progress_entries(session_data)
            
            # Clear the buffer
            del self.session_buffer[ldap_id]
            logger.info(f"Flushed session data for {ldap_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error flushing session data: {e}")
            return False
    
    async def auto_flush_if_needed(self, ldap_id: str, threshold: int = 5) -> bool:
        """Auto-flush session data if threshold is reached"""
        try:
            if ldap_id in self.session_buffer:
                session_data = self.session_buffer[ldap_id]
                if len(session_data) >= threshold:
                    await self.flush_session_data(ldap_id)
                    return True
            return False
        except Exception as e:
            logger.error(f"Error in auto-flush: {e}")
            return False


class BadgeService:
    """Service for badge management"""
    
    async def award_badge(self, user_id: str, badge_name: str, scenario_id: str = None) -> BadgeData:
        """Award a badge to a user"""
        try:
            query = """
            INSERT INTO user_badges (id, user_id, badge_name, scenario_id)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (user_id, badge_name) DO NOTHING
            RETURNING *
            """
            
            badge_id = str(uuid4())
            async with db_connection.get_connection() as conn:
                result = await conn.fetchrow(query, badge_id, user_id, badge_name, scenario_id)
                return BadgeData(**dict(result)) if result else None
                
        except Exception as e:
            logger.error(f"Error awarding badge: {e}")
            raise
    
    async def get_user_badges(self, user_id: str) -> List[BadgeData]:
        """Get all badges for a user"""
        try:
            query = "SELECT * FROM user_badges WHERE user_id = $1 ORDER BY awarded_at DESC"
            async with db_connection.get_connection() as conn:
                results = await conn.fetch(query, user_id)
                return [BadgeData(**dict(row)) for row in results]
        except Exception as e:
            logger.error(f"Error getting user badges: {e}")
            raise
    
    async def check_and_award_badges(self, ldap_id: str, progress_data: ProgressData) -> List[str]:
        """Check and award badges based on progress"""
        try:
            new_badges = []
            
            # Get user
            user = await UserService().get_user_by_ldap_id(ldap_id)
            if not user:
                return new_badges
            
            # Get existing badges
            existing_badges = await self.get_user_badges(user.id)
            existing_badge_names = {badge.badge_name for badge in existing_badges}
            
            # Get user's progress summary
            progress_summary = await ProgressService().get_user_progress_summary(ldap_id)
            
            if not progress_summary:
                return new_badges
            
            total_attempts = progress_summary['total_attempts']
            avg_score = progress_summary['avg_score']
            
            # Check for badges
            badges_to_check = [
                ("Perfect Score", "Always"),  # Check if current score is 100
                ("Consistent Performer", "If avg_score > 80 and attempts >= 3"),
                ("Dedicated Learner", "If attempts >= 10"),
                ("Advanced Master", "If attempts >= 5 on advanced scenarios and avg > 85")
            ]
            
            for badge_name, condition in badges_to_check:
                if badge_name in existing_badge_names:
                    continue
                
                should_award = False
                
                if badge_name == "Perfect Score" and progress_data.total_score == 100:
                    should_award = True
                elif badge_name == "Consistent Performer" and total_attempts >= 3 and avg_score >= 80:
                    should_award = True
                elif badge_name == "Dedicated Learner" and total_attempts >= 10:
                    should_award = True
                elif badge_name == "Advanced Master":
                    # Check advanced scenario performance
                    if scenario_id.startswith('a') and total_attempts >= 5 and avg_score > 85:
                        should_award = True
                
                if should_award:
                    await self.award_badge(user.id, badge_name, progress_data.scenario_id)
                    new_badges.append(badge_name)
            
            return new_badges
            
        except Exception as e:
            logger.error(f"Error checking badges: {e}")
            return []


class LeaderboardService:
    """Service for leaderboard operations"""
    
    async def get_leaderboard(self, limit: int = 10, group: str = None) -> List[LeaderboardEntry]:
        """Get leaderboard data"""
        try:
            if group:
                query = """
                SELECT * FROM leaderboard 
                WHERE user_group = $1 AND total_attempts > 0
                ORDER BY avg_score DESC, total_attempts DESC 
                LIMIT $2
                """
            else:
                query = """
                SELECT * FROM leaderboard 
                WHERE total_attempts > 0
                ORDER BY avg_score DESC, total_attempts DESC 
                LIMIT $1
                """
            
            async with db_connection.get_connection() as conn:
                if group:
                    results = await conn.fetch(query, group, limit)
                else:
                    results = await conn.fetch(query, limit)
                
                return [LeaderboardEntry(**dict(row)) for row in results]
                
        except Exception as e:
            logger.error(f"Error getting leaderboard: {e}")
            raise
    
    async def get_multi_group_leaderboard(self, limit_per_group: int = 20) -> Dict[str, List[LeaderboardEntry]]:
        """Get leaderboard data organized by groups plus overall"""
        try:
            # Get all unique groups
            groups_query = """
            SELECT DISTINCT user_group 
            FROM leaderboard 
            WHERE user_group IS NOT NULL AND user_group != '' AND total_attempts > 0
            ORDER BY user_group
            """
            
            async with db_connection.get_connection() as conn:
                # Get all groups
                group_results = await conn.fetch(groups_query)
                all_groups = [row['user_group'] for row in group_results]
                
                result = {}
                
                # Get leaderboard for each group
                for group in all_groups:
                    group_query = """
                    SELECT * FROM leaderboard 
                    WHERE user_group = $1 AND total_attempts > 0
                    ORDER BY avg_score DESC, total_attempts DESC 
                    LIMIT $2
                    """
                    group_results = await conn.fetch(group_query, group, limit_per_group)
                    result[group] = [LeaderboardEntry(**dict(row)) for row in group_results]
                
                # Get overall leaderboard (all groups combined)
                overall_query = """
                SELECT * FROM leaderboard 
                WHERE total_attempts > 0
                ORDER BY avg_score DESC, total_attempts DESC 
                LIMIT $1
                """
                overall_results = await conn.fetch(overall_query, limit_per_group)
                result['all_groups'] = [LeaderboardEntry(**dict(row)) for row in overall_results]
                
                return result
                
        except Exception as e:
            logger.error(f"Error getting multi-group leaderboard: {e}")
            raise
    
    async def refresh_leaderboard(self):
        """Manually refresh the leaderboard materialized view"""
        try:
            async with db_connection.get_connection() as conn:
                await conn.execute("REFRESH MATERIALIZED VIEW leaderboard")
                logger.info("Leaderboard refreshed")
        except Exception as e:
            logger.error(f"Error refreshing leaderboard: {e}")
            raise


# Convenience functions
async def init_database_services():
    """Initialize all database services"""
    await db_connection.initialize_pool()
    logger.info("All database services initialized")


async def close_database_services():
    """Close all database services"""
    await db_connection.close_pool()
    logger.info("All database services closed")
