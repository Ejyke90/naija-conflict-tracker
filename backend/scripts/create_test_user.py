#!/usr/bin/env python3
"""
Create a test user for verifying login functionality.
"""
import psycopg2
import os
import sys
from passlib.context import CryptContext
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_test_user():
    db_url = os.getenv("DATABASE_URL") or os.getenv("NEON_URL")
    if not db_url:
        print("❌ Error: DATABASE_URL environment variable not set")
        sys.exit(1)
    
    email = "logintest@example.com"
    password = "TestPass123!"
    role = "viewer"
    
    print(f"🔗 Connecting to database...")
    
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # Check if user already exists
        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        existing = cur.fetchone()
        
        if existing:
            print(f"✓ User {email} already exists")
            user_id = existing[0]
        else:
            # Hash the password
            hashed_password = pwd_context.hash(password)
            user_id = str(uuid.uuid4())
            
            # Create the user
            cur.execute("""
                INSERT INTO users (id, email, hashed_password, role, full_name, is_active)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, email, hashed_password, role, "Login Test User", True))
            
            conn.commit()
            print(f"✅ Created test user: {email}")
        
        cur.close()
        conn.close()
        
        print(f"\n📧 Test Credentials:")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        print(f"   Role: {role}")
        
        return email, password
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    create_test_user()
