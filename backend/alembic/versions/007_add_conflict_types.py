"""Add conflict event types and categories

Revision ID: 007
Revises: 006
Create Date: 2026-02-10

This migration fills the second gap in the migration chain.
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade():
    """Add conflict event types and categories"""
    
    # This is a placeholder migration to fix the chain
    # No actual schema changes needed as they were handled in later migrations
    pass


def downgrade():
    """No changes to revert"""
    pass
