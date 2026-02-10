#!/usr/bin/env python3
"""
Enhanced MySQL to PostgreSQL Converter
Fixes parsing issues with multi-line INSERT statements
"""

import csv
import os
import re
import psycopg2
from psycopg2 import sql, extras
import logging
from typing import Dict, List, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedSQLParser:
    def __init__(self, mysql_file: str, output_dir: str = "enhanced_csv_exports"):
        self.mysql_file = mysql_file
        self.output_dir = output_dir
        self.connection = None
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
    
    def count_records_in_insert(self, insert_text: str) -> int:
        """Accurately count records in a multi-line INSERT statement"""
        # Remove the INSERT INTO part and just look at VALUES
        values_match = re.search(r'VALUES\s*(.*)', insert_text, re.DOTALL)
        if not values_match:
            return 0
        
        values_str = values_match.group(1)
        # Count opening parentheses that start a new record
        record_count = 0
        paren_depth = 0
        in_quotes = False
        quote_char = None
        
        i = 0
        while i < len(values_str):
            char = values_str[i]
            
            if char in ("'", '"') and not in_quotes:
                in_quotes = True
                quote_char = char
            elif char == quote_char and in_quotes:
                # Check for escaped quotes
                if i + 1 < len(values_str) and values_str[i + 1] == quote_char:
                    i += 2  # Skip escaped quote
                    continue
                else:
                    in_quotes = False
                    quote_char = None
            elif char == '(' and not in_quotes:
                paren_depth += 1
                if paren_depth == 1:
                    record_count += 1
            elif char == ')' and not in_quotes:
                paren_depth -= 1
            
            i += 1
        
        return record_count
    
    def split_sql_statements(self, content: str) -> List[str]:
        """Split SQL content into statements by semicolons, respecting quotes"""
        statements = []
        current_statement = ""
        in_quotes = False
        quote_char = None
        i = 0
        
        while i < len(content):
            char = content[i]
            
            # Handle quote tracking
            if char in ("'", '"') and not in_quotes:
                in_quotes = True
                quote_char = char
            elif char == quote_char and in_quotes:
                # Check for escaped quotes
                if i + 1 < len(content) and content[i + 1] == quote_char:
                    current_statement += char + content[i + 1]
                    i += 2
                    continue
                else:
                    in_quotes = False
                    quote_char = None
            
            # Split on semicolon if not in quotes
            if char == ';' and not in_quotes:
                statement = current_statement.strip()
                if statement:
                    statements.append(statement + ';')
                current_statement = ""
            else:
                current_statement += char
            
            i += 1
        
        # Add any remaining content
        if current_statement.strip():
            statements.append(current_statement.strip())
        
        return statements
    
    def parse_insert_statement(self, stmt: str) -> Tuple[str, List[str], List[List[str]]]:
        """Parse a single INSERT statement with improved handling"""
        # Extract table name
        table_match = re.search(r'INSERT\s+INTO\s+`([^`]+)`', stmt, re.IGNORECASE)
        if not table_match:
            raise ValueError("Could not extract table name")
        
        table_name = table_match.group(1)
        
        # Extract columns
        columns_match = re.search(r'INSERT\s+INTO\s+`[^`]+`\s*\(([^)]+)\)\s+VALUES', stmt, re.IGNORECASE | re.DOTALL)
        if not columns_match:
            raise ValueError("Could not extract columns")
        
        columns_str = columns_match.group(1)
        columns = [col.strip().replace('`', '') for col in columns_str.split(',')]
        
        # Extract values part
        values_start = stmt.find('VALUES') + len('VALUES')
        values_part = stmt[values_start:].rstrip(';')
        
        # Parse values using improved method
        data = self.parse_values(values_part)
        
        return table_name, columns, data
    
    def parse_values(self, values_str: str) -> List[List[str]]:
        """Parse the VALUES part of INSERT statement with improved accuracy"""
        values = []
        current_row = []
        current_value = ""
        in_quotes = False
        quote_char = None
        paren_depth = 0
        i = 0
        
        while i < len(values_str):
            char = values_str[i]
            
            # Handle quote tracking
            if char in ("'", '"') and not in_quotes:
                in_quotes = True
                quote_char = char
                current_value += char  # Include the quote
            elif char == quote_char and in_quotes:
                # Check for escaped quotes
                if i + 1 < len(values_str) and values_str[i + 1] == quote_char:
                    current_value += char + values_str[i + 1]  # Include escaped quote
                    i += 2
                    continue
                else:
                    current_value += char  # Include closing quote
                    in_quotes = False
                    quote_char = None
            elif char == '(' and not in_quotes:
                paren_depth += 1
                if paren_depth == 1:
                    # Start of new row
                    current_row = []
                    current_value = ""
                else:
                    current_value += char
            elif char == ')' and not in_quotes:
                paren_depth -= 1
                if paren_depth == 0:
                    # End of row
                    current_row.append(self.convert_value(current_value))
                    values.append(current_row)
                    current_row = []
                    current_value = ""
                else:
                    current_value += char
            elif char == ',' and not in_quotes and paren_depth == 1:
                # End of value in current row
                current_row.append(self.convert_value(current_value))
                current_value = ""
            else:
                current_value += char
            
            i += 1
        
        return values
    
    def convert_value(self, value: str) -> str:
        """Convert MySQL value to clean string"""
        if not value or value.strip() == 'NULL':
            return ''  # Empty string for NULL (CSV will handle this)
        
        value = value.strip()
        
        # Remove quotes if present
        if (value.startswith("'") and value.endswith("'")) or \
           (value.startswith('"') and value.endswith('"')):
            value = value[1:-1]
            # Handle escaped quotes
            value = value.replace("''", "'").replace('""', '"')
        
        return value
    
    def parse_sql_file(self) -> Dict[str, Tuple[List[str], List[List[str]]]]:
        """Parse entire SQL file and extract all INSERT data"""
        logger.info(f"Parsing SQL file: {self.mysql_file}")
        
        with open(self.mysql_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Split into statements
        statements = self.split_sql_statements(content)
        
        # Process INSERT statements
        table_data = {}
        
        for stmt in statements:
            stmt = stmt.strip()
            if not stmt.upper().startswith('INSERT INTO'):
                continue
            
            try:
                table_name, columns, data = self.parse_insert_statement(stmt)
                
                if table_name not in table_data:
                    table_data[table_name] = (columns, data)
                else:
                    # Append data to existing table
                    existing_columns, existing_data = table_data[table_name]
                    if columns != existing_columns:
                        logger.warning(f"Column mismatch for table {table_name}")
                        continue
                    existing_data.extend(data)
                
                logger.info(f"Parsed {len(data)} records for {table_name}")
                
            except Exception as e:
                logger.error(f"Failed to parse statement: {e}")
                logger.error(f"Statement preview: {stmt[:200]}...")
                continue
        
        return table_data
    
    def export_table_to_csv(self, table_name: str, columns: List[str], data: List[List[str]]) -> str:
        """Export table data to CSV file with proper handling for PostgreSQL"""
        csv_file = os.path.join(self.output_dir, f"{table_name}.csv")
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
            
            # Write header
            writer.writerow(columns)
            
            # Write data with proper NULL handling
            for row in data:
                processed_row = []
                for value in row:
                    if value == '' or value is None:
                        processed_row.append('\\N')  # PostgreSQL NULL indicator
                    else:
                        processed_row.append(value)
                writer.writerow(processed_row)
        
        logger.info(f"Exported {len(data)} records to {csv_file}")
        return csv_file
    
    def convert_all_to_csv(self) -> Dict[str, str]:
        """Convert all INSERT statements to CSV files"""
        table_data = self.parse_sql_file()
        csv_files = {}
        
        for table_name, (columns, data) in table_data.items():
            if data:  # Only export if there's data
                csv_file = self.export_table_to_csv(table_name, columns, data)
                csv_files[table_name] = csv_file
        
        logger.info(f"Created {len(csv_files)} CSV files")
        return csv_files
    
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
            if table_name not in csv_files:
                logger.info(f"No CSV file for {table_name}")
                continue
            
            csv_file = csv_files[table_name]
            logger.info(f"Importing {table_name} from {csv_file}")
            
            try:
                # Get column count from CSV header
                with open(csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    columns = next(reader)
                    column_count = len(columns)
                
                # Use COPY command for efficient import with NULL handling
                with open(csv_file, 'r', encoding='utf-8') as f:
                    cursor.copy_expert(
                        f"COPY {table_name} FROM STDIN WITH CSV HEADER NULL AS '\\N'",
                        f
                    )
                
                self.connection.commit()
                
                # Count imported records
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                logger.info(f"Successfully imported {count} records to {table_name}")
                
                # Reset sequence if table has ID column
                if 'id' in columns:
                    self.reset_sequence(cursor, table_name, 'id')
                
            except Exception as e:
                self.connection.rollback()
                logger.error(f"Failed to import {table_name}: {e}")
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
                sequence_name = f"{table_name}_{column_name}_seq"
                cursor.execute(f"ALTER SEQUENCE {sequence_name} RESTART WITH {max_id + 1}")
                self.connection.commit()
                logger.info(f"Reset sequence for {table_name}.{column_name} to {max_id + 1}")
        except Exception as e:
            logger.warning(f"Could not reset sequence for {table_name}: {e}")
    
    def verify_import(self, cursor):
        """Verify the import results"""
        logger.info("Verifying import results...")
        
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
        
        # Check conflicts date range
        try:
            cursor.execute("""
                SELECT 
                    MIN(incidence_date) as earliest,
                    MAX(incidence_date) as latest,
                    COUNT(*) as total
                FROM conflicts
            """)
            result = cursor.fetchone()
            if result[2] > 0:
                logger.info(f"📅 Conflicts data: {result[0]} to {result[1]} ({result[2]:,} total records)")
        except Exception as e:
            logger.error(f"Failed to check conflicts date range: {e}")


def main():
    mysql_file = "/Users/ejikeudeze/AI_Projects/naija-conflict-tracker/u503102722_conflictdb (1).sql"
    connection_string = "postgresql://neondb_owner:npg_bL6dDyw8WEMI@ep-gentle-union-agwmnyzn-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
    
    parser = EnhancedSQLParser(mysql_file)
    
    try:
        # Convert to CSV
        logger.info("🔄 Converting MySQL INSERT statements to CSV...")
        csv_files = parser.convert_all_to_csv()
        
        logger.info(f"📄 Created {len(csv_files)} CSV files:")
        for table, csv_file in csv_files.items():
            # Get record count
            with open(csv_file, 'r') as f:
                lines = sum(1 for _ in f) - 1  # Subtract header
            logger.info(f"  📊 {table}: {lines:,} records")
        
        # Import to PostgreSQL
        logger.info("📥 Importing CSV files to PostgreSQL...")
        parser.import_csv_to_postgres(csv_files, connection_string)
        
        logger.info("🎉 Enhanced MySQL to PostgreSQL conversion completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Conversion failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
