"""
Execution Client

Handles all workflow execution operations:
- Executing workflows
- Getting execution details
- Deleting executions

Author: Project Automata - Architecture Specialist
Version: 2.0.0
Created: 2025-11-21
"""

import logging
from typing import Any, Dict, Optional

from .base_client import BaseN8nClient, N8nApiError

# Import pydantic validation schemas
try:
    from ..validation_schemas import validate_execution, ExecutionInput
    VALIDATION_AVAILABLE = True
except ImportError:
    VALIDATION_AVAILABLE = False

logger = logging.getLogger(__name__)


class ExecutionClient(BaseN8nClient):
    """
    Client for workflow execution operations.

    Provides methods for executing workflows and managing executions.

    Note:
        Execution capabilities may vary based on n8n version and configuration.
        Some features may not be available in all n8n deployments.
    """

    def __init__(self, *args, validate_inputs: bool = True, **kwargs):
        """
        Initialize execution client.

        Args:
            validate_inputs: Enable pydantic input validation (default: True)
            *args, **kwargs: Passed to BaseN8nClient
        """
        super().__init__(*args, **kwargs)
        self.validate_inputs = validate_inputs and VALIDATION_AVAILABLE

        if validate_inputs and not VALIDATION_AVAILABLE:
            logger.warning(
                "Input validation requested but validation_schemas not available. "
                "Validation disabled."
            )

    def execute_workflow(
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

        Raises:
            N8nApiError: If execution fails or is not available
        """
        # Pydantic validation if enabled
        if self.validate_inputs:
            try:
                exec_input = {
                    "workflowId": workflow_id,
                    "data": input_data,
                    "mode": "manual"
                }
                validated = validate_execution(exec_input)
                logger.debug(f"Execution data validated for workflow: {workflow_id}")
            except Exception as e:
                logger.error(f"Execution data validation failed: {e}")
                raise N8nApiError(f"Invalid execution data: {e}")

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

    def get_execution(self, execution_id: str) -> Dict[str, Any]:
        """
        Get details of a specific execution.

        Args:
            execution_id: Execution ID

        Returns:
            Execution details

        Raises:
            N8nApiError: If execution not found or API error occurs
        """
        response = self._request("GET", f"/executions/{execution_id}")
        logger.debug(f"Retrieved execution: {execution_id}")
        return response

    def delete_execution(self, execution_id: str) -> bool:
        """
        Delete an execution.

        Args:
            execution_id: Execution ID to delete

        Returns:
            True if deletion successful

        Raises:
            N8nApiError: If deletion fails
        """
        self._request("DELETE", f"/executions/{execution_id}")
        logger.info(f"Deleted execution: {execution_id}")
        return True
