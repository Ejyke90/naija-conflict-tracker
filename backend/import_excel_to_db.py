"""
ETL Script: Import Nextier's Nigeria Violent Conflicts Database to PostgreSQL
Handles 10,741 records from Excel → PostgreSQL with data cleaning and normalization
"""

import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import warnings
warnings.filterwarnings('ignore')

# Add backend app to path
sys.path.insert(0, str(Path(__file__).parent))
from app.db.database import get_db, engine
from app.models.conflict import Conflict

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
        'Communiity': 'community',  # Typo in original
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
    
    # Remove rows with null dates (can't have events without dates)
    initial_count = len(df_clean)
    df_clean = df_clean[df_clean['event_date'].notna()]
    print(f"   Removed {initial_count - len(df_clean)} records with invalid dates")
    
    # Clean fatalities (ensure numeric)
    df_clean['fatalities'] = pd.to_numeric(df_clean['fatalities'], errors='coerce').fillna(0).astype(int)
    df_clean['civilian_casualties'] = pd.to_numeric(df_clean['civilian_casualties'], errors='coerce').fillna(0).astype(int)
    df_clean['injured'] = pd.to_numeric(df_clean['injured'], errors='coerce').fillna(0).astype(int)
    
    # Clean kidnapped (some are stored as objects like "few", "several")
    def parse_vague_amount(val):
        """Convert vague amounts to estimates"""
        if pd.isna(val):
            return 0
        if isinstance(val, (int, float)):
            return int(val)
        val_lower = str(val).lower()
        vague_mapping = {
            'few': 3,
            'several': 5,
            'many': 10,
            'dozens': 24,
            'scores': 40,
            'hundreds': 100,
            'couple': 2,
            'some': 4
        }
        for term, num in vague_mapping.items():
            if term in val_lower:
                return num
        # Try to extract number
        import re
        match = re.search(r'\d+', str(val))
        if match:
            return int(match.group())
        return 0
    
    df_clean['kidnapped'] = df_clean['kidnapped'].apply(parse_vague_amount)
    
    # Clean displaced
    df_clean['displaced'] = df_clean.get('displaced', pd.Series([0]*len(df_clean))).apply(parse_vague_amount)
    
    # Clean text fields
    text_cols = ['state', 'lga', 'community', 'actor1', 'actor2', 'conflict_type', 'description']
    for col in text_cols:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].fillna('').astype(str).str.strip()
    
    # Standardize state names (title case)
    df_clean['state'] = df_clean['state'].str.title().str.replace(' State', '', regex=False)
    
    # Remove "Unnamed" placeholder data
    df_clean = df_clean[df_clean['state'] != '']
    
    print(f"✅ Cleaned {len(df_clean)} valid records")
    return df_clean


def create_lookup_tables(df, engine):
    """Create normalized lookup tables for states, actors, crisis types"""
    print("📋 Creating lookup tables...")
    
    with engine.connect() as conn:
        # Create states table
        states = df['state'].unique()
        states = [s for s in states if s and s.strip()]
        print(f"   States: {len(states)}")
        
        for state in states:
            region = df[df['state'] == state]['region'].iloc[0] if 'region' in df.columns else None
            conn.execute(text("""
                INSERT INTO states (name, region)
                VALUES (:name, :region)
                ON CONFLICT (name) DO NOTHING
            """), {'name': state, 'region': region})
        
        # Create actors table
        actors = set()
        for col in ['actor1', 'actor2', 'actor3']:
            if col in df.columns:
                actors.update(df[col].dropna().unique())
        actors = [a for a in actors if a and a.strip()]
        print(f"   Actors: {len(actors)}")
        
        for actor in actors:
            conn.execute(text("""
                INSERT INTO actors (name)
                VALUES (:name)
                ON CONFLICT (name) DO NOTHING
            """), {'name': actor})
        
        # Create crisis types table
        crisis_types = df['conflict_type'].dropna().unique() if 'conflict_type' in df.columns else []
        crisis_types = [ct for ct in crisis_types if ct and ct.strip()]
        print(f"   Crisis types: {len(crisis_types)}")
        
        for crisis_type in crisis_types:
            conn.execute(text("""
                INSERT INTO crisis_types (name)
                VALUES (:name)
                ON CONFLICT (name) DO NOTHING
            """), {'name': crisis_type})
        
        conn.commit()
    
    print("✅ Lookup tables created")


def import_conflicts(df, engine):
    """Import conflict records"""
    print(f"📥 Importing {len(df)} conflict records...")
    
    # Prepare records for bulk insert
    records = []
    for idx, row in df.iterrows():
        record = {
            'event_date': row.get('event_date'),
            'state': row.get('state', ''),
            'lga': row.get('lga', ''),
            'community': row.get('community', ''),
            'conflict_type': row.get('conflict_type', ''),
            'actor1': row.get('actor1', ''),
            'actor2': row.get('actor2', ''),
            'actor3': row.get('actor3', ''),
            'fatalities': int(row.get('fatalities', 0)),
            'civilian_casualties': int(row.get('civilian_casualties', 0)),
            'gsa_casualties': int(row.get('gsa_casualties', 0)),
            'injured': int(row.get('injured', 0)),
            'kidnapped': int(row.get('kidnapped', 0)),
            'displaced': int(row.get('displaced', 0)),
            'description': row.get('description', ''),
            'source': row.get('source', ''),
            'source_url': row.get('source_url', ''),
            'data_source': row.get('data_source', 'Nextier Database'),
            'created_at': datetime.now()
        }
        records.append(record)
        
        # Batch insert every 500 records
        if len(records) >= 500:
            _bulk_insert(records, engine)
            records = []
            if idx % 1000 == 0:
                print(f"   Imported {idx}/{len(df)} records...")
    
    # Insert remaining records
    if records:
        _bulk_insert(records, engine)
    
    print(f"✅ Imported {len(df)} records successfully")


def _bulk_insert(records, engine):
    """Helper function for bulk insert"""
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO conflicts (
                event_date, state, lga, community, conflict_type,
                actor1, actor2, actor3,
                fatalities, civilian_casualties, gsa_casualties,
                injured, kidnapped, displaced,
                description, source, source_url, data_source, created_at
            ) VALUES (
                :event_date, :state, :lga, :community, :conflict_type,
                :actor1, :actor2, :actor3,
                :fatalities, :civilian_casualties, :gsa_casualties,
                :injured, :kidnapped, :displaced,
                :description, :source, :source_url, :data_source, :created_at
            )
        """), records)
        conn.commit()


def create_schema_if_needed(engine):
    """Create required tables if they don't exist"""
    print("🏗️  Checking database schema...")
    
    with engine.connect() as conn:
        # Create states table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS states (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) UNIQUE NOT NULL,
                region VARCHAR(50),
                geometry GEOGRAPHY(MULTIPOLYGON, 4326),
                population INTEGER,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """))
        
        # Create actors table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS actors (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) UNIQUE NOT NULL,
                category VARCHAR(50),
                description TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """))
        
        # Create crisis_types table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS crisis_types (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) UNIQUE NOT NULL,
                severity_level INTEGER,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """))
        
        # Create conflicts table
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
                location GEOGRAPHY(POINT, 4326),
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """))
        
        # Create indexes
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_conflicts_event_date ON conflicts(event_date DESC)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_conflicts_state ON conflicts(state)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_conflicts_conflict_type ON conflicts(conflict_type)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_conflicts_fatalities ON conflicts(fatalities DESC)"))
        
        conn.commit()
    
    print("✅ Schema ready")


def main():
    """Main ETL process"""
    print("="*80)
    print("ETL: Nextier Nigeria Violent Conflicts Database → PostgreSQL")
    print("="*80)
    print()
    
    # Check Excel file exists
    if not EXCEL_PATH.exists():
        print(f"❌ Excel file not found: {EXCEL_PATH}")
        return
    
    print(f"📄 Reading Excel file: {EXCEL_PATH.name}")
    
    # Read Excel
    df = pd.read_excel(EXCEL_PATH, sheet_name='Home')
    print(f"✅ Loaded {len(df)} records from Excel")
    print()
    
    # Clean data
    df_clean = clean_data(df)
    print()
    
    # Create schema
    create_schema_if_needed(engine)
    print()
    
    # Create lookup tables
    create_lookup_tables(df_clean, engine)
    print()
    
    # Import conflicts
    import_conflicts(df_clean, engine)
    print()
    
    # Summary statistics
    print("="*80)
    print("📊 IMPORT SUMMARY")
    print("="*80)
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM conflicts")).scalar()
        print(f"Total conflicts imported: {result:,}")
        
        result = conn.execute(text("SELECT MIN(event_date), MAX(event_date) FROM conflicts")).first()
        print(f"Date range: {result[0]} to {result[1]}")
        
        result = conn.execute(text("SELECT COUNT(DISTINCT state) FROM conflicts")).scalar()
        print(f"States affected: {result}")
        
        result = conn.execute(text("SELECT SUM(fatalities) FROM conflicts")).scalar()
        print(f"Total fatalities: {result:,}")
        
        result = conn.execute(text("""
            SELECT state, COUNT(*) as incidents, SUM(fatalities) as deaths
            FROM conflicts
            GROUP BY state
            ORDER BY deaths DESC
            LIMIT 5
        """)).fetchall()
        
        print(f"\nTop 5 states by fatalities:")
        for row in result:
            print(f"   {row[0]:20s} - {row[1]:5,} incidents, {row[2]:6,} deaths")
    
    print()
    print("="*80)
    print("✅ ETL COMPLETE - Data ready for API integration")
    print("="*80)


if __name__ == '__main__':
    main()
