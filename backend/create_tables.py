#!/usr/bin/env python3
"""
Create database tables for Railway deployment.
Alternative to alembic migrations for quick setup.
"""
import os
import sys
sys.path.append('/app')

from sqlalchemy import create_engine, text
from app.core.config import settings

def create_tables():
    """Create the basic auth tables needed for the application."""
    engine = create_engine(settings.DATABASE_URL)
    
    # Create users table
    users_sql = """
    CREATE TABLE IF NOT EXISTS users (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        email VARCHAR(255) UNIQUE NOT NULL,
        hashed_password VARCHAR(255) NOT NULL,
        role VARCHAR(50) NOT NULL DEFAULT 'viewer',
        full_name VARCHAR(255),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
        last_login TIMESTAMP WITH TIME ZONE,
        is_active BOOLEAN DEFAULT TRUE NOT NULL
    );
    """
    
    # Create password reset tokens table
    reset_tokens_sql = """
    CREATE TABLE IF NOT EXISTS password_reset_tokens (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID REFERENCES users(id) ON DELETE CASCADE,
        token VARCHAR(255) UNIQUE NOT NULL,
        expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
        used BOOLEAN DEFAULT FALSE NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
    );
    """
    
    # Create audit log table
    audit_log_sql = """
    CREATE TABLE IF NOT EXISTS audit_log (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID REFERENCES users(id) ON DELETE SET NULL,
        action VARCHAR(100) NOT NULL,
        resource VARCHAR(255) NOT NULL,
        ip_address INET,
        user_agent TEXT,
        details JSONB,
        success BOOLEAN NOT NULL,
        timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
    );
    """
    
    try:
        with engine.connect() as connection:
            # Execute table creation
            connection.execute(text(users_sql))
            connection.execute(text(reset_tokens_sql))
            connection.execute(text(audit_log_sql))
            connection.commit()
            
        print("✅ Database tables created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

if __name__ == "__main__":
    success = create_tables()
    sys.exit(0 if success else 1)