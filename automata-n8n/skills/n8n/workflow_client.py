"""
Workflow Client

Handles all workflow-related operations:
- Importing/creating workflows
- Getting workflow details
- Updating workflows
- Deleting workflows
- Activating/deactivating workflows
- Listing workflows
- Validating workflows

Author: Project Automata - Architecture Specialist
Version: 2.0.0
Created: 2025-11-21
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from .base_client import BaseN8nClient, N8nValidationError, N8nApiError

# Import pydantic validation schemas
try:
    from ..validation_schemas import validate_workflow, WorkflowInput
    VALIDATION_AVAILABLE = True
except ImportError:
    VALIDATION_AVAILABLE = False

logger = logging.getLogger(__name__)


class WorkflowClient(BaseN8nClient):
    """
    Client for workflow operations.

    Provides methods for managing n8n workflows including CRUD operations
    and workflow activation/deactivation.
    """

    def __init__(self, *args, validate_inputs: bool = True, **kwargs):
        """
        Initialize workflow client.

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

        # Pydantic validation if enabled
        if self.validate_inputs:
            try:
                validated = validate_workflow(workflow_data)
                logger.debug("Workflow validated before import")
            except Exception as e:
                logger.error(f"Workflow validation failed: {e}")
                raise N8nValidationError(f"Invalid workflow: {e}")

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

        Raises:
            N8nValidationError: If workflow validation fails
        """
        # Pydantic validation if enabled
        if self.validate_inputs:
            try:
                validated = validate_workflow(workflow_data)
                logger.debug(f"Workflow validated before update: {workflow_id}")
            except Exception as e:
                logger.error(f"Workflow validation failed: {e}")
                raise N8nValidationError(f"Invalid workflow: {e}")

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
