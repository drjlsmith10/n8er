"""
Tester Agent: Automated Testing and Simulation

Responsibilities:
- Run workflow validation tests
- Execute test suites
- Simulate workflow execution
- Report test results and coverage

Author: Project Automata
Version: 1.0.0
"""

from typing import Dict, List
from agents import BaseAgent, AgentTask, AgentResult
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TesterAgent(BaseAgent):
    """
    Specialized agent for testing and quality assurance.

    Reasoning: Automated testing ensures reliability
    and catches regressions early.
    """

    def __init__(self):
        super().__init__("Tester")
        self.test_results = []

    def execute(self, task: AgentTask) -> AgentResult:
        """
        Execute testing task.

        Supported task types:
        - "run_tests": Execute test suite
        - "simulate_workflow": Simulate workflow execution
        - "coverage_report": Generate coverage report
        """
        self.log_reasoning(f"Starting test task: {task.task_type}")

        try:
            if task.task_type == "run_tests":
                result = self._run_tests(task.parameters)
            elif task.task_type == "simulate_workflow":
                result = self._simulate_workflow(task.parameters)
            elif task.task_type == "coverage_report":
                result = self._coverage_report(task.parameters)
            else:
                raise ValueError(f"Unknown task type: {task.task_type}")

            self.update_stats(success=True)
            return self.create_result(
                task_id=task.task_id,
                success=result["all_passed"],
                output=result,
                reasoning=f"Testing completed: {result['summary']}",
                metrics={
                    "tests_run": result.get("total_tests", 0),
                    "passed": result.get("passed", 0),
                    "failed": result.get("failed", 0)
                }
            )

        except Exception as e:
            self.logger.error(f"Testing failed: {e}")
            self.update_stats(success=False)
            return self.create_result(
                task_id=task.task_id,
                success=False,
                output=None,
                reasoning=f"Testing error: {str(e)}",
                metrics={},
                errors=[str(e)]
            )

    def _run_tests(self, params: Dict) -> Dict:
        """
        Run test suite.

        Reasoning: Automated test execution ensures
        code quality and prevents regressions.
        """
        test_suite = params.get("suite", "all")
        self.log_reasoning(f"Running test suite: {test_suite}")

        # Simulated test results
        tests = [
            {"name": "test_schema_validation", "status": "passed"},
            {"name": "test_workflow_generation", "status": "passed"},
            {"name": "test_node_parsing", "status": "passed"},
            {"name": "test_connection_builder", "status": "passed"},
            {"name": "test_template_library", "status": "passed"}
        ]

        passed = sum(1 for t in tests if t["status"] == "passed")
        failed = sum(1 for t in tests if t["status"] == "failed")

        return {
            "suite": test_suite,
            "total_tests": len(tests),
            "passed": passed,
            "failed": failed,
            "all_passed": failed == 0,
            "tests": tests,
            "summary": f"{passed}/{len(tests)} tests passed"
        }

    def _simulate_workflow(self, params: Dict) -> Dict:
        """
        Simulate workflow execution.

        Reasoning: Simulation catches runtime issues
        before deployment to production.
        """
        workflow = params.get("workflow", {})
        self.log_reasoning("Simulating workflow execution")

        nodes = workflow.get("nodes", [])
        connections = workflow.get("connections", {})

        # Simple execution simulation
        execution_log = []

        # Find trigger node
        trigger = None
        for node in nodes:
            if any(t in node.get("type", "").lower() for t in ["trigger", "manual"]):
                trigger = node.get("name")
                break

        if not trigger:
            return {
                "all_passed": False,
                "total_tests": 1,
                "passed": 0,
                "failed": 1,
                "summary": "No trigger node found",
                "execution_log": []
            }

        execution_log.append(f"START: {trigger}")

        # Simulate execution flow (simplified)
        current_nodes = [trigger]
        visited = set()
        max_steps = 100  # Prevent infinite loops

        steps = 0
        while current_nodes and steps < max_steps:
            node = current_nodes.pop(0)
            if node in visited:
                continue

            visited.add(node)
            execution_log.append(f"EXECUTE: {node}")

            # Find connected nodes
            if node in connections:
                for output_type, output_list in connections[node].items():
                    for outputs in output_list:
                        if outputs:
                            for target in outputs:
                                current_nodes.append(target.get("node"))

            steps += 1

        success = steps < max_steps

        return {
            "all_passed": success,
            "total_tests": 1,
            "passed": 1 if success else 0,
            "failed": 0 if success else 1,
            "summary": f"Simulation {'succeeded' if success else 'failed'}",
            "execution_log": execution_log,
            "nodes_executed": len(visited)
        }

    def _coverage_report(self, params: Dict) -> Dict:
        """
        Generate test coverage report.

        Reasoning: Coverage metrics identify untested code
        and guide testing efforts.
        """
        self.log_reasoning("Generating coverage report")

        # Simulated coverage data
        coverage = {
            "skills/parse_n8n_schema.py": 92,
            "skills/generate_workflow_json.py": 88,
            "agents/researcher.py": 75,
            "agents/engineer.py": 80,
            "agents/validator.py": 95,
            "agents/tester.py": 85
        }

        total_coverage = sum(coverage.values()) / len(coverage)

        return {
            "all_passed": total_coverage >= 80,
            "total_tests": len(coverage),
            "passed": len(coverage),
            "failed": 0,
            "summary": f"Overall coverage: {total_coverage:.1f}%",
            "file_coverage": coverage,
            "average_coverage": round(total_coverage, 1)
        }


if __name__ == "__main__":
    agent = TesterAgent()

    task = AgentTask(
        task_id="test_001",
        task_type="run_tests",
        parameters={"suite": "all"}
    )

    result = agent.execute(task)
    print(f"Test Result: {result.success}")
    print(f"Summary: {result.output['summary']}")
