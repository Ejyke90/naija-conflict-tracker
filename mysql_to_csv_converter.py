#!/usr/bin/env python3
"""
MySQL to PostgreSQL CSV Converter
Uses sqlparse to properly parse SQL and convert INSERT statements to CSV format
for reliable import using PostgreSQL COPY command
"""

import sqlparse
import csv
import os
import re
import psycopg2
from psycopg2 import sql, extras
import logging
from typing import Dict, List, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MySQLToCSVConverter:
    def __init__(self, mysql_file: str, output_dir: str = "csv_exports"):
        self.mysql_file = mysql_file
        self.output_dir = output_dir
        self.connection = None
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
    def parse_sql_file(self) -> List[str]:
        """Parse SQL file into individual statements using sqlparse"""
        logger.info(f"Parsing SQL file: {self.mysql_file}")
        
        with open(self.mysql_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Parse SQL into statements
        statements = sqlparse.parse(content)
        
        # Filter for INSERT statements and clean them up
        insert_statements = []
        for stmt in statements:
            stmt_str = str(stmt).strip()
            if stmt_str.upper().startswith('INSERT INTO'):
                # Remove MySQL comments and clean up
                cleaned_stmt = self.clean_insert_statement(stmt_str)
                if cleaned_stmt:
                    insert_statements.append(cleaned_stmt)
        
        logger.info(f"Found {len(insert_statements)} INSERT statements")
        return insert_statements
    
    def clean_insert_statement(self, stmt: str) -> str:
        """Clean up INSERT statement for parsing"""
        # Remove comments
        lines = stmt.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('--'):
                cleaned_lines.append(line)
        
        return ' '.join(cleaned_lines)
    
    def parse_insert_statement(self, stmt: str) -> Tuple[str, List[str], List[List[str]]]:
        """Parse INSERT statement into table name, columns, and data"""
        # Use regex to extract table name
        table_match = re.search(r'INSERT INTO `([^`]+)`', stmt, re.IGNORECASE)
        if not table_match:
            raise ValueError("Could not extract table name")
        
        table_name = table_match.group(1)
        
        # Use sqlparse to parse the statement
        parsed = sqlparse.parse(stmt)[0]
        
        # Extract columns from the first parenthesis group
        columns = []
        data_rows = []
        
        # Find the column list and VALUES
        tokens = list(parsed.flatten())
        
        in_column_list = False
        in_values = False
        current_row = []
        current_value = ""
        in_quotes = False
        quote_char = None
        paren_depth = 0
        
        i = 0
        while i < len(tokens):
            token = tokens[i]
            token_str = str(token).strip()
            
            # Skip whitespace tokens
            if token.ttype is None and not token_str:
                i += 1
                continue
            
            # Look for column list
            if token_str.upper() == 'INSERT' and i + 1 < len(tokens) and str(tokens[i + 1]).strip().upper() == 'INTO':
                # Skip to table name and opening parenthesis
                i += 2
                while i < len(tokens) and str(tokens[i]).strip() != '(':
                    i += 1
                if i < len(tokens):
                    in_column_list = True
                    i += 1
                continue
            
            # Handle column list
            if in_column_list:
                if token_str == ')':
                    in_column_list = False
                    # Look for VALUES keyword
                    while i < len(tokens) and str(tokens[i]).strip().upper() != 'VALUES':
                        i += 1
                    if i < len(tokens):
                        in_values = True
                        i += 1
                    continue
                elif token_str != ',':
                    # Clean column name (remove backticks)
                    clean_col = token_str.replace('`', '').strip()
                    if clean_col:
                        columns.append(clean_col)
                i += 1
                continue
            
            # Handle VALUES section
            if in_values:
                if token_str == '(':
                    paren_depth += 1
                    if paren_depth == 1:
                        current_row = []
                        current_value = ""
                    i += 1
                    continue
                elif token_str == ')':
                    paren_depth -= 1
                    if paren_depth == 0:
                        # End of row
                        current_row.append(self.convert_value(current_value.strip()))
                        data_rows.append(current_row)
                        current_row = []
                        current_value = ""
                    i += 1
                    continue
                elif token_str == ',' and paren_depth == 1:
                    # End of value in row
                    current_row.append(self.convert_value(current_value.strip()))
                    current_value = ""
                    i += 1
                    continue
                else:
                    # Add to current value
                    if current_value:
                        current_value += " "
                    current_value += token_str
                    i += 1
                    continue
            
            i += 1
        
        return table_name, columns, data_rows
    
    def convert_value(self, value: str) -> str:
        """Convert a single value from MySQL to CSV format"""
        if value == 'NULL' or value == '':
            return ''
        
        # Remove quotes if present
        if (value.startswith("'") and value.endswith("'")) or \
           (value.startswith('"') and value.endswith('"')):
            value = value[1:-1]
            # Handle escaped quotes
            value = value.replace("''", "'").replace('""', '"')
        
        return value
    
    def export_table_to_csv(self, table_name: str, columns: List[str], data: List[List[str]]) -> str:
        """Export table data to CSV file"""
        csv_file = os.path.join(self.output_dir, f"{table_name}.csv")
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow(columns)
            
            # Write data
            for row in data:
                writer.writerow(row)
        
        logger.info(f"Exported {len(data)} records to {csv_file}")
        return csv_file
    
    def convert_all_tables(self) -> Dict[str, str]:
        """Convert all INSERT statements to CSV files"""
        statements = self.parse_sql_file()
        csv_files = {}
        
        for stmt in statements:
            try:
                table_name, columns, data = self.parse_insert_statement(stmt)
                
                if data:  # Only export if there's data
                    csv_file = self.export_table_to_csv(table_name, columns, data)
                    csv_files[table_name] = csv_file
                    
            except Exception as e:
                logger.error(f"Failed to parse statement: {e}")
                logger.error(f"Statement: {stmt[:100]}...")
                continue
        
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
                
                # Use COPY command for efficient import
                with open(csv_file, 'r', encoding='utf-8') as f:
                    cursor.copy_expert(
                        f"COPY {table_name} FROM STDIN WITH CSV HEADER",
                        f
                    )
                
                self.connection.commit()
                logger.info(f"Successfully imported {table_name}")
                
                # Reset sequence if table has ID column
                if 'id' in columns:
                    self.reset_sequence(cursor, table_name, 'id')
                
            except Exception as e:
                self.connection.rollback()
                logger.error(f"Failed to import {table_name}: {e}")
                continue
        
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


def main():
    mysql_file = "/Users/ejikeudeze/AI_Projects/naija-conflict-tracker/u503102722_conflictdb (1).sql"
    connection_string = "postgresql://neondb_owner:npg_bL6dDyw8WEMI@ep-gentle-union-agwmnyzn-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
    
    converter = MySQLToCSVConverter(mysql_file)
    
    try:
        # Convert to CSV
        logger.info("Converting MySQL INSERT statements to CSV...")
        csv_files = converter.convert_all_tables()
        
        logger.info(f"Created {len(csv_files)} CSV files:")
        for table, csv_file in csv_files.items():
            logger.info(f"  {table}: {csv_file}")
        
        # Import to PostgreSQL
        converter.import_csv_to_postgres(csv_files, connection_string)
        
        logger.info("🎉 MySQL to PostgreSQL conversion completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Conversion failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
