#!/usr/bin/env python3
"""
Validation script for conflict_events → conflicts migration.

Checks performed:
1) Table existence
2) Row count parity (old vs new)
3) Casualty totals parity (fatalities, injuries)
4) Foreign key nulls (state_id, lga_id, conflict_type_id)
5) Unmapped items (states, lgas, actors, conflict types)
6) Sample diff (first 5 mismatches by date/state/community)

Usage:
    python validate_migration.py --db-url $NEON_DATABASE_URL
"""

import argparse
import logging
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_tables(session):
    tables = ['conflict_events', 'conflicts']
    missing = []
    for t in tables:
        exists = session.execute(text(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = :t)")
        , {'t': t}).scalar()
        if not exists:
            missing.append(t)
    return missing


def row_counts(session):
    old_count = session.execute(text("SELECT COUNT(*) FROM conflict_events")).scalar()
    new_count = session.execute(text("SELECT COUNT(*) FROM conflicts")).scalar()
    return old_count, new_count


def casualty_totals(session):
    # Old schema totals
    old = session.execute(text(
        "SELECT COALESCE(SUM(fatalities),0) AS fatalities, COALESCE(SUM(injuries),0) AS injuries FROM conflict_events"
    )).mappings().one()

    # New schema totals (deaths = civilian + security)
    new = session.execute(text(
        """
        SELECT 
          COALESCE(SUM(civilian_death_male + civilian_death_female + civilian_death_unknown
                      + security_death_male + security_death_female + security_death_unknown),0) AS fatalities,
          COALESCE(SUM(injured_male + injured_female + injured_unknown),0) AS injuries
        FROM conflicts
        """
    )).mappings().one()
    return old, new


def fk_nulls(session):
    rows = session.execute(text(
        """
        SELECT 
          SUM(CASE WHEN state_id IS NULL THEN 1 ELSE 0 END) AS missing_state,
          SUM(CASE WHEN lga_id IS NULL THEN 1 ELSE 0 END) AS missing_lga,
          SUM(CASE WHEN conflict_type_id IS NULL THEN 1 ELSE 0 END) AS missing_conflict_type
        FROM conflicts
        """
    )).mappings().one()
    return rows


def sample_mismatch(session):
    # Compare by date/state/community text to spot obvious mapping gaps
    sql = text(
        """
        SELECT ce.id AS old_id, ce.event_date, ce.state, ce.lga, ce.location,
               c.state_id, c.lga_id, c.community
        FROM conflict_events ce
        LEFT JOIN conflicts c
          ON c.incidence_date = ce.event_date
         AND LOWER(COALESCE(c.community,'')) = LOWER(COALESCE(ce.location,''))
        WHERE c.id IS NULL
        ORDER BY ce.event_date
        LIMIT 5;
        """
    )
    return [dict(r) for r in session.execute(sql)]


def main():
    parser = argparse.ArgumentParser(description="Validate conflict migration")
    parser.add_argument('--db-url', help='Database URL (defaults to NEON_DATABASE_URL or DATABASE_URL)')
    args = parser.parse_args()

    db_url = args.db_url or os.getenv('NEON_DATABASE_URL') or os.getenv('DATABASE_URL')
    if not db_url:
        logger.error("No database URL provided. Use --db-url or set NEON_DATABASE_URL/DATABASE_URL")
        sys.exit(1)

    engine = create_engine(db_url, pool_pre_ping=True)
    SessionLocal = sessionmaker(bind=engine)

    with SessionLocal() as session:
        missing = check_tables(session)
        if missing:
            logger.error(f"Missing tables: {missing}")
            sys.exit(1)
        logger.info("✅ Both tables exist")

        old_count, new_count = row_counts(session)
        logger.info(f"Old count: {old_count} | New count: {new_count}")

        old_cas, new_cas = casualty_totals(session)
        logger.info(f"Fatalities old/new: {old_cas['fatalities']} / {new_cas['fatalities']}")
        logger.info(f"Injuries old/new: {old_cas['injuries']} / {new_cas['injuries']}")

        fks = fk_nulls(session)
        logger.info(f"Null state_id: {fks['missing_state']}")
        logger.info(f"Null lga_id: {fks['missing_lga']}")
        logger.info(f"Null conflict_type_id: {fks['missing_conflict_type']}")

        mismatches = sample_mismatch(session)
        if mismatches:
            logger.warning("Sample unmapped rows (first 5):")
            for m in mismatches:
                logger.warning(m)
        else:
            logger.info("No obvious mapping mismatches detected in sample.")

        # Basic acceptance checks
        success = True
        if old_count != new_count:
            logger.warning("Row counts differ")
            success = False
        if old_cas['fatalities'] != new_cas['fatalities']:
            logger.warning("Fatalities totals differ")
            success = False
        if old_cas['injuries'] != new_cas['injuries']:
            logger.warning("Injuries totals differ")
            success = False

        if success:
            logger.info("✅ Validation passed")
            sys.exit(0)
        else:
            logger.warning("⚠️ Validation failed")
            sys.exit(1)


if __name__ == '__main__':
    main()
