"""
Authentication dependencies for protected routes.
"""
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from jose import JWTError
import logging

from app.db.database import get_db
from app.services.token_service import decode_token, verify_token_type, get_token_jti
from app.services.session_service import session_service
from app.repositories.user_repository import user_repo
from app.models.auth import User
from app.core.config import settings


# HTTP Bearer token scheme
security = HTTPBearer()
logger = logging.getLogger(__name__)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.
    
    Validates:
    - Token signature and expiration
    - Token type (must be "access")
    - Token not blacklisted
    - User exists and is active
    
    Args:
        credentials: Bearer token from Authorization header
        db: Database session
        
    Returns:
        Current authenticated User instance
        
    Raises:
        HTTPException 401: If token is invalid, expired, blacklisted, or user not found
        
    Example:
        @router.get("/protected")
        async def protected_route(current_user: User = Depends(get_current_user)):
            return {"user_id": current_user.id}
    """
    
    # Check if auth is disabled via feature flag
    if not settings.ENABLE_AUTH:
        # Return a demo user when auth is disabled
        if settings.AUTH_BYPASS_USER_ID:
            user = user_repo.get_by_id_sync(db, settings.AUTH_BYPASS_USER_ID)
            if user:
                return user
        
        # Create a default demo user if no bypass user specified
        demo_user = User()
        demo_user.id = 1
        demo_user.email = "demo@naija-conflict-tracker.com"
        demo_user.role = "admin"
        demo_user.name = "Demo User"
        return demo_user
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_expired_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_invalid_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token format",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_revoked_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token has been revoked",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        
        # Decode and verify token
        try:
            payload = verify_token_type(token, "access")
            user_id: str = payload.get("sub")
            
            if user_id is None:
                raise credentials_exception
                
        except JWTError as e:
            # Check if it's an expired token error
            if "expired" in str(e).lower():
                raise token_expired_exception
            else:
                raise token_invalid_exception
        
        # Check if token is blacklisted
        try:
            jti = get_token_jti(token)
            is_blacklisted = await session_service.is_token_blacklisted(jti)
            
            if is_blacklisted:
                raise token_revoked_exception
        except Exception as e:
            # Log session service error but don't block authentication
            logger.warning(f"Session service error: {str(e)}")
        
    except ValueError:
        raise token_invalid_exception
    
    # Get user from database using sync method
    # Convert user_id from string to integer (not UUID)
    try:
        user_id_int = int(user_id)
        user = user_repo.get_by_id_sync(db, user_id_int)
    except (ValueError, TypeError):
        raise credentials_exception
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to get current user and verify they are active.
    
    This is redundant with get_current_user but kept for semantic clarity.
    
    Args:
        current_user: User from get_current_user dependency
        
    Returns:
        Active User instance
        
    Raises:
        HTTPException 403: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


def require_role(required_role: str):
    """
    Dependency factory for role-based access control (RBAC).
    
    Creates a dependency that checks if the current user has the required role.
    
    Role hierarchy:
    - admin: Full access (can access admin, analyst, viewer routes)
    - analyst: Data analysis (can access analyst, viewer routes)
    - viewer: Read-only (can only access viewer routes)
    
    Args:
        required_role: Minimum required role ("admin", "analyst", or "viewer")
        
    Returns:
        Dependency function that validates role
        
    Example:
        @router.post("/admin/users")
        async def create_user(
            user: User = Depends(require_role("admin"))
        ):
            # Only admins can access
            pass
        
        @router.get("/analytics")
        async def get_analytics(
            user: User = Depends(require_role("analyst"))
        ):
            # Analysts and admins can access
            pass
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        # Define role hierarchy
        role_hierarchy = {
            "viewer": 1,
            "analyst": 2,
            "admin": 3
        }
        
        # When auth is disabled, grant all permissions (demo mode)
        if not settings.ENABLE_AUTH:
            return current_user
        
        user_role_level = role_hierarchy.get(current_user.role, 0)
        required_role_level = role_hierarchy.get(required_role, 99)
        
        if user_role_level < required_role_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {required_role}, your role: {current_user.role}"
            )
        
        return current_user
    
    return role_checker


async def get_optional_user(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Dependency to get current user if token is provided, otherwise None.
    
    Useful for endpoints that work for both authenticated and anonymous users,
    but provide different functionality based on authentication status.
    
    Args:
        request: FastAPI request object
        db: Database session
        
    Returns:
        User instance if authenticated, None otherwise
        
    Example:
        @router.get("/conflicts")
        async def get_conflicts(
            user: Optional[User] = Depends(get_optional_user)
        ):
            if user:
                # Show sensitive data to authenticated users
                return conflicts_with_details
            else:
                # Show limited data to anonymous users
                return conflicts_basic
    """
    
    # Check if auth is disabled via feature flag
    if not settings.ENABLE_AUTH:
        # Return demo user for optional auth when disabled
        if settings.AUTH_BYPASS_USER_ID:
            user = user_repo.get_by_id_sync(db, settings.AUTH_BYPASS_USER_ID)
            if user:
                return user
        
        # Create a default demo user
        demo_user = User()
        demo_user.id = 1
        demo_user.email = "demo@naija-conflict-tracker.com"
        demo_user.role = "admin"
        demo_user.name = "Demo User"
        return demo_user
    
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    try:
        token = auth_header.split(" ")[1]
        payload = verify_token_type(token, "access")
        user_id = payload.get("sub")
        
        if user_id:
            # Check blacklist
            jti = get_token_jti(token)
            is_blacklisted = await session_service.is_token_blacklisted(jti)
            
            if not is_blacklisted:
                # Convert string user_id to integer for database query
                try:
                    user_id_int = int(user_id)
                    user = user_repo.get_by_id_sync(db, user_id_int)
                except (ValueError, TypeError):
                    pass
                if user and user.is_active:
                    return user
    except (JWTError, ValueError, Exception):
        # Silently fail for optional auth
        pass
    
    return None
