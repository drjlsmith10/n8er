"""
n8n API Client Package

Provides modular clients for interacting with n8n REST API.
Split from monolithic N8nApiClient into focused, single-responsibility clients.

Author: Project Automata
Version: 2.0.0
"""

from .base_client import BaseN8nClient, N8nApiError, N8nAuthenticationError, N8nConnectionError
from .workflow_client import WorkflowClient
from .execution_client import ExecutionClient
from .health_client import HealthClient
from .client import N8nClient

__all__ = [
    "N8nClient",
    "BaseN8nClient",
    "WorkflowClient",
    "ExecutionClient",
    "HealthClient",
    "N8nApiError",
    "N8nAuthenticationError",
    "N8nConnectionError",
]
