"""
n8n API Client

Provides a Python client for interacting with n8n REST API.
Supports workflow import/export, version detection, and validation.

Author: Project Automata - Agent 3
Version: 1.0.0
Created: 2025-11-20

API Documentation: https://docs.n8n.io/api/
Authentication: X-N8N-API-KEY header
"""

import logging
import time
from typing import Any, Dict, List, Optional, Tuple

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Application should configure logging, not libraries
# logging.basicConfig() removed to prevent global logging configuration conflicts
logger = logging.getLogger(__name__)


class N8nApiError(Exception):
    """Base exception for n8n API errors"""

    pass


class N8nAuthenticationError(N8nApiError):
    """Raised when authentication fails"""

    pass


class N8nConnectionError(N8nApiError):
    """Raised when connection to n8n fails"""

    pass


class N8nValidationError(N8nApiError):
    """Raised when workflow validation fails"""

    pass


class N8nRateLimitError(N8nApiError):
    """Raised when rate limit is exceeded"""

    pass


class N8nApiClient:
    """
    Client for interacting with n8n REST API.

    Features:
    - Workflow import/export
    - Version detection
    - Validation
    - Error handling with retry logic
    - Rate limiting support

    Example:
        client = N8nApiClient(api_url="http://localhost:5678", api_key="your-key")
        version = client.get_n8n_version()
        workflow_id = client.import_workflow(workflow_json)
    """

    def __init__(
        self,
        api_url: str,
        api_key: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        rate_limit_requests: int = 60,
        rate_limit_period: int = 60,
    ):
        """
        Initialize n8n API client.

        Args:
            api_url: Base URL of n8n API (e.g., "http://localhost:5678" or "https://n8n.example.com")
            api_key: n8n API key (from Settings > n8n API)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            rate_limit_requests: Maximum requests per period
            rate_limit_period: Rate limit period in seconds
        """
        # Clean up API URL - remove trailing slash and /api/v1 if present
        self.base_url = api_url.rstrip("/")
        if self.base_url.endswith("/api/v1"):
            self.base_url = self.base_url[:-7]

        self.api_url = f"{self.base_url}/api/v1"
        self.api_key = api_key
        self.timeout = timeout

        # Rate limiting
        self.rate_limit_requests = rate_limit_requests
        self.rate_limit_period = rate_limit_period
        self._request_times: List[float] = []

        # Configure session with retry logic
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            # SECURITY: POST and PATCH removed from retry list to prevent duplicate mutations
            # Retrying non-idempotent operations can cause data corruption
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Set default headers
        self.session.headers.update(
            {"Accept": "application/json", "Content-Type": "application/json"}
        )

        if self.api_key:
            self.session.headers.update({"X-N8N-API-KEY": self.api_key})

        logger.debug(f"Initialized n8n API client for {self.api_url}")

    def __enter__(self) -> "N8nApiClient":
        """Context manager entry - returns self for use in 'with' statements."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - ensures session is properly closed."""
        self.close()
        return None  # Don't suppress exceptions

    def close(self) -> None:
        """
        Close the HTTP session and release resources.

        Should be called when done using the client, or use context manager:

            with N8nApiClient(api_url, api_key) as client:
                client.list_workflows()
            # Session automatically closed
        """
        if self.session:
            self.session.close()
            logger.debug("Closed n8n API client session")

    def _check_rate_limit(self):
        """Check and enforce rate limiting."""
        now = time.time()

        # Remove requests outside the current period
        self._request_times = [t for t in self._request_times if now - t < self.rate_limit_period]

        # Check if we've exceeded the limit
        if len(self._request_times) >= self.rate_limit_requests:
            oldest_request = self._request_times[0]
            wait_time = self.rate_limit_period - (now - oldest_request)
            if wait_time > 0:
                logger.warning(f"Rate limit reached, waiting {wait_time:.2f}s")
                raise N8nRateLimitError(
                    f"Rate limit exceeded. Wait {wait_time:.2f}s before retrying."
                )

        # Record this request
        self._request_times.append(now)

    def _request(
        self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to n8n API with error handling.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without /api/v1 prefix)
            data: Request body data
            params: Query parameters

        Returns:
            Response JSON data

        Raises:
            N8nAuthenticationError: If authentication fails
            N8nConnectionError: If connection fails
            N8nApiError: For other API errors
        """
        self._check_rate_limit()

        url = f"{self.api_url}/{endpoint.lstrip('/')}"

        try:
            logger.debug(f"{method} {url}")
            response = self.session.request(
                method=method, url=url, json=data, params=params, timeout=self.timeout
            )

            # Handle authentication errors
            if response.status_code == 401:
                raise N8nAuthenticationError("Authentication failed. Check your API key.")

            # Handle rate limiting
            if response.status_code == 429:
                raise N8nRateLimitError("Rate limit exceeded. Please wait before retrying.")

            # Raise for other HTTP errors
            response.raise_for_status()

            # Return JSON response if available
            if response.content:
                return response.json()
            return {}

        except requests.exceptions.Timeout:
            raise N8nConnectionError(f"Request timeout after {self.timeout}s")

        except requests.exceptions.ConnectionError as e:
            raise N8nConnectionError(f"Connection failed: {str(e)}")

        except requests.exceptions.HTTPError:
            error_msg = f"HTTP {response.status_code}: {response.text}"
            logger.error(error_msg)
            raise N8nApiError(error_msg)

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise N8nApiError(f"Unexpected error: {str(e)}")

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

    def get_n8n_version(self) -> Dict[str, Any]:
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

    def list_workflows(
        self,
        limit: Optional[int] = None,
        active: Optional[bool] = None,
        tags: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        List workflows from n8n.

        Args:
            limit: Maximum number of workflows to return
            active: Filter by active status
            tags: Filter by tags

        Returns:
            List of workflow objects
        """
        params = {}
        if limit is not None:
            params["limit"] = limit
        if active is not None:
            params["active"] = str(active).lower()
        if tags:
            params["tags"] = ",".join(tags)

        response = self._request("GET", "/workflows", params=params)

        # Response structure: {"data": [...]}
        return response.get("data", [])

    def get_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Get a specific workflow by ID.

        Args:
            workflow_id: Workflow ID

        Returns:
            Workflow object
        """
        return self._request("GET", f"/workflows/{workflow_id}")

    def import_workflow(
        self, workflow_data: Dict[str, Any], activate: bool = False
    ) -> Dict[str, Any]:
        """
        Import a workflow to n8n (create new workflow).

        Args:
            workflow_data: Workflow JSON object
            activate: Whether to activate the workflow immediately

        Returns:
            Created workflow object with ID

        Raises:
            N8nValidationError: If workflow validation fails
            N8nApiError: If import fails
        """
        # Validate basic structure
        if not isinstance(workflow_data, dict):
            raise N8nValidationError("Workflow data must be a dictionary")

        if "nodes" not in workflow_data:
            raise N8nValidationError("Workflow must contain 'nodes' field")

        if "connections" not in workflow_data:
            raise N8nValidationError("Workflow must contain 'connections' field")

        # Set active status
        workflow_data["active"] = activate

        try:
            response = self._request("POST", "/workflows", data=workflow_data)
            logger.info(f"Imported workflow: {response.get('name', 'Unknown')}")
            return response
        except N8nApiError as e:
            logger.error(f"Failed to import workflow: {str(e)}")
            raise

    def export_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Export a workflow from n8n.

        Args:
            workflow_id: Workflow ID to export

        Returns:
            Workflow JSON object
        """
        workflow = self.get_workflow(workflow_id)
        logger.info(f"Exported workflow: {workflow.get('name', 'Unknown')}")
        return workflow

    def update_workflow(self, workflow_id: str, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing workflow.

        Args:
            workflow_id: Workflow ID to update
            workflow_data: Updated workflow data

        Returns:
            Updated workflow object
        """
        response = self._request("PUT", f"/workflows/{workflow_id}", data=workflow_data)
        logger.info(f"Updated workflow: {workflow_id}")
        return response

    def delete_workflow(self, workflow_id: str) -> bool:
        """
        Delete a workflow from n8n.

        Args:
            workflow_id: Workflow ID to delete

        Returns:
            True if deletion successful
        """
        self._request("DELETE", f"/workflows/{workflow_id}")
        logger.info(f"Deleted workflow: {workflow_id}")
        return True

    def activate_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Activate a workflow.

        Args:
            workflow_id: Workflow ID to activate

        Returns:
            Updated workflow object

        Note:
            Uses PATCH to atomically update only the 'active' field,
            avoiding TOCTOU (Time-Of-Check-Time-Of-Use) race conditions.
        """
        # Use PATCH to atomically update just the 'active' field
        # This avoids race condition from GET → modify → PUT pattern
        response = self._request("PATCH", f"/workflows/{workflow_id}", data={"active": True})
        logger.info(f"Activated workflow: {workflow_id}")
        return response

    def deactivate_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Deactivate a workflow.

        Args:
            workflow_id: Workflow ID to deactivate

        Returns:
            Updated workflow object

        Note:
            Uses PATCH to atomically update only the 'active' field,
            avoiding TOCTOU (Time-Of-Check-Time-Of-Use) race conditions.
        """
        # Use PATCH to atomically update just the 'active' field
        # This avoids race condition from GET → modify → PUT pattern
        response = self._request("PATCH", f"/workflows/{workflow_id}", data={"active": False})
        logger.info(f"Deactivated workflow: {workflow_id}")
        return response

    def validate_workflow_import(self, workflow_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate that a workflow can be imported without actually importing it.

        Args:
            workflow_data: Workflow JSON to validate

        Returns:
            Tuple of (is_valid: bool, errors: List[str])
        """
        errors = []

        # Check required fields
        required_fields = ["name", "nodes", "connections"]
        for field in required_fields:
            if field not in workflow_data:
                errors.append(f"Missing required field: {field}")

        # Validate nodes
        if "nodes" in workflow_data:
            if not isinstance(workflow_data["nodes"], list):
                errors.append("'nodes' must be a list")
            elif len(workflow_data["nodes"]) == 0:
                errors.append("Workflow must have at least one node")
            else:
                # Check each node
                for i, node in enumerate(workflow_data["nodes"]):
                    if not isinstance(node, dict):
                        errors.append(f"Node {i} is not a dictionary")
                        continue

                    node_required = ["name", "type", "position", "parameters"]
                    for field in node_required:
                        if field not in node:
                            errors.append(f"Node {i} missing required field: {field}")

        # Validate connections
        if "connections" in workflow_data:
            if not isinstance(workflow_data["connections"], dict):
                errors.append("'connections' must be a dictionary")

        return len(errors) == 0, errors

    def test_workflow_execution(
        self, workflow_id: str, input_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Test execute a workflow (manual execution).

        Note: This is an advanced feature and may not be available in all n8n versions.

        Args:
            workflow_id: Workflow ID to execute
            input_data: Optional input data for the workflow

        Returns:
            Execution result
        """
        # Note: Workflow execution via API may require specific n8n configuration
        # and may not be available in all versions
        try:
            endpoint = f"/workflows/{workflow_id}/execute"
            data = input_data or {}
            response = self._request("POST", endpoint, data=data)
            logger.info(f"Executed workflow: {workflow_id}")
            return response
        except N8nApiError as e:
            logger.warning(f"Workflow execution not available or failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "note": "Workflow execution via API may not be available in your n8n version",
            }

    def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check.

        Returns:
            Dictionary with health check results
        """
        results = {"timestamp": time.time(), "checks": {}}

        # Test connection
        conn_ok, conn_msg = self.test_connection()
        results["checks"]["connection"] = {
            "status": "ok" if conn_ok else "error",
            "message": conn_msg,
        }

        # Test version detection
        version_info = self.get_n8n_version()
        results["checks"]["version"] = {
            "status": "ok" if version_info.get("success") else "warning",
            "version": version_info.get("version", "unknown"),
            "method": version_info.get("method", "none"),
        }

        # Test workflow listing
        try:
            workflows = self.list_workflows(limit=1)
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


# Convenience function for quick testing
def create_client_from_env() -> Optional[N8nApiClient]:
    """
    Create N8nApiClient from environment variables.

    Looks for:
    - N8N_API_URL
    - N8N_API_KEY

    Returns:
        N8nApiClient instance or None if config not available
    """
    import os

    api_url = os.getenv("N8N_API_URL")
    api_key = os.getenv("N8N_API_KEY")

    if not api_url:
        logger.error("N8N_API_URL not set in environment")
        return None

    return N8nApiClient(api_url=api_url, api_key=api_key)


# ==========================================
# BACKWARDS COMPATIBILITY NOTE
# ==========================================
# This monolithic client is maintained for backwards compatibility.
# For new code, prefer the modular clients in skills/n8n/:
#
#   from skills.n8n import N8nClient, WorkflowClient, HealthClient
#
#   # Unified client (recommended)
#   with N8nClient(api_url, api_key) as client:
#       workflows = client.list_workflows()
#
#   # Or specialized clients for specific needs
#   with WorkflowClient(api_url, api_key) as wf_client:
#       workflow = wf_client.get_workflow(id)
# ==========================================


if __name__ == "__main__":
    # Example usage
    print("n8n API Client")
    print("=" * 50)

    client = create_client_from_env()
    if not client:
        print("Error: Could not create client from environment variables")
        print("Please set N8N_API_URL and N8N_API_KEY")
        exit(1)

    # Test connection
    print("\n1. Testing connection...")
    ok, msg = client.test_connection()
    print(f"   {msg}")

    if ok:
        # Get version
        print("\n2. Detecting n8n version...")
        version = client.get_n8n_version()
        print(f"   Version: {version.get('version', 'unknown')}")
        print(f"   Method: {version.get('method', 'unknown')}")

        # List workflows
        print("\n3. Listing workflows...")
        workflows = client.list_workflows(limit=5)
        print(f"   Found {len(workflows)} workflow(s)")
        for wf in workflows:
            print(f"   - {wf.get('name')} (ID: {wf.get('id')})")

        # Health check
        print("\n4. Health check...")
        health = client.health_check()
        print(f"   Overall: {health['overall_status']}")
        for check_name, check_result in health["checks"].items():
            print(f"   - {check_name}: {check_result['status']}")

    print("\n" + "=" * 50)
