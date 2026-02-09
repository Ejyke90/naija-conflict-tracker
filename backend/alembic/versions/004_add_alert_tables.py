"""add alert tables

Revision ID: 004
Revises: 003
Create Date: 2026-02-08

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    # Create alert_events table
    op.create_table(
        'alert_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conflict_event_id', sa.Integer(), nullable=False),
        sa.Column('alert_type', sa.String(50), nullable=False),
        sa.Column('risk_score', sa.Float(), nullable=False),
        sa.Column('priority', sa.String(20), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='ACTIVE'),
        sa.Column('location', sa.String(255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('acknowledged_at', sa.DateTime(), nullable=True),
        sa.Column('acknowledged_by', sa.Integer(), nullable=True),
        sa.Column('acknowledgment_notes', sa.Text(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_by', sa.Integer(), nullable=True),
        sa.Column('resolution_notes', sa.Text(), nullable=True),
        sa.Column('resolution_actions', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('dedup_key', sa.String(64), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for alert_events
    op.create_index('ix_alert_events_status', 'alert_events', ['status'])
    op.create_index('ix_alert_events_created_at', 'alert_events', ['created_at'])
    op.create_index('ix_alert_events_risk_score', 'alert_events', ['risk_score'])
    op.create_index('ix_alert_events_conflict_event_id', 'alert_events', ['conflict_event_id'])
    op.create_index('ix_alert_events_dedup_key', 'alert_events', ['dedup_key'], unique=True)
    
    # Create foreign keys
    op.create_foreign_key(
        'fk_alert_events_conflict_event',
        'alert_events', 'conflict_events_new',
        ['conflict_event_id'], ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'fk_alert_events_acknowledged_by',
        'alert_events', 'users',
        ['acknowledged_by'], ['id'],
        ondelete='SET NULL'
    )
    op.create_foreign_key(
        'fk_alert_events_resolved_by',
        'alert_events', 'users',
        ['resolved_by'], ['id'],
        ondelete='SET NULL'
    )
    
    # Create alert_read_status table
    op.create_table(
        'alert_read_status',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('alert_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('read_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for alert_read_status
    op.create_index('ix_alert_read_status_alert_id', 'alert_read_status', ['alert_id'])
    op.create_index('ix_alert_read_status_user_id', 'alert_read_status', ['user_id'])
    op.create_index(
        'ix_alert_read_status_unique',
        'alert_read_status',
        ['alert_id', 'user_id'],
        unique=True
    )
    
    # Create foreign keys
    op.create_foreign_key(
        'fk_alert_read_status_alert',
        'alert_read_status', 'alert_events',
        ['alert_id'], ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'fk_alert_read_status_user',
        'alert_read_status', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade():
    # Drop alert_read_status table
    op.drop_table('alert_read_status')
    
    # Drop alert_events table
    op.drop_table('alert_events')
