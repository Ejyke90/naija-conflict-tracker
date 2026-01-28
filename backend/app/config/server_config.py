"""Centralized server configuration management."""

import os
import logging
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class ServerConfig:
    """Centralized configuration for server components."""

    def __init__(self):
        self._config = {}
        self._load_config()

    def _load_config(self):
        """Load configuration from environment variables."""
        # Server configuration
        self._config.update({
            "host": os.getenv("HOST", "0.0.0.0"),
            "port": int(os.getenv("PORT", "8000")),
            "debug": os.getenv("DEBUG", "false").lower() == "true",
            "environment": os.getenv("ENVIRONMENT", "development"),

            # Process management
            "pid_file": os.getenv("PID_FILE", "/tmp/naija-api.pid"),
            "graceful_timeout": int(os.getenv("GRACEFUL_TIMEOUT", "30")),
            "health_check_timeout": int(os.getenv("HEALTH_CHECK_TIMEOUT", "5")),

            # Dependency configuration
            "bcrypt_fallback": os.getenv("BCRYPT_FALLBACK", "false").lower() == "true",
            "redis_retry_attempts": int(os.getenv("REDIS_RETRY_ATTEMPTS", "3")),
            "db_connection_timeout": int(os.getenv("DB_CONNECTION_TIMEOUT", "10")),
            "max_startup_retries": int(os.getenv("MAX_STARTUP_RETRIES", "3")),

            # Logging
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "log_file": os.getenv("LOG_FILE"),

            # Security
            "cors_origins": os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
            "jwt_secret_key": os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production"),
            "jwt_algorithm": os.getenv("JWT_ALGORITHM", "HS256"),
            "jwt_expiration_hours": int(os.getenv("JWT_EXPIRATION_HOURS", "24")),

            # Database
            "database_url": os.getenv("DATABASE_URL"),
            "db_pool_size": int(os.getenv("DB_POOL_SIZE", "10")),
            "db_max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "20")),

            # Redis
            "redis_url": os.getenv("REDIS_URL", "redis://localhost:6379"),
            "redis_db": int(os.getenv("REDIS_DB", "0")),

            # External services
            "openai_api_key": os.getenv("OPENAI_API_KEY"),
            "anthropic_api_key": os.getenv("ANTHROPIC_API_KEY"),

            # Feature flags
            "enable_analytics": os.getenv("ENABLE_ANALYTICS", "true").lower() == "true",
            "enable_forecasting": os.getenv("ENABLE_FORECASTING", "true").lower() == "true",
            "enable_notifications": os.getenv("ENABLE_NOTIFICATIONS", "false").lower() == "true",
        })

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self._config.get(key, default)

    def set(self, key: str, value: Any):
        """Set configuration value."""
        self._config[key] = value
        logger.debug(f"Configuration updated: {key} = {value}")

    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values (with sensitive data masked)."""
        masked_config = {}
        sensitive_keys = {"jwt_secret_key", "openai_api_key", "anthropic_api_key", "database_url"}

        for key, value in self._config.items():
            if key in sensitive_keys and value:
                masked_config[key] = "***masked***"
            else:
                masked_config[key] = value

        return masked_config

    def validate(self) -> Tuple[bool, list[str]]:
        """Validate configuration and return (is_valid, errors)."""
        errors = []

        # Required configurations
        required_configs = {
            "jwt_secret_key": "JWT_SECRET_KEY environment variable must be set",
            "database_url": "DATABASE_URL environment variable must be set",
        }

        for key, error_msg in required_configs.items():
            if not self.get(key):
                errors.append(error_msg)

        # Port validation
        port = self.get("port")
        if not (1 <= port <= 65535):
            errors.append(f"Port {port} is not in valid range (1-65535)")

        # Host validation
        host = self.get("host")
        if not host:
            errors.append("Host cannot be empty")

        # JWT expiration validation
        jwt_expiration = self.get("jwt_expiration_hours")
        if not (1 <= jwt_expiration <= 8760):  # Max 1 year
            errors.append(f"JWT expiration {jwt_expiration} hours is not reasonable (1-8760)")

        # Database pool validation
        db_pool_size = self.get("db_pool_size")
        db_max_overflow = self.get("db_max_overflow")
        if db_pool_size < 1:
            errors.append("Database pool size must be at least 1")
        if db_max_overflow < 0:
            errors.append("Database max overflow cannot be negative")

        return len(errors) == 0, errors

    def get_server_config(self) -> Tuple[str, int]:
        """Get server host and port configuration."""
        return self.get("host"), self.get("port")

    def get_database_config(self) -> Dict[str, Any]:
        """Get database-related configuration."""
        return {
            "url": self.get("database_url"),
            "pool_size": self.get("db_pool_size"),
            "max_overflow": self.get("db_max_overflow"),
            "connection_timeout": self.get("db_connection_timeout"),
        }

    def get_redis_config(self) -> Dict[str, Any]:
        """Get Redis-related configuration."""
        return {
            "url": self.get("redis_url"),
            "db": self.get("redis_db"),
            "retry_attempts": self.get("redis_retry_attempts"),
        }

    def get_security_config(self) -> Dict[str, Any]:
        """Get security-related configuration."""
        return {
            "jwt_secret_key": self.get("jwt_secret_key"),
            "jwt_algorithm": self.get("jwt_algorithm"),
            "jwt_expiration_hours": self.get("jwt_expiration_hours"),
            "cors_origins": self.get("cors_origins"),
        }

    def get_process_config(self) -> Dict[str, Any]:
        """Get process management configuration."""
        return {
            "pid_file": self.get("pid_file"),
            "graceful_timeout": self.get("graceful_timeout"),
            "health_check_timeout": self.get("health_check_timeout"),
        }

    def reload(self):
        """Reload configuration from environment."""
        logger.info("Reloading server configuration")
        self._load_config()

        is_valid, errors = self.validate()
        if not is_valid:
            logger.warning(f"Configuration validation failed after reload: {errors}")

    def export_to_env_file(self, file_path: str, include_sensitive: bool = False):
        """Export configuration to .env file format."""
        try:
            with open(file_path, 'w') as f:
                f.write("# Nigeria Conflict Tracker Configuration\n")
                f.write(f"# Generated at {os.environ.get('CURRENT_TIME', 'unknown')}\n\n")

                for key, value in self._config.items():
                    if not include_sensitive and key in {"jwt_secret_key", "openai_api_key", "anthropic_api_key"}:
                        f.write(f"# {key}=***masked***\n")
                    else:
                        f.write(f"{key.upper()}={value}\n")

            logger.info(f"Configuration exported to {file_path}")
        except Exception as e:
            logger.error(f"Failed to export configuration: {e}")

    def get_feature_flags(self) -> Dict[str, bool]:
        """Get feature flag configuration."""
        return {
            "analytics": self.get("enable_analytics"),
            "forecasting": self.get("enable_forecasting"),
            "notifications": self.get("enable_notifications"),
        }


# Global configuration instance
server_config = ServerConfig()


def get_server_config() -> ServerConfig:
    """Get the global server configuration instance."""
    return server_config


def validate_dependencies() -> list[str]:
    """Validate that all required dependencies are available and compatible."""
    errors = []

    # Check bcrypt
    try:
        import bcrypt
        if bcrypt.__version__ not in ["4.1.2", "3.2.2"]:
            errors.append(f"bcrypt version {bcrypt.__version__} may not be compatible, expected 4.1.2 or 3.2.2")
    except ImportError:
        errors.append("bcrypt package not found")
    except Exception as e:
        errors.append(f"bcrypt validation failed: {e}")

    # Check passlib
    try:
        from passlib.context import CryptContext
        ctx = CryptContext(schemes=['bcrypt'])
        # Test bcrypt functionality
        hashed = ctx.hash("test")
        ctx.verify("test", hashed)
    except Exception as e:
        errors.append(f"passlib bcrypt validation failed: {e}")

    # Check database connectivity (basic import check)
    try:
        import sqlalchemy
        import psycopg2
    except ImportError as e:
        errors.append(f"Database dependencies missing: {e}")

    # Check Redis connectivity (basic import check)
    try:
        import redis
    except ImportError:
        errors.append("redis package not found")

    # Check FastAPI and core dependencies
    try:
        import fastapi
        import uvicorn
        import pydantic
    except ImportError as e:
        errors.append(f"Core web framework dependencies missing: {e}")

    return errors