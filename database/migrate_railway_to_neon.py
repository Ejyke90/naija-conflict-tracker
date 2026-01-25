"""
Migration script to transfer data from Railway PostgreSQL to Neon
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import pandas as pd
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def migrate_data():
    """Migrate data from Railway to Neon"""
    
    # Source: Railway PostgreSQL
    railway_url = os.getenv('RAILWAY_DATABASE_URL')
    if not railway_url:
        print("ERROR: RAILWAY_DATABASE_URL not set")
        print("Set it with: export RAILWAY_DATABASE_URL='postgresql://...'")
        return
    
    # Destination: Neon PostgreSQL
    neon_url = os.getenv('NEON_DATABASE_URL')
    if not neon_url:
        print("ERROR: NEON_DATABASE_URL not set")
        print("Set it with: export NEON_DATABASE_URL='postgresql://...?sslmode=require'")
        return
    
    # Ensure SSL mode for Neon
    if 'sslmode' not in neon_url:
        if '?' in neon_url:
            neon_url += '&sslmode=require'
        else:
            neon_url += '?sslmode=require'
    print("🔄 Starting migration from Railway to Neon...")
    print(f"📍 Source: {railway_url[:30]}...")
    print(f"📍 Destination: {neon_url[:30]}...")
    
    try:
        # Connect to Railway
        print("\n1️⃣ Connecting to Railway database...")
        railway_engine = create_engine(railway_url)
        
        # Connect to Neon
        print("2️⃣ Connecting to Neon database...")
        neon_engine = create_engine(neon_url)
        
        # Extract data from Railway
        print("\n3️⃣ Extracting data from Railway...")
        query = """
            SELECT 
                id,
                event_date,
                conflict_type,
                description,
                state,
                lga,
                community,
                actor1,
                actor2,
                actor3,
                fatalities,
                civilian_casualties,
                gsa_casualties,
                injured,
                kidnapped,
                displaced,
                source,
                source_url,
                data_source,
                created_at
            FROM conflicts
            WHERE event_date IS NOT NULL
            ORDER BY event_date DESC
        """
        
        df = pd.read_sql(query, railway_engine)
        print(f"   ✅ Extracted {len(df)} records")
        
        if len(df) == 0:
            print("   ⚠️  No data found in source database")
            return
        
        # Transform data for new schema
        print("\n4️⃣ Transforming data for new schema...")
        df['year'] = pd.to_datetime(df['event_date']).dt.year
        df['month'] = pd.to_datetime(df['event_date']).dt.month
        df['event_type'] = df['conflict_type'].fillna('Unknown')
        df['location'] = df['community']
        df['injuries'] = df['injured'].fillna(0)
        df['displaced_persons'] = df['displaced'].fillna(0)
        df['notes'] = df['description']
        df['verified'] = False
        df['confidence_level'] = 'Medium'
        df['updated_at'] = datetime.now()
        
        # Select only needed columns
        new_df = df[[
            'event_date', 'year', 'month', 'state', 'lga', 'location',
            'event_type', 'conflict_type', 'actor1', 'actor2',
            'fatalities', 'injuries', 'displaced_persons',
            'source', 'notes', 'verified', 'confidence_level',
            'created_at', 'updated_at'
        ]].copy()
        
        # Clean nulls
        new_df = new_df.where(pd.notnull(new_df), None)
        
        print(f"   ✅ Transformed {len(new_df)} records")
        
        # Load data into Neon
        print("\n5️⃣ Loading data into Neon...")
        new_df.to_sql(
            'conflict_events',
            neon_engine,
            if_exists='append',
            index=False,
            method='multi',
            chunksize=1000
        )
        
        print(f"   ✅ Loaded {len(new_df)} records")
        
        # Refresh materialized view
        print("\n6️⃣ Refreshing materialized views...")
        with neon_engine.connect() as conn:
            conn.execute(text("SELECT refresh_dashboard_stats()"))
            conn.commit()
        print("   ✅ Dashboard statistics refreshed")
        
        # Verify migration
        print("\n7️⃣ Verifying migration...")
        with neon_engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM conflict_events"))
            count = result.scalar()
            print(f"   ✅ Verified {count} records in Neon")
        
        print("\n✅ Migration completed successfully!")
        print("\n📊 Next steps:")
        print("   1. Verify data in Neon dashboard")
        print("   2. Update Railway backend DATABASE_URL to Neon connection string")
        print("   3. Redeploy backend on Railway")
        print("   4. Test API endpoint: /api/v1/conflicts")
        print("   5. Verify map displays markers at: https://naija-conflict-tracker.vercel.app/map")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        if 'railway_engine' in locals():
            railway_engine.dispose()
        if 'neon_engine' in locals():
            neon_engine.dispose()

if __name__ == "__main__":
    migrate_data()
