"""
Password hashing and verification service using bcrypt with enhanced error handling.
"""
import hashlib
import secrets
import logging
from passlib.context import CryptContext

logger = logging.getLogger(__name__)

# Create password context with bcrypt and enhanced error handling
try:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=4)
    # Test if bcrypt is working properly
    test_hash = pwd_context.hash("test")
    logger.info("Bcrypt successfully initialized")
except Exception as e:
    logger.warning(f"Bcrypt initialization failed: {e}, using fallback")
    # Create a dummy context that will always fail for bcrypt
    pwd_context = None


def hash_password(plain_password: str) -> str:
    """
    Hash a plain password.
    
    Uses bcrypt if available, falls back to SHA256 + salt if bcrypt fails.
    """
    # Always use fallback in Railway environment to avoid bcrypt issues
    try:
        if pwd_context is not None:
            # Try bcrypt first
            return pwd_context.hash(plain_password)
    except Exception as e:
        logger.warning(f"Bcrypt hashing failed: {e}, using SHA256 fallback")
    
    # Fallback to SHA256 + salt
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((plain_password + salt).encode()).hexdigest()
    return f"sha256${salt}${hashed}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hash.
    """
    try:
        # Try bcrypt first
        if hashed_password.startswith("$2b$") and pwd_context is not None:
            return pwd_context.verify(plain_password, hashed_password)
        elif hashed_password.startswith("sha256$"):
            # Handle SHA256 fallback
            parts = hashed_password.split("$")
            if len(parts) == 3:
                _, salt, stored_hash = parts
                test_hash = hashlib.sha256((plain_password + salt).encode()).hexdigest()
                return test_hash == stored_hash
        return False
    except Exception as e:
        logger.warning(f"Password verification failed: {e}")
        return False


def needs_update(hashed_password: str) -> bool:
    """
    Check if a password hash needs to be updated.
    """
    try:
        if pwd_context is not None and not hashed_password.startswith("sha256$"):
            return pwd_context.needs_update(hashed_password)
    except Exception:
        pass
    # SHA256 hashes should be updated to bcrypt when possible
    return hashed_password.startswith("sha256$")
