"""
n8n Workflow Client

Handles workflow CRUD operations: list, get, create, update, delete, activate.

Author: Project Automata
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from .base_client import BaseN8nClient, N8nValidationError, N8nApiError

logger = logging.getLogger(__name__)


class WorkflowClient(BaseN8nClient):
    """
    Client for n8n workflow operations.

    Provides single-responsibility interface for workflow management.
    """

    def list_workflows(
        self,
        limit: Optional[int] = None,
        active: Optional[bool] = None,
        tags: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        List workflows from n8n.

        Args:
            limit: Maximum workflows to return
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
        self,
        workflow_data: Dict[str, Any],
        activate: bool = False
    ) -> Dict[str, Any]:
        """
        Import/create a workflow in n8n.

        Args:
            workflow_data: Workflow JSON
            activate: Whether to activate immediately

        Returns:
            Created workflow with ID

        Raises:
            N8nValidationError: Invalid workflow structure
        """
        if not isinstance(workflow_data, dict):
            raise N8nValidationError("Workflow data must be a dictionary")

        if "nodes" not in workflow_data:
            raise N8nValidationError("Workflow must contain 'nodes' field")

        if "connections" not in workflow_data:
            raise N8nValidationError("Workflow must contain 'connections' field")

        workflow_data["active"] = activate

        try:
            response = self._request("POST", "/workflows", data=workflow_data)
            logger.info(f"Imported workflow: {response.get('name', 'Unknown')}")
            return response
        except N8nApiError as e:
            logger.error(f"Failed to import workflow: {e}")
            raise

    def export_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Export a workflow from n8n.

        Args:
            workflow_id: Workflow ID

        Returns:
            Workflow JSON
        """
        workflow = self.get_workflow(workflow_id)
        logger.info(f"Exported workflow: {workflow.get('name', 'Unknown')}")
        return workflow

    def update_workflow(
        self,
        workflow_id: str,
        workflow_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an existing workflow.

        Args:
            workflow_id: Workflow ID
            workflow_data: Updated workflow data

        Returns:
            Updated workflow
        """
        response = self._request("PUT", f"/workflows/{workflow_id}", data=workflow_data)
        logger.info(f"Updated workflow: {workflow_id}")
        return response

    def delete_workflow(self, workflow_id: str) -> bool:
        """
        Delete a workflow.

        Args:
            workflow_id: Workflow ID

        Returns:
            True if successful
        """
        self._request("DELETE", f"/workflows/{workflow_id}")
        logger.info(f"Deleted workflow: {workflow_id}")
        return True

    def activate_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Activate a workflow using atomic PATCH operation.

        Args:
            workflow_id: Workflow ID

        Returns:
            Updated workflow
        """
        response = self._request(
            "PATCH",
            f"/workflows/{workflow_id}",
            data={"active": True}
        )
        logger.info(f"Activated workflow: {workflow_id}")
        return response

    def deactivate_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Deactivate a workflow using atomic PATCH operation.

        Args:
            workflow_id: Workflow ID

        Returns:
            Updated workflow
        """
        response = self._request(
            "PATCH",
            f"/workflows/{workflow_id}",
            data={"active": False}
        )
        logger.info(f"Deactivated workflow: {workflow_id}")
        return response

    def validate_workflow(
        self,
        workflow_data: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Validate workflow structure without importing.

        Args:
            workflow_data: Workflow JSON

        Returns:
            Tuple of (is_valid, errors)
        """
        errors = []

        required_fields = ["name", "nodes", "connections"]
        for field in required_fields:
            if field not in workflow_data:
                errors.append(f"Missing required field: {field}")

        if "nodes" in workflow_data:
            if not isinstance(workflow_data["nodes"], list):
                errors.append("'nodes' must be a list")
            elif len(workflow_data["nodes"]) == 0:
                errors.append("Workflow must have at least one node")
            else:
                for i, node in enumerate(workflow_data["nodes"]):
                    if not isinstance(node, dict):
                        errors.append(f"Node {i} is not a dictionary")
                        continue

                    for field in ["name", "type", "position", "parameters"]:
                        if field not in node:
                            errors.append(f"Node {i} missing field: {field}")

        if "connections" in workflow_data:
            if not isinstance(workflow_data["connections"], dict):
                errors.append("'connections' must be a dictionary")

        return len(errors) == 0, errors
