#!/usr/bin/env python3
"""
Validate that the date mapping fix was successful.
"""

import os
import psycopg2

def validate_date_fix():
    """Connect to database and validate the date fix."""
    
    # Production database URL
    db_url = "postgresql://neondb_owner:npg_bL6dDyw8WEMI@ep-gentle-union-agwmnyzn.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
    
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    
    print("=== DATE MAPPING FIX VALIDATION ===\n")
    
    # 1. Basic statistics
    cursor.execute("""
        SELECT 
            COUNT(*) as total_records,
            COUNT(CASE WHEN incidence_date = created_at::date THEN 1 END) as fake_dates,
            COUNT(CASE WHEN incidence_date != created_at::date THEN 1 END) as real_dates,
            MIN(incidence_date) as earliest_date,
            MAX(incidence_date) as latest_date
        FROM conflicts
    """)
    
    total, fake, real, earliest, latest = cursor.fetchone()
    print(f"📊 Basic Statistics:")
    print(f"   Total records: {total}")
    print(f"   Records with real dates: {real}")
    print(f"   Records with fake dates: {fake}")
    print(f"   Date range: {earliest} to {latest}")
    print(f"   Success rate: {(real/total)*100:.1f}%")
    print()
    
    # 2. Year distribution
    cursor.execute("""
        SELECT 
            EXTRACT(YEAR FROM incidence_date) as year,
            COUNT(*) as count
        FROM conflicts 
        WHERE incidence_date IS NOT NULL 
        GROUP BY EXTRACT(YEAR FROM incidence_date)
        ORDER BY year
    """)
    
    years = cursor.fetchall()
    print(f"📅 Year Distribution:")
    for year, count in years:
        print(f"   {int(year)}: {count} incidents")
    print()
    
    # 3. Seasonal patterns (should show realistic patterns)
    cursor.execute("""
        SELECT 
            EXTRACT(MONTH FROM incidence_date) as month,
            COUNT(*) as incident_count,
            AVG(civilian_death_male + civilian_death_female + civilian_death_unknown + 
                security_death_male + security_death_female + security_death_unknown) as avg_fatalities
        FROM conflicts 
        WHERE incidence_date IS NOT NULL 
        GROUP BY EXTRACT(MONTH FROM incidence_date)
        ORDER BY incident_count DESC
        LIMIT 5
    """)
    
    seasonal = cursor.fetchall()
    print(f"🌤️  Top 5 Months by Incidents:")
    for month, count, fatalities in seasonal:
        month_names = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        print(f"   {month_names[int(month)]}: {count} incidents (avg {fatalities:.1f} fatalities)")
    print()
    
    # 4. Sample records to verify
    cursor.execute("""
        SELECT id, incidence_date, created_at,
               incidence_date = created_at::date as is_fake
        FROM conflicts 
        ORDER BY id 
        LIMIT 10
    """)
    
    samples = cursor.fetchall()
    print(f"🔍 Sample Records:")
    for sample in samples:
        id, date, created, is_fake = sample
        status = "❌ FAKE" if is_fake else "✅ REAL"
        print(f"   ID {id}: {date} ({status})")
    print()
    
    # 5. Success criteria check
    print("✅ SUCCESS CRITERIA CHECK:")
    
    criteria_met = 0
    total_criteria = 5
    
    # Criteria 1: All records have correct dates (2020-2025)
    if earliest.year >= 2020 and latest.year <= 2025 and real == total:
        print("   ✅ All records have correct incident dates from 2020-2025")
        criteria_met += 1
    else:
        print("   ❌ Date range or real dates check failed")
    
    # Criteria 2: No fake dates remaining
    if fake == 0:
        print("   ✅ No fake dates (created_at) remaining")
        criteria_met += 1
    else:
        print(f"   ❌ Still have {fake} fake dates")
    
    # Criteria 3: Year distribution looks realistic
    if len(years) >= 4:  # Should have multiple years
        print("   ✅ Realistic year distribution (multiple years represented)")
        criteria_met += 1
    else:
        print("   ❌ Year distribution doesn't look realistic")
    
    # Criteria 4: Seasonal patterns show variation
    if len(seasonal) >= 4:
        print("   ✅ Seasonal analysis shows realistic patterns")
        criteria_met += 1
    else:
        print("   ❌ Seasonal patterns insufficient")
    
    # Criteria 5: Data quality
    if real / total >= 0.95:  # 95% success rate
        print("   ✅ High data quality (>95% real dates)")
        criteria_met += 1
    else:
        print(f"   ❌ Data quality below threshold ({(real/total)*100:.1f}% real dates)")
    
    print(f"\n🎯 OVERALL RESULT: {criteria_met}/{total_criteria} criteria met")
    
    if criteria_met == total_criteria:
        print("🎉 DATE MAPPING FIX COMPLETELY SUCCESSFUL!")
        print("   Historical analysis will now show accurate patterns")
        print("   Monthly trends and seasonal patterns are restored")
        print("   Forecasting will use proper historical baseline")
    else:
        print("⚠️  Some issues remain - review the criteria above")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    validate_date_fix()
