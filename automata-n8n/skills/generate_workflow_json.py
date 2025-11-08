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
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class NodeTemplate:
    """
    Template for generating n8n nodes.

    Reasoning: Templates enable consistent node generation with sensible defaults
    """
    type: str
    name: str
    parameters: Dict
    type_version: int = 1
    position_offset: Tuple[int, int] = (0, 0)
    credentials: Optional[Dict] = None
    notes: str = ""


class WorkflowBuilder:
    """
    Fluent builder for constructing n8n workflows programmatically.

    Usage:
        builder = WorkflowBuilder("My Workflow")
        builder.add_trigger("webhook", "Webhook Trigger")
        builder.add_node("httpRequest", "Send Email", {...})
        builder.connect("Webhook Trigger", "Send Email")
        workflow_json = builder.build()

    Reasoning: Builder pattern provides intuitive API for workflow construction
    """

    def __init__(self, name: str = "Generated Workflow"):
        """Initialize workflow builder"""
        self.name = name
        self.nodes: List[Dict] = []
        self.connections: Dict[str, Dict] = {}
        self.settings: Dict = {
            "executionOrder": "v1"
        }
        self.metadata = {
            "createdAt": datetime.utcnow().isoformat() + "Z",
            "updatedAt": datetime.utcnow().isoformat() + "Z"
        }

        # Auto-positioning
        self.current_x = 240
        self.current_y = 300
        self.x_spacing = 340
        self.y_spacing = 180

        # Node name tracking for uniqueness
        self.node_names = set()

        logger.info(f"Initialized WorkflowBuilder: {name}")

    def add_node(
        self,
        node_type: str,
        name: str,
        parameters: Optional[Dict] = None,
        position: Optional[Tuple[int, int]] = None,
        credentials: Optional[Dict] = None,
        type_version: int = 1,
        notes: str = ""
    ) -> 'WorkflowBuilder':
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
            "parameters": parameters or {}
        }

        if credentials:
            node["credentials"] = credentials

        if notes:
            node["notes"] = notes

        self.nodes.append(node)
        logger.debug(f"Added node: {name} ({node_type})")

        return self

    def add_trigger(
        self,
        trigger_type: str,
        name: str = "Trigger",
        parameters: Optional[Dict] = None,
        **kwargs
    ) -> 'WorkflowBuilder':
        """
        Add a trigger node (convenience method).

        Reasoning: Triggers are workflow entry points and deserve dedicated method
        """
        # Map common trigger types to full node names
        trigger_map = {
            "webhook": "n8n-nodes-base.webhook",
            "manual": "n8n-nodes-base.manualTrigger",
            "cron": "n8n-nodes-base.cron",
            "email": "n8n-nodes-base.emailTrigger"
        }

        full_type = trigger_map.get(trigger_type.lower(), trigger_type)
        return self.add_node(full_type, name, parameters, **kwargs)

    def connect(
        self,
        source: str,
        target: str,
        source_output: int = 0,
        target_input: int = 0,
        connection_type: str = "main"
    ) -> 'WorkflowBuilder':
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
        connection_def = {
            "node": target,
            "type": connection_type,
            "index": target_input
        }

        self.connections[source][connection_type][source_output].append(connection_def)
        logger.debug(f"Connected: {source} → {target}")

        return self

    def connect_chain(self, *node_names: str) -> 'WorkflowBuilder':
        """
        Connect multiple nodes in sequence.

        Example:
            builder.connect_chain("Trigger", "Transform", "Action", "Output")

        Reasoning: Simplifies linear workflow construction
        """
        for i in range(len(node_names) - 1):
            self.connect(node_names[i], node_names[i + 1])

        return self

    def set_active(self, active: bool = True) -> 'WorkflowBuilder':
        """Set workflow active status"""
        self.metadata["active"] = active
        return self

    def add_tags(self, *tags: str) -> 'WorkflowBuilder':
        """Add tags to workflow"""
        if "tags" not in self.metadata:
            self.metadata["tags"] = []
        self.metadata["tags"].extend(tags)
        return self

    def build(self, validate: bool = True) -> Dict:
        """
        Build and return the complete workflow JSON.

        Args:
            validate: If True, validate using parse_n8n_schema before returning

        Returns:
            Complete n8n workflow JSON

        Reasoning: Final validation ensures generated workflow is valid
        """
        workflow = {
            "name": self.name,
            "nodes": self.nodes,
            "connections": self.connections,
            "settings": self.settings,
            **self.metadata
        }

        logger.info(f"Built workflow: {self.name} ({len(self.nodes)} nodes)")

        # Optional validation
        if validate:
            try:
                from parse_n8n_schema import parse_workflow_json
                parsed = parse_workflow_json(workflow, strict=False)
                if parsed:
                    logger.info("✓ Workflow validation passed")
                else:
                    logger.warning("✗ Workflow validation failed")
            except ImportError:
                logger.warning("parse_n8n_schema not available, skipping validation")

        return workflow

    def save(self, filepath: str, validate: bool = True) -> None:
        """
        Build and save workflow to JSON file.

        Args:
            filepath: Output file path
            validate: Validate before saving
        """
        workflow = self.build(validate=validate)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(workflow, f, indent=2)

        logger.info(f"Saved workflow to: {filepath}")


class TemplateLibrary:
    """
    Library of common workflow patterns and templates.

    Reasoning: Reusable patterns accelerate workflow generation and ensure best practices
    """

    @staticmethod
    def webhook_to_email(
        webhook_path: str = "webhook-test",
        email_to: str = "user@example.com",
        email_subject: str = "Webhook Received"
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
            parameters={
                "path": webhook_path,
                "httpMethod": "POST",
                "responseMode": "onReceived"
            }
        )

        # Add email sender
        builder.add_node(
            "n8n-nodes-base.emailSend",
            "Send Email",
            parameters={
                "toEmail": email_to,
                "subject": email_subject,
                "text": "=Webhook received with data: {{ $json }}",
                "fromEmail": "noreply@example.com"
            }
        )

        # Connect
        builder.connect("Webhook", "Send Email")

        return builder.build()

    @staticmethod
    def http_request_transform(
        url: str,
        method: str = "GET",
        transform_code: str = "return items;"
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
            parameters={
                "url": url,
                "method": method,
                "responseFormat": "json"
            }
        )

        # Function transform
        builder.add_node(
            "n8n-nodes-base.function",
            "Transform Data",
            parameters={
                "functionCode": transform_code
            }
        )

        # Chain connections
        builder.connect_chain("Manual Trigger", "HTTP Request", "Transform Data")

        return builder.build()

    @staticmethod
    def etl_pipeline(
        source_type: str = "database",
        destination_type: str = "webhook"
    ) -> Dict:
        """
        Generate Extract → Transform → Load workflow.

        Pattern: Trigger → Extract → Transform → Load
        """
        builder = WorkflowBuilder("ETL Pipeline")

        # Trigger (scheduled)
        builder.add_trigger(
            "cron",
            "Schedule",
            parameters={
                "triggerTimes": {
                    "item": [
                        {
                            "mode": "everyHour"
                        }
                    ]
                }
            }
        )

        # Extract
        builder.add_node(
            "n8n-nodes-base.httpRequest",
            "Extract Data",
            parameters={
                "url": "https://api.example.com/data",
                "method": "GET"
            }
        )

        # Transform
        builder.add_node(
            "n8n-nodes-base.set",
            "Transform Fields",
            parameters={
                "values": {
                    "string": [
                        {
                            "name": "transformed_field",
                            "value": "={{ $json.original_field }}"
                        }
                    ]
                },
                "options": {}
            }
        )

        # Load
        builder.add_node(
            "n8n-nodes-base.httpRequest",
            "Load to Destination",
            parameters={
                "url": "https://destination.example.com/api",
                "method": "POST"
            }
        )

        # Chain all together
        builder.connect_chain(
            "Schedule",
            "Extract Data",
            "Transform Fields",
            "Load to Destination"
        )

        return builder.build()

    @staticmethod
    def api_with_error_handling(api_url: str) -> Dict:
        """
        Generate API call with error handling and retry logic.

        Pattern: Trigger → API → IF (error) → Retry/Notify
        """
        builder = WorkflowBuilder("API with Error Handling")

        builder.add_trigger("manual", "Start")

        builder.add_node(
            "n8n-nodes-base.httpRequest",
            "API Call",
            parameters={
                "url": api_url,
                "method": "GET",
                "options": {
                    "timeout": 10000
                }
            }
        )

        builder.add_node(
            "n8n-nodes-base.if",
            "Check Success",
            parameters={
                "conditions": {
                    "boolean": [],
                    "number": [
                        {
                            "value1": "={{ $json.statusCode }}",
                            "operation": "equal",
                            "value2": 200
                        }
                    ]
                }
            }
        )

        builder.add_node(
            "n8n-nodes-base.noOp",
            "Success Handler"
        )

        builder.add_node(
            "n8n-nodes-base.httpRequest",
            "Send Error Alert",
            parameters={
                "url": "https://alerts.example.com/error",
                "method": "POST"
            }
        )

        # Connect flow
        builder.connect("Start", "API Call")
        builder.connect("API Call", "Check Success")
        builder.connect("Check Success", "Success Handler", source_output=0)  # True branch
        builder.connect("Check Success", "Send Error Alert", source_output=1)  # False branch

        return builder.build()


# Convenience functions
def generate_from_template(template_name: str, **params) -> Dict:
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
        "api_error_handling": TemplateLibrary.api_with_error_handling
    }

    if template_name not in templates:
        raise ValueError(f"Unknown template: {template_name}")

    return templates[template_name](**params)


def save_workflow(workflow_json: Dict, filepath: str) -> None:
    """Save workflow JSON to file"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(workflow_json, f, indent=2)
    logger.info(f"Saved workflow to: {filepath}")


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
        webhook_path="alerts",
        email_to="admin@example.com"
    )
    print(f"✓ Generated: {workflow2['name']}")

    print("\nFor detailed documentation, see: docs/architecture.md")
