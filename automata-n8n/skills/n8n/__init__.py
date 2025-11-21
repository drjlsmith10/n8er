"""
n8n API Client Package

Refactored client architecture with specialized clients for different operations.

Author: Project Automata - Architecture Specialist
Version: 2.0.0
Created: 2025-11-21
"""

from .base_client import BaseN8nClient
from .workflow_client import WorkflowClient
from .execution_client import ExecutionClient
from .health_client import HealthClient

__all__ = [
    "BaseN8nClient",
    "WorkflowClient",
    "ExecutionClient",
    "HealthClient",
]
