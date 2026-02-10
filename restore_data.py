#!/usr/bin/env python3
"""
Emergency Data Restoration Script
Fast execution to restore complete dataset from SQL file
"""

import requests
import json
import time
import sys

def restore_data():
    """Execute emergency data restoration"""
    
    print("🚨 EMERGENCY DATA RESTORATION")
    print("=" * 50)
    
    # Configuration
    BACKEND_URL = "https://naija-conflict-tracker-production.up.railway.app"
    
    print(f"Target Backend: {BACKEND_URL}")
    print("This will restore the complete dataset from SQL file")
    print()
    
    # Step 1: Check current status
    print("📊 Step 1: Checking current data status...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/data-management/verify-data-integrity")
        if response.status_code == 200:
            current_data = response.json()
            print(f"✅ Current database has {current_data['total_statistics']['total_incidents']} incidents")
            
            # Show yearly breakdown
            print("   Current yearly data:")
            for year_data in current_data['yearly_breakdown']:
                print(f"   {year_data['year']}: {year_data['incidents']} incidents")
        else:
            print(f"❌ Failed to check status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking status: {e}")
        return False
    
    print()
    
    # Step 2: Create backup
    print("💾 Step 2: Creating backup...")
    try:
        response = requests.post(f"{BACKEND_URL}/api/v1/data-management/create-backup")
        if response.status_code == 200:
            backup_result = response.json()
            print(f"✅ Backup created: {backup_result['backup_file']}")
        else:
            print(f"⚠️  Backup creation failed, continuing anyway...")
    except Exception as e:
        print(f"⚠️  Backup creation error: {e}")
    
    print()
    
    # Step 3: Restore data
    print("🔄 Step 3: Restoring complete dataset...")
    print("   This may take several minutes...")
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/data-management/restore-from-sql",
            json={
                "truncate_existing": True,
                "batch_size": 1000
            },
            timeout=300  # 5 minute timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ RESTORATION SUCCESSFUL!")
            print(f"   Total records: {result['total_records']}")
            print(f"   Processed: {result['processed_records']}")
            print(f"   Message: {result['message']}")
        else:
            print(f"❌ RESTORATION FAILED!")
            print(f"   Status: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out - this is normal for large datasets")
        print("   Check the backend logs for completion status")
        return False
    except Exception as e:
        print(f"❌ Restoration error: {e}")
        return False
    
    print()
    
    # Step 4: Verify restoration
    print("🔍 Step 4: Verifying restoration...")
    time.sleep(2)  # Brief pause to allow database to settle
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/data-management/verify-data-integrity")
        if response.status_code == 200:
            new_data = response.json()
            new_total = new_data['total_statistics']['total_incidents']
            
            print(f"✅ Verification complete!")
            print(f"   New total incidents: {new_total}")
            
            # Show yearly breakdown
            print("   Restored yearly data:")
            for year_data in new_data['yearly_breakdown']:
                print(f"   {year_data['year']}: {year_data['incidents']} incidents")
            
            # Check if restoration worked
            if new_total > 1000:
                print("🎉 RESTORATION SUCCESSFUL - Database now has complete dataset!")
                return True
            else:
                print("⚠️  Restoration may not have completed fully")
                return False
        else:
            print(f"❌ Verification failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False

def check_dashboard():
    """Check if dashboard is working with restored data"""
    print()
    print("📈 Step 5: Testing dashboard endpoints...")
    
    BACKEND_URL = "https://naija-conflict-tracker-production.up.railway.app"
    
    try:
        # Test monthly trends
        response = requests.get(f"{BACKEND_URL}/api/v1/timeseries/monthly-trends?months_back=12")
        if response.status_code == 200:
            trends_data = response.json()
            print(f"✅ Monthly trends working: {trends_data['summary']['totalIncidents']} incidents in last year")
        else:
            print(f"❌ Monthly trends failed: {response.status_code}")
        
        # Test dashboard data
        response = requests.get(f"{BACKEND_URL}/api/v1/data-management/dashboard-data?months_back=12")
        if response.status_code == 200:
            dashboard_data = response.json()
            print(f"✅ Dashboard data working: {dashboard_data['summary']['total_incidents']} incidents")
        else:
            print(f"❌ Dashboard data failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Dashboard test error: {e}")

if __name__ == "__main__":
    print("NIGERIA CONFLICT TRACKER - EMERGENCY DATA RESTORATION")
    print("=" * 60)
    print()
    
    # Confirm execution
    if len(sys.argv) > 1 and sys.argv[1] == "--confirm":
        success = restore_data()
        if success:
            check_dashboard()
        
        print()
        if success:
            print("🎉 RESTORATION PROCESS COMPLETED!")
            print("   The Monthly Trends chart should now show complete data")
            print("   Check the frontend dashboard to verify the fix")
        else:
            print("❌ RESTORATION PROCESS FAILED!")
            print("   Check backend logs and try manual restoration via the API")
    else:
        print("⚠️  WARNING: This will replace all current database data")
        print("   Make sure you have backups before proceeding")
        print()
        print("To execute restoration, run:")
        print("   python3 restore_data.py --confirm")
        print()
        print("To cancel, press Ctrl+C")
