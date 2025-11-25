"""
Researcher Agent - DEPRECATED

This module is deprecated. Use KnowledgeAgent instead.

For backwards compatibility, this re-exports KnowledgeAgent as ResearcherAgent.

Author: Project Automata
Version: 2.2.0 (Deprecated - use agents.knowledge.KnowledgeAgent)
"""

import warnings

from agents.knowledge import KnowledgeAgent

# Emit deprecation warning on import
warnings.warn(
    "ResearcherAgent is deprecated. Use KnowledgeAgent from agents.knowledge instead.",
    DeprecationWarning,
    stacklevel=2
)

# Backwards compatibility alias
ResearcherAgent = KnowledgeAgent

__all__ = ["ResearcherAgent"]
