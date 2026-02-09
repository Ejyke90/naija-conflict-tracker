"""Add reference tables for conflicts schema

Revision ID: 007
Revises: 006
Create Date: 2026-02-09

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade():
    # Create countries table
    op.create_table(
        'countries',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('iso_code', sa.String(length=3), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('iso_code')
    )
    op.create_index('ix_countries_name', 'countries', ['name'])
    
    # Create regions table  
    op.create_table(
        'regions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('country_id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['country_id'], ['countries.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('name')
    )
    op.create_index('ix_regions_name', 'regions', ['name'])
    op.create_index('ix_regions_country_id', 'regions', ['country_id'])
    
    # Create conflict_types table
    op.create_table(
        'conflict_types',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index('ix_conflict_types_name', 'conflict_types', ['name'])
    op.create_index('ix_conflict_types_active', 'conflict_types', ['active'])
    
    # Create actors table
    op.create_table(
        'actors',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('actor_type', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index('ix_actors_name', 'actors', ['name'])
    op.create_index('ix_actors_actor_type', 'actors', ['actor_type'])
    
    # Insert default data
    connection = op.get_bind()
    
    # Insert Nigeria as country
    connection.execute(sa.text("""
        INSERT INTO countries (id, name, iso_code) 
        VALUES (gen_random_uuid(), 'Nigeria', 'NGA')
    """))
    
    # Get Nigeria ID for regions
    nigeria_result = connection.execute(sa.text("""
        SELECT id FROM countries WHERE iso_code = 'NGA'
    """)).fetchone()
    
    if nigeria_result:
        nigeria_id = str(nigeria_result[0])
        
        # Insert default regions (6 geopolitical zones)
        regions = [
            'North Central', 'North East', 'North West',
            'South East', 'South South', 'South West'
        ]
        
        for region in regions:
            connection.execute(sa.text("""
                INSERT INTO regions (id, name, country_id, description)
                VALUES (gen_random_uuid(), :name, :country_id, :description)
            """), {
                'name': region,
                'country_id': nigeria_id,
                'description': f'{region} Region'
            })
    
    # Insert default conflict types
    conflict_types = [
        'Violence against civilians',
        'Battles',
        'Explosions/Remote violence',
        'Protests',
        'Riots',
        'Strategic developments',
        'Armed clash',
        'Armed violence',
        'Communal clash',
        'Ethnic clash',
        'Religious clash',
        'Cultism',
        'Kidnapping',
        'Terrorism',
        'Unknown'
    ]
    
    for conflict_type in conflict_types:
        connection.execute(sa.text("""
            INSERT INTO conflict_types (id, name, description, active)
            VALUES (gen_random_uuid(), :name, :description, true)
        """), {
            'name': conflict_type,
            'description': f'{conflict_type} conflict'
        })
    
    # Insert default actor types
    actor_types = [
        ('State Forces', 'Government military and police'),
        ('Armed Group', 'Non-state armed organizations'),
        ('Armed Militia', 'Community-based armed groups'),
        ('Religious Group', 'Groups organized along religious lines'),
        ('Ethnic Group', 'Groups organized along ethnic lines'),
        ('Criminal Group', 'Organized crime and criminal networks'),
        ('Unknown Actors', 'Unidentified or unclassified actors')
    ]
    
    for actor_type, description in actor_types:
        connection.execute(sa.text("""
            INSERT INTO actors (id, name, actor_type, description)
            VALUES (gen_random_uuid(), :name, :actor_type, :description)
        """), {
            'name': actor_type,
            'actor_type': actor_type,
            'description': description
        })
    
    connection.commit()


def downgrade():
    op.drop_table('actors')
    op.drop_table('conflict_types')
    op.drop_table('regions')
    op.drop_table('countries')
