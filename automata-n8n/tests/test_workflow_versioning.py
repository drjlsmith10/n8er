"""
Tests for Workflow Versioning

Tests workflow versioning functionality including:
- Semantic versioning
- Version bumping
- Version comparison
- Workflow diffing
- Change detection

Author: Project Automata - Agent 5 (High Priority Features)
Version: 2.1.0
Date: 2025-11-20
Issue: #12 - Workflow Versioning
"""

import unittest
import json
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from skills.workflow_versioning import (
    WorkflowVersion,
    WorkflowVersionManager,
    create_versioned_workflow,
    bump_workflow_version
)


class TestWorkflowVersion(unittest.TestCase):
    """Test WorkflowVersion class"""

    def test_create_workflow_version(self):
        """Test creating a workflow version"""
        version = WorkflowVersion(
            version="1.0.0",
            workflow_name="Test Workflow",
            changelog=["Initial release"]
        )

        self.assertEqual(version.version, "1.0.0")
        self.assertEqual(version.workflow_name, "Test Workflow")
        self.assertEqual(len(version.changelog), 1)

    def test_parse_version_valid(self):
        """Test parsing valid semantic version"""
        major, minor, patch = WorkflowVersion.parse_version("1.2.3")

        self.assertEqual(major, 1)
        self.assertEqual(minor, 2)
        self.assertEqual(patch, 3)

    def test_parse_version_invalid(self):
        """Test parsing invalid version raises error"""
        with self.assertRaises(ValueError):
            WorkflowVersion.parse_version("invalid")

        with self.assertRaises(ValueError):
            WorkflowVersion.parse_version("1.2")

        with self.assertRaises(ValueError):
            WorkflowVersion.parse_version("1.2.3.4")

    def test_format_version(self):
        """Test formatting version components"""
        version_str = WorkflowVersion.format_version(1, 2, 3)

        self.assertEqual(version_str, "1.2.3")

    def test_validate_valid_version(self):
        """Test validation of valid version"""
        version = WorkflowVersion(
            version="1.0.0",
            workflow_name="Test"
        )

        errors = version.validate()
        self.assertEqual(len(errors), 0)

    def test_validate_invalid_version_format(self):
        """Test validation fails for invalid version format"""
        version = WorkflowVersion(
            version="invalid",
            workflow_name="Test"
        )

        errors = version.validate()
        self.assertGreater(len(errors), 0)

    def test_to_dict(self):
        """Test converting version to dictionary"""
        version = WorkflowVersion(
            version="1.0.0",
            workflow_name="Test",
            changelog=["Initial release"]
        )

        version_dict = version.to_dict()

        self.assertIsInstance(version_dict, dict)
        self.assertEqual(version_dict["version"], "1.0.0")
        self.assertIn("changelog", version_dict)


class TestWorkflowVersionManager(unittest.TestCase):
    """Test WorkflowVersionManager class"""

    def setUp(self):
        """Set up test fixtures"""
        self.manager = WorkflowVersionManager()
        self.workflow = {
            "name": "Test Workflow",
            "nodes": [
                {"name": "Start", "type": "n8n-nodes-base.start"}
            ],
            "connections": {},
            "settings": {}
        }

    def test_create_version(self):
        """Test creating a workflow version"""
        version = self.manager.create_version(
            self.workflow,
            version="1.0.0",
            changelog=["Initial release"]
        )

        self.assertIsInstance(version, WorkflowVersion)
        self.assertEqual(version.version, "1.0.0")
        self.assertEqual(version.workflow_name, "Test Workflow")

    def test_version_bump_patch(self):
        """Test bumping patch version"""
        # Create initial version
        v1 = self.manager.create_version(
            self.workflow,
            version="1.0.0",
            workflow_id="test-workflow"
        )

        # Bump patch
        v2 = self.manager.version_bump(
            self.workflow,
            bump_type="patch",
            workflow_id="test-workflow"
        )

        self.assertEqual(v2.version, "1.0.1")

    def test_version_bump_minor(self):
        """Test bumping minor version"""
        v1 = self.manager.create_version(
            self.workflow,
            version="1.0.5",
            workflow_id="test-workflow"
        )

        v2 = self.manager.version_bump(
            self.workflow,
            bump_type="minor",
            workflow_id="test-workflow"
        )

        self.assertEqual(v2.version, "1.1.0")

    def test_version_bump_major(self):
        """Test bumping major version"""
        v1 = self.manager.create_version(
            self.workflow,
            version="1.5.3",
            workflow_id="test-workflow"
        )

        v2 = self.manager.version_bump(
            self.workflow,
            bump_type="major",
            workflow_id="test-workflow"
        )

        self.assertEqual(v2.version, "2.0.0")

    def test_version_bump_invalid_type(self):
        """Test invalid bump type raises error"""
        with self.assertRaises(ValueError):
            self.manager.version_bump(
                self.workflow,
                bump_type="invalid"
            )

    def test_get_latest_version(self):
        """Test getting latest version"""
        workflow_id = "test-workflow"

        self.manager.create_version(
            self.workflow,
            version="1.0.0",
            workflow_id=workflow_id
        )

        self.manager.create_version(
            self.workflow,
            version="1.1.0",
            workflow_id=workflow_id
        )

        self.manager.create_version(
            self.workflow,
            version="1.0.5",
            workflow_id=workflow_id
        )

        latest = self.manager.get_latest_version(workflow_id)

        self.assertEqual(latest.version, "1.1.0")

    def test_get_version(self):
        """Test getting specific version"""
        workflow_id = "test-workflow"

        self.manager.create_version(
            self.workflow,
            version="1.0.0",
            workflow_id=workflow_id
        )

        version = self.manager.get_version(workflow_id, "1.0.0")

        self.assertIsNotNone(version)
        self.assertEqual(version.version, "1.0.0")

    def test_get_nonexistent_version(self):
        """Test getting non-existent version returns None"""
        version = self.manager.get_version("nonexistent", "1.0.0")

        self.assertIsNone(version)

    def test_list_versions(self):
        """Test listing all versions"""
        workflow_id = "test-workflow"

        self.manager.create_version(
            self.workflow,
            version="1.0.0",
            workflow_id=workflow_id
        )

        self.manager.create_version(
            self.workflow,
            version="2.0.0",
            workflow_id=workflow_id
        )

        versions = self.manager.list_versions(workflow_id)

        self.assertEqual(len(versions), 2)
        # Should be sorted descending by default
        self.assertEqual(versions[0].version, "2.0.0")

    def test_list_versions_ascending(self):
        """Test listing versions in ascending order"""
        workflow_id = "test-workflow"

        self.manager.create_version(
            self.workflow,
            version="1.0.0",
            workflow_id=workflow_id
        )

        self.manager.create_version(
            self.workflow,
            version="2.0.0",
            workflow_id=workflow_id
        )

        versions = self.manager.list_versions(workflow_id, ascending=True)

        self.assertEqual(versions[0].version, "1.0.0")

    def test_compare_versions(self):
        """Test comparing two versions"""
        workflow_id = "test-workflow"

        self.manager.create_version(
            self.workflow,
            version="1.0.0",
            workflow_id=workflow_id
        )

        self.manager.create_version(
            self.workflow,
            version="2.0.0",
            workflow_id=workflow_id
        )

        comparison = self.manager.compare_versions(
            workflow_id,
            "1.0.0",
            "2.0.0"
        )

        self.assertEqual(comparison["newer_version"], "2.0.0")
        self.assertEqual(comparison["older_version"], "1.0.0")
        self.assertIn("version_difference", comparison)

    def test_generate_diff(self):
        """Test generating workflow diff"""
        workflow1 = {
            "name": "Workflow",
            "nodes": [
                {"name": "Node1"}
            ]
        }

        workflow2 = {
            "name": "Workflow",
            "nodes": [
                {"name": "Node1"},
                {"name": "Node2"}
            ]
        }

        diff = self.manager.generate_diff(workflow1, workflow2)

        self.assertIsInstance(diff, str)
        self.assertIn("Node2", diff)

    def test_detect_changes_nodes_added(self):
        """Test detecting added nodes"""
        workflow1 = {
            "nodes": [
                {"name": "Node1", "type": "test"}
            ],
            "connections": {},
            "settings": {}
        }

        workflow2 = {
            "nodes": [
                {"name": "Node1", "type": "test"},
                {"name": "Node2", "type": "test"}
            ],
            "connections": {},
            "settings": {}
        }

        changes = self.manager.detect_changes(workflow1, workflow2)

        self.assertIn("Node2", changes["nodes_added"])
        self.assertEqual(len(changes["nodes_removed"]), 0)

    def test_detect_changes_nodes_removed(self):
        """Test detecting removed nodes"""
        workflow1 = {
            "nodes": [
                {"name": "Node1", "type": "test"},
                {"name": "Node2", "type": "test"}
            ],
            "connections": {},
            "settings": {}
        }

        workflow2 = {
            "nodes": [
                {"name": "Node1", "type": "test"}
            ],
            "connections": {},
            "settings": {}
        }

        changes = self.manager.detect_changes(workflow1, workflow2)

        self.assertIn("Node2", changes["nodes_removed"])
        self.assertTrue(changes["breaking_changes"])

    def test_detect_changes_nodes_modified(self):
        """Test detecting modified nodes"""
        workflow1 = {
            "nodes": [
                {"name": "Node1", "type": "test", "param": "old"}
            ],
            "connections": {},
            "settings": {}
        }

        workflow2 = {
            "nodes": [
                {"name": "Node1", "type": "test", "param": "new"}
            ],
            "connections": {},
            "settings": {}
        }

        changes = self.manager.detect_changes(workflow1, workflow2)

        self.assertIn("Node1", changes["nodes_modified"])

    def test_suggest_version_bump_patch(self):
        """Test suggesting patch bump for minor changes"""
        workflow1 = {
            "name": "Workflow",
            "nodes": [
                {"name": "Node1", "param": "old"}
            ],
            "connections": {},
            "settings": {}
        }

        workflow2 = {
            "name": "Workflow",
            "nodes": [
                {"name": "Node1", "param": "new"}
            ],
            "connections": {},
            "settings": {}
        }

        suggestion = self.manager.suggest_version_bump(workflow1, workflow2)

        self.assertEqual(suggestion, "patch")

    def test_suggest_version_bump_minor(self):
        """Test suggesting minor bump for added features"""
        workflow1 = {
            "name": "Workflow",
            "nodes": [
                {"name": "Node1"}
            ],
            "connections": {},
            "settings": {}
        }

        workflow2 = {
            "name": "Workflow",
            "nodes": [
                {"name": "Node1"},
                {"name": "Node2"}
            ],
            "connections": {},
            "settings": {}
        }

        suggestion = self.manager.suggest_version_bump(workflow1, workflow2)

        self.assertEqual(suggestion, "minor")

    def test_suggest_version_bump_major(self):
        """Test suggesting major bump for breaking changes"""
        workflow1 = {
            "name": "Workflow",
            "nodes": [
                {"name": "Node1"},
                {"name": "Node2"}
            ],
            "connections": {},
            "settings": {}
        }

        workflow2 = {
            "name": "Workflow",
            "nodes": [
                {"name": "Node1"}
            ],
            "connections": {},
            "settings": {}
        }

        suggestion = self.manager.suggest_version_bump(workflow1, workflow2)

        self.assertEqual(suggestion, "major")

    def test_add_version_to_workflow(self):
        """Test adding version metadata to workflow"""
        workflow = {"name": "Test"}

        versioned = self.manager.add_version_to_workflow(
            workflow,
            version="1.0.0",
            changelog=["Initial release"]
        )

        self.assertIn("version", versioned)
        self.assertIn("versionId", versioned)
        self.assertIn("changelog", versioned)
        self.assertIn("meta", versioned)
        self.assertEqual(versioned["version"], "1.0.0")

    def test_export_version_history(self):
        """Test exporting version history"""
        workflow_id = "test-workflow"

        self.manager.create_version(
            self.workflow,
            version="1.0.0",
            workflow_id=workflow_id
        )

        self.manager.create_version(
            self.workflow,
            version="1.1.0",
            workflow_id=workflow_id
        )

        history = self.manager.export_version_history(workflow_id)

        self.assertIn("total_versions", history)
        self.assertEqual(history["total_versions"], 2)
        self.assertIn("latest_version", history)
        self.assertEqual(history["latest_version"], "1.1.0")


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions"""

    def setUp(self):
        """Set up test fixtures"""
        self.workflow = {
            "name": "Test Workflow",
            "nodes": [],
            "connections": {}
        }

    def test_create_versioned_workflow(self):
        """Test creating versioned workflow"""
        versioned = create_versioned_workflow(
            self.workflow,
            version="1.0.0",
            changelog=["Initial release"]
        )

        self.assertIn("version", versioned)
        self.assertEqual(versioned["version"], "1.0.0")
        self.assertIn("changelog", versioned)

    def test_bump_workflow_version(self):
        """Test bumping workflow version"""
        workflow = {
            "name": "Test",
            "version": "1.0.0",
            "nodes": [],
            "connections": {}
        }

        bumped = bump_workflow_version(
            workflow,
            bump_type="minor",
            changelog=["New feature"]
        )

        self.assertEqual(bumped["version"], "1.1.0")


if __name__ == '__main__':
    unittest.main()
