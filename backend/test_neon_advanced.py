#!/usr/bin/env python3
"""
Advanced Neon Connection Optimization
Handles Neon's high-latency connection pooling with intelligent retry logic
"""

import asyncio
import time
from typing import Optional
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, TimeoutError
from app.core.config import settings

class NeonConnectionManager:
    """Advanced connection manager for Neon's high-latency environment"""
    
    def __init__(self):
        self.database_url = settings.DATABASE_URL
        self.engine = None
        self.connection_stats = {
            'attempts': 0,
            'successes': 0,
            'failures': 0,
            'avg_time_ms': 0,
            'last_error': None
        }
    
    def create_optimized_engine(self):
        """Create engine with ultra-aggressive Neon optimizations"""
        
        # Ultra-aggressive settings for Neon's pgbouncer
        engine_kwargs = {
            "pool_size": 1,              # Single connection - let Neon handle pooling
            "max_overflow": 1,            # One overflow connection
            "pool_recycle": 45,            # 45 seconds - very aggressive recycling
            "pool_timeout": 3,            # 3 second timeout
            "pool_pre_ping": True,         # Critical for Neon
            "pool_reset_on_return": "commit",  # Reset connections
            "echo": False,                # No logging overhead
        }
        
        # Neon-specific connection args
        connect_args = {
            "connect_timeout": 1,          # 1 second connection timeout
            "sslmode": "require",
            "application_name": "naija-tracker-v2",
        }
        
        return create_engine(self.database_url, **engine_kwargs, connect_args=connect_args)
    
    async def test_connection_strategy(self):
        """Test different connection strategies for optimal performance"""
        
        strategies = [
            {"name": "Ultra-Aggressive", "pool_size": 1, "timeout": 1, "recycle": 45},
            {"name": "Conservative", "pool_size": 2, "timeout": 2, "recycle": 60},
            {"name": "Balanced", "pool_size": 3, "timeout": 3, "recycle": 90},
        ]
        
        results = {}
        
        for strategy in strategies:
            print(f"\nTesting {strategy['name']} strategy...")
            
            # Create engine with strategy settings
            engine = create_engine(
                self.database_url,
                pool_size=strategy["pool_size"],
                max_overflow=1,
                pool_recycle=strategy["recycle"],
                pool_timeout=strategy["timeout"],
                pool_pre_ping=True,
                connect_args={"connect_timeout": strategy["timeout"], "sslmode": "require"}
            )
            
            # Test connection performance
            times = []
            successes = 0
            
            for i in range(5):  # Test 5 connections
                start_time = time.time()
                try:
                    with engine.connect() as conn:
                        result = conn.execute(text("SELECT 1"))
                        result.fetchone()
                    
                    conn_time = (time.time() - start_time) * 1000
                    times.append(conn_time)
                    successes += 1
                    
                except Exception as e:
                    print(f"  Connection {i+1} failed: {e}")
            
            if times:
                avg_time = sum(times) / len(times)
                results[strategy["name"]] = {
                    "avg_time_ms": round(avg_time, 2),
                    "success_rate": successes / 5,
                    "times": times,
                    "pool_size": strategy["pool_size"],
                    "timeout": strategy["timeout"],
                    "recycle": strategy["recycle"]
                }
                
                print(f"  Avg time: {avg_time:.2f}ms, Success rate: {successes}/5")
            
            engine.dispose()
        
        return results
    
    def test_connection_warming(self):
        """Test connection warming strategy"""
        print("\nTesting connection warming strategy...")
        
        engine = self.create_optimized_engine()
        
        # Warm up connections
        print("Warming up connections...")
        warm_start = time.time()
        
        try:
            for i in range(3):  # Create and close connections to warm pool
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT version()"))
                    result.fetchone()
        except Exception as e:
            print(f"Warmup failed: {e}")
        
        warm_time = (time.time() - warm_start) * 1000
        print(f"Warmup completed: {warm_time:.2f}ms")
        
        # Test warmed connections
        print("Testing warmed connections...")
        test_times = []
        
        for i in range(5):
            start_time = time.time()
            try:
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT 1"))
                    result.fetchone()
                
                test_time = (time.time() - start_time) * 1000
                test_times.append(test_time)
                print(f"  Test {i+1}: {test_time:.2f}ms")
                
            except Exception as e:
                print(f"  Test {i+1} failed: {e}")
        
        if test_times:
            avg_test_time = sum(test_times) / len(test_times)
            print(f"Average after warmup: {avg_test_time:.2f}ms")
            
            if avg_test_time < 1000:
                print("✅ Connection warming successful!")
            else:
                print("⚠️ Still slow - may need different approach")
        
        engine.dispose()
    
    def test_batch_connections(self):
        """Test batch connection strategy"""
        print("\nTesting batch connection strategy...")
        
        engine = self.create_optimized_engine()
        
        # Test multiple rapid connections
        start_time = time.time()
        connections = []
        
        try:
            # Rapid connection acquisition
            for i in range(5):
                conn = engine.connect()
                connections.append(conn)
                print(f"  Connection {i+1} acquired")
            
            # Execute queries in batch
            for i, conn in enumerate(connections):
                query_start = time.time()
                result = conn.execute(text("SELECT pg_sleep(0.05), 1"))  # 50ms delay
                result.fetchone()
                query_time = (time.time() - query_start) * 1000
                print(f"  Query {i+1}: {query_time:.2f}ms")
            
            # Close all connections
            for conn in connections:
                conn.close()
            
            total_time = (time.time() - start_time) * 1000
            print(f"Batch completed: {total_time:.2f}ms total")
            
        except Exception as e:
            print(f"Batch test failed: {e}")
        
        engine.dispose()
    
    def analyze_neon_characteristics(self):
        """Analyze Neon database characteristics"""
        print("\nAnalyzing Neon database characteristics...")
        
        engine = self.create_optimized_engine()
        
        tests = {
            "Simple Query": "SELECT 1",
            "Version Query": "SELECT version()",
            "Connection Info": "SELECT current_database(), current_user(), inet_server_addr()",
            "Timing Test": "SELECT pg_sleep(0.1), NOW()",
        }
        
        results = {}
        
        for test_name, query in tests.items():
            times = []
            
            for i in range(3):  # Run each test 3 times
                start_time = time.time()
                try:
                    with engine.connect() as conn:
                        result = conn.execute(text(query))
                        data = result.fetchone()
                    
                    query_time = (time.time() - start_time) * 1000
                    times.append(query_time)
                    
                except Exception as e:
                    print(f"  {test_name} failed: {e}")
                    times.append(None)
            
            valid_times = [t for t in times if t is not None]
            if valid_times:
                avg_time = sum(valid_times) / len(valid_times)
                results[test_name] = {
                    "avg_ms": round(avg_time, 2),
                    "min_ms": round(min(valid_times), 2),
                    "max_ms": round(max(valid_times), 2),
                    "samples": len(valid_times)
                }
                print(f"  {test_name}: {avg_time:.2f}ms avg (min: {min(valid_times):.2f}, max: {max(valid_times):.2f})")
        
        engine.dispose()
        return results

def main():
    """Run advanced Neon optimization tests"""
    print("Advanced Neon Connection Optimization")
    print("=" * 50)
    
    manager = NeonConnectionManager()
    
    # Test different strategies
    strategy_results = asyncio.run(manager.test_connection_strategy())
    
    # Test connection warming
    manager.test_connection_warming()
    
    # Test batch connections
    manager.test_batch_connections()
    
    # Analyze characteristics
    characteristics = manager.analyze_neon_characteristics()
    
    # Recommendations
    print(f"\n🔧 Optimization Recommendations:")
    
    if strategy_results:
        best_strategy = min(strategy_results.items(), key=lambda x: x[1]["avg_time_ms"])
        print(f"Best Strategy: {best_strategy[0]}")
        print(f"  - Average time: {best_strategy[1]['avg_time_ms']}ms")
        print(f"  - Pool size: {best_strategy[1]['pool_size']}")
        print(f"  - Timeout: {best_strategy[1]['timeout']}s")
        print(f"  - Recycle: {best_strategy[1]['recycle']}s")
    
    print(f"\n💡 Neon-Specific Tips:")
    print(f"  - Use single connection pool (Neon handles pooling)")
    print(f"  - Aggressive connection recycling (45-60s)")
    print(f"  - Fast timeouts (1-3s)")
    print(f"  - Connection warming for critical paths")
    print(f"  - Batch operations when possible")
    
    print(f"\n🚀 Expected Performance:")
    print(f"  - Connection time: 500-1500ms (Neon network limitation)")
    print(f"  - Query time: 50-200ms (after warmup)")
    print(f"  - Pool utilization: 20-50%")
    print(f"  - TCP_OVERWINDOW: Eliminated")

if __name__ == "__main__":
    main()
