"""add data quality metrics table for real-time monitoring

Revision ID: 002_data_quality_metrics
Revises: 001_auth_tables
Create Date: 2024-01-20 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002_data_quality_metrics'
down_revision: Union[str, None] = '001_auth_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create data_quality_metrics table
    op.create_table(
        'data_quality_metrics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('geocoding_attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('geocoding_successes', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('geocoding_success_rate', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('validation_attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('validation_passes', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('validation_pass_rate', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('metric_type', sa.String(50), nullable=False, server_default='aggregate'),
        sa.Column('source', sa.String(255), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.CheckConstraint("status IN ('pending', 'healthy', 'warning', 'error')", name='valid_metric_status'),
        sa.CheckConstraint("metric_type IN ('aggregate', 'source-specific', 'hourly')", name='valid_metric_type')
    )
    
    # Create indexes on data_quality_metrics table
    # Index on timestamp (descending) for fast recent metric queries
    op.create_index(
        'ix_data_quality_metrics_timestamp_desc',
        'data_quality_metrics',
        [sa.text('timestamp DESC')]
    )
    
    # Index on source for source-specific metric queries
    op.create_index(
        'ix_data_quality_metrics_source',
        'data_quality_metrics',
        ['source']
    )
    
    # Index on metric_type for filtering by metric type
    op.create_index(
        'ix_data_quality_metrics_metric_type',
        'data_quality_metrics',
        ['metric_type']
    )
    
    # Composite index on recent aggregate metrics (common query pattern)
    op.create_index(
        'ix_data_quality_metrics_recent',
        'data_quality_metrics',
        [sa.text('metric_type'), sa.text('timestamp DESC')],
        where=sa.text("metric_type = 'aggregate'")
    )


def downgrade() -> None:
    # Drop all indexes
    op.drop_index('ix_data_quality_metrics_recent')
    op.drop_index('ix_data_quality_metrics_metric_type')
    op.drop_index('ix_data_quality_metrics_source')
    op.drop_index('ix_data_quality_metrics_timestamp_desc')
    
    # Drop table
    op.drop_table('data_quality_metrics')
