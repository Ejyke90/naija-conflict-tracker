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
        # High-latency optimized PostgreSQL settings
        # Reduced pool size to prevent TCP_OVERWINDOW
        # Shorter connection lifetimes to avoid stale connections
        engine_kwargs.update({
            "pool_size": 8,  # Reduced from 20 to prevent connection pile-up
            "max_overflow": 5,  # Reduced from 10 for better control
            "pool_recycle": 180,  # Reduced from 300s (3 minutes) for high-latency
            "pool_pre_ping": True,  # Keep this - critical for detecting dead connections
            "pool_timeout": 15,  # Reduced from 30s for faster failure detection
            "echo": False,  # Disable SQL logging in production
        })
        
        # High-latency optimized connection arguments
        connect_args = {
            "sslmode": "require",
            "sslcert": None,
            "sslkey": None,
            "sslrootcert": None,
            "application_name": "nextier-conflict-tracker",
            "connect_timeout": 8,  # Reduced from 10s for faster connection attempts
        }
        
        # Neon-specific optimizations
        if "neon" in database_url.lower():
            # Fixed connection pooling for production stability
            # Increased pool size to handle concurrent requests per Step 2 requirements
            engine_kwargs.update({
                "pool_size": 10,             # Increased to 10 per Step 2 requirements (was 5)
                "max_overflow": 20,          # Increased to 20 per Step 2 requirements (was 10)
                "pool_recycle": 300,         # Increased from 45s to reduce connection churn
                "pool_timeout": 30,          # Increased from 3s to prevent premature timeouts
                "pool_pre_ping": True,        # Critical for detecting dead connections
                "echo": False,               # Disable SQL logging overhead
            })
            connect_args.update({
                "connect_timeout": 10,       # Increased from 1s for more reliable connections
                "sslmode": "require",        # Required for Neon
                "application_name": "naija-conflict-tracker",
            })
        
        # Railway-specific optimizations
        elif "railway" in database_url.lower() or os.getenv("RAILWAY_ENVIRONMENT_NAME"):
            # Railway has different network characteristics
            engine_kwargs.update({
                "pool_size": 10,  # Medium pool for Railway
                "max_overflow": 3,
                "pool_recycle": 240,  # 4 minutes
            })
            connect_args["server_settings"]["statement_timeout"] = "30000"  # 30 seconds for Railway
        
        # Generic cloud PostgreSQL
        else:
            # Standard cloud optimizations
            engine_kwargs.update({
                "pool_size": 6,
                "max_overflow": 3,
                "pool_recycle": 200,  # ~3.3 minutes
            })
        
        engine_kwargs["connect_args"] = connect_args
    
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
