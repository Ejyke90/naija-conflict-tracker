#!/usr/bin/env python3
"""
Connection Warming System for Neon Database
Pre-warms connections to reduce latency for critical operations
"""

import asyncio
import time
from typing import Dict, Any
from sqlalchemy import create_engine, text
from app.core.config import settings

class ConnectionWarmer:
    """Manages connection warming for optimal performance"""
    
    def __init__(self):
        self.database_url = settings.DATABASE_URL
        self.warm_engine = None
        self.last_warm_time = None
        self.warm_interval = 30  # Warm every 30 seconds
        
    def create_warm_engine(self):
        """Create dedicated engine for warming connections"""
        engine_kwargs = {
            "pool_size": 1,
            "max_overflow": 0,  # No overflow for warming
            "pool_recycle": 30,  # 30 seconds
            "pool_timeout": 2,
            "pool_pre_ping": True,
            "echo": False,
        }
        
        connect_args = {
            "connect_timeout": 1,
            "sslmode": "require",
            "application_name": "naija-tracker-warmer",
        }
        
        return create_engine(self.database_url, **engine_kwargs, connect_args=connect_args)
    
    async def warm_connections(self):
        """Warm up database connections"""
        if not self.warm_engine:
            self.warm_engine = self.create_warm_engine()
        
        print("Warming database connections...")
        start_time = time.time()
        
        try:
            # Create and warm connections
            connections = []
            for i in range(2):  # Warm 2 connections
                conn = self.warm_engine.connect()
                connections.append(conn)
                
                # Execute warmup queries
                warmup_queries = [
                    "SELECT 1",
                    "SELECT version()",
                    "SELECT NOW()",
                ]
                
                for query in warmup_queries:
                    result = conn.execute(text(query))
                    result.fetchone()
                
                print(f"  Connection {i+1} warmed")
            
            # Close connections
            for conn in connections:
                conn.close()
            
            warm_time = (time.time() - start_time) * 1000
            self.last_warm_time = time.time()
            
            print(f"✅ Connections warmed in {warm_time:.2f}ms")
            
        except Exception as e:
            print(f"❌ Warming failed: {e}")
    
    def get_warmed_connection(self):
        """Get a pre-warmed connection for critical operations"""
        if not self.warm_engine:
            self.warm_engine = self.create_warm_engine()
        
        # Check if warming is needed
        if (self.last_warm_time is None or 
            time.time() - self.last_warm_time > self.warm_interval):
            asyncio.create_task(self.warm_connections())
        
        # Return connection from warm pool
        return self.warm_engine.connect()
    
    def test_warmed_performance(self):
        """Test performance with warmed connections"""
        print("Testing warmed connection performance...")
        
        if not self.warm_engine:
            self.warm_engine = self.create_warm_engine()
        
        # First, warm the connections
        asyncio.run(self.warm_connections())
        
        # Test warmed performance
        print("Testing warmed connection speed...")
        times = []
        
        for i in range(5):
            start_time = time.time()
            try:
                with self.get_warmed_connection() as conn:
                    result = conn.execute(text("SELECT 1"))
                    result.fetchone()
                
                conn_time = (time.time() - start_time) * 1000
                times.append(conn_time)
                print(f"  Test {i+1}: {conn_time:.2f}ms")
                
            except Exception as e:
                print(f"  Test {i+1} failed: {e}")
        
        if times:
            avg_time = sum(times) / len(times)
            print(f"✅ Average warmed connection time: {avg_time:.2f}ms")
            
            if avg_time < 600:
                print("🎉 Excellent performance!")
            elif avg_time < 1000:
                print("✅ Good performance")
            else:
                print("⚠️ Still slow - may need further optimization")
        
        return times

def main():
    """Test connection warming system"""
    print("Neon Connection Warming System")
    print("=" * 40)
    
    warmer = ConnectionWarmer()
    
    # Test warming performance
    warmed_times = warmer.test_warmed_performance()
    
    print(f"\n📊 Warming Results:")
    if warmed_times:
        avg_warmed = sum(warmed_times) / len(warmed_times)
        print(f"  Average warmed: {avg_warmed:.2f}ms")
        print(f"  Min warmed: {min(warmed_times):.2f}ms")
        print(f"  Max warmed: {max(warmed_times):.2f}ms")
    
    print(f"\n🔧 Warming Strategy:")
    print(f"  - Warm 2 connections every 30 seconds")
    print(f"  - Use warm pool for critical operations")
    print(f"  - Ultra-aggressive timeouts (1s)")
    print(f"  - Single connection pool (Neon optimized)")
    
    print(f"\n💡 Usage Tips:")
    print(f"  - Call get_warmed_connection() for critical paths")
    print(f"  - Let warming run automatically in background")
    print(f"  - Monitor warm performance regularly")

if __name__ == "__main__":
    main()
