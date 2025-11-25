"""
Project Automata: Agent Framework

Base classes and utilities for the simplified multi-agent system.

Simplified Architecture (v2.2.0):
- KnowledgeAgent: Research and knowledge base management (agents.knowledge)
- BuilderAgent: Code and documentation generation (agents.builder)
- ValidatorAgent: Workflow validation (agents.validator)

Deprecated agents (shims for backwards compatibility):
- ResearcherAgent → use KnowledgeAgent
- WebResearcherAgent → use KnowledgeAgent
- EngineerAgent → use BuilderAgent
- DocumenterAgent → use BuilderAgent
- TesterAgent → REMOVED (was mock-only)
- ProjectManagerAgent → REMOVED (was mock-only)

Author: Project Automata
Version: 2.2.0 (Architecture Simplification)
Created: 2025-11-08
Updated: 2025-11-25
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


@dataclass
class AgentTask:
    """Standardized task input for agents"""

    task_id: str
    task_type: str
    parameters: Dict[str, Any]
    context: Dict[str, Any] = None
    priority: int = 1


@dataclass
class AgentResult:
    """Standardized result output from agents"""

    task_id: str
    agent_name: str
    success: bool
    output: Any
    reasoning: str
    metrics: Dict[str, Any]
    timestamp: str
    errors: List[str] = None
    warnings: List[str] = None


class BaseAgent(ABC):
    """
    Abstract base class for all Automata agents.

    All agents must implement execute() and provide standardized
    logging, error handling, and result formatting.
    """

    def __init__(self, name: str):
        """Initialize base agent"""
        self.name = name
        self.logger = logging.getLogger(f"Agent.{name}")
        self.task_count = 0
        self.success_count = 0
        self.error_count = 0

    @abstractmethod
    def execute(self, task: AgentTask) -> AgentResult:
        """
        Execute assigned task.

        Args:
            task: Standardized AgentTask

        Returns:
            AgentResult with output and reasoning

        Reasoning: All agents must implement core execution logic
        """
        pass

    def log_reasoning(self, message: str) -> None:
        """Log reasoning trace for transparency"""
        self.logger.info(f"[REASONING] {message}")

    def create_result(
        self,
        task_id: str,
        success: bool,
        output: Any,
        reasoning: str,
        metrics: Dict[str, Any] = None,
        errors: List[str] = None,
        warnings: List[str] = None,
    ) -> AgentResult:
        """Helper to create standardized results"""
        return AgentResult(
            task_id=task_id,
            agent_name=self.name,
            success=success,
            output=output,
            reasoning=reasoning,
            metrics=metrics or {},
            timestamp=datetime.utcnow().isoformat() + "Z",
            errors=errors or [],
            warnings=warnings or [],
        )

    def update_stats(self, success: bool) -> None:
        """Update agent performance statistics"""
        self.task_count += 1
        if success:
            self.success_count += 1
        else:
            self.error_count += 1

    def get_performance(self) -> Dict[str, Any]:
        """Get agent performance metrics"""
        success_rate = (self.success_count / self.task_count * 100) if self.task_count > 0 else 0

        return {
            "agent": self.name,
            "tasks_completed": self.task_count,
            "successes": self.success_count,
            "errors": self.error_count,
            "success_rate": f"{success_rate:.1f}%",
        }
