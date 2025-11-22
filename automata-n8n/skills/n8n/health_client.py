"""
n8n Health Client

Handles health checks and version detection.

Author: Project Automata
Version: 2.0.0
"""

import logging
import re
import time
from typing import Any, Dict, Tuple

from .base_client import BaseN8nClient

logger = logging.getLogger(__name__)


class HealthClient(BaseN8nClient):
    """
    Client for n8n health and version operations.
    """

    def test_connection(self) -> Tuple[bool, str]:
        """
        Test connection to n8n API.

        Returns:
            Tuple of (success, message)
        """
        try:
            self._request("GET", "/workflows", params={"limit": 1})
            return True, "Connection successful"
        except Exception as e:
            return False, f"Connection failed: {e}"

    def get_version(self) -> Dict[str, Any]:
        """
        Detect n8n instance version.

        Returns:
            Version information dict
        """
        try:
            # Try root endpoint first
            try:
                response = self.session.get(
                    f"{self.base_url}/",
                    timeout=self.timeout
                )
                if response.ok and "n8n" in response.text.lower():
                    version_match = re.search(
                        r'version["\s:]+([0-9.]+)',
                        response.text,
                        re.IGNORECASE
                    )
                    if version_match:
                        return {
                            "version": version_match.group(1),
                            "success": True,
                            "method": "root_endpoint"
                        }
            except Exception:
                pass

            # Fallback: verify API is working
            self._request("GET", "/workflows", params={"limit": 1})

            return {
                "version": "1.x",
                "success": True,
                "method": "api_check",
                "note": "Exact version unavailable"
            }

        except Exception as e:
            logger.warning(f"Version detection failed: {e}")
            return {
                "version": "unknown",
                "success": False,
                "error": str(e)
            }

    def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check.

        Returns:
            Health check results
        """
        results = {
            "timestamp": time.time(),
            "checks": {}
        }

        # Connection check
        conn_ok, conn_msg = self.test_connection()
        results["checks"]["connection"] = {
            "status": "ok" if conn_ok else "error",
            "message": conn_msg
        }

        # Version check
        version_info = self.get_version()
        results["checks"]["version"] = {
            "status": "ok" if version_info.get("success") else "warning",
            "version": version_info.get("version", "unknown"),
            "method": version_info.get("method", "none")
        }

        # API access check
        try:
            from .workflow_client import WorkflowClient
            # Create temporary workflow client to check
            wf_client = WorkflowClient(
                api_url=self.base_url,
                api_key=self.api_key,
                timeout=self.timeout
            )
            try:
                workflows = wf_client.list_workflows(limit=1)
                results["checks"]["api_access"] = {
                    "status": "ok",
                    "message": f"API accessible ({len(workflows)} workflows found)"
                }
            finally:
                wf_client.close()
        except Exception as e:
            results["checks"]["api_access"] = {
                "status": "error",
                "message": str(e)
            }

        # Overall status
        all_ok = all(
            check["status"] == "ok"
            for check in results["checks"].values()
        )
        results["overall_status"] = "healthy" if all_ok else "degraded"

        return results
