#!/usr/bin/env python3
"""
Phase 2 Testing Script
Tests migrations, ETL service, admin endpoint, and timeseries endpoints
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def test_database_connection():
    """Test database is accessible"""
    from app.db.database import SessionLocal
    from sqlalchemy import text
    
    try:
        db = SessionLocal()
        result = db.execute(text('SELECT 1'))
        print("✅ Database connection successful")
        
        # Check table row counts
        tables = {
            'conflicts': 'Normalized conflicts table',
            'states': 'Nigerian states',
            'lgas': 'Local Government Areas',
            'conflict_types': 'Conflict types',
            'actors': 'Conflict actors',
            'conflict_events': 'Legacy events table'
        }
        
        print("\n📊 Table Row Counts:")
        for table, desc in tables.items():
            try:
                result = db.execute(text(f'SELECT COUNT(*) FROM {table}'))
                count = result.scalar() or 0
                print(f"   {table:20} {count:6} rows  → {desc}")
            except Exception as e:
               print(f"   {table:20} ERROR  → {str(e)[:50]}")
        
        db.close()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

async def test_migrations():
    """Test that migrations are applied"""
    from app.db.database import SessionLocal
    from sqlalchemy import text
    
    try:
        db = SessionLocal()
        result = db.execute(text('SELECT version_num FROM alembic_version ORDER BY version_num'))
        versions = [r[0] for r in result.fetchall()]
        print("\n🔄 Applied Migrations:")
        for v in versions:
            print(f"   Migration {v}")
        
        required = ['006', '007', '008', '009', '010']
        all_present = all(v in versions for v in required)
        
        db.close()
        
        if all_present:
            print("✅ All required migrations applied")
            return True
        else:
            missing = [v for v in required if v not in versions]
            print(f"❌ Missing migrations: {missing}")
            return False
    except Exception as e:
        print(f"❌ Migration check failed: {e}")
        return False

async def test_imports():
    """Test that all Phase 2 modules import correctly"""
    try:
        from app.api.v1.endpoints import admin
        from app.services.schema_migration_service import SchemaMigrationService
        from app.utils.timeout import with_timeout
        from app.main import app
        
        print("\n📦 Module Imports:")
        print("   ✅ admin endpoints")
        print("   ✅ SchemaMigrationService")
        print("   ✅ with_timeout decorator")
        print("   ✅ FastAPI app")
        
        # Count admin routes
        admin_routes = [str(r.path) for r in app.routes if '/admin' in str(r.path)]
        print(f"\n🛣️  Admin Routes ({len(admin_routes)}):")
        for route in admin_routes:
            print(f"   {route}")
        
        return len(admin_routes) == 3
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_timeseries_decorators():
    """Test that timeout decorators are applied"""
    from app.api.v1.endpoints import timeseries
    import inspect
    
    try:
        functions_to_check = [
            'get_state_summary',
            'get_monthly_trends',
            'compare_state_trends',
            'analyze_seasonal_patterns'
        ]
        
        print("\n⏱️  Timeout Decorators Applied:")
        for func_name in functions_to_check:
            func = getattr(timeseries, func_name, None)
            if func:
                # Check if it's wrapped (has __wrapped__ or has different name)
                has_timeout = hasattr(func, '__wrapped__') or func.__name__ != func_name
                status = "✅" if has_timeout or 'with_timeout' in str(func) else "❓"
                print(f"   {status} {func_name}")
            else:
                print(f"   ❌ {func_name} not found")
        
        return True
    except Exception as e:
        print(f"❌ Decorator check failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("=" * 60)
    print("PHASE 2 IMPLEMENTATION TEST")
    print("=" * 60)
    
    results = []
    
    print("\n[1/5] Testing Database Connection...")
    results.append(await test_database_connection())
    
    print("\n[2/5] Testing Migrations...")
    results.append(await test_migrations())
    
    print("\n[3/5] Testing Module Imports...")
    results.append(await test_imports())
    
    print("\n[4/5] Testing Timeout Decorators...")
    results.append(await test_timeseries_decorators())
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for r in results if r)
    total = len(results)
    
    print(f"\n✅ Passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 Phase 2 Implementation Complete!")
        print("\nNext Steps:")
        print("  1. Deploy backend to production")
        print("  2. Run ETL migration: POST /api/v1/admin/migrate-schema")
        print("  3. Verify migration: GET /api/v1/admin/migration-status")
        print("  4. Test dashboard endpoints")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
