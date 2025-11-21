"""
Project Automata: Skills Module

Reusable utilities and tools for workflow generation and validation.

Author: Project Automata
Version: 1.0.0
"""

# Version info
__version__ = "1.0.0"
__author__ = "Project Automata"

# Expose main functionality
try:
    from .parse_n8n_schema import N8nSchemaParser, parse_workflow_file, parse_workflow_json
except ImportError:
    pass

try:
    from .generate_workflow_json import TemplateLibrary, WorkflowBuilder, generate_from_template
except ImportError:
    pass
