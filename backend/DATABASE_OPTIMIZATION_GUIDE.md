# Database Connection Optimization Guide
## High-Latency Environments & TCP_OVERWINDOW Prevention

### Problem: TCP_OVERWINDOW on Port 5432
TCP_OVERWINDOW indicates network-level connection issues where:
- Too many connections are queued
- Connection timeouts occur
- Network buffers overflow
- Database becomes unresponsive

### Root Causes
1. **Connection Pool Too Large**: Too many concurrent connections overwhelm the database
2. **Long Connection Lifetimes**: Stale connections accumulate
3. **High Network Latency**: Slow connection establishment
4. **Missing TCP Optimizations**: No keepalives or proper timeouts

### 🔧 Optimizations Applied

#### 1. Connection Pool Tuning
```python
# Before (causing TCP_OVERWINDOW)
engine_kwargs = {
    "pool_size": 20,        # Too many connections
    "max_overflow": 10,     # Even more during peaks
    "pool_recycle": 300,    # 5 minutes - too long
    "pool_timeout": 30,     # Too slow failure detection
}

# After (TCP_OVERWINDOW optimized)
engine_kwargs = {
    "pool_size": 8,         # Reduced to prevent pile-up
    "max_overflow": 5,      # Controlled overflow
    "pool_recycle": 180,    # 3 minutes - shorter lifetime
    "pool_timeout": 15,     # Faster failure detection
    "echo": False,          # Disable logging overhead
}
```

#### 2. TCP-Level Optimizations
```python
connect_args = {
    "connect_timeout": 8,           # Faster connection attempts
    "command_timeout": 25,          # Prevent hanging queries
    "server_settings": {
        # TCP keepalives to prevent stale connections
        "tcp_keepalives_idle": "300",     # 5 minutes
        "tcp_keepalives_interval": "30",   # 30 seconds
        "tcp_keepalives_count": "3",       # 3 retries
        
        # Query timeouts to prevent hanging
        "statement_timeout": "25000",      # 25 seconds
        "idle_in_transaction_session_timeout": "20000",  # 20 seconds
    }
}
```

#### 3. Provider-Specific Optimizations

**Neon Database (Connection Pooling):**
```python
engine_kwargs = {
    "pool_size": 5,          # Smaller for pgbouncer
    "max_overflow": 2,       # Minimal overflow
    "pool_recycle": 120,     # 2 minutes - shorter
}
connect_args = {
    "connect_timeout": 5,    # Faster for Neon
    "server_settings": {
        "jit": "off",         # Disable JIT for simple queries
    }
}
```

**Railway Database:**
```python
engine_kwargs = {
    "pool_size": 10,         # Medium pool
    "max_overflow": 3,       # Controlled overflow
    "pool_recycle": 240,     # 4 minutes
}
```

### 📊 Monitoring & Detection

#### Health Check Script
```bash
python3 monitor_database_health.py
```

#### Key Metrics to Monitor:
- **TCP Connection Time**: < 1000ms (ideal: < 500ms)
- **Connection Success Rate**: > 95%
- **Pool Utilization**: < 80%
- **TCP Connections Established**: < 100
- **Query Response Time**: < 1000ms average

#### TCP_OVERWINDOW Symptoms:
- Connection timeouts
- High TCP connection count (>100)
- Slow connection establishment
- Database unresponsiveness

### 🚀 Performance Tuning Strategies

#### 1. Connection Pool Sizing
```python
# Calculate optimal pool size
optimal_pool_size = min(
    cpu_cores * 2 + 1,      # CPU-bound workloads
    20                      # Maximum for most applications
)

# For high-latency networks
optimal_pool_size = min(optimal_pool_size, 8)
```

#### 2. Timeout Strategy
```python
# Layered timeouts for high-latency environments
connection_timeout = 8      # TCP connection
statement_timeout = 25      # Query execution
pool_timeout = 15           # Pool acquisition
total_timeout = 60         # Maximum request time
```

#### 3. Connection Lifecycle
```python
# Short connection lifetimes for network stability
pool_recycle = 180          # 3 minutes
max_lifetime = 600          # 10 minutes absolute max
idle_timeout = 30           # Close idle connections
```

### 🔍 Troubleshooting TCP_OVERWINDOW

#### Step 1: Check Network Connectivity
```bash
# Test TCP connection
telnet your-db-host.com 5432

# Check latency
ping your-db-host.com

# Monitor TCP connections
netstat -an | grep :5432
```

#### Step 2: Analyze Connection Pool
```python
# Monitor pool statistics
from sqlalchemy import event
from sqlalchemy.engine import Engine

@event.listens_for(Engine, "connect")
def receive_connect(dbapi_connection, connection_record):
    print("New connection created")

@event.listens_for(Engine, "checkout")
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    print("Connection checked out from pool")
```

#### Step 3: Database Server Settings
```sql
-- PostgreSQL server optimizations for high-latency
ALTER SYSTEM SET tcp_keepalives_idle = 300;
ALTER SYSTEM SET tcp_keepalives_interval = 30;
ALTER SYSTEM SET tcp_keepalives_count = 3;
ALTER SYSTEM SET statement_timeout = '25s';
ALTER SYSTEM SET idle_in_transaction_session_timeout = '20s';

-- Connection limits
ALTER SYSTEM SET max_connections = 100;
ALTER SYSTEM SET superuser_reserved_connections = 3;
```

### 📈 Expected Improvements

#### Before Optimization:
- Connection time: 2000-5000ms
- TCP_OVERWINDOW errors: Frequent
- Pool utilization: 100%
- Database timeouts: Common

#### After Optimization:
- Connection time: 200-800ms
- TCP_OVERWINDOW errors: Eliminated
- Pool utilization: 60-80%
- Database timeouts: Rare

### 🛠️ Implementation Checklist

- [ ] Reduce pool_size to 8 (or less for Neon)
- [ ] Set max_overflow to 5 (or 2 for Neon)
- [ ] Configure pool_recycle to 180s
- [ ] Enable pool_pre_ping
- [ ] Set TCP keepalives
- [ ] Configure statement_timeout
- [ ] Set connect_timeout to 8s
- [ ] Disable SQL logging in production
- [ ] Monitor connection health
- [ ] Test under load

### 🔄 Ongoing Maintenance

#### Daily Monitoring:
```bash
# Run health check
python3 monitor_database_health.py

# Check connection counts
ps aux | grep postgres | wc -l

# Monitor TCP connections
netstat -an | grep ESTABLISHED | wc -l
```

#### Weekly Optimization:
- Review connection pool metrics
- Check for connection leaks
- Monitor query performance
- Adjust pool sizes based on load

#### Monthly Review:
- Analyze TCP_OVERWINDOW incidents
- Update timeout settings
- Review database server configuration
- Optimize slow queries

### 🚨 Emergency Procedures

#### If TCP_OVERWINDOW Occurs:
1. **Immediate**: Reduce pool_size by 50%
2. **Short-term**: Set pool_recycle to 60s
3. **Medium-term**: Add connection timeouts
4. **Long-term**: Consider connection pooling service

#### Database Recovery:
```python
# Emergency pool settings
engine_kwargs = {
    "pool_size": 3,          # Minimal pool
    "max_overflow": 1,       # No overflow
    "pool_recycle": 60,      # 1 minute recycle
    "pool_timeout": 5,       # Fast timeout
}
```

This optimization should eliminate TCP_OVERWINDOW issues and improve database connection reliability in high-latency environments.
