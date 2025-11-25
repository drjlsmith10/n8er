"""
Documenter Agent - DEPRECATED

This module is deprecated. Use BuilderAgent instead.

For backwards compatibility, this re-exports BuilderAgent as DocumenterAgent.

Author: Project Automata
Version: 2.2.0 (Deprecated - use agents.builder.BuilderAgent)
"""

import warnings

from agents.builder import BuilderAgent

# Emit deprecation warning on import
warnings.warn(
    "DocumenterAgent is deprecated. Use BuilderAgent from agents.builder instead.",
    DeprecationWarning,
    stacklevel=2
)

# Backwards compatibility alias
DocumenterAgent = BuilderAgent

__all__ = ["DocumenterAgent"]
