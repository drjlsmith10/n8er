"""
n8n Execution Client

Handles workflow execution operations.

Author: Project Automata
Version: 2.0.0
"""

import logging
from typing import Any, Dict, Optional

from .base_client import BaseN8nClient, N8nApiError

logger = logging.getLogger(__name__)


class ExecutionClient(BaseN8nClient):
    """
    Client for n8n workflow execution operations.
    """

    def execute_workflow(
        self,
        workflow_id: str,
        input_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a workflow manually.

        Note: May not be available in all n8n versions.

        Args:
            workflow_id: Workflow ID
            input_data: Optional input data

        Returns:
            Execution result
        """
        try:
            response = self._request(
                "POST",
                f"/workflows/{workflow_id}/execute",
                data=input_data or {}
            )
            logger.info(f"Executed workflow: {workflow_id}")
            return response
        except N8nApiError as e:
            logger.warning(f"Workflow execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "note": "Execution API may not be available"
            }

    def get_executions(
        self,
        workflow_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Get workflow executions.

        Args:
            workflow_id: Filter by workflow
            status: Filter by status (success, error, waiting)
            limit: Max results

        Returns:
            Execution list
        """
        params = {"limit": limit}
        if workflow_id:
            params["workflowId"] = workflow_id
        if status:
            params["status"] = status

        return self._request("GET", "/executions", params=params)

    def get_execution(self, execution_id: str) -> Dict[str, Any]:
        """
        Get a specific execution by ID.

        Args:
            execution_id: Execution ID

        Returns:
            Execution details
        """
        return self._request("GET", f"/executions/{execution_id}")

    def delete_execution(self, execution_id: str) -> bool:
        """
        Delete an execution record.

        Args:
            execution_id: Execution ID

        Returns:
            True if successful
        """
        self._request("DELETE", f"/executions/{execution_id}")
        logger.info(f"Deleted execution: {execution_id}")
        return True
