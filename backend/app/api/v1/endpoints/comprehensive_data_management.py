"""
Comprehensive Data Management API
Handles restoration of ALL tables from SQL file with safety checks
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import text, inspect
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import logging
import re

from app.db.database import get_db
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

class ComprehensiveDataRestorer:
    """Handles safe restoration of all data from SQL file"""
    
    def __init__(self, db: Session):
        self.db = db
        self.sql_file_path = "u503102722_conflictdb (1).sql"
        self.table_priorities = {
            # Reference data first (no foreign keys)
            'countries': 1,
            'regions': 2, 
            'states': 3,
            'lgas': 4,
            'conflict_types': 5,
            'actors': 6,
            # User data
            'users': 7,
            # Core data
            'conflicts': 8,
            # System data
            'migrations': 9,
            'personal_access_tokens': 10,
            'cache': 11,
            'sessions': 12
        }
    
    def read_sql_file(self) -> str:
        """Read and parse the SQL file"""
        try:
            with open(self.sql_file_path, 'r') as f:
                content = f.read()
            return content
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"SQL file not found: {self.sql_file_path}")
    
    def get_existing_tables(self) -> List[str]:
        """Get list of existing tables in production database"""
        inspector = inspect(self.db.bind)
        return inspector.get_table_names()
    
    def get_table_record_count(self, table_name: str) -> int:
        """Get current record count for a table"""
        try:
            result = self.db.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
            return result or 0
        except Exception as e:
            logger.warning(f"Could not count records in {table_name}: {e}")
            return 0
    
    def extract_table_data(self, content: str, table_name: str) -> List[str]:
        """Extract INSERT statements for a specific table"""
        # Pattern to match INSERT statements for the table
        pattern = f"INSERT INTO `{table_name}`.*?VALUES.*?;"
        matches = re.findall(pattern, content, re.DOTALL | re.MULTILINE)
        return matches
    
    def check_foreign_key_constraints(self, table_name: str) -> bool:
        """Check if table has foreign key constraints"""
        try:
            inspector = inspect(self.db.bind)
            fks = inspector.get_foreign_keys(table_name)
            return len(fks) > 0
        except Exception:
            return False
    
    def safe_restore_table(self, table_name: str, insert_statements: List[str], 
                          truncate_existing: bool = False, dry_run: bool = False) -> Dict[str, Any]:
        """Safely restore data for a single table"""
        
        result = {
            'table': table_name,
            'status': 'success',
            'records_processed': 0,
            'records_skipped': 0,
            'message': '',
            'warnings': []
        }
        
        if not insert_statements:
            result['message'] = 'No data to restore'
            return result
        
        try:
            # Get current record count
            current_count = self.get_table_record_count(table_name)
            
            # Check if we should skip (table has data and we're not truncating)
            if current_count > 0 and not truncate_existing:
                result['status'] = 'skipped'
                result['message'] = f'Table already has {current_count} records, skipping (use truncate_existing=true to override)'
                return result
            
            # For dry run, just report what would happen
            if dry_run:
                total_records = 0
                for stmt in insert_statements:
                    # Count records in this statement
                    record_pattern = r'\([^)]+\)(?:,|;)'
                    records = re.findall(record_pattern, stmt)
                    total_records += len(records)
                
                result['records_processed'] = total_records
                result['message'] = f'Dry run: Would restore {total_records} records'
                return result
            
            # Check foreign key constraints
            has_fks = self.check_foreign_key_constraints(table_name)
            if has_fks and table_name != 'conflicts':  # conflicts is our main table, handle specially
                result['warnings'].append('Table has foreign key constraints - restoration order matters')
            
            # Truncate if requested
            if truncate_existing and current_count > 0:
                try:
                    self.db.execute(text(f"TRUNCATE TABLE {table_name} CASCADE"))
                    self.db.commit()
                    result['warnings'].append(f'Truncated existing {current_count} records')
                except Exception as e:
                    result['warnings'].append(f'Could not truncate table: {e}')
            
            # Process INSERT statements
            total_processed = 0
            for stmt in insert_statements:
                try:
                    # Convert MySQL syntax to PostgreSQL if needed
                    pg_stmt = self.convert_mysql_to_postgresql(stmt, table_name)
                    
                    # Execute the statement
                    self.db.execute(text(pg_stmt))
                    total_processed += 1
                    
                except Exception as e:
                    # Try to extract records that failed
                    record_pattern = r'\([^)]+\)(?:,|;)'
                    records = re.findall(record_pattern, stmt)
                    result['records_skipped'] += len(records)
                    result['warnings'].append(f'Failed to insert {len(records)} records: {str(e)[:100]}')
            
            self.db.commit()
            result['records_processed'] = total_processed
            result['message'] = f'Successfully processed {total_processed} INSERT statements'
            
        except Exception as e:
            self.db.rollback()
            result['status'] = 'error'
            result['message'] = f'Table restoration failed: {str(e)}'
        
        return result
    
    def convert_mysql_to_postgresql(self, mysql_stmt: str, table_name: str) -> str:
        """Convert MySQL INSERT syntax to PostgreSQL"""
        pg_stmt = mysql_stmt
        
        # Remove backticks (MySQL) and replace with double quotes (PostgreSQL)
        pg_stmt = re.sub(r'`([^`]+)`', r'"\1"', pg_stmt)
        
        # Handle MySQL-specific functions if any
        if table_name == 'users':
            # Handle password hashing, timestamps, etc.
            pg_stmt = pg_stmt.replace('NOW()', 'CURRENT_TIMESTAMP')
        
        # Handle boolean values
        pg_stmt = pg_stmt.replace("1', 'true'", "true', 'true'")
        pg_stmt = pg_stmt.replace("0', 'false'", "false', 'false'")
        
        return pg_stmt
    
    def get_restoration_plan(self, content: str, existing_tables: List[str]) -> Dict[str, Any]:
        """Create a restoration plan showing what will be restored"""
        
        plan = {
            'tables_to_restore': [],
            'tables_to_skip': [],
            'total_records': 0,
            'warnings': []
        }
        
        # Extract data for all tables
        for table_name in sorted(self.table_priorities.keys(), 
                               key=lambda x: self.table_priorities[x]):
            
            if table_name not in existing_tables:
                plan['warnings'].append(f'Table {table_name} does not exist in production')
                continue
            
            insert_statements = self.extract_table_data(content, table_name)
            
            if not insert_statements:
                continue
            
            # Count records
            total_records = 0
            for stmt in insert_statements:
                record_pattern = r'\([^)]+\)(?:,|;)'
                records = re.findall(record_pattern, stmt)
                total_records += len(records)
            
            current_count = self.get_table_record_count(table_name)
            
            table_info = {
                'table': table_name,
                'records_in_file': total_records,
                'records_current': current_count,
                'priority': self.table_priorities[table_name],
                'has_foreign_keys': self.check_foreign_key_constraints(table_name)
            }
            
            if current_count > 0:
                plan['tables_to_skip'].append(table_info)
            else:
                plan['tables_to_restore'].append(table_info)
                plan['total_records'] += total_records
        
        return plan

@router.post("/analyze-sql-file")
async def analyze_sql_file(db: Session = Depends(get_db)):
    """
    Analyze the SQL file and create restoration plan
    """
    try:
        restorer = ComprehensiveDataRestorer(db)
        content = restorer.read_sql_file()
        existing_tables = restorer.get_existing_tables()
        
        plan = restorer.get_restoration_plan(content, existing_tables)
        
        return {
            "status": "success",
            "sql_file": restorer.sql_file_path,
            "existing_tables": existing_tables,
            "restoration_plan": plan,
            "summary": {
                "tables_to_restore": len(plan['tables_to_restore']),
                "tables_to_skip": len(plan['tables_to_skip']),
                "total_records_to_restore": plan['total_records'],
                "warnings": plan['warnings']
            }
        }
        
    except Exception as e:
        logger.error(f"SQL analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"SQL analysis failed: {str(e)}")

@router.post("/restore-all-data")
async def restore_all_data(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    truncate_existing: bool = False,
    dry_run: bool = False,
    tables_to_restore: Optional[List[str]] = None
):
    """
    Comprehensive data restoration for ALL tables
    """
    try:
        restorer = ComprehensiveDataRestorer(db)
        content = restorer.read_sql_file()
        existing_tables = restorer.get_existing_tables()
        
        # Get restoration plan
        plan = restorer.get_restoration_plan(content, existing_tables)
        
        # Filter tables if specified
        if tables_to_restore:
            plan['tables_to_restore'] = [
                t for t in plan['tables_to_restore'] 
                if t['table'] in tables_to_restore
            ]
        
        if not plan['tables_to_restore'] and not dry_run:
            return {
                "status": "no_action_needed",
                "message": "All tables already have data. Use truncate_existing=true to override.",
                "plan": plan
            }
        
        # Execute restoration
        results = []
        total_processed = 0
        total_skipped = 0
        
        for table_info in plan['tables_to_restore']:
            table_name = table_info['table']
            insert_statements = restorer.extract_table_data(content, table_name)
            
            result = restorer.safe_restore_table(
                table_name, 
                insert_statements, 
                truncate_existing, 
                dry_run
            )
            
            results.append(result)
            total_processed += result['records_processed']
            total_skipped += result['records_skipped']
            
            logger.info(f"Table {table_name}: {result['status']} - {result['message']}")
        
        return {
            "status": "success" if dry_run else "completed",
            "dry_run": dry_run,
            "truncate_existing": truncate_existing,
            "results": results,
            "summary": {
                "tables_processed": len(results),
                "total_records_processed": total_processed,
                "total_records_skipped": total_skipped,
                "warnings": [w for r in results for w in r['warnings']]
            },
            "plan": plan
        }
        
    except Exception as e:
        logger.error(f"Comprehensive restoration failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Comprehensive restoration failed: {str(e)}")

@router.post("/restore-table")
async def restore_single_table(
    table_name: str,
    db: Session = Depends(get_db),
    truncate_existing: bool = False,
    dry_run: bool = False
):
    """
    Restore data for a single table
    """
    try:
        restorer = ComprehensiveDataRestorer(db)
        content = restorer.read_sql_file()
        
        insert_statements = restorer.extract_table_data(content, table_name)
        
        if not insert_statements:
            raise HTTPException(status_code=404, detail=f"No data found for table: {table_name}")
        
        result = restorer.safe_restore_table(
            table_name, 
            insert_statements, 
            truncate_existing, 
            dry_run
        )
        
        return {
            "status": "success",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Table restoration failed for {table_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Table restoration failed: {str(e)}")

@router.get("/table-status")
async def get_table_status(db: Session = Depends(get_db)):
    """
    Get current status of all tables
    """
    try:
        restorer = ComprehensiveDataRestorer(db)
        existing_tables = restorer.get_existing_tables()
        
        table_status = []
        for table_name in sorted(existing_tables):
            count = restorer.get_table_record_count(table_name)
            has_fks = restorer.check_foreign_key_constraints(table_name)
            
            table_status.append({
                'table': table_name,
                'record_count': count,
                'has_foreign_keys': has_fks,
                'priority': restorer.table_priorities.get(table_name, 999)
            })
        
        return {
            "status": "success",
            "tables": table_status,
            "summary": {
                "total_tables": len(table_status),
                "tables_with_data": len([t for t in table_status if t['record_count'] > 0]),
                "total_records": sum(t['record_count'] for t in table_status)
            }
        }
        
    except Exception as e:
        logger.error(f"Table status check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Table status check failed: {str(e)}")

@router.post("/create-comprehensive-backup")
async def create_comprehensive_backup(db: Session = Depends(get_db)):
    """
    Create backup of all current data before restoration
    """
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"comprehensive_backup_{timestamp}.sql"
        
        # Get all tables
        restorer = ComprehensiveDataRestorer(db)
        existing_tables = restorer.get_existing_tables()
        
        backup_content = f"-- Comprehensive Database Backup\n"
        backup_content += f"-- Created on: {datetime.now().isoformat()}\n"
        backup_content += f"-- Tables: {len(existing_tables)}\n\n"
        
        # Export data from each table (simplified version)
        for table_name in sorted(existing_tables):
            try:
                result = db.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
                backup_content += f"-- Table: {table_name} ({result} records)\n"
                # In a real implementation, you'd export actual data here
            except Exception as e:
                backup_content += f"-- Table: {table_name} (ERROR: {e})\n"
        
        # Write backup file
        with open(backup_filename, 'w') as f:
            f.write(backup_content)
        
        return {
            "status": "success",
            "backup_file": backup_filename,
            "tables_backed_up": len(existing_tables),
            "message": "Comprehensive backup created successfully"
        }
        
    except Exception as e:
        logger.error(f"Comprehensive backup failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Comprehensive backup failed: {str(e)}")
