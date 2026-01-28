"""Process management utilities for server lifecycle and signal handling."""

import atexit
import logging
import os
import signal
import sys
from typing import Callable, Optional
import time

logger = logging.getLogger(__name__)


class ProcessManager:
    """Manages server process lifecycle, signals, and cleanup."""

    def __init__(self, pid_file: str = "/tmp/naija-api.pid"):
        self.pid_file = pid_file
        self.shutdown_handlers: list[Callable] = []
        self.is_shutting_down = False
        self.start_time = time.time()

    def setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

        # Register cleanup on exit
        atexit.register(self.graceful_shutdown)

        logger.info("Signal handlers registered for graceful shutdown")

    def _signal_handler(self, signum: int, frame) -> None:
        """Handle shutdown signals."""
        signal_name = signal.Signals(signum).name
        logger.info(f"Received signal {signal_name} ({signum}), initiating graceful shutdown")

        self.graceful_shutdown(signum)

    def graceful_shutdown(self, signum: int = signal.SIGTERM) -> None:
        """Perform graceful shutdown with cleanup."""
        if self.is_shutting_down:
            logger.warning("Shutdown already in progress")
            return

        self.is_shutting_down = True
        logger.info("Starting graceful shutdown sequence")

        try:
            # Execute all registered shutdown handlers
            for handler in self.shutdown_handlers:
                try:
                    handler()
                except Exception as e:
                    logger.error(f"Error in shutdown handler: {e}")

            # Remove PID file
            self.remove_pid_file()

            logger.info("Graceful shutdown completed")

        except Exception as e:
            logger.error(f"Error during graceful shutdown: {e}")
        finally:
            # Force exit after cleanup
            sys.exit(0)

    def register_shutdown_handler(self, handler: Callable) -> None:
        """Register a function to be called during shutdown."""
        self.shutdown_handlers.append(handler)
        logger.debug(f"Registered shutdown handler: {handler.__name__}")

    def write_pid_file(self) -> None:
        """Write current process ID to PID file."""
        try:
            pid = os.getpid()
            with open(self.pid_file, 'w') as f:
                f.write(str(pid))
            logger.info(f"PID file written: {self.pid_file} (PID: {pid})")
        except Exception as e:
            logger.error(f"Failed to write PID file {self.pid_file}: {e}")

    def remove_pid_file(self) -> None:
        """Remove PID file."""
        try:
            if os.path.exists(self.pid_file):
                os.remove(self.pid_file)
                logger.info(f"PID file removed: {self.pid_file}")
        except Exception as e:
            logger.error(f"Failed to remove PID file {self.pid_file}: {e}")

    def is_process_running(self, pid: int) -> bool:
        """Check if a process with given PID is running."""
        try:
            os.kill(pid, 0)  # Signal 0 doesn't kill, just checks if process exists
            return True
        except OSError:
            return False

    def get_process_info(self) -> dict:
        """Get information about the current process."""
        return {
            "pid": os.getpid(),
            "ppid": os.getppid(),
            "uptime": time.time() - self.start_time,
            "memory_usage": self._get_memory_usage(),
            "pid_file": self.pid_file,
            "is_shutting_down": self.is_shutting_down
        }

    def _get_memory_usage(self) -> Optional[float]:
        """Get current process memory usage in MB."""
        try:
            import psutil
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / 1024 / 1024  # Convert to MB
        except ImportError:
            # psutil not available, return None
            return None
        except Exception as e:
            logger.debug(f"Could not get memory usage: {e}")
            return None

    def check_health(self) -> dict:
        """Check process health status."""
        info = self.get_process_info()
        return {
            "status": "healthy" if not self.is_shutting_down else "shutting_down",
            "uptime_seconds": info["uptime"],
            "memory_mb": info["memory_usage"],
            "pid": info["pid"],
            "timestamp": time.time()
        }


# Global process manager instance
process_manager = ProcessManager()


def setup_process_management(pid_file: str = "/tmp/naija-api.pid") -> ProcessManager:
    """Setup global process management.

    Args:
        pid_file: Path to PID file

    Returns:
        Configured ProcessManager instance
    """
    global process_manager
    process_manager = ProcessManager(pid_file)
    process_manager.setup_signal_handlers()
    process_manager.write_pid_file()

    return process_manager


def get_process_manager() -> ProcessManager:
    """Get the global process manager instance."""
    return process_manager