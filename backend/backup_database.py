#!/usr/bin/env python3
"""
Database backup utility for migration safety
"""

import os
import sys
from datetime import datetime
import subprocess

def create_database_backup():
    """Create a backup of current database state"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backup_kidnapping_migration_{timestamp}.sql"
    
    print(f"Creating database backup: {backup_file}")
    
    # Try to get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("WARNING: DATABASE_URL not found in environment")
        print("Creating backup file placeholder...")
        
        # Create a placeholder backup file
        with open(backup_file, 'w') as f:
            f.write(f"-- Database Backup Placeholder\n")
            f.write(f"-- Created: {timestamp}\n")
            f.write(f"-- Note: Run manual backup before migration\n")
            f.write(f"-- PostgreSQL command: pg_dump $DATABASE_URL > {backup_file}\n")
        
        print(f"✓ Backup placeholder created: {backup_file}")
        print("⚠️  MANUAL ACTION REQUIRED: Create actual database backup before proceeding")
        return backup_file
    
    # If we have database URL, attempt actual backup
    try:
        # Extract connection details from DATABASE_URL
        # postgresql://user:password@host:port/database
        if database_url.startswith('postgresql://'):
            # Remove protocol prefix
            db_info = database_url.replace('postgresql://', '')
            
            # Split user:password@host:port/database
            if '@' in db_info:
                user_pass, host_db = db_info.split('@', 1)
                if '/' in host_db:
                    host_port, database = host_db.split('/', 1)
                    
                    # Build pg_dump command
                    cmd = [
                        'pg_dump',
                        '--no-password',
                        '--verbose',
                        '--clean',
                        '--no-acl',
                        '--no-owner',
                        '-f', backup_file,
                        database
                    ]
                    
                    # Set environment variables for connection
                    env = os.environ.copy()
                    if ':' in user_pass:
                        user, password = user_pass.split(':', 1)
                        env['PGUSER'] = user
                        env['PGPASSWORD'] = password
                    
                    if ':' in host_port:
                        host, port = host_port.split(':', 1)
                        env['PGHOST'] = host
                        env['PGPORT'] = port
                    else:
                        env['PGHOST'] = host_port
                    
                    print(f"Running: {' '.join(cmd)}")
                    result = subprocess.run(cmd, env=env, capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        print(f"✓ Database backup created: {backup_file}")
                        return backup_file
                    else:
                        print(f"❌ Backup failed: {result.stderr}")
                        return None
    except Exception as e:
        print(f"❌ Backup error: {e}")
        return None
    
    return None

def verify_backup(backup_file):
    """Verify backup file was created and has content"""
    if not os.path.exists(backup_file):
        print(f"❌ Backup file not found: {backup_file}")
        return False
    
    file_size = os.path.getsize(backup_file)
    if file_size == 0:
        print(f"❌ Backup file is empty: {backup_file}")
        return False
    
    print(f"✓ Backup verified: {backup_file} ({file_size} bytes)")
    return True

if __name__ == "__main__":
    print("=== Database Backup for Migration ===")
    
    backup_file = create_database_backup()
    
    if backup_file and verify_backup(backup_file):
        print(f"\n✅ Backup completed successfully")
        print(f"📁 Backup file: {backup_file}")
        print(f"🔄 You can restore with: psql $DATABASE_URL < {backup_file}")
    else:
        print(f"\n❌ Backup failed or incomplete")
        print(f"🚨 DO NOT PROCEED WITH MIGRATION until backup is verified")
        sys.exit(1)
