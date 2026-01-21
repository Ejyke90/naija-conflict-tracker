"""
Standalone ETL Script: Import Excel → PostgreSQL (Railway)
No dependencies on app modules - uses direct SQLAlchemy connection
"""

import sys
import os
from pathlib import Path
sys.path.insert(0, '/opt/homebrew/lib/python3.13/site-packages')

import pandas as pd
import numpy as np
from datetime import datetime
from sqlalchemy import create_engine, text
import warnings
warnings.filterwarnings('ignore')

# Railway PostgreSQL connection (PUBLIC URL for external access)
DATABASE_URL = os.getenv('DATABASE_PUBLIC_URL', 'postgresql://postgres:bxrZnlNamzLLMoFsTrUBHmbegNVIGBEX@shuttle.proxy.rlwy.net:38253/railway')

# Excel file path
EXCEL_PATH = Path(__file__).parent.parent / "Nextier's Nigeria Violent Conflicts Database Original.xlsx"

def clean_data(df):
    """Clean and standardize data"""
    print("🧹 Cleaning data...")
    
    # Rename columns to match our schema
    column_mapping = {
        'Date ': 'event_date',
        'State': 'state',
        'LGA': 'lga',
        'Communiity': 'community',
        'Region': 'region',
        'Actor 1': 'actor1',
        'Actor 2': 'actor2',
        'Actor 3': 'actor3',
        'Crisis Type': 'conflict_type',
        'Action': 'action',
        'Total Deaths': 'fatalities',
        '# Civilian Casualties': 'civilian_casualties',
        '# GSA Casualties': 'gsa_casualties',
        '#Injured Victims': 'injured',
        '#Kidnap Victims': 'kidnapped',
        '# IDPs': 'displaced',
        'Description': 'description',
        'Sources': 'source',
        'Source URL': 'source_url',
        'Data Source': 'data_source'
    }
    
    df_clean = df.rename(columns=column_mapping)
    
    # Clean dates
    df_clean['event_date'] = pd.to_datetime(df_clean['event_date'], errors='coerce')
    
    # Remove rows with null dates
    initial_count = len(df_clean)
    df_clean = df_clean[df_clean['event_date'].notna()]
    print(f"   Removed {initial_count - len(df_clean)} records with invalid dates")
    
    # Clean numeric fields
    df_clean['fatalities'] = pd.to_numeric(df_clean['fatalities'], errors='coerce').fillna(0).astype(int)
    df_clean['civilian_casualties'] = pd.to_numeric(df_clean['civilian_casualties'], errors='coerce').fillna(0).astype(int)
    df_clean['injured'] = pd.to_numeric(df_clean['injured'], errors='coerce').fillna(0).astype(int)
    
    # Parse vague amounts for kidnapped/displaced
    def parse_vague_amount(val):
        if pd.isna(val):
            return 0
        if isinstance(val, (int, float)):
            return int(val)
        val_lower = str(val).lower()
        vague_mapping = {
            'few': 3, 'several': 5, 'many': 10, 'dozens': 24,
            'scores': 40, 'hundreds': 100, 'couple': 2, 'some': 4
        }
        for term, num in vague_mapping.items():
            if term in val_lower:
                return num
        import re
        match = re.search(r'\d+', str(val))
        if match:
            return int(match.group())
        return 0
    
    df_clean['kidnapped'] = df_clean['kidnapped'].apply(parse_vague_amount)
    df_clean['displaced'] = df_clean.get('displaced', pd.Series([0]*len(df_clean))).apply(parse_vague_amount)
    
    # Clean text fields
    text_cols = ['state', 'lga', 'community', 'actor1', 'actor2', 'conflict_type', 'description']
    for col in text_cols:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].fillna('').astype(str).str.strip()
    
    # Standardize state names
    df_clean['state'] = df_clean['state'].str.title().str.replace(' State', '', regex=False)
    df_clean = df_clean[df_clean['state'] != '']
    
    print(f"✅ Cleaned {len(df_clean)} valid records")
    return df_clean


def create_schema(engine):
    """Create database schema"""
    print("🏗️  Creating database schema...")
    
    # Try PostGIS in separate transaction
    try:
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
            conn.commit()
            print("   ✓ PostGIS extension enabled")
    except:
        print("   ⚠ PostGIS not available (will skip geolocation)")
    
    # Create tables in new transaction
    with engine.connect() as conn:
        # States table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS states (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) UNIQUE NOT NULL,
                region VARCHAR(50),
                created_at TIMESTAMP DEFAULT NOW()
            )
        """))
        
        # Actors table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS actors (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """))
        
        # Crisis types table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS crisis_types (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """))
        
        # Main conflicts table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS conflicts (
                id SERIAL PRIMARY KEY,
                event_date DATE NOT NULL,
                state VARCHAR(100),
                lga VARCHAR(100),
                community VARCHAR(255),
                conflict_type VARCHAR(100),
                actor1 VARCHAR(255),
                actor2 VARCHAR(255),
                actor3 VARCHAR(255),
                fatalities INTEGER DEFAULT 0,
                civilian_casualties INTEGER DEFAULT 0,
                gsa_casualties INTEGER DEFAULT 0,
                injured INTEGER DEFAULT 0,
                kidnapped INTEGER DEFAULT 0,
                displaced INTEGER DEFAULT 0,
                description TEXT,
                source VARCHAR(255),
                source_url TEXT,
                data_source VARCHAR(100),
                latitude NUMERIC(10, 7),
                longitude NUMERIC(10, 7),
                created_at TIMESTAMP DEFAULT NOW()
            )
        """))
        
        # Create indexes
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_conflicts_date ON conflicts(event_date DESC)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_conflicts_state ON conflicts(state)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_conflicts_type ON conflicts(conflict_type)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_conflicts_fatalities ON conflicts(fatalities DESC)"))
        
        conn.commit()
    
    print("✅ Schema created")


def import_data(df, engine):
    """Import data to database"""
    print(f"📥 Importing {len(df)} records...")
    
    batch_size = 100
    total = len(df)
    
    for i in range(0, total, batch_size):
        batch = df.iloc[i:i+batch_size]
        records = []
        
        for _, row in batch.iterrows():
            # Helper to safely get string value
            def safe_str(val, max_len=None):
                if pd.isna(val):
                    return ''
                s = str(val).strip()
                return s[:max_len] if max_len else s
            
            # Helper to safely get int value
            def safe_int(val):
                if pd.isna(val):
                    return 0
                try:
                    return int(float(val))
                except:
                    return 0
            
            records.append({
                'event_date': row.get('event_date'),
                'state': safe_str(row.get('state'), 100),
                'lga': safe_str(row.get('lga'), 100),
                'community': safe_str(row.get('community'), 255),
                'conflict_type': safe_str(row.get('conflict_type'), 100),
                'actor1': safe_str(row.get('actor1'), 255),
                'actor2': safe_str(row.get('actor2'), 255),
                'actor3': safe_str(row.get('actor3'), 255),
                'fatalities': safe_int(row.get('fatalities')),
                'civilian_casualties': safe_int(row.get('civilian_casualties')),
                'gsa_casualties': safe_int(row.get('gsa_casualties')),
                'injured': safe_int(row.get('injured')),
                'kidnapped': safe_int(row.get('kidnapped')),
                'displaced': safe_int(row.get('displaced')),
                'description': safe_str(row.get('description'), 5000),
                'source': safe_str(row.get('source'), 255),
                'source_url': safe_str(row.get('source_url'), 1000),
                'data_source': 'Nextier Database'
            })
        
        with engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO conflicts (
                    event_date, state, lga, community, conflict_type,
                    actor1, actor2, actor3,
                    fatalities, civilian_casualties, gsa_casualties,
                    injured, kidnapped, displaced,
                    description, source, source_url, data_source
                ) VALUES (
                    :event_date, :state, :lga, :community, :conflict_type,
                    :actor1, :actor2, :actor3,
                    :fatalities, :civilian_casualties, :gsa_casualties,
                    :injured, :kidnapped, :displaced,
                    :description, :source, :source_url, :data_source
                )
            """), records)
            conn.commit()
        
        if (i + batch_size) % 1000 == 0 or i + batch_size >= total:
            print(f"   Progress: {min(i + batch_size, total)}/{total} records")
    
    print(f"✅ Imported {total} records")


def create_lookup_tables(df, engine):
    """Populate lookup tables"""
    print("📋 Creating lookup tables...")
    
    with engine.connect() as conn:
        # States
        states = df[['state', 'region']].drop_duplicates()
        for _, row in states.iterrows():
            if row['state']:
                conn.execute(text("""
                    INSERT INTO states (name, region)
                    VALUES (:name, :region)
                    ON CONFLICT (name) DO NOTHING
                """), {'name': row['state'], 'region': row.get('region')})
        
        # Actors
        actors = set()
        for col in ['actor1', 'actor2', 'actor3']:
            if col in df.columns:
                actors.update(df[col].dropna().unique())
        for actor in actors:
            if actor and actor.strip():
                conn.execute(text("""
                    INSERT INTO actors (name) VALUES (:name)
                    ON CONFLICT (name) DO NOTHING
                """), {'name': actor})
        
        # Crisis types
        crisis_types = df['conflict_type'].dropna().unique()
        for ct in crisis_types:
            if ct and ct.strip():
                conn.execute(text("""
                    INSERT INTO crisis_types (name) VALUES (:name)
                    ON CONFLICT (name) DO NOTHING
                """), {'name': ct})
        
        conn.commit()
    
    print("✅ Lookup tables populated")


def print_summary(engine):
    """Print import summary"""
    print("\n" + "="*80)
    print("📊 IMPORT SUMMARY")
    print("="*80)
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM conflicts")).scalar()
        print(f"Total conflicts: {result:,}")
        
        result = conn.execute(text("SELECT MIN(event_date), MAX(event_date) FROM conflicts")).first()
        print(f"Date range: {result[0]} to {result[1]}")
        
        result = conn.execute(text("SELECT COUNT(DISTINCT state) FROM conflicts")).scalar()
        print(f"States: {result}")
        
        result = conn.execute(text("SELECT SUM(fatalities) FROM conflicts")).scalar()
        print(f"Total fatalities: {result:,}")
        
        result = conn.execute(text("""
            SELECT state, COUNT(*) as incidents, SUM(fatalities) as deaths
            FROM conflicts
            WHERE state IS NOT NULL AND state != ''
            GROUP BY state
            ORDER BY deaths DESC
            LIMIT 5
        """)).fetchall()
        
        print(f"\n🔥 Top 5 states by fatalities:")
        for row in result:
            print(f"   {row[0]:20s} {row[1]:5,} events, {row[2]:6,} deaths")
    
    print("\n" + "="*80)
    print("✅ DATABASE READY - Update API endpoints to use this data!")
    print("="*80)


def main():
    print("="*80)
    print("ETL: Nextier Excel Database → PostgreSQL (Railway)")
    print("="*80)
    print()
    
    # Check file
    if not EXCEL_PATH.exists():
        print(f"❌ Excel file not found: {EXCEL_PATH}")
        return
    
    # Connect to database
    print(f"🔌 Connecting to Railway PostgreSQL...")
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()")).scalar()
            print(f"✅ Connected: {result.split(',')[0]}")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return
    
    print()
    
    # Load Excel
    print(f"📄 Reading Excel: {EXCEL_PATH.name}")
    df = pd.read_excel(EXCEL_PATH, sheet_name='Home')
    print(f"✅ Loaded {len(df)} records")
    print()
    
    # Clean data
    df_clean = clean_data(df)
    print()
    
    # Create schema
    create_schema(engine)
    print()
    
    # Create lookups
    create_lookup_tables(df_clean, engine)
    print()
    
    # Import conflicts
    import_data(df_clean, engine)
    print()
    
    # Summary
    print_summary(engine)


if __name__ == '__main__':
    main()
