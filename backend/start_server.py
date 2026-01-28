#!/usr/bin/env python3
"""Nigeria Conflict Tracker API Server Startup Script."""

import argparse
import logging
import os
import sys
from typing import Optional, Tuple

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config.server_config import get_server_config, validate_dependencies
from app.utils.port_manager import (
    check_port_available,
    find_available_port,
    get_process_info,
    kill_process_on_port,
    get_server_config as get_port_config,
    validate_port_config
)
from app.utils.process_manager import setup_process_management, get_process_manager
from app.utils.error_recovery import get_dependency_checker, CircuitBreaker, RetryConfig, retry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Start Nigeria Conflict Tracker API")
    parser.add_argument(
        "--kill-existing",
        action="store_true",
        help="Kill existing process using the target port"
    )
    parser.add_argument(
        "--port",
        type=int,
        help="Port to bind to (overrides PORT environment variable)"
    )
    parser.add_argument(
        "--host",
        help="Host to bind to (overrides HOST environment variable)"
    )
    parser.add_argument(
        "--find-available",
        action="store_true",
        help="Find and use the next available port if target port is in use"
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate configuration and dependencies, then exit"
    )
    parser.add_argument(
        "--deployment-check",
        action="store_true",
        help="Run pre-deployment validation checks"
    )
    parser.add_argument(
        "--production-mode",
        action="store_true",
        help="Enable production hardening features"
    )
    return parser.parse_args()
    """Run comprehensive pre-deployment validation checks."""
    logger.info("Running pre-deployment validation checks...")

    try:
        import requests
        import time
        from app.db.database import get_db_session

        # Get configuration
        config = get_server_config()
        port = config.get("port")
        host = config.get("host", "0.0.0.0")

        # Test health endpoint
        health_url = f"http://{host}:{port}/api/v1/monitoring/health"
        logger.info(f"Testing health endpoint: {health_url}")

        response = requests.get(health_url, timeout=10)
        if response.status_code != 200:
            logger.error(f"Health check failed: {response.status_code}")
            return False

        health_data = response.json()
        if health_data.get("status") != "healthy":
            logger.error(f"Health status not healthy: {health_data.get('status')}")
            return False

        # Test readiness probe
        ready_url = f"http://{host}:{port}/api/v1/monitoring/ready"
        logger.info(f"Testing readiness probe: {ready_url}")

        response = requests.get(ready_url, timeout=5)
        if response.status_code != 200:
            logger.error(f"Readiness probe failed: {response.status_code}")
            return False

        # Test database connectivity
        logger.info("Testing database connectivity...")
        db = next(get_db_session())
        try:
            result = db.execute(text("SELECT 1")).scalar()
            if result != 1:
                logger.error("Database connectivity test failed")
                return False
        finally:
            db.close()

        # Test Redis connectivity
        logger.info("Testing Redis connectivity...")
        try:
            from app.core.cache import get_redis_client
            redis_client = get_redis_client()
            redis_client.ping()
        except Exception as e:
            logger.error(f"Redis connectivity test failed: {e}")
            return False

        logger.info("✓ All deployment checks passed")
        return True

    except Exception as e:
        logger.error(f"Deployment check failed: {e}")
        return False


def enable_production_hardening():
    """Enable production hardening features."""
    logger.info("Enabling production hardening features...")

    # Set production environment variables if not set
    if not os.getenv("ENVIRONMENT"):
        os.environ["ENVIRONMENT"] = "production"

    # Enable more aggressive health checking
    if not os.getenv("HEALTH_CHECK_TIMEOUT"):
        os.environ["HEALTH_CHECK_TIMEOUT"] = "30"

    # Enable circuit breaker for external services
    if not os.getenv("CIRCUIT_BREAKER_ENABLED"):
        os.environ["CIRCUIT_BREAKER_ENABLED"] = "true"

    # Set production logging
    if not os.getenv("LOG_LEVEL"):
        os.environ["LOG_LEVEL"] = "WARNING"

    logger.info("✓ Production hardening features enabled")


def validate_system() -> bool:
    """Validate system configuration and dependencies."""
    logger.info("Validating system configuration and dependencies...")

    # Validate dependencies
    dep_errors = validate_dependencies()
    if dep_errors:
        logger.error("Dependency validation failed:")
        for error in dep_errors:
            logger.error(f"  - {error}")
        return False

    # Validate server configuration
    config = get_server_config()
    is_valid, config_errors = config.validate()
    if not is_valid:
        logger.error("Configuration validation failed:")
        for error in config_errors:
            logger.error(f"  - {error}")
        return False

    logger.info("✓ System validation passed")
    return True


def setup_dependencies():
    """Setup dependency checkers and circuit breakers."""
    from app.utils.error_recovery import get_dependency_checker, CircuitBreaker

    dep_checker = get_dependency_checker()

    # Database checker with circuit breaker
    @retry(RetryConfig(max_attempts=3, initial_delay=1.0))
    def check_database():
        try:
            from app.db.database import engine
            from sqlalchemy import text
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1")).scalar()
                return result == 1, "Database connection healthy"
        except Exception as e:
            return False, f"Database connection failed: {e}"

    # Redis checker with circuit breaker
    @retry(RetryConfig(max_attempts=3, initial_delay=1.0))
    async def check_redis():
        try:
            from app.core.cache import get_redis_client
            redis_client = await get_redis_client()
            await redis_client.ping()
            return True, "Redis connection healthy"
        except Exception as e:
            return False, f"Redis connection failed: {e}"

    # Register checkers
    dep_checker.register_checker("database", check_database, CircuitBreaker())
    dep_checker.register_checker("redis", check_redis, CircuitBreaker())

    logger.info("Dependency checkers registered")


def setup_server(host: str, port: int, args: argparse.Namespace) -> Tuple[str, int]:
    """Setup server configuration with port management.

    Args:
        host: Target host
        port: Target port
        args: Command line arguments

    Returns:
        Tuple of (final_host, final_port)
    """
    logger.info(f"Attempting to start server on {host}:{port}")

    # Validate configuration
    is_valid, error_msg = validate_port_config(host, port)
    if not is_valid:
        logger.error(f"Invalid configuration: {error_msg}")
        sys.exit(1)

    # Check if port is available
    if check_port_available(port, host):
        logger.info(f"Port {port} is available")
        return host, port

    # Port is in use
    process_info = get_process_info(port)
    if process_info:
        logger.warning(f"Port {port} is in use by: {process_info}")

        if args.kill_existing:
            logger.info("Attempting to kill existing process...")
            if kill_process_on_port(port):
                logger.info("Successfully killed existing process")
                # Wait a moment for cleanup
                import time
                time.sleep(1)
                return host, port
            else:
                logger.error("Failed to kill existing process")
                sys.exit(1)
        elif args.find_available:
            logger.info("Finding alternative port...")
            try:
                new_port = find_available_port(port + 1)
                logger.info(f"Using alternative port: {new_port}")
                return host, new_port
            except RuntimeError as e:
                logger.error(f"Failed to find available port: {e}")
                sys.exit(1)
        else:
            logger.error(f"Port {port} is already in use. Use --kill-existing or --find-available")
            sys.exit(1)
    else:
        logger.warning(f"Port {port} appears in use but no process found")
        return host, port


def main():
    """Main server startup function."""
    args = parse_arguments()

    # Enable production hardening if requested
    if args.production_mode:
        enable_production_hardening()

    # Validate system first
    if not validate_system():
        logger.error("System validation failed. Please fix the issues above.")
        sys.exit(1)

    # Handle deployment check mode (requires server to be running)
    if args.deployment_check:
        logger.info("Running deployment validation checks...")
        if run_deployment_checks():
            logger.info("✓ Deployment validation passed")
            sys.exit(0)
        else:
            logger.error("✗ Deployment validation failed")
            sys.exit(1)

    # Setup dependencies
    setup_dependencies()

    # Get base configuration
    config = get_server_config()
    host, port = config.get_server_config()

    # Override with command line args if provided
    if args.host:
        host = args.host
    if args.port:
        port = args.port

    # Setup server with port management
    final_host, final_port = setup_server(host, port, args)

    # Setup process management
    process_config = config.get_process_config()
    setup_process_management(pid_file=process_config["pid_file"])

    # Register shutdown handlers
    process_mgr = get_process_manager()

    async def cleanup_database():
        """Cleanup database connections on shutdown."""
        try:
            from app.db.database import engine
            engine.dispose()
            logger.info("Database connections cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up database: {e}")

    async def cleanup_redis():
        """Cleanup Redis connections on shutdown."""
        try:
            from app.core.cache import close_redis_client
            await close_redis_client()
            logger.info("Redis connections cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up Redis: {e}")

    # Register cleanup handlers
    process_mgr.register_shutdown_handler(cleanup_database)
    process_mgr.register_shutdown_handler(cleanup_redis)

    logger.info(f"Starting Nigeria Conflict Tracker API on {final_host}:{final_port}")

    try:
        import uvicorn
        uvicorn.run(
            "app.main:app",
            host=final_host,
            port=final_port,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        logger.info("Server shutdown requested by user")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)

    # Setup dependencies
    setup_dependencies()

    # Get base configuration
    config = get_server_config()
    host, port = config.get_server_config()

    # Override with command line args if provided
    if args.host:
        host = args.host
    if args.port:
        port = args.port

    # Setup server with port management
    final_host, final_port = setup_server(host, port, args)

    # Setup process management
    process_config = config.get_process_config()
    setup_process_management(pid_file=process_config["pid_file"])

    # Register shutdown handlers
    process_mgr = get_process_manager()

    async def cleanup_database():
        """Cleanup database connections on shutdown."""
        try:
            from app.db.database import engine
            engine.dispose()
            logger.info("Database connections cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up database: {e}")

    async def cleanup_redis():
        """Cleanup Redis connections on shutdown."""
        try:
            from app.core.cache import close_redis_client
            await close_redis_client()
            logger.info("Redis connections cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up Redis: {e}")

    # Register cleanup handlers
    process_mgr.register_shutdown_handler(cleanup_database)
    process_mgr.register_shutdown_handler(cleanup_redis)

    logger.info(f"Starting Nigeria Conflict Tracker API on {final_host}:{final_port}")

    try:
        import uvicorn
        uvicorn.run(
            "app.main:app",
            host=final_host,
            port=final_port,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        logger.info("Server shutdown requested by user")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
