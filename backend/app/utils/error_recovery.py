"""Error recovery and retry utilities for robust service operation."""

import asyncio
import logging
import random
import time
from typing import Any, Callable, Optional, TypeVar, Union
from contextlib import asynccontextmanager
import functools

logger = logging.getLogger(__name__)

T = TypeVar('T')


class RetryConfig:
    """Configuration for retry behavior."""

    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_factor: float = 2.0,
        jitter: bool = True,
        retry_on: tuple = (Exception,)
    ):
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter
        self.retry_on = retry_on


class CircuitBreaker:
    """Circuit breaker pattern implementation."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: tuple = (Exception,)
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half_open

    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt to reset."""
        if self.state != "open":
            return True

        if self.last_failure_time is None:
            return True

        return (time.time() - self.last_failure_time) >= self.recovery_timeout

    def _record_success(self):
        """Record a successful operation."""
        self.failure_count = 0
        self.state = "closed"
        logger.debug("Circuit breaker: success recorded, state=closed")

    def _record_failure(self):
        """Record a failed operation."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = "open"
            logger.warning(f"Circuit breaker: failure threshold reached, state=open")
        else:
            logger.debug(f"Circuit breaker: failure recorded ({self.failure_count}/{self.failure_threshold})")

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        if not self._should_attempt_reset():
            raise CircuitBreakerOpenException("Circuit breaker is open")

        try:
            result = func(*args, **kwargs)
            self._record_success()
            return result
        except self.expected_exception as e:
            self._record_failure()
            raise


class CircuitBreakerOpenException(Exception):
    """Exception raised when circuit breaker is open."""
    pass


def retry(
    config: Optional[RetryConfig] = None,
    **retry_kwargs
) -> Callable:
    """Decorator for retrying functions on failure.

    Args:
        config: RetryConfig instance
        **retry_kwargs: Retry configuration overrides
    """
    if config is None:
        config = RetryConfig()

    # Override config with kwargs
    for key, value in retry_kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None

            for attempt in range(config.max_attempts):
                try:
                    return func(*args, **kwargs)
                except config.retry_on as e:
                    last_exception = e

                    if attempt + 1 == config.max_attempts:
                        logger.error(f"Function {func.__name__} failed after {config.max_attempts} attempts: {e}")
                        raise

                    # Calculate delay with exponential backoff
                    delay = min(
                        config.initial_delay * (config.backoff_factor ** attempt),
                        config.max_delay
                    )

                    # Add jitter
                    if config.jitter:
                        delay = delay * (0.5 + random.random() * 0.5)

                    logger.warning(f"Function {func.__name__} failed (attempt {attempt + 1}/{config.max_attempts}): {e}. Retrying in {delay:.2f}s")
                    time.sleep(delay)

            # This should never be reached, but just in case
            raise last_exception

        return wrapper
    return decorator


async def retry_async(
    config: Optional[RetryConfig] = None,
    **retry_kwargs
) -> Callable:
    """Decorator for retrying async functions on failure."""
    if config is None:
        config = RetryConfig()

    # Override config with kwargs
    for key, value in retry_kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            last_exception = None

            for attempt in range(config.max_attempts):
                try:
                    return await func(*args, **kwargs)
                except config.retry_on as e:
                    last_exception = e

                    if attempt + 1 == config.max_attempts:
                        logger.error(f"Async function {func.__name__} failed after {config.max_attempts} attempts: {e}")
                        raise

                    # Calculate delay with exponential backoff
                    delay = min(
                        config.initial_delay * (config.backoff_factor ** attempt),
                        config.max_delay
                    )

                    # Add jitter
                    if config.jitter:
                        delay = delay * (0.5 + random.random() * 0.5)

                    logger.warning(f"Async function {func.__name__} failed (attempt {attempt + 1}/{config.max_attempts}): {e}. Retrying in {delay:.2f}s")
                    await asyncio.sleep(delay)

            # This should never be reached, but just in case
            raise last_exception

        return wrapper
    return decorator


class DependencyChecker:
    """Checks health of external dependencies."""

    def __init__(self):
        self.checkers = {}
        self.circuit_breakers = {}

    def register_checker(self, name: str, checker_func: Callable, circuit_breaker: Optional[CircuitBreaker] = None):
        """Register a dependency health checker."""
        self.checkers[name] = checker_func
        if circuit_breaker:
            self.circuit_breakers[name] = circuit_breaker
        logger.debug(f"Registered dependency checker: {name}")

    def check_dependency(self, name: str) -> tuple[bool, str]:
        """Check a specific dependency.

        Returns:
            Tuple of (is_healthy, status_message)
        """
        if name not in self.checkers:
            return False, f"No checker registered for {name}"

        checker = self.checkers[name]
        circuit_breaker = self.circuit_breakers.get(name)

        try:
            if circuit_breaker:
                result = circuit_breaker.call(checker)
            else:
                result = checker()

            if isinstance(result, tuple):
                return result
            elif isinstance(result, bool):
                return result, "OK" if result else "Failed"
            else:
                return True, str(result)

        except CircuitBreakerOpenException:
            return False, "Circuit breaker open"
        except Exception as e:
            return False, f"Check failed: {e}"

    def check_all_dependencies(self) -> dict:
        """Check all registered dependencies.

        Returns:
            Dict mapping dependency names to (is_healthy, status_message) tuples
        """
        results = {}
        for name in self.checkers:
            results[name] = self.check_dependency(name)
        return results

    def get_health_summary(self) -> dict:
        """Get overall health summary."""
        all_results = self.check_all_dependencies()

        healthy = sum(1 for status, _ in all_results.values() if status)
        total = len(all_results)

        return {
            "overall_healthy": healthy == total,
            "healthy_count": healthy,
            "total_count": total,
            "details": all_results
        }


# Global dependency checker instance
dependency_checker = DependencyChecker()


def get_dependency_checker() -> DependencyChecker:
    """Get the global dependency checker instance."""
    return dependency_checker


@asynccontextmanager
@asynccontextmanager
async def error_boundary(fallback: Optional[Any] = None, log_errors: bool = True):
    """Async context manager for error boundaries."""
    try:
        yield
    except Exception as e:
        if log_errors:
            logger.error(f"Error in error boundary: {e}", exc_info=True)
        if fallback is not None:
            # Can't return in async generator, so we'll just log and continue
            logger.info(f"Using fallback: {fallback}")
        else:
            raise


def with_fallback(primary: Callable, fallback: Callable, *args, **kwargs) -> Any:
    """Execute primary function, fall back to secondary on failure."""
    try:
        return primary(*args, **kwargs)
    except Exception as e:
        logger.warning(f"Primary function failed, using fallback: {e}")
        try:
            return fallback(*args, **kwargs)
        except Exception as fallback_error:
            logger.error(f"Both primary and fallback functions failed. Primary: {e}, Fallback: {fallback_error}")
            raise fallback_error