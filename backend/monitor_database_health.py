#!/usr/bin/env python3
"""
Database Connection Health Monitor for High-Latency Environments
Tests TCP_OVERWINDOW issues and connection pool performance
"""

import asyncio
import time
import psutil
import socket
from typing import Dict, List, Any
from datetime import datetime, timedelta
import logging

# Database imports
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, DatabaseError, TimeoutError
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseHealthMonitor:
    """Monitor database connection health and detect TCP_OVERWINDOW issues"""
    
    def __init__(self):
        self.database_url = settings.DATABASE_URL
        self.results = {}
        
    def test_tcp_connection(self, host: str, port: int, timeout: int = 5) -> Dict[str, Any]:
        """Test basic TCP connectivity to database server"""
        result = {
            "host": host,
            "port": port,
            "success": False,
            "error": None,
            "connect_time_ms": 0
        }
        
        try:
            start_time = time.time()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            
            sock.connect((host, port))
            connect_time = (time.time() - start_time) * 1000
            
            result.update({
                "success": True,
                "connect_time_ms": round(connect_time, 2)
            })
            
            sock.close()
            
        except socket.timeout:
            result["error"] = f"Connection timeout after {timeout}s"
        except socket.gaierror:
            result["error"] = "DNS resolution failed"
        except ConnectionRefusedError:
            result["error"] = "Connection refused"
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def parse_database_url(self) -> Dict[str, str]:
        """Parse database URL to extract connection details"""
        try:
            if self.database_url.startswith("postgresql://"):
                # Remove postgresql:// prefix
                url_part = self.database_url.replace("postgresql://", "")
                
                # Split credentials and host
                if "@" in url_part:
                    credentials, host_part = url_part.split("@", 1)
                    username, password = credentials.split(":", 1) if ":" in credentials else (credentials, "")
                else:
                    username, password = "", ""
                    host_part = url_part
                
                # Split host and database
                if "/" in host_part:
                    host_port, database = host_part.split("/", 1)
                else:
                    host_port, database = host_part, ""
                
                # Split host and port
                if ":" in host_port:
                    host, port = host_port.split(":", 1)
                    port = int(port)
                else:
                    host, port = host_port, 5432
                
                return {
                    "username": username,
                    "password": password,
                    "host": host,
                    "port": port,
                    "database": database
                }
                
        except Exception as e:
            logger.error(f"Failed to parse database URL: {e}")
            return {}
    
    def test_connection_pool_performance(self, max_connections: int = 10) -> Dict[str, Any]:
        """Test connection pool performance under load"""
        results = {
            "max_connections_tested": max_connections,
            "successful_connections": 0,
            "failed_connections": 0,
            "connection_times": [],
            "errors": []
        }
        
        try:
            # Create engine with minimal pool for testing
            engine = create_engine(
                self.database_url,
                pool_size=1,
                max_overflow=max_connections - 1,
                pool_pre_ping=True,
                pool_timeout=10
            )
            
            # Test concurrent connections
            async def test_single_connection(conn_id: int):
                try:
                    start_time = time.time()
                    
                    with engine.connect() as conn:
                        # Simple query to test connection
                        result = conn.execute(text("SELECT 1"))
                        result.fetchone()
                    
                    connect_time = (time.time() - start_time) * 1000
                    results["connection_times"].append({
                        "connection_id": conn_id,
                        "time_ms": round(connect_time, 2),
                        "success": True
                    })
                    results["successful_connections"] += 1
                    
                except Exception as e:
                    results["failed_connections"] += 1
                    results["errors"].append({
                        "connection_id": conn_id,
                        "error": str(e)
                    })
            
            # Run concurrent connection tests
            async def run_concurrent_tests():
                tasks = [test_single_connection(i) for i in range(max_connections)]
                await asyncio.gather(*tasks, return_exceptions=True)
            
            # Run the test
            asyncio.run(run_concurrent_tests())
            
            # Calculate statistics
            if results["connection_times"]:
                times = [c["time_ms"] for c in results["connection_times"]]
                results.update({
                    "avg_connection_time_ms": round(sum(times) / len(times), 2),
                    "min_connection_time_ms": round(min(times), 2),
                    "max_connection_time_ms": round(max(times), 2),
                    "success_rate": round(results["successful_connections"] / max_connections * 100, 2)
                })
            
            engine.dispose()
            
        except Exception as e:
            results["test_error"] = str(e)
        
        return results
    
    def test_query_performance(self) -> Dict[str, Any]:
        """Test database query performance"""
        results = {
            "queries_tested": 0,
            "avg_query_time_ms": 0,
            "slow_queries": [],
            "errors": []
        }
        
        try:
            engine = create_engine(self.database_url, pool_pre_ping=True)
            
            test_queries = [
                ("Simple SELECT", "SELECT 1"),
                ("Table Count", "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"),
                ("Connection Info", "SELECT version(), current_database(), current_user()"),
            ]
            
            query_times = []
            
            for query_name, query_sql in test_queries:
                try:
                    start_time = time.time()
                    
                    with engine.connect() as conn:
                        result = conn.execute(text(query_sql))
                        data = result.fetchall()
                    
                    query_time = (time.time() - start_time) * 1000
                    query_times.append(query_time)
                    
                    results["queries_tested"] += 1
                    
                    # Flag slow queries (>1000ms)
                    if query_time > 1000:
                        results["slow_queries"].append({
                            "query": query_name,
                            "time_ms": round(query_time, 2)
                        })
                    
                    logger.info(f"Query '{query_name}': {query_time:.2f}ms")
                    
                except Exception as e:
                    results["errors"].append({
                        "query": query_name,
                        "error": str(e)
                    })
            
            if query_times:
                results["avg_query_time_ms"] = round(sum(query_times) / len(query_times), 2)
            
            engine.dispose()
            
        except Exception as e:
            results["test_error"] = str(e)
        
        return results
    
    def check_system_resources(self) -> Dict[str, Any]:
        """Check system resources that might affect database connections"""
        try:
            # Network connections
            network_connections = psutil.net_connections()
            tcp_connections = [conn for conn in network_connections if conn.type == socket.SOCK_STREAM]
            
            # Memory usage
            memory = psutil.virtual_memory()
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            return {
                "tcp_connections_total": len(tcp_connections),
                "tcp_connections_established": len([c for c in tcp_connections if c.status == 'ESTABLISHED']),
                "memory_usage_percent": memory.percent,
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "cpu_usage_percent": cpu_percent,
                "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def run_full_health_check(self) -> Dict[str, Any]:
        """Run comprehensive database health check"""
        logger.info("Starting comprehensive database health check...")
        
        # Parse database URL
        db_info = self.parse_database_url()
        
        health_report = {
            "timestamp": datetime.now().isoformat(),
            "database_info": db_info,
            "tests": {}
        }
        
        # Test 1: TCP Connectivity
        if db_info.get("host") and db_info.get("port"):
            logger.info(f"Testing TCP connectivity to {db_info['host']}:{db_info['port']}")
            tcp_result = self.test_tcp_connection(db_info["host"], db_info["port"])
            health_report["tests"]["tcp_connectivity"] = tcp_result
        
        # Test 2: Connection Pool Performance
        logger.info("Testing connection pool performance...")
        pool_result = self.test_connection_pool_performance(max_connections=8)
        health_report["tests"]["connection_pool"] = pool_result
        
        # Test 3: Query Performance
        logger.info("Testing query performance...")
        query_result = self.test_query_performance()
        health_report["tests"]["query_performance"] = query_result
        
        # Test 4: System Resources
        logger.info("Checking system resources...")
        system_result = self.check_system_resources()
        health_report["tests"]["system_resources"] = system_result
        
        # Generate recommendations
        health_report["recommendations"] = self.generate_recommendations(health_report)
        
        return health_report
    
    def generate_recommendations(self, health_report: Dict[str, Any]) -> List[str]:
        """Generate optimization recommendations based on health check results"""
        recommendations = []
        
        # TCP connectivity recommendations
        tcp_test = health_report["tests"].get("tcp_connectivity", {})
        if not tcp_test.get("success"):
            recommendations.append("❌ TCP connectivity failed - check network/firewall settings")
        elif tcp_test.get("connect_time_ms", 0) > 1000:
            recommendations.append(f"⚠️ High TCP connection time ({tcp_test['connect_time_ms']}ms) - consider closer database server")
        
        # Connection pool recommendations
        pool_test = health_report["tests"].get("connection_pool", {})
        success_rate = pool_test.get("success_rate", 100)
        if success_rate < 90:
            recommendations.append(f"⚠️ Low connection success rate ({success_rate}%) - reduce pool_size or check database load")
        
        if pool_test.get("avg_connection_time_ms", 0) > 500:
            recommendations.append("⚠️ Slow connection times - consider connection pooling optimizations")
        
        # Query performance recommendations
        query_test = health_report["tests"].get("query_performance", {})
        if query_test.get("avg_query_time_ms", 0) > 1000:
            recommendations.append("⚠️ Slow average query times - check database performance and indexing")
        
        slow_queries = query_test.get("slow_queries", [])
        if slow_queries:
            recommendations.append(f"⚠️ {len(slow_queries)} slow queries detected - optimize database queries")
        
        # System resource recommendations
        system_test = health_report["tests"].get("system_resources", {})
        if system_test.get("memory_usage_percent", 0) > 80:
            recommendations.append("⚠️ High memory usage - may affect connection stability")
        
        tcp_connections = system_test.get("tcp_connections_established", 0)
        if tcp_connections > 100:
            recommendations.append(f"⚠️ High TCP connection count ({tcp_connections}) - may indicate connection leaks")
        
        if not recommendations:
            recommendations.append("✅ Database connection health looks good!")
        
        return recommendations


def main():
    """Run database health check and display results"""
    print("Database Connection Health Monitor")
    print("=" * 50)
    
    monitor = DatabaseHealthMonitor()
    health_report = monitor.run_full_health_check()
    
    # Display results
    print(f"\n📊 Health Check Results - {health_report['timestamp']}")
    print("-" * 50)
    
    # Database info
    db_info = health_report.get("database_info", {})
    if db_info:
        print(f"Database: {db_info.get('database', 'unknown')}@{db_info.get('host', 'unknown')}:{db_info.get('port', 5432)}")
    
    # TCP Connectivity
    tcp_test = health_report["tests"].get("tcp_connectivity", {})
    if tcp_test:
        status = "✅ Connected" if tcp_test["success"] else "❌ Failed"
        print(f"TCP Connectivity: {status} ({tcp_test.get('connect_time_ms', 0)}ms)")
        if tcp_test.get("error"):
            print(f"  Error: {tcp_test['error']}")
    
    # Connection Pool
    pool_test = health_report["tests"].get("connection_pool", {})
    if pool_test:
        success_rate = pool_test.get("success_rate", 0)
        avg_time = pool_test.get("avg_connection_time_ms", 0)
        print(f"Connection Pool: {success_rate}% success rate, {avg_time}ms avg time")
    
    # Query Performance
    query_test = health_report["tests"].get("query_performance", {})
    if query_test:
        avg_time = query_test.get("avg_query_time_ms", 0)
        slow_count = len(query_test.get("slow_queries", []))
        print(f"Query Performance: {avg_time}ms avg, {slow_count} slow queries")
    
    # System Resources
    system_test = health_report["tests"].get("system_resources", {})
    if system_test:
        tcp_conn = system_test.get("tcp_connections_established", 0)
        mem_usage = system_test.get("memory_usage_percent", 0)
        print(f"System Resources: {tcp_conn} TCP connections, {mem_usage}% memory usage")
    
    # Recommendations
    print(f"\n🔧 Recommendations:")
    for rec in health_report.get("recommendations", []):
        print(f"  {rec}")
    
    # Save detailed report
    import json
    with open("database_health_report.json", "w") as f:
        json.dump(health_report, f, indent=2, default=str)
    
    print(f"\n📄 Detailed report saved to: database_health_report.json")


if __name__ == "__main__":
    main()
