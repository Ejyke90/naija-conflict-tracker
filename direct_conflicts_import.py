#!/usr/bin/env python3
"""
Final Direct Import Solution
Bypasses CSV issues and directly imports MySQL data to PostgreSQL
"""

import psycopg2
from psycopg2 import sql, extras
import re
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DirectImporter:
    def __init__(self, mysql_file: str, connection_string: str):
        self.mysql_file = mysql_file
        self.connection_string = connection_string
        self.conn = None
        self.cursor = None
    
    def connect(self):
        self.conn = psycopg2.connect(self.connection_string)
        self.cursor = self.conn.cursor()
        logger.info("Connected to PostgreSQL")
    
    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("Connection closed")
    
    def extract_conflicts_data(self):
        """Extract conflicts data directly from MySQL file"""
        logger.info("Extracting conflicts data from MySQL file...")
        
        with open(self.mysql_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Find the conflicts INSERT statement
        pattern = r'INSERT INTO `conflicts` \([^)]+\) VALUES\s+(.+?);'
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        
        if not match:
            raise ValueError("Could not find conflicts INSERT statement")
        
        values_str = match.group(1)
        
        # Parse the values manually
        data = self.parse_values(values_str)
        logger.info(f"Extracted {len(data)} conflict records")
        
        return data
    
    def parse_values(self, values_str):
        """Parse values from MySQL INSERT"""
        values = []
        current_row = []
        current_value = ""
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
                current_value += char
                # Check for escaped quotes
                if i + 1 < len(values_str) and values_str[i + 1] == quote_char:
                    current_value += values_str[i + 1]
                    i += 2
                    continue
                else:
                    in_quotes = False
                    quote_char = None
            elif char == '(' and not in_quotes:
                paren_depth += 1
                if paren_depth == 1:
                    current_row = []
                    current_value = ""
                else:
                    current_value += char
            elif char == ')' and not in_quotes:
                paren_depth -= 1
                if paren_depth == 0:
                    current_row.append(self.clean_value(current_value))
                    values.append(current_row)
                    current_row = []
                    current_value = ""
                else:
                    current_value += char
            elif char == ',' and not in_quotes and paren_depth == 1:
                current_row.append(self.clean_value(current_value))
                current_value = ""
            else:
                current_value += char
            
            i += 1
        
        return values
    
    def clean_value(self, value):
        """Clean a single value"""
        if not value or value.strip() == 'NULL':
            return None
        
        value = value.strip()
        
        # Remove quotes if present
        if (value.startswith("'") and value.endswith("'")) or \
           (value.startswith('"') and value.endswith('"')):
            value = value[1:-1]
            # Handle escaped quotes
            value = value.replace("''", "'").replace('""', '"')
        
        # Convert to appropriate type
        try:
            if value == '':
                return None
            elif '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            return value
    
    def import_conflicts_data(self, data):
        """Import conflicts data directly"""
        logger.info(f"Importing {len(data)} conflict records...")
        
        # Define the columns in order
        columns = [
            'id', 'incidence_date', 'conflict_type_id', 'country_id', 'region_id', 
            'state_id', 'lga_id', 'community', 'civilian_death_male', 'civilian_death_female',
            'civilian_death_unknown', 'security_death_male', 'security_death_female', 
            'security_death_unknown', 'injured_male', 'injured_female', 'injured_unknown',
            'kidnapped_male', 'kidnapped_female', 'kidnapped_unknown', 'displaced_persons',
            'displaced_male', 'displaced_female', 'actor_1', 'actor_2', 'actor_3',
            'description', 'action', 'highway_roads_water', 'confirmation_verification',
            'verification_level', 'source_url', 'source_contact_details', 'source_contact_pictures',
            'source_metadata', 'data_source', 'reporter_id', 'created_at', 'updated_at', 'deleted_at'
        ]
        
        # Create INSERT statement
        insert_sql = sql.SQL("INSERT INTO conflicts ({}) VALUES ({})").format(
            sql.SQL(", ").join(map(sql.Identifier, columns)),
            sql.SQL(", ").join([sql.Placeholder()] * len(columns))
        )
        
        # Import in batches
        batch_size = 100
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            
            try:
                extras.execute_batch(self.cursor, insert_sql, batch)
                self.conn.commit()
                logger.info(f"  Imported {min(i + batch_size, len(data))}/{len(data)} records")
            except Exception as e:
                self.conn.rollback()
                logger.error(f"Failed to import batch starting at record {i}: {e}")
                # Try individual records
                for j, record in enumerate(batch):
                    try:
                        self.cursor.execute(insert_sql, record)
                        self.conn.commit()
                    except Exception as e2:
                        self.conn.rollback()
                        logger.error(f"Failed to import record {i+j}: {e2}")
                        continue
                continue
        
        logger.info("Conflicts data import completed")
    
    def verify_import(self):
        """Verify the import results"""
        logger.info("Verifying import...")
        
        # Check total count
        self.cursor.execute("SELECT COUNT(*) FROM conflicts")
        count = self.cursor.fetchone()[0]
        logger.info(f"✅ Total conflicts: {count:,}")
        
        # Check date range
        self.cursor.execute("""
            SELECT 
                MIN(incidence_date) as earliest,
                MAX(incidence_date) as latest,
                COUNT(*) as total
            FROM conflicts
        """)
        result = self.cursor.fetchone()
        if result[2] > 0:
            logger.info(f"📅 Date range: {result[0]} to {result[1]} ({result[2]:,} records)")
        
        # Check by year
        self.cursor.execute("""
            SELECT 
                EXTRACT(YEAR FROM incidence_date) as year,
                COUNT(*) as count
            FROM conflicts
            GROUP BY EXTRACT(YEAR FROM incidence_date)
            ORDER BY year
        """)
        years = self.cursor.fetchall()
        logger.info("📊 Records by year:")
        for year, count in years:
            logger.info(f"  {int(year)}: {count:,}")
    
    def reset_sequence(self):
        """Reset the conflicts ID sequence"""
        try:
            self.cursor.execute("SELECT MAX(id) FROM conflicts")
            max_id = self.cursor.fetchone()[0]
            
            if max_id:
                self.cursor.execute("ALTER SEQUENCE conflicts_id_seq RESTART WITH %s", (max_id + 1,))
                self.conn.commit()
                logger.info(f"Reset conflicts_id_seq to {max_id + 1}")
        except Exception as e:
            logger.warning(f"Could not reset sequence: {e}")


def main():
    mysql_file = "/Users/ejikeudeze/AI_Projects/naija-conflict-tracker/u503102722_conflictdb (1).sql"
    connection_string = "postgresql://neondb_owner:npg_bL6dDyw8WEMI@ep-gentle-union-agwmnyzn-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
    
    importer = DirectImporter(mysql_file, connection_string)
    
    try:
        importer.connect()
        
        # Extract and import conflicts data
        data = importer.extract_conflicts_data()
        importer.import_conflicts_data(data)
        
        # Verify and cleanup
        importer.verify_import()
        importer.reset_sequence()
        
        logger.info("🎉 Conflicts data import completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        importer.close()


if __name__ == "__main__":
    main()
