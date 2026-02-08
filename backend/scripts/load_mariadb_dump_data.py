#!/usr/bin/env python3
"""
Load MariaDB dump data (INSERT statements) into PostgreSQL (Neon DB).

- Reads the original MariaDB SQL dump (u503102722_conflictdb.sql)
- Extracts INSERT statements
- Converts backticks to PostgreSQL-friendly identifiers
- Adds ON CONFLICT DO NOTHING to avoid duplicate key errors
- Executes against the target PostgreSQL database

Usage:
    python load_mariadb_dump_data.py --dump-file database/migrations/u503102722_conflictdb.sql \
        --db-url $NEON_DATABASE_URL

Notes:
- Assumes the PostgreSQL schema is already created via neondb_postgres_schema.sql
- Safe to re-run; duplicate rows will be skipped via ON CONFLICT DO NOTHING
- After load, sequences are reset to MAX(id) for all tables with serial keys
"""

import argparse
import logging
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('load_data.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)



def convert_insert_statement(stmt: str) -> str:
    """Convert a MariaDB INSERT statement to PostgreSQL-friendly syntax."""
    import re
    
    # Replace backticks with double quotes
    stmt = stmt.replace('`', '"')

    # MariaDB dumps escape single quotes as \\', which is not valid when
    # standard_conforming_strings is ON (default in Postgres). Normalize to
    # doubled quotes so strings like Jama\'atu become Jama''atu.
    stmt = stmt.replace("\\'", "''")

    # Remove ENGINE/COLLATE suffix if accidentally included (defensive)
    stmt = stmt.replace('ENGINE=InnoDB', '')

    # Fix table-specific column name mismatches: MariaDB "title" → PostgreSQL "name"
    table_column_mapping = {
        '"countries"': ('"title"', '"name"'),
        '"regions"': ('"title"', '"name"'),
        '"states"': ('"title"', '"name"'),
        '"lgas"': ('"title"', '"name"'),
    }
    
    for table_quote, (old_col, new_col) in table_column_mapping.items():
        if f'INSERT INTO {table_quote}' in stmt:
            stmt = stmt.replace(old_col, new_col)
    
    # For lgas table: drop region_id column entirely
    # For lgas table: drop region_id column and add state_name placeholder
    if 'INSERT INTO "lgas"' in stmt:
        # Original dump: (id, name, state_id, region_id, created_at, updated_at)
        # Target schema: (id, name, state_name, state_id, created_at, updated_at)
        
        # Step 1: Update column list
        # Remove region_id, add state_name after name
        stmt = re.sub(r',\s*"region_id"', '', stmt)
        stmt = re.sub(r'(INSERT INTO "lgas" \([^)]*"name")', r'\1, "state_name"', stmt)
        
        # Step 2: Transform VALUES tuples
        # Old: (id, name, state_id, region_id, created_at, updated_at)
        # New: (id, name, NULL_for_state_name, state_id, created_at, updated_at)
        # Pattern: (digits, 'string', digits, digits, timestamp, timestamp)
        # Replace: (digits, 'string', NULL, digits, timestamp, timestamp)
        stmt = re.sub(
            r"(\(\d+,\s*'[^']*'),\s*(\d+),\s*(\d+),",
            r"\1, NULL, \2,",
            stmt
        )
        
        stmt = stmt.rstrip().rstrip(';') + ' ON CONFLICT DO NOTHING;'
    else:
        # Add ON CONFLICT DO NOTHING to make reruns idempotent
        if stmt.strip().upper().startswith('INSERT INTO'):
            stmt = stmt.rstrip().rstrip(';')
            stmt = f"{stmt} ON CONFLICT DO NOTHING;"
    
    return stmt


def load_dump(dump_path: str, allowed_tables=None):
    """Yield converted INSERT statements from dump file, optionally filtered by table list."""
    # Default: load only reference tables (safe to rerun), skip heavy/conflicts data
    if allowed_tables is None:
        # Safe default: load only reference tables that match target schema
        allowed_tables = {
            'actors',
            'conflict_types',
            'regions',
            'states',
            'lgas'
        }
    with open(dump_path, 'r', encoding='utf-8') as f:
        buffer = []
        for line in f:
            # Skip comments and empty lines
            if line.startswith('--') or line.startswith('/*') or line.strip() == '':
                continue
            buffer.append(line)
            # Statements end with semicolon
            if line.strip().endswith(';'):
                stmt = ''.join(buffer).strip()
                buffer = []
                if stmt.upper().startswith('INSERT INTO'):
                    # Handle backtick or plain identifiers
                    table_name = None
                    if '`' in stmt:
                        parts = stmt.split('`')
                        if len(parts) > 1:
                            table_name = parts[1]
                    else:
                        tokens = stmt.split()
                        if len(tokens) > 2:
                            table_name = tokens[2].strip('"')

                    # Skip any table not explicitly allowed
                    if table_name and allowed_tables and table_name not in allowed_tables:
                        continue

                    yield convert_insert_statement(stmt)
        # Safety: flush remaining
        if buffer:
            stmt = ''.join(buffer).strip()
            if stmt.upper().startswith('INSERT INTO'):
                table_name = None
                if '`' in stmt:
                    parts = stmt.split('`')
                    if len(parts) > 1:
                        table_name = parts[1]
                else:
                    tokens = stmt.split()
                    if len(tokens) > 2:
                        table_name = tokens[2].strip('"')
                if table_name and allowed_tables and table_name not in allowed_tables:
                    return
                yield convert_insert_statement(stmt)


def reset_sequences(session):
    """Reset sequences to MAX(id) for key tables."""
    tables = [
        ('actors', 'id'),
        ('conflict_types', 'id'),
        ('regions', 'id'),
        ('states', 'id'),
        ('lgas', 'id'),
        ('conflicts', 'id'),
    ]
    for table, col in tables:
        try:
            seq_name = f"{table}_{col}_seq"
            session.execute(text(
                f"SELECT setval('{seq_name}', COALESCE(MAX({col}), 1)) FROM {table};"
            ))
        except Exception as e:
            logger.warning(f"Could not reset sequence {seq_name}: {e}")
    session.commit()


def main():
    parser = argparse.ArgumentParser(description='Load MariaDB dump data into PostgreSQL')
    parser.add_argument('--dump-file', required=True, help='Path to MariaDB SQL dump (e.g., u503102722_conflictdb.sql)')
    parser.add_argument('--db-url', help='PostgreSQL connection URL (default env: NEON_DATABASE_URL or DATABASE_URL)')
    parser.add_argument('--tables', nargs='*', default=None, help='Optional list of tables to load (e.g., actors conflict_types regions states lgas)')
    args = parser.parse_args()

    db_url = args.db_url or os.getenv('NEON_DATABASE_URL') or os.getenv('DATABASE_URL')
    if not db_url:
        logger.error('No database URL provided. Use --db-url or set NEON_DATABASE_URL/DATABASE_URL.')
        sys.exit(1)

    engine = create_engine(db_url, pool_pre_ping=True)
    SessionLocal = sessionmaker(bind=engine)

    statements = list(load_dump(args.dump_file, allowed_tables=args.tables))
    logger.info(f"Found {len(statements)} INSERT statements to execute.")

    with SessionLocal() as session:
        try:
            for idx, stmt in enumerate(statements, 1):
                session.execute(text(stmt))
                if idx % 50 == 0:
                    session.commit()
                    logger.info(f"Committed {idx} statements...")
            session.commit()
            logger.info("All INSERT statements executed.")

            # After loading lgas, populate state_name from states table
            session.execute(text("""
                UPDATE lgas l
                SET state_name = s.name
                FROM states s
                WHERE l.state_id = s.id AND (l.state_name IS NULL OR l.state_name = '');
            """))
            session.commit()
            logger.info("Populated state_name for all LGAs.")

            # Reset sequences
            reset_sequences(session)
            logger.info("Sequences reset to MAX(id).")
        except Exception as e:
            session.rollback()
            logger.error(f"Error loading data: {e}")
            sys.exit(1)

    logger.info("✅ Data load complete.")


if __name__ == '__main__':
    main()
