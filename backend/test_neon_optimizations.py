#!/usr/bin/env python3
"""
Quick test to verify Neon database optimizations
"""

import time
from app.db.database import engine, SessionLocal
from sqlalchemy import text

def test_neon_optimizations():
    """Test that Neon optimizations are working"""
    print("Testing Neon Database Optimizations")
    print("=" * 40)
    
    # Test 1: Connection speed
    print("\n1. Testing connection speed...")
    start_time = time.time()
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            data = result.fetchone()
        
        connection_time = (time.time() - start_time) * 1000
        print(f"✅ Connection successful: {connection_time:.2f}ms")
        
        if connection_time > 1000:
            print("⚠️ Still slow - may need further optimization")
        else:
            print("✅ Good connection speed")
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return
    
    # Test 2: Pool parameters
    print(f"\n2. Checking pool parameters...")
    pool = engine.pool
    print(f"Pool size: {pool.size()}")
    print(f"Max overflow: {pool.overflow()}")
    
    # Try to get pool status safely
    try:
        status = pool.status()
        print(f"Current connections: {getattr(status, 'checkedin', 'N/A')}")
        print(f"Checked out connections: {getattr(status, 'checkedout', 'N/A')}")
    except (AttributeError, TypeError):
        print("Pool status: Not available (using simple pool)")
        print(f"Pool type: {type(pool)}")
        print(f"Pool attributes: {[attr for attr in dir(pool) if not attr.startswith('_')]}")
    
    # Test 3: Multiple connections
    print(f"\n3. Testing multiple concurrent connections...")
    start_time = time.time()
    
    connections = []
    try:
        for i in range(3):  # Test with small number for Neon
            conn = engine.connect()
            connections.append(conn)
            result = conn.execute(text("SELECT pg_sleep(0.1), 1"))  # Small delay
            result.fetchone()
        
        multi_time = (time.time() - start_time) * 1000
        print(f"✅ 3 concurrent connections: {multi_time:.2f}ms")
        
        # Close connections
        for conn in connections:
            conn.close()
            
    except Exception as e:
        print(f"❌ Multiple connections failed: {e}")
    
    # Test 4: Query performance
    print(f"\n4. Testing query performance...")
    
    queries = [
        ("Simple SELECT", "SELECT 1"),
        ("Version", "SELECT version()"),
        ("Current Time", "SELECT NOW()"),
    ]
    
    for name, query in queries:
        start_time = time.time()
        try:
            with engine.connect() as conn:
                result = conn.execute(text(query))
                data = result.fetchone()
            
            query_time = (time.time() - start_time) * 1000
            status = "✅" if query_time < 500 else "⚠️"
            print(f"{status} {name}: {query_time:.2f}ms")
            
        except Exception as e:
            print(f"❌ {name}: {e}")
    
    print(f"\n5. Summary:")
    print(f"Database URL: {engine.url}")
    print(f"Driver: {engine.driver}")
    print(f"Dialect: {engine.dialect.name}")
    
    # Recommendations
    print(f"\n🔧 Neon Optimization Status:")
    if connection_time < 500:
        print("✅ Connection speed optimized")
    else:
        print("⚠️ Consider further connection optimization")
    
    if pool.size() <= 3:
        print("✅ Pool size optimized for Neon")
    else:
        print("⚠️ Pool size may be too large for Neon")
    
    print(f"\n💡 Neon-specific tips:")
    print(f"- Use small pool sizes (3-5)")
    print(f"- Short connection lifetimes (90-120s)")
    print(f"- Aggressive timeouts (3-8s)")
    print(f"- Let Neon handle connection pooling")

if __name__ == "__main__":
    test_neon_optimizations()
