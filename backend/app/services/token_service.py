"""
JWT token creation and validation service.
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from uuid import uuid4
from app.core.config import settings


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Payload data to encode in the token (typically {"sub": user_id, "role": role})
        expires_delta: Optional custom expiration time, defaults to settings.ACCESS_TOKEN_EXPIRE_MINUTES
        
    Returns:
        Encoded JWT token string
        
    Example:
        >>> token = create_access_token({"sub": "user-123", "role": "analyst"})
        >>> print(token[:10])
        eyJhbGciO...
    """
    to_encode = data.copy()
    
    # Set expiration
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Add standard JWT claims
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "jti": str(uuid4()),  # JWT ID for token blacklisting
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Create a JWT refresh token with longer expiration.
    
    Args:
        data: Payload data to encode in the token (typically {"sub": user_id})
        
    Returns:
        Encoded JWT refresh token string
        
    Example:
        >>> token = create_refresh_token({"sub": "user-123"})
        >>> decoded = decode_token(token)
        >>> decoded["type"]
        'refresh'
    """
    to_encode = data.copy()
    
    # Refresh tokens have longer expiration
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "jti": str(uuid4()),
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT token.
    
    Args:
        token: JWT token string to decode
        
    Returns:
        Decoded payload dictionary
        
    Raises:
        JWTError: If token is invalid, expired, or malformed
        
    Example:
        >>> token = create_access_token({"sub": "user-123", "role": "analyst"})
        >>> payload = decode_token(token)
        >>> payload["sub"]
        'user-123'
        >>> payload["role"]
        'analyst'
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise


def verify_token_type(token: str, expected_type: str) -> Dict[str, Any]:
    """
    Decode token and verify it matches the expected type (access/refresh).
    
    Args:
        token: JWT token string to verify
        expected_type: Expected token type ("access" or "refresh")
        
    Returns:
        Decoded payload dictionary if type matches
        
    Raises:
        ValueError: If token type doesn't match expected type
        JWTError: If token is invalid, expired, or malformed
        
    Example:
        >>> access_token = create_access_token({"sub": "user-123"})
        >>> payload = verify_token_type(access_token, "access")  # OK
        >>> verify_token_type(access_token, "refresh")  # Raises ValueError
    """
    payload = decode_token(token)
    
    if payload.get("type") != expected_type:
        raise ValueError(f"Invalid token type. Expected {expected_type}, got {payload.get('type')}")
    
    return payload


def get_token_jti(token: str) -> str:
    """
    Extract the JTI (JWT ID) from a token for blacklisting purposes.
    
    Args:
        token: JWT token string
        
    Returns:
        JTI string from the token
        
    Raises:
        JWTError: If token is invalid or missing JTI
        
    Example:
        >>> token = create_access_token({"sub": "user-123"})
        >>> jti = get_token_jti(token)
        >>> len(jti)  # UUID length
        36
    """
    payload = decode_token(token)
    jti = payload.get("jti")
    
    if not jti:
        raise JWTError("Token missing JTI claim")
    
    return jti
