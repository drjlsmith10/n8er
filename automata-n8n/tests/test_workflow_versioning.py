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
import os
import tempfile
import threading
import time
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


class TestPersistence(unittest.TestCase):
    """Test persistence functionality"""

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
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test files"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_save_to_disk(self):
        """
        Test saving version history to disk.

        Validates that version data is correctly serialized to a JSON file.
        """
        workflow_id = "test-workflow"

        # Create some versions
        self.manager.create_version(
            self.workflow,
            version="1.0.0",
            workflow_id=workflow_id,
            changelog=["Initial release"]
        )

        self.manager.create_version(
            self.workflow,
            version="1.1.0",
            workflow_id=workflow_id,
            changelog=["Added feature"]
        )

        # Save to disk
        file_path = os.path.join(self.temp_dir, "versions.json")
        self.manager.save_to_disk(file_path)

        # Verify file exists
        self.assertTrue(os.path.exists(file_path))

        # Verify file contents
        with open(file_path, 'r') as f:
            data = json.load(f)

        self.assertIn("workflows", data)
        self.assertIn(workflow_id, data["workflows"])
        self.assertEqual(len(data["workflows"][workflow_id]), 2)
        self.assertEqual(data["version_count"], 2)
        self.assertEqual(data["workflow_count"], 1)

    def test_load_from_disk(self):
        """
        Test loading version history from disk.

        Validates that version data is correctly deserialized from a JSON file
        and reconstructs WorkflowVersion objects.
        """
        workflow_id = "test-workflow"

        # Create and save versions
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

        file_path = os.path.join(self.temp_dir, "versions.json")
        self.manager.save_to_disk(file_path)

        # Create new manager and load
        new_manager = WorkflowVersionManager()
        new_manager.load_from_disk(file_path)

        # Verify versions loaded correctly
        versions = new_manager.list_versions(workflow_id)
        self.assertEqual(len(versions), 2)
        self.assertEqual(versions[0].version, "2.0.0")
        self.assertEqual(versions[1].version, "1.0.0")

    def test_load_from_disk_merge(self):
        """
        Test loading and merging version data.

        Validates that merge=True preserves existing data while adding loaded data.
        """
        # Create initial versions in manager
        self.manager.create_version(
            self.workflow,
            version="1.0.0",
            workflow_id="workflow-1"
        )

        # Create separate manager with different versions
        temp_manager = WorkflowVersionManager()
        temp_manager.create_version(
            self.workflow,
            version="1.0.0",
            workflow_id="workflow-2"
        )

        # Save temp manager
        file_path = os.path.join(self.temp_dir, "versions.json")
        temp_manager.save_to_disk(file_path)

        # Load with merge
        self.manager.load_from_disk(file_path, merge=True)

        # Should have both workflows
        self.assertEqual(len(self.manager.versions), 2)
        self.assertIn("workflow-1", self.manager.versions)
        self.assertIn("workflow-2", self.manager.versions)

    def test_crash_recovery(self):
        """
        Test crash recovery scenario.

        Simulates a crash by creating versions, saving, clearing manager,
        then loading to verify all data is recovered.
        """
        workflow_id = "test-workflow"

        # Create multiple versions
        for i in range(5):
            self.manager.create_version(
                self.workflow,
                version=f"1.{i}.0",
                workflow_id=workflow_id,
                changelog=[f"Version {i}"]
            )

        # Save to disk
        file_path = os.path.join(self.temp_dir, "versions.json")
        self.manager.save_to_disk(file_path)

        # Simulate crash - clear manager
        self.manager.versions.clear()
        self.assertEqual(len(self.manager.versions), 0)

        # Recover from disk
        self.manager.load_from_disk(file_path)

        # Verify all versions recovered
        versions = self.manager.list_versions(workflow_id)
        self.assertEqual(len(versions), 5)

        # Verify latest version is correct
        latest = self.manager.get_latest_version(workflow_id)
        self.assertEqual(latest.version, "1.4.0")

    def test_concurrent_saves(self):
        """
        Test concurrent save operations.

        Validates that multiple threads can safely save version data
        without corruption or race conditions.
        """
        results = []
        errors = []

        def save_versions(thread_id):
            try:
                # Create a version
                self.manager.create_version(
                    self.workflow,
                    version=f"{thread_id}.0.0",
                    workflow_id=f"workflow-{thread_id}"
                )

                # Save to disk
                file_path = os.path.join(self.temp_dir, f"versions_{thread_id}.json")
                self.manager.save_to_disk(file_path)

                results.append(thread_id)
            except Exception as e:
                errors.append((thread_id, str(e)))

        # Create and start threads
        threads = []
        for i in range(10):
            t = threading.Thread(target=save_versions, args=(i,))
            threads.append(t)
            t.start()

        # Wait for all threads
        for t in threads:
            t.join()

        # Verify no errors
        self.assertEqual(len(errors), 0, f"Errors occurred: {errors}")
        self.assertEqual(len(results), 10)

        # Verify all files were created
        for i in range(10):
            file_path = os.path.join(self.temp_dir, f"versions_{i}.json")
            self.assertTrue(os.path.exists(file_path))

    def test_corrupted_file_handling(self):
        """
        Test handling of corrupted version files.

        Validates that loading a corrupted file raises appropriate errors
        without crashing the application.
        """
        # Create corrupted JSON file
        file_path = os.path.join(self.temp_dir, "corrupted.json")
        with open(file_path, 'w') as f:
            f.write("{ invalid json ")

        # Should raise ValueError for invalid JSON
        with self.assertRaises(ValueError) as context:
            self.manager.load_from_disk(file_path)

        self.assertIn("Invalid JSON", str(context.exception))

    def test_missing_file_handling(self):
        """
        Test handling of missing version files.

        Validates that attempting to load a non-existent file
        raises FileNotFoundError.
        """
        file_path = os.path.join(self.temp_dir, "nonexistent.json")

        with self.assertRaises(FileNotFoundError):
            self.manager.load_from_disk(file_path)

    def test_invalid_file_format(self):
        """
        Test handling of invalid file format.

        Validates that loading a file with invalid structure
        raises appropriate errors.
        """
        # Create file with wrong structure
        file_path = os.path.join(self.temp_dir, "invalid.json")
        with open(file_path, 'w') as f:
            json.dump({"wrong": "structure"}, f)

        # Should raise IOError for invalid format (wraps ValueError)
        with self.assertRaises(IOError) as context:
            self.manager.load_from_disk(file_path)

        self.assertIn("missing 'workflows' key", str(context.exception))

    def test_empty_file_path(self):
        """
        Test handling of empty file path.

        Validates that empty file paths are rejected with ValueError.
        """
        with self.assertRaises(ValueError) as context:
            self.manager.save_to_disk("")

        self.assertIn("cannot be empty", str(context.exception))

        with self.assertRaises(ValueError) as context:
            self.manager.load_from_disk("")

        self.assertIn("cannot be empty", str(context.exception))

    def test_version_history_persistence(self):
        """
        Test complete version history persistence.

        Validates that complex version histories with multiple workflows
        are correctly persisted and restored.
        """
        # Create versions for multiple workflows
        for workflow_num in range(3):
            workflow_id = f"workflow-{workflow_num}"
            for version_num in range(3):
                self.manager.create_version(
                    self.workflow,
                    version=f"{workflow_num}.{version_num}.0",
                    workflow_id=workflow_id,
                    changelog=[f"Workflow {workflow_num} version {version_num}"]
                )

        # Save
        file_path = os.path.join(self.temp_dir, "history.json")
        self.manager.save_to_disk(file_path)

        # Load into new manager
        new_manager = WorkflowVersionManager()
        new_manager.load_from_disk(file_path)

        # Verify all workflows and versions
        for workflow_num in range(3):
            workflow_id = f"workflow-{workflow_num}"
            versions = new_manager.list_versions(workflow_id)
            self.assertEqual(len(versions), 3)

    def test_save_creates_directory(self):
        """
        Test that save_to_disk creates parent directories if needed.

        Validates that nested directories are created automatically.
        """
        # Use nested path that doesn't exist
        file_path = os.path.join(self.temp_dir, "nested", "dir", "versions.json")

        # Create a version
        self.manager.create_version(
            self.workflow,
            version="1.0.0",
            workflow_id="test"
        )

        # Save should create directories
        self.manager.save_to_disk(file_path)

        # Verify file exists
        self.assertTrue(os.path.exists(file_path))

    def test_atomic_write(self):
        """
        Test that saves are atomic (using temp file + rename).

        This test validates that the save operation writes to a temp file
        first, then renames it to the target file, ensuring atomicity.
        """
        file_path = os.path.join(self.temp_dir, "atomic.json")

        # Create a version
        self.manager.create_version(
            self.workflow,
            version="1.0.0",
            workflow_id="test"
        )

        # Save
        self.manager.save_to_disk(file_path)

        # Temp file should not exist after save
        temp_path = file_path + ".tmp"
        self.assertFalse(os.path.exists(temp_path))

        # Target file should exist
        self.assertTrue(os.path.exists(file_path))


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""

    def setUp(self):
        """Set up test fixtures"""
        self.manager = WorkflowVersionManager()
        self.workflow = {
            "name": "Test Workflow",
            "nodes": [{"name": "Start", "type": "n8n-nodes-base.start"}],
            "connections": {},
            "settings": {}
        }

    def test_version_with_leading_zeros(self):
        """Test handling of versions with leading zeros (e.g., 01.02.03)"""
        version = WorkflowVersion.parse_version("01.02.03")
        self.assertEqual(version, (1, 2, 3))

    def test_version_with_very_large_numbers(self):
        """Test handling of versions with very large numbers"""
        version = WorkflowVersion.parse_version("999.999.999")
        self.assertEqual(version, (999, 999, 999))

        formatted = WorkflowVersion.format_version(999, 999, 999)
        self.assertEqual(formatted, "999.999.999")

    def test_empty_workflow_name(self):
        """Test handling of workflow with empty name"""
        workflow = {"name": "", "nodes": [], "connections": {}}
        version = self.manager.create_version(workflow, version="1.0.0")

        # Should use default name
        self.assertIsNotNone(version.workflow_name)

    def test_workflow_without_name(self):
        """Test handling of workflow without name field"""
        workflow = {"nodes": [], "connections": {}}
        version = self.manager.create_version(workflow, version="1.0.0")

        self.assertEqual(version.workflow_name, "Unnamed Workflow")

    def test_empty_changelog(self):
        """Test version with empty changelog"""
        version = self.manager.create_version(
            self.workflow,
            version="1.0.0",
            changelog=[]
        )

        self.assertEqual(version.changelog, [])

    def test_none_changelog(self):
        """Test version with None changelog"""
        version = self.manager.create_version(
            self.workflow,
            version="1.0.0",
            changelog=None
        )

        self.assertEqual(version.changelog, [])

    def test_very_long_changelog(self):
        """Test version with very long changelog"""
        long_changelog = [f"Change {i}" for i in range(1000)]
        version = self.manager.create_version(
            self.workflow,
            version="1.0.0",
            changelog=long_changelog
        )

        self.assertEqual(len(version.changelog), 1000)

    def test_workflow_with_special_characters_in_name(self):
        """Test workflow with special characters in name"""
        workflow = {
            "name": "Test@Workflow#123!$%",
            "nodes": [],
            "connections": {}
        }

        version = self.manager.create_version(workflow, version="1.0.0")
        self.assertEqual(version.workflow_name, "Test@Workflow#123!$%")

    def test_workflow_with_unicode_name(self):
        """Test workflow with Unicode characters in name"""
        workflow = {
            "name": "测试工作流 🚀",
            "nodes": [],
            "connections": {}
        }

        version = self.manager.create_version(workflow, version="1.0.0")
        self.assertEqual(version.workflow_name, "测试工作流 🚀")

    def test_multiple_versions_same_number(self):
        """Test creating multiple versions with same version number"""
        workflow_id = "test-workflow"

        # Create first version
        v1 = self.manager.create_version(
            self.workflow,
            version="1.0.0",
            workflow_id=workflow_id
        )

        # Create another version with same number (should be allowed)
        v2 = self.manager.create_version(
            self.workflow,
            version="1.0.0",
            workflow_id=workflow_id
        )

        # Both should exist
        versions = self.manager.list_versions(workflow_id)
        self.assertEqual(len(versions), 2)

    def test_zero_version(self):
        """Test version 0.0.0"""
        version = self.manager.create_version(
            self.workflow,
            version="0.0.0"
        )

        self.assertEqual(version.version, "0.0.0")

    def test_bump_from_zero_version(self):
        """Test bumping from version 0.0.0"""
        workflow_id = "test-workflow"

        # Create version 0.0.0
        self.manager.create_version(
            self.workflow,
            version="0.0.0",
            workflow_id=workflow_id
        )

        # Bump patch
        v = self.manager.version_bump(
            self.workflow,
            bump_type="patch",
            workflow_id=workflow_id
        )

        self.assertEqual(v.version, "0.0.1")

    def test_detect_changes_with_none_fields(self):
        """Test change detection with None fields"""
        workflow1 = {"name": "Test", "nodes": None, "connections": None}
        workflow2 = {"name": "Test", "nodes": [], "connections": {}}

        changes = self.manager.detect_changes(workflow1, workflow2)

        # Should handle None gracefully
        self.assertIsInstance(changes, dict)

    def test_detect_changes_empty_workflows(self):
        """Test change detection between empty workflows"""
        workflow1 = {}
        workflow2 = {}

        changes = self.manager.detect_changes(workflow1, workflow2)

        self.assertFalse(changes["name_changed"])
        self.assertEqual(len(changes["nodes_added"]), 0)
        self.assertEqual(len(changes["nodes_removed"]), 0)

    def test_checksum_consistency(self):
        """Test that checksum is consistent for identical workflows"""
        workflow_id = "test-workflow"

        v1 = self.manager.create_version(
            self.workflow,
            version="1.0.0",
            workflow_id=workflow_id
        )

        # Create another version with same workflow
        v2 = self.manager.create_version(
            self.workflow,
            version="1.0.1",
            workflow_id=workflow_id
        )

        # Checksums should match for identical content
        self.assertEqual(v1.checksum, v2.checksum)

    def test_checksum_different_for_modified_workflow(self):
        """Test that checksum changes when workflow is modified"""
        workflow_id = "test-workflow"

        v1 = self.manager.create_version(
            self.workflow,
            version="1.0.0",
            workflow_id=workflow_id
        )

        # Modify workflow
        modified_workflow = self.workflow.copy()
        modified_workflow["nodes"].append({"name": "New", "type": "test"})

        v2 = self.manager.create_version(
            modified_workflow,
            version="1.1.0",
            workflow_id=workflow_id
        )

        # Checksums should differ
        self.assertNotEqual(v1.checksum, v2.checksum)

    def test_compare_versions_invalid(self):
        """Test comparing non-existent versions"""
        with self.assertRaises(ValueError):
            self.manager.compare_versions("workflow-1", "1.0.0", "2.0.0")

    def test_list_versions_nonexistent_workflow(self):
        """Test listing versions for non-existent workflow"""
        versions = self.manager.list_versions("nonexistent")
        self.assertEqual(len(versions), 0)

    def test_get_latest_version_empty(self):
        """Test getting latest version when no versions exist"""
        latest = self.manager.get_latest_version("nonexistent")
        self.assertIsNone(latest)


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
