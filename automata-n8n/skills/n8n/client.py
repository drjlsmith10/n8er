"""
n8n Unified Client

Facade that provides access to all n8n operations through a single interface.
Combines WorkflowClient, ExecutionClient, and HealthClient.

Author: Project Automata
Version: 2.0.0
"""

import logging
import os
from typing import Any, Dict, List, Optional, Tuple

from .workflow_client import WorkflowClient
from .execution_client import ExecutionClient
from .health_client import HealthClient
from .base_client import N8nApiError, N8nAuthenticationError, N8nConnectionError

logger = logging.getLogger(__name__)


class N8nClient:
    """
    Unified n8n API client providing access to all operations.

    This is a facade that delegates to specialized clients:
    - workflows: WorkflowClient for CRUD operations
    - executions: ExecutionClient for execution management
    - health: HealthClient for health checks

    Example:
        with N8nClient(api_url, api_key) as client:
            # Workflow operations
            workflows = client.list_workflows()
            client.import_workflow(workflow_data)

            # Execution operations
            client.execute_workflow(workflow_id)

            # Health operations
            health = client.health_check()
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
        Initialize unified n8n client.

        Args:
            api_url: Base URL of n8n API
            api_key: n8n API key
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            rate_limit_requests: Max requests per period
            rate_limit_period: Rate limit period in seconds
        """
        self._config = {
            "api_url": api_url,
            "api_key": api_key,
            "timeout": timeout,
            "max_retries": max_retries,
            "rate_limit_requests": rate_limit_requests,
            "rate_limit_period": rate_limit_period,
        }

        # Initialize specialized clients
        self._workflow_client = WorkflowClient(**self._config)
        self._execution_client = ExecutionClient(**self._config)
        self._health_client = HealthClient(**self._config)

        logger.debug(f"Initialized unified n8n client for {api_url}")

    def __enter__(self) -> "N8nClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - closes all clients."""
        self.close()
        return None

    def close(self) -> None:
        """Close all client sessions."""
        self._workflow_client.close()
        self._execution_client.close()
        self._health_client.close()
        logger.debug("Closed all n8n client sessions")

    # ==================== Workflow Operations ====================

    def list_workflows(
        self,
        limit: Optional[int] = None,
        active: Optional[bool] = None,
        tags: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """List workflows from n8n."""
        return self._workflow_client.list_workflows(limit, active, tags)

    def get_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Get a specific workflow by ID."""
        return self._workflow_client.get_workflow(workflow_id)

    def import_workflow(
        self,
        workflow_data: Dict[str, Any],
        activate: bool = False
    ) -> Dict[str, Any]:
        """Import/create a workflow."""
        return self._workflow_client.import_workflow(workflow_data, activate)

    def export_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Export a workflow."""
        return self._workflow_client.export_workflow(workflow_id)

    def update_workflow(
        self,
        workflow_id: str,
        workflow_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an existing workflow."""
        return self._workflow_client.update_workflow(workflow_id, workflow_data)

    def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow."""
        return self._workflow_client.delete_workflow(workflow_id)

    def activate_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Activate a workflow."""
        return self._workflow_client.activate_workflow(workflow_id)

    def deactivate_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Deactivate a workflow."""
        return self._workflow_client.deactivate_workflow(workflow_id)

    def validate_workflow(
        self,
        workflow_data: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """Validate workflow structure."""
        return self._workflow_client.validate_workflow(workflow_data)

    # ==================== Execution Operations ====================

    def execute_workflow(
        self,
        workflow_id: str,
        input_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a workflow."""
        return self._execution_client.execute_workflow(workflow_id, input_data)

    def get_executions(
        self,
        workflow_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """Get workflow executions."""
        return self._execution_client.get_executions(workflow_id, status, limit)

    def get_execution(self, execution_id: str) -> Dict[str, Any]:
        """Get a specific execution."""
        return self._execution_client.get_execution(execution_id)

    def delete_execution(self, execution_id: str) -> bool:
        """Delete an execution record."""
        return self._execution_client.delete_execution(execution_id)

    # ==================== Health Operations ====================

    def test_connection(self) -> Tuple[bool, str]:
        """Test connection to n8n."""
        return self._health_client.test_connection()

    def get_n8n_version(self) -> Dict[str, Any]:
        """Get n8n version information."""
        return self._health_client.get_version()

    def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check."""
        return self._health_client.health_check()


def create_client_from_env() -> Optional[N8nClient]:
    """
    Create N8nClient from environment variables.

    Looks for:
    - N8N_API_URL
    - N8N_API_KEY

    Returns:
        N8nClient instance or None if config unavailable
    """
    api_url = os.getenv("N8N_API_URL")
    api_key = os.getenv("N8N_API_KEY")

    if not api_url:
        logger.error("N8N_API_URL not set in environment")
        return None

    return N8nClient(api_url=api_url, api_key=api_key)
