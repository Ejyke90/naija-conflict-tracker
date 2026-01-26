"""
Authentication API endpoints - simplified version for basic auth.
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
    LoginResponse,
    UserResponse,
    MessageResponse,
    ErrorResponse
)
from app.models.auth import User
from app.repositories.user_repository import user_repo
from app.services.password_service import verify_password
from app.services.token_service import (
    create_access_token,
    create_refresh_token,
)
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
        # Check if email already exists
        existing_user = user_repo.get_by_email_sync(db, user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user with default "viewer" role
        user = user_repo.create_user_sync(
            db=db,
            email=user_data.email,
            password=user_data.password,
            role="viewer",  # Default role
            full_name=user_data.full_name
        )
        
        return user
        
    except HTTPException:
        raise
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
    """
    try:
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
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )


# Simple message endpoint for testing
@router.get("/status")
def auth_status():
    """Check auth service status."""
    return {"status": "auth service running", "endpoints": ["register", "login"]}