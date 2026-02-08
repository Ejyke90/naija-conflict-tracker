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
    # Replace backticks with double quotes
    stmt = stmt.replace('`', '"')

    # Remove ENGINE/COLLATE suffix if accidentally included (defensive)
    # Not expected in INSERT, but keep safe
    stmt = stmt.replace('ENGINE=InnoDB', '')

    # Add ON CONFLICT DO NOTHING to make reruns idempotent
    if stmt.strip().upper().startswith('INSERT INTO'):
        # Ensure terminating semicolon exists once
        stmt = stmt.rstrip().rstrip(';')
        stmt = f"{stmt} ON CONFLICT DO NOTHING;"
    return stmt


def load_dump(dump_path: str):
    """Yield converted INSERT statements from dump file."""
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
                    yield convert_insert_statement(stmt)
        # Safety: flush remaining
        if buffer:
            stmt = ''.join(buffer).strip()
            if stmt.upper().startswith('INSERT INTO'):
                yield convert_insert_statement(stmt)


def reset_sequences(session):
    """Reset sequences to MAX(id) for key tables."""
    tables = [
        ('actors', 'id'),
        ('conflict_types', 'id'),
        ('countries', 'id'),
        ('regions', 'id'),
        ('states', 'id'),
        ('lgas', 'id'),
        ('conflicts', 'id'),
        ('users', 'id'),
        ('personal_access_tokens', 'id'),
    ]
    for table, col in tables:
        seq_name = f"{table}_{col}_seq"
        session.execute(text(
            f"SELECT setval('{seq_name}', COALESCE(MAX({col}), 1)) FROM {table};"
        ))
    session.commit()


def main():
    parser = argparse.ArgumentParser(description='Load MariaDB dump data into PostgreSQL')
    parser.add_argument('--dump-file', required=True, help='Path to MariaDB SQL dump (e.g., u503102722_conflictdb.sql)')
    parser.add_argument('--db-url', help='PostgreSQL connection URL (default env: NEON_DATABASE_URL or DATABASE_URL)')
    args = parser.parse_args()

    db_url = args.db_url or os.getenv('NEON_DATABASE_URL') or os.getenv('DATABASE_URL')
    if not db_url:
        logger.error('No database URL provided. Use --db-url or set NEON_DATABASE_URL/DATABASE_URL.')
        sys.exit(1)

    engine = create_engine(db_url, pool_pre_ping=True)
    SessionLocal = sessionmaker(bind=engine)

    statements = list(load_dump(args.dump_file))
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
