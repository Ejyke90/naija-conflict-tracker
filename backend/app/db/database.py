from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import os

# Configure engine parameters based on environment and database type
def get_database_url_and_params():
    database_url = settings.DATABASE_URL
    engine_kwargs = {}
    
    # Check if we're using PostgreSQL in production (Railway, Neon, etc.)
    if database_url.startswith("postgresql://") or database_url.startswith("postgres://"):
        # Production PostgreSQL settings for stability
        engine_kwargs.update({
            "pool_size": 10,
            "max_overflow": 20,
            "pool_recycle": 300,  # Recycle connections every 5 minutes
            "pool_pre_ping": True,  # Verify connections before use
            "pool_timeout": 30,  # Timeout after 30 seconds
        })
        
        # Add SSL configuration for cloud PostgreSQL
        if "railway" in database_url or "neon" in database_url or os.getenv("RAILWAY_ENVIRONMENT_NAME"):
            engine_kwargs["connect_args"] = {
                "sslmode": "require",
                "sslcert": None,
                "sslkey": None,
                "sslrootcert": None,
                "application_name": "nextier-conflict-tracker"
            }
    
    elif database_url.startswith("sqlite://"):
        # SQLite settings for local development
        engine_kwargs.update({
            "pool_timeout": 20,
            "pool_recycle": -1,
            "pool_pre_ping": True,
            "connect_args": {"check_same_thread": False}
        })
    
    return database_url, engine_kwargs

# Create SQLAlchemy engine with appropriate parameters
database_url, engine_kwargs = get_database_url_and_params()
engine = create_engine(database_url, **engine_kwargs)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
