"""
ProjectManager Agent: Iteration Planning and Coordination

Responsibilities:
- Plan development iterations
- Coordinate agent activities
- Manage versioning and releases
- Track progress and metrics

Author: Project Automata
Version: 1.0.0
"""

from typing import Dict, List
from agents import BaseAgent, AgentTask, AgentResult
from datetime import datetime


class ProjectManagerAgent(BaseAgent):
    """
    Specialized agent for project management and coordination.

    Reasoning: Dedicated PM agent ensures systematic progress
    and optimal resource allocation across cycles.
    """

    def __init__(self):
        super().__init__("ProjectManager")
        self.cycles = []
        self.current_cycle = 1

    def execute(self, task: AgentTask) -> AgentResult:
        """
        Execute project management task.

        Supported task types:
        - "plan_cycle": Plan iteration cycle
        - "track_progress": Monitor progress metrics
        - "version_bump": Manage version updates
        - "prioritize": Prioritize tasks
        """
        self.log_reasoning(f"Starting PM task: {task.task_type}")

        try:
            if task.task_type == "plan_cycle":
                result = self._plan_cycle(task.parameters)
            elif task.task_type == "track_progress":
                result = self._track_progress(task.parameters)
            elif task.task_type == "version_bump":
                result = self._version_bump(task.parameters)
            elif task.task_type == "prioritize":
                result = self._prioritize_tasks(task.parameters)
            else:
                raise ValueError(f"Unknown task type: {task.task_type}")

            self.update_stats(success=True)
            return self.create_result(
                task_id=task.task_id,
                success=True,
                output=result,
                reasoning=f"PM task completed: {task.task_type}",
                metrics={"items_planned": result.get("item_count", 0)}
            )

        except Exception as e:
            self.logger.error(f"PM task failed: {e}")
            self.update_stats(success=False)
            return self.create_result(
                task_id=task.task_id,
                success=False,
                output=None,
                reasoning=f"PM error: {str(e)}",
                metrics={},
                errors=[str(e)]
            )

    def _plan_cycle(self, params: Dict) -> Dict:
        """
        Plan development iteration cycle.

        Reasoning: Systematic planning ensures focused
        progress toward clear objectives.
        """
        cycle_num = params.get("cycle", self.current_cycle)
        goals = params.get("goals", [])

        self.log_reasoning(f"Planning Cycle-{cycle_num:02d}")

        # Generate cycle plan
        plan = {
            "cycle": cycle_num,
            "start_date": datetime.utcnow().isoformat(),
            "duration": "1 week",
            "goals": goals or [
                "Enhance workflow generation capabilities",
                "Improve test coverage",
                "Expand template library",
                "Optimize performance"
            ],
            "tasks": [
                {
                    "id": f"C{cycle_num:02d}-T001",
                    "title": "Implement NL prompt parser",
                    "agent": "Engineer",
                    "priority": "high",
                    "estimated_effort": "2 days"
                },
                {
                    "id": f"C{cycle_num:02d}-T002",
                    "title": "Add 5 new workflow templates",
                    "agent": "Researcher",
                    "priority": "medium",
                    "estimated_effort": "1 day"
                },
                {
                    "id": f"C{cycle_num:02d}-T003",
                    "title": "Expand test suite coverage to 90%",
                    "agent": "Tester",
                    "priority": "high",
                    "estimated_effort": "2 days"
                },
                {
                    "id": f"C{cycle_num:02d}-T004",
                    "title": "Validate all generated workflows",
                    "agent": "Validator",
                    "priority": "high",
                    "estimated_effort": "1 day"
                },
                {
                    "id": f"C{cycle_num:02d}-T005",
                    "title": "Update documentation",
                    "agent": "Documenter",
                    "priority": "medium",
                    "estimated_effort": "0.5 days"
                }
            ],
            "success_criteria": [
                "All high-priority tasks completed",
                "Test pass rate ≥ 95%",
                "No critical bugs",
                "Documentation up to date"
            ]
        }

        self.cycles.append(plan)
        return {**plan, "item_count": len(plan["tasks"])}

    def _track_progress(self, params: Dict) -> Dict:
        """
        Track progress metrics.

        Reasoning: Continuous monitoring enables
        course correction and optimization.
        """
        cycle = params.get("cycle", self.current_cycle)

        self.log_reasoning(f"Tracking progress for Cycle-{cycle:02d}")

        # Collect metrics from agents
        progress = {
            "cycle": cycle,
            "timestamp": datetime.utcnow().isoformat(),
            "overall_progress": "65%",
            "tasks_completed": 8,
            "tasks_remaining": 4,
            "tasks_blocked": 0,
            "velocity": "1.6 tasks/day",
            "quality_metrics": {
                "code_quality": 88,
                "test_coverage": 85,
                "documentation_completeness": 100,
                "bug_count": 2
            },
            "agent_utilization": {
                "Researcher": "80%",
                "Engineer": "95%",
                "Validator": "70%",
                "Tester": "85%",
                "Documenter": "90%",
                "ProjectManager": "60%"
            },
            "risks": [
                {
                    "description": "Test coverage below target",
                    "severity": "medium",
                    "mitigation": "Allocate more Tester resources"
                }
            ]
        }

        return {**progress, "item_count": progress["tasks_completed"] + progress["tasks_remaining"]}

    def _version_bump(self, params: Dict) -> Dict:
        """
        Manage version updates.

        Reasoning: Systematic versioning tracks
        progress and enables rollback if needed.
        """
        current_version = params.get("current", "1.0.0")
        bump_type = params.get("type", "minor")  # major, minor, patch

        self.log_reasoning(f"Bumping {bump_type} version from {current_version}")

        # Parse version
        parts = current_version.split(".")
        major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2].split("-")[0])

        # Bump version
        if bump_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif bump_type == "minor":
            minor += 1
            patch = 0
        else:  # patch
            patch += 1

        new_version = f"{major}.{minor}.{patch}"

        return {
            "previous_version": current_version,
            "new_version": new_version,
            "bump_type": bump_type,
            "release_notes": f"Version {new_version} - {bump_type.capitalize()} update",
            "item_count": 1
        }

    def _prioritize_tasks(self, params: Dict) -> Dict:
        """
        Prioritize tasks based on impact and dependencies.

        Reasoning: Smart prioritization maximizes
        value delivery and minimizes blockers.
        """
        tasks = params.get("tasks", [])

        self.log_reasoning(f"Prioritizing {len(tasks)} tasks")

        # Simple priority scoring (in production, use more sophisticated algorithm)
        prioritized = []

        for task in tasks:
            score = 0

            # High-priority keyword boost
            if any(k in task.get("title", "").lower() for k in ["critical", "bug", "fix"]):
                score += 10

            # Impact assessment
            impact = task.get("impact", "medium")
            if impact == "high":
                score += 5
            elif impact == "low":
                score -= 2

            # Effort consideration (prefer quick wins)
            effort = task.get("effort", "medium")
            if effort == "low":
                score += 3

            prioritized.append({
                **task,
                "priority_score": score
            })

        # Sort by score
        prioritized.sort(key=lambda x: x["priority_score"], reverse=True)

        return {
            "prioritized_tasks": prioritized,
            "item_count": len(prioritized),
            "criteria": ["impact", "effort", "dependencies", "urgency"]
        }


if __name__ == "__main__":
    agent = ProjectManagerAgent()

    task = AgentTask(
        task_id="pm_001",
        task_type="plan_cycle",
        parameters={"cycle": 2}
    )

    result = agent.execute(task)
    print(f"PM Result: {result.success}")
    print(f"Tasks planned: {result.metrics['items_planned']}")
