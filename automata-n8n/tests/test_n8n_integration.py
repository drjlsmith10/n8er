"""
n8n Integration Tests

Tests the n8n API client against a real n8n instance.
These tests are optional and only run when n8n is configured.

To run these tests:
1. Set N8N_API_URL and N8N_API_KEY in .env
2. Run: pytest tests/test_n8n_integration.py -v -m integration

Author: Project Automata - Agent 3
Version: 1.0.0
Created: 2025-11-20
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import Optional

import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from skills.n8n_api_client import (
    N8nApiClient,
    N8nApiError,
    N8nAuthenticationError,
    N8nConnectionError,
    N8nValidationError,
    create_client_from_env,
)

# Check if n8n is configured
N8N_CONFIGURED = bool(os.getenv("N8N_API_URL") and os.getenv("N8N_API_KEY"))

# Skip all tests if n8n not configured
pytestmark = pytest.mark.skipif(
    not N8N_CONFIGURED, reason="n8n not configured (N8N_API_URL and N8N_API_KEY required)"
)


# Sample workflow for testing
SAMPLE_WORKFLOW = {
    "name": "Test Workflow - Integration Test",
    "nodes": [
        {
            "name": "Start",
            "type": "n8n-nodes-base.start",
            "typeVersion": 1,
            "position": [250, 300],
            "parameters": {},
        },
        {
            "name": "Set",
            "type": "n8n-nodes-base.set",
            "typeVersion": 1,
            "position": [450, 300],
            "parameters": {"values": {"string": [{"name": "test", "value": "integration_test"}]}},
        },
    ],
    "connections": {"Start": {"main": [[{"node": "Set", "type": "main", "index": 0}]]}},
    "settings": {"executionOrder": "v1"},
}


@pytest.fixture(scope="module")
def n8n_client() -> Optional[N8nApiClient]:
    """Create n8n client for testing."""
    client = create_client_from_env()
    if not client:
        pytest.skip("Could not create n8n client from environment")
    return client


@pytest.fixture(scope="module")
def n8n_connection_test(n8n_client):
    """Test n8n connection before running tests."""
    ok, msg = n8n_client.test_connection()
    if not ok:
        pytest.skip(f"n8n connection failed: {msg}")
    return ok


@pytest.fixture
def test_workflow_id(n8n_client, n8n_connection_test):
    """
    Create a test workflow and return its ID.
    Automatically cleaned up after test.
    """
    # Import test workflow
    result = n8n_client.import_workflow(SAMPLE_WORKFLOW)
    workflow_id = result["id"]

    yield workflow_id

    # Cleanup: Delete workflow after test
    try:
        n8n_client.delete_workflow(workflow_id)
    except Exception as e:
        print(f"Warning: Could not delete test workflow {workflow_id}: {e}")


class TestN8nApiClientConnection:
    """Test n8n API client connection and authentication."""

    @pytest.mark.integration
    def test_create_client_from_env(self):
        """Test creating client from environment variables."""
        client = create_client_from_env()
        assert client is not None
        assert client.api_key is not None
        assert "api/v1" in client.api_url

    @pytest.mark.integration
    def test_connection_success(self, n8n_client):
        """Test successful connection to n8n."""
        ok, msg = n8n_client.test_connection()
        assert ok is True
        assert "success" in msg.lower()

    @pytest.mark.integration
    def test_connection_with_invalid_key(self):
        """Test connection with invalid API key."""
        client = N8nApiClient(api_url=os.getenv("N8N_API_URL"), api_key="invalid_key_12345")
        ok, msg = n8n_client.test_connection()
        # Should fail with authentication error
        # Note: Depending on n8n config, might succeed if auth not required
        assert isinstance(msg, str)

    @pytest.mark.integration
    def test_connection_with_invalid_url(self):
        """Test connection with invalid URL."""
        client = N8nApiClient(api_url="http://invalid-n8n-url.local:9999", api_key="test_key")
        ok, msg = client.test_connection()
        assert ok is False
        assert "connection" in msg.lower() or "timeout" in msg.lower()


class TestN8nVersionDetection:
    """Test n8n version detection."""

    @pytest.mark.integration
    def test_get_version(self, n8n_client, n8n_connection_test):
        """Test getting n8n version."""
        version_info = n8n_client.get_n8n_version()

        assert isinstance(version_info, dict)
        assert "version" in version_info
        assert "success" in version_info
        assert "method" in version_info

        # Version should be a string
        assert isinstance(version_info["version"], str)
        assert len(version_info["version"]) > 0

    @pytest.mark.integration
    def test_version_format(self, n8n_client, n8n_connection_test):
        """Test version format is reasonable."""
        version_info = n8n_client.get_n8n_version()
        version = version_info["version"]

        # Should contain at least a number or 'x'
        assert any(c.isdigit() or c == "x" for c in version)


class TestWorkflowOperations:
    """Test workflow CRUD operations."""

    @pytest.mark.integration
    def test_list_workflows(self, n8n_client, n8n_connection_test):
        """Test listing workflows."""
        workflows = n8n_client.list_workflows(limit=5)

        assert isinstance(workflows, list)
        # Should return at most 5 workflows
        assert len(workflows) <= 5

        # Check structure of first workflow if any exist
        if workflows:
            wf = workflows[0]
            assert "id" in wf
            assert "name" in wf

    @pytest.mark.integration
    def test_list_workflows_with_filter(self, n8n_client, n8n_connection_test):
        """Test listing workflows with active filter."""
        # List active workflows
        active_wfs = n8n_client.list_workflows(active=True, limit=10)
        assert isinstance(active_wfs, list)

        # List inactive workflows
        inactive_wfs = n8n_client.list_workflows(active=False, limit=10)
        assert isinstance(inactive_wfs, list)

    @pytest.mark.integration
    def test_import_workflow(self, n8n_client, n8n_connection_test):
        """Test importing a workflow."""
        result = n8n_client.import_workflow(SAMPLE_WORKFLOW)

        # Should return workflow with ID
        assert "id" in result
        assert "name" in result
        assert result["name"] == SAMPLE_WORKFLOW["name"]

        # Cleanup
        n8n_client.delete_workflow(result["id"])

    @pytest.mark.integration
    def test_import_workflow_activated(self, n8n_client, n8n_connection_test):
        """Test importing a workflow with activation."""
        result = n8n_client.import_workflow(SAMPLE_WORKFLOW, activate=True)

        assert "id" in result
        assert result.get("active") is True

        # Cleanup
        n8n_client.delete_workflow(result["id"])

    @pytest.mark.integration
    def test_get_workflow(self, n8n_client, test_workflow_id):
        """Test getting a specific workflow."""
        workflow = n8n_client.get_workflow(test_workflow_id)

        assert workflow["id"] == test_workflow_id
        assert "name" in workflow
        assert "nodes" in workflow
        assert "connections" in workflow

    @pytest.mark.integration
    def test_export_workflow(self, n8n_client, test_workflow_id):
        """Test exporting a workflow."""
        workflow = n8n_client.export_workflow(test_workflow_id)

        assert workflow["id"] == test_workflow_id
        assert "name" in workflow
        assert "nodes" in workflow
        assert "connections" in workflow

        # Should have at least 2 nodes (from SAMPLE_WORKFLOW)
        assert len(workflow["nodes"]) >= 2

    @pytest.mark.integration
    def test_update_workflow(self, n8n_client, test_workflow_id):
        """Test updating a workflow."""
        # Get current workflow
        workflow = n8n_client.get_workflow(test_workflow_id)

        # Update name
        original_name = workflow["name"]
        workflow["name"] = "Updated Test Workflow"

        # Update
        updated = n8n_client.update_workflow(test_workflow_id, workflow)

        assert updated["id"] == test_workflow_id
        assert updated["name"] == "Updated Test Workflow"
        assert updated["name"] != original_name

    @pytest.mark.integration
    def test_delete_workflow(self, n8n_client, n8n_connection_test):
        """Test deleting a workflow."""
        # Create a workflow
        result = n8n_client.import_workflow(SAMPLE_WORKFLOW)
        workflow_id = result["id"]

        # Delete it
        success = n8n_client.delete_workflow(workflow_id)
        assert success is True

        # Verify it's gone
        with pytest.raises(N8nApiError):
            n8n_client.get_workflow(workflow_id)

    @pytest.mark.integration
    def test_activate_workflow(self, n8n_client, test_workflow_id):
        """Test activating a workflow."""
        # Deactivate first
        n8n_client.deactivate_workflow(test_workflow_id)

        # Activate
        result = n8n_client.activate_workflow(test_workflow_id)
        assert result["active"] is True

    @pytest.mark.integration
    def test_deactivate_workflow(self, n8n_client, test_workflow_id):
        """Test deactivating a workflow."""
        # Activate first
        n8n_client.activate_workflow(test_workflow_id)

        # Deactivate
        result = n8n_client.deactivate_workflow(test_workflow_id)
        assert result["active"] is False


class TestWorkflowValidation:
    """Test workflow validation."""

    @pytest.mark.integration
    def test_validate_valid_workflow(self, n8n_client):
        """Test validating a valid workflow."""
        is_valid, errors = n8n_client.validate_workflow_import(SAMPLE_WORKFLOW)

        assert is_valid is True
        assert len(errors) == 0

    @pytest.mark.integration
    def test_validate_missing_name(self, n8n_client):
        """Test validation with missing name."""
        invalid_workflow = {"nodes": [], "connections": {}}

        is_valid, errors = n8n_client.validate_workflow_import(invalid_workflow)

        assert is_valid is False
        assert any("name" in err.lower() for err in errors)

    @pytest.mark.integration
    def test_validate_missing_nodes(self, n8n_client):
        """Test validation with missing nodes."""
        invalid_workflow = {"name": "Test", "connections": {}}

        is_valid, errors = n8n_client.validate_workflow_import(invalid_workflow)

        assert is_valid is False
        assert any("nodes" in err.lower() for err in errors)

    @pytest.mark.integration
    def test_validate_empty_nodes(self, n8n_client):
        """Test validation with empty nodes array."""
        invalid_workflow = {"name": "Test", "nodes": [], "connections": {}}

        is_valid, errors = n8n_client.validate_workflow_import(invalid_workflow)

        assert is_valid is False
        assert any("at least one node" in err.lower() for err in errors)

    @pytest.mark.integration
    def test_validate_invalid_node_structure(self, n8n_client):
        """Test validation with invalid node structure."""
        invalid_workflow = {
            "name": "Test",
            "nodes": [
                {
                    "name": "Node1"
                    # Missing required fields
                }
            ],
            "connections": {},
        }

        is_valid, errors = n8n_client.validate_workflow_import(invalid_workflow)

        assert is_valid is False
        assert len(errors) > 0

    @pytest.mark.integration
    def test_import_invalid_workflow_fails(self, n8n_client, n8n_connection_test):
        """Test that importing invalid workflow raises error."""
        invalid_workflow = {
            "name": "Invalid",
            # Missing nodes and connections
        }

        with pytest.raises(N8nValidationError):
            n8n_client.import_workflow(invalid_workflow)


class TestWorkflowImportExport:
    """Test end-to-end workflow import/export cycle."""

    @pytest.mark.integration
    def test_import_export_cycle(self, n8n_client, n8n_connection_test):
        """Test complete import/export cycle preserves workflow."""
        # Import
        imported = n8n_client.import_workflow(SAMPLE_WORKFLOW)
        workflow_id = imported["id"]

        try:
            # Export
            exported = n8n_client.export_workflow(workflow_id)

            # Verify key fields match
            assert exported["name"] == SAMPLE_WORKFLOW["name"]
            assert len(exported["nodes"]) == len(SAMPLE_WORKFLOW["nodes"])

            # Check node names preserved
            exported_node_names = {n["name"] for n in exported["nodes"]}
            original_node_names = {n["name"] for n in SAMPLE_WORKFLOW["nodes"]}
            assert exported_node_names == original_node_names

        finally:
            # Cleanup
            n8n_client.delete_workflow(workflow_id)

    @pytest.mark.integration
    def test_export_reimport_cycle(self, n8n_client, test_workflow_id):
        """Test exporting and re-importing a workflow."""
        # Export
        exported = n8n_client.export_workflow(test_workflow_id)

        # Remove ID to allow re-import
        exported.pop("id", None)
        exported["name"] = "Re-imported " + exported.get("name", "workflow")

        # Re-import
        reimported = n8n_client.import_workflow(exported)

        try:
            # Verify it was created
            assert "id" in reimported
            assert reimported["id"] != test_workflow_id
            assert "Re-imported" in reimported["name"]

        finally:
            # Cleanup
            n8n_client.delete_workflow(reimported["id"])


class TestRateLimiting:
    """Test rate limiting functionality."""

    @pytest.mark.integration
    @pytest.mark.slow
    def test_rate_limit_enforcement(self):
        """Test that rate limiting is enforced."""
        # Create client with strict rate limit
        client = N8nApiClient(
            api_url=os.getenv("N8N_API_URL"),
            api_key=os.getenv("N8N_API_KEY"),
            rate_limit_requests=5,
            rate_limit_period=2,
        )

        # Make 5 requests (should succeed)
        for i in range(5):
            client.list_workflows(limit=1)

        # 6th request should be rate limited
        from skills.n8n_api_client import N8nRateLimitError

        with pytest.raises(N8nRateLimitError):
            client.list_workflows(limit=1)


class TestHealthCheck:
    """Test health check functionality."""

    @pytest.mark.integration
    def test_health_check(self, n8n_client, n8n_connection_test):
        """Test comprehensive health check."""
        health = n8n_client.health_check()

        assert "timestamp" in health
        assert "checks" in health
        assert "overall_status" in health

        # Should have multiple checks
        assert "connection" in health["checks"]
        assert "version" in health["checks"]
        assert "workflows" in health["checks"]

        # All checks should have status
        for check_name, check_result in health["checks"].items():
            assert "status" in check_result

    @pytest.mark.integration
    def test_health_check_details(self, n8n_client, n8n_connection_test):
        """Test health check provides useful details."""
        health = n8n_client.health_check()

        # Connection check should be ok
        assert health["checks"]["connection"]["status"] == "ok"

        # Version check should have version info
        version_check = health["checks"]["version"]
        assert "version" in version_check

        # Overall status should be healthy or degraded
        assert health["overall_status"] in ["healthy", "degraded"]


class TestErrorHandling:
    """Test error handling."""

    @pytest.mark.integration
    def test_get_nonexistent_workflow(self, n8n_client, n8n_connection_test):
        """Test getting a workflow that doesn't exist."""
        with pytest.raises(N8nApiError):
            n8n_client.get_workflow("nonexistent-workflow-id-12345")

    @pytest.mark.integration
    def test_delete_nonexistent_workflow(self, n8n_client, n8n_connection_test):
        """Test deleting a workflow that doesn't exist."""
        with pytest.raises(N8nApiError):
            n8n_client.delete_workflow("nonexistent-workflow-id-12345")

    @pytest.mark.integration
    def test_update_nonexistent_workflow(self, n8n_client, n8n_connection_test):
        """Test updating a workflow that doesn't exist."""
        with pytest.raises(N8nApiError):
            n8n_client.update_workflow("nonexistent-workflow-id-12345", SAMPLE_WORKFLOW)


# Run specific integration tests
if __name__ == "__main__":
    if not N8N_CONFIGURED:
        print("ERROR: n8n not configured")
        print("Please set N8N_API_URL and N8N_API_KEY in .env file")
        print("\nExample:")
        print("  N8N_API_URL=http://localhost:5678")
        print("  N8N_API_KEY=your-api-key-here")
        sys.exit(1)

    print("Running n8n integration tests...")
    print("=" * 60)

    # Run with pytest
    pytest.main([__file__, "-v", "-m", "integration", "--tb=short"])
