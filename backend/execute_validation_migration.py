#!/usr/bin/env python3
"""
Execute Validation Summary Migration

Simple script to create the validation summary view and required schema
"""

import os
import sys
import logging
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_database_url():
    """Load database URL from environment variables"""
    load_dotenv()
    
    database_url = (
        os.getenv('DATABASE_URL') or 
        os.getenv('POSTGRES_URL') or
        os.getenv('POSTGRESQL_URL') or
        'postgresql://localhost:5432/conflict_tracker'
    )
    
    logger.info(f"Using database URL: {database_url.split('@')[0] if '@' in database_url else 'local'}")
    return database_url

def main():
    """Execute the migration"""
    logger.info("🚀 Executing Validation Summary Migration")
    
    try:
        # Load database configuration
        database_url = load_database_url()
        
        # Create database engine
        engine = create_engine(database_url)
        
        # Read and execute the migration
        migration_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'migrations', '004_create_validation_summary_view_fixed.sql')
        
        with open(migration_path, 'r') as f:
            migration_sql = f.read()
        
        with engine.connect() as conn:
            # Execute the migration
            conn.execute(text(migration_sql))
            conn.commit()
            logger.info("✅ Validation summary view migration completed successfully")
        
        # Test the view
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM validation_summary")).first()
            
            if result:
                logger.info("✅ Validation summary view working:")
                logger.info(f"   Pending count: {result[0]}")
                logger.info(f"   Is urgent: {result[1]}")
                logger.info(f"   High priority count: {result[2]}")
                logger.info(f"   Total verified: {result[4]}")
            else:
                logger.info("ℹ️ Validation summary view created but no data available")
        
        logger.info("🎉 Migration completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
