"""
Batch management system for user progress tracking
Implements session-based batching with automatic flushing
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, asdict
import logging
from collections import defaultdict
import json

from database.service import ProgressService, ProgressData, UserService
from database.config import db_connection

logger = logging.getLogger(__name__)


@dataclass
class SessionData:
    """Session data structure for batching"""
    session_id: str
    user_ldap_id: str
    entries: List[ProgressData]
    created_at: datetime
    last_activity: datetime
    auto_flush_threshold: int = 5
    max_session_duration: timedelta = timedelta(hours=2)


class BatchManager:
    """Manages batch operations for progress tracking"""
    
    def __init__(self, default_flush_threshold: int = 5, default_session_timeout: int = 7200):
        self.default_flush_threshold = default_flush_threshold
        self.default_session_timeout = default_session_timeout  # 2 hours in seconds
        self.active_sessions: Dict[str, SessionData] = {}
        self.auto_flush_tasks: Dict[str, asyncio.Task]

        self.progress_service = ProgressService()
        self.user_service = UserService()
        
        # Start background cleanup task
        self.cleanup_task = asyncio.create_task(self._cleanup_expired_sessions())
    
    async def start_session(self, user_ldap_id: str, session_id: str = None) -> str:
        """Start a new user session"""
        try:
            if session_id is None:
                session_id = f"session_{user_ldap_id}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
            
            # Clean up any existing session for this user
            await self.end_session(user_ldap_id)
            
            session_data = SessionData(
                session_id=session_id,
                user_ldap_id=user_ldap_id,
                entries=[],
                created_at=datetime.now(timezone.utc),
                last_activity=datetime.now(timezone.utc)
            )
            
            self.active_sessions[session_id] = session_data
            
            logger.info(f"Started session {session_id} for user {user_ldap_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Error starting session: {e}")
            raise
    
    async def end_session(self, user_ldap_id: str) -> bool:
        """End a user's current session and flush all data"""
        try:
            # Find active session for user
            session_to_end = None
            for session_id, session_data in self.active_sessions.items():
                if session_data.user_ldap_id == user_ldap_id:
                    session_to_end = session_id
                    break
            
            if not session_to_end:
                logger.info(f"No active session found for user {user_ldap_id}")
                return True
            
            session_data = self.active_sessions[session_to_end]
            
            # Flush all remaining entries
            if session_data.entries:
                await self._flush_session_data(session_data)
            
            # Remove session
            del self.active_sessions[session_to_end]
            
            logger.info(f"Ended session {session_to_end} for user {user_ldap_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error ending session: {e}")
            return False
    
    async def add_progress_entry(self, user_ldap_id: str, progress_data: ProgressData) -> bool:
        """Add a progress entry to the current session"""
        try:
            # Find or create session
            session_id = await self._get_or_create_session(user_ldap_id)
            session_data = self.active_sessions[session_id]
            
            # Add to session
            session_data.entries.append(progress_data)
            session_data.last_activity = datetime.now(timezone.utc)
            
            logger.debug(f"Added entry to session {session_id}. Total entries: {len(session_data.entries)}")
            
            # Check if auto-flush threshold is reached
            if len(session_data.entries) >= session_data.auto_flush_threshold:
                await self.auto_flush_session(session_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding progress entry: {e}")
            return False
    
    async def auto_flush_session(self, session_id: str) -> bool:
        """Automatically flush session data if threshold is reached"""
        try:
            if session_id not in self.active_sessions:
                return False
            
            session_data = self.active_sessions[session_id]
            
            if len(session_data.entries) >= session_data.auto_flush_threshold:
                await self._flush_session_data(session_data)
                
                # Clear flushed entries
                session_data.entries = []
                
                logger.info(f"Auto-flushed session {session_id} with {session_data.auto_flush_threshold} entries")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error auto-flushing session: {e}")
            return False
    
    async def manual_flush_session(self, user_ldap_id: str) -> bool:
        """Manually flush current session data"""
        try:
            # Find session
            session = await self._get_session_for_user(user_ldap_id)
            if not session:
                logger.info(f"No active session found for user {user_ldap_id}")
                return True
            
            session_data = self.active_sessions[session]
            
            if not session_data.entries:
                logger.info(f"No data to flush for session {session}")
                return True
            
            await self._flush_session_data(session_data)
            
            # Clear flushed entries
            session_data.entries = []
            
            logger.info(f"Manually flushed session {session} with {len(session_data.entries)} entries")
            return True
            
        except Exception as e:
            logger.error(f"Error manually flushing session: {e}")
            return False
    
    async def _get_or_create_session(self, user_ldap_id: str) -> str:
        """Get existing session or create new one"""
        # Find existing session
        session_id = await self._get_session_for_user(user_ldap_id)
        
        if session_id:
            return session_id
        
        # Create new session
        return await self.start_session(user_ldap_id)
    
    async def _get_session_for_user(self, user_ldap_id: str) -> Optional[str]:
        """Get session ID for a user"""
        for session_id, session_data in self.active_sessions.items():
            if session_data.user_ldap_id == user_ldap_id:
                return session_id
        return None
    
    async def _flush_session_data(self, session_data: SessionData) -> bool:
        """Flush session data to database"""
        try:
            if not session_data.entries:
                return True
            
            # Validate user exists
            user = await self.user_service.get_user_by_ldap_id(session_data.user_ldap_id)
            if not user:
                logger.error(f"User {session_data.user_ldap_id} not found")
                return False
            
            # Prepare sessions data for batch insert
            entries_to_flush = []
            for entry in session_data.entries:
                entry.user_id = user.id
                entry.session_id = session_data.session_id
                entries_to_flush.append(entry)
            
            # Batch insert
            await self.progress_service.batch_create_progress_entries(entries_to_flush)
            
            logger.info(f"Flushed {len(entries_to_flush)} entries for session {session_data.session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error flushing session data: {e}")
            return False
    
    async def get_session_info(self, user_ldap_id: str) -> Optional[Dict[str, Any]]:
        """Get information about user's current session"""
        try:
            session_id = await self._get_session_for_user(user_ldap_id)
            if not session_id:
                return None
            
            session_data = self.active_sessions[session_id]
            
            return {
                "session_id": session_data.session_id,
                "user_ldap_id": session_data.user_ldap_id,
                "entry_count": len(session_data.entries),
                "created_at": session_data.created_at.isoformat(),
                "last_activity": session_data.last_activity.isoformat(),
                "auto_flush_threshold": session_data.auto_flush_threshold,
                "is_pending_flush": len(session_data.entries) >= session_data.auto_flush_threshold,
                "session_duration": datetime.now(timezone.utc) - session_data.created_at
            }
            
        except Exception as e:
            logger.error(f"Error getting session info: {e}")
            return None
    
    async def _cleanup_expired_sessions(self):
        """Background task to clean up expired sessions"""
        while True:
            try:
                current_time = datetime.now(timezone.utc)
                expired_sessions = []
                
                for session_id, session_data in self.active_sessions.items():
                    # Check if session has expired
                    if current_time - session_data.last_activity > session_data.max_session_duration:
                        expired_sessions.append(session_id)
                
                # Clean up expired sessions
                for session_id in expired_sessions:
                    session_data = self.active_sessions[session_id]
                    
                    # Flush any remaining data
                    if session_data.entries:
                        await self._flush_session_data(session_data)
                    
                    # Remove session
                    del self.active_sessions[session_id]
                    logger.info(f"Cleaned up expired session {session_id}")
                
                # Sleep for 5 minutes before next cleanup
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")
                await asyncio.sleep(60)  # Short sleep on error
    
    async def get_all_sessions_info(self) -> List[Dict[str, Any]]:
        """Get information about all active sessions"""
        try:
            sessions_info = []
            for session_data in self.active_sessions.values():
                info = await self.get_session_info(session_data.user_ldap_id)
                if info:
                    sessions_info.append(info)
            return sessions_info
        except Exception as e:
            logger.error(f"Error getting all sessions info: {e}")
            return []
    
    async def force_flush_all_sessions(self) -> Dict[str, int]:
        """Force flush all active sessions"""
        try:
            results = {"flushed": 0, "errors": 0}
            
            for session_id, session_data in list(self.active_sessions.items()):
                try:
                    if session_data.entries:
                        await self._flush_session_data(session_data)
                        session_data.entries = []
                        results["flushed"] += 1
                except Exception as e:
                    logger.error(f"Error flushing session {session_id}: {e}")
                    results["errors"] += 1
            
            logger.info(f"Force flushed all sessions: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Error force flushing all sessions: {e}")
            return {"flushed": 0, "errors": 1}
    
    async def shutdown(self):
        """Gracefully shutdown batch manager"""
        try:
            # Cancel cleanup task
            if hasattr(self, 'cleanup_task'):
                self.cleanup_task.cancel()
                try:
                    await self.cleanup_task
                except asyncio.CancelledError:
                    pass
            
            # Flush all remaining sessions
            await self.force_flush_all_sessions()
            
            logger.info("Batch manager shutdown completed")
            
        except Exception as e:
            logger.error(f"Error shutting down batch manager: {e}")


# Convenience functions for integration
async def create_batch_manager() -> BatchManager:
    """Create and initialize batch manager"""
    batch_manager = BatchManager()
    logger.info("Batch manager created")
    return batch_manager


async def cleanup_batch_manager(batch_manager: BatchManager):
    """Cleanup batch manager"""
    await batch_manager.shutdown()
    logger.info("Batch manager cleaned up")
