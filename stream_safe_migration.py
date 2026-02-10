#!/usr/bin/env python3
"""
Stream-Safe MySQL to PostgreSQL Migration Script
Processes large SQL dumps line-by-line to capture all data
"""

import csv
import os
import re
import psycopg2
from psycopg2 import sql, extras
import logging
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StreamSafeSQLParser:
    def __init__(self, mysql_file: str, output_dir: str = "stream_csv_exports"):
        self.mysql_file = mysql_file
        self.output_dir = output_dir
        self.connection = None
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
    
    def stream_parse_sql(self) -> Dict[str, str]:
        """Parse SQL file line-by-line to handle large INSERT blocks"""
        logger.info(f"Starting stream parse of {self.mysql_file}...")
        
        current_table = None
        current_columns = []
        csv_writer = None
        f_out = None
        csv_files = {}
        record_counts = {}
        
        # Regex to catch: INSERT INTO `table_name` (`col1`, `col2`) VALUES
        insert_re = re.compile(r"INSERT INTO `([^`]+)` \((.*?)\) VALUES", re.IGNORECASE)
        
        with open(self.mysql_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line: continue
                
                # Skip comments and directives
                if line.startswith('--') or line.startswith('/*') or line.startswith('*/'):
                    continue
                
                # Detect new table insert block
                match = insert_re.match(line)
                if match:
                    new_table = match.group(1)
                    cols = [c.strip(' `') for c in match.group(2).split(',')]
                    
                    # If we switched tables, close the old file
                    if new_table != current_table:
                        if f_out:
                            f_out.close()
                            record_counts[current_table] = csv_files.get(current_table, 0)
                        
                        current_table = new_table
                        current_columns = cols
                        csv_path = os.path.join(self.output_dir, f"{current_table}.csv")
                        f_out = open(csv_path, 'w', newline='', encoding='utf-8')
                        csv_writer = csv.writer(f_out, quoting=csv.QUOTE_MINIMAL)
                        csv_writer.writerow(current_columns)
                        csv_files[current_table] = 0
                        logger.info(f"Line {line_num}: Extracting data for table: {current_table}")
                    
                    # Process the values attached to the INSERT line or subsequent lines
                    values_part = line[match.end():].strip()
                    records_added = self.process_values(values_part, csv_writer, current_columns)
                    if records_added > 0:
                        csv_files[current_table] += records_added
                
                elif current_table and line.startswith('('):
                    # Process continuing value lines
                    records_added = self.process_values(line, csv_writer, current_columns)
                    if records_added > 0:
                        csv_files[current_table] += records_added
        
        if f_out:
            f_out.close()
            record_counts[current_table] = csv_files.get(current_table, 0)
        
        logger.info("Extraction complete. Checking extracted data...")
        
        # Verify record counts
        for table, count in csv_files.items():
            csv_path = os.path.join(self.output_dir, f"{table}.csv")
            if os.path.exists(csv_path):
                with open(csv_path, 'r') as f:
                    lines = sum(1 for _ in f) - 1  # Subtract header
                logger.info(f"✅ {table}: {lines:,} records extracted")
                csv_files[table] = lines
            else:
                logger.warning(f"⚠️ {table}: CSV file not found")
        
        return csv_files
    
    def process_values(self, text: str, writer, columns: List[str]) -> int:
        """Process VALUES text and extract rows"""
        if not text or not writer:
            return 0
        
        # Clean up trailing semicolons or commas
        text = text.rstrip(';').rstrip(',')
        
        if not text:
            return 0
        
        # Use a more robust parsing approach
        rows = self.extract_rows_from_values(text)
        
        for row in rows:
            # Parse individual values
            values = self.parse_row_values(row)
            if len(values) == len(columns):
                # Convert NULL values to PostgreSQL format
                cleaned_vals = []
                for val in values:
                    val = val.strip()
                    if val.upper() == 'NULL' or val == '':
                        cleaned_vals.append('\\N')  # PostgreSQL NULL
                    else:
                        # Handle escaped quotes
                        cleaned_vals.append(val.replace("''", "'"))
                writer.writerow(cleaned_vals)
        
        return len(rows)
    
    def extract_rows_from_values(self, values_text: str) -> List[str]:
        """Extract individual rows from VALUES text"""
        rows = []
        current_row = ""
        paren_depth = 0
        in_quotes = False
        quote_char = None
        i = 0
        
        while i < len(values_text):
            char = values_text[i]
            
            if char in ("'", '"') and not in_quotes:
                in_quotes = True
                quote_char = char
                current_row += char
            elif char == quote_char and in_quotes:
                # Check for escaped quotes
                if i + 1 < len(values_text) and values_text[i + 1] == quote_char:
                    current_row += char + values_text[i + 1]
                    i += 2
                    continue
                else:
                    current_row += char
                    in_quotes = False
                    quote_char = None
            elif char == '(' and not in_quotes:
                paren_depth += 1
                if paren_depth == 1:
                    current_row = ""
                else:
                    current_row += char
            elif char == ')' and not in_quotes:
                paren_depth -= 1
                if paren_depth == 0:
                    rows.append(current_row)
                    current_row = ""
                    # Skip comma after row if present
                    if i + 1 < len(values_text) and values_text[i + 1] == ',':
                        i += 1
                else:
                    current_row += char
            else:
                if paren_depth > 0:
                    current_row += char
            
            i += 1
        
        return rows
    
    def parse_row_values(self, row: str) -> List[str]:
        """Parse individual row values with proper quote handling"""
        values = []
        current_value = ""
        in_quotes = False
        quote_char = None
        i = 0
        
        while i < len(row):
            char = row[i]
            
            if char in ("'", '"') and not in_quotes:
                in_quotes = True
                quote_char = char
                current_value += char
            elif char == quote_char and in_quotes:
                # Check for escaped quotes
                if i + 1 < len(row) and row[i + 1] == quote_char:
                    current_value += char + row[i + 1]
                    i += 2
                    continue
                else:
                    current_value += char
                    in_quotes = False
                    quote_char = None
            elif char == ',' and not in_quotes:
                # End of value
                values.append(current_value)
                current_value = ""
            else:
                current_value += char
            
            i += 1
        
        # Add the last value
        if current_value or in_quotes:
            values.append(current_value)
        
        return values
    
    def import_csv_to_postgres(self, csv_files: Dict[str, str], connection_string: str):
        """Import CSV files to PostgreSQL using COPY command"""
        logger.info("Connecting to PostgreSQL...")
        self.connection = psycopg2.connect(connection_string)
        cursor = self.connection.cursor()
        
        # Import order respecting foreign keys
        import_order = [
            'countries', 'regions', 'states', 'lgas',
            'actors', 'conflict_types', 'users', 'conflicts',
            'cache', 'cache_locks', 'sessions', 'migrations',
            'failed_jobs', 'jobs', 'job_batches',
            'password_reset_tokens', 'personal_access_tokens'
        ]
        
        for table_name in import_order:
            csv_file = os.path.join(self.output_dir, f"{table_name}.csv")
            if not os.path.exists(csv_file):
                logger.info(f"No CSV file for {table_name}")
                continue
            
            record_count = csv_files.get(table_name, 0)
            logger.info(f"Importing {table_name}: {record_count:,} records from {csv_file}")
            
            try:
                # Use COPY command for efficient import
                with open(csv_file, 'r', encoding='utf-8') as f:
                    cursor.copy_expert(
                        f"COPY {table_name} FROM STDIN WITH CSV HEADER NULL AS '\\N'",
                        f
                    )
                
                self.connection.commit()
                
                # Count imported records
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                logger.info(f"✅ Successfully imported {count:,} records to {table_name}")
                
                # Reset sequence if table has ID column
                cursor.execute(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = '{table_name}' AND column_name = 'id'
                """)
                if cursor.fetchone():
                    self.reset_sequence(cursor, table_name, 'id')
                
            except Exception as e:
                self.connection.rollback()
                logger.error(f"❌ Failed to import {table_name}: {e}")
                continue
        
        # Final verification
        self.verify_import(cursor)
        
        cursor.close()
        self.connection.close()
        logger.info("All imports completed")
    
    def reset_sequence(self, cursor, table_name: str, column_name: str):
        """Reset sequence for auto-increment column"""
        try:
            cursor.execute(f"SELECT MAX({column_name}) FROM {table_name}")
            max_id = cursor.fetchone()[0]
            
            if max_id:
                cursor.execute(f"""
                    SELECT setval(pg_get_serial_sequence('{table_name}', '{column_name}'), 
                                 coalesce(max({column_name}), 1)) 
                    FROM {table_name}
                """)
                self.connection.commit()
                logger.info(f"🔄 Reset sequence for {table_name}.{column_name}")
        except Exception as e:
            logger.warning(f"⚠️ Could not reset sequence for {table_name}: {e}")
    
    def verify_import(self, cursor):
        """Verify the import results"""
        logger.info("📊 Final verification results...")
        
        verification_queries = [
            ("actors", "SELECT COUNT(*) FROM actors"),
            ("conflicts", "SELECT COUNT(*) FROM conflicts"),
            ("states", "SELECT COUNT(*) FROM states"),
            ("lgas", "SELECT COUNT(*) FROM lgas"),
            ("users", "SELECT COUNT(*) FROM users"),
            ("conflict_types", "SELECT COUNT(*) FROM conflict_types"),
            ("regions", "SELECT COUNT(*) FROM regions"),
            ("countries", "SELECT COUNT(*) FROM countries")
        ]
        
        for table_name, query in verification_queries:
            try:
                cursor.execute(query)
                count = cursor.fetchone()[0]
                logger.info(f"✅ {table_name}: {count:,} records")
            except Exception as e:
                logger.error(f"❌ Failed to verify {table_name}: {e}")
        
        # Check conflicts date range and highest ID
        try:
            cursor.execute("""
                SELECT 
                    MIN(incidence_date) as earliest,
                    MAX(incidence_date) as latest,
                    COUNT(*) as total,
                    MAX(id) as max_id
                FROM conflicts
            """)
            result = cursor.fetchone()
            if result[3] > 0:
                logger.info(f"📅 Conflicts: {result[0]} to {result[1]} ({result[2]:,} total, max ID: {result[3]})")
        except Exception as e:
            logger.error(f"Failed to check conflicts details: {e}")


def main():
    mysql_file = "/Users/ejikeudeze/AI_Projects/naija-conflict-tracker/u503102722_conflictdb (1).sql"
    connection_string = "postgresql://neondb_owner:npg_bL6dDyw8WEMI@ep-gentle-union-agwmnyzn-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
    
    parser = StreamSafeSQLParser(mysql_file)
    
    try:
        # Extract all data using stream-safe parsing
        logger.info("🔄 Starting stream-safe extraction...")
        csv_files = parser.stream_parse_sql()
        
        logger.info(f"📄 Extracted data from {len(csv_files)} tables:")
        for table, count in csv_files.items():
            logger.info(f"  📊 {table}: {count:,} records")
        
        # Import to PostgreSQL
        logger.info("📥 Importing CSV files to PostgreSQL...")
        parser.import_csv_to_postgres(csv_files, connection_string)
        
        logger.info("🎉 Stream-safe MySQL to PostgreSQL migration completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
