"""Add performance indexes for dashboard queries

Revision ID: 004_performance_indexes
Revises: 003
Create Date: 2026-02-09

Indexes added:
- idx_conflicts_incidence_date (for time-range queries)
- idx_conflicts_state_id (for state filtering)
- idx_conflicts_lga_id (for LGA aggregations)
- idx_conflicts_conflict_type_id (for archetype queries)
- idx_conflicts_composite_state_date (composite index for common query pattern)
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic
revision = '004_performance_indexes'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    """Add indexes to improve query performance"""
    
    # Individual indexes
    op.create_index(
        'idx_conflicts_incidence_date',
        'conflicts',
        ['incidence_date'],
        postgresql_using='btree'
    )
    
    op.create_index(
        'idx_conflicts_state_id',
        'conflicts',
        ['state_id'],
        postgresql_using='btree'
    )
    
    op.create_index(
        'idx_conflicts_lga_id',
        'conflicts',
        ['lga_id'],
        postgresql_using='btree'
    )
    
    op.create_index(
        'idx_conflicts_conflict_type_id',
        'conflicts',
        ['conflict_type_id'],
        postgresql_using='btree'
    )
    
    # Composite index for most common query pattern (state + date range)
    op.create_index(
        'idx_conflicts_composite_state_date',
        'conflicts',
        ['state_id', 'incidence_date'],
        postgresql_using='btree'
    )
    
    # Index for LGA + date queries (hotspots)
    op.create_index(
        'idx_conflicts_composite_lga_date',
        'conflicts',
        ['lga_id', 'incidence_date'],
        postgresql_using='btree'
    )


def downgrade():
    """Remove all performance indexes"""
    op.drop_index('idx_conflicts_composite_lga_date', table_name='conflicts')
    op.drop_index('idx_conflicts_composite_state_date', table_name='conflicts')
    op.drop_index('idx_conflicts_conflict_type_id', table_name='conflicts')
    op.drop_index('idx_conflicts_lga_id', table_name='conflicts')
    op.drop_index('idx_conflicts_state_id', table_name='conflicts')
    op.drop_index('idx_conflicts_incidence_date', table_name='conflicts')
