"""
Redis-based session management and token blacklisting service.
"""
from typing import Optional, Dict, Any
import redis.asyncio as redis
import json
from datetime import timedelta
from app.core.config import settings


class SessionService:
    """Manage user sessions and token blacklisting in Redis."""
    
    def __init__(self):
        """Initialize Redis connection."""
        self.redis: Optional[redis.Redis] = None
    
    async def connect(self):
        """Establish Redis connection."""
        if not self.redis:
            self.redis = await redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
    
    async def close(self):
        """Close Redis connection."""
        if self.redis:
            await self.redis.close()
    
    async def create_session(
        self,
        user_id: str,
        session_data: Dict[str, Any],
        expire_minutes: Optional[int] = None
    ) -> str:
        """
        Create a new user session in Redis.
        
        Args:
            user_id: User UUID
            session_data: Dictionary containing session info (e.g., {"ip": "...", "user_agent": "..."})
            expire_minutes: Session TTL, defaults to settings.SESSION_EXPIRE_MINUTES
            
        Returns:
            Session ID
            
        Example:
            >>> await session_service.create_session(
            ...     "user-123",
            ...     {"ip": "192.168.1.1", "user_agent": "Chrome"}
            ... )
            'session:user-123'
        """
        await self.connect()
        
        session_key = f"session:{user_id}"
        expire_time = expire_minutes or settings.SESSION_EXPIRE_MINUTES
        
        # Store session data as JSON
        await self.redis.setex(
            session_key,
            timedelta(minutes=expire_time),
            json.dumps(session_data)
        )
        
        return session_key
    
    async def get_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve session data for a user.
        
        Args:
            user_id: User UUID
            
        Returns:
            Session data dictionary or None if session doesn't exist
            
        Example:
            >>> data = await session_service.get_session("user-123")
            >>> data["ip"]
            '192.168.1.1'
        """
        await self.connect()
        
        session_key = f"session:{user_id}"
        session_data = await self.redis.get(session_key)
        
        if session_data:
            return json.loads(session_data)
        return None
    
    async def delete_session(self, user_id: str) -> bool:
        """
        Delete a user session (used during logout).
        
        Args:
            user_id: User UUID
            
        Returns:
            True if session was deleted, False if it didn't exist
            
        Example:
            >>> await session_service.delete_session("user-123")
            True
        """
        await self.connect()
        
        session_key = f"session:{user_id}"
        result = await self.redis.delete(session_key)
        return result > 0
    
    async def refresh_session(self, user_id: str, expire_minutes: Optional[int] = None) -> bool:
        """
        Extend session expiration time (used during token refresh).
        
        Args:
            user_id: User UUID
            expire_minutes: New TTL, defaults to settings.SESSION_EXPIRE_MINUTES
            
        Returns:
            True if session was refreshed, False if it doesn't exist
            
        Example:
            >>> await session_service.refresh_session("user-123")
            True
        """
        await self.connect()
        
        session_key = f"session:{user_id}"
        expire_time = expire_minutes or settings.SESSION_EXPIRE_MINUTES
        
        # Check if session exists
        exists = await self.redis.exists(session_key)
        if not exists:
            return False
        
        # Extend expiration
        await self.redis.expire(session_key, timedelta(minutes=expire_time))
        return True
    
    async def blacklist_token(self, jti: str, expires_in_seconds: int):
        """
        Add a token JTI to the blacklist (used during logout or token invalidation).
        
        Args:
            jti: JWT ID (JTI claim from token)
            expires_in_seconds: How long to keep in blacklist (should match token exp)
            
        Example:
            >>> await session_service.blacklist_token("abc-123-def", 3600)
        """
        await self.connect()
        
        blacklist_key = f"blacklist:{jti}"
        
        # Store with expiration matching the token's remaining lifetime
        await self.redis.setex(
            blacklist_key,
            timedelta(seconds=expires_in_seconds),
            "1"
        )
    
    async def is_token_blacklisted(self, jti: str) -> bool:
        """
        Check if a token JTI is blacklisted.
        
        Args:
            jti: JWT ID (JTI claim from token)
            
        Returns:
            True if token is blacklisted, False otherwise
            
        Example:
            >>> await session_service.is_token_blacklisted("abc-123-def")
            False
        """
        await self.connect()
        
        blacklist_key = f"blacklist:{jti}"
        exists = await self.redis.exists(blacklist_key)
        return exists > 0
    
    async def increment_login_attempts(self, identifier: str) -> int:
        """
        Increment login attempt counter for rate limiting.
        
        Args:
            identifier: Email or IP address
            
        Returns:
            Current number of attempts
            
        Example:
            >>> attempts = await session_service.increment_login_attempts("user@example.com")
            >>> attempts
            1
        """
        await self.connect()
        
        attempts_key = f"login_attempts:{identifier}"
        
        # Increment counter
        attempts = await self.redis.incr(attempts_key)
        
        # Set expiration on first attempt
        if attempts == 1:
            await self.redis.expire(
                attempts_key,
                timedelta(minutes=settings.LOGIN_RATE_LIMIT_WINDOW_MINUTES)
            )
        
        return attempts
    
    async def get_login_attempts(self, identifier: str) -> int:
        """
        Get current login attempt count.
        
        Args:
            identifier: Email or IP address
            
        Returns:
            Number of attempts in the current window
            
        Example:
            >>> attempts = await session_service.get_login_attempts("user@example.com")
            >>> attempts
            3
        """
        await self.connect()
        
        attempts_key = f"login_attempts:{identifier}"
        attempts = await self.redis.get(attempts_key)
        
        return int(attempts) if attempts else 0
    
    async def reset_login_attempts(self, identifier: str):
        """
        Reset login attempt counter (called after successful login).
        
        Args:
            identifier: Email or IP address
            
        Example:
            >>> await session_service.reset_login_attempts("user@example.com")
        """
        await self.connect()
        
        attempts_key = f"login_attempts:{identifier}"
        await self.redis.delete(attempts_key)


# Global instance
session_service = SessionService()
