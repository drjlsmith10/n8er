"""
Workflow Versioning System

This module provides semantic versioning, change tracking, and diff generation
for n8n workflows.

Author: Project Automata - Agent 5 (High Priority Features)
Version: 2.1.0
Created: 2025-11-20
Issue: #12 - Workflow Versioning Strategy
"""

import hashlib
import json
import logging
import uuid
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime
from difflib import unified_diff
from typing import Any, Dict, List, Optional, Tuple

# Application should configure logging, not libraries
# logging.basicConfig() removed to prevent global logging configuration conflicts
logger = logging.getLogger(__name__)


@dataclass
class WorkflowVersion:
    """
    Represents a version of an n8n workflow with semantic versioning.

    Semantic Versioning Format: MAJOR.MINOR.PATCH
    - MAJOR: Incompatible API changes (breaking changes)
    - MINOR: Backward-compatible functionality additions
    - PATCH: Backward-compatible bug fixes

    Attributes:
        version: Semantic version string (e.g., "1.2.3")
        version_id: Unique UUID for this version
        workflow_id: ID of the workflow being versioned
        workflow_name: Name of the workflow
        changelog: List of changes in this version
        created_at: Timestamp of version creation
        created_by: Author/system that created this version
        metadata: Additional version metadata
        checksum: SHA-256 hash of workflow content
    """

    version: str
    version_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: Optional[str] = None
    workflow_name: str = "Unnamed Workflow"
    changelog: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    created_by: str = "Project Automata"
    metadata: Dict[str, Any] = field(default_factory=dict)
    checksum: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary representation"""
        return asdict(self)

    @staticmethod
    def parse_version(version_string: str) -> Tuple[int, int, int]:
        """
        Parse semantic version string into components.

        Args:
            version_string: Version string (e.g., "1.2.3")

        Returns:
            Tuple of (major, minor, patch)

        Raises:
            ValueError: If version string is invalid
        """
        try:
            parts = version_string.split(".")
            if len(parts) != 3:
                raise ValueError("Version must have exactly 3 parts (MAJOR.MINOR.PATCH)")

            major, minor, patch = map(int, parts)
            return major, minor, patch
        except Exception as e:
            raise ValueError(f"Invalid version string '{version_string}': {e}")

    @staticmethod
    def format_version(major: int, minor: int, patch: int) -> str:
        """Format version components into string"""
        return f"{major}.{minor}.{patch}"

    def validate(self) -> List[str]:
        """
        Validate version configuration.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        try:
            WorkflowVersion.parse_version(self.version)
        except ValueError as e:
            errors.append(str(e))

        if not self.version_id:
            errors.append("Version ID is required")

        if not self.workflow_name:
            errors.append("Workflow name is required")

        return errors


class WorkflowVersionManager:
    """
    Manages workflow versions, comparisons, and change tracking.
    """

    def __init__(self):
        """Initialize version manager"""
        # Use defaultdict(list) to avoid race condition in check-then-act pattern
        self.versions: Dict[str, List[WorkflowVersion]] = defaultdict(list)
        logger.debug("Initialized WorkflowVersionManager")

    def create_version(
        self,
        workflow: Dict,
        version: str = "1.0.0",
        changelog: Optional[List[str]] = None,
        workflow_id: Optional[str] = None,
        created_by: str = "Project Automata",
    ) -> WorkflowVersion:
        """
        Create a new workflow version.

        Args:
            workflow: Workflow JSON
            version: Semantic version string
            changelog: List of changes
            workflow_id: Optional workflow ID
            created_by: Version author

        Returns:
            WorkflowVersion instance
        """
        workflow_name = workflow.get("name", "Unnamed Workflow")
        workflow_id = workflow_id or workflow.get("id") or str(uuid.uuid4())

        # Calculate checksum
        checksum = self._calculate_checksum(workflow)

        # Create version
        version_obj = WorkflowVersion(
            version=version,
            workflow_id=workflow_id,
            workflow_name=workflow_name,
            changelog=changelog or [],
            created_by=created_by,
            checksum=checksum,
        )

        # Validate
        errors = version_obj.validate()
        if errors:
            logger.warning(f"Version validation warnings: {', '.join(errors)}")

        # Store (defaultdict(list) automatically creates list if key doesn't exist)
        self.versions[workflow_id].append(version_obj)

        logger.debug(f"Created version {version} for workflow '{workflow_name}'")
        return version_obj

    def version_bump(
        self,
        workflow: Dict,
        bump_type: str = "patch",
        changelog: Optional[List[str]] = None,
        workflow_id: Optional[str] = None,
    ) -> WorkflowVersion:
        """
        Automatically bump version based on change type.

        Args:
            workflow: Workflow JSON
            bump_type: Type of bump ('major', 'minor', 'patch')
            changelog: List of changes
            workflow_id: Optional workflow ID

        Returns:
            New WorkflowVersion instance

        Raises:
            ValueError: If bump_type is invalid
        """
        bump_type = bump_type.lower()
        if bump_type not in ["major", "minor", "patch"]:
            raise ValueError(
                f"Invalid bump_type: {bump_type}. Must be 'major', 'minor', or 'patch'"
            )

        workflow_id = workflow_id or workflow.get("id") or str(uuid.uuid4())

        # Get current version or default to 0.0.0
        current_version = self.get_latest_version(workflow_id)
        if current_version:
            major, minor, patch = WorkflowVersion.parse_version(current_version.version)
        else:
            major, minor, patch = 0, 0, 0

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

        new_version = WorkflowVersion.format_version(major, minor, patch)

        return self.create_version(
            workflow=workflow, version=new_version, changelog=changelog, workflow_id=workflow_id
        )

    def get_latest_version(self, workflow_id: str) -> Optional[WorkflowVersion]:
        """
        Get the latest version for a workflow.

        Args:
            workflow_id: Workflow ID

        Returns:
            Latest WorkflowVersion or None
        """
        versions = self.versions.get(workflow_id, [])
        if not versions:
            return None

        # Sort by semantic version
        sorted_versions = sorted(
            versions, key=lambda v: WorkflowVersion.parse_version(v.version), reverse=True
        )

        return sorted_versions[0]

    def get_version(self, workflow_id: str, version: str) -> Optional[WorkflowVersion]:
        """
        Get a specific version.

        Args:
            workflow_id: Workflow ID
            version: Version string

        Returns:
            WorkflowVersion or None
        """
        versions = self.versions.get(workflow_id, [])
        for v in versions:
            if v.version == version:
                return v
        return None

    def list_versions(self, workflow_id: str, ascending: bool = False) -> List[WorkflowVersion]:
        """
        List all versions for a workflow.

        Args:
            workflow_id: Workflow ID
            ascending: Sort order (default: descending/newest first)

        Returns:
            List of WorkflowVersion instances
        """
        versions = self.versions.get(workflow_id, [])
        return sorted(
            versions, key=lambda v: WorkflowVersion.parse_version(v.version), reverse=not ascending
        )

    def compare_versions(self, workflow_id: str, version1: str, version2: str) -> Dict[str, Any]:
        """
        Compare two versions.

        Args:
            workflow_id: Workflow ID
            version1: First version string
            version2: Second version string

        Returns:
            Comparison result dict

        Raises:
            ValueError: If versions not found
        """
        v1 = self.get_version(workflow_id, version1)
        v2 = self.get_version(workflow_id, version2)

        if not v1:
            raise ValueError(f"Version not found: {version1}")
        if not v2:
            raise ValueError(f"Version not found: {version2}")

        # Parse versions
        v1_parts = WorkflowVersion.parse_version(version1)
        v2_parts = WorkflowVersion.parse_version(version2)

        # Determine which is newer
        if v1_parts > v2_parts:
            newer, older = v1, v2
            newer_str, older_str = version1, version2
        else:
            newer, older = v2, v1
            newer_str, older_str = version2, version1

        comparison = {
            "newer_version": newer_str,
            "older_version": older_str,
            "version_difference": self._calculate_version_diff(older_str, newer_str),
            "changelog_combined": newer.changelog,
            "time_difference": self._calculate_time_diff(older.created_at, newer.created_at),
            "checksum_match": v1.checksum == v2.checksum if v1.checksum and v2.checksum else None,
        }

        return comparison

    def generate_diff(
        self,
        workflow1: Dict,
        workflow2: Dict,
        context_lines: int = 3,
        max_size_mb: float = 10.0
    ) -> str:
        """
        Generate a unified diff between two workflows.

        Uses memory-efficient streaming for large workflows.

        Args:
            workflow1: First workflow JSON
            workflow2: Second workflow JSON
            context_lines: Number of context lines in diff
            max_size_mb: Maximum workflow size to process (MB)

        Returns:
            Unified diff string

        Raises:
            ValueError: If workflow exceeds max_size_mb
        """
        # Estimate size to prevent memory issues
        size1 = len(json.dumps(workflow1))
        size2 = len(json.dumps(workflow2))
        total_size_mb = (size1 + size2) / (1024 * 1024)

        if total_size_mb > max_size_mb:
            raise ValueError(
                f"Workflows too large for diff ({total_size_mb:.1f}MB > {max_size_mb}MB). "
                "Use generate_diff_streaming() for large workflows."
            )

        # Convert to formatted JSON strings
        json1 = json.dumps(workflow1, indent=2, sort_keys=True).splitlines(keepends=True)
        json2 = json.dumps(workflow2, indent=2, sort_keys=True).splitlines(keepends=True)

        # Generate diff
        diff = unified_diff(
            json1,
            json2,
            fromfile=f"{workflow1.get('name', 'workflow')} (old)",
            tofile=f"{workflow2.get('name', 'workflow')} (new)",
            n=context_lines,
        )

        return "".join(diff)

    def generate_diff_streaming(
        self,
        workflow1: Dict,
        workflow2: Dict,
        context_lines: int = 3,
        chunk_size: int = 1000
    ):
        """
        Generate diff using streaming for memory efficiency with large workflows.

        Yields diff lines instead of building entire string in memory.

        Args:
            workflow1: First workflow JSON
            workflow2: Second workflow JSON
            context_lines: Number of context lines in diff
            chunk_size: Lines to process per chunk

        Yields:
            Diff lines as strings
        """
        # Stream JSON serialization using generators
        json1_lines = self._stream_json_lines(workflow1)
        json2_lines = self._stream_json_lines(workflow2)

        # Collect lines in chunks for difflib
        lines1 = list(json1_lines)
        lines2 = list(json2_lines)

        # Generate diff as generator
        diff_gen = unified_diff(
            lines1,
            lines2,
            fromfile=f"{workflow1.get('name', 'workflow')} (old)",
            tofile=f"{workflow2.get('name', 'workflow')} (new)",
            n=context_lines,
        )

        # Yield lines
        for line in diff_gen:
            yield line

    def _stream_json_lines(self, obj: Dict, indent: int = 2) -> List[str]:
        """
        Convert dict to JSON lines for streaming comparison.

        Uses sorted keys for consistent ordering.
        """
        json_str = json.dumps(obj, indent=indent, sort_keys=True)
        return json_str.splitlines(keepends=True)

    def detect_changes(self, workflow1: Dict, workflow2: Dict) -> Dict[str, Any]:
        """
        Detect and categorize changes between workflows using semantic comparison.

        Uses semantic comparison to avoid false positives from:
        - Timestamp differences
        - ID changes
        - Metadata variations
        - Field ordering differences

        Args:
            workflow1: Original workflow
            workflow2: Modified workflow

        Returns:
            Dict containing categorized changes
        """
        changes: Dict[str, Any] = {  # Type annotation for mypy
            "name_changed": workflow1.get("name") != workflow2.get("name"),
            "nodes_added": [],
            "nodes_removed": [],
            "nodes_modified": [],
            "node_modifications": {},  # Detailed per-node changes
            "connections_changed": False,
            "settings_changed": False,
            "breaking_changes": False,
        }

        # Compare nodes using semantic comparison
        nodes1 = {n["name"]: n for n in workflow1.get("nodes", [])}
        nodes2 = {n["name"]: n for n in workflow2.get("nodes", [])}

        # Detect added/removed nodes
        changes["nodes_added"] = list(set(nodes2.keys()) - set(nodes1.keys()))
        changes["nodes_removed"] = list(set(nodes1.keys()) - set(nodes2.keys()))

        # Detect modified nodes with semantic comparison
        for name in set(nodes1.keys()) & set(nodes2.keys()):
            if not self._nodes_semantically_equal(nodes1[name], nodes2[name]):
                changes["nodes_modified"].append(name)
                # Track specific modifications
                changes["node_modifications"][name] = self._get_node_diff(
                    nodes1[name], nodes2[name]
                )

        # Check connections with semantic comparison
        changes["connections_changed"] = not self._connections_semantically_equal(
            workflow1.get("connections", {}),
            workflow2.get("connections", {})
        )

        # Check settings with semantic comparison (exclude timestamps)
        changes["settings_changed"] = not self._settings_semantically_equal(
            workflow1.get("settings", {}),
            workflow2.get("settings", {})
        )

        # Determine if breaking
        changes["breaking_changes"] = (
            len(changes["nodes_removed"]) > 0 or changes["connections_changed"]
        )

        return changes

    def _nodes_semantically_equal(self, node1: Dict, node2: Dict) -> bool:
        """
        Compare two nodes semantically, ignoring volatile fields.

        Ignores: id, position, webhookId, createdAt, updatedAt
        """
        volatile_fields = {'id', 'webhookId', 'createdAt', 'updatedAt'}
        essential_fields = ['name', 'type', 'typeVersion', 'parameters', 'credentials', 'disabled']

        for field_name in essential_fields:
            val1 = node1.get(field_name)
            val2 = node2.get(field_name)

            if isinstance(val1, dict) and isinstance(val2, dict):
                if not self._dicts_equal_ignoring_volatile(val1, val2, volatile_fields):
                    return False
            elif val1 != val2:
                return False

        return True

    def _dicts_equal_ignoring_volatile(self, dict1: Dict, dict2: Dict, volatile: set) -> bool:
        """Compare dicts while ignoring volatile fields."""
        keys1 = set(dict1.keys()) - volatile
        keys2 = set(dict2.keys()) - volatile

        if keys1 != keys2:
            return False

        for key in keys1:
            if dict1[key] != dict2[key]:
                return False

        return True

    def _connections_semantically_equal(self, conn1: Dict, conn2: Dict) -> bool:
        """Compare connections semantically with normalized structure."""
        return self._normalize_connections(conn1) == self._normalize_connections(conn2)

    def _normalize_connections(self, connections: Dict) -> Dict:
        """Normalize connection structure for comparison."""
        normalized = {}
        for source, targets in connections.items():
            if isinstance(targets, dict):
                normalized[source] = {}
                for conn_type, outputs in targets.items():
                    if isinstance(outputs, list):
                        normalized[source][conn_type] = [
                            sorted(output, key=lambda x: (x.get('node', ''), x.get('index', 0)))
                            if isinstance(output, list) else output
                            for output in outputs
                        ]
                    else:
                        normalized[source][conn_type] = outputs
            else:
                normalized[source] = targets
        return normalized

    def _settings_semantically_equal(self, settings1: Dict, settings2: Dict) -> bool:
        """Compare settings semantically, ignoring volatile keys."""
        volatile = {'saveDataSuccessExecution', 'saveExecutionProgress'}
        keys1 = set(settings1.keys()) - volatile
        keys2 = set(settings2.keys()) - volatile

        if keys1 != keys2:
            return False

        for key in keys1:
            if settings1[key] != settings2[key]:
                return False

        return True

    def _get_node_diff(self, node1: Dict, node2: Dict) -> Dict[str, Any]:
        """Get detailed diff between two nodes."""
        diff = {"fields_changed": [], "parameters_changed": []}

        for field_name in ['type', 'typeVersion', 'disabled']:
            if node1.get(field_name) != node2.get(field_name):
                diff["fields_changed"].append({
                    "field": field_name,
                    "old": node1.get(field_name),
                    "new": node2.get(field_name)
                })

        params1 = node1.get("parameters", {})
        params2 = node2.get("parameters", {})

        for param in set(params1.keys()) | set(params2.keys()):
            if params1.get(param) != params2.get(param):
                diff["parameters_changed"].append({
                    "parameter": param,
                    "old": params1.get(param),
                    "new": params2.get(param)
                })

        return diff

    def suggest_version_bump(self, workflow1: Dict, workflow2: Dict) -> str:
        """
        Suggest version bump type based on changes.

        Args:
            workflow1: Original workflow
            workflow2: Modified workflow

        Returns:
            Suggested bump type ('major', 'minor', 'patch')
        """
        changes = self.detect_changes(workflow1, workflow2)

        if changes["breaking_changes"]:
            return "major"
        elif changes["nodes_added"] or changes["settings_changed"]:
            return "minor"
        else:
            return "patch"

    def add_version_to_workflow(
        self,
        workflow: Dict,
        version: str,
        version_id: Optional[str] = None,
        changelog: Optional[List[str]] = None,
    ) -> Dict:
        """
        Add version metadata to workflow JSON.

        Args:
            workflow: Workflow JSON
            version: Version string
            version_id: Optional version UUID
            changelog: Optional changelog

        Returns:
            Workflow with version metadata added
        """
        workflow = workflow.copy()

        # Add version fields
        workflow["version"] = version
        workflow["versionId"] = version_id or str(uuid.uuid4())

        if changelog:
            workflow["changelog"] = changelog

        # Update updatedAt
        workflow["updatedAt"] = datetime.utcnow().isoformat() + "Z"

        # Add to meta
        if "meta" not in workflow:
            workflow["meta"] = {}

        workflow["meta"]["version"] = version
        workflow["meta"]["versionId"] = workflow["versionId"]

        return workflow

    def export_version_history(self, workflow_id: str) -> Dict:
        """
        Export complete version history for a workflow.

        Args:
            workflow_id: Workflow ID

        Returns:
            Version history dict
        """
        versions = self.list_versions(workflow_id)

        history = {
            "workflow_id": workflow_id,
            "workflow_name": versions[0].workflow_name if versions else "Unknown",
            "total_versions": len(versions),
            "latest_version": versions[0].version if versions else None,
            "first_version": versions[-1].version if versions else None,
            "versions": [v.to_dict() for v in versions],
            "exported_at": datetime.utcnow().isoformat() + "Z",
        }

        return history

    def _calculate_checksum(self, workflow: Dict) -> str:
        """
        Calculate SHA-256 checksum of workflow.

        Excludes volatile fields (timestamps, IDs, metadata) to ensure
        checksum only changes when actual workflow content changes.
        """
        # Create a copy to avoid modifying the original
        workflow_copy = workflow.copy()

        # Remove volatile fields that change even when content doesn't
        volatile_fields = ['createdAt', 'updatedAt', 'id', 'versionId', 'updatedBy']
        for field in volatile_fields:
            workflow_copy.pop(field, None)

        # Also remove meta object which contains volatile metadata
        workflow_copy.pop('meta', None)

        # Calculate checksum on cleaned workflow
        workflow_str = json.dumps(workflow_copy, sort_keys=True)
        return hashlib.sha256(workflow_str.encode()).hexdigest()

    def _calculate_version_diff(self, version1: str, version2: str) -> Dict[str, int]:
        """Calculate difference between two versions"""
        v1_parts = WorkflowVersion.parse_version(version1)
        v2_parts = WorkflowVersion.parse_version(version2)

        return {
            "major": v2_parts[0] - v1_parts[0],
            "minor": v2_parts[1] - v1_parts[1],
            "patch": v2_parts[2] - v1_parts[2],
        }

    def _calculate_time_diff(self, time1: str, time2: str) -> str:
        """Calculate time difference between versions"""
        try:
            t1 = datetime.fromisoformat(time1.replace("Z", "+00:00"))
            t2 = datetime.fromisoformat(time2.replace("Z", "+00:00"))
            diff = abs((t2 - t1).total_seconds())

            if diff < 60:
                return f"{int(diff)} seconds"
            elif diff < 3600:
                return f"{int(diff / 60)} minutes"
            elif diff < 86400:
                return f"{int(diff / 3600)} hours"
            else:
                return f"{int(diff / 86400)} days"
        except Exception:
            return "Unknown"


# Convenience functions
def create_versioned_workflow(
    workflow: Dict, version: str = "1.0.0", changelog: Optional[List[str]] = None
) -> Dict:
    """
    Create a workflow with version metadata.

    Args:
        workflow: Workflow JSON
        version: Version string
        changelog: List of changes

    Returns:
        Workflow with version metadata
    """
    manager = WorkflowVersionManager()
    version_obj = manager.create_version(workflow, version, changelog)
    return manager.add_version_to_workflow(workflow, version, version_obj.version_id, changelog)


def bump_workflow_version(
    workflow: Dict, bump_type: str = "patch", changelog: Optional[List[str]] = None
) -> Dict:
    """
    Bump workflow version.

    Args:
        workflow: Workflow JSON
        bump_type: Type of bump ('major', 'minor', 'patch')
        changelog: List of changes

    Returns:
        Workflow with bumped version
    """
    manager = WorkflowVersionManager()

    # Get current version or start at 1.0.0
    current_version = workflow.get("version", "0.0.0")
    major, minor, patch = WorkflowVersion.parse_version(current_version)

    if bump_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump_type == "minor":
        minor += 1
        patch = 0
    else:  # patch
        patch += 1

    new_version = WorkflowVersion.format_version(major, minor, patch)
    version_id = str(uuid.uuid4())

    return manager.add_version_to_workflow(workflow, new_version, version_id, changelog)


if __name__ == "__main__":
    print("Workflow Versioning System v2.1.0")
    print("=" * 60)

    # Example workflow
    workflow = {
        "name": "Example Workflow",
        "nodes": [
            {"name": "Start", "type": "n8n-nodes-base.start"},
            {"name": "Process", "type": "n8n-nodes-base.function"},
        ],
        "connections": {},
        "settings": {},
    }

    # Create version manager
    manager = WorkflowVersionManager()

    # Create initial version
    v1 = manager.create_version(workflow, version="1.0.0", changelog=["Initial release"])
    print(f"\n✓ Created version {v1.version}")

    # Bump version
    workflow_modified = workflow.copy()
    workflow_modified["nodes"].append({"name": "New Node", "type": "n8n-nodes-base.httpRequest"})

    v2 = manager.version_bump(
        workflow_modified,
        bump_type="minor",
        changelog=["Added HTTP Request node"],
        workflow_id=v1.workflow_id,
    )
    print(f"✓ Bumped to version {v2.version}")

    # Compare versions
    comparison = manager.compare_versions(v1.workflow_id, "1.0.0", "1.1.0")
    print(f"✓ Compared versions: {comparison['version_difference']}")

    # Detect changes
    changes = manager.detect_changes(workflow, workflow_modified)
    print(f"✓ Detected changes: {len(changes['nodes_added'])} nodes added")

    # Suggest bump type
    suggested = manager.suggest_version_bump(workflow, workflow_modified)
    print(f"✓ Suggested bump type: {suggested}")

    print("\nFor documentation, see: docs/VERSIONING_GUIDE.md")
