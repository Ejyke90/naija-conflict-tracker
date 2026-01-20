#!/usr/bin/env python3
"""Test database connection and model import"""

import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.append(os.path.dirname(__file__))

from app.core.config import settings

def test_db():
    print(f"DATABASE_URL: {settings.DATABASE_URL}")
    
    try:
        # Create engine
        engine = create_engine(settings.DATABASE_URL)
        print("✅ Engine created")
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print(f"✅ Database connection: {result.fetchone()}")
        
        # Test model import
        try:
            from app.models.conflict import Conflict
            print("✅ Conflict model imported")
            
            # Create session
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            db = SessionLocal()
            
            # Count conflicts
            count = db.query(Conflict).count()
            print(f"✅ Conflicts count: {count}")
            
            db.close()
            
        except Exception as e:
            print(f"❌ Model import error: {e}")
            
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    test_db()
