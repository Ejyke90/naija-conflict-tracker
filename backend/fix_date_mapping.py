#!/usr/bin/env python3
"""
Fix the date mapping issue in PostgreSQL database.

Problem: 
- Original MariaDB data had IDs 1-6005 with correct incident dates (2020-2025)
- PostgreSQL conversion has IDs 19886-24182 but with wrong dates (2026-02-09)
- Need to map the correct dates from original data to current PostgreSQL IDs

Solution:
1. Extract ID-date pairs from original SQL file
2. Connect to production PostgreSQL database
3. Find the mapping pattern between old and new IDs
4. Update PostgreSQL with correct incident dates
"""

import os
import re
import psycopg2
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_original_dates(sql_file_path):
    """Extract ID-date pairs from original MariaDB SQL dump."""
    logger.info(f"Extracting dates from {sql_file_path}")
    
    id_date_map = {}
    
    with open(sql_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find INSERT statements for conflicts table - updated regex pattern
    insert_pattern = r'\((\d+),\s*\'(\d{4}-\d{2}-\d{2})\''
    matches = re.findall(insert_pattern, content)
    
    for match in matches:
        old_id = int(match[0])
        date = match[1]
        id_date_map[old_id] = date
    
    logger.info(f"Extracted {len(id_date_map)} ID-date pairs from original data")
    return id_date_map

def connect_to_database():
    """Connect to PostgreSQL database."""
    
    # Try to get production database URL
    db_url = os.getenv('NEON_DATABASE_URL')
    if not db_url:
        # Check for other possible env variables
        db_url = os.getenv('DATABASE_URL')
    
    if not db_url or 'sqlite' in db_url:
        logger.error("Production PostgreSQL database URL not found!")
        logger.info("Please set NEON_DATABASE_URL in your environment")
        return None, None
    
    logger.info("Connecting to PostgreSQL database...")
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    
    return conn, cursor

def analyze_current_ids(cursor):
    """Analyze current PostgreSQL ID structure."""
    logger.info("Analyzing current PostgreSQL ID structure...")
    
    # Get current ID range
    cursor.execute("SELECT MIN(id), MAX(id), COUNT(*) FROM conflicts")
    min_id, max_id, count = cursor.fetchone()
    logger.info(f"Current PostgreSQL IDs: {min_id}-{max_id}, Total: {count}")
    
    # Check date distribution
    cursor.execute("""
        SELECT incidence_date, COUNT(*) 
        FROM conflicts 
        GROUP BY incidence_date 
        ORDER BY COUNT(*) DESC 
        LIMIT 5
    """)
    date_dist = cursor.fetchall()
    logger.info("Date distribution (top 5):")
    for date, count in date_dist:
        logger.info(f"  {date}: {count}")
    
    # Sample some records to understand the data
    cursor.execute("""
        SELECT id, incidence_date, created_at, 
               incidence_date = created_at::date as is_fake_date
        FROM conflicts 
        ORDER BY id 
        LIMIT 10
    """)
    samples = cursor.fetchall()
    logger.info("Sample records:")
    for sample in samples:
        logger.info(f"  ID: {sample[0]}, Date: {sample[1]}, Created: {sample[2]}, Fake: {sample[3]}")
    
    return min_id, max_id, count

def find_id_mapping_pattern(cursor, original_map):
    """Find how original MariaDB IDs map to PostgreSQL IDs."""
    logger.info("Finding ID mapping pattern...")
    
    # Get current PostgreSQL IDs and some sample data for comparison
    cursor.execute("SELECT id, incidence_date FROM conflicts ORDER BY id LIMIT 100")
    current_records = cursor.fetchall()
    
    # Try to find if there's a simple offset pattern
    original_min_id = min(original_map.keys())
    original_max_id = max(original_map.keys())
    
    cursor.execute("SELECT MIN(id), MAX(id) FROM conflicts")
    current_min_id, current_max_id = cursor.fetchone()
    
    # Calculate potential offset
    offset = current_min_id - original_min_id
    logger.info(f"Potential ID offset: {offset}")
    logger.info(f"Original range: {original_min_id}-{original_max_id}")
    logger.info(f"Current range: {current_min_id}-{current_max_id}")
    
    # Test the offset by checking a few records
    test_matches = 0
    for i, (old_id, date) in enumerate(list(original_map.items())[:20]):
        predicted_new_id = old_id + offset
        cursor.execute("SELECT incidence_date FROM conflicts WHERE id = %s", (predicted_new_id,))
        result = cursor.fetchone()
        if result:
            current_date = result[0]
            # Check if current date is fake (created_at)
            cursor.execute("SELECT created_at::date FROM conflicts WHERE id = %s", (predicted_new_id,))
            created_date = cursor.fetchone()[0]
            if current_date == created_date:
                test_matches += 1
                logger.info(f"  Match found: Old ID {old_id} -> New ID {predicted_new_id}, Original date: {date}")
    
    logger.info(f"Offset test: {test_matches}/20 matches found")
    
    return offset if test_matches > 15 else None

def create_date_fix_script(cursor, original_map, offset):
    """Create SQL script to fix dates with correct ID mapping."""
    logger.info("Creating date fix script...")
    
    script_lines = [
        "-- Fix incidence_date with REAL data from original MariaDB dump",
        "-- This script maps original IDs to current PostgreSQL IDs using offset",
        f"-- Offset pattern: original_id + {offset} = current_id",
        "-- Generated automatically by fix_date_mapping.py",
        "",
        "BEGIN;",
        ""
    ]
    
    updates_count = 0
    
    for old_id, original_date in original_map.items():
        new_id = old_id + offset
        
        # Only add update if the new ID exists and currently has a fake date
        cursor.execute("SELECT incidence_date, created_at::date FROM conflicts WHERE id = %s", (new_id,))
        result = cursor.fetchone()
        
        if result and result[0] == result[1]:  # Current date equals created_at (fake)
            script_lines.append(f"UPDATE conflicts SET incidence_date = '{original_date}' WHERE id = {new_id} AND incidence_date = created_at::date;")
            updates_count += 1
    
    script_lines.extend([
        "",
        f"-- Total updates: {updates_count}",
        "COMMIT;",
        "",
        "-- Verify the fix",
        "SELECT incidence_date, COUNT(*) FROM conflicts GROUP BY incidence_date ORDER BY COUNT(*) DESC LIMIT 10;"
    ])
    
    script_content = "\n".join(script_lines)
    
    # Write script to file
    with open('backend/fix_dates_corrected.sql', 'w') as f:
        f.write(script_content)
    
    logger.info(f"Created fix script with {updates_count} updates")
    logger.info("Script saved to: backend/fix_dates_corrected.sql")
    
    return updates_count

def main():
    """Main execution function."""
    logger.info("Starting date mapping fix...")
    
    # Step 1: Extract original dates
    sql_file = "u503102722_conflictdb (1).sql"
    if not os.path.exists(sql_file):
        logger.error(f"Original SQL file not found: {sql_file}")
        return
    
    original_map = extract_original_dates(sql_file)
    
    # Step 2: Connect to database
    conn, cursor = connect_to_database()
    if not conn:
        logger.error("Failed to connect to database")
        return
    
    try:
        # Step 3: Analyze current state
        analyze_current_ids(cursor)
        
        # Step 4: Find mapping pattern
        offset = find_id_mapping_pattern(cursor, original_map)
        
        if offset is None:
            logger.error("Could not determine ID mapping pattern")
            return
        
        logger.info(f"Found ID offset pattern: {offset}")
        
        # Step 5: Create fix script
        updates_count = create_date_fix_script(cursor, original_map, offset)
        
        logger.info(f"Successfully created fix script with {updates_count} date corrections")
        logger.info("Review the script and then execute: psql $DATABASE_URL < backend/fix_dates_corrected.sql")
        
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
