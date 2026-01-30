"""Add success column to audit_log table

Revision ID: 003
Revises: 002_add_data_quality_metrics
Create Date: 2026-01-30 03:35:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002_add_data_quality_metrics'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add success column to audit_log table."""
    op.add_column('audit_log', sa.Column('success', sa.Boolean(), nullable=False, server_default='true'))
    
    # Create index on success column for filtering failed actions
    op.create_index(op.f('ix_audit_log_success'), 'audit_log', ['success'], unique=False)


def downgrade() -> None:
    """Remove success column from audit_log table."""
    op.drop_index(op.f('ix_audit_log_success'), table_name='audit_log')
    op.drop_column('audit_log', 'success')
