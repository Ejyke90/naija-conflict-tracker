#!/usr/bin/env python3
"""
MySQL to PostgreSQL Data Migration Script
For Nigeria Conflict Tracker Database Migration to Neon

This script converts and migrates data from MySQL dump to PostgreSQL-compatible format.
Handles large datasets efficiently with batch processing and proper type conversions.
"""

import re
import sys
import psycopg2
from psycopg2 import sql, extras
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MySQLToPostgreSQLConverter:
    def __init__(self, mysql_sql_file: str, postgres_connection_string: str):
        self.mysql_sql_file = mysql_sql_file
        self.postgres_connection_string = postgres_connection_string
        self.pg_connection = None
        self.pg_cursor = None
        
        # Type mappings
        self.type_mappings = {
            'bigint(20) UNSIGNED': 'BIGINT',
            'int(11)': 'INTEGER',
            'int(10) UNSIGNED': 'INTEGER',
            'tinyint(1)': 'BOOLEAN',
            'tinyint(4)': 'SMALLINT',
            'varchar(255)': 'VARCHAR(255)',
            'varchar(45)': 'VARCHAR(45)',
            'varchar(100)': 'VARCHAR(100)',
            'varchar(64)': 'VARCHAR(64)',
            'text': 'TEXT',
            'longtext': 'TEXT',
            'mediumtext': 'TEXT',
            'date': 'DATE',
            'timestamp': 'TIMESTAMP',
            'datetime': 'TIMESTAMP',
            'enum(\'Yes\',\'No\')': 'VARCHAR(3) CHECK (column_name IN (\'Yes\', \'No\'))',
        }
        
        # Table processing order (respecting foreign key dependencies)
        self.table_order = [
            'countries', 'regions', 'states', 'lgas', 
            'actors', 'conflict_types', 'users',
            'conflicts', 'cache', 'cache_locks', 'sessions',
            'migrations', 'failed_jobs', 'jobs', 'job_batches',
            'password_reset_tokens', 'personal_access_tokens'
        ]
    
    def connect_postgres(self):
        """Establish connection to PostgreSQL"""
        try:
            self.pg_connection = psycopg2.connect(self.postgres_connection_string)
            self.pg_connection.autocommit = False
            self.pg_cursor = self.pg_connection.cursor()
            logger.info("Connected to PostgreSQL successfully")
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise
    
    def close_connection(self):
        """Close database connection"""
        if self.pg_cursor:
            self.pg_cursor.close()
        if self.pg_connection:
            self.pg_connection.close()
        logger.info("PostgreSQL connection closed")
    
    def parse_mysql_dump(self) -> Dict[str, Dict[str, Any]]:
        """Parse MySQL dump file and extract table structures and data"""
        logger.info(f"Parsing MySQL dump file: {self.mysql_sql_file}")
        
        with open(self.mysql_sql_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Remove MySQL-specific comments and directives
        content = re.sub(r'^--.*$', '', content, flags=re.MULTILINE)
        content = re.sub(r'^SET .*$', '', content, flags=re.MULTILINE)
        content = re.sub(r'^START TRANSACTION;$', '', content, flags=re.MULTILINE)
        content = re.sub(r'^/\*.*\*/;$', '', content, flags=re.MULTILINE)
        
        # Extract table structures and data
        tables = {}
        current_table = None
        current_section = None
        
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Detect table creation
            if line.startswith('CREATE TABLE'):
                match = re.search(r'CREATE TABLE `([^`]+)`', line)
                if match:
                    current_table = match.group(1)
                    tables[current_table] = {
                        'structure': [],
                        'data': [],
                        'primary_key': None
                    }
                    current_section = 'structure'
                    continue
            
            # Detect INSERT statements
            if line.startswith('INSERT INTO') and current_table:
                current_section = 'data'
                if 'VALUES' in line:
                    # Extract values from INSERT statement
                    values_match = re.search(r'VALUES (.+)$', line)
                    if values_match:
                        values_str = values_match.group(1)
                        # Handle multi-line INSERT statements
                        if not values_str.endswith(';'):
                            # Continue reading until we find the semicolon
                            continue
                        self._parse_insert_values(current_table, values_str, tables)
                continue
            
            # Parse table structure
            if current_section == 'structure' and current_table and line.startswith('`'):
                self._parse_table_structure_line(current_table, line, tables)
            
            # End of table definition
            if line == ');' and current_section == 'structure':
                current_section = None
        
        logger.info(f"Parsed {len(tables)} tables from MySQL dump")
        return tables
    
    def _parse_table_structure_line(self, table_name: str, line: str, tables: Dict):
        """Parse individual table structure line"""
        # Remove backticks and split
        clean_line = line.replace('`', '')
        
        # Extract column definition
        if 'PRIMARY KEY' in clean_line:
            # Extract primary key
            pk_match = re.search(r'PRIMARY KEY \(`([^`]+)`\)', clean_line)
            if pk_match:
                tables[table_name]['primary_key'] = pk_match.group(1)
        elif clean_line and not clean_line.startswith(') ENGINE'):
            parts = clean_line.split(' ', 2)
            if len(parts) >= 2:
                column_name = parts[0]
                column_type = parts[1]
                
                # Handle special cases
                if 'UNSIGNED' in column_type:
                    column_type = column_type.replace(' UNSIGNED', '')
                if 'NOT NULL' in column_type:
                    column_type = column_type.replace(' NOT NULL', '')
                if 'DEFAULT NULL' in column_type:
                    column_type = column_type.replace(' DEFAULT NULL', '')
                
                tables[table_name]['structure'].append({
                    'name': column_name,
                    'type': column_type.strip(),
                    'original_line': line
                })
    
    def _parse_insert_values(self, table_name: str, values_str: str, tables: Dict):
        """Parse INSERT VALUES and convert to Python data types"""
        # Remove trailing semicolon
        values_str = values_str.rstrip(';')
        
        # Split into individual rows
        rows = []
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
                in_quotes = False
                quote_char = None
            elif char == '(' and not in_quotes:
                paren_depth += 1
                if paren_depth == 1:
                    current_row = ""
            elif char == ')' and not in_quotes:
                paren_depth -= 1
                if paren_depth == 0:
                    rows.append(current_row)
                    current_row = ""
                    # Skip comma after row
                    if i + 1 < len(values_str) and values_str[i + 1] == ',':
                        i += 1
                else:
                    current_row += char
            else:
                if paren_depth > 0:
                    current_row += char
            
            i += 1
        
        # Parse each row's values
        for row_str in rows:
            if row_str.strip():
                values = self._parse_row_values(row_str)
                tables[table_name]['data'].append(values)
    
    def _parse_row_values(self, row_str: str) -> List[Any]:
        """Parse individual row values with proper type conversion"""
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
                in_quotes = False
                quote_char = None
            elif char == ',' and not in_quotes:
                # Process the completed value
                values.append(self._convert_value(current_value.strip()))
                current_value = ""
            else:
                current_value += char
            
            i += 1
        
        # Add the last value
        if current_value.strip():
            values.append(self._convert_value(current_value.strip()))
        
        return values
    
    def _convert_value(self, value: str) -> Any:
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
    
    def create_postgresql_tables(self, tables: Dict):
        """Create PostgreSQL tables with converted schema"""
        logger.info("Creating PostgreSQL tables...")
        
        for table_name in self.table_order:
            if table_name not in tables:
                logger.warning(f"Table {table_name} not found in parsed data")
                continue
            
            table_info = tables[table_name]
            
            # Drop table if exists
            drop_sql = sql.SQL("DROP TABLE IF EXISTS {} CASCADE").format(
                sql.Identifier(table_name)
            )
            self.pg_cursor.execute(drop_sql)
            
            # Create table
            columns = []
            for col in table_info['structure']:
                pg_type = self._convert_mysql_type(col['type'], col['name'])
                
                # Handle special cases
                column_def = sql.SQL("{} {}").format(
                    sql.Identifier(col['name']),
                    sql.SQL(pg_type)
                )
                
                # Add primary key if this is the primary key column
                if table_info['primary_key'] == col['name']:
                    column_def = sql.SQL("{} {} PRIMARY KEY").format(
                        sql.Identifier(col['name']),
                        sql.SQL(pg_type)
                    )
                
                columns.append(column_def)
            
            create_sql = sql.SQL("CREATE TABLE {} ({})").format(
                sql.Identifier(table_name),
                sql.SQL(", ").join(columns)
            )
            
            try:
                self.pg_cursor.execute(create_sql)
                logger.info(f"Created table: {table_name}")
            except Exception as e:
                logger.error(f"Failed to create table {table_name}: {e}")
                raise
    
    def _convert_mysql_type(self, mysql_type: str, column_name: str = None) -> str:
        """Convert MySQL data type to PostgreSQL equivalent"""
        # Remove extra specifications
        clean_type = re.sub(r'\(.*?\)', '', mysql_type)
        clean_type = clean_type.replace('UNSIGNED', '').strip()
        
        # Handle ENUM types specifically
        if 'enum' in mysql_type.lower():
            if column_name == 'displaced_persons':
                return f"VARCHAR(3) CHECK ({column_name} IN ('Yes', 'No'))"
            else:
                # Generic ENUM handling - convert to TEXT for now
                logger.warning(f"ENUM column {column_name} converted to TEXT - manual review needed")
                return 'TEXT'
        
        # Apply mappings
        for mysql_pattern, pg_type in self.type_mappings.items():
            if clean_type in mysql_pattern or mysql_pattern in clean_type:
                return pg_type
        
        # Default to TEXT for unknown types
        logger.warning(f"Unknown MySQL type: {mysql_type}, defaulting to TEXT")
        return 'TEXT'
    
    def import_table_data(self, tables: Dict):
        """Import data into PostgreSQL tables"""
        logger.info("Importing table data...")
        
        for table_name in self.table_order:
            if table_name not in tables or not tables[table_name]['data']:
                logger.info(f"No data to import for table: {table_name}")
                continue
            
            table_info = tables[table_name]
            data = table_info['data']
            
            if not data:
                continue
            
            # Get column names
            columns = [col['name'] for col in table_info['structure']]
            
            # Prepare INSERT statement
            insert_sql = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
                sql.Identifier(table_name),
                sql.SQL(", ").join(map(sql.Identifier, columns)),
                sql.SQL(", ").join([sql.Placeholder()] * len(columns))
            )
            
            # Import data in batches
            batch_size = 1000
            total_rows = len(data)
            
            logger.info(f"Importing {total_rows} rows into {table_name}...")
            
            for i in range(0, total_rows, batch_size):
                batch = data[i:i + batch_size]
                
                try:
                    # Use execute_batch for better performance
                    extras.execute_batch(self.pg_cursor, insert_sql, batch)
                    self.pg_connection.commit()
                    
                    logger.info(f"  Imported {min(i + batch_size, total_rows)}/{total_rows} rows")
                    
                except Exception as e:
                    self.pg_connection.rollback()
                    logger.error(f"Failed to import batch for {table_name}: {e}")
                    raise
            
            logger.info(f"Completed import for table: {table_name}")
    
    def reset_sequences(self, tables: Dict):
        """Reset PostgreSQL sequences after manual ID insertion"""
        logger.info("Resetting sequences...")
        
        for table_name in self.table_order:
            if table_name not in tables:
                continue
            
            table_info = tables[table_name]
            if not table_info['data']:
                continue
            
            # Find the primary key column
            pk_column = table_info['primary_key']
            if not pk_column:
                continue
            
            # Get the maximum ID value
            max_id_query = sql.SQL("SELECT MAX({}) FROM {}").format(
                sql.Identifier(pk_column),
                sql.Identifier(table_name)
            )
            
            self.pg_cursor.execute(max_id_query)
            max_id = self.pg_cursor.fetchone()[0]
            
            if max_id:
                # Reset sequence
                sequence_name = f"{table_name}_{pk_column}_seq"
                reset_sql = sql.SQL("ALTER SEQUENCE {} RESTART WITH {}").format(
                    sql.Identifier(sequence_name),
                    sql.Literal(max_id + 1)
                )
                
                try:
                    self.pg_cursor.execute(reset_sql)
                    logger.info(f"Reset sequence for {table_name}.{pk_column} to {max_id + 1}")
                except Exception as e:
                    logger.warning(f"Could not reset sequence for {table_name}: {e}")
        
        self.pg_connection.commit()
    
    def create_indexes(self):
        """Create performance indexes"""
        logger.info("Creating indexes...")
        
        indexes = [
            ("idx_conflicts_incidence_date", "conflicts", "incidence_date"),
            ("idx_conflicts_conflict_type_id", "conflicts", "conflict_type_id"),
            ("idx_conflicts_state_id", "conflicts", "state_id"),
            ("idx_conflicts_lga_id", "conflicts", "lga_id"),
            ("idx_lgas_state_id", "lgas", "state_id"),
            ("idx_states_region_id", "states", "region_id"),
        ]
        
        for index_name, table_name, column_name in indexes:
            try:
                create_index_sql = sql.SQL("CREATE INDEX IF NOT EXISTS {} ON {} ({})").format(
                    sql.Identifier(index_name),
                    sql.Identifier(table_name),
                    sql.Identifier(column_name)
                )
                self.pg_cursor.execute(create_index_sql)
                logger.info(f"Created index: {index_name}")
            except Exception as e:
                logger.warning(f"Could not create index {index_name}: {e}")
        
        self.pg_connection.commit()
    
    def migrate(self):
        """Execute the complete migration process"""
        try:
            logger.info("Starting MySQL to PostgreSQL migration...")
            
            # Connect to PostgreSQL
            self.connect_postgres()
            
            # Parse MySQL dump
            tables = self.parse_mysql_dump()
            
            # Create PostgreSQL tables
            self.create_postgresql_tables(tables)
            
            # Import data
            self.import_table_data(tables)
            
            # Reset sequences
            self.reset_sequences(tables)
            
            # Create indexes
            self.create_indexes()
            
            logger.info("Migration completed successfully!")
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            if self.pg_connection:
                self.pg_connection.rollback()
            raise
        finally:
            self.close_connection()


def main():
    """Main execution function"""
    # Configuration
    mysql_sql_file = "/Users/ejikeudeze/AI_Projects/naija-conflict-tracker/u503102722_conflictdb (1).sql"
    
    # Neon PostgreSQL connection string
    postgres_connection_string = (
        "postgresql://neondb_owner:npg_bL6dDyw8WEMI@"
        "ep-gentle-union-agwmnyzn-pooler.c-2.eu-central-1.aws.neon.tech/"
        "neondb?sslmode=require&channel_binding=require"
    )
    
    # Check if MySQL dump file exists
    if not os.path.exists(mysql_sql_file):
        logger.error(f"MySQL dump file not found: {mysql_sql_file}")
        sys.exit(1)
    
    # Create converter and run migration
    converter = MySQLToPostgreSQLConverter(mysql_sql_file, postgres_connection_string)
    
    try:
        converter.migrate()
        logger.info("🎉 Migration completed successfully!")
        logger.info("Your MySQL data has been migrated to Neon PostgreSQL!")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
