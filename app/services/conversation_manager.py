"""
Conversation manager for handling session state and message history.
Uses in-memory storage with TTL cleanup.
"""
import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import uuid
from collections import defaultdict
from app.config import settings
from app.utils.logger import app_logger
from app.prompts.system_prompt import get_system_prompt


class ConversationManager:
    """
    Manages conversation sessions and message history.
    Uses in-memory storage with automatic cleanup.
    """
    
    def __init__(self):
        """Initialize conversation storage."""
        self.sessions: Dict[str, Dict] = {}
        self.session_lock = asyncio.Lock()
        
        # Start cleanup task
        asyncio.create_task(self._cleanup_expired_sessions())
    
    def _create_session_data(self) -> Dict:
        """Create initial session data structure."""
        return {
            "messages": [
                {
                    "role": "system",
                    "content": get_system_prompt()
                }
            ],
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "message_count": 0
        }
    
    async def create_session(self) -> str:
        """
        Create a new conversation session.
        
        Returns:
            Session ID (UUID)
        """
        session_id = str(uuid.uuid4())
        
        async with self.session_lock:
            self.sessions[session_id] = self._create_session_data()
            app_logger.info(f"Created new session: {session_id}")
        
        return session_id
    
    async def get_session(self, session_id: str) -> Optional[Dict]:
        """
        Get session data by ID.
        
        Args:
            session_id: Session identifier
        
        Returns:
            Session data or None if not found/expired
        """
        async with self.session_lock:
            session = self.sessions.get(session_id)
            
            if not session:
                app_logger.warning(f"Session not found: {session_id}")
                return None
            
            # Check if session expired
            if self._is_session_expired(session):
                app_logger.info(f"Session expired: {session_id}")
                del self.sessions[session_id]
                return None
            
            return session
    
    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str
    ) -> bool:
        """
        Add a message to the conversation history.
        
        Args:
            session_id: Session identifier
            role: Message role (user, assistant)
            content: Message content
        
        Returns:
            True if successful, False if session not found
        """
        session = await self.get_session(session_id)
        
        if not session:
            return False
        
        async with self.session_lock:
            # Add message
            session["messages"].append({
                "role": role,
                "content": content
            })
            
            # Update metadata
            session["last_activity"] = datetime.utcnow()
            session["message_count"] += 1
            
            # Trim history if too long
            await self._trim_conversation_history(session_id)
            
            app_logger.debug(
                f"Added {role} message to session {session_id}. "
                f"Total messages: {len(session['messages'])}"
            )
        
        return True
    
    async def get_messages(self, session_id: str) -> Optional[List[Dict[str, str]]]:
        """
        Get all messages for a session.
        
        Args:
            session_id: Session identifier
        
        Returns:
            List of messages or None if session not found
        """
        session = await self.get_session(session_id)
        
        if not session:
            return None
        
        return session["messages"]
    
    async def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            session_id: Session identifier
        
        Returns:
            True if deleted, False if not found
        """
        async with self.session_lock:
            if session_id in self.sessions:
                del self.sessions[session_id]
                app_logger.info(f"Deleted session: {session_id}")
                return True
            return False
    
    async def _trim_conversation_history(self, session_id: str):
        """
        Trim conversation history to max length.
        Keeps system message and recent messages only.
        """
        session = self.sessions.get(session_id)
        
        if not session:
            return
        
        messages = session["messages"]
        max_length = settings.max_conversation_length
        
        # Always keep system message (first message)
        if len(messages) > max_length + 1:  # +1 for system message
            system_message = messages[0]
            recent_messages = messages[-(max_length):]
            session["messages"] = [system_message] + recent_messages
            
            app_logger.debug(f"Trimmed session {session_id} history to {len(session['messages'])} messages")
    
    def _is_session_expired(self, session: Dict) -> bool:
        """Check if session has expired based on last activity."""
        timeout = timedelta(seconds=settings.session_timeout_seconds)
        return datetime.utcnow() - session["last_activity"] > timeout
    
    async def _cleanup_expired_sessions(self):
        """Background task to cleanup expired sessions."""
        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                
                async with self.session_lock:
                    expired_sessions = [
                        session_id
                        for session_id, session in self.sessions.items()
                        if self._is_session_expired(session)
                    ]
                    
                    for session_id in expired_sessions:
                        del self.sessions[session_id]
                    
                    if expired_sessions:
                        app_logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
                        
            except Exception as e:
                app_logger.error(f"Error in cleanup task: {e}")
    
    async def get_session_stats(self) -> Dict:
        """
        Get statistics about active sessions.
        
        Returns:
            Dictionary with session statistics
        """
        async with self.session_lock:
            total_sessions = len(self.sessions)
            total_messages = sum(
                session["message_count"]
                for session in self.sessions.values()
            )
            
            return {
                "active_sessions": total_sessions,
                "total_messages": total_messages,
                "avg_messages_per_session": (
                    total_messages / total_sessions if total_sessions > 0 else 0
                )
            }


# Global conversation manager instance
conversation_manager = ConversationManager()
