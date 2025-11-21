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
import threading
import os
import uuid
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime
from difflib import unified_diff
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Import pydantic validation schemas
try:
    from validation_schemas import validate_version, VersionInput
    VALIDATION_AVAILABLE = True
except ImportError:
    VALIDATION_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
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

    def to_dict(self) -> Dict[str, Any]:
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

    Thread Safety:
        This class is thread-safe. All public methods that modify state are protected
        by an internal lock. The create_version() method uses pessimistic locking to
        prevent duplicate versions from being created concurrently.

    Note:
        @thread_safe - All public methods are protected by internal RLock
    """

    def __init__(self):
        """Initialize version manager with thread-safe state management"""
        # Use defaultdict(list) to avoid race condition in check-then-act pattern
        self.versions: Dict[str, List[WorkflowVersion]] = defaultdict(list)

        # Thread safety: RLock allows same thread to acquire lock multiple times
        # This is needed because some methods call other methods that also acquire the lock
        self._lock = threading.RLock()

        # Pessimistic locking: Per-workflow locks for version creation
        # Use RLock to allow same thread to acquire lock multiple times (e.g., version_bump calls create_version)
        # This prevents duplicate versions from being created concurrently
        self._version_locks: Dict[str, threading.RLock] = {}
        self._version_locks_lock = threading.Lock()  # Lock for the locks dictionary

        logger.debug("Initialized WorkflowVersionManager with thread safety")

    def _get_workflow_lock(self, workflow_id: str) -> threading.RLock:
        """
        Get or create a lock for a specific workflow.

        This implements pessimistic locking at the workflow level to prevent
        concurrent version creation for the same workflow.

        Uses RLock to allow the same thread to acquire the lock multiple times,
        which is necessary when version_bump calls create_version.

        Args:
            workflow_id: Workflow ID

        Returns:
            RLock for this workflow
        """
        with self._version_locks_lock:
            if workflow_id not in self._version_locks:
                self._version_locks[workflow_id] = threading.RLock()
            return self._version_locks[workflow_id]

    def create_version(
        self,
        workflow: Dict[str, Any],
        version: str = "1.0.0",
        changelog: Optional[List[str]] = None,
        workflow_id: Optional[str] = None,
        created_by: str = "Project Automata",
        lock_timeout: float = 5.0,
    ) -> WorkflowVersion:
        """
        Create a new workflow version with pessimistic locking.

        This method uses pessimistic locking to prevent duplicate versions from being
        created concurrently. A per-workflow lock is acquired before version creation,
        ensuring that only one thread can create a version for a specific workflow at a time.

        Thread Safety:
            @thread_safe - Uses pessimistic locking with timeout to prevent race conditions

        Args:
            workflow: Workflow JSON
            version: Semantic version string
            changelog: List of changes
            workflow_id: Optional workflow ID
            created_by: Version author
            lock_timeout: Maximum time to wait for lock (default: 5 seconds)

        Returns:
            WorkflowVersion instance

        Raises:
            TimeoutError: If lock cannot be acquired within timeout period
        """
        workflow_name = workflow.get("name", "Unnamed Workflow")
        workflow_id = workflow_id or workflow.get("id") or str(uuid.uuid4())

        # PESSIMISTIC LOCKING: Acquire workflow-specific lock before creating version
        # This prevents duplicate versions from being created concurrently
        workflow_lock = self._get_workflow_lock(workflow_id)

        if not workflow_lock.acquire(timeout=lock_timeout):
            raise TimeoutError(
                f"Could not acquire version lock for workflow {workflow_id} within {lock_timeout}s. "
                "Another thread may be creating a version for this workflow."
            )

        try:
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

            # Store version - Protected by workflow lock
            with self._lock:
                self.versions[workflow_id].append(version_obj)

            logger.debug(f"Created version {version} for workflow '{workflow_name}'")
            return version_obj

        finally:
            # CRITICAL: Always release lock, even if an exception occurs
            workflow_lock.release()

    def version_bump(
        self,
        workflow: Dict[str, Any],
        bump_type: str = "patch",
        changelog: Optional[List[str]] = None,
        workflow_id: Optional[str] = None,
        lock_timeout: float = 5.0,
    ) -> WorkflowVersion:
        """
        Automatically bump version based on change type.

        This method is protected against TOCTOU (Time-Of-Check-Time-Of-Use) race conditions
        by acquiring the workflow lock before reading the current version and creating the new one.

        Thread Safety:
            @thread_safe - Protected by pessimistic locking to prevent TOCTOU

        Args:
            workflow: Workflow JSON
            bump_type: Type of bump ('major', 'minor', 'patch')
            changelog: List of changes
            workflow_id: Optional workflow ID
            lock_timeout: Maximum time to wait for lock (default: 5 seconds)

        Returns:
            New WorkflowVersion instance

        Raises:
            ValueError: If bump_type is invalid
            TimeoutError: If lock cannot be acquired within timeout period
        """
        bump_type = bump_type.lower()
        if bump_type not in ["major", "minor", "patch"]:
            raise ValueError(
                f"Invalid bump_type: {bump_type}. Must be 'major', 'minor', or 'patch'"
            )

        workflow_id = workflow_id or workflow.get("id") or str(uuid.uuid4())

        # PESSIMISTIC LOCKING: Acquire workflow lock to prevent TOCTOU race condition
        # This ensures that the check (get_latest_version) and act (create_version)
        # operations are atomic with respect to other threads
        workflow_lock = self._get_workflow_lock(workflow_id)

        if not workflow_lock.acquire(timeout=lock_timeout):
            raise TimeoutError(
                f"Could not acquire version lock for workflow {workflow_id} within {lock_timeout}s"
            )

        try:
            # Get current version or default to 0.0.0
            # Protected by lock - no other thread can create a version concurrently
            with self._lock:
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

            # Create version - lock is already held, so we pass it through
            # Note: create_version will try to acquire the same lock, but we use RLock
            # so the same thread can acquire it multiple times
            return self.create_version(
                workflow=workflow,
                version=new_version,
                changelog=changelog,
                workflow_id=workflow_id,
                lock_timeout=lock_timeout,
            )

        finally:
            # CRITICAL: Always release lock
            workflow_lock.release()

    def get_latest_version(self, workflow_id: str) -> Optional[WorkflowVersion]:
        """
        Get the latest version for a workflow.

        Thread Safety:
            @thread_safe - Protected by internal lock

        Args:
            workflow_id: Workflow ID

        Returns:
            Latest WorkflowVersion or None
        """
        with self._lock:
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

        Thread Safety:
            @thread_safe - Protected by internal lock

        Args:
            workflow_id: Workflow ID
            version: Version string

        Returns:
            WorkflowVersion or None
        """
        with self._lock:
            versions = self.versions.get(workflow_id, [])
            for v in versions:
                if v.version == version:
                    return v
            return None

    def list_versions(self, workflow_id: str, ascending: bool = False) -> List[WorkflowVersion]:
        """
        List all versions for a workflow.

        Thread Safety:
            @thread_safe - Protected by internal lock

        Args:
            workflow_id: Workflow ID
            ascending: Sort order (default: descending/newest first)

        Returns:
            List of WorkflowVersion instances
        """
        with self._lock:
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

    def generate_diff(self, workflow1: Dict[str, Any], workflow2: Dict[str, Any], context_lines: int = 3) -> str:
        """
        Generate a unified diff between two workflows (textual).

        Args:
            workflow1: First workflow JSON
            workflow2: Second workflow JSON
            context_lines: Number of context lines in diff

        Returns:
            Unified diff string

        Note:
            This is a textual diff. For semantic comparison that ignores
            formatting and focuses on logic changes, use semantic_compare().
        """
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

    def semantic_compare(self, workflow1: Dict[str, Any], workflow2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform semantic comparison of workflows, focusing on functional changes.

        Unlike textual diff, this method:
        - Compares nodes by functionality, not exact JSON
        - Ignores whitespace, formatting changes
        - Normalizes comparable fields (timestamps, IDs, metadata)
        - Focuses on actual workflow logic changes
        - Detects node reordering vs. modification

        Args:
            workflow1: First workflow JSON
            workflow2: Second workflow JSON

        Returns:
            Dictionary with semantic comparison results:
            {
                "identical": bool,
                "name_changed": bool,
                "nodes": {
                    "added": List[str],
                    "removed": List[str],
                    "modified": List[Dict],
                    "reordered": List[str],
                },
                "connections": {
                    "added": List[Dict],
                    "removed": List[Dict],
                },
                "settings": {
                    "changed": bool,
                    "changes": List[str],
                },
                "summary": str,
            }
        """
        result = {
            "identical": False,
            "name_changed": False,
            "nodes": {
                "added": [],
                "removed": [],
                "modified": [],
                "reordered": [],
            },
            "connections": {
                "added": [],
                "removed": [],
            },
            "settings": {
                "changed": False,
                "changes": [],
            },
            "summary": "",
        }

        # Normalize workflows (remove volatile fields)
        wf1_norm = self._normalize_workflow(workflow1)
        wf2_norm = self._normalize_workflow(workflow2)

        # Compare name
        result["name_changed"] = wf1_norm.get("name") != wf2_norm.get("name")

        # Compare nodes semantically
        nodes1 = {n["name"]: n for n in wf1_norm.get("nodes", [])}
        nodes2 = {n["name"]: n for n in wf2_norm.get("nodes", [])}

        # Detect added/removed
        result["nodes"]["added"] = sorted(set(nodes2.keys()) - set(nodes1.keys()))
        result["nodes"]["removed"] = sorted(set(nodes1.keys()) - set(nodes2.keys()))

        # Detect modified/reordered
        for name in sorted(set(nodes1.keys()) & set(nodes2.keys())):
            n1 = self._normalize_node(nodes1[name])
            n2 = self._normalize_node(nodes2[name])

            if self._nodes_equal_ignoring_position(n1, n2):
                if n1.get("position") != n2.get("position"):
                    result["nodes"]["reordered"].append(name)
            else:
                changes = self._detect_node_changes(n1, n2)
                if changes:
                    result["nodes"]["modified"].append({"name": name, "changes": changes})

        # Compare connections
        conn_diff = self._compare_connections(
            wf1_norm.get("connections", {}),
            wf2_norm.get("connections", {})
        )
        result["connections"] = conn_diff

        # Compare settings
        s1 = wf1_norm.get("settings", {})
        s2 = wf2_norm.get("settings", {})
        if s1 != s2:
            result["settings"]["changed"] = True
            all_keys = set(s1.keys()) | set(s2.keys())
            result["settings"]["changes"] = sorted([k for k in all_keys if s1.get(k) != s2.get(k)])

        # Determine if identical
        result["identical"] = (
            not result["name_changed"]
            and not result["nodes"]["added"]
            and not result["nodes"]["removed"]
            and not result["nodes"]["modified"]
            and not result["connections"]["added"]
            and not result["connections"]["removed"]
            and not result["settings"]["changed"]
        )

        # Generate summary
        result["summary"] = self._generate_semantic_summary(result)

        return result

    def _normalize_workflow(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Remove volatile fields that don't affect workflow logic."""
        normalized = workflow.copy()
        volatile = ['createdAt', 'updatedAt', 'id', 'versionId', 'meta', 'createdBy', 'updatedBy']
        for field in volatile:
            normalized.pop(field, None)
        return normalized

    def _normalize_node(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize node by removing volatile fields."""
        normalized = node.copy()
        volatile = ['id', 'webhookId']
        for field in volatile:
            normalized.pop(field, None)
        if 'position' in normalized and isinstance(normalized['position'], list):
            normalized['position'] = tuple(normalized['position'])
        return normalized

    def _nodes_equal_ignoring_position(self, node1: Dict[str, Any], node2: Dict[str, Any]) -> bool:
        """Check if nodes are equal ignoring position."""
        n1 = {k: v for k, v in node1.items() if k != 'position'}
        n2 = {k: v for k, v in node2.items() if k != 'position'}
        return n1 == n2

    def _detect_node_changes(self, node1: Dict[str, Any], node2: Dict[str, Any]) -> List[str]:
        """Detect changed fields between two nodes."""
        changes = []
        if node1.get('type') != node2.get('type'):
            changes.append('type')
        if node1.get('parameters') != node2.get('parameters'):
            changes.append('parameters')
        if node1.get('credentials') != node2.get('credentials'):
            changes.append('credentials')
        if node1.get('typeVersion') != node2.get('typeVersion'):
            changes.append('typeVersion')
        if node1.get('disabled') != node2.get('disabled'):
            changes.append('disabled')
        return changes

    def _compare_connections(self, conn1: Dict[str, Any], conn2: Dict[str, Any]) -> Dict[str, Any]:
        """Compare workflow connections."""
        def normalize_connections(conns):
            normalized = []
            for source, outputs in conns.items():
                for output_type, conn_list in outputs.items():
                    for conn_group in conn_list:
                        for conn in conn_group:
                            normalized.append((
                                source,
                                output_type,
                                conn.get('node'),
                                conn.get('type'),
                                conn.get('index'),
                            ))
            return set(normalized)

        c1_set = normalize_connections(conn1)
        c2_set = normalize_connections(conn2)

        added = c2_set - c1_set
        removed = c1_set - c2_set

        return {
            "added": sorted([
                {"from": c[0], "output": c[1], "to": c[2], "type": c[3], "index": c[4]}
                for c in added
            ], key=str),
            "removed": sorted([
                {"from": c[0], "output": c[1], "to": c[2], "type": c[3], "index": c[4]}
                for c in removed
            ], key=str),
        }

    def _generate_semantic_summary(self, result: Dict[str, Any]) -> str:
        """Generate human-readable summary."""
        if result["identical"]:
            return "Workflows are semantically identical (no functional changes)"

        parts = []
        if result["name_changed"]:
            parts.append("name changed")

        n = result["nodes"]
        if n["added"]:
            parts.append(f"{len(n['added'])} node(s) added")
        if n["removed"]:
            parts.append(f"{len(n['removed'])} node(s) removed")
        if n["modified"]:
            parts.append(f"{len(n['modified'])} node(s) modified")
        if n["reordered"]:
            parts.append(f"{len(n['reordered'])} node(s) reordered")

        c = result["connections"]
        conn_changes = len(c["added"]) + len(c["removed"])
        if conn_changes:
            parts.append(f"{conn_changes} connection(s) changed")

        if result["settings"]["changed"]:
            parts.append(f"{len(result['settings']['changes'])} setting(s) changed")

        return "; ".join(parts) if parts else "No changes detected"

    def detect_changes(self, workflow1: Dict[str, Any], workflow2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect and categorize changes between workflows.

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
            "connections_changed": False,
            "settings_changed": False,
            "breaking_changes": False,
        }

        # Compare nodes (handle None values)
        nodes1_list = workflow1.get("nodes") or []
        nodes2_list = workflow2.get("nodes") or []
        nodes1 = {n["name"]: n for n in nodes1_list}
        nodes2 = {n["name"]: n for n in nodes2_list}

        # Detect added/removed nodes
        changes["nodes_added"] = list(set(nodes2.keys()) - set(nodes1.keys()))
        changes["nodes_removed"] = list(set(nodes1.keys()) - set(nodes2.keys()))

        # Detect modified nodes
        for name in set(nodes1.keys()) & set(nodes2.keys()):
            if nodes1[name] != nodes2[name]:
                changes["nodes_modified"].append(name)

        # Check connections
        changes["connections_changed"] = workflow1.get("connections", {}) != workflow2.get(
            "connections", {}
        )

        # Check settings
        changes["settings_changed"] = workflow1.get("settings", {}) != workflow2.get("settings", {})

        # Determine if breaking
        changes["breaking_changes"] = (
            len(changes["nodes_removed"]) > 0 or changes["connections_changed"]
        )

        return changes

    def suggest_version_bump(self, workflow1: Dict[str, Any], workflow2: Dict[str, Any]) -> str:
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
        workflow: Dict[str, Any],
        version: str,
        version_id: Optional[str] = None,
        changelog: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
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

    def export_version_history(self, workflow_id: str) -> Dict[str, Any]:
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

    def save_to_disk(self, file_path: str, pretty: bool = True) -> None:
        """
        Save all version data to disk in JSON format.

        This method persists the entire version history to a JSON file,
        enabling crash recovery and version history persistence across sessions.

        Thread Safety:
            @thread_safe - Uses lock to ensure consistent snapshot

        Args:
            file_path: Path to save file
            pretty: Whether to pretty-print JSON (default: True)

        Raises:
            IOError: If file cannot be written
            ValueError: If file_path is invalid
        """
        if not file_path:
            raise ValueError("file_path cannot be empty")

        # Convert Path to string if needed
        if isinstance(file_path, Path):
            file_path = str(file_path)

        # Ensure parent directory exists
        parent_dir = os.path.dirname(file_path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)

        # Create a consistent snapshot with lock
        with self._lock:
            # Convert all versions to dict format
            data = {
                "saved_at": datetime.utcnow().isoformat() + "Z",
                "version_count": sum(len(v) for v in self.versions.values()),
                "workflow_count": len(self.versions),
                "workflows": {},
            }

            for workflow_id, versions in self.versions.items():
                data["workflows"][workflow_id] = [v.to_dict() for v in versions]

        # Write to temporary file first, then atomic rename
        temp_path = file_path + ".tmp"
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                if pretty:
                    json.dump(data, f, indent=2, sort_keys=True)
                else:
                    json.dump(data, f)

            # Atomic rename (on most systems)
            os.replace(temp_path, file_path)

            logger.info(
                f"Saved {data['version_count']} versions across {data['workflow_count']} workflows to {file_path}"
            )

        except Exception as e:
            # Clean up temp file if it exists
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
            raise IOError(f"Failed to save version data to {file_path}: {e}")

    def load_from_disk(self, file_path: str, merge: bool = False) -> None:
        """
        Load version data from disk.

        This method loads previously saved version history from a JSON file,
        enabling crash recovery and version history persistence across sessions.

        Thread Safety:
            @thread_safe - Uses lock to ensure consistent state during load

        Args:
            file_path: Path to load file
            merge: If True, merge with existing data. If False, replace (default: False)

        Raises:
            IOError: If file cannot be read
            ValueError: If file contains invalid data
            FileNotFoundError: If file doesn't exist
        """
        if not file_path:
            raise ValueError("file_path cannot be empty")

        # Convert Path to string if needed
        if isinstance(file_path, Path):
            file_path = str(file_path)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Version file not found: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Validate data format
            if not isinstance(data, dict) or "workflows" not in data:
                raise ValueError("Invalid version data format: missing 'workflows' key")

            # Load versions with lock
            with self._lock:
                if not merge:
                    # Clear existing versions
                    self.versions.clear()

                # Load each workflow's versions
                loaded_count = 0
                for workflow_id, version_list in data["workflows"].items():
                    if not isinstance(version_list, list):
                        logger.warning(f"Skipping invalid version list for workflow {workflow_id}")
                        continue

                    for version_dict in version_list:
                        try:
                            # Reconstruct WorkflowVersion from dict
                            version_obj = WorkflowVersion(
                                version=version_dict["version"],
                                version_id=version_dict.get("version_id", str(uuid.uuid4())),
                                workflow_id=version_dict.get("workflow_id", workflow_id),
                                workflow_name=version_dict.get("workflow_name", "Unknown"),
                                changelog=version_dict.get("changelog", []),
                                created_at=version_dict.get("created_at", datetime.utcnow().isoformat() + "Z"),
                                created_by=version_dict.get("created_by", "Unknown"),
                                metadata=version_dict.get("metadata", {}),
                                checksum=version_dict.get("checksum"),
                            )

                            # Add to versions (don't use create_version to avoid lock issues)
                            self.versions[workflow_id].append(version_obj)
                            loaded_count += 1

                        except Exception as e:
                            logger.warning(f"Skipping invalid version entry: {e}")

            logger.info(
                f"Loaded {loaded_count} versions across {len(data['workflows'])} workflows from {file_path}"
            )

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in version file {file_path}: {e}")
        except Exception as e:
            raise IOError(f"Failed to load version data from {file_path}: {e}")


    def _calculate_checksum(self, workflow: Dict[str, Any]) -> str:
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
    workflow: Dict[str, Any], version: str = "1.0.0", changelog: Optional[List[str]] = None
) -> Dict[str, Any]:
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
    workflow: Dict[str, Any], bump_type: str = "patch", changelog: Optional[List[str]] = None
) -> Dict[str, Any]:
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
