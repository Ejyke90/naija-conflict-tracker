"""
Password hashing and verification service using bcrypt.
"""
from passlib.context import CryptContext

# Create password context with bcrypt
# cost factor of 12 provides good security while maintaining reasonable performance
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


def hash_password(plain_password: str) -> str:
    """
    Hash a plain password using bcrypt with cost factor 12.
    
    Args:
        plain_password: The plaintext password to hash
        
    Returns:
        The bcrypt-hashed password string
        
    Example:
        >>> hashed = hash_password("MyP@ssw0rd")
        >>> print(hashed[:7])
        $2b$12$
    """
    # Bcrypt has a 72-byte limit - truncate if necessary
    password_bytes = plain_password.encode('utf-8')
    if len(password_bytes) > 72:
        # Truncate to 72 bytes at character boundary
        truncated = plain_password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
        return pwd_context.hash(truncated)
    
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a bcrypt hash using constant-time comparison.
    
    Args:
        plain_password: The plaintext password to verify
        hashed_password: The bcrypt hash to verify against
        
    Returns:
        True if the password matches, False otherwise
        
    Example:
        >>> hashed = hash_password("MyP@ssw0rd")
        >>> verify_password("MyP@ssw0rd", hashed)
        True
        >>> verify_password("WrongPassword", hashed)
        False
    """
    return pwd_context.verify(plain_password, hashed_password)


def needs_update(hashed_password: str) -> bool:
    """
    Check if a password hash needs to be updated (e.g., cost factor changed).
    
    Args:
        hashed_password: The bcrypt hash to check
        
    Returns:
        True if the hash should be regenerated, False otherwise
    """
    return pwd_context.needs_update(hashed_password)
