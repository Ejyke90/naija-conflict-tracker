"""
Password hashing and verification service using bcrypt.
"""
import hashlib
import secrets
from passlib.context import CryptContext

# Create password context with bcrypt
# Lower cost factor for initial testing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=4)


def hash_password(plain_password: str) -> str:
    """
    Hash a plain password.
    
    For now using a simple approach due to bcrypt issues in Railway environment.
    TODO: Fix bcrypt implementation.
    """
    try:
        # Try bcrypt first
        return pwd_context.hash(plain_password)
    except Exception as e:
        # Fallback to SHA256 + salt for testing
        salt = secrets.token_hex(16)
        hashed = hashlib.sha256((plain_password + salt).encode()).hexdigest()
        return f"sha256${salt}${hashed}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hash.
    """
    try:
        # Try bcrypt first
        if hashed_password.startswith("$2b$"):
            return pwd_context.verify(plain_password, hashed_password)
        elif hashed_password.startswith("sha256$"):
            # Handle SHA256 fallback
            parts = hashed_password.split("$")
            if len(parts) == 3:
                _, salt, stored_hash = parts
                test_hash = hashlib.sha256((plain_password + salt).encode()).hexdigest()
                return test_hash == stored_hash
        return False
    except Exception:
        return False


def needs_update(hashed_password: str) -> bool:
    """
    Check if a password hash needs to be updated.
    """
    try:
        return pwd_context.needs_update(hashed_password)
    except Exception:
        # SHA256 hashes should be updated to bcrypt when possible
        return hashed_password.startswith("sha256$")
