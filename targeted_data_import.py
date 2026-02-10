#!/usr/bin/env python3
"""
Targeted Data Import Script for MySQL to PostgreSQL Migration
Handles large INSERT statements from MySQL dump with proper parsing
"""

import re
import psycopg2
from psycopg2 import sql, extras
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TargetedDataImporter:
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
        
    def extract_table_data(self, table_name: str) -> list:
        """Extract INSERT data for a specific table from MySQL dump"""
        logger.info(f"Extracting data for table: {table_name}")
        
        with open(self.mysql_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Find the INSERT section for this table (multi-line format)
        # Pattern matches: INSERT INTO `table_name` (columns) VALUES\n(data),\n(data),...;
        
        # First find the INSERT statement start
        insert_start_pattern = rf"INSERT INTO `{table_name}` \([^)]+\) VALUES"
        insert_match = re.search(insert_start_pattern, content, re.IGNORECASE | re.DOTALL)
        
        if not insert_match:
            logger.warning(f"No INSERT statements found for table: {table_name}")
            return []
        
        # Extract everything from INSERT to the final semicolon
        start_pos = insert_match.start()
        
        # Find the end by looking for the semicolon after the values
        remaining_content = content[start_pos:]
        paren_count = 0
        in_values = False
        end_pos = 0
        
        for i, char in enumerate(remaining_content):
            if char == '(':
                paren_count += 1
                in_values = True
            elif char == ')':
                paren_count -= 1
            elif char == ';' and paren_count == 0 and in_values:
                end_pos = i
                break
        
        if end_pos == 0:
            logger.warning(f"Could not find end of INSERT statement for {table_name}")
            return []
        
        full_insert = remaining_content[:end_pos + 1]
        
        # Extract column names
        columns_match = re.search(r"INSERT INTO `" + re.escape(table_name) + r"` \((.*?)\) VALUES", full_insert, re.IGNORECASE | re.DOTALL)
        if not columns_match:
            logger.warning(f"Could not extract columns for {table_name}")
            return []
        
        columns_str = columns_match.group(1)
        columns = [col.strip().replace('`', '') for col in columns_str.split(',')]
        
        # Extract the VALUES part
        values_start = full_insert.find("VALUES") + len("VALUES")
        values_str = full_insert[values_start:].rstrip(';')
        
        # Parse values
        values = self.parse_values_block(values_str)
        
        # Convert to dict format
        all_data = []
        for row in values:
            if len(row) == len(columns):
                all_data.append(dict(zip(columns, row)))
            else:
                logger.warning(f"Column count mismatch in {table_name}: expected {len(columns)}, got {len(row)}")
        
        logger.info(f"Extracted {len(all_data)} records for {table_name}")
        return all_data
    
    def parse_values_block(self, values_str: str) -> list:
        """Parse a block of VALUES from INSERT statement"""
        values = []
        current_row = ""
        in_quotes = False
        quote_char = None
        paren_depth = 0
        i = 0
        
        while i < len(values_str):
            char = values_str[i]
            
            if char in ("'", '"') and not in_quotes:
                in_quotes = True
                quote_char = char
            elif char == quote_char and in_quotes:
                # Check for escaped quotes
                if i + 1 < len(values_str) and values_str[i + 1] == quote_char:
                    current_row += char
                    i += 1  # Skip the escaped quote
                else:
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
                    # Parse the completed row
                    row_values = self.parse_row_values(current_row)
                    values.append(row_values)
                    current_row = ""
                    # Skip comma after row if present
                    if i + 1 < len(values_str) and values_str[i + 1] == ',':
                        i += 1
                else:
                    current_row += char
            else:
                if paren_depth > 0:
                    current_row += char
            
            i += 1
        
        return values
    
    def parse_row_values(self, row_str: str) -> list:
        """Parse individual row values"""
        values = []
        current_value = ""
        in_quotes = False
        quote_char = None
        i = 0
        
        while i < len(row_str):
            char = row_str[i]
            
            if char in ("'", '"') and not in_quotes:
                in_quotes = True
                quote_char = char
            elif char == quote_char and in_quotes:
                # Handle escaped quotes
                if i + 1 < len(row_str) and row_str[i + 1] == quote_char:
                    current_value += char
                    i += 1
                else:
                    in_quotes = False
                    quote_char = None
            elif char == ',' and not in_quotes:
                # Process completed value
                values.append(self.convert_value(current_value.strip()))
                current_value = ""
            else:
                current_value += char
            
            i += 1
        
        # Add last value
        if current_value.strip():
            values.append(self.convert_value(current_value.strip()))
        
        return values
    
    def convert_value(self, value: str) -> any:
        """Convert string value to appropriate Python type"""
        if value == 'NULL' or value == '':
            return None
        
        # Remove quotes if present
        if (value.startswith("'") and value.endswith("'")) or \
           (value.startswith('"') and value.endswith('"')):
            value = value[1:-1]
            # Handle escaped quotes
            value = value.replace("''", "'").replace('""', '"')
            return value
        
        # Try to convert to number
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            return value
    
    def import_table_data(self, table_name: str, data: list):
        """Import data into a specific table"""
        if not data:
            logger.info(f"No data to import for {table_name}")
            return
        
        logger.info(f"Importing {len(data)} records into {table_name}")
        
        # Get column names from first record
        columns = list(data[0].keys())
        
        # Prepare INSERT statement
        insert_sql = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
            sql.Identifier(table_name),
            sql.SQL(", ").join(map(sql.Identifier, columns)),
            sql.SQL(", ").join([sql.Placeholder()] * len(columns))
        )
        
        # Convert dict list to tuple list for execute_batch
        tuple_data = []
        for record in data:
            tuple_data.append(tuple(record[col] for col in columns))
        
        # Import in batches
        batch_size = 1000
        for i in range(0, len(tuple_data), batch_size):
            batch = tuple_data[i:i + batch_size]
            
            try:
                extras.execute_batch(self.cursor, insert_sql, batch)
                self.conn.commit()
                logger.info(f"  Imported {min(i + batch_size, len(tuple_data))}/{len(tuple_data)} records")
            except Exception as e:
                self.conn.rollback()
                logger.error(f"Failed to import batch for {table_name}: {e}")
                raise
        
        logger.info(f"Completed import for {table_name}")
    
    def reset_sequence(self, table_name: str, column_name: str):
        """Reset sequence for auto-increment column"""
        try:
            # Get max ID
            max_id_sql = sql.SQL("SELECT MAX({}) FROM {}").format(
                sql.Identifier(column_name),
                sql.Identifier(table_name)
            )
            self.cursor.execute(max_id_sql)
            max_id = self.cursor.fetchone()[0]
            
            if max_id:
                # Reset sequence
                sequence_name = f"{table_name}_{column_name}_seq"
                reset_sql = sql.SQL("ALTER SEQUENCE {} RESTART WITH {}").format(
                    sql.Identifier(sequence_name),
                    sql.Literal(max_id + 1)
                )
                self.cursor.execute(reset_sql)
                self.conn.commit()
                logger.info(f"Reset sequence for {table_name}.{column_name} to {max_id + 1}")
        except Exception as e:
            logger.warning(f"Could not reset sequence for {table_name}: {e}")
    
    def import_all_data(self):
        """Import data for all tables in priority order"""
        # Tables in dependency order
        tables = [
            ('countries', 'id'),
            ('regions', 'id'),
            ('states', 'id'),
            ('lgas', 'id'),
            ('actors', 'id'),
            ('conflict_types', 'id'),
            ('users', 'id'),
            ('conflicts', 'id'),
            ('cache', None),  # No auto-increment
            ('cache_locks', None),
            ('sessions', None),
            ('migrations', 'id'),
            ('failed_jobs', 'id'),
            ('jobs', 'id'),
            ('job_batches', None),
            ('password_reset_tokens', None),
            ('personal_access_tokens', 'id')
        ]
        
        for table_name, pk_column in tables:
            try:
                # Extract data from MySQL dump
                data = self.extract_table_data(table_name)
                
                # Import data
                self.import_table_data(table_name, data)
                
                # Reset sequence if table has auto-increment primary key
                if pk_column and data:
                    self.reset_sequence(table_name, pk_column)
                
            except Exception as e:
                logger.error(f"Failed to import {table_name}: {e}")
                continue
        
        # Final verification
        self.verify_import()
    
    def verify_import(self):
        """Verify the import by checking record counts"""
        logger.info("Verifying import...")
        
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
                self.cursor.execute(query)
                count = self.cursor.fetchone()[0]
                logger.info(f"{table_name}: {count} records")
            except Exception as e:
                logger.error(f"Failed to verify {table_name}: {e}")
        
        # Check conflicts date range
        try:
            self.cursor.execute("""
                SELECT 
                    MIN(incidence_date) as earliest,
                    MAX(incidence_date) as latest,
                    COUNT(*) as total
                FROM conflicts
            """)
            result = self.cursor.fetchone()
            if result[2] > 0:
                logger.info(f"Conflicts data: {result[0]} to {result[1]} ({result[2]} total records)")
        except Exception as e:
            logger.error(f"Failed to check conflicts date range: {e}")


def main():
    mysql_file = "/Users/ejikeudeze/AI_Projects/naija-conflict-tracker/u503102722_conflictdb (1).sql"
    connection_string = "postgresql://neondb_owner:npg_bL6dDyw8WEMI@ep-gentle-union-agwmnyzn-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
    
    importer = TargetedDataImporter(mysql_file, connection_string)
    
    try:
        importer.connect()
        importer.import_all_data()
        logger.info("🎉 Data import completed successfully!")
    except Exception as e:
        logger.error(f"❌ Import failed: {e}")
        sys.exit(1)
    finally:
        importer.close()


if __name__ == "__main__":
    main()
