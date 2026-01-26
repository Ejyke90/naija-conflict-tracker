"""
Pydantic schemas for authentication endpoints.
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID


# ===== Request Schemas =====

class UserRegisterRequest(BaseModel):
    """Schema for user registration."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=100, description="Password (min 8 characters)")
    full_name: Optional[str] = Field(None, max_length=255, description="User's full name")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "analyst@nextier.org",
                "password": "SecureP@ssw0rd123",
                "full_name": "John Doe"
            }
        }
    )


class UserLoginRequest(BaseModel):
    """Schema for user login."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "analyst@nextier.org",
                "password": "SecureP@ssw0rd123"
            }
        }
    )


class TokenRefreshRequest(BaseModel):
    """Schema for token refresh."""
    refresh_token: str = Field(..., description="Refresh token from login")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }
    )


class PasswordResetRequest(BaseModel):
    """Schema for requesting password reset."""
    email: EmailStr = Field(..., description="Email of account to reset")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "analyst@nextier.org"
            }
        }
    )


class PasswordResetConfirm(BaseModel):
    """Schema for confirming password reset with token."""
    token: str = Field(..., description="Reset token from email")
    new_password: str = Field(..., min_length=8, max_length=100, description="New password")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "token": "abc123def456",
                "new_password": "NewSecureP@ssw0rd456"
            }
        }
    )


# ===== Response Schemas =====

class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str = Field(..., description="JWT access token (1 hour expiry)")
    refresh_token: str = Field(..., description="JWT refresh token (7 days expiry)")
    token_type: str = Field(default="bearer", description="Token type")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }
    )


class UserResponse(BaseModel):
    """Schema for user data response."""
    id: UUID
    email: str
    role: str
    full_name: Optional[str] = None
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool
    
    model_config = ConfigDict(
        from_attributes=True,  # Allows creating from SQLAlchemy models
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "analyst@nextier.org",
                "role": "analyst",
                "full_name": "John Doe",
                "created_at": "2024-01-15T10:30:00Z",
                "last_login": "2024-01-15T14:20:00Z",
                "is_active": True
            }
        }
    )


class LoginResponse(BaseModel):
    """Schema for login response (includes tokens + user data)."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "analyst@nextier.org",
                    "role": "analyst",
                    "full_name": "John Doe",
                    "created_at": "2024-01-15T10:30:00Z",
                    "last_login": "2024-01-15T14:20:00Z",
                    "is_active": True
                }
            }
        }
    )


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Operation successful"
            }
        }
    )


class ErrorResponse(BaseModel):
    """Error response schema."""
    detail: str
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "detail": "Invalid credentials"
            }
        }
    )
