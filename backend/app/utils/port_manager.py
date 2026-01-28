"""Port management utilities for server startup and process handling."""

import socket
import subprocess
import sys
from typing import Optional, Tuple, Dict, Any
import logging

logger = logging.getLogger(__name__)


def check_port_available(port: int, host: str = "0.0.0.0") -> bool:
    """Check if a port is available for binding.

    Args:
        port: Port number to check
        host: Host address to check (default: 0.0.0.0)

    Returns:
        True if port is available, False if in use
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((host, port))
            return True
    except OSError:
        return False


def find_available_port(start_port: int = 8000, max_attempts: int = 10) -> int:
    """Find the next available port starting from start_port.

    Args:
        start_port: Port to start checking from
        max_attempts: Maximum number of ports to check

    Returns:
        Available port number

    Raises:
        RuntimeError: If no available port found within max_attempts
    """
    for port in range(start_port, start_port + max_attempts):
        if check_port_available(port):
            logger.info(f"Found available port: {port}")
            return port

    raise RuntimeError(f"No available port found in range {start_port}-{start_port + max_attempts - 1}")


def get_process_info(port: int) -> Optional[Dict[str, Any]]:
    """Get information about the process using a specific port.

    Args:
        port: Port number to check

    Returns:
        Dictionary with process information or None if port is free
    """
    try:
        # Use lsof to find process using the port
        result = subprocess.run(
            ["lsof", "-i", f":{port}"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0 and result.stdout.strip():
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:  # Skip header line
                parts = lines[1].split()
                if len(parts) >= 2:
                    return {
                        "command": parts[0],
                        "pid": int(parts[1]),
                        "user": parts[2] if len(parts) > 2 else "unknown",
                        "port": port
                    }

    except (subprocess.TimeoutExpired, subprocess.SubprocessError, ValueError) as e:
        logger.warning(f"Failed to get process info for port {port}: {e}")

    return None


def kill_process_on_port(port: int, force: bool = False) -> bool:
    """Kill the process using a specific port.

    Args:
        port: Port number
        force: Use SIGKILL instead of SIGTERM

    Returns:
        True if process was killed, False otherwise
    """
    process_info = get_process_info(port)
    if not process_info:
        logger.info(f"No process found using port {port}")
        return True

    pid = process_info["pid"]
    command = process_info["command"]

    logger.warning(f"Killing process {command} (PID: {pid}) using port {port}")

    try:
        signal = "-9" if force else "-TERM"
        result = subprocess.run(
            ["kill", signal, str(pid)],
            capture_output=True,
            timeout=10
        )

        if result.returncode == 0:
            logger.info(f"Successfully killed process {pid}")
            return True
        else:
            logger.error(f"Failed to kill process {pid}: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        logger.error(f"Timeout killing process {pid}")
        return False
    except Exception as e:
        logger.error(f"Error killing process {pid}: {e}")
        return False


def get_server_config() -> Tuple[str, int]:
    """Get server host and port configuration from environment or defaults.

    Returns:
        Tuple of (host, port)
    """
    import os

    host = os.getenv("HOST", "0.0.0.0")
    port_str = os.getenv("PORT", "8000")

    try:
        port = int(port_str)
    except ValueError:
        logger.warning(f"Invalid PORT value '{port_str}', using default 8000")
        port = 8000

    return host, port


def validate_port_config(host: str, port: int) -> Tuple[bool, str]:
    """Validate host and port configuration.

    Args:
        host: Host address
        port: Port number

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not (1 <= port <= 65535):
        return False, f"Port {port} is not in valid range (1-65535)"

    if not host:
        return False, "Host cannot be empty"

    # Basic IP address validation
    try:
        socket.inet_aton(host)
    except socket.error:
        # Allow localhost and 0.0.0.0
        if host not in ["localhost", "0.0.0.0"]:
            return False, f"Invalid host address: {host}"

    return True, ""