#!/usr/bin/env python3
"""
Fix migration conflict by checking if tables exist and setting proper version.
This script resolves the "countries table already exists" error.
"""
import psycopg2
import os
from sqlalchemy import create_engine, text
from app.core.config import settings

def fix_migration_conflict():
    """Fix migration conflict by ensuring proper alembic version state"""
    
    # Get database URL from settings
    database_url = settings.DATABASE_URL
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Check if alembic_version table exists
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'alembic_version'
                )
            """))
            alembic_exists = result.scalar()
            
            print(f"📊 Alembic version table exists: {alembic_exists}")
            
            # Check if countries table exists
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'countries'
                )
            """))
            countries_exists = result.scalar()
            
            print(f"📊 Countries table exists: {countries_exists}")
            
            if alembic_exists:
                # Get current version
                try:
                    result = conn.execute(text("SELECT version_num FROM alembic_version"))
                    current_version = result.scalar()
                    print(f"📊 Current alembic version: {current_version}")
                except:
                    print("📊 No version found in alembic_version table")
                    current_version = None
                
                # Clear and set to version 011 (our target)
                conn.execute(text("DELETE FROM alembic_version"))
                conn.execute(text("INSERT INTO alembic_version (version_num) VALUES ('011')"))
                conn.commit()
                print("✅ Set alembic version to 011")
            else:
                print("ℹ️  No alembic_version table - will be created by first migration")
            
            # Verify key tables exist
            tables_to_check = ['countries', 'regions', 'conflict_types', 'actors', 'locations']
            for table in tables_to_check:
                result = conn.execute(text(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = '{table}'
                    )
                """))
                exists = result.scalar()
                status = "✅" if exists else "❌"
                print(f"{status} {table} table exists: {exists}")
            
            print("\n🎉 Migration conflict fix completed!")
            print("📝 Next steps:")
            print("   1. Restart the backend application")
            print("   2. Test /api/v1/analytics/stats endpoint")
            print("   3. Test registration endpoint")
            
    except Exception as e:
        print(f"❌ Error fixing migration conflict: {e}")
        raise

if __name__ == "__main__":
    fix_migration_conflict()
