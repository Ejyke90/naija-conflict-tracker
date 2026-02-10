#!/usr/bin/env python3
"""
Comprehensive Data Restoration Script
Restores ALL tables from SQL file with safety checks
"""

import requests
import json
import time
import sys

def analyze_sql_file():
    """Analyze the SQL file and show restoration plan"""
    
    print("🔍 ANALYZING COMPREHENSIVE DATA RESTORATION")
    print("=" * 60)
    
    BACKEND_URL = "https://naija-conflict-tracker-production.up.railway.app"
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/comprehensive-data/analyze-sql-file")
        
        if response.status_code == 200:
            analysis = response.json()
            
            print(f"📁 SQL File: {analysis['sql_file']}")
            print(f"🗄️  Existing Tables: {len(analysis['existing_tables'])}")
            print()
            
            plan = analysis['restoration_plan']
            summary = analysis['summary']
            
            print("📊 RESTORATION PLAN:")
            print(f"   Tables to Restore: {summary['tables_to_restore']}")
            print(f"   Tables to Skip: {summary['tables_to_skip']}")
            print(f"   Total Records: {summary['total_records_to_restore']:,}")
            print()
            
            if plan['tables_to_restore']:
                print("🔄 Tables that will be restored:")
                for table in plan['tables_to_restore']:
                    print(f"   • {table['table']}: {table['records_in_file']} records (Priority: {table['priority']})")
            
            if plan['tables_to_skip']:
                print()
                print("⏭️  Tables that will be skipped (already have data):")
                for table in plan['tables_to_skip']:
                    print(f"   • {table['table']}: {table['records_current']} existing records")
            
            if summary['warnings']:
                print()
                print("⚠️  Warnings:")
                for warning in summary['warnings']:
                    print(f"   • {warning}")
            
            return analysis
            
        else:
            print(f"❌ Analysis failed: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"❌ Error analyzing SQL file: {e}")
        return None

def get_current_table_status():
    """Get current status of all tables"""
    
    print("📋 CURRENT TABLE STATUS")
    print("=" * 40)
    
    BACKEND_URL = "https://naija-conflict-tracker-production.up.railway.app"
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/comprehensive-data/table-status")
        
        if response.status_code == 200:
            status = response.json()
            
            print(f"Total Tables: {status['summary']['total_tables']}")
            print(f"Tables with Data: {status['summary']['tables_with_data']}")
            print(f"Total Records: {status['summary']['total_records']:,}")
            print()
            
            print("Table Details:")
            for table in sorted(status['tables'], key=lambda x: x['priority']):
                status_icon = "✅" if table['record_count'] > 0 else "❌"
                fk_icon = "🔗" if table['has_foreign_keys'] else "📄"
                print(f"   {status_icon} {fk_icon} {table['table']:15}: {table['record_count']:6,} records")
            
            return status
            
        else:
            print(f"❌ Status check failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error checking table status: {e}")
        return None

def dry_run_restoration():
    """Perform a dry run of the restoration"""
    
    print("🧪 DRY RUN - SIMULATING RESTORATION")
    print("=" * 50)
    
    BACKEND_URL = "https://naija-conflict-tracker-production.up.railway.app"
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/comprehensive-data/restore-all-data",
            json={
                "dry_run": True,
                "truncate_existing": False
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print("🎯 Dry Run Results:")
            print(f"   Status: {result['status']}")
            print(f"   Tables Processed: {result['summary']['tables_processed']}")
            print(f"   Records to Restore: {result['summary']['total_records_processed']:,}")
            print(f"   Records to Skip: {result['summary']['total_records_skipped']:,}")
            
            if result['summary']['warnings']:
                print()
                print("⚠️  Warnings:")
                for warning in result['summary']['warnings'][:5]:  # Show first 5 warnings
                    print(f"   • {warning}")
                if len(result['summary']['warnings']) > 5:
                    print(f"   ... and {len(result['summary']['warnings']) - 5} more")
            
            print()
            print("📋 Per-Table Results:")
            for table_result in result['results']:
                status_icon = "✅" if table_result['status'] == 'success' else "⚠️"
                print(f"   {status_icon} {table_result['table']}: {table_result['message']}")
            
            return result
            
        else:
            print(f"❌ Dry run failed: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"❌ Error during dry run: {e}")
        return None

def execute_restoration(truncate_existing=False):
    """Execute the actual restoration"""
    
    print("🚀 EXECUTING COMPREHENSIVE DATA RESTORATION")
    print("=" * 60)
    
    if truncate_existing:
        print("⚠️  WARNING: truncate_existing=True - This will DELETE existing data!")
    else:
        print("ℹ️  Safe mode: Will only restore to empty tables")
    
    print()
    
    BACKEND_URL = "https://naija-conflict-tracker-production.up.railway.app"
    
    try:
        print("🔄 Starting restoration...")
        response = requests.post(
            f"{BACKEND_URL}/api/v1/comprehensive-data/restore-all-data",
            json={
                "dry_run": False,
                "truncate_existing": truncate_existing
            },
            timeout=300  # 5 minute timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ RESTORATION COMPLETED!")
            print(f"   Status: {result['status']}")
            print(f"   Tables Processed: {result['summary']['tables_processed']}")
            print(f"   Records Restored: {result['summary']['total_records_processed']:,}")
            print(f"   Records Skipped: {result['summary']['total_records_skipped']:,}")
            
            if result['summary']['warnings']:
                print()
                print("⚠️  Warnings during restoration:")
                for warning in result['summary']['warnings']:
                    print(f"   • {warning}")
            
            print()
            print("📋 Per-Table Results:")
            for table_result in result['results']:
                if table_result['status'] == 'success':
                    print(f"   ✅ {table_result['table']}: {table_result['records_processed']} statements processed")
                elif table_result['status'] == 'skipped':
                    print(f"   ⏭️  {table_result['table']}: {table_result['message']}")
                else:
                    print(f"   ❌ {table_result['table']}: {table_result['message']}")
            
            return True
            
        else:
            print(f"❌ RESTORATION FAILED!")
            print(f"   Status: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out - restoration may still be running")
        print("   Check the backend logs for completion status")
        return False
    except Exception as e:
        print(f"❌ Restoration error: {e}")
        return False

def verify_restoration():
    """Verify the restoration was successful"""
    
    print()
    print("🔍 VERIFYING RESTORATION RESULTS")
    print("=" * 40)
    
    # Get updated table status
    status = get_current_table_status()
    
    if status:
        print()
        print("🎯 RESTORATION VERIFICATION:")
        
        # Check key tables
        key_tables = ['conflicts', 'states', 'lgas', 'users', 'actors', 'conflict_types']
        
        for table_name in key_tables:
            table_info = next((t for t in status['tables'] if t['table'] == table_name), None)
            if table_info:
                if table_info['record_count'] > 0:
                    print(f"   ✅ {table_name}: {table_info['record_count']:,} records")
                else:
                    print(f"   ❌ {table_name}: Still empty")
        
        # Test monthly trends endpoint
        print()
        print("📈 Testing Monthly Trends API:")
        try:
            BACKEND_URL = "https://naija-conflict-tracker-production.up.railway.app"
            response = requests.get(f"{BACKEND_URL}/api/v1/timeseries/monthly-trends?months_back=12")
            
            if response.status_code == 200:
                trends_data = response.json()
                total_incidents = trends_data['summary']['totalIncidents']
                avg_incidents = trends_data['summary']['avgIncidentsPerMonth']
                
                print(f"   ✅ Monthly Trends: {total_incidents} total incidents")
                print(f"   ✅ Average per month: {avg_incidents}")
                
                if total_incidents > 1000:
                    print("   🎉 MONTHLY TRENDS ISSUE FIXED!")
                else:
                    print("   ⚠️  Monthly Trends still showing low numbers")
                    
            else:
                print(f"   ❌ Monthly Trends API failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error testing Monthly Trends: {e}")

def main():
    """Main execution flow"""
    
    print("🗄️  NIGERIA CONFLICT TRACKER - COMPREHENSIVE DATA RESTORATION")
    print("=" * 70)
    print()
    
    # Step 1: Analyze SQL file
    analysis = analyze_sql_file()
    if not analysis:
        print("❌ Cannot proceed without successful analysis")
        return False
    
    print()
    input("Press Enter to continue to current status check...")
    
    # Step 2: Check current status
    get_current_table_status()
    
    print()
    input("Press Enter to continue to dry run...")
    
    # Step 3: Dry run
    dry_run_result = dry_run_restoration()
    if not dry_run_result:
        print("❌ Cannot proceed without successful dry run")
        return False
    
    print()
    # Step 4: Ask for confirmation
    print("🚨 READY FOR ACTUAL RESTORATION")
    print("=" * 40)
    print("This will restore ALL data from the SQL file to the production database.")
    print()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--confirm":
            truncate = "--truncate" in sys.argv
            success = execute_restoration(truncate_existing=truncate)
            
            if success:
                verify_restoration()
            
            return success
        elif sys.argv[1] == "--help":
            print("Usage:")
            print("  python3 comprehensive_restore.py --confirm")
            print("  python3 comprehensive_restore.py --confirm --truncate")
            print("  python3 comprehensive_restore.py --help")
            return False
        else:
            print(f"Unknown argument: {sys.argv[1]}")
            return False
    else:
        print("To execute restoration, run:")
        print("  python3 comprehensive_restore.py --confirm")
        print("  python3 comprehensive_restore.py --confirm --truncate  # Deletes existing data")
        print()
        print("To cancel, press Ctrl+C")
        return False

if __name__ == "__main__":
    main()
