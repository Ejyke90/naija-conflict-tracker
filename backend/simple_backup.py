#!/usr/bin/env python3
"""
Simple database backup that handles connection strings properly
"""

import os
import subprocess
from datetime import datetime

def create_simple_backup():
    """Create backup using environment variables directly"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backup_kidnapping_migration_{timestamp}.sql"
    
    print(f"=== Creating Database Backup ===")
    print(f"Backup file: {backup_file}")
    
    # Get database connection details from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found")
        return None
    
    print(f"Database URL found: {database_url[:50]}...")
    
    # Parse DATABASE_URL manually
    try:
        # Expected format: postgresql://user:password@host:port/database?sslmode=require
        if database_url.startswith('postgresql://'):
            # Remove protocol
            clean_url = database_url.replace('postgresql://', '')
            
            # Split user:password@host:port/database
            if '@' in clean_url:
                user_pass, host_db = clean_url.split('@', 1)
                
                # Split host:port/database
                if '/' in host_db:
                    host_port, db_with_params = host_db.split('/', 1)
                    
                    # Remove URL parameters from database name
                    database = db_with_params.split('?')[0]
                    
                    # Extract user and password
                    if ':' in user_pass:
                        user, password = user_pass.split(':', 1)
                    else:
                        user = user_pass
                        password = ''
                    
                    # Extract host and port
                    if ':' in host_port:
                        host, port = host_port.split(':', 1)
                    else:
                        host = host_port
                        port = '5432'
                    
                    print(f"Host: {host}")
                    print(f"Port: {port}")
                    print(f"Database: {database}")
                    print(f"User: {user}")
                    
                    # Build pg_dump command with explicit parameters
                    cmd = [
                        'pg_dump',
                        f'--host={host}',
                        f'--port={port}',
                        f'--username={user}',
                        f'--dbname={database}',
                        '--no-password',
                        '--verbose',
                        '--clean',
                        '--no-acl',
                        '--no-owner',
                        '-f', backup_file
                    ]
                    
                    # Set environment variables
                    env = os.environ.copy()
                    env['PGPASSWORD'] = password
                    
                    print(f"Running: pg_dump --host={host} --port={port} --username={user} --dbname={database}")
                    
                    result = subprocess.run(cmd, env=env, capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        # Check if backup file was created and has content
                        if os.path.exists(backup_file) and os.path.getsize(backup_file) > 0:
                            print(f"✅ Backup created successfully")
                            print(f"📁 File: {backup_file}")
                            print(f"📊 Size: {os.path.getsize(backup_file)} bytes")
                            return backup_file
                        else:
                            print(f"❌ Backup file is empty or missing")
                            return None
                    else:
                        print(f"❌ pg_dump failed:")
                        print(f"Error: {result.stderr}")
                        return None
                else:
                    print("❌ Could not parse host/database from URL")
                    return None
            else:
                print("❌ Could not parse user/host from URL")
                return None
    except Exception as e:
        print(f"❌ Backup error: {e}")
        return None

if __name__ == "__main__":
    backup_file = create_simple_backup()
    
    if backup_file:
        print(f"\n✅ BACKUP SUCCESSFUL")
        print(f"🔄 To restore: psql --host=<host> --username=<user> --dbname=<database> < {backup_file}")
    else:
        print(f"\n❌ BACKUP FAILED")
        print(f"🚨 DO NOT PROCEED WITH MIGRATION")
        exit(1)
