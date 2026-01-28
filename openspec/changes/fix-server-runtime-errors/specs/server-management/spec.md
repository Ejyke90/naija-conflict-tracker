# Server Management Capability

## ADDED Requirements

### Requirement: Process Lifecycle Management
The server SHALL provide robust process lifecycle management including startup validation, port conflict resolution, and graceful shutdown to ensure reliable service operation.

#### Scenario: Server starts successfully with port management
- GIVEN the system has port 8000 available
- WHEN the server starts with `python start_server.py`
- THEN the server binds to port 8000
- AND the health check endpoint responds with 200 OK
- AND no bcrypt compatibility errors occur

#### Scenario: Server handles port conflicts gracefully
- GIVEN port 8000 is already in use by another process
- WHEN the server starts with `python start_server.py`
- THEN the server either finds an alternative port (8001, 8002, etc.)
- OR provides clear error message about port conflict
- AND offers option to kill existing process with `--kill-existing`

#### Scenario: Server kills existing process when requested
- GIVEN port 8000 is occupied by a previous server instance
- WHEN the server starts with `python start_server.py --kill-existing`
- THEN the existing process is terminated gracefully
- AND the new server binds to port 8000 successfully
- AND the PID file is updated with new process ID

### Requirement: Dependency Management
The server SHALL validate and manage dependencies including bcrypt compatibility and library versions to prevent runtime errors and security fallbacks.

#### Scenario: bcrypt compatibility is validated on startup
- GIVEN the server is starting
- WHEN bcrypt and passlib libraries are loaded
- THEN bcrypt version 4.1.2 is available
- AND passlib can use bcrypt backend successfully
- AND no fallback to SHA256 occurs unless explicitly configured

#### Scenario: Dependencies are validated before server start
- GIVEN the server is starting
- WHEN dependency validation runs
- THEN all required packages (bcrypt, passlib, uvicorn) are checked
- AND incompatible versions are reported with specific error messages
- AND server startup is blocked if critical dependencies fail

### Requirement: Graceful Shutdown
The server SHALL implement graceful shutdown procedures that handle signals properly and clean up resources to prevent data loss and service disruption.

#### Scenario: Server handles SIGTERM gracefully  
- GIVEN the server is running normally
- WHEN a SIGTERM signal is received
- THEN all active requests complete within 30 seconds
- AND database connections are closed properly
- AND Redis connections are cleaned up
- AND the PID file is removed
- AND exit code 0 is returned

#### Scenario: Server handles SIGINT gracefully (Ctrl+C)
- GIVEN the server is running in development mode
- WHEN a SIGINT signal is received (Ctrl+C)
- THEN the shutdown process begins immediately
- AND cleanup tasks complete within 5 seconds
- AND clear shutdown message is displayed
- AND terminal prompt is restored

### Requirement: Health Monitoring
The server SHALL provide comprehensive health monitoring endpoints that report process status, dependency health, and system metrics for operational visibility.

#### Scenario: Health check includes process status
- GIVEN the server is running
- WHEN GET /api/v1/public/health is called
- THEN response includes server uptime
- AND response includes process ID
- AND response includes memory usage
- AND response includes dependency status (Redis, PostgreSQL)
- AND response time is under 100ms

#### Scenario: Readiness probe verifies dependencies
- GIVEN the server is starting up
- WHEN GET /api/v1/public/ready is called
- THEN response indicates if database connection is ready
- AND response indicates if Redis connection is ready  
- AND response indicates if all services are initialized
- AND returns 503 if not ready, 200 if ready

### Requirement: Error Recovery
The server SHALL implement automatic error recovery mechanisms for dependency failures and provide graceful degradation when external services are unavailable.

#### Scenario: Server recovers from Redis connection failure
- GIVEN the server is running normally
- WHEN Redis connection is lost
- THEN server continues operating with degraded functionality
- AND health check reports Redis as unhealthy
- AND automatic reconnection attempts are made every 5 seconds
- AND normal functionality resumes when Redis is available

#### Scenario: Server recovers from database connection failure
- GIVEN the server is running normally  
- WHEN database connection is lost
- THEN server returns 503 for data-dependent endpoints
- AND health check reports database as unhealthy
- AND connection retry logic activates with exponential backoff
- AND normal functionality resumes when database is available

## ADDED Components

### Port Manager (`app/utils/port_manager.py`)
- `check_port_available(port: int) -> bool`
- `find_available_port(start_port: int = 8000) -> int`
- `kill_process_on_port(port: int) -> bool`
- `get_process_info(port: int) -> dict`

### Process Manager (`app/utils/process_manager.py`)  
- `setup_signal_handlers() -> None`
- `graceful_shutdown(signal_num: int) -> None`
- `write_pid_file(path: str) -> None`
- `remove_pid_file(path: str) -> None`
- `is_process_running(pid: int) -> bool`

### Server Configuration (`app/config/server_config.py`)
- `ServerConfig` class with environment variable loading
- `validate_dependencies() -> List[str]` (returns errors)
- `get_port_config() -> Tuple[str, int]` (host, port)
- `get_process_config() -> dict` (PID file, timeouts)

### Health Check Enhancements (`app/api/v1/endpoints/monitoring.py`)
- Enhanced `/health` endpoint with process information
- New `/ready` endpoint for readiness probes
- New `/alive` endpoint for liveness probes
- Process status in monitoring dashboard

## ADDED Environment Variables

```bash
# Server Configuration
PORT=8000                          # Server port with fallback
HOST=0.0.0.0                      # Server host binding
KILL_EXISTING=false               # Auto-kill existing processes

# Process Management  
PID_FILE=/tmp/naija-api.pid       # PID file location
GRACEFUL_TIMEOUT=30               # Graceful shutdown timeout
HEALTH_CHECK_TIMEOUT=5            # Health check timeout

# Dependency Configuration
BCRYPT_FALLBACK=false             # Allow bcrypt fallback
REDIS_RETRY_ATTEMPTS=3            # Redis retry attempts
DB_CONNECTION_TIMEOUT=10          # Database timeout
MAX_STARTUP_RETRIES=3             # Maximum startup retries
```

## ADDED Error Handling

### Startup Errors
- Port binding conflicts with clear resolution steps
- bcrypt compatibility errors with specific fix instructions  
- Dependency validation errors with version requirements
- Configuration errors with environment variable guidance

### Runtime Errors  
- Redis connection failures with automatic retry
- Database connection failures with circuit breaker pattern
- Resource exhaustion with graceful degradation
- Signal handling errors with fallback mechanisms

## ADDED Monitoring Metrics

### Process Health
- Server uptime duration
- Process memory usage
- CPU usage percentage  
- File descriptor count
- Thread count

### Dependency Status
- Database connection state (healthy/unhealthy/retry)
- Redis connection state (healthy/unhealthy/retry)
- External service availability
- Error rates per dependency

### Performance Metrics
- Health check response time (<100ms target)
- Startup time (<10s target)
- Shutdown time (<30s target)
- Request processing time per endpoint

---

This specification ensures the server management system provides robust process lifecycle management, dependency validation, graceful shutdown, and comprehensive health monitoring for the Nigeria Conflict Tracker platform.