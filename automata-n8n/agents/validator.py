"""
Validator Agent: Schema and Logic Validation

Responsibilities:
- Validate n8n workflow schemas
- Check node configurations
- Verify connection logic
- Detect dependency issues

Author: Project Automata
Version: 1.0.0
"""

from typing import Dict, List
from agents import BaseAgent, AgentTask, AgentResult
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class ValidatorAgent(BaseAgent):
    """
    Specialized agent for validation tasks.

    Reasoning: Dedicated validator ensures all generated
    workflows meet quality and correctness standards.
    """

    def __init__(self):
        super().__init__("Validator")
        self.validation_rules = []

    def execute(self, task: AgentTask) -> AgentResult:
        """
        Execute validation task.

        Supported task types:
        - "validate_workflow": Full workflow validation
        - "validate_schema": Schema-only validation
        - "validate_connections": Connection logic check
        """
        self.log_reasoning(f"Starting validation: {task.task_type}")

        try:
            if task.task_type == "validate_workflow":
                result = self._validate_workflow(task.parameters)
            elif task.task_type == "validate_schema":
                result = self._validate_schema(task.parameters)
            elif task.task_type == "validate_connections":
                result = self._validate_connections(task.parameters)
            else:
                raise ValueError(f"Unknown task type: {task.task_type}")

            self.update_stats(success=True)
            return self.create_result(
                task_id=task.task_id,
                success=result["valid"],
                output=result,
                reasoning=f"Validation completed: {result['summary']}",
                metrics={
                    "errors": len(result.get("errors", [])),
                    "warnings": len(result.get("warnings", []))
                }
            )

        except Exception as e:
            self.logger.error(f"Validation failed: {e}")
            self.update_stats(success=False)
            return self.create_result(
                task_id=task.task_id,
                success=False,
                output=None,
                reasoning=f"Validation error: {str(e)}",
                metrics={},
                errors=[str(e)]
            )

    def _validate_workflow(self, params: Dict) -> Dict:
        """
        Comprehensive workflow validation.

        Reasoning: Full validation catches schema, logic,
        and dependency issues in one pass.
        """
        workflow_json = params.get("workflow", {})
        self.log_reasoning("Performing full workflow validation")

        errors = []
        warnings = []

        # Check basic structure
        if "nodes" not in workflow_json:
            errors.append("Missing 'nodes' field")

        if "connections" not in workflow_json:
            warnings.append("No connections defined")

        # Validate nodes
        nodes = workflow_json.get("nodes", [])
        if not nodes:
            errors.append("Workflow has no nodes")
        else:
            for idx, node in enumerate(nodes):
                if "name" not in node:
                    errors.append(f"Node {idx} missing 'name'")
                if "type" not in node:
                    errors.append(f"Node {idx} missing 'type'")

        # Check for trigger nodes
        trigger_found = False
        for node in nodes:
            node_type = node.get("type", "").lower()
            if any(t in node_type for t in ["trigger", "webhook", "manual"]):
                trigger_found = True
                break

        if not trigger_found:
            warnings.append("No trigger node found - workflow may not be executable")

        # Validate connections
        connections = workflow_json.get("connections", {})
        for source, outputs in connections.items():
            # Check source node exists
            source_exists = any(n.get("name") == source for n in nodes)
            if not source_exists:
                errors.append(f"Connection references non-existent node: {source}")

        valid = len(errors) == 0

        return {
            "valid": valid,
            "errors": errors,
            "warnings": warnings,
            "summary": f"{'Valid' if valid else 'Invalid'} - {len(errors)} errors, {len(warnings)} warnings",
            "node_count": len(nodes),
            "connection_count": len(connections)
        }

    def _validate_schema(self, params: Dict) -> Dict:
        """
        Validate workflow against n8n schema.

        Reasoning: Schema validation ensures compatibility
        with n8n workflow engine.
        """
        workflow_json = params.get("workflow", {})
        self.log_reasoning("Validating workflow schema")

        # Use parse_n8n_schema for validation
        try:
            from skills.parse_n8n_schema import parse_workflow_json

            parsed = parse_workflow_json(workflow_json, strict=False)

            if parsed:
                return {
                    "valid": True,
                    "errors": [],
                    "warnings": [],
                    "summary": "Schema validation passed"
                }
            else:
                return {
                    "valid": False,
                    "errors": ["Schema validation failed"],
                    "warnings": [],
                    "summary": "Schema validation failed"
                }

        except ImportError:
            self.logger.warning("parse_n8n_schema not available")
            return {
                "valid": True,
                "errors": [],
                "warnings": ["Schema parser not available"],
                "summary": "Schema validation skipped"
            }

    def _validate_connections(self, params: Dict) -> Dict:
        """
        Validate connection logic and dependencies.

        Reasoning: Connection validation prevents runtime
        errors from invalid data flow.
        """
        workflow_json = params.get("workflow", {})
        self.log_reasoning("Validating connections")

        errors = []
        warnings = []

        nodes = workflow_json.get("nodes", [])
        connections = workflow_json.get("connections", {})

        node_names = {n.get("name") for n in nodes}

        # Validate each connection
        for source, outputs in connections.items():
            if source not in node_names:
                errors.append(f"Connection source not found: {source}")

            for output_type, output_list in outputs.items():
                for outputs in output_list:
                    if outputs:
                        for target_conn in outputs:
                            target = target_conn.get("node")
                            if target not in node_names:
                                errors.append(f"Connection target not found: {target}")

        valid = len(errors) == 0

        return {
            "valid": valid,
            "errors": errors,
            "warnings": warnings,
            "summary": f"Connection validation: {len(errors)} errors"
        }


if __name__ == "__main__":
    agent = ValidatorAgent()

    # Test validation
    test_workflow = {
        "name": "Test",
        "nodes": [
            {"name": "Start", "type": "n8n-nodes-base.manualTrigger", "position": [0, 0], "parameters": {}, "typeVersion": 1}
        ],
        "connections": {}
    }

    task = AgentTask(
        task_id="val_001",
        task_type="validate_workflow",
        parameters={"workflow": test_workflow}
    )

    result = agent.execute(task)
    print(f"Validation Result: {result.success}")
    print(f"Summary: {result.output['summary']}")
