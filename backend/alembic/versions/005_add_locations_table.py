"""Add locations table with Nigerian states and LGAs

Revision ID: 005
Revises: 004_add_performance_indexes
Create Date: 2026-02-09

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from geoalchemy2 import Geography

# revision identifiers, used by alembic.
revision = '005'
down_revision = '004_add_performance_indexes'
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
    
    # Get connection for data insertion
    connection = op.get_bind()
    
    # Insert Nigerian states
    state_inserts = []
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
    
    connection.commit()


def downgrade():
    # Drop the locations table and indexes
    op.drop_index('ix_locations_parent_id', table_name='locations')
    op.drop_index('ix_locations_name', table_name='locations')
    op.drop_index('ix_locations_type', table_name='locations')
    op.drop_table('locations')
