"""
n8n API Client (Refactored with Facade Pattern)

Provides a Python client for interacting with n8n REST API.
Supports workflow import/export, version detection, and validation.

Author: Project Automata - Architecture Specialist
Version: 2.0.0 (Refactored)
Created: 2025-11-20
Updated: 2025-11-21 (Architecture refactoring)

API Documentation: https://docs.n8n.io/api/
Authentication: X-N8N-API-KEY header

Architecture:
- N8nApiClient: Facade pattern that delegates to specialized clients
- WorkflowClient: Workflow CRUD operations
- ExecutionClient: Execution operations
- HealthClient: Health checks and version detection
- BaseN8nClient: Shared HTTP/session management

Breaking Changes from v1.0.0:
- None (backward compatible facade)

Deprecations:
- Direct instantiation of clients other than N8nApiClient is discouraged
  but supported for advanced use cases
"""

import logging
import warnings
from typing import Any, Dict, List, Optional, Tuple

# Import exception classes from base client
from .n8n.base_client import (
    N8nApiError,
    N8nAuthenticationError,
    N8nConnectionError,
    N8nValidationError,
    N8nRateLimitError,
)

# Import specialized clients
from .n8n.workflow_client import WorkflowClient
from .n8n.execution_client import ExecutionClient
from .n8n.health_client import HealthClient

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


class N8nApiClient:
    """
    Facade for interacting with n8n REST API.

    This class delegates to specialized clients:
    - WorkflowClient: For workflow operations
    - ExecutionClient: For execution operations
    - HealthClient: For health/version operations

    Features:
    - Workflow import/export
    - Version detection
    - Validation
    - Error handling with retry logic
    - Rate limiting support

    Thread Safety:
        All clients are thread-safe for rate limiting.
        However, requests.Session is NOT inherently thread-safe.
        For multi-threaded applications, create one client instance per thread.

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
        Initialize n8n API client (facade).

        Args:
            api_url: Base URL of n8n API (e.g., "http://localhost:5678")
            api_key: n8n API key (from Settings > n8n API)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            rate_limit_requests: Maximum requests per period
            rate_limit_period: Rate limit period in seconds
        """
        # Store configuration
        self.api_url = api_url
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.rate_limit_requests = rate_limit_requests
        self.rate_limit_period = rate_limit_period

        # Initialize specialized clients with shared configuration
        self._workflow_client = WorkflowClient(
            api_url=api_url,
            api_key=api_key,
            timeout=timeout,
            max_retries=max_retries,
            rate_limit_requests=rate_limit_requests,
            rate_limit_period=rate_limit_period,
        )

        self._execution_client = ExecutionClient(
            api_url=api_url,
            api_key=api_key,
            timeout=timeout,
            max_retries=max_retries,
            rate_limit_requests=rate_limit_requests,
            rate_limit_period=rate_limit_period,
        )

        self._health_client = HealthClient(
            api_url=api_url,
            api_key=api_key,
            timeout=timeout,
            max_retries=max_retries,
            rate_limit_requests=rate_limit_requests,
            rate_limit_period=rate_limit_period,
        )

        logger.debug(f"Initialized n8n API client facade for {api_url}")

    # ========================================================================
    # Health and Connection Methods (delegate to HealthClient)
    # ========================================================================

    def test_connection(self) -> Tuple[bool, str]:
        """
        Test connection to n8n API.

        Returns:
            Tuple of (success: bool, message: str)
        """
        return self._health_client.test_connection()

    def get_n8n_version(self) -> Dict[str, Any]:
        """
        Detect n8n instance version.

        Returns:
            Dictionary with version information

        Note:
            n8n doesn't have a dedicated version endpoint in all versions.
            This method tries multiple approaches to detect the version.
        """
        return self._health_client.get_version()

    def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check.

        Returns:
            Dictionary with health check results
        """
        return self._health_client.health_check()

    # ========================================================================
    # Workflow Methods (delegate to WorkflowClient)
    # ========================================================================

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
        return self._workflow_client.list_workflows(limit=limit, active=active, tags=tags)

    def get_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Get a specific workflow by ID.

        Args:
            workflow_id: Workflow ID

        Returns:
            Workflow object
        """
        return self._workflow_client.get_workflow(workflow_id)

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
        return self._workflow_client.import_workflow(workflow_data, activate=activate)

    def export_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Export a workflow from n8n.

        Args:
            workflow_id: Workflow ID to export

        Returns:
            Workflow JSON object
        """
        return self._workflow_client.export_workflow(workflow_id)

    def update_workflow(self, workflow_id: str, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing workflow.

        Args:
            workflow_id: Workflow ID to update
            workflow_data: Updated workflow data

        Returns:
            Updated workflow object
        """
        return self._workflow_client.update_workflow(workflow_id, workflow_data)

    def delete_workflow(self, workflow_id: str) -> bool:
        """
        Delete a workflow from n8n.

        Args:
            workflow_id: Workflow ID to delete

        Returns:
            True if deletion successful
        """
        return self._workflow_client.delete_workflow(workflow_id)

    def activate_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Activate a workflow.

        Args:
            workflow_id: Workflow ID to activate

        Returns:
            Updated workflow object
        """
        return self._workflow_client.activate_workflow(workflow_id)

    def deactivate_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Deactivate a workflow.

        Args:
            workflow_id: Workflow ID to deactivate

        Returns:
            Updated workflow object
        """
        return self._workflow_client.deactivate_workflow(workflow_id)

    def validate_workflow_import(self, workflow_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate that a workflow can be imported without actually importing it.

        Args:
            workflow_data: Workflow JSON to validate

        Returns:
            Tuple of (is_valid: bool, errors: List[str])
        """
        return self._workflow_client.validate_workflow_import(workflow_data)

    # ========================================================================
    # Execution Methods (delegate to ExecutionClient)
    # ========================================================================

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
        return self._execution_client.execute_workflow(workflow_id, input_data)

    def execute_workflow(
        self, workflow_id: str, input_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a workflow (alias for test_workflow_execution for consistency).

        Args:
            workflow_id: Workflow ID to execute
            input_data: Optional input data for the workflow

        Returns:
            Execution result
        """
        return self._execution_client.execute_workflow(workflow_id, input_data)

    def get_execution(self, execution_id: str) -> Dict[str, Any]:
        """
        Get details of a specific execution.

        Args:
            execution_id: Execution ID

        Returns:
            Execution details
        """
        return self._execution_client.get_execution(execution_id)

    def delete_execution(self, execution_id: str) -> bool:
        """
        Delete an execution.

        Args:
            execution_id: Execution ID to delete

        Returns:
            True if deletion successful
        """
        return self._execution_client.delete_execution(execution_id)

    # ========================================================================
    # Direct Client Access (for advanced use cases)
    # ========================================================================

    @property
    def workflow_client(self) -> WorkflowClient:
        """Get direct access to WorkflowClient for advanced use cases."""
        return self._workflow_client

    @property
    def execution_client(self) -> ExecutionClient:
        """Get direct access to ExecutionClient for advanced use cases."""
        return self._execution_client

    @property
    def health_client(self) -> HealthClient:
        """Get direct access to HealthClient for advanced use cases."""
        return self._health_client


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


if __name__ == "__main__":
    # Example usage
    print("n8n API Client v2.0.0 (Refactored)")
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
    print("Refactoring complete - using facade pattern with specialized clients")
