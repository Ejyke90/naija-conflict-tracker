#!/usr/bin/env python3
"""
Create a test user for the conflict tracker
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.services.password_service import hash_password
from app.core.config import settings

def create_test_user():
    """Create a test user directly in the database"""
    db_url = settings.DATABASE_URL
    engine = create_engine(db_url)

    # Create a test user directly
    with engine.connect() as conn:
        hashed_password = hash_password('test12345')
        
        conn.execute(text("""
            INSERT INTO users (name, email, role, password, created_at, updated_at)
            VALUES ('Test User', 'testuser@conflicttracker.com', 'viewer', :password, NOW(), NOW())
        """), {'password': hashed_password})
        
        conn.commit()
        print('Test user created successfully!')
        print('Email: testuser@conflicttracker.com')
        print('Password: test12345')

if __name__ == "__main__":
    create_test_user()
