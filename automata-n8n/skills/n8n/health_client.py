"""
Health Client

Handles health check and version detection operations:
- Testing connection
- Getting n8n version
- Comprehensive health checks

Author: Project Automata - Architecture Specialist
Version: 2.0.0
Created: 2025-11-21
"""

import logging
import time
from typing import Any, Dict, Tuple

from .base_client import (
    BaseN8nClient,
    N8nAuthenticationError,
    N8nConnectionError,
)

logger = logging.getLogger(__name__)


class HealthClient(BaseN8nClient):
    """
    Client for health check and version detection operations.

    Provides methods for testing connectivity, detecting n8n version,
    and performing comprehensive health checks.
    """

    def test_connection(self) -> Tuple[bool, str]:
        """
        Test connection to n8n API.

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Try to get workflows list as a simple connectivity test
            self._request("GET", "/workflows", params={"limit": 1})
            return True, "Connection successful"
        except N8nAuthenticationError as e:
            return False, f"Authentication failed: {str(e)}"
        except N8nConnectionError as e:
            return False, f"Connection failed: {str(e)}"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def get_version(self) -> Dict[str, Any]:
        """
        Detect n8n instance version.

        Returns:
            Dictionary with version information:
            {
                "version": "1.70.0",
                "success": True,
                "method": "workflows_list"  # Method used to detect version
            }

        Note:
            n8n doesn't have a dedicated version endpoint in all versions.
            This method tries multiple approaches to detect the version.
        """
        try:
            # Method 1: Try to get version from root endpoint
            try:
                response = self.session.get(f"{self.base_url}/", timeout=self.timeout)
                if response.ok and "n8n" in response.text.lower():
                    # Try to extract version from HTML/response
                    import re

                    version_match = re.search(
                        r'version["\s:]+([0-9.]+)', response.text, re.IGNORECASE
                    )
                    if version_match:
                        return {
                            "version": version_match.group(1),
                            "success": True,
                            "method": "root_endpoint",
                        }
            except Exception:
                pass

            # Method 2: Check if workflows endpoint is available (indicates API is working)
            self._request("GET", "/workflows", params={"limit": 1})

            # If we can access workflows, API is working
            # We can infer version based on available features
            return {
                "version": "1.x",  # Generic version if specific version unavailable
                "success": True,
                "method": "workflows_list",
                "note": "Exact version detection unavailable. API is functional.",
            }

        except Exception as e:
            logger.warning(f"Could not detect n8n version: {str(e)}")
            return {"version": "unknown", "success": False, "error": str(e)}

    def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check.

        Returns:
            Dictionary with health check results including:
            - Connection status
            - Version detection
            - Workflow API access
            - Overall health status
        """
        results = {"timestamp": time.time(), "checks": {}}

        # Test connection
        conn_ok, conn_msg = self.test_connection()
        results["checks"]["connection"] = {
            "status": "ok" if conn_ok else "error",
            "message": conn_msg,
        }

        # Test version detection
        version_info = self.get_version()
        results["checks"]["version"] = {
            "status": "ok" if version_info.get("success") else "warning",
            "version": version_info.get("version", "unknown"),
            "method": version_info.get("method", "none"),
        }

        # Test workflow listing
        try:
            # Import here to avoid circular dependency
            from .workflow_client import WorkflowClient

            # Create workflow client with same config
            wf_client = WorkflowClient(
                api_url=self.base_url,
                api_key=self.api_key,
                timeout=self.timeout,
            )
            workflows = wf_client.list_workflows(limit=1)
            results["checks"]["workflows"] = {
                "status": "ok",
                "message": f"Can access workflows (found {len(workflows)})",
            }
        except Exception as e:
            results["checks"]["workflows"] = {"status": "error", "message": str(e)}

        # Overall status
        all_ok = all(check["status"] == "ok" for check in results["checks"].values())
        results["overall_status"] = "healthy" if all_ok else "degraded"

        return results
