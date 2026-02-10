"""Add states and LGAs tables for Nigerian geography

Revision ID: 008_add_states_and_lgas
Revises: 011_fix_migration_conflict
Create Date: 2026-02-09

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by alembic.
revision = '008'
down_revision = '006'
branch_labels = None
depends_on = None

# All 36 Nigerian states + FCT with their codes
NIGERIAN_STATES = [
    ('Abia', 'AB'), ('Adamawa', 'AD'), ('Akwa Ibom', 'AK'), ('Anambra', 'AN'),
    ('Bauchi', 'BA'), ('Bayelsa', 'BY'), ('Benue', 'BE'), ('Borno', 'BO'),
    ('Cross River', 'CR'), ('Delta', 'DE'), ('Ebonyi', 'EB'), ('Edo', 'ED'),
    ('Ekiti', 'EK'), ('Enugu', 'EN'), ('FCT', 'FC'), ('Gombe', 'GO'),
    ('Imo', 'IM'), ('Jigawa', 'JI'), ('Kaduna', 'KA'), ('Kano', 'KN'),
    ('Katsina', 'KT'), ('Kebbi', 'KE'), ('Kogi', 'KO'), ('Kwara', 'KW'),
    ('Lagos', 'LA'), ('Nasarawa', 'NA'), ('Niger', 'NI'), ('Ogun', 'OG'),
    ('Ondo', 'ON'), ('Osun', 'OS'), ('Oyo', 'OY'), ('Plateau', 'PL'),
    ('Rivers', 'RI'), ('Sokoto', 'SO'), ('Taraba', 'TA'), ('Yobe', 'YO'),
    ('Zamfara', 'ZA')
]

# Sample LGAs for each state (key ones)
NIGERIAN_LGAS = {
    'Abia': ['Aba North', 'Aba South', 'Arochukwu', 'Bende', 'Ikwuano', 'Isiala Ngwa North', 'Isiala Ngwa South', 'Isuikwuato', 'Obi Ngwa', 'Ohafia', 'Osisioma', 'Ugwunagbo', 'Ukwa East', 'Ukwa West', 'Umuahia North', 'Umuahia South', 'Umunneochi'],
    'Adamawa': ['Demsa', 'Fufure', 'Guyuk', 'Hong', 'Jimeta', 'Maiduguri', 'Maye', 'Mayobelwa', 'Shelleng', 'Singwari', 'Song', 'Toungo', 'Yola North', 'Yola South'],
    'Akwa Ibom': ['Abak', 'Afilang', 'Etim Ekpo', 'Eket', 'Etinan', 'Ikot Abasi', 'Ikot Okoro', 'Ibian', 'Ifiayong', 'Ikono', 'Itu', 'Mbo', 'Nsit Atai', 'Nsit Ibom', 'Nsit Ubium', 'Obot Akara', 'Okobo', 'Onna', 'Oron', 'Udung Uko', 'Ukanafun', 'Uruan', 'Urue-Offong/Oruko', 'Uyo'],
    'Anambra': ['Aguata', 'Anambra East', 'Anambra West', 'Anaocha', 'Awka North', 'Awka South', 'Ayamelum', 'Dunukofia', 'Ekwusigo', 'Idemili North', 'Idemili South', 'Ihiala', 'Njikoka', 'Nnewi North', 'Nnewi South', 'Ogbaru', 'Onitsha North', 'Onitsha South', 'Orumba North', 'Orumba South', 'Oyi'],
    'Bauchi': ['Alkaleri', 'Bauchi', 'Bogoro', 'Damban', 'Darazo', 'Das', 'Dass', 'Dindim', 'Gamawa', 'Ganjuwa', 'Giade', 'Illo', 'Jama\'are', 'Kadarko', 'Kafin Madaki', 'Katagum', 'Kirfi', 'Lere', 'Misau', 'Ningi', 'Sur', 'Tafawa Balewa', 'Toro', 'Warji', 'Yakari'],
    'Bayelsa': ['Brass', 'Ekeremor', 'Ekeremah', 'Forecast', 'Kolokuma/Opokuma', 'Nembe', 'Ogbia', 'Sagbama', 'Southern Ijaw', 'Yenagoa'],
    'Kaduna': ['Birnin Gwari', 'Chikun', 'Giwa', 'Jaba', 'Jema\'a', 'Kachia', 'Kaduna North', 'Kaduna South', 'Kagarko', 'Kajuru', 'Kaura', 'Kauru', 'Kazaure', 'Kudan', 'Lere', 'Makarfi', 'Malumfashi', 'Manchok', 'Mapeo', 'Saba', 'Sabon Gida', 'Saminaka', 'Sanga', 'Satyar', 'Soba', 'Suru', 'Takasku', 'Takauri', 'Tudun Wada', 'Tungar Kawo', 'Zangon Kataf', 'Zaria'],
    'Kano': ['Ajinkyire', 'Albasu', 'Bagwaji', 'Bebeji', 'Bichi', 'Bunkure', 'Dala', 'Dawakin Kudu', 'Dawakin Tofa', 'Diye', 'Fagge', 'Firingoji', 'Gabasawa', 'Garko', 'Garun Mallam', 'Gaya', 'Gezawa', 'Gidi', 'Gilau', 'Gwarzo', 'Hassauwa', 'Karaye', 'Kaura Namoda', 'Kaya', 'Kiri Kasamma', 'Kiyawa', 'Kunchi', 'Kura', 'Kurkur', 'Kwadabne', 'Kwali', 'Kwaraja', 'Lagos', 'Lardin Darezo', 'Madobi', 'Magama', 'Magani', 'Makoda', 'Makunun', 'Makurdi', 'Mala', 'Malimala', 'Malobski', 'Malumfashi', 'Mamuda', 'Mandawari', 'Mangaje', 'Mangu', 'Manonkari', 'Matazu'],
    'Lagos': ['Agege', 'Ajeromi-Ifelodun', 'Alimosho', 'Amuwo-Odofin', 'Apapa', 'Badagry', 'Epe', 'Eti-Osa', 'Ibeju-Lekki', 'Ifako-Ijaye', 'Ikeja', 'Ikorodu', 'Ikeja', 'Ikeja Metropolitan', 'Ikotun/Igando', 'Ikoyi', 'Isolo', 'Lagos Island', 'Lagos Mainland', 'Lekki', 'Ojo', 'Oshodi-Isolo', 'Shomolu', 'Surulere'],
    'Yobe': ['Bade', 'Bursari', 'Damaturu', 'Fune', 'Geidam', 'Gujba', 'Gumel', 'Karasuwa', 'Kariya', 'Machina', 'Nangere', 'Nganzai', 'Potiskum', 'Tarmuwa', 'Yunusari', 'Yusufari'],
}


def upgrade():
    # Create states table
    op.create_table(
        'states',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('code', sa.String(length=2), nullable=False),
        sa.Column('region_id', sa.UUID(), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('code'),
        sa.ForeignKeyConstraint(['region_id'], ['regions.id'], ondelete='SET NULL')
    )
    op.create_index('ix_states_name', 'states', ['name'])
    op.create_index('ix_states_code', 'states', ['code'])
    op.create_index('ix_states_region_id', 'states', ['region_id'])
    op.create_index('ix_states_active', 'states', ['active'])
    
    # Create LGAs table
    op.create_table(
        'lgas',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('state_id', sa.UUID(), nullable=False),
        sa.Column('code', sa.String(length=10), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['state_id'], ['states.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('name', 'state_id')
    )
    op.create_index('ix_lgas_name', 'lgas', ['name'])
    op.create_index('ix_lgas_state_id', 'lgas', ['state_id'])
    op.create_index('ix_lgas_state_name', 'lgas', ['state_id', 'name'])
    op.create_index('ix_lgas_active', 'lgas', ['active'])
    
    # Insert all Nigerian states
    connection = op.get_bind()
    
    for state_name, state_code in NIGERIAN_STATES:
        connection.execute(sa.text("""
            INSERT INTO states (id, name, code, active)
            VALUES (gen_random_uuid(), :name, :code, true)
        """), {
            'name': state_name,
            'code': state_code
        })
    
    # Insert sample LGAs for each state
    for state_name, lgas in NIGERIAN_LGAS.items():
        # Get state ID
        state_result = connection.execute(sa.text("""
            SELECT id FROM states WHERE name = :name
        """), {'name': state_name}).fetchone()
        
        if state_result:
            state_id = str(state_result[0])
            
            for lga_name in lgas:
                connection.execute(sa.text("""
                    INSERT INTO lgas (id, name, state_id, active)
                    VALUES (gen_random_uuid(), :name, :state_id, true)
                """), {
                    'name': lga_name,
                    'state_id': state_id
                })
    
    connection.commit()


def downgrade():
    op.drop_table('lgas')
    op.drop_table('states')
