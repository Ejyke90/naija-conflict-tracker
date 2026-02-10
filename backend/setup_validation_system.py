#!/usr/bin/env python3
"""
Setup Validation System for Nigeria Conflict Tracker

This script:
1. Creates the validation_summary view in PostgreSQL
2. Sets up required database schema changes
3. Adds sample conflict data for testing
4. Tests the verification endpoints
"""

import os
import sys
import logging
from datetime import datetime, timedelta
import random
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_database_url():
    """Load database URL from environment variables"""
    load_dotenv()
    
    # Try different environment variable names
    database_url = (
        os.getenv('DATABASE_URL') or 
        os.getenv('POSTGRES_URL') or
        os.getenv('POSTGRESQL_URL') or
        'postgresql://localhost:5432/conflict_tracker'
    )
    
    logger.info(f"Using database URL: {database_url.split('@')[0] if '@' in database_url else 'local'}")
    return database_url

def execute_migration(engine):
    """Execute the validation summary view migration"""
    logger.info("Creating validation summary view...")
    
    migration_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'migrations', '004_create_validation_summary_view.sql')
    
    with open(migration_path, 'r') as f:
        migration_sql = f.read()
    
    with engine.connect() as conn:
        try:
            # Execute the migration
            conn.execute(text(migration_sql))
            conn.commit()
            logger.info("✅ Validation summary view created successfully")
        except Exception as e:
            logger.error(f"❌ Failed to create validation summary view: {e}")
            raise

def add_sample_conflict_data(session):
    """Add sample conflict data for testing verification workflow"""
    logger.info("Adding sample conflict data...")
    
    # Sample conflict data
    sample_conflicts = [
        {
            'incidence_date': datetime.now() - timedelta(days=random.randint(1, 30)),
            'state_id': random.randint(1, 36),  # Assuming states have IDs 1-36
            'conflict_type_id': random.randint(1, 5),  # Assuming conflict types have IDs 1-5
            'description': f"Sample conflict incident {random.randint(1000, 9999)}",
            'civilian_death_male': random.randint(0, 10),
            'civilian_death_female': random.randint(0, 5),
            'civilian_death_unknown': random.randint(0, 3),
            'security_death_male': random.randint(0, 5),
            'security_death_female': random.randint(0, 2),
            'security_death_unknown': random.randint(0, 2),
            'kidnapped_male': random.randint(0, 8),
            'kidnapped_female': random.randint(0, 6),
            'kidnapped_unknown': random.randint(0, 4),
            'verified': False,  # All start as unverified for testing
            'created_at': datetime.now() - timedelta(hours=random.randint(1, 72))
        }
        for _ in range(20)  # Create 20 sample conflicts
    ]
    
    try:
        # Check if conflicts table exists and has the right structure
        result = session.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'conflicts'
            ORDER BY ordinal_position
        """))
        columns = [row[0] for row in result.fetchall()]
        logger.info(f"Conflicts table columns: {columns}")
        
        # Insert sample data
        for conflict in sample_conflicts:
            # Build INSERT statement dynamically based on available columns
            available_columns = [col for col in conflict.keys() if col in columns]
            if not available_columns:
                logger.warning("No matching columns found for sample data insertion")
                continue
                
            placeholders = [f":{col}" for col in available_columns]
            insert_sql = f"""
                INSERT INTO conflicts ({', '.join(available_columns)})
                VALUES ({', '.join(placeholders)})
            """
            
            filtered_conflict = {col: conflict[col] for col in available_columns}
            session.execute(text(insert_sql), filtered_conflict)
        
        session.commit()
        logger.info(f"✅ Added {len(sample_conflicts)} sample conflict records")
        
    except Exception as e:
        logger.error(f"❌ Failed to add sample data: {e}")
        session.rollback()
        raise

def test_validation_summary(session):
    """Test the validation summary view"""
    logger.info("Testing validation summary view...")
    
    try:
        result = session.execute(text("SELECT * FROM validation_summary")).first()
        
        if result:
            logger.info("✅ Validation summary view working:")
            logger.info(f"   Pending count: {result[0]}")
            logger.info(f"   Is urgent: {result[1]}")
            logger.info(f"   High priority count: {result[2]}")
            logger.info(f"   Last validation: {result[3]}")
            logger.info(f"   Total verified: {result[4]}")
            logger.info(f"   Oldest pending: {result[5]}")
        else:
            logger.warning("⚠️ Validation summary view returned no data")
            
    except Exception as e:
        logger.error(f"❌ Failed to test validation summary: {e}")
        raise

def test_pending_conflicts_query(session):
    """Test the pending conflicts query used by the API"""
    logger.info("Testing pending conflicts query...")
    
    try:
        query = text("""
            SELECT 
                c.id, 
                c.incidence_date, 
                ct.name as conflict_type,
                c.description,
                c.state_id,
                s.name as state_name,
                (c.civilian_death_male + c.civilian_death_female + c.civilian_death_unknown +
                 c.security_death_male + c.security_death_female + c.security_death_unknown) as total_deaths,
                (c.kidnapped_male + c.kidnapped_female + c.kidnapped_unknown) as total_kidnapped,
                c.created_at
            FROM conflicts c
            LEFT JOIN conflict_types ct ON c.conflict_type_id = ct.id
            LEFT JOIN states s ON c.state_id = s.id
            WHERE c.verified = false
            ORDER BY (total_deaths + total_kidnapped) DESC, c.created_at ASC
            LIMIT 20
        """)
        
        result = session.execute(query).fetchall()
        logger.info(f"✅ Found {len(result)} pending conflicts for review")
        
        # Show first few examples
        for i, row in enumerate(result[:3]):
            logger.info(f"   {i+1}. ID: {row.id}, Deaths: {row.total_deaths}, Kidnapped: {row.total_kidnapped}")
            
    except Exception as e:
        logger.error(f"❌ Failed to test pending conflicts query: {e}")
        # Don't raise here - this might fail due to missing reference tables

def main():
    """Main setup function"""
    logger.info("🚀 Starting Validation System Setup")
    
    try:
        # Load database configuration
        database_url = load_database_url()
        
        # Create database engine
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = SessionLocal()
        
        # Step 1: Execute migration
        execute_migration(engine)
        
        # Step 2: Add sample data
        add_sample_conflict_data(session)
        
        # Step 3: Test validation summary
        test_validation_summary(session)
        
        # Step 4: Test pending conflicts query
        test_pending_conflicts_query(session)
        
        logger.info("🎉 Validation system setup completed successfully!")
        logger.info("📊 Next steps:")
        logger.info("   1. Start the backend server: python -m uvicorn app.main:app --reload")
        logger.info("   2. Test the endpoints: ./test_verification_endpoints.sh")
        logger.info("   3. Access the frontend: http://localhost:3000/dashboard/review")
        
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        sys.exit(1)
    finally:
        if 'session' in locals():
            session.close()

if __name__ == "__main__":
    main()
