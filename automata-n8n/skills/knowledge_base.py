"""
Knowledge Base Infrastructure

Stores and manages learned patterns, workflows, and best practices
from community sources (Reddit, YouTube, Twitter, GitHub, etc.)

Author: Project Automata - Researcher Agent
Version: 1.0.0
"""

import json
import os
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class WorkflowPattern:
    """Represents a learned workflow pattern from the community"""

    pattern_id: str
    name: str
    description: str
    source: str  # reddit, youtube, twitter, github, etc.
    source_url: str
    nodes_used: List[str]
    complexity: str  # low, medium, high
    use_cases: List[str]
    error_handling: Optional[str] = None
    best_practices: List[str] = None
    discovered_date: str = None
    popularity_score: int = 0  # upvotes, views, likes, etc.

    def __post_init__(self):
        if self.discovered_date is None:
            self.discovered_date = datetime.utcnow().isoformat()
        if self.best_practices is None:
            self.best_practices = []


@dataclass
class ErrorPattern:
    """Represents a common error and its solution"""

    error_id: str
    error_type: str
    error_message: str
    context: str
    solution: str
    source: str
    source_url: str
    nodes_affected: List[str]
    discovered_date: str = None

    def __post_init__(self):
        if self.discovered_date is None:
            self.discovered_date = datetime.utcnow().isoformat()


@dataclass
class NodeInsight:
    """Insights about a specific n8n node"""

    node_type: str
    common_use_cases: List[str]
    common_parameters: Dict
    common_errors: List[str]
    tips: List[str]
    source_count: int = 0


class KnowledgeBase:
    """
    Central knowledge repository for Project Automata.

    Stores and manages:
    - Workflow patterns from community
    - Common errors and solutions
    - Node usage insights
    - Best practices
    """

    def __init__(self, base_dir: str = None):
        """Initialize knowledge base"""
        if base_dir is None:
            base_dir = os.path.join(os.path.dirname(__file__), "..", "knowledge_base")

        self.base_dir = base_dir
        self.patterns_file = os.path.join(base_dir, "workflow_patterns.json")
        self.errors_file = os.path.join(base_dir, "error_patterns.json")
        self.nodes_file = os.path.join(base_dir, "node_insights.json")
        self.meta_file = os.path.join(base_dir, "metadata.json")

        # In-memory storage
        self.workflow_patterns: Dict[str, WorkflowPattern] = {}
        self.error_patterns: Dict[str, ErrorPattern] = {}
        self.node_insights: Dict[str, NodeInsight] = {}
        self.metadata = {
            "created_at": datetime.utcnow().isoformat(),
            "last_updated": datetime.utcnow().isoformat(),
            "total_patterns": 0,
            "total_errors": 0,
            "sources": defaultdict(int),
        }

        # Create directory and load existing data
        os.makedirs(base_dir, exist_ok=True)
        self.load()

    def add_workflow_pattern(self, pattern: WorkflowPattern) -> None:
        """Add a new workflow pattern to the knowledge base"""
        self.workflow_patterns[pattern.pattern_id] = pattern
        self.metadata["total_patterns"] = len(self.workflow_patterns)
        self.metadata["sources"][pattern.source] += 1
        self.metadata["last_updated"] = datetime.utcnow().isoformat()

    def add_error_pattern(self, error: ErrorPattern) -> None:
        """Add a new error pattern to the knowledge base"""
        self.error_patterns[error.error_id] = error
        self.metadata["total_errors"] = len(self.error_patterns)
        self.metadata["sources"][error.source] += 1
        self.metadata["last_updated"] = datetime.utcnow().isoformat()

    def add_node_insight(self, node_type: str, insight: NodeInsight) -> None:
        """Add or update node insights"""
        if node_type in self.node_insights:
            # Merge insights
            existing = self.node_insights[node_type]
            existing.common_use_cases.extend(insight.common_use_cases)
            existing.tips.extend(insight.tips)
            existing.source_count += 1
        else:
            self.node_insights[node_type] = insight

        self.metadata["last_updated"] = datetime.utcnow().isoformat()

    def search_patterns(
        self, query: str = None, source: str = None, complexity: str = None
    ) -> List[WorkflowPattern]:
        """Search workflow patterns by criteria"""
        results = list(self.workflow_patterns.values())

        if query:
            query_lower = query.lower()
            results = [
                p
                for p in results
                if query_lower in p.name.lower()
                or query_lower in p.description.lower()
                or any(query_lower in uc.lower() for uc in p.use_cases)
            ]

        if source:
            results = [p for p in results if p.source == source]

        if complexity:
            results = [p for p in results if p.complexity == complexity]

        # Sort by popularity
        results.sort(key=lambda p: p.popularity_score, reverse=True)
        return results

    def get_top_patterns(self, n: int = 10) -> List[WorkflowPattern]:
        """Get top N most popular patterns"""
        all_patterns = list(self.workflow_patterns.values())
        all_patterns.sort(key=lambda p: p.popularity_score, reverse=True)
        return all_patterns[:n]

    def get_errors_for_node(self, node_type: str) -> List[ErrorPattern]:
        """Get all known errors for a specific node type"""
        return [e for e in self.error_patterns.values() if node_type in e.nodes_affected]

    def get_node_insights(self, node_type: str) -> Optional[NodeInsight]:
        """Get insights for a specific node"""
        return self.node_insights.get(node_type)

    def save(self) -> None:
        """Save knowledge base to disk"""
        # Save patterns
        with open(self.patterns_file, "w") as f:
            patterns_dict = {k: asdict(v) for k, v in self.workflow_patterns.items()}
            json.dump(patterns_dict, f, indent=2)

        # Save errors
        with open(self.errors_file, "w") as f:
            errors_dict = {k: asdict(v) for k, v in self.error_patterns.items()}
            json.dump(errors_dict, f, indent=2)

        # Save node insights
        with open(self.nodes_file, "w") as f:
            nodes_dict = {k: asdict(v) for k, v in self.node_insights.items()}
            json.dump(nodes_dict, f, indent=2)

        # Save metadata
        with open(self.meta_file, "w") as f:
            json.dump(dict(self.metadata), f, indent=2)

    def load(self) -> None:
        """Load knowledge base from disk"""
        # Load patterns
        if os.path.exists(self.patterns_file):
            with open(self.patterns_file, "r") as f:
                patterns_dict = json.load(f)
                self.workflow_patterns = {k: WorkflowPattern(**v) for k, v in patterns_dict.items()}

        # Load errors
        if os.path.exists(self.errors_file):
            with open(self.errors_file, "r") as f:
                errors_dict = json.load(f)
                self.error_patterns = {k: ErrorPattern(**v) for k, v in errors_dict.items()}

        # Load node insights
        if os.path.exists(self.nodes_file):
            with open(self.nodes_file, "r") as f:
                nodes_dict = json.load(f)
                self.node_insights = {k: NodeInsight(**v) for k, v in nodes_dict.items()}

        # Load metadata
        if os.path.exists(self.meta_file):
            with open(self.meta_file, "r") as f:
                self.metadata = json.load(f)

    def get_statistics(self) -> Dict:
        """Get knowledge base statistics"""
        return {
            "total_workflow_patterns": len(self.workflow_patterns),
            "total_error_patterns": len(self.error_patterns),
            "total_node_insights": len(self.node_insights),
            "sources": dict(self.metadata["sources"]),
            "last_updated": self.metadata["last_updated"],
            "top_nodes": self._get_most_common_nodes(5),
            "complexity_distribution": self._get_complexity_distribution(),
        }

    def _get_most_common_nodes(self, n: int) -> List[tuple]:
        """Get most commonly used nodes"""
        node_counts = defaultdict(int)
        for pattern in self.workflow_patterns.values():
            for node in pattern.nodes_used:
                node_counts[node] += 1

        sorted_nodes = sorted(node_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_nodes[:n]

    def _get_complexity_distribution(self) -> Dict:
        """Get distribution of workflow complexity"""
        distribution = defaultdict(int)
        for pattern in self.workflow_patterns.values():
            distribution[pattern.complexity] += 1
        return dict(distribution)

    def export_summary(self) -> str:
        """Export a markdown summary of the knowledge base"""
        stats = self.get_statistics()

        summary = f"""# Knowledge Base Summary

**Last Updated:** {stats['last_updated']}

## Statistics

- **Total Workflow Patterns:** {stats['total_workflow_patterns']}
- **Total Error Patterns:** {stats['total_error_patterns']}
- **Total Node Insights:** {stats['total_node_insights']}

## Sources

{self._format_sources(stats['sources'])}

## Top Nodes

{self._format_top_nodes(stats['top_nodes'])}

## Complexity Distribution

{self._format_complexity(stats['complexity_distribution'])}

## Top Patterns

{self._format_top_patterns()}
"""
        return summary

    def _format_sources(self, sources: Dict) -> str:
        """Format sources for markdown"""
        lines = []
        for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"- **{source.capitalize()}:** {count} patterns")
        return "\n".join(lines) if lines else "- No sources yet"

    def _format_top_nodes(self, top_nodes: List[tuple]) -> str:
        """Format top nodes for markdown"""
        lines = []
        for i, (node, count) in enumerate(top_nodes, 1):
            lines.append(f"{i}. {node}: {count} uses")
        return "\n".join(lines) if lines else "- No nodes yet"

    def _format_complexity(self, distribution: Dict) -> str:
        """Format complexity distribution for markdown"""
        lines = []
        for complexity in ["low", "medium", "high"]:
            count = distribution.get(complexity, 0)
            lines.append(f"- **{complexity.capitalize()}:** {count}")
        return "\n".join(lines)

    def _format_top_patterns(self, n: int = 5) -> str:
        """Format top patterns for markdown"""
        top = self.get_top_patterns(n)
        lines = []
        for i, pattern in enumerate(top, 1):
            lines.append(f"{i}. **{pattern.name}** ({pattern.source})")
            lines.append(f"   - {pattern.description}")
            lines.append(f"   - Popularity: {pattern.popularity_score}")
            lines.append("")
        return "\n".join(lines) if lines else "- No patterns yet"


if __name__ == "__main__":
    # Example usage
    kb = KnowledgeBase()
    print("Knowledge Base initialized")
    print(f"Location: {kb.base_dir}")
    print(kb.export_summary())
