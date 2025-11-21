"""
n8n Workflow JSON Generator

This module generates valid n8n workflow JSON files from high-level descriptions,
templates, and learned patterns. Integrates with parse_n8n_schema for validation.

Author: Project Automata - Engineer Agent
Version: 1.0.0
Created: 2025-11-08
"""

import json
import logging
import sys
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Add parent directory to path for config imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import pydantic validation schemas
try:
    from validation_schemas import validate_node, validate_workflow, NodeInput, WorkflowInput
    VALIDATION_AVAILABLE = True
except ImportError:
    VALIDATION_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

# Import config for workflow limits
try:
    from config import config

    WORKFLOW_LIMITS_ENABLED = True
except ImportError:
    WORKFLOW_LIMITS_ENABLED = False
    logger.warning("Config not available, workflow size limits disabled")


@dataclass
class NodeTemplate:
    """
    Template for generating n8n nodes.

    Reasoning: Templates enable consistent node generation with sensible defaults
    """

    type: str
    name: str
    parameters: Dict[str, Any]
    type_version: int = 1
    position_offset: Tuple[int, int] = (0, 0)
    credentials: Optional[Dict[str, Any]] = None
    notes: str = ""


class WorkflowBuilder:
    """
    Fluent builder for constructing n8n workflows programmatically.

    Thread Safety:
        This class is NOT thread-safe for shared instance usage.
        Builder instances maintain mutable state during workflow construction.

        RECOMMENDATION: Each thread should create its own WorkflowBuilder instance.
        Do NOT share builder instances between threads.

    Example (Thread-Safe Usage):
        # Good: Each thread creates its own builder
        def worker():
            builder = WorkflowBuilder("My Workflow")
            builder.add_node(...)
            return builder.build()

        # Bad: Sharing builder between threads
        builder = WorkflowBuilder()  # DON'T DO THIS
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(builder.add_node, ...) for ...]  # NOT THREAD-SAFE

    Usage:
        builder = WorkflowBuilder("My Workflow")
        builder.add_trigger("webhook", "Webhook Trigger")
        builder.add_node("httpRequest", "Send Email", {...})
        builder.connect("Webhook Trigger", "Send Email")
        workflow_json = builder.build()

    Reasoning: Builder pattern provides intuitive API for workflow construction
    """

    def __init__(self, name: str = "Generated Workflow", validate_inputs: bool = True):
        """
        Initialize workflow builder.

        Note:
            Builder instances are designed for single-threaded use and are NOT thread-safe.
            Create a new builder instance for each workflow in multi-threaded code.

        Args:
            name: Workflow name
            validate_inputs: Enable pydantic input validation (default: True)
        """
        self.name = name
        self.nodes: List[Dict[str, Any]] = []
        self.connections: Dict[str, Dict[str, Any]] = {}
        self.validate_inputs = validate_inputs and VALIDATION_AVAILABLE

        if validate_inputs and not VALIDATION_AVAILABLE:
            logger.warning(
                "Input validation requested but validation_schemas not available. "
                "Validation disabled."
            )

        # Complete settings with all supported n8n options
        self.settings: Dict[str, Any] = {
            "executionOrder": "v1",
            "saveExecutionProgress": False,
            "saveManualExecutions": True,
            "timezone": "UTC",
            "callerPolicy": "workflowsFromSameOwner",
        }

        # Workflow-level IDs and metadata
        self.workflow_id = str(uuid.uuid4())
        self.version_id = str(uuid.uuid4())

        self.metadata: Dict[str, Any] = {
            "createdAt": datetime.utcnow().isoformat() + "Z",
            "updatedAt": datetime.utcnow().isoformat() + "Z",
        }

        # Additional n8n workflow fields
        self.meta: Dict[str, Any] = {"templateCredsSetupCompleted": True, "instanceId": str(uuid.uuid4())}

        self.pin_data: Dict[str, Any] = {}  # Type annotation for mypy
        self.static_data: Dict[str, Any] = {}  # Type annotation for mypy

        # Auto-positioning
        self.current_x = 240
        self.current_y = 300
        self.x_spacing = 340
        self.y_spacing = 180

        # Node name tracking for uniqueness
        self.node_names: Set[str] = set()

        logger.debug(f"Initialized WorkflowBuilder: {name}")

    def add_node(
        self,
        node_type: str,
        name: str,
        parameters: Optional[Dict[str, Any]] = None,
        position: Optional[Tuple[int, int]] = None,
        credentials: Optional[Dict[str, Any]] = None,
        type_version: int = 1,
        notes: str = "",
    ) -> "WorkflowBuilder":
        """
        Add a node to the workflow.

        Args:
            node_type: n8n node type (e.g., 'n8n-nodes-base.httpRequest')
            name: Unique node name
            parameters: Node configuration parameters
            position: Optional (x, y) position, auto-calculated if None
            credentials: Optional credential configuration
            type_version: Node type version (default: 1)
            notes: Optional notes/documentation

        Returns:
            Self for method chaining

        Reasoning: Auto-positioning reduces boilerplate while maintaining flexibility
        """
        # Ensure unique name
        if name in self.node_names:
            original_name = name
            counter = 1
            while name in self.node_names:
                name = f"{original_name}{counter}"
                counter += 1
            logger.warning(f"Duplicate node name detected, renamed to: {name}")

        self.node_names.add(name)

        # Auto-calculate position if not provided
        if position is None:
            position = (self.current_x, self.current_y)
            self.current_x += self.x_spacing

        # Build node structure
        node = {
            "name": name,
            "type": node_type,
            "typeVersion": type_version,
            "position": list(position),
            "parameters": parameters or {},
        }

        if credentials:
            node["credentials"] = credentials

        if notes:
            node["notes"] = notes

        # Validate node input if validation is enabled
        if self.validate_inputs:
            try:
                validated_node = validate_node(node)
                # Convert back to dict for storage
                node = validated_node.model_dump()
                logger.debug(f"Node validated: {name}")
            except Exception as e:
                logger.error(f"Node validation failed for '{name}': {e}")
                raise ValueError(f"Invalid node '{name}': {e}")

        self.nodes.append(node)
        logger.debug(f"Added node: {name} ({node_type})")

        return self

    def add_trigger(
        self, trigger_type: str, name: str = "Trigger", parameters: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> "WorkflowBuilder":
        """
        Add a trigger node (convenience method).

        Reasoning: Triggers are workflow entry points and deserve dedicated method
        """
        # Map common trigger types to full node names
        trigger_map = {
            "webhook": "n8n-nodes-base.webhook",
            "manual": "n8n-nodes-base.manualTrigger",
            "cron": "n8n-nodes-base.cron",
            "email": "n8n-nodes-base.emailTrigger",
        }

        full_type = trigger_map.get(trigger_type.lower(), trigger_type)
        return self.add_node(full_type, name, parameters, **kwargs)

    def connect(
        self,
        source: str,
        target: str,
        source_output: int = 0,
        target_input: int = 0,
        connection_type: str = "main",
    ) -> "WorkflowBuilder":
        """
        Create a connection between two nodes.

        Args:
            source: Source node name
            target: Target node name
            source_output: Output index from source (default: 0)
            target_input: Input index to target (default: 0)
            connection_type: Connection type (default: "main")

        Returns:
            Self for method chaining

        Reasoning: Explicit connection building with validation
        """
        # Validate nodes exist
        if source not in self.node_names:
            raise ValueError(f"Source node not found: {source}")
        if target not in self.node_names:
            raise ValueError(f"Target node not found: {target}")

        # Initialize connection structure if needed
        if source not in self.connections:
            self.connections[source] = {}

        if connection_type not in self.connections[source]:
            self.connections[source][connection_type] = []

        # Ensure output array is large enough
        while len(self.connections[source][connection_type]) <= source_output:
            self.connections[source][connection_type].append([])

        # Add connection
        connection_def = {"node": target, "type": connection_type, "index": target_input}

        self.connections[source][connection_type][source_output].append(connection_def)
        logger.debug(f"Connected: {source} → {target}")

        return self

    def connect_chain(self, *node_names: str) -> "WorkflowBuilder":
        """
        Connect multiple nodes in sequence.

        Example:
            builder.connect_chain("Trigger", "Transform", "Action", "Output")

        Reasoning: Simplifies linear workflow construction
        """
        for i in range(len(node_names) - 1):
            self.connect(node_names[i], node_names[i + 1])

        return self

    def set_active(self, active: bool = True) -> "WorkflowBuilder":
        """Set workflow active status"""
        self.metadata["active"] = active
        return self

    def add_tags(self, *tags: str) -> "WorkflowBuilder":
        """Add tags to workflow"""
        if "tags" not in self.metadata:
            self.metadata["tags"] = []
        self.metadata["tags"].extend(tags)
        return self

    def _validate_size(self) -> Tuple[bool, List[str]]:
        """
        Validate workflow size against configured limits.

        Returns:
            Tuple of (is_valid, warning_messages)
        """
        warnings = []

        if not WORKFLOW_LIMITS_ENABLED:
            return True, []

        node_count = len(self.nodes)
        connection_count = sum(
            len(conns.get(conn_type, []))
            for conns in self.connections.values()
            for conn_type in conns
        )
        complexity = node_count + connection_count

        # Check warnings
        if node_count > config.WARN_WORKFLOW_NODES:
            warnings.append(
                f"WARNING: Workflow has {node_count} nodes (warning threshold: {config.WARN_WORKFLOW_NODES}). "
                "Large workflows may be slow to execute."
            )

        if complexity > config.WARN_WORKFLOW_COMPLEXITY:
            warnings.append(
                f"WARNING: Workflow complexity is {complexity} (warning threshold: {config.WARN_WORKFLOW_COMPLEXITY}). "
                "Consider breaking into smaller workflows."
            )

        # Check hard limits
        is_valid = True
        if node_count > config.MAX_WORKFLOW_NODES:
            warnings.append(
                f"ERROR: Workflow exceeds maximum nodes ({node_count} > {config.MAX_WORKFLOW_NODES})"
            )
            is_valid = False

        if complexity > config.MAX_WORKFLOW_COMPLEXITY:
            warnings.append(
                f"ERROR: Workflow exceeds maximum complexity ({complexity} > {config.MAX_WORKFLOW_COMPLEXITY})"
            )
            is_valid = False

        return is_valid, warnings

    def build(self, validate: bool = True) -> Dict[str, Any]:
        """
        Build and return the complete workflow JSON.

        Args:
            validate: If True, validate using parse_n8n_schema before returning

        Returns:
            Complete n8n workflow JSON

        Reasoning: Final validation ensures generated workflow is valid
        """
        # Check size limits
        is_size_valid, size_warnings = self._validate_size()
        for warning in size_warnings:
            if warning.startswith("ERROR"):
                logger.error(warning)
            else:
                logger.warning(warning)

        if not is_size_valid:
            raise ValueError(f"Workflow exceeds size limits: {size_warnings}")

        workflow = {
            "id": self.workflow_id,
            "name": self.name,
            "nodes": self.nodes,
            "connections": self.connections,
            "settings": self.settings,
            "versionId": self.version_id,
            "meta": self.meta,
            "pinData": self.pin_data,
            "staticData": self.static_data,
            **self.metadata,
        }

        logger.debug(f"Built workflow: {self.name} ({len(self.nodes)} nodes)")

        # Pydantic validation if enabled
        if self.validate_inputs and validate:
            try:
                # Validate the complete workflow structure
                validated = validate_workflow(workflow)
                logger.debug("✓ Workflow pydantic validation passed")
            except Exception as e:
                logger.error(f"Workflow pydantic validation failed: {e}")
                raise ValueError(f"Invalid workflow: {e}")

        # Optional schema validation
        if validate:
            try:
                from parse_n8n_schema import parse_workflow_json

                parsed = parse_workflow_json(workflow, strict=False)
                if parsed:
                    logger.debug("✓ Workflow schema validation passed")
                else:
                    logger.warning("✗ Workflow schema validation failed")
            except ImportError:
                logger.warning("parse_n8n_schema not available, skipping schema validation")

        return workflow

    def save(self, filepath: str, validate: bool = True) -> None:
        """
        Build and save workflow to JSON file.

        Args:
            filepath: Output file path
            validate: Validate before saving
        """
        workflow = self.build(validate=validate)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(workflow, f, indent=2)

        logger.debug(f"Saved workflow to: {filepath}")


class TemplateLibrary:
    """
    Library of common workflow patterns and templates.

    Reasoning: Reusable patterns accelerate workflow generation and ensure best practices
    """

    @staticmethod
    def webhook_to_email(
        webhook_path: str = "webhook-test",
        email_to: str = "user@example.com",
        email_subject: str = "Webhook Received",
    ) -> Dict:
        """
        Generate a simple webhook → email notification workflow.

        Pattern: Trigger → Action
        """
        builder = WorkflowBuilder("Webhook to Email")

        # Add webhook trigger
        builder.add_trigger(
            "webhook",
            "Webhook",
            parameters={"path": webhook_path, "httpMethod": "POST", "responseMode": "onReceived"},
        )

        # Add email sender
        builder.add_node(
            "n8n-nodes-base.emailSend",
            "Send Email",
            type_version=2,
            parameters={
                "fromEmail": "noreply@example.com",
                "toEmail": email_to,
                "subject": email_subject,
                "emailFormat": "text",
                "message": "=Webhook received with data: {{ $json }}",
                "options": {},
            },
        )

        # Connect
        builder.connect("Webhook", "Send Email")

        return builder.build()

    @staticmethod
    def http_request_transform(
        url: str, method: str = "GET", transform_code: str = "return items;"
    ) -> Dict:
        """
        Generate HTTP Request → Transform → Output workflow.

        Pattern: Trigger → HTTP → Transform
        """
        builder = WorkflowBuilder("HTTP Request + Transform")

        # Manual trigger
        builder.add_trigger("manual", "Manual Trigger")

        # HTTP Request
        builder.add_node(
            "n8n-nodes-base.httpRequest",
            "HTTP Request",
            parameters={"url": url, "method": method, "responseFormat": "json"},
        )

        # Function transform
        builder.add_node(
            "n8n-nodes-base.function", "Transform Data", parameters={"functionCode": transform_code}
        )

        # Chain connections
        builder.connect_chain("Manual Trigger", "HTTP Request", "Transform Data")

        return builder.build()

    @staticmethod
    def etl_pipeline(source_type: str = "database", destination_type: str = "webhook") -> Dict[str, Any]:
        """
        Generate Extract → Transform → Load workflow.

        Pattern: Trigger → Extract → Transform → Load
        """
        builder = WorkflowBuilder("ETL Pipeline")

        # Trigger (scheduled)
        builder.add_trigger(
            "cron", "Schedule", parameters={"triggerTimes": {"item": [{"mode": "everyHour"}]}}
        )

        # Extract
        builder.add_node(
            "n8n-nodes-base.httpRequest",
            "Extract Data",
            parameters={"url": "https://api.example.com/data", "method": "GET"},
        )

        # Transform
        builder.add_node(
            "n8n-nodes-base.set",
            "Transform Fields",
            parameters={
                "values": {
                    "string": [
                        {"name": "transformed_field", "value": "={{ $json.original_field }}"}
                    ]
                },
                "options": {},
            },
        )

        # Load
        builder.add_node(
            "n8n-nodes-base.httpRequest",
            "Load to Destination",
            parameters={"url": "https://destination.example.com/api", "method": "POST"},
        )

        # Chain all together
        builder.connect_chain("Schedule", "Extract Data", "Transform Fields", "Load to Destination")

        return builder.build()

    @staticmethod
    def api_with_error_handling(api_url: str) -> Dict[str, Any]:
        """
        Generate API call with error handling and retry logic.

        Pattern: Trigger → API → IF (error) → Retry/Notify
        """
        builder = WorkflowBuilder("API with Error Handling")

        builder.add_trigger("manual", "Start")

        builder.add_node(
            "n8n-nodes-base.httpRequest",
            "API Call",
            parameters={"url": api_url, "method": "GET", "options": {"timeout": 10000}},
        )

        builder.add_node(
            "n8n-nodes-base.if",
            "Check Success",
            type_version=2,
            parameters={
                "conditions": {
                    "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
                    "conditions": [
                        {
                            "id": "condition-check-success",
                            "leftValue": "={{ $json.statusCode }}",
                            "rightValue": 200,
                            "operator": {"type": "number", "operation": "equals"},
                        }
                    ],
                    "combinator": "and",
                }
            },
        )

        builder.add_node("n8n-nodes-base.noOp", "Success Handler")

        builder.add_node(
            "n8n-nodes-base.httpRequest",
            "Send Error Alert",
            parameters={"url": "https://alerts.example.com/error", "method": "POST"},
        )

        # Connect flow
        builder.connect("Start", "API Call")
        builder.connect("API Call", "Check Success")
        builder.connect("Check Success", "Success Handler", source_output=0)  # True branch
        builder.connect("Check Success", "Send Error Alert", source_output=1)  # False branch

        return builder.build()


# Convenience functions
def generate_from_template(template_name: str, **params: Any) -> Dict[str, Any]:
    """
    Generate workflow from named template.

    Args:
        template_name: Template identifier
        **params: Template-specific parameters

    Returns:
        Generated workflow JSON
    """
    templates = {
        "webhook_email": TemplateLibrary.webhook_to_email,
        "http_transform": TemplateLibrary.http_request_transform,
        "etl": TemplateLibrary.etl_pipeline,
        "api_error_handling": TemplateLibrary.api_with_error_handling,
    }

    if template_name not in templates:
        raise ValueError(f"Unknown template: {template_name}")

    return templates[template_name](**params)


def save_workflow(workflow_json: Dict[str, Any], filepath: str) -> None:
    """Save workflow JSON to file"""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(workflow_json, f, indent=2)
    logger.debug(f"Saved workflow to: {filepath}")


if __name__ == "__main__":
    # Example usage
    print("n8n Workflow Generator v1.0.0")
    print("=" * 60)
    print("\nGenerating example workflows...")

    # Example 1: Using builder directly
    builder = WorkflowBuilder("Custom Workflow")
    builder.add_trigger("webhook", "Start", {"path": "test"})
    builder.add_node("n8n-nodes-base.set", "Process", {"values": {}})
    builder.connect("Start", "Process")
    workflow = builder.build()
    print(f"\n✓ Generated: {workflow['name']}")

    # Example 2: Using template
    workflow2 = TemplateLibrary.webhook_to_email(
        webhook_path="alerts", email_to="admin@example.com"
    )
    print(f"✓ Generated: {workflow2['name']}")

    print("\nFor detailed documentation, see: docs/architecture.md")
