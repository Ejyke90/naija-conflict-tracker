#!/usr/bin/env python3
"""
Check what tables exist in the database
"""

import os
import sys

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def check_database_tables():
    """Check what tables exist"""
    try:
        from sqlalchemy import create_engine, text
        from core.config import settings
        
        # Create database connection
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.connect() as conn:
            # List all tables
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            
            tables = [row[0] for row in result]
            
            print("=== Database Tables ===")
            if tables:
                for table in tables:
                    print(f"✅ {table}")
                    
                # Check if conflicts table exists
                if 'conflicts' in tables:
                    print(f"\n📊 Conflicts table exists - checking data...")
                    result = conn.execute(text("SELECT COUNT(*) FROM conflicts"))
                    count = result.scalar()
                    print(f"   Records: {count}")
                    
                    if count > 0:
                        result = conn.execute(text("""
                            SELECT 
                                COUNT(*) FILTER (WHERE kidnapped_male > 0 OR kidnapped_female > 0 OR kidnapped_unknown > 0) as kidnapping_records,
                                SUM(kidnapped_male + kidnapped_female + kidnapped_unknown) as total_victims
                            FROM conflicts
                        """))
                        kidnapping_stats = result.fetchone()
                        print(f"   Kidnapping records: {kidnapping_stats[0]}")
                        print(f"   Total victims: {kidnapping_stats[1]}")
                else:
                    print(f"\n❌ Conflicts table does not exist")
                    print(f"   This means we need to run migration first")
            else:
                print("❌ No tables found - database is empty")
            
            return tables
            
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return []

if __name__ == "__main__":
    check_database_tables()
