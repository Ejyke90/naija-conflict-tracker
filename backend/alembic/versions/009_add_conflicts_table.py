"""Add conflicts and conflict_actors tables for core conflict data

Revision ID: 009
Revises: 008
Create Date: 2026-02-09

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by alembic.
revision = '009'
down_revision = '008'
branch_labels = None
depends_on = None


def upgrade():
    # Create conflicts table - main conflict events
    op.create_table(
        'conflicts',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('incidence_date', sa.Date(), nullable=False),
        sa.Column('state_id', sa.UUID(), nullable=False),
        sa.Column('lga_id', sa.UUID(), nullable=True),
        sa.Column('conflict_type_id', sa.UUID(), nullable=True),
        sa.Column('location_description', sa.String(length=500), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        # Civilian casualties
        sa.Column('civilian_death_male', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('civilian_death_female', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('civilian_death_unknown', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('civilian_injured', sa.Integer(), nullable=False, server_default='0'),
        # Security casualties
        sa.Column('security_death_male', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('security_death_female', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('security_death_unknown', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('security_injured', sa.Integer(), nullable=False, server_default='0'),
        # Displacement and property
        sa.Column('displaced_persons', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('property_destroyed', sa.Integer(), nullable=False, server_default='0'),
        # Source tracking
        sa.Column('source', sa.String(length=100), nullable=True),
        sa.Column('source_url', sa.Text(), nullable=True),
        sa.Column('verified', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('verified_at', sa.DateTime(), nullable=True),
        sa.Column('verified_by', sa.String(length=255), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        # Metadata
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['state_id'], ['states.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['lga_id'], ['lgas.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['conflict_type_id'], ['conflict_types.id'], ondelete='SET NULL')
    )
    
    # Indexes for common queries (critical for dashboard)
    op.create_index('ix_conflicts_state_id_date', 'conflicts', ['state_id', 'incidence_date'], order_by=['state_id', 'incidence_date DESC'])
    op.create_index('ix_conflicts_incidence_date', 'conflicts', ['incidence_date'])
    op.create_index('ix_conflicts_state_id', 'conflicts', ['state_id'])
    op.create_index('ix_conflicts_lga_id', 'conflicts', ['lga_id'])
    op.create_index('ix_conflicts_conflict_type_id', 'conflicts', ['conflict_type_id'])
    op.create_index('ix_conflicts_verified', 'conflicts', ['verified'])
    op.create_index('ix_conflicts_source', 'conflicts', ['source'])
    
    # Create junction table for conflict actors (many-to-many)
    op.create_table(
        'conflict_actors',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('conflict_id', sa.UUID(), nullable=False),
        sa.Column('actor_id', sa.UUID(), nullable=False),
        sa.Column('role', sa.String(length=100), nullable=True),
        sa.Column('is_primary', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['conflict_id'], ['conflicts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['actor_id'], ['actors.id'], ondelete='RESTRICT'),
        sa.UniqueConstraint('conflict_id', 'actor_id', name='uc_conflict_actor')
    )
    
    # Indexes for actor queries
    op.create_index('ix_conflict_actors_conflict_id', 'conflict_actors', ['conflict_id'])
    op.create_index('ix_conflict_actors_actor_id', 'conflict_actors', ['actor_id'])
    op.create_index('ix_conflict_actors_is_primary', 'conflict_actors', ['is_primary'])


def downgrade():
    op.drop_table('conflict_actors')
    op.drop_table('conflicts')
