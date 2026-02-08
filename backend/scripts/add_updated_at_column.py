#!/usr/bin/env python3
"""
Apply migration to add updated_at column to users table.
"""
import psycopg2
import os
import sys

def apply_migration():
    db_url = os.getenv("DATABASE_URL") or os.getenv("NEON_URL")
    if not db_url:
        print("❌ Error: DATABASE_URL or NEON_URL environment variable not set")
        sys.exit(1)
    
    print(f"🔗 Connecting to database...")
    
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        print("📝 Adding updated_at column to users table...")
        
        # Add the column
        cur.execute("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL;
        """)
        
        # Update existing rows
        cur.execute("""
            UPDATE users 
            SET updated_at = created_at 
            WHERE updated_at IS NULL;
        """)
        
        # Verify the column was added
        cur.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'users' 
              AND column_name = 'updated_at';
        """)
        
        result = cur.fetchone()
        
        if result:
            print(f"✅ Migration successful!")
            print(f"   Column: {result[0]}")
            print(f"   Data Type: {result[1]}")
            print(f"   Nullable: {result[2]}")
            print(f"   Default: {result[3]}")
        else:
            print("❌ Error: Column was not added")
            sys.exit(1)
        
        # Check how many users have updated_at set
        cur.execute("SELECT COUNT(*) FROM users WHERE updated_at IS NOT NULL")
        count = cur.fetchone()[0]
        print(f"   Users with updated_at: {count}")
        
        conn.commit()
        cur.close()
        conn.close()
        
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Error applying migration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    apply_migration()
