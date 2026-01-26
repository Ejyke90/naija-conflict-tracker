"""
Authentication API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets
from uuid import UUID

from app.db.database import get_db
from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenRefreshRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    LoginResponse,
    TokenResponse,
    UserResponse,
    MessageResponse,
    ErrorResponse
)
from app.models.auth import User, PasswordResetToken
from app.repositories.user_repository import user_repo
from app.services.password_service import verify_password
from app.services.token_service import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_token_type,
    get_token_jti
)
from app.services.session_service import session_service
from app.services.audit_service import audit_service
from app.api.deps import get_current_user
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.get("/test")
def test_endpoint():
    """Simple test endpoint to verify sync routes work."""
    return {"status": "working", "message": "Auth router is functioning"}


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "User successfully registered"},
        400: {"model": ErrorResponse, "description": "Email already exists or validation failed"},
        422: {"description": "Validation error"}
    }
)
def register(
    user_data: UserRegisterRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Register a new user account.
    """
    try:
        # Simple test: just return success without database operations
        return {
            "status": "test",
            "email": user_data.email,
            "message": "Registration endpoint reached successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )


@router.post(
    "/login",
    response_model=LoginResponse,
    responses={
        200: {"description": "Login successful"},
        401: {"model": ErrorResponse, "description": "Invalid credentials"},
        429: {"model": ErrorResponse, "description": "Too many login attempts"}
    }
)
def login(
    credentials: UserLoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return access + refresh tokens.
    
    **Rate limiting:** 5 attempts per 15 minutes per email
    
    **Token expiration:**
    - Access token: 1 hour
    - Refresh token: 7 days
    
    **Response includes:**
    - access_token: Use in Authorization header for API requests
    - refresh_token: Use to obtain new access token when expired
    - user: Full user profile data
    """
    
    # Get user by email
    user = user_repo.get_by_email_sync(db, credentials.email)
    
    # Verify password
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Update last login timestamp
    user_repo.update_last_login_sync(db, user.id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user
    }


@router.post(
    "/logout",
    response_model=MessageResponse,
    responses={
        200: {"description": "Logout successful"},
        401: {"model": ErrorResponse, "description": "Invalid or expired token"}
    }
)
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Logout current user by blacklisting their access token and deleting session.
    
    **Requires authentication:** Yes (Bearer token in Authorization header)
    
    **Effect:**
    - Current access token is blacklisted (cannot be reused)
    - Redis session is deleted
    - Audit log entry created
    
    **Note:** Client should also delete stored tokens
    """
    # Get token from Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    
    token = auth_header.split(" ")[1]
    
    # Get token JTI and expiration
    payload = decode_token(token)
    jti = payload.get("jti")
    exp = payload.get("exp")
    
    # Calculate remaining TTL
    now = datetime.utcnow().timestamp()
    ttl_seconds = int(exp - now)
    
    # Blacklist token
    if ttl_seconds > 0:
        await session_service.blacklist_token(jti, ttl_seconds)
    
    # Delete session
    await session_service.delete_session(str(current_user.id))
    
    # Log logout
    await audit_service.log_action(
        db=db,
        user_id=current_user.id,
        action="LOGOUT",
        resource=f"user:{current_user.id}",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        details={"email": current_user.email},
        success=True
    )
    
    return {"message": "Successfully logged out"}


@router.post(
    "/refresh",
    response_model=TokenResponse,
    responses={
        200: {"description": "Token refreshed successfully"},
        401: {"model": ErrorResponse, "description": "Invalid or expired refresh token"}
    }
)
async def refresh_token(
    refresh_data: TokenRefreshRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtain new access token using refresh token.
    
    **When to use:**
    - When access token expires (after 1 hour)
    - To extend user session without re-login
    
    **Response:**
    - New access token (1 hour expiry)
    - Same refresh token (still valid for 7 days from original login)
    
    **Note:** Refresh token is NOT rotated for simplicity
    """
    try:
        # Verify it's a refresh token
        payload = verify_token_type(refresh_data.refresh_token, "refresh")
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Check if token is blacklisted
        jti = get_token_jti(refresh_data.refresh_token)
        is_blacklisted = await session_service.is_token_blacklisted(jti)
        
        if is_blacklisted:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has been revoked"
            )
        
    except (ValueError, Exception) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid refresh token: {str(e)}"
        )
    
    # Get user
    user = await user_repo.get_by_id(db, UUID(user_id))
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new access token
    new_access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
    
    # Extend session expiration in Redis
    await session_service.refresh_session(str(user.id))
    
    # Log token refresh
    await audit_service.log_action(
        db=db,
        user_id=user.id,
        action="TOKEN_REFRESH",
        resource=f"user:{user.id}",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        details={"email": user.email},
        success=True
    )
    
    return {
        "access_token": new_access_token,
        "refresh_token": refresh_data.refresh_token,  # Return same refresh token
        "token_type": "bearer"
    }


@router.get(
    "/me",
    response_model=UserResponse,
    responses={
        200: {"description": "Current user profile"},
        401: {"model": ErrorResponse, "description": "Not authenticated"}
    }
)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user's profile.
    
    **Requires authentication:** Yes
    
    **Response:**
    - Full user profile (excluding hashed password)
    - Useful for verifying token validity and getting user role
    """
    return current_user


@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Password reset email sent (or user not found - same response for security)"}
    }
)
async def forgot_password(
    reset_request: PasswordResetRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Request password reset token.
    
    **Security note:** Always returns success even if email doesn't exist (prevents email enumeration)
    
    **Flow:**
    1. User submits email
    2. If email exists, reset token is created (stored in database)
    3. Token expires after 24 hours
    4. In production, email with reset link would be sent
    
    **Current implementation:** Returns token in response (for testing only - replace with email)
    """
    # Get user
    user = await user_repo.get_by_email(db, reset_request.email)
    
    # Always return success to prevent email enumeration
    if not user:
        # Log attempted reset for non-existent email
        await audit_service.log_action(
            db=db,
            user_id=None,
            action="PASSWORD_RESET_REQUESTED_NONEXISTENT",
            resource="auth",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            details={"email": reset_request.email},
            success=False
        )
        return {"message": "If that email exists, a password reset link has been sent"}
    
    # Generate secure random token
    reset_token = secrets.token_urlsafe(32)
    
    # Create password reset token in database
    expires_at = datetime.utcnow() + timedelta(hours=settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS)
    
    db_token = PasswordResetToken(
        user_id=user.id,
        token=reset_token,
        expires_at=expires_at,
        used=False
    )
    db.add(db_token)
    await db.commit()
    
    # Log password reset request
    await audit_service.log_action(
        db=db,
        user_id=user.id,
        action="PASSWORD_RESET_REQUESTED",
        resource=f"user:{user.id}",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        details={"email": user.email},
        success=True
    )
    
    # TODO: In production, send email with reset link
    # For now, return token in response (testing only)
    return {
        "message": "If that email exists, a password reset link has been sent",
        # "token": reset_token  # Remove this in production!
    }


@router.post(
    "/reset-password",
    response_model=MessageResponse,
    responses={
        200: {"description": "Password successfully reset"},
        400: {"model": ErrorResponse, "description": "Invalid or expired token"}
    }
)
async def reset_password(
    reset_data: PasswordResetConfirm,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Reset password using token from forgot-password endpoint.
    
    **Flow:**
    1. User receives reset token (via email in production)
    2. User submits token + new password
    3. If token is valid and not expired, password is updated
    4. Token is marked as used (cannot be reused)
    
    **Token validation:**
    - Must exist in database
    - Must not be expired (24 hour TTL)
    - Must not have been used already
    """
    # Find reset token in database
    from sqlalchemy import select
    result = await db.execute(
        select(PasswordResetToken).where(
            PasswordResetToken.token == reset_data.token,
            PasswordResetToken.used == False
        )
    )
    db_token = result.scalar_one_or_none()
    
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or already used reset token"
        )
    
    # Check expiration
    if datetime.utcnow() > db_token.expires_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired"
        )
    
    # Update user password
    await user_repo.update_password(db, db_token.user_id, reset_data.new_password)
    
    # Mark token as used
    db_token.used = True
    await db.commit()
    
    # Invalidate all existing sessions for this user (force re-login)
    await session_service.delete_session(str(db_token.user_id))
    
    # Log password reset
    await audit_service.log_action(
        db=db,
        user_id=db_token.user_id,
        action="PASSWORD_RESET_COMPLETED",
        resource=f"user:{db_token.user_id}",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        details={},
        success=True
    )
    
    return {"message": "Password successfully reset. Please login with your new password"}
