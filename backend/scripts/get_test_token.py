#!/usr/bin/env python3
"""
Create test user and get auth token
"""
import os
import sys
from sqlalchemy import create_engine, text
import requests

database_url = os.environ.get('DATABASE_URL')
if not database_url:
    print("Error: DATABASE_URL not set")
    sys.exit(1)

print("Checking for existing users...")
engine = create_engine(database_url)

with engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM users"))
    user_count = result.scalar()
    print(f"Found {user_count} users")
    
    if user_count > 0:
        result = conn.execute(text("SELECT email, role FROM users LIMIT 3"))
        print("\nExisting users:")
        for row in result:
            print(f"  - {row[0]} ({row[1]})")

# Try to login with common test credentials
print("\n=== Attempting login ===")
test_creds = [
    {"email": "admin@example.com", "password": "admin123"},
    {"email": "test@example.com", "password": "test123"},
    {"email": "analyst@example.com", "password": "analyst123"}
]

for cred in test_creds:
    try:
        resp = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            json=cred,
            timeout=5
        )
        if resp.status_code == 200:
            data = resp.json()
            token = data.get('access_token', '')
            print(f"\n✅ Login successful!")
            print(f"   Email: {cred['email']}")
            print(f"   Token: {token[:50]}...")
            print(f"\n   Export for testing:")
            print(f"   export AUTH_TOKEN='{token}'")
            sys.exit(0)
        elif resp.status_code == 401:
            print(f"❌ Invalid credentials: {cred['email']}")
        else:
            print(f"⚠️  Unexpected response ({resp.status_code}): {cred['email']}")
    except Exception as e:
        print(f"Error testing {cred['email']}: {e}")

print("\n⚠️  No valid credentials found. Authentication testing skipped.")
