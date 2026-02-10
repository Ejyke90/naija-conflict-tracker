#!/usr/bin/env python3
"""
Complete MySQL to PostgreSQL Migration using sqlglot
Extracts all data from the SQL file including missed records
"""

import sqlglot
from sqlglot import transpile
import csv
import os
import psycopg2
from psycopg2 import sql, extras
import logging
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def transpile_and_extract_all():
    mysql_file = '/Users/ejikeudeze/AI_Projects/naija-conflict-tracker/u503102722_conflictdb (1).sql'
    connection_string = 'postgresql://neondb_owner:npg_bL6dDyw8WEMI@ep-gentle-union-agwmnyzn-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'
    
    logger.info('Starting complete migration with sqlglot...')
    
    # Read the MySQL file
    with open(mysql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Split by semicolon to handle statements individually
    statements = sql_content.split(';')
    postgres_statements = []
    
    conflicts_data = []
    other_tables = {}
    
    for stmt in statements:
        stmt = stmt.strip()
        if not stmt or stmt.startswith('--') or stmt.startswith('/*'):
            continue
        
        try:
            # Use sqlglot for reliable transpilation
            transpiled = transpile(stmt, read='mysql', write='postgres')[0]
            
            # Apply PostgreSQL-specific fixes
            transpiled = re.sub(r'TINYINT\(1\)', 'BOOLEAN', transpiled, flags=re.IGNORECASE)
            transpiled = re.sub(
                r'BIGINT NOT NULL AUTO_INCREMENT',
                'BIGINT GENERATED ALWAYS AS IDENTITY',
                transpiled,
                flags=re.IGNORECASE
            )
            
            postgres_statements.append(transpiled + ';')
            
            # If it's a conflicts INSERT, extract the data
            if 'INSERT INTO "conflicts"' in transpiled:
                # Parse the INSERT statement to extract data
                conflicts_data.extend(extract_insert_data(transpiled))
            elif 'INSERT INTO' in transpiled:
                # Handle other tables
                table_match = re.search(r'INSERT INTO "([^"]+)"', transpiled)
                if table_match:
                    table_name = table_match.group(1)
                    if table_name not in other_tables:
                        other_tables[table_name] = []
                    other_tables[table_name].extend(extract_insert_data(transpiled))
                    
        except Exception as e:
            logger.warning(f'Skipping statement due to parse error: {stmt[:50]}... Error: {e}')
            continue
    
    logger.info(f'Transpiled {len(postgres_statements)} statements')
    logger.info(f'Found {len(conflicts_data)} conflict records')
    
    # Export all data to CSV
    os.makedirs('complete_migration', exist_ok=True)
    
    # Export conflicts
    if conflicts_data:
        export_to_csv('complete_migration/conflicts.csv', conflicts_data)
        logger.info(f'Exported {len(conflicts_data)} conflict records')
    
    # Export other tables
    for table_name, data in other_tables.items():
        if data:
            export_to_csv(f'complete_migration/{table_name}.csv', data)
            logger.info(f'Exported {len(data)} {table_name} records')
    
    # Import to PostgreSQL
    import_to_postgres('complete_migration', connection_string)

def extract_insert_data(sql_statement):
    """Extract data from an INSERT statement"""
    data = []
    
    # Find the VALUES part
    values_match = re.search(r'VALUES\s*(.*)', sql_statement, re.DOTALL)
    if not values_match:
        return data
    
    values_str = values_match.group(1)
    
    # Parse each row
    current_row = []
    current_value = ''
    in_quotes = False
    quote_char = None
    paren_depth = 0
    i = 0
    
    while i < len(values_str):
        char = values_str[i]
        
        if char in ("'", '"') and not in_quotes:
            in_quotes = True
            quote_char = char
            current_value += char
        elif char == quote_char and in_quotes:
            if i + 1 < len(values_str) and values_str[i + 1] == quote_char:
                current_value += char + values_str[i + 1]
                i += 2
                continue
            else:
                current_value += char
                in_quotes = False
                quote_char = None
        elif char == '(' and not in_quotes:
            paren_depth += 1
            if paren_depth == 1:
                current_row = []
                current_value = ''
            else:
                current_value += char
        elif char == ')' and not in_quotes:
            paren_depth -= 1
            if paren_depth == 0:
                current_row.append(clean_value(current_value))
                data.append(current_row)
                current_row = []
                current_value = ''
            else:
                current_value += char
        elif char == ',' and not in_quotes and paren_depth == 1:
            current_row.append(clean_value(current_value))
            current_value = ''
        else:
            current_value += char
        
        i += 1
    
    return data

def clean_value(value):
    """Clean a value from quotes and handle NULL"""
    if not value or value.strip() == 'NULL':
        return ''
    
    value = value.strip()
    
    # Remove quotes if present
    if (value.startswith("'") and value.endswith("'")) or \
       (value.startswith('"') and value.endswith('"')):
        value = value[1:-1]
        # Handle escaped quotes
        value = value.replace("''", "'").replace('""', '"')
    
    return value

def export_to_csv(filename, data):
    """Export data to CSV file"""
    if not data:
        return
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        
        # Write header (assuming first row has correct structure)
        # For conflicts, we know the column structure
        if 'conflicts' in filename:
            header = ['id', 'incidence_date', 'conflict_type_id', 'country_id', 'region_id', 
                     'state_id', 'lga_id', 'community', 'civilian_death_male', 'civilian_death_female',
                     'civilian_death_unknown', 'security_death_male', 'security_death_female',
                     'security_death_unknown', 'injured_male', 'injured_female', 'injured_unknown',
                     'kidnapped_male', 'kidnapped_female', 'kidnapped_unknown', 'displaced_persons',
                     'displaced_male', 'displaced_female', 'actor_1', 'actor_2', 'actor_3',
                     'description', 'action', 'highway_roads_water', 'confirmation_verification',
                     'verification_level', 'source_url', 'source_contact_details', 'source_contact_pictures',
                     'source_metadata', 'data_source', 'reporter_id', 'created_at', 'updated_at', 'deleted_at']
            writer.writerow(header)
        
        # Write data
        for row in data:
            processed_row = []
            for value in row:
                if value == '' or value is None:
                    processed_row.append('\\N')  # PostgreSQL NULL indicator
                else:
                    processed_row.append(value)
            writer.writerow(processed_row)

def import_to_postgres(csv_dir, connection_string):
    """Import CSV files to PostgreSQL"""
    logger.info('Connecting to PostgreSQL...')
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()
    
    # Import order respecting foreign keys
    import_order = ['countries', 'regions', 'states', 'lgas', 'actors', 'conflict_types', 'users', 'conflicts']
    
    for table_name in import_order:
        csv_file = os.path.join(csv_dir, f'{table_name}.csv')
        if not os.path.exists(csv_file):
            logger.info(f'No CSV file for {table_name}')
            continue
        
        logger.info(f'Importing {table_name} from {csv_file}')
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                cursor.copy_expert(f'COPY {table_name} FROM STDIN WITH CSV HEADER NULL AS \\N', f)
            
            conn.commit()
            
            # Count imported records
            cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
            count = cursor.fetchone()[0]
            logger.info(f'✅ Successfully imported {count:,} records to {table_name}')
            
        except Exception as e:
            conn.rollback()
            logger.error(f'❌ Failed to import {table_name}: {e}')
    
    # Final verification
    logger.info('Final verification:')
    for table_name in ['countries', 'regions', 'states', 'lgas', 'actors', 'conflict_types', 'users', 'conflicts']:
        try:
            cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
            count = cursor.fetchone()[0]
            logger.info(f'✅ {table_name}: {count:,} records')
        except:
            pass
    
    cursor.close()
    conn.close()
    logger.info('🎉 Complete migration finished!')

if __name__ == '__main__':
    transpile_and_extract_all()
