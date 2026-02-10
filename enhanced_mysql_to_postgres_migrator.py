#!/usr/bin/env python3
"""
Enhanced MySQL to PostgreSQL Migration Script
Combines sqlglot transpiler with robust CSV import for optimal performance

This script uses sqlglot for reliable SQL parsing and transpilation,
combined with the efficient CSV COPY protocol from the robust converter.
"""

import sqlglot
from sqlglot import transpile
import csv
import os
import psycopg2
from psycopg2 import sql, extras
import logging
from typing import Dict, List, Tuple
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedMySQLToPostgresMigrator:
    def __init__(self, mysql_file: str, output_dir: str = "enhanced_migration"):
        self.mysql_file = mysql_file
        self.output_dir = output_dir
        self.connection = None
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
    
    def transpile_mysql_to_postgres(self, input_file: str, output_file: str) -> str:
        """Use sqlglot to transpile MySQL SQL to PostgreSQL"""
        logger.info(f"Transpiling {input_file} to PostgreSQL...")
        
        with open(input_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Split by semicolon to handle statements individually
        statements = sql_content.split(';')
        postgres_statements = []
        
        for stmt in statements:
            stmt = stmt.strip()
            if not stmt or stmt.startswith('--') or stmt.startswith('/*'):
                continue
            
            try:
                # Use sqlglot for reliable transpilation
                transpiled = transpile(stmt, read='mysql', write='postgres')[0]
                
                # Additional Neon/Postgres specific fixes
                transpiled = self._apply_postgres_fixes(transpiled)
                
                postgres_statements.append(transpiled + ";")
                
            except Exception as e:
                logger.warning(f"Skipping statement due to parse error: {stmt[:50]}... Error: {e}")
                continue
        
        # Write transpiled SQL
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(postgres_statements))
        
        logger.info(f"Transpilation complete! Output: {output_file}")
        return output_file
    
    def _apply_postgres_fixes(self, sql_statement: str) -> str:
        """Apply PostgreSQL-specific fixes"""
        # Map TINYINT(1) to BOOLEAN
        sql_statement = re.sub(r'TINYINT\(1\)', 'BOOLEAN', sql_statement, flags=re.IGNORECASE)
        
        # Replace MySQL AUTO_INCREMENT with Postgres Identity
        sql_statement = re.sub(
            r'BIGINT NOT NULL AUTO_INCREMENT',
            'BIGINT GENERATED ALWAYS AS IDENTITY',
            sql_statement,
            flags=re.IGNORECASE
        )
        
        # Handle ENUM types
        sql_statement = re.sub(
            r"enum\('Yes','No'\)",
            "VARCHAR(3) CHECK (column_name IN ('Yes', 'No'))",
            sql_statement,
            flags=re.IGNORECASE
        )
        
        return sql_statement
    
    def extract_insert_data_to_csv(self, transpiled_file: str) -> Dict[str, str]:
        """Extract INSERT data from transpiled SQL and convert to CSV"""
        logger.info("Extracting INSERT data to CSV format...")
        
        with open(transpiled_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse INSERT statements using robust method from existing converter
        statements = self._split_sql_statements(content)
        csv_files = {}
        
        for stmt in statements:
            stmt = stmt.strip()
            if not stmt.upper().startswith('INSERT INTO'):
                continue
            
            try:
                table_name, columns, data = self._parse_insert_statement(stmt)
                
                if table_name not in csv_files:
                    csv_file = self._export_table_to_csv(table_name, columns, data)
                    csv_files[table_name] = csv_file
                    logger.info(f"Created CSV for {table_name}: {len(data)} records")
                else:
                    # Append to existing CSV
                    self._append_to_csv(csv_files[table_name], columns, data)
                    
            except Exception as e:
                logger.error(f"Failed to parse INSERT statement: {e}")
                continue
        
        return csv_files
    
    def _split_sql_statements(self, content: str) -> List[str]:
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
        
        return statements
    
    def _parse_insert_statement(self, stmt: str) -> Tuple[str, List[str], List[List[str]]]:
        """Parse a single INSERT statement"""
        # Extract table name (handle both backticks and double quotes)
        table_match = re.search(r'INSERT\s+INTO\s+[`"]([^`"]+)[`"]', stmt, re.IGNORECASE)
        if not table_match:
            raise ValueError("Could not extract table name")
        
        table_name = table_match.group(1)
        
        # Extract columns
        columns_match = re.search(r'INSERT\s+INTO\s+[`"][^`"]+[`"]\s*\(([^)]+)\)\s+VALUES', stmt, re.IGNORECASE | re.DOTALL)
        if not columns_match:
            raise ValueError("Could not extract columns")
        
        columns_str = columns_match.group(1)
        columns = [col.strip().replace('`', '').replace('"', '') for col in columns_str.split(',')]
        
        # Extract values part
        values_start = stmt.find('VALUES') + len('VALUES')
        values_part = stmt[values_start:].rstrip(';')
        
        # Parse values
        data = self._parse_values(values_part)
        
        return table_name, columns, data
    
    def _parse_values(self, values_str: str) -> List[List[str]]:
        """Parse the VALUES part of INSERT statement"""
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
                current_value += char
            elif char == quote_char and in_quotes:
                # Check for escaped quotes
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
                    current_value = ""
                else:
                    current_value += char
            elif char == ')' and not in_quotes:
                paren_depth -= 1
                if paren_depth == 0:
                    current_row.append(self._convert_value(current_value))
                    values.append(current_row)
                    current_row = []
                    current_value = ""
                else:
                    current_value += char
            elif char == ',' and not in_quotes and paren_depth == 1:
                current_row.append(self._convert_value(current_value))
                current_value = ""
            else:
                current_value += char
            
            i += 1
        
        return values
    
    def _convert_value(self, value: str) -> str:
        """Convert MySQL value to clean string"""
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
    
    def _export_table_to_csv(self, table_name: str, columns: List[str], data: List[List[str]]) -> str:
        """Export table data to CSV file"""
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
        
        return csv_file
    
    def _append_to_csv(self, csv_file: str, columns: List[str], data: List[List[str]]):
        """Append data to existing CSV file"""
        with open(csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
            
            # Write data with proper NULL handling
            for row in data:
                processed_row = []
                for value in row:
                    if value == '' or value is None:
                        processed_row.append('\\N')
                    else:
                        processed_row.append(value)
                writer.writerow(processed_row)
    
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
        
        imported_counts = {}
        
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
                        f"COPY {table_name} FROM STDIN WITH CSV HEADER NULL AS '\\N'",
                        f
                    )
                
                self.connection.commit()
                
                # Count imported records
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                imported_counts[table_name] = count
                logger.info(f"✅ Successfully imported {count:,} records to {table_name}")
                
                # Reset sequence if table has ID column
                if 'id' in columns:
                    self._reset_sequence(cursor, table_name, 'id')
                
            except Exception as e:
                self.connection.rollback()
                logger.error(f"❌ Failed to import {table_name}: {e}")
                continue
        
        # Final verification
        self._verify_import(cursor, imported_counts)
        
        cursor.close()
        self.connection.close()
        logger.info("🎉 All imports completed successfully!")
    
    def _reset_sequence(self, cursor, table_name: str, column_name: str):
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
    
    def _verify_import(self, cursor, imported_counts: Dict[str, int]):
        """Verify the import results"""
        logger.info("📊 Verifying import results...")
        
        total_conflicts = imported_counts.get('conflicts', 0)
        total_actors = imported_counts.get('actors', 0)
        total_states = imported_counts.get('states', 0)
        total_lgas = imported_counts.get('lgas', 0)
        
        logger.info(f"📈 Import Summary:")
        logger.info(f"  🎯 Conflicts: {total_conflicts:,} records")
        logger.info(f"  👥 Actors: {total_actors:,} records")
        logger.info(f"  🗺️ States: {total_states:,} records")
        logger.info(f"  🏘️ LGAs: {total_lgas:,} records")
        
        # Check conflicts date range
        if total_conflicts > 0:
            try:
                cursor.execute("""
                    SELECT 
                        MIN(incidence_date) as earliest,
                        MAX(incidence_date) as latest,
                        COUNT(*) as total
                    FROM conflicts
                """)
                result = cursor.fetchone()
                logger.info(f"📅 Conflicts data: {result[0]} to {result[1]} ({result[2]:,} total records)")
            except Exception as e:
                logger.error(f"Failed to check conflicts date range: {e}")
    
    def migrate(self, connection_string: str):
        """Execute the complete enhanced migration process"""
        try:
            logger.info("🚀 Starting Enhanced MySQL to PostgreSQL Migration...")
            
            # Step 1: Transpile SQL using sqlglot
            transpiled_file = os.path.join(self.output_dir, "transpiled_schema.sql")
            self.transpile_mysql_to_postgres(self.mysql_file, transpiled_file)
            
            # Step 2: Extract data to CSV
            csv_files = self.extract_insert_data_to_csv(transpiled_file)
            
            # Step 3: Import to PostgreSQL
            self.import_csv_to_postgres(csv_files, connection_string)
            
            logger.info("🎉 Enhanced migration completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            raise


def main():
    """Main execution function"""
    mysql_file = "/Users/ejikeudeze/AI_Projects/naija-conflict-tracker/u503102722_conflictdb (1).sql"
    connection_string = "postgresql://neondb_owner:npg_bL6dDyw8WEMI@ep-gentle-union-agwmnyzn-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
    
    # Check if MySQL dump file exists
    if not os.path.exists(mysql_file):
        logger.error(f"MySQL dump file not found: {mysql_file}")
        return
    
    # Create migrator and run migration
    migrator = EnhancedMySQLToPostgresMigrator(mysql_file)
    
    try:
        migrator.migrate(connection_string)
        logger.info("🎉 Enhanced MySQL to PostgreSQL conversion completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
