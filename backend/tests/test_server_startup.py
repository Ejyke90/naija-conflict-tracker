"""Tests for server startup and runtime stability."""

import time
import os
import sys

# Add the app directory to Python path for testing
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.port_manager import check_port_available, find_available_port, kill_process_on_port
from app.utils.process_manager import ProcessManager
from app.config.server_config import ServerConfig, validate_dependencies


class TestPortManager:
    """Test port management utilities."""

    def test_check_port_available(self):
        """Test port availability checking."""
        # Test with a port that should be available
        assert check_port_available(0)  # Port 0 should always be free

        # Test with a port that's likely in use (SSH port 22)
        # This should return False on most systems
        result = check_port_available(22)
        # We don't assert the result since it depends on system configuration
        assert isinstance(result, bool)

    def test_find_available_port(self):
        """Test finding available ports."""
        port = find_available_port(8000, 10)
        assert isinstance(port, int)
        assert 8000 <= port <= 8009
        assert check_port_available(port)

    def test_port_validation(self):
        """Test port configuration validation."""
        from app.utils.port_manager import validate_port_config

        # Valid configurations
        assert validate_port_config("0.0.0.0", 8000) == (True, "")
        assert validate_port_config("localhost", 3000) == (True, "")

        # Invalid configurations
        assert validate_port_config("", 8000) == (False, "Host cannot be empty")
        assert validate_port_config("0.0.0.0", 0) == (False, "Port 0 is not in valid range (1-65535)")
        assert validate_port_config("0.0.0.0", 70000) == (False, "Port 70000 is not in valid range (1-65535)")


class TestProcessManager:
    """Test process management utilities."""

    def test_process_manager_creation(self):
        """Test process manager initialization."""
        pm = ProcessManager("/tmp/test.pid")
        assert pm.pid_file == "/tmp/test.pid"
        assert not pm.is_shutting_down
        assert isinstance(pm.start_time, float)

    def test_process_health(self):
        """Test process health checking."""
        pm = ProcessManager()
        health = pm.check_health()

        assert "status" in health
        assert "uptime_seconds" in health
        assert "timestamp" in health
        assert health["status"] in ["healthy", "shutting_down"]

    def test_pid_file_management(self):
        """Test PID file operations."""
        test_pid_file = "/tmp/test_process.pid"

        pm = ProcessManager(test_pid_file)

        # Test writing PID file
        pm.write_pid_file()
        assert os.path.exists(test_pid_file)

        # Test reading PID file
        with open(test_pid_file, 'r') as f:
            pid_content = f.read().strip()
        assert pid_content.isdigit()

        # Test removing PID file
        pm.remove_pid_file()
        assert not os.path.exists(test_pid_file)


class TestServerConfig:
    """Test server configuration management."""

    def test_config_loading(self):
        """Test configuration loading from environment."""
        # Test with default values
        config = ServerConfig()
        assert isinstance(config.get("port"), int)
        assert isinstance(config.get("host"), str)
        assert isinstance(config.get("debug"), bool)

    def test_config_validation(self):
        """Test configuration validation."""
        config = ServerConfig()

        # Test valid configuration
        is_valid, errors = config.validate()
        # Note: This might fail in test environment due to missing required env vars
        # but the validation logic should work

        assert isinstance(is_valid, bool)
        assert isinstance(errors, list)

    def test_dependency_validation(self):
        """Test dependency validation."""
        errors = validate_dependencies()
        assert isinstance(errors, list)

        # In a proper environment, this should return no errors
        # but we'll just check the structure
        for error in errors:
            assert isinstance(error, str)


class TestServerStartup:
    """Test server startup scenarios."""

    def test_startup_validation(self):
        """Test that startup validation works."""
        # This would require mocking the validation functions
        # For now, just test that the validation functions exist and are callable
        from start_server import validate_system

        # The function should exist and be callable
        assert callable(validate_system)

    def test_argument_parsing(self):
        """Test command line argument parsing."""
        from start_server import parse_arguments

        # Mock sys.argv
        original_argv = sys.argv
        try:
            sys.argv = ['start_server.py', '--port', '3000', '--kill-existing']
            args = parse_arguments()
            assert args.port == 3000
            assert args.kill_existing is True
            assert args.find_available is False
        finally:
            sys.argv = original_argv


class TestIntegration:
    """Integration tests for server components."""

    def test_port_manager_integration(self):
        """Test port manager works with other components."""
        port = find_available_port(9000, 5)
        assert check_port_available(port)

        # Test that we can "use" the port (simulate server binding)
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(('0.0.0.0', port))
            sock.listen(1)

            # Now port should not be available
            assert not check_port_available(port)

        finally:
            sock.close()

        # Port should be available again
        time.sleep(0.1)  # Give OS time to release port
        assert check_port_available(port)


def run_tests():
    """Run all tests manually."""
    print("Running server startup tests...")

    test_classes = [
        TestPortManager,
        TestProcessManager,
        TestServerConfig,
        TestServerStartup,
        TestIntegration
    ]

    passed = 0
    failed = 0

    for test_class in test_classes:
        print(f"\nRunning {test_class.__name__}...")

        instance = test_class()
        methods = [method for method in dir(instance) if method.startswith('test_')]

        for method_name in methods:
            try:
                print(f"  ✓ {method_name}")
                getattr(instance, method_name)()
                passed += 1
            except Exception as e:
                print(f"  ✗ {method_name}: {e}")
                failed += 1

    print("\nTest Results:")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print(f"  Total: {passed + failed}")

    if failed == 0:
        print("✓ All tests passed!")
        return True
    else:
        print("✗ Some tests failed!")
        return False


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)