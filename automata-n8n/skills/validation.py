"""
Input Validation Schemas

Provides Pydantic-style validation for workflow and API inputs.
Uses dataclasses with validation methods for compatibility (no Pydantic dependency).

Author: Project Automata
Version: 1.0.0
"""

import logging
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when validation fails"""
    def __init__(self, errors: List[str]):
        self.errors = errors
        super().__init__(f"Validation failed: {', '.join(errors)}")


@dataclass
class WorkflowInput:
    """
    Validated workflow input structure.

    Validates:
    - Name length and format
    - Node structure and required fields
    - Connection references
    - Settings format
    """
    name: str
    nodes: List[Dict[str, Any]]
    connections: Dict[str, Any]
    settings: Dict[str, Any] = field(default_factory=dict)
    active: bool = False
    tags: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate all fields after initialization."""
        errors = self.validate()
        if errors:
            raise ValidationError(errors)

    def validate(self) -> List[str]:
        """
        Validate all fields.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Validate name
        if not self.name or not self.name.strip():
            errors.append("Workflow name cannot be empty")
        elif len(self.name) > 255:
            errors.append(f"Workflow name too long ({len(self.name)} chars, max 255)")
        elif not re.match(r'^[\w\s\-_.]+$', self.name):
            errors.append("Workflow name contains invalid characters")

        # Validate nodes
        if not isinstance(self.nodes, list):
            errors.append("'nodes' must be a list")
        elif len(self.nodes) == 0:
            errors.append("Workflow must have at least one node")
        else:
            node_names = set()
            for i, node in enumerate(self.nodes):
                node_errors = self._validate_node(node, i)
                errors.extend(node_errors)

                # Check for duplicate names
                node_name = node.get("name", "")
                if node_name in node_names:
                    errors.append(f"Duplicate node name: {node_name}")
                node_names.add(node_name)

        # Validate connections
        if not isinstance(self.connections, dict):
            errors.append("'connections' must be a dictionary")
        else:
            # Validate connection references
            node_names = {n.get("name", "") for n in self.nodes}
            for source in self.connections:
                if source not in node_names:
                    errors.append(f"Connection source '{source}' not found in nodes")

        # Validate settings
        if not isinstance(self.settings, dict):
            errors.append("'settings' must be a dictionary")

        # Validate tags
        if not isinstance(self.tags, list):
            errors.append("'tags' must be a list")
        else:
            for tag in self.tags:
                if not isinstance(tag, str) or len(tag) > 100:
                    errors.append(f"Invalid tag: {tag}")

        return errors

    def _validate_node(self, node: Any, index: int) -> List[str]:
        """Validate a single node structure."""
        errors = []

        if not isinstance(node, dict):
            errors.append(f"Node {index} is not a dictionary")
            return errors

        # Required fields
        required = ["name", "type", "position", "parameters"]
        for field_name in required:
            if field_name not in node:
                errors.append(f"Node {index} missing required field: {field_name}")

        # Validate name
        name = node.get("name", "")
        if not name or not name.strip():
            errors.append(f"Node {index} has empty name")
        elif len(name) > 255:
            errors.append(f"Node {index} name too long")

        # Validate type
        node_type = node.get("type", "")
        if not node_type:
            errors.append(f"Node {index} has empty type")
        elif not node_type.startswith("n8n-nodes-"):
            errors.append(f"Node {index} has invalid type format: {node_type}")

        # Validate position
        position = node.get("position", [])
        if not isinstance(position, (list, tuple)) or len(position) != 2:
            errors.append(f"Node {index} has invalid position format")
        elif not all(isinstance(p, (int, float)) for p in position):
            errors.append(f"Node {index} position must be numeric")

        # Validate parameters
        params = node.get("parameters")
        if params is not None and not isinstance(params, dict):
            errors.append(f"Node {index} parameters must be a dictionary")

        # Validate typeVersion if present
        type_version = node.get("typeVersion")
        if type_version is not None:
            if not isinstance(type_version, (int, float)):
                errors.append(f"Node {index} typeVersion must be numeric")
            elif type_version < 1:
                errors.append(f"Node {index} typeVersion must be >= 1")

        return errors


@dataclass
class ApiKeyInput:
    """Validated API key input."""
    api_key: str
    min_length: int = 8
    max_length: int = 512

    def __post_init__(self):
        errors = self.validate()
        if errors:
            raise ValidationError(errors)

    def validate(self) -> List[str]:
        errors = []

        if not self.api_key:
            errors.append("API key cannot be empty")
        elif len(self.api_key) < self.min_length:
            errors.append(f"API key too short (min {self.min_length} chars)")
        elif len(self.api_key) > self.max_length:
            errors.append(f"API key too long (max {self.max_length} chars)")

        # Check for common invalid patterns
        if self.api_key and self.api_key.strip() != self.api_key:
            errors.append("API key has leading/trailing whitespace")

        return errors


@dataclass
class WorkflowIdInput:
    """Validated workflow ID input."""
    workflow_id: str

    def __post_init__(self):
        errors = self.validate()
        if errors:
            raise ValidationError(errors)

    def validate(self) -> List[str]:
        errors = []

        if not self.workflow_id:
            errors.append("Workflow ID cannot be empty")
        elif len(self.workflow_id) > 255:
            errors.append("Workflow ID too long")

        # Prevent path traversal
        if ".." in self.workflow_id or "/" in self.workflow_id or "\\" in self.workflow_id:
            errors.append("Workflow ID contains invalid characters (path traversal attempt)")

        return errors


def validate_workflow(workflow_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate workflow data structure.

    Args:
        workflow_data: Raw workflow dictionary

    Returns:
        Tuple of (is_valid, errors)
    """
    try:
        WorkflowInput(
            name=workflow_data.get("name", ""),
            nodes=workflow_data.get("nodes", []),
            connections=workflow_data.get("connections", {}),
            settings=workflow_data.get("settings", {}),
            active=workflow_data.get("active", False),
            tags=workflow_data.get("tags", [])
        )
        return True, []
    except ValidationError as e:
        return False, e.errors
    except Exception as e:
        return False, [str(e)]


def validate_api_key(api_key: str) -> Tuple[bool, List[str]]:
    """Validate API key format."""
    try:
        ApiKeyInput(api_key=api_key)
        return True, []
    except ValidationError as e:
        return False, e.errors


def validate_workflow_id(workflow_id: str) -> Tuple[bool, List[str]]:
    """Validate workflow ID format."""
    try:
        WorkflowIdInput(workflow_id=workflow_id)
        return True, []
    except ValidationError as e:
        return False, e.errors
