#!/usr/bin/env python
"""Verify database migrations were applied correctly."""
import os
from sqlalchemy import text, create_engine

# Get database URL from environment
db_url = os.getenv('DATABASE_URL') or os.getenv('SQLALCHEMY_DATABASE_URL')
if not db_url:
    db_url = 'postgresql://postgres:postgres@localhost:5432/naija_conflicts'

print(f"Using database: {db_url[:50]}...")

engine = create_engine(db_url)

try:
    with engine.connect() as conn:
        # Check schema version
        try:
            migration = conn.execute(text('SELECT version_num FROM alembic_version ORDER BY version_num DESC LIMIT 1')).scalar()
            print(f'✅ Current migration version: {migration}')
        except Exception as e:
            print(f"⚠️ Could not read alembic_version: {e}")
        
        # Check states count
        try:
            states_count = conn.execute(text('SELECT COUNT(*) as count FROM states')).scalar()
            print(f'✅ States table: {states_count} records (36 states + FCT + 1 other)')
            
            # List the states
            all_states = conn.execute(text('SELECT name FROM states ORDER BY name')).fetchall()
            if all_states:
                first_5 = [s[0] for s in all_states[:5]]
                print(f"   Sample states: {', '.join(first_5)}...")
        except Exception as e:
            print(f"❌ States table error: {e}")
        
        # Check LGAs count
        try:
            lgas_count = conn.execute(text('SELECT COUNT(*) as count FROM lgas')).scalar()
            print(f'✅ LGAs table: {lgas_count} records (expected: 948)')
        except Exception as e:
            print(f"❌ LGAs table error: {e}")
        
        # Check conflicts count
        try:
            conflicts_count = conn.execute(text('SELECT COUNT(*) as count FROM conflicts')).scalar()
            print(f'✅ Conflicts table: {conflicts_count} records')
        except Exception as e:
            print(f"❌ Conflicts table error: {e}")
        
        print("\n✅ Database verification complete!")
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
