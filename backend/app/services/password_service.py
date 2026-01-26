"""
Password hashing and verification service using bcrypt with enhanced error handling.
"""
import hashlib
import secrets
import logging
from passlib.context import CryptContext

logger = logging.getLogger(__name__)

# Create password context with bcrypt and enhanced error handling
def _initialize_bcrypt():
    """Initialize bcrypt with proper error handling"""
    try:
        # Try creating context
        context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=4)
        
        # Test with a simple 4-byte password
        test_password = "test"
        if len(test_password.encode()) <= 72:  # bcrypt limit
            test_hash = context.hash(test_password)
            # Verify the test hash works
            if context.verify(test_password, test_hash):
                logger.info("Bcrypt successfully initialized and tested")
                return context
    except Exception as e:
        logger.warning(f"Bcrypt initialization failed: {e}, using SHA256 fallback")
    
    return None

pwd_context = _initialize_bcrypt()


def hash_password(plain_password: str) -> str:
    """
    Hash a plain password.
    
    Uses bcrypt if available, falls back to SHA256 + salt if bcrypt fails.
    Handles bcrypt's 72-byte password limit.
    """
    # Truncate password if longer than 72 bytes for bcrypt compatibility
    password_bytes = plain_password.encode('utf-8')
    if len(password_bytes) > 72:
        logger.warning(f"Password truncated from {len(password_bytes)} to 72 bytes for bcrypt compatibility")
        plain_password = password_bytes[:72].decode('utf-8', errors='ignore')
    
    # Try bcrypt first if available
    if pwd_context is not None:
        try:
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
