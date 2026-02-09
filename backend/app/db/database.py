from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError, DatabaseError
from app.core.config import settings
import os
import logging

logger = logging.getLogger(__name__)

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
            # Prevent hung connections but allow legitimate slow queries
            engine_kwargs["connect_args"] = {
                "sslmode": "require",
                "sslcert": None,
                "sslkey": None,
                "sslrootcert": None,
                "application_name": "nextier-conflict-tracker",
                "connect_timeout": 10,  # 10s to establish connection
                "options": "-c statement_timeout=30000"  # 30s max per query
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
        # Close session gracefully, suppressing errors from dead connections
        try:
            db.close()
        except (OperationalError, DatabaseError) as e:
            # Connection already closed/dead (e.g., SSL timeout, network failure)
            # Log but don't crash - the connection is being cleaned up anyway
            logger.warning(f"Error closing database session (likely dead connection): {e}")
            # Forcefully invalidate the connection to prevent reuse
            try:
                db.bind.pool.dispose()
            except Exception:
                pass  # Best effort cleanup
