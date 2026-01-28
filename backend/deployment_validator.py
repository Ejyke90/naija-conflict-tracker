#!/usr/bin/env python3
"""Deployment validation script for Nigeria Conflict Tracker.

This script performs comprehensive pre-deployment and post-deployment validation
checks to ensure the application is ready for production deployment.
"""

import argparse
import logging
import sys
import os
import time
import requests
from typing import Dict, Any, List

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DeploymentValidator:
    """Comprehensive deployment validation."""

    def __init__(self, host: str = "localhost", port: int = 8000):
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"

    def run_pre_deployment_checks(self) -> Dict[str, Any]:
        """Run pre-deployment validation checks."""
        logger.info("Running pre-deployment validation checks...")

        results = {
            "timestamp": time.time(),
            "phase": "pre-deployment",
            "checks": {},
            "passed": True
        }

        # Configuration validation
        results["checks"]["configuration"] = self._check_configuration()
        if not results["checks"]["configuration"]["passed"]:
            results["passed"] = False

        # Dependency validation
        results["checks"]["dependencies"] = self._check_dependencies()
        if not results["checks"]["dependencies"]["passed"]:
            results["passed"] = False

        # Environment validation
        results["checks"]["environment"] = self._check_environment()
        if not results["checks"]["environment"]["passed"]:
            results["passed"] = False

        return results

    def run_post_deployment_checks(self) -> Dict[str, Any]:
        """Run post-deployment validation checks."""
        logger.info("Running post-deployment validation checks...")

        results = {
            "timestamp": time.time(),
            "phase": "post-deployment",
            "checks": {},
            "passed": True
        }

        # Health endpoint check
        results["checks"]["health_endpoint"] = self._check_health_endpoint()
        if not results["checks"]["health_endpoint"]["passed"]:
            results["passed"] = False

        # Readiness probe
        results["checks"]["readiness"] = self._check_readiness_probe()
        if not results["checks"]["readiness"]["passed"]:
            results["passed"] = False

        # Liveness probe
        results["checks"]["liveness"] = self._check_liveness_probe()
        if not results["checks"]["liveness"]["passed"]:
            results["passed"] = False

        # API functionality
        results["checks"]["api_functionality"] = self._check_api_functionality()
        if not results["checks"]["api_functionality"]["passed"]:
            results["passed"] = False

        return results

    def _check_configuration(self) -> Dict[str, Any]:
        """Check server configuration."""
        try:
            from app.config.server_config import ServerConfig
            config = ServerConfig()
            is_valid, errors = config.validate()

            return {
                "passed": is_valid,
                "errors": errors,
                "config_values": {
                    "port": config.get("port"),
                    "host": config.get("host"),
                    "debug": config.get("debug")
                }
            }
        except Exception as e:
            return {"passed": False, "error": str(e)}

    def _check_dependencies(self) -> Dict[str, Any]:
        """Check system dependencies."""
        try:
            from app.config.server_config import validate_dependencies
            errors = validate_dependencies()

            return {
                "passed": len(errors) == 0,
                "errors": errors
            }
        except Exception as e:
            return {"passed": False, "error": str(e)}

    def _check_environment(self) -> Dict[str, Any]:
        """Check deployment environment."""
        required_vars = ["DATABASE_URL", "JWT_SECRET_KEY"]
        missing_vars = []

        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        return {
            "passed": len(missing_vars) == 0,
            "missing_variables": missing_vars,
            "environment": os.getenv("ENVIRONMENT", "development")
        }

    def _check_health_endpoint(self) -> Dict[str, Any]:
        """Check health endpoint."""
        try:
            url = f"{self.base_url}/api/v1/monitoring/health"
            start_time = time.time()
            response = requests.get(url, timeout=10)
            response_time = time.time() - start_time

            health_data = response.json()

            return {
                "passed": response.status_code == 200 and health_data.get("status") == "healthy",
                "status_code": response.status_code,
                "response_time": response_time,
                "health_status": health_data.get("status"),
                "url": url
            }
        except Exception as e:
            return {"passed": False, "error": str(e)}

    def _check_readiness_probe(self) -> Dict[str, Any]:
        """Check readiness probe."""
        try:
            url = f"{self.base_url}/api/v1/monitoring/ready"
            start_time = time.time()
            response = requests.get(url, timeout=5)
            response_time = time.time() - start_time

            return {
                "passed": response.status_code == 200,
                "status_code": response.status_code,
                "response_time": response_time,
                "url": url
            }
        except Exception as e:
            return {"passed": False, "error": str(e)}

    def _check_liveness_probe(self) -> Dict[str, Any]:
        """Check liveness probe."""
        try:
            url = f"{self.base_url}/api/v1/monitoring/alive"
            start_time = time.time()
            response = requests.get(url, timeout=5)
            response_time = time.time() - start_time

            return {
                "passed": response.status_code == 200,
                "status_code": response.status_code,
                "response_time": response_time,
                "url": url
            }
        except Exception as e:
            return {"passed": False, "error": str(e)}

    def _check_api_functionality(self) -> Dict[str, Any]:
        """Check basic API functionality."""
        checks = {}

        # Test public health endpoint
        try:
            url = f"{self.base_url}/api/v1/public/health"
            response = requests.get(url, timeout=5)
            checks["public_health"] = {
                "passed": response.status_code == 200,
                "status_code": response.status_code
            }
        except Exception as e:
            checks["public_health"] = {"passed": False, "error": str(e)}

        # Test system metrics endpoint
        try:
            url = f"{self.base_url}/api/v1/monitoring/system-metrics"
            response = requests.get(url, timeout=5)
            checks["system_metrics"] = {
                "passed": response.status_code == 200,
                "status_code": response.status_code
            }
        except Exception as e:
            checks["system_metrics"] = {"passed": False, "error": str(e)}

        all_passed = all(check.get("passed", False) for check in checks.values())

        return {
            "passed": all_passed,
            "checks": checks
        }


def main():
    """Main validation function."""
    parser = argparse.ArgumentParser(description="Deployment validation for Nigeria Conflict Tracker")
    parser.add_argument(
        "--host",
        default="localhost",
        help="Server host (default: localhost)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Server port (default: 8000)"
    )
    parser.add_argument(
        "--phase",
        choices=["pre", "post", "both"],
        default="both",
        help="Validation phase (default: both)"
    )
    parser.add_argument(
        "--json-output",
        action="store_true",
        help="Output results as JSON"
    )

    args = parser.parse_args()

    validator = DeploymentValidator(args.host, args.port)

    results = {}

    if args.phase in ["pre", "both"]:
        results["pre_deployment"] = validator.run_pre_deployment_checks()

    if args.phase in ["post", "both"]:
        results["post_deployment"] = validator.run_post_deployment_checks()

    # Determine overall success
    all_passed = True
    for phase_result in results.values():
        if not phase_result.get("passed", False):
            all_passed = False
            break

    if args.json_output:
        import json
        results["overall_success"] = all_passed
        print(json.dumps(results, indent=2))
    else:
        # Print human-readable results
        for phase_name, phase_result in results.items():
            print(f"\n{phase_name.upper().replace('_', ' ')} RESULTS:")
            print(f"Status: {'PASSED' if phase_result['passed'] else 'FAILED'}")

            for check_name, check_result in phase_result["checks"].items():
                status = "✓" if check_result.get("passed", False) else "✗"
                print(f"  {status} {check_name}")
                if not check_result.get("passed", False):
                    if "error" in check_result:
                        print(f"    Error: {check_result['error']}")
                    if "errors" in check_result:
                        for error in check_result["errors"]:
                            print(f"    Error: {error}")

        print(f"\nOVERALL RESULT: {'SUCCESS' if all_passed else 'FAILURE'}")

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()