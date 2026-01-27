from pydantic_settings import BaseSettings
from typing import List, Optional
import json
import os


class Settings(BaseSettings):
    # Project
    PROJECT_NAME: str = "Nextier Nigeria Conflict Tracker"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = (
        os.getenv("DATABASE_URL")
        or os.getenv("RAILWAY_DATABASE_URL")
        or os.getenv("POSTGRES_URL")
        or os.getenv("POSTGRESQL_URL")
        or "postgresql://postgres:password@localhost:5432/conflict_tracker"
    )
    
    # Redis
    REDIS_URL: str = (
        os.getenv("REDIS_PUBLIC_URL") 
        or os.getenv("REDIS_URL") 
        or "redis://localhost:6379"
    )
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # 1 hour
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # 7 days
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = 24  # 24 hours
    
    # Session management
    SESSION_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Rate limiting
    LOGIN_RATE_LIMIT_ATTEMPTS: int = 5
    LOGIN_RATE_LIMIT_WINDOW_MINUTES: int = 15
    
    # CORS - Allow all Vercel preview deployments and production
    ALLOWED_HOSTS: List[str] = (
        json.loads(os.getenv("ALLOWED_HOSTS"))
        if os.getenv("ALLOWED_HOSTS")
        else ["*"]  # Allow all origins for now - restrict in production
    )
    
    # External APIs
    TWITTER_BEARER_TOKEN: Optional[str] = os.getenv("TWITTER_BEARER_TOKEN")
    MAPBOX_ACCESS_TOKEN: Optional[str] = os.getenv("MAPBOX_ACCESS_TOKEN")
    
    # Data Processing
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    
    model_config = {"extra": "ignore", "protected_namespaces": ()}  # Allow model_ prefix


settings = Settings()
