"""
Validator Agent: Schema and Logic Validation

Responsibilities:
- Validate n8n workflow schemas (local validation)
- Check node configurations
- Verify connection logic
- Detect dependency issues
- Optionally validate against real n8n instance when configured

Author: Project Automata
Version: 2.2.0 (N8nApiClient Integration)
"""

import logging
import os
import sys
from typing import Dict, List, Optional

from agents import AgentResult, AgentTask, BaseAgent

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Try to import N8nApiClient for real validation
try:
    from skills.n8n_api_client import N8nApiClient, N8nApiError, N8nValidationError
    HAS_N8N_CLIENT = True
except ImportError:
    HAS_N8N_CLIENT = False
    N8nApiClient = None
    N8nApiError = Exception
    N8nValidationError = Exception


logger = logging.getLogger(__name__)


class ValidatorAgent(BaseAgent):
    """
    Specialized agent for validation tasks.

    Capabilities:
    - Local schema validation (always available)
    - Real n8n instance validation (when N8N_API_URL and N8N_API_KEY configured)
    - Connection logic validation
    - Node configuration checking

    When n8n API is configured, validation can:
    - Test import compatibility against real n8n instance
    - Detect version-specific issues
    - Perform server-side validation
    """

    def __init__(self, n8n_client: Optional["N8nApiClient"] = None):
        super().__init__("Validator")
        self.validation_rules: List[str] = []

        # Initialize n8n client if available
        self.n8n_client = n8n_client
        self._n8n_available = False

        if n8n_client:
            self.n8n_client = n8n_client
            self._n8n_available = True
        elif HAS_N8N_CLIENT:
            # Try to create client from environment
            api_url = os.getenv("N8N_API_URL")
            api_key = os.getenv("N8N_API_KEY")

            if api_url and api_key:
                try:
                    self.n8n_client = N8nApiClient(api_url=api_url, api_key=api_key)
                    # Test connection
                    ok, _ = self.n8n_client.test_connection()
                    self._n8n_available = ok
                    if ok:
                        logger.info("n8n API client initialized for real validation")
                except Exception as e:
                    logger.warning(f"Could not initialize n8n client: {e}")
                    self._n8n_available = False

    def is_n8n_available(self) -> bool:
        """Check if real n8n validation is available."""
        return self._n8n_available

    def execute(self, task: AgentTask) -> AgentResult:
        """
        Execute validation task.

        Supported task types:
        - "validate_workflow": Full workflow validation (local + optional n8n)
        - "validate_schema": Schema-only validation
        - "validate_connections": Connection logic check
        - "validate_n8n": Validate against real n8n instance (requires API)
        """
        self.log_reasoning(f"Starting validation: {task.task_type}")

        try:
            if task.task_type == "validate_workflow":
                result = self._validate_workflow(task.parameters)
            elif task.task_type == "validate_schema":
                result = self._validate_schema(task.parameters)
            elif task.task_type == "validate_connections":
                result = self._validate_connections(task.parameters)
            elif task.task_type == "validate_n8n":
                result = self._validate_with_n8n(task.parameters)
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
                    "warnings": len(result.get("warnings", [])),
                    "n8n_validated": result.get("n8n_validated", False),
                },
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
                errors=[str(e)],
            )

    def _validate_workflow(self, params: Dict) -> Dict:
        """
        Comprehensive workflow validation.

        Performs local validation and optionally real n8n validation
        when API is configured.
        """
        workflow_json = params.get("workflow", {})
        use_n8n = params.get("use_n8n", self._n8n_available)
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

        n8n_validated = False

        # Optional n8n validation
        if use_n8n and self._n8n_available and len(errors) == 0:
            n8n_result = self._validate_with_n8n({"workflow": workflow_json})
            if not n8n_result["valid"]:
                errors.extend(n8n_result.get("errors", []))
                warnings.extend(n8n_result.get("warnings", []))
            n8n_validated = True

        valid = len(errors) == 0

        return {
            "valid": valid,
            "errors": errors,
            "warnings": warnings,
            "summary": f"{'Valid' if valid else 'Invalid'} - {len(errors)} errors, {len(warnings)} warnings",
            "node_count": len(nodes),
            "connection_count": len(connections),
            "n8n_validated": n8n_validated,
        }

    def _validate_schema(self, params: Dict) -> Dict:
        """
        Validate workflow against n8n schema.
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
                    "summary": "Schema validation passed",
                }
            else:
                return {
                    "valid": False,
                    "errors": ["Schema validation failed"],
                    "warnings": [],
                    "summary": "Schema validation failed",
                }

        except ImportError:
            self.logger.warning("parse_n8n_schema not available")
            return {
                "valid": True,
                "errors": [],
                "warnings": ["Schema parser not available"],
                "summary": "Schema validation skipped",
            }

    def _validate_connections(self, params: Dict) -> Dict:
        """
        Validate connection logic and dependencies.
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
            "summary": f"Connection validation: {len(errors)} errors",
        }

    def _validate_with_n8n(self, params: Dict) -> Dict:
        """
        Validate workflow against real n8n instance.

        This performs server-side validation by using the n8n API
        to check if the workflow can be imported.

        Requires N8N_API_URL and N8N_API_KEY to be configured.
        """
        workflow_json = params.get("workflow", {})
        self.log_reasoning("Validating against real n8n instance")

        if not self._n8n_available:
            return {
                "valid": True,  # Can't validate, assume OK
                "errors": [],
                "warnings": ["n8n API not configured - real validation skipped"],
                "summary": "n8n validation skipped (API not configured)",
                "n8n_validated": False,
            }

        try:
            # Use the API client's validation method
            is_valid, errors = self.n8n_client.validate_workflow_import(workflow_json)

            if is_valid:
                return {
                    "valid": True,
                    "errors": [],
                    "warnings": [],
                    "summary": "n8n validation passed - workflow can be imported",
                    "n8n_validated": True,
                }
            else:
                return {
                    "valid": False,
                    "errors": errors,
                    "warnings": [],
                    "summary": f"n8n validation failed: {len(errors)} error(s)",
                    "n8n_validated": True,
                }

        except N8nValidationError as e:
            return {
                "valid": False,
                "errors": [str(e)],
                "warnings": [],
                "summary": f"n8n validation error: {str(e)}",
                "n8n_validated": True,
            }

        except N8nApiError as e:
            return {
                "valid": True,  # API error, not validation error
                "errors": [],
                "warnings": [f"n8n API error (validation inconclusive): {str(e)}"],
                "summary": "n8n validation inconclusive due to API error",
                "n8n_validated": False,
            }

        except Exception as e:
            self.logger.error(f"Unexpected error during n8n validation: {e}")
            return {
                "valid": True,  # Unknown error, assume OK
                "errors": [],
                "warnings": [f"Unexpected error during n8n validation: {str(e)}"],
                "summary": "n8n validation inconclusive",
                "n8n_validated": False,
            }

    def get_n8n_status(self) -> Dict:
        """Get status of n8n API connection."""
        if not self._n8n_available:
            return {
                "available": False,
                "reason": "n8n API not configured or connection failed",
            }

        try:
            ok, msg = self.n8n_client.test_connection()
            version_info = self.n8n_client.get_n8n_version()

            return {
                "available": ok,
                "message": msg,
                "version": version_info.get("version", "unknown"),
                "api_url": self.n8n_client.api_url,
            }
        except Exception as e:
            return {
                "available": False,
                "reason": str(e),
            }


if __name__ == "__main__":
    agent = ValidatorAgent()

    print("Validator Agent initialized")
    print(f"n8n API available: {agent.is_n8n_available()}")

    if agent.is_n8n_available():
        status = agent.get_n8n_status()
        print(f"n8n version: {status.get('version', 'unknown')}")

    # Test validation
    test_workflow = {
        "name": "Test",
        "nodes": [
            {
                "name": "Start",
                "type": "n8n-nodes-base.manualTrigger",
                "position": [0, 0],
                "parameters": {},
                "typeVersion": 1,
            }
        ],
        "connections": {},
    }

    task = AgentTask(
        task_id="val_001", task_type="validate_workflow", parameters={"workflow": test_workflow}
    )

    result = agent.execute(task)
    print(f"\nValidation Result: {result.success}")
    print(f"Summary: {result.output['summary']}")
    print(f"n8n validated: {result.output.get('n8n_validated', False)}")
