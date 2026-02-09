"""Add performance indexes for conflicts queries

Revision ID: 010_add_conflict_indexes
Revises: 009_add_conflicts_table
Create Date: 2026-02-09

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by alembic.
revision = '010_add_conflict_indexes'
down_revision = '009_add_conflicts_table'
branch_labels = None
depends_on = None


def upgrade():
    # Additional performance indexes for dashboard queries
    
    # Index for seasonal analysis (month extraction queries)
    op.create_index(
        'ix_conflicts_state_incidence_for_seasonal',
        'conflicts',
        ['state_id', 'incidence_date'],
        postgresql_where=sa.text('verified = true')
    )
    
    # Index for casualty aggregations (sum queries)
    op.create_index(
        'ix_conflicts_casualty_aggregation',
        'conflicts',
        ['state_id', 'incidence_date'],
        postgresql_where=sa.text('(civilian_death_male + civilian_death_female + civilian_death_unknown + security_death_male + security_death_female + security_death_unknown) > 0')
    )
    
    # Index for date range queries (common in time-series)
    op.create_index(
        'ix_conflicts_state_date_range',
        'conflicts',
        ['state_id', 'incidence_date'],
        postgresql_where=sa.text('verified = true')
    )
    
    # Index for multi-state comparisons (used in state comparison chart)
    op.create_index(
        'ix_conflicts_multiple_states',
        'conflicts',
        ['state_id', 'incidence_date', 'verified'],
        postgresql_where=sa.text('incidence_date >= CURRENT_DATE - INTERVAL \'12 months\'')
    )
    
    # Index for LGA-level analysis
    op.create_index(
        'ix_conflicts_lga_date',
        'conflicts',
        ['lga_id', 'incidence_date']
    )
    
    # Index for actor analysis (who was involved)
    op.create_index(
        'ix_conflict_actors_state_analysis',
        'conflict_actors',
        ['actor_id', 'is_primary']
    )
    
    # Covering index for common select patterns
    op.create_index(
        'ix_conflicts_covering_state_trends',
        'conflicts',
        ['state_id', 'incidence_date', 'conflict_type_id', 'civilian_death_male', 'civilian_death_female', 'civilian_death_unknown', 'security_death_male', 'security_death_female', 'security_death_unknown'],
        postgresql_where=sa.text('verified = true')
    )


def downgrade():
    op.drop_index('ix_conflicts_covering_state_trends', table_name='conflicts')
    op.drop_index('ix_conflict_actors_state_analysis', table_name='conflict_actors')
    op.drop_index('ix_conflicts_lga_date', table_name='conflicts')
    op.drop_index('ix_conflicts_multiple_states', table_name='conflicts')
    op.drop_index('ix_conflicts_state_date_range', table_name='conflicts')
    op.drop_index('ix_conflicts_casualty_aggregation', table_name='conflicts')
    op.drop_index('ix_conflicts_state_incidence_for_seasonal', table_name='conflicts')
