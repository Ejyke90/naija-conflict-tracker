"""Fix migration conflict between locations and reference tables

Revision ID: 011_fix_migration_conflict
Revises: 005
Create Date: 2026-02-09

This migration consolidates the conflicting 006 and 007 migrations
and resolves the dependency issues.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from geoalchemy2 import Geography

# revision identifiers, used by alembic.
revision = '011'
down_revision = '010'
branch_labels = None
depends_on = None

# Nigerian states and their capitals
NIGERIAN_STATES = {
    'Abia': 'Umuahia', 'Adamawa': 'Yola', 'Akwa Ibom': 'Uyo', 'Anambra': 'Awka',
    'Bauchi': 'Bauchi', 'Bayelsa': 'Yenagoa', 'Benue': 'Makurdi', 'Borno': 'Maiduguri',
    'Cross River': 'Calabar', 'Delta': 'Asaba', 'Ebonyi': 'Abakaliki', 'Edo': 'Benin City',
    'Ekiti': 'Ado Ekiti', 'Enugu': 'Enugu', 'Gombe': 'Gombe', 'Imo': 'Owerri',
    'Jigawa': 'Dutse', 'Kaduna': 'Kaduna', 'Kano': 'Kano', 'Katsina': 'Katsina',
    'Kebbi': 'Birnin Kebbi', 'Kogi': 'Lokoja', 'Kwara': 'Ilorin', 'Lagos': 'Ikeja',
    'Nasarawa': 'Karu', 'Niger': 'Minna', 'Ogun': 'Abeokuta', 'Ondo': 'Akure',
    'Osun': 'Osogbo', 'Oyo': 'Ibadan', 'Plateau': 'Jos', 'Rivers': 'Port Harcourt',
    'Sokoto': 'Sokoto', 'Taraba': 'Jalingo', 'Yobe': 'Damaturu', 'Zamfara': 'Gusau',
    'FCT': 'Abuja'
}

# Some key LGAs by state
NIGERIAN_LGAS = {
    'Abia': ['Aba North', 'Aba South', 'Arochukwu', 'Bende', 'Ikwuano', 'Isiala Ngwa North'],
    'Adamawa': ['Demsa', 'Fufure', 'Guyuk', 'Hong', 'Jimeta', 'Maiduguri', 'Mayobelwa'],
    'Akwa Ibom': ['Abak', 'Afilang', 'Etim Ekpo', 'Eket', 'Etinan', 'Ikot Abasi'],
    'Anambra': ['Aguata', 'Anambra East', 'Anambra West', 'Anaocha', 'Awka North'],
    'Borno': ['Abadam', 'Askira Uba', 'Bama', 'Bayo', 'Biu', 'Chibok'],
    'Kaduna': ['Birnin Gwari', 'Chikun', 'Giwa', 'Jaba', 'Jema\'a', 'Kachia'],
    'Kano': ['Ajinkyire', 'Albasu', 'Bagwaji', 'Bebeji', 'Bichi', 'Bunkure'],
    'Lagos': ['Agege', 'Ajeromi-Ifelodun', 'Alimosho', 'Amuwo-Odofin', 'Apapa'],
    'Oyo': ['Afijio', 'Egbeda', 'Ibadan North', 'Ibadan South East', 'Ibarapa Central'],
    'Rivers': ['Abua/Odual', 'Ahoada East', 'Ahoada West', 'Akuku-Toru', 'Andoni'],
}


def upgrade():
    # Create locations table with PostGIS support
    op.create_table(
        'locations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(length=20), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('boundary', Geography('MULTIPOLYGON, 4326'), nullable=True),
        sa.Column('population', sa.Integer(), nullable=True),
        sa.Column('poverty_rate', sa.Float(), nullable=True),
        sa.Column('unemployment_rate', sa.Float(), nullable=True),
        sa.Column('extra_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['parent_id'], ['locations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add indexes for performance
    op.create_index('ix_locations_type', 'locations', ['type'])
    op.create_index('ix_locations_name', 'locations', ['name'])
    op.create_index('ix_locations_parent_id', 'locations', ['parent_id'])
    
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
    
    # Insert Nigerian states
    for state_name in sorted(NIGERIAN_STATES.keys()):
        connection.execute(sa.text("""
            INSERT INTO locations (type, name) 
            VALUES (:type, :name)
        """), {'type': 'state', 'name': state_name})
    
    # Get state IDs for LGA insertion
    connection.commit()
    
    # Insert some key LGAs
    for state_name, lgas in NIGERIAN_LGAS.items():
        # Get state ID
        result = connection.execute(sa.text("""
            SELECT id FROM locations WHERE type = 'state' AND name = :name
        """), {'name': state_name}).fetchone()
        
        if result:
            state_id = result[0]
            for lga_name in lgas:
                connection.execute(sa.text("""
                    INSERT INTO locations (type, name, parent_id) 
                    VALUES (:type, :name, :parent_id)
                """), {'type': 'lga', 'name': lga_name, 'parent_id': state_id})
    
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
    # Drop reference tables
    op.drop_table('actors')
    op.drop_table('conflict_types')
    op.drop_table('regions')
    op.drop_table('countries')
    
    # Drop locations table and indexes
    op.drop_index('ix_locations_parent_id', table_name='locations')
    op.drop_index('ix_locations_name', table_name='locations')
    op.drop_index('ix_locations_type', table_name='locations')
    op.drop_table('locations')
