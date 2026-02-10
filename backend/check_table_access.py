#!/usr/bin/env python3
"""
Check what tables we can actually access
"""

import os
import sys

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def check_table_access():
    """Check what tables exist and are accessible"""
    try:
        from sqlalchemy import create_engine, text
        from core.config import settings
        
        # Create database connection
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.connect() as conn:
            # List all tables we can see
            result = conn.execute(text("""
                SELECT table_name, table_type
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            
            tables = result.fetchall()
            
            print("=== ACCESSIBLE TABLES ===")
            for table_name, table_type in tables:
                print(f"✅ {table_name} ({table_type})")
            
            # Try to access each table
            print(f"\n=== TESTING TABLE ACCESS ===")
            for table_name, _ in tables:
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                    count = result.scalar()
                    print(f"✅ {table_name}: {count} records")
                except Exception as e:
                    print(f"❌ {table_name}: {e}")
            
            # Check specifically for conflicts-related tables
            conflict_tables = [t for t in tables if 'conflict' in t[0].lower()]
            
            if conflict_tables:
                print(f"\n=== CONFLICT-RELATED TABLES ===")
                for table_name, table_type in conflict_tables:
                    try:
                        result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                        count = result.scalar()
                        print(f"✅ {table_name}: {count} records")
                        
                        # Check for kidnapping data
                        if 'kidnapp' in conn.dialect.get_table_names(conn):  # This might not work, but let's try
                            try:
                                result = conn.execute(text(f"""
                                    SELECT COUNT(*) FILTER (WHERE 
                                        (kidnapped_male > 0 OR kidnapped_female > 0 OR kidnapped_unknown > 0)
                                    ) FROM {table_name}
                                """))
                                kidnapping_count = result.scalar()
                                print(f"   🎯 Kidnapping records: {kidnapping_count}")
                            except:
                                pass
                                
                    except Exception as e:
                        print(f"❌ {table_name}: {e}")
            else:
                print(f"\n❌ No conflict-related tables found")
            
            return tables
            
    except Exception as e:
        print(f"❌ Error checking tables: {e}")
        return []

if __name__ == "__main__":
    check_table_access()
