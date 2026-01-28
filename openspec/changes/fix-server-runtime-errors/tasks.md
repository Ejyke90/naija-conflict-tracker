# Fix Server Runtime Errors - Implementation Tasks

## Phase 1: Emergency Fixes (2 hours)

### 1.1 Process Cleanup
- [ ] 1.1.1 Kill zombie processes: `pkill -f "start_server.py"`
- [ ] 1.1.2 Free port 8000: `lsof -ti:8000 | xargs kill -9`
- [ ] 1.1.3 Verify port availability: `lsof -i:8000` (should return empty)
- [ ] 1.1.4 Check for other Python processes: `ps aux | grep python | grep naija`

### 1.2 bcrypt Dependency Fix  
- [ ] 1.2.1 Uninstall conflicting packages: `pip uninstall bcrypt passlib -y`
- [ ] 1.2.2 Install compatible versions: `pip install bcrypt==4.1.2 passlib[bcrypt]==1.7.4`
- [ ] 1.2.3 Test bcrypt import: `python -c "import bcrypt; print(bcrypt.__version__)"`
- [ ] 1.2.4 Test passlib bcrypt: `python -c "from passlib.context import CryptContext; print('OK')"`
- [ ] 1.2.5 Update requirements.txt with pinned versions

### 1.3 Port Management Implementation
- [ ] 1.3.1 Create `backend/app/utils/port_manager.py`
- [ ] 1.3.2 Implement `check_port_available(port: int) -> bool`
- [ ] 1.3.3 Implement `find_available_port(start_port: int = 8000) -> int`
- [ ] 1.3.4 Implement `kill_process_on_port(port: int) -> bool`
- [ ] 1.3.5 Add environment variable support: `PORT` with fallback to 8000

### 1.4 Server Startup Fix
- [ ] 1.4.1 Update `backend/start_server.py` to use port management
- [ ] 1.4.2 Add port availability check before uvicorn start
- [ ] 1.4.3 Add option to kill existing process: `--kill-existing`
- [ ] 1.4.4 Add verbose logging for startup process
- [ ] 1.4.5 Test server startup: `python start_server.py`

### 1.5 Immediate Validation
- [ ] 1.5.1 Start server successfully: `python start_server.py`
- [ ] 1.5.2 Health check responds: `curl http://localhost:8000/api/v1/public/health`
- [ ] 1.5.3 No bcrypt errors in console output
- [ ] 1.5.4 Server shutdown cleanly: `Ctrl+C`

## Phase 2: Robust Solutions (4 hours)

### 2.1 Process Management System
- [ ] 2.1.1 Create `backend/app/utils/process_manager.py`
- [ ] 2.1.2 Implement signal handlers for SIGTERM/SIGINT
- [ ] 2.1.3 Add PID file management in `/tmp/naija-api.pid`
- [ ] 2.1.4 Implement graceful shutdown with cleanup
- [ ] 2.1.5 Add process health monitoring

### 2.2 Error Recovery Framework
- [ ] 2.2.1 Create `backend/app/utils/error_recovery.py`
- [ ] 2.2.2 Implement retry logic for failed dependencies
- [ ] 2.2.3 Add fallback mechanisms for critical services
- [ ] 2.2.4 Implement error reporting and logging
- [ ] 2.2.5 Add recovery metrics tracking

### 2.3 Health Check System
- [ ] 2.3.1 Enhance `/api/v1/public/health` endpoint
- [ ] 2.3.2 Add dependency checks (database, Redis, etc.)
- [ ] 2.3.3 Implement readiness probe: `/api/v1/public/ready`
- [ ] 2.3.4 Add liveness probe: `/api/v1/public/alive`
- [ ] 2.3.5 Include process information in health response

### 2.4 Configuration Management
- [ ] 2.4.1 Create `backend/app/config/server_config.py`
- [ ] 2.4.2 Centralize environment variables
- [ ] 2.4.3 Add configuration validation
- [ ] 2.4.4 Implement config reload without restart
- [ ] 2.4.5 Add config export for debugging

### 2.5 Testing Infrastructure
- [ ] 2.5.1 Create `backend/tests/test_server_startup.py`
- [ ] 2.5.2 Write port conflict detection tests
- [ ] 2.5.3 Write bcrypt compatibility tests
- [ ] 2.5.4 Write graceful shutdown tests
- [ ] 2.5.5 Add integration tests for full startup cycle

## Phase 3: Production Hardening (2 hours)

### 3.1 Deployment Safety
- [ ] 3.1.1 Update `backend/Dockerfile` for production
- [ ] 3.1.2 Add health checks to Docker configuration
- [ ] 3.1.3 Implement blue/green deployment support
- [ ] 3.1.4 Add rollback procedures
- [ ] 3.1.5 Update Railway deployment configuration

### 3.2 Monitoring Integration
- [ ] 3.2.1 Add process health metrics to `/api/v1/monitoring/health`
- [ ] 3.2.2 Implement error rate tracking
- [ ] 3.2.3 Add performance monitoring for startup time
- [ ] 3.2.4 Create alerting rules for critical errors
- [ ] 3.2.5 Add dashboard for server health metrics

### 3.3 Documentation and Procedures
- [ ] 3.3.1 Update `backend/README.md` with troubleshooting
- [ ] 3.3.2 Create runbook for server issues
- [ ] 3.3.3 Document port management procedures
- [ ] 3.3.4 Add deployment checklist
- [ ] 3.3.5 Create emergency response procedures

## File Structure Created

```
backend/
├── app/
│   ├── utils/
│   │   ├── port_manager.py        # Port availability and management
│   │   ├── process_manager.py     # Process lifecycle management  
│   │   └── error_recovery.py      # Error handling and recovery
│   └── config/
│       └── server_config.py       # Centralized configuration
├── tests/
│   └── test_server_startup.py     # Server startup tests
├── start_server.py                # Updated with robust startup
└── requirements.txt               # Updated with pinned dependencies
```

## Environment Variables Added

```bash
# Server Configuration
PORT=8000                          # Server port (with fallback)
HOST=0.0.0.0                      # Server host
KILL_EXISTING=false                # Kill existing process on startup

# Process Management
PID_FILE=/tmp/naija-api.pid       # PID file location
GRACEFUL_TIMEOUT=30               # Seconds to wait for graceful shutdown
HEALTH_CHECK_TIMEOUT=5            # Health check timeout in seconds

# Dependency Configuration  
BCRYPT_FALLBACK=false             # Whether to allow SHA256 fallback
REDIS_RETRY_ATTEMPTS=3            # Redis connection retry attempts
DB_CONNECTION_TIMEOUT=10          # Database connection timeout
```

## Validation Commands

```bash
# Phase 1 Validation
python start_server.py --kill-existing
curl http://localhost:8000/api/v1/public/health
python -c "import bcrypt, passlib; print('Dependencies OK')"

# Phase 2 Validation  
python start_server.py &
PID=$!
kill -TERM $PID  # Should shutdown gracefully
curl http://localhost:8000/api/v1/public/ready

# Phase 3 Validation
pytest backend/tests/test_server_startup.py
docker build -t naija-api backend/ && docker run --rm naija-api
```

## Success Criteria Checklist

### Phase 1 Success
- [ ] Server starts without bcrypt errors
- [ ] No port binding conflicts  
- [ ] Health checks return 200 OK
- [ ] Clean process termination

### Phase 2 Success
- [ ] Graceful shutdown on signals
- [ ] Automated error recovery working
- [ ] Comprehensive test coverage >80%
- [ ] Zero manual intervention for restarts

### Phase 3 Success
- [ ] Production deployment successful
- [ ] Monitoring and alerting active
- [ ] Zero-downtime deployment capability
- [ ] SLA compliance ready (99.9% uptime target)

## Critical Dependencies

### Must Complete Before
- Process cleanup (Phase 1.1)
- bcrypt fix (Phase 1.2)

### Integrates With
- `fix-analytics-endpoints` (analytics will work after server fixes)
- `add-authentication-system` (benefits from bcrypt fixes)
- Production deployment configs

### Blocks
- All other development work
- Analytics dashboard features
- Authentication implementation
- Production deployment

---

**Next Steps:** Execute Phase 1 tasks immediately to restore server functionality, then proceed with robust solutions in Phase 2 and 3.