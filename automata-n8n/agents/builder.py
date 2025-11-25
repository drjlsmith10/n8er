"""
Builder Agent: Code Generation and Documentation

Consolidates EngineerAgent and DocumenterAgent functionality into a single agent.

Responsibilities:
- Generate code modules and utilities
- Create and maintain documentation
- Review code for quality
- Generate architecture diagrams

NOTE: This agent provides template-based code and documentation generation.
It does NOT use AI/ML for code generation - it applies predefined patterns.

Author: Project Automata - Cycle 02
Version: 2.2.0 (Architecture Simplification)
"""

from datetime import datetime
from typing import Dict, List

from agents import AgentResult, AgentTask, BaseAgent


class BuilderAgent(BaseAgent):
    """
    Unified agent for code and documentation generation.

    This agent consolidates the previous EngineerAgent and DocumenterAgent
    into a single, streamlined builder.

    Capabilities:
    - Generate code module templates
    - Create documentation from templates
    - Review code for quality
    - Generate changelogs and reports
    - Create architecture diagrams (Mermaid format)

    NOTE: This agent uses predefined templates, not AI generation.
    """

    def __init__(self):
        super().__init__("Builder")
        self.code_quality_rules = [
            "Use type hints",
            "Write docstrings",
            "Follow PEP8",
            "Include error handling",
        ]

    def execute(self, task: AgentTask) -> AgentResult:
        """
        Execute builder task.

        Supported task types:
        - "build_module": Create new code module template
        - "review_code": Check code quality
        - "generate_docs": Create documentation
        - "update_changelog": Add changelog entry
        - "create_diagram": Generate architecture diagram
        - "eval_report": Create evaluation report
        """
        self.log_reasoning(f"Starting builder task: {task.task_type}")

        try:
            if task.task_type == "build_module":
                result = self._build_module(task.parameters)
            elif task.task_type == "review_code":
                result = self._review_code(task.parameters)
            elif task.task_type == "generate_docs":
                result = self._generate_docs(task.parameters)
            elif task.task_type == "update_changelog":
                result = self._update_changelog(task.parameters)
            elif task.task_type == "create_diagram":
                result = self._create_diagram(task.parameters)
            elif task.task_type == "eval_report":
                result = self._create_eval_report(task.parameters)
            else:
                raise ValueError(f"Unknown task type: {task.task_type}")

            self.update_stats(success=True)
            return self.create_result(
                task_id=task.task_id,
                success=True,
                output=result,
                reasoning=f"Builder task completed: {task.task_type}",
                metrics={
                    "quality_score": result.get("quality_score", 0),
                    "items_created": result.get("items_created", 1),
                },
            )

        except Exception as e:
            self.logger.error(f"Builder task failed: {e}")
            self.update_stats(success=False)
            return self.create_result(
                task_id=task.task_id,
                success=False,
                output=None,
                reasoning=f"Builder error: {str(e)}",
                metrics={},
                errors=[str(e)],
            )

    def _build_module(self, params: Dict) -> Dict:
        """
        Generate a code module template.

        NOTE: This creates a skeleton structure, not actual implementation.
        """
        module_name = params.get("name", "new_module")
        module_type = params.get("type", "skill")

        self.log_reasoning(f"Building {module_type} template: {module_name}")

        # Generate module template
        template = f'''"""
{module_name}: [Description]

Author: Project Automata
Version: 1.0.0
"""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class {module_name.title().replace("_", "")}:
    """
    [Class description]
    """

    def __init__(self):
        """Initialize the module."""
        pass

    def execute(self, params: Dict) -> Dict:
        """
        Execute the main functionality.

        Args:
            params: Input parameters

        Returns:
            Result dictionary
        """
        raise NotImplementedError("Implement this method")


if __name__ == "__main__":
    # Module test code
    instance = {module_name.title().replace("_", "")}()
    print(f"{{instance.__class__.__name__}} initialized")
'''

        return {
            "name": module_name,
            "type": module_type,
            "template": template,
            "quality_score": 85,
            "items_created": 1,
        }

    def _review_code(self, params: Dict) -> Dict:
        """
        Review code for quality and best practices.

        NOTE: This performs basic static checks, not semantic analysis.
        """
        code = params.get("code", "")
        self.log_reasoning("Performing code review")

        review_results: List[Dict] = []
        score = 100

        for rule in self.code_quality_rules:
            passed = True
            if rule == "Use type hints" and "->" not in code and ": " not in code:
                passed = False
            elif rule == "Write docstrings" and '"""' not in code:
                passed = False
            elif rule == "Include error handling" and "try:" not in code and "except" not in code:
                passed = False

            review_results.append({"rule": rule, "passed": passed})

            if not passed:
                score -= 15

        return {
            "review_results": review_results,
            "quality_score": max(score, 0),
            "recommendations": [r["rule"] for r in review_results if not r["passed"]],
            "items_created": 0,
        }

    def _generate_docs(self, params: Dict) -> Dict:
        """
        Generate documentation from template.

        NOTE: This creates template documentation, not AI-generated content.
        """
        source = params.get("source", "module")
        doc_type = params.get("type", "markdown")

        self.log_reasoning(f"Generating {doc_type} documentation for {source}")

        documentation = f"""# {source} Documentation

## Overview

Auto-generated documentation template for {source}.

## Installation

```bash
pip install -e .
```

## Usage

```python
from {source} import main
result = main()
```

## API Reference

### Functions

#### main()

Primary entry point for the module.

**Arguments:** None

**Returns:** Dict - Result dictionary

## Examples

See the `examples/` directory for usage examples.

## Contributing

See CONTRIBUTING.md for guidelines.

---

*Documentation generated: {datetime.utcnow().isoformat()}*
"""

        return {
            "documentation": documentation,
            "doc_type": doc_type,
            "source": source,
            "quality_score": 80,
            "items_created": 1,
        }

    def _update_changelog(self, params: Dict) -> Dict:
        """Add entry to changelog."""
        version = params.get("version", "1.0.0")
        changes = params.get("changes", [])

        self.log_reasoning(f"Updating changelog for version {version}")

        added = [c for c in changes if "add" in c.lower()]
        changed = [c for c in changes if "change" in c.lower() or "update" in c.lower()]
        fixed = [c for c in changes if "fix" in c.lower()]

        changelog_entry = f"""## [{version}] - {datetime.utcnow().strftime('%Y-%m-%d')}

### Added
{chr(10).join(f'- {change}' for change in added) or '- None'}

### Changed
{chr(10).join(f'- {change}' for change in changed) or '- None'}

### Fixed
{chr(10).join(f'- {change}' for change in fixed) or '- None'}
"""

        return {
            "changelog_entry": changelog_entry,
            "version": version,
            "change_count": len(changes),
            "quality_score": 90,
            "items_created": 1,
        }

    def _create_diagram(self, params: Dict) -> Dict:
        """Generate architecture diagram in Mermaid format."""
        diagram_type = params.get("type", "architecture")

        self.log_reasoning(f"Creating {diagram_type} diagram")

        if diagram_type == "architecture":
            diagram = """```mermaid
graph TD
    A[Automata-Prime] --> B[KnowledgeAgent]
    A --> C[BuilderAgent]
    A --> D[ValidatorAgent]

    B --> E[Knowledge Base]
    C --> F[Code & Docs]
    D --> G[Validation Reports]

    subgraph Knowledge
        B
        E
    end

    subgraph Building
        C
        F
    end

    subgraph Quality
        D
        G
    end
```"""
        elif diagram_type == "workflow":
            diagram = """```mermaid
graph LR
    T[Trigger] --> P[Process]
    P --> A[Action]
    A --> O[Output]
```"""
        elif diagram_type == "simplified":
            diagram = """```mermaid
graph TD
    Prime[Automata-Prime] --> Knowledge[KnowledgeAgent]
    Prime --> Builder[BuilderAgent]
    Prime --> Validator[ValidatorAgent]
```"""
        else:
            diagram = f"Unknown diagram type: {diagram_type}"

        return {
            "diagram": diagram,
            "diagram_type": diagram_type,
            "format": "mermaid",
            "quality_score": 85,
            "items_created": 1,
        }

    def _create_eval_report(self, params: Dict) -> Dict:
        """Create cycle evaluation report."""
        cycle = params.get("cycle", 1)
        metrics = params.get("metrics", {})

        self.log_reasoning(f"Creating evaluation report for Cycle-{cycle:02d}")

        report = f"""# Project Automata: Cycle-{cycle:02d} Evaluation Report

**Date:** {datetime.utcnow().strftime('%Y-%m-%d')}
**Status:** Completed

---

## Executive Summary

Cycle-{cycle:02d} evaluation report for Project Automata.

## Metrics

| Metric | Target | Achieved | Status |
|--------|--------|----------|--------|
| Schema validity | ≥90% | {metrics.get('schema_validity', '-')}% | {'✓' if metrics.get('schema_validity', 0) >= 90 else '○'} |
| Test pass rate | ≥95% | {metrics.get('test_pass_rate', '-')}% | {'✓' if metrics.get('test_pass_rate', 0) >= 95 else '○'} |
| Documentation | 100% | {metrics.get('doc_coverage', '-')}% | {'✓' if metrics.get('doc_coverage', 0) == 100 else '○'} |

## Agent Performance

| Agent | Status |
|-------|--------|
| KnowledgeAgent | Active |
| BuilderAgent | Active |
| ValidatorAgent | Active |

---

*Report generated by: BuilderAgent*
"""

        return {
            "report": report,
            "cycle": cycle,
            "format": "markdown",
            "quality_score": 85,
            "items_created": 1,
        }


# Backwards compatibility aliases
EngineerAgent = BuilderAgent
DocumenterAgent = BuilderAgent


if __name__ == "__main__":
    agent = BuilderAgent()

    task = AgentTask(
        task_id="build_001",
        task_type="build_module",
        parameters={"name": "test_module", "type": "skill"},
    )

    result = agent.execute(task)
    print(f"Builder Result: {result.success}")
    print(f"Quality Score: {result.metrics.get('quality_score')}")
