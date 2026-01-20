from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    # Project
    PROJECT_NAME: str = "Nigeria Conflict Tracker"
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
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS
    ALLOWED_HOSTS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://your-vercel-app.vercel.app"
    ]
    
    # External APIs
    TWITTER_BEARER_TOKEN: Optional[str] = os.getenv("TWITTER_BEARER_TOKEN")
    MAPBOX_ACCESS_TOKEN: Optional[str] = os.getenv("MAPBOX_ACCESS_TOKEN")
    
    # Data Processing
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    
    class Config:
        env_file = ".env"


settings = Settings()
