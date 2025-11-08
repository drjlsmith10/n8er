"""
n8n Workflow Schema Parser

This module provides comprehensive parsing and validation capabilities for n8n workflow JSON files.
It extracts nodes, connections, credentials, and validates against n8n v1.x schema specifications.

Author: Project Automata - Engineer Agent
Version: 1.0.0
Created: 2025-11-08
"""

import json
import logging
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum

# Configure logging for reasoning traces
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)


class NodeType(Enum):
    """n8n node categories for classification"""
    TRIGGER = "trigger"
    ACTION = "regular"
    WEBHOOK = "webhook"
    TRANSFORM = "transform"
    LOGIC = "logic"


@dataclass
class N8nNode:
    """
    Represents a single n8n workflow node with all metadata.

    Reasoning: Structured representation enables easy validation and manipulation
    """
    id: str
    name: str
    type: str
    type_version: int
    position: Tuple[float, float]
    parameters: Dict
    credentials: Optional[Dict] = None
    disabled: bool = False
    notes: str = ""

    def is_trigger(self) -> bool:
        """Check if node is a trigger type"""
        # Reasoning: Triggers typically start with specific prefixes or have webhook in name
        trigger_indicators = ['trigger', 'webhook', 'cron', 'manual']
        return any(indicator in self.type.lower() for indicator in trigger_indicators)

    def get_node_category(self) -> NodeType:
        """Classify node into functional category"""
        if self.is_trigger():
            return NodeType.TRIGGER
        elif 'webhook' in self.type.lower():
            return NodeType.WEBHOOK
        elif any(t in self.type.lower() for t in ['set', 'function', 'code', 'item']):
            return NodeType.TRANSFORM
        elif any(t in self.type.lower() for t in ['if', 'switch', 'merge', 'split']):
            return NodeType.LOGIC
        else:
            return NodeType.ACTION


@dataclass
class N8nConnection:
    """
    Represents a connection between nodes in the workflow.

    Reasoning: Explicit connection tracking enables dependency resolution and flow validation
    """
    source_node: str
    target_node: str
    source_output: int = 0  # Output index from source
    target_input: int = 0   # Input index to target

    def __repr__(self) -> str:
        return f"{self.source_node}[{self.source_output}] → {self.target_node}[{self.target_input}]"


@dataclass
class WorkflowMetadata:
    """Workflow-level metadata and settings"""
    name: str = "Untitled Workflow"
    active: bool = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    settings: Dict = field(default_factory=dict)


@dataclass
class ParsedWorkflow:
    """
    Complete parsed representation of an n8n workflow.

    This is the primary output of the parser, containing all extracted information
    in a structured, validated format ready for further processing.
    """
    metadata: WorkflowMetadata
    nodes: Dict[str, N8nNode]
    connections: List[N8nConnection]
    raw_json: Dict

    # Computed properties
    node_count: int = 0
    trigger_nodes: List[str] = field(default_factory=list)
    required_credentials: Set[str] = field(default_factory=set)
    execution_order: List[str] = field(default_factory=list)

    def get_entry_points(self) -> List[str]:
        """
        Identify workflow entry points (trigger nodes).

        Reasoning: Entry points are critical for understanding workflow execution flow
        """
        return self.trigger_nodes

    def get_node_by_name(self, name: str) -> Optional[N8nNode]:
        """Find node by name"""
        for node in self.nodes.values():
            if node.name == name:
                return node
        return None

    def get_dependencies(self, node_name: str) -> List[str]:
        """
        Get all nodes that the specified node depends on.

        Reasoning: Dependency tracking essential for validation and optimization
        """
        dependencies = []
        for conn in self.connections:
            if conn.target_node == node_name:
                dependencies.append(conn.source_node)
        return dependencies

    def get_dependents(self, node_name: str) -> List[str]:
        """Get all nodes that depend on the specified node"""
        dependents = []
        for conn in self.connections:
            if conn.source_node == node_name:
                dependents.append(conn.target_node)
        return dependents

    def has_circular_dependencies(self) -> Tuple[bool, List[str]]:
        """
        Detect circular dependencies in the workflow.

        Returns: (has_cycles, cycle_path)

        Reasoning: Circular dependencies cause infinite loops and must be detected
        """
        visited = set()
        rec_stack = set()
        cycle_path = []

        def visit(node: str, path: List[str]) -> bool:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for dependent in self.get_dependents(node):
                if dependent not in visited:
                    if visit(dependent, path):
                        return True
                elif dependent in rec_stack:
                    # Found cycle
                    cycle_start = path.index(dependent)
                    cycle_path.extend(path[cycle_start:])
                    return True

            path.pop()
            rec_stack.remove(node)
            return False

        for node in self.nodes:
            if node not in visited:
                if visit(node, []):
                    return True, cycle_path

        return False, []


class N8nSchemaParser:
    """
    Main parser class for n8n workflow JSON files.

    Responsibilities:
    - Load and validate JSON structure
    - Extract nodes, connections, metadata
    - Perform schema validation
    - Build structured ParsedWorkflow object

    Reasoning: Single responsibility parser with comprehensive validation
    """

    def __init__(self, strict_mode: bool = True):
        """
        Initialize parser.

        Args:
            strict_mode: If True, raise exceptions on validation errors.
                        If False, log warnings and continue parsing.
        """
        self.strict_mode = strict_mode
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def parse_file(self, filepath: str) -> Optional[ParsedWorkflow]:
        """
        Parse n8n workflow from JSON file.

        Args:
            filepath: Path to .json workflow file

        Returns:
            ParsedWorkflow object or None if parsing fails
        """
        logger.info(f"Parsing workflow file: {filepath}")

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                workflow_json = json.load(f)
            return self.parse_json(workflow_json)
        except FileNotFoundError:
            self._handle_error(f"File not found: {filepath}")
            return None
        except json.JSONDecodeError as e:
            self._handle_error(f"Invalid JSON: {e}")
            return None

    def parse_json(self, workflow_json: Dict) -> Optional[ParsedWorkflow]:
        """
        Parse n8n workflow from dictionary.

        Args:
            workflow_json: Dictionary representation of n8n workflow

        Returns:
            ParsedWorkflow object or None if parsing fails
        """
        logger.info("Parsing workflow JSON")

        # Reset error/warning state
        self.errors = []
        self.warnings = []

        # Validate basic structure
        if not self._validate_basic_structure(workflow_json):
            return None

        # Extract components
        metadata = self._extract_metadata(workflow_json)
        nodes = self._extract_nodes(workflow_json)
        connections = self._extract_connections(workflow_json, nodes)

        # Build ParsedWorkflow
        parsed = ParsedWorkflow(
            metadata=metadata,
            nodes=nodes,
            connections=connections,
            raw_json=workflow_json,
            node_count=len(nodes)
        )

        # Compute derived properties
        self._compute_trigger_nodes(parsed)
        self._compute_required_credentials(parsed)
        self._compute_execution_order(parsed)

        # Validate workflow logic
        self._validate_workflow_logic(parsed)

        if self.errors and self.strict_mode:
            logger.error(f"Parsing failed with {len(self.errors)} errors")
            for error in self.errors:
                logger.error(f"  - {error}")
            return None

        logger.info(f"Successfully parsed workflow: {metadata.name} ({len(nodes)} nodes)")
        return parsed

    def _validate_basic_structure(self, workflow_json: Dict) -> bool:
        """
        Validate that JSON has required top-level fields.

        Reasoning: Early validation prevents cascading errors
        """
        required_fields = ['nodes']

        for field in required_fields:
            if field not in workflow_json:
                self._handle_error(f"Missing required field: {field}")
                return False

        if not isinstance(workflow_json['nodes'], list):
            self._handle_error("'nodes' must be a list")
            return False

        return True

    def _extract_metadata(self, workflow_json: Dict) -> WorkflowMetadata:
        """Extract workflow-level metadata"""
        return WorkflowMetadata(
            name=workflow_json.get('name', 'Untitled Workflow'),
            active=workflow_json.get('active', False),
            created_at=workflow_json.get('createdAt'),
            updated_at=workflow_json.get('updatedAt'),
            tags=workflow_json.get('tags', []),
            settings=workflow_json.get('settings', {})
        )

    def _extract_nodes(self, workflow_json: Dict) -> Dict[str, N8nNode]:
        """
        Extract and validate all nodes.

        Returns: Dictionary mapping node names to N8nNode objects

        Reasoning: Name-based indexing enables fast lookups during connection parsing
        """
        nodes = {}

        for node_data in workflow_json['nodes']:
            try:
                node = self._parse_node(node_data)
                if node.name in nodes:
                    self._handle_warning(f"Duplicate node name: {node.name}")
                nodes[node.name] = node
            except Exception as e:
                self._handle_error(f"Failed to parse node: {e}")

        return nodes

    def _parse_node(self, node_data: Dict) -> N8nNode:
        """Parse a single node from JSON"""
        # Validate required fields
        required = ['name', 'type', 'typeVersion', 'position']
        for field in required:
            if field not in node_data:
                raise ValueError(f"Node missing required field: {field}")

        return N8nNode(
            id=node_data.get('id', node_data['name']),
            name=node_data['name'],
            type=node_data['type'],
            type_version=node_data['typeVersion'],
            position=(node_data['position'][0], node_data['position'][1]),
            parameters=node_data.get('parameters', {}),
            credentials=node_data.get('credentials'),
            disabled=node_data.get('disabled', False),
            notes=node_data.get('notes', '')
        )

    def _extract_connections(self, workflow_json: Dict, nodes: Dict[str, N8nNode]) -> List[N8nConnection]:
        """
        Extract and validate connections between nodes.

        Reasoning: Connection validation ensures workflow integrity
        """
        connections = []

        if 'connections' not in workflow_json:
            self._handle_warning("No connections defined in workflow")
            return connections

        conn_data = workflow_json['connections']

        for source_name, outputs in conn_data.items():
            if source_name not in nodes:
                self._handle_error(f"Connection references non-existent source node: {source_name}")
                continue

            for output_type, output_connections in outputs.items():
                for output_idx, targets in enumerate(output_connections):
                    if targets is None:
                        continue

                    for target in targets:
                        target_name = target['node']
                        target_input = target.get('type', 'main')
                        target_idx = target.get('index', 0)

                        if target_name not in nodes:
                            self._handle_error(f"Connection references non-existent target node: {target_name}")
                            continue

                        connections.append(N8nConnection(
                            source_node=source_name,
                            target_node=target_name,
                            source_output=output_idx,
                            target_input=target_idx
                        ))

        return connections

    def _compute_trigger_nodes(self, workflow: ParsedWorkflow) -> None:
        """Identify trigger nodes in the workflow"""
        workflow.trigger_nodes = [
            name for name, node in workflow.nodes.items()
            if node.is_trigger()
        ]

        if not workflow.trigger_nodes:
            self._handle_warning("No trigger nodes found - workflow may not be executable")

    def _compute_required_credentials(self, workflow: ParsedWorkflow) -> None:
        """Extract all credential types required by the workflow"""
        credentials = set()

        for node in workflow.nodes.values():
            if node.credentials:
                for cred_type in node.credentials.keys():
                    credentials.add(cred_type)

        workflow.required_credentials = credentials

    def _compute_execution_order(self, workflow: ParsedWorkflow) -> None:
        """
        Compute topological execution order of nodes.

        Reasoning: Execution order critical for workflow simulation and optimization
        """
        # Simple topological sort using Kahn's algorithm
        in_degree = {name: 0 for name in workflow.nodes}

        for conn in workflow.connections:
            in_degree[conn.target_node] += 1

        queue = [name for name, degree in in_degree.items() if degree == 0]
        execution_order = []

        while queue:
            node = queue.pop(0)
            execution_order.append(node)

            for dependent in workflow.get_dependents(node):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        workflow.execution_order = execution_order

    def _validate_workflow_logic(self, workflow: ParsedWorkflow) -> None:
        """
        Perform logical validation of workflow structure.

        Checks:
        - Circular dependencies
        - Disconnected nodes
        - Missing credentials
        """
        # Check for cycles
        has_cycle, cycle_path = workflow.has_circular_dependencies()
        if has_cycle:
            self._handle_error(f"Circular dependency detected: {' → '.join(cycle_path)}")

        # Check for disconnected nodes (except triggers)
        for name, node in workflow.nodes.items():
            if not node.is_trigger():
                dependencies = workflow.get_dependencies(name)
                dependents = workflow.get_dependents(name)

                if not dependencies and not dependents:
                    self._handle_warning(f"Node '{name}' is disconnected from workflow")

    def _handle_error(self, message: str) -> None:
        """Handle parsing error"""
        self.errors.append(message)
        if self.strict_mode:
            logger.error(message)
        else:
            logger.warning(f"Error (non-strict): {message}")

    def _handle_warning(self, message: str) -> None:
        """Handle parsing warning"""
        self.warnings.append(message)
        logger.warning(message)


# Convenience functions for quick parsing
def parse_workflow_file(filepath: str, strict: bool = True) -> Optional[ParsedWorkflow]:
    """
    Parse n8n workflow from file.

    Args:
        filepath: Path to workflow JSON file
        strict: Enable strict validation mode

    Returns:
        ParsedWorkflow object or None
    """
    parser = N8nSchemaParser(strict_mode=strict)
    return parser.parse_file(filepath)


def parse_workflow_json(workflow_json: Dict, strict: bool = True) -> Optional[ParsedWorkflow]:
    """
    Parse n8n workflow from dictionary.

    Args:
        workflow_json: Workflow JSON as dictionary
        strict: Enable strict validation mode

    Returns:
        ParsedWorkflow object or None
    """
    parser = N8nSchemaParser(strict_mode=strict)
    return parser.parse_json(workflow_json)


if __name__ == "__main__":
    # Example usage and testing
    print("n8n Schema Parser v1.0.0")
    print("=" * 60)
    print("\nThis module provides parsing capabilities for n8n workflows.")
    print("\nUsage:")
    print("  from parse_n8n_schema import parse_workflow_file")
    print("  workflow = parse_workflow_file('my_workflow.json')")
    print("  print(f'Nodes: {workflow.node_count}')")
    print("  print(f'Triggers: {workflow.trigger_nodes}')")
    print("\nFor detailed documentation, see: docs/architecture.md")
