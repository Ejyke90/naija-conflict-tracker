#!/usr/bin/env python3
"""
Excel Data Import Script for Nigeria Conflict Tracker

This script imports conflict data from Excel files into the PostgreSQL database.
It handles the specific format of the Nextier Nigeria Violent Conflicts Database.
"""

import pandas as pd
import sys
import os
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from uuid import uuid4
import argparse
# Removed geoalchemy2 import

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.models.conflict import Conflict
from app.core.config import settings
from app.db.base import Base  # Import Base


def parse_excel_file(file_path: str):
    """Parse the Excel file and extract conflict data"""
    
    print(f"📊 Reading Excel file: {file_path}")
    
    try:
        # Read all sheets
        xl_file = pd.ExcelFile(file_path)
        print(f"📋 Found sheets: {xl_file.sheet_names}")
        
        # Read main data from Sheet2 (contains detailed incident data)
        df_main = pd.read_excel(xl_file, sheet_name='Sheet2', header=None)
        
        # Skip header rows and get actual data
        data_rows = []
        for idx, row in df_main.iterrows():
            if idx >= 4:  # Skip first 4 rows (headers)
                if pd.notna(row.iloc[0]) and isinstance(row.iloc[0], datetime):
                    # Extract incident data
                    incident = {
                        'event_date': row.iloc[0],
                        'community': row.iloc[1] if pd.notna(row.iloc[1]) else None,
                        'lga': row.iloc[2] if pd.notna(row.iloc[2]) else None,
                        'state': row.iloc[3] if pd.notna(row.iloc[3]) else None,
                        'region': row.iloc[4] if pd.notna(row.iloc[4]) else None,
                        'perpetrator_group': row.iloc[5] if pd.notna(row.iloc[5]) else None,
                        'event_type': 'conflict',  # Default type
                        'archetype': 'unknown',    # Will be categorized later
                        'description': f"Incident in {row.iloc[1] if pd.notna(row.iloc[1]) else 'Unknown location'}",
                        'source_type': 'excel_import',
                        'source_url': file_path,
                        'source_reliability': 4,  # High reliability for official database
                        'confidence_score': 0.8,
                        'verified': False
                    }
                    data_rows.append(incident)
        
        print(f"✅ Extracted {len(data_rows)} incident records")
        return data_rows
        
    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")
        return []


def categorize_incident(perpetrator_group: str) -> tuple:
    """Categorize incident type and archetype based on perpetrator"""
    
    if not perpetrator_group:
        return 'conflict', 'unknown'
    
    perpetrator_lower = perpetrator_group.lower()
    
    # Determine event type and archetype
    if 'boko haram' in perpetrator_lower or 'iswap' in perpetrator_lower:
        return 'terrorism', 'terrorism'
    elif 'bandit' in perpetrator_lower:
        return 'armed_attack', 'banditry'
    elif 'herdsmen' in perpetrator_lower or 'farmer' in perpetrator_lower:
        return 'communal_violence', 'farmer_herder_conflict'
    elif 'security' in perpetrator_lower or 'police' in perpetrator_lower or 'military' in perpetrator_lower:
        return 'state_violence', 'extra_judicial_killings'
    elif 'cultist' in perpetrator_lower:
        return 'gang_violence', 'cultism'
    elif 'gunmen' in perpetrator_lower:
        return 'armed_attack', 'banditry'
    else:
        return 'conflict', 'unknown'


def geocode_location(state: str, lga: str, community: str) -> tuple:
    """
    Mock geocoding function. In production, this would use a geocoding service
    to convert location names to coordinates.
    """
    
    # This is a placeholder - implement actual geocoding
    # For now, return approximate coordinates based on state
    
    state_coordinates = {
        'lagos': (6.5244, 3.3792),
        'abuja': (9.0765, 7.3986),
        'kano': (11.9804, 8.5168),
        'borno': (11.8313, 13.1059),
        'rivers': (4.8156, 7.0498),
        'delta': (5.5881, 5.7579),
        'enugu': (6.4419, 7.5018),
        'anambra': (6.2104, 6.9775),
        'imo': (5.5339, 7.0488),
        'abia': (5.4527, 7.5229),
    }
    
    if state and state.lower() in state_coordinates:
        return state_coordinates[state.lower()]
    
    # Default to Nigeria center if state not found
    return (9.0820, 8.6753)


def import_to_database(data_rows: list, db_session):
    """Import parsed data into PostgreSQL database"""
    
    print(f"💾 Importing {len(data_rows)} records to database...")
    
    imported_count = 0
    skipped_count = 0
    
    for row in data_rows:
        try:
            # Categorize the incident
            event_type, archetype = categorize_incident(row['perpetrator_group'])
            
            # Get coordinates
            latitude, longitude = geocode_location(row['state'], row['lga'], row['community'])
            
            # Create conflict record
            conflict = Conflict(
                id=str(uuid4()),
                event_date=row['event_date'],
                event_type=event_type,
                archetype=archetype,
                description=row['description'],
                state=row['state'] or 'Unknown',
                lga=row['lga'],
                community=row['community'],
                location_detail=f"{row['community']}, {row['lga']}, {row['state']}",
                latitude=latitude,
                longitude=longitude,
                perpetrator_group=row['perpetrator_group'],
                source_type=row['source_type'],
                source_url=row['source_url'],
                source_reliability=row['source_reliability'],
                confidence_score=row['confidence_score'],
                verified=row['verified'],
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            db_session.add(conflict)
            imported_count += 1
            
            if imported_count % 100 == 0:
                print(f"   Imported {imported_count} records...")
                
        except Exception as e:
            print(f"⚠️  Skipping record due to error: {e}")
            skipped_count += 1
            continue
    
    # Commit all changes
    try:
        db_session.commit()
        print(f"✅ Successfully imported {imported_count} records")
        if skipped_count > 0:
            print(f"⚠️  Skipped {skipped_count} records due to errors")
    except Exception as e:
        db_session.rollback()
        print(f"❌ Failed to commit to database: {e}")
        raise


def main():
    """Main import function"""
    
    parser = argparse.ArgumentParser(description='Import Excel data to Conflict Tracker database')
    parser.add_argument('--file', required=True, help='Excel file path')
    parser.add_argument('--db-url', default=settings.DATABASE_URL, help='Database URL')
    
    args = parser.parse_args()
    
    # Check if file exists
    if not os.path.exists(args.file):
        print(f"❌ File not found: {args.file}")
        sys.exit(1)
    
    print("🇳🇬 Nigeria Conflict Tracker - Excel Data Import")
    print("=" * 50)
    
    # Setup database connection
    try:
        engine = create_engine(args.db_url)
        Base.metadata.create_all(engine)  # Create tables if they don't exist
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db_session = SessionLocal()
        print("✅ Connected to database")
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        sys.exit(1)
    
    try:
        # Parse Excel file
        data_rows = parse_excel_file(args.file)
        
        if not data_rows:
            print("❌ No data found in Excel file")
            sys.exit(1)
        
        # Import to database
        import_to_database(data_rows, db_session)
        
        print("\n🎉 Import completed successfully!")
        print(f"📊 Total records processed: {len(data_rows)}")
        print(f"💾 Records imported to database: Check database for count")
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        db_session.rollback()
        sys.exit(1)
    
    finally:
        db_session.close()


if __name__ == "__main__":
    main()
