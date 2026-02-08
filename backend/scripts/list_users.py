#!/usr/bin/env python3
"""
List all users in the database with their emails and roles.
"""
import psycopg2
import os
import sys

def list_users():
    db_url = os.getenv("DATABASE_URL") or os.getenv("NEON_URL")
    if not db_url:
        print("❌ Error: DATABASE_URL environment variable not set")
        sys.exit(1)
    
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        cur.execute("""
            SELECT id, email, role, full_name, created_at, last_login, is_active 
            FROM users 
            ORDER BY created_at DESC
        """)
        
        users = cur.fetchall()
        
        print(f"\n📊 Found {len(users)} users:\n")
        print(f"{'Email':<40} {'Role':<10} {'Active':<8} {'Last Login':<20}")
        print("=" * 90)
        
        for user in users:
            user_id, email, role, full_name, created_at, last_login, is_active = user
            last_login_str = str(last_login)[:19] if last_login else "Never"
            active_str = "Yes" if is_active else "No"
            print(f"{email:<40} {role:<10} {active_str:<8} {last_login_str:<20}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    list_users()
