#!/usr/bin/env python3
"""
Monthly Trends Performance Monitor
Tracks API performance improvements and provides diagnostics
"""

import asyncio
import time
import json
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

class MonthlyTrendsMonitor:
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL', 'postgresql://user:pass@localhost/db')
        self.engine = create_engine(self.db_url)
        
    async def test_query_performance(self, query_name: str, query: str, params: dict = None):
        """Test a specific query's performance"""
        with self.engine.connect() as conn:
            start_time = time.time()
            
            # Run EXPLAIN ANALYZE to get detailed performance metrics
            explain_query = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}"
            result = conn.execute(text(explain_query), params or {}).scalar()
            
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000
            
            if result:
                plan = result[0]['Plan']
                execution_time = plan.get('Execution Time', 0)
                planning_time = plan.get('Planning Time', 0)
                total_cost = plan.get('Total Cost', 0)
                
                return {
                    'query_name': query_name,
                    'total_duration_ms': duration_ms,
                    'execution_time_ms': execution_time,
                    'planning_time_ms': planning_time,
                    'total_cost': total_cost,
                    'uses_index': 'Index' in plan.get('Node Type', '') or plan.get('Index Name'),
                    'index_name': plan.get('Index Name'),
                    'rows_processed': plan.get('Actual Rows', 0)
                }
            
            return None
    
    async def run_performance_tests(self):
        """Run comprehensive performance tests"""
        print("🔍 Monthly Trends Performance Monitor")
        print("=" * 50)
        
        tests = [
            {
                'name': 'Materialized View (Optimized)',
                'query': """
                    SELECT 
                        month,
                        SUM(count) as incidents,
                        SUM(fatalities) as fatalities
                    FROM monthly_trends_view
                    WHERE month >= CURRENT_DATE - INTERVAL '12 months'
                    GROUP BY month
                    ORDER BY month
                    LIMIT 24
                """
            },
            {
                'name': 'Materialized View (State-Specific)',
                'query': """
                    SELECT 
                        mts.month,
                        SUM(mts.count) as incidents,
                        SUM(mts.fatalities) as fatalities
                    FROM monthly_trends_view mts
                    JOIN states s ON mts.state_id = s.id
                    WHERE s.name = :state
                    AND mts.month >= CURRENT_DATE - INTERVAL '12 months'
                    GROUP BY mts.month
                    ORDER BY mts.month
                    LIMIT 24
                """,
                'params': {'state': 'Borno'}
            },
            {
                'name': 'Conflict Events View (Original)',
                'query': """
                    SELECT 
                        DATE_TRUNC('month', event_date) as month,
                        COUNT(*) as incidents,
                        COALESCE(SUM(fatalities), 0) as fatalities
                    FROM conflict_events
                    WHERE event_date >= CURRENT_DATE - INTERVAL '12 months'
                    GROUP BY DATE_TRUNC('month', event_date)
                    ORDER BY month
                    LIMIT 24
                """
            },
            {
                'name': 'Direct Conflicts Table (Indexed)',
                'query': """
                    SELECT 
                        DATE_TRUNC('month', incidence_date) as month,
                        COUNT(*) as incidents,
                        COALESCE(SUM(civilian_death_male + civilian_death_female + civilian_death_unknown + 
                            security_death_male + security_death_female + security_death_unknown), 0) as fatalities
                    FROM conflicts
                    WHERE incidence_date >= CURRENT_DATE - INTERVAL '12 months'
                    GROUP BY DATE_TRUNC('month', incidence_date)
                    ORDER BY month
                    LIMIT 24
                """
            }
        ]
        
        results = []
        
        for test in tests:
            print(f"\n📊 Testing: {test['name']}")
            result = await self.test_query_performance(
                test['name'], 
                test['query'], 
                test.get('params')
            )
            
            if result:
                results.append(result)
                
                # Performance classification
                duration = result['execution_time_ms']
                if duration < 50:
                    performance = "🟢 Excellent (< 50ms)"
                elif duration < 200:
                    performance = "🟡 Good (< 200ms)"
                elif duration < 1000:
                    performance = "🟠 Acceptable (< 1s)"
                else:
                    performance = "🔴 Slow (> 1s)"
                
                print(f"   Execution Time: {duration:.2f}ms {performance}")
                print(f"   Planning Time: {result['planning_time_ms']:.2f}ms")
                print(f"   Total Cost: {result['total_cost']}")
                print(f"   Uses Index: {'✓' if result['uses_index'] else '✗'}")
                if result['index_name']:
                    print(f"   Index: {result['index_name']}")
                print(f"   Rows Processed: {result['rows_processed']:,}")
            else:
                print("   ❌ Query failed")
        
        # Summary
        print("\n" + "=" * 50)
        print("📈 PERFORMANCE SUMMARY")
        print("=" * 50)
        
        if results:
            fastest = min(results, key=lambda x: x['execution_time_ms'])
            slowest = max(results, key=lambda x: x['execution_time_ms'])
            
            print(f"Fastest: {fastest['query_name']} ({fastest['execution_time_ms']:.2f}ms)")
            print(f"Slowest: {slowest['query_name']} ({slowest['execution_time_ms']:.2f}ms)")
            
            # Performance improvement calculation
            original_view = next((r for r in results if 'Original' in r['query_name']), None)
            materialized_view = next((r for r in results if 'Optimized' in r['query_name']), None)
            
            if original_view and materialized_view:
                original_time = original_view['execution_time_ms']
                materialized_time = materialized_view['execution_time_ms']
                
                if original_time > 0:
                    improvement = (original_time - materialized_time) / original_time * 100
                    speedup = original_time / materialized_time if materialized_time > 0 else float('inf')
                else:
                    improvement = 0
                    speedup = 1
                
                print(f"\n🚀 Optimization Results:")
                print(f"   Performance Improvement: {improvement:.1f}%")
                print(f"   Speedup Factor: {speedup:.1f}x")
                
                if speedup > 10:
                    print("   🎯 EXCELLENT: >10x speedup achieved!")
                elif speedup > 5:
                    print("   ✅ GREAT: >5x speedup achieved!")
                elif speedup > 2:
                    print("   ⚡ GOOD: >2x speedup achieved!")
                else:
                    print("   📈 MODERATE: Some improvement achieved")
        
        return results
    
    async def check_cache_status(self):
        """Check Redis cache status"""
        print("\n🗄️  CACHE STATUS")
        print("-" * 30)
        
        try:
            from app.core.cache import get_cache_stats
            stats = await get_cache_stats()
            
            if stats.get('status') == 'connected':
                print(f"✓ Redis Connected")
                print(f"  Keys: {stats.get('keys', 0):,}")
                print(f"  Hit Rate: {stats.get('hit_rate', 0):.1f}%")
                print(f"  Hits: {stats.get('hits', 0):,}")
                print(f"  Misses: {stats.get('misses', 0):,}")
            else:
                print("✗ Redis Disconnected")
                print(f"  Status: {stats.get('status')}")
                
        except Exception as e:
            print(f"✗ Cache check failed: {e}")
    
    async def check_indexes(self):
        """Check if performance indexes exist"""
        print("\n📚 INDEX STATUS")
        print("-" * 30)
        
        with self.engine.connect() as conn:
            # Check conflicts table indexes
            result = conn.execute(text("""
                SELECT indexname, indexdef 
                FROM pg_indexes 
                WHERE tablename = 'conflicts'
                ORDER BY indexname
            """)).fetchall()
            
            expected_indexes = [
                'idx_conflicts_incidence_date',
                'idx_conflicts_monthly_trends', 
                'idx_conflicts_state_id'
            ]
            
            existing_indexes = [row[0] for row in result]
            
            for expected in expected_indexes:
                if expected in existing_indexes:
                    print(f"✓ {expected}")
                else:
                    print(f"✗ {expected} (MISSING)")
            
            # Check materialized view
            try:
                result = conn.execute(text("""
                    SELECT COUNT(*) FROM monthly_trends_view
                """)).scalar()
                print(f"✓ Materialized View ({result:,} rows)")
            except:
                print("✗ Materialized View (MISSING)")
    
    async def generate_report(self):
        """Generate comprehensive performance report"""
        print(f"\n📋 PERFORMANCE REPORT")
        print(f"Generated: {datetime.now().isoformat()}")
        print("=" * 50)
        
        # Run all tests
        results = await self.run_performance_tests()
        await self.check_indexes()
        await self.check_cache_status()
        
        # Recommendations
        print("\n💡 RECOMMENDATIONS")
        print("-" * 30)
        
        if results:
            avg_time = sum(r['execution_time_ms'] for r in results) / len(results)
            
            if avg_time < 100:
                print("✅ Performance is excellent")
                print("   - Current optimizations are working well")
                print("   - Consider increasing cache TTL for better hit rates")
            elif avg_time < 500:
                print("⚡ Performance is good")
                print("   - Monitor for performance degradation")
                print("   - Consider materialized view refresh optimization")
            else:
                print("🔍 Performance needs attention")
                print("   - Review missing indexes")
                print("   - Check materialized view refresh schedule")
                print("   - Consider query optimization")
        
        print("\n🔄 MAINTENANCE TASKS")
        print("-" * 30)
        print("• Refresh materialized view: POST /api/v1/timeseries/refresh-materialized-view")
        print("• Monitor cache hit rates: GET /api/v1/cache/stats")
        print("• Schedule view refresh: Every 30 minutes via cron")
        print("• Monitor query performance: Run this script weekly")


async def main():
    monitor = MonthlyTrendsMonitor()
    await monitor.generate_report()


if __name__ == "__main__":
    asyncio.run(main())
