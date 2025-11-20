"""
Test Suite: Workflow Generation

Tests for generate_workflow_json.py module

Author: Project Automata - Tester Agent
Version: 1.0.0
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from skills.generate_workflow_json import (
        TemplateLibrary,
        WorkflowBuilder,
        generate_from_template,
    )
except ImportError:
    pytest.skip("generate_workflow_json module not available", allow_module_level=True)


class TestWorkflowBuilder:
    """Test suite for WorkflowBuilder class"""

    def test_builder_initialization(self):
        """Test builder can be initialized"""
        builder = WorkflowBuilder("Test Workflow")
        assert builder.name == "Test Workflow"
        assert len(builder.nodes) == 0
        assert len(builder.connections) == 0

    def test_add_node(self):
        """Test adding a node"""
        builder = WorkflowBuilder("Test")
        builder.add_node("n8n-nodes-base.manualTrigger", "Start", parameters={})

        assert len(builder.nodes) == 1
        assert builder.nodes[0]["name"] == "Start"
        assert builder.nodes[0]["type"] == "n8n-nodes-base.manualTrigger"

    def test_add_trigger(self):
        """Test adding a trigger node"""
        builder = WorkflowBuilder("Test")
        builder.add_trigger("webhook", "Webhook Trigger", {"path": "test"})

        assert len(builder.nodes) == 1
        assert "webhook" in builder.nodes[0]["type"].lower()

    def test_connect_nodes(self):
        """Test connecting two nodes"""
        builder = WorkflowBuilder("Test")
        builder.add_trigger("manual", "Start")
        builder.add_node("n8n-nodes-base.noOp", "Action")
        builder.connect("Start", "Action")

        assert "Start" in builder.connections
        assert len(builder.connections["Start"]["main"][0]) == 1

    def test_connect_chain(self):
        """Test chaining multiple nodes"""
        builder = WorkflowBuilder("Test")
        builder.add_trigger("manual", "Start")
        builder.add_node("n8n-nodes-base.noOp", "Middle")
        builder.add_node("n8n-nodes-base.noOp", "End")
        builder.connect_chain("Start", "Middle", "End")

        assert "Start" in builder.connections
        assert "Middle" in builder.connections

    def test_duplicate_node_names(self):
        """Test handling of duplicate node names"""
        builder = WorkflowBuilder("Test")
        builder.add_node("n8n-nodes-base.noOp", "Action")
        builder.add_node("n8n-nodes-base.noOp", "Action")  # Duplicate

        assert len(builder.nodes) == 2
        assert builder.nodes[0]["name"] == "Action"
        assert builder.nodes[1]["name"] == "Action1"  # Auto-renamed

    def test_build_workflow(self):
        """Test building complete workflow"""
        builder = WorkflowBuilder("Test Workflow")
        builder.add_trigger("manual", "Start")
        builder.add_node("n8n-nodes-base.noOp", "Action")
        builder.connect("Start", "Action")

        workflow = builder.build(validate=False)

        assert workflow["name"] == "Test Workflow"
        assert "nodes" in workflow
        assert "connections" in workflow
        assert len(workflow["nodes"]) == 2

    def test_auto_positioning(self):
        """Test automatic node positioning"""
        builder = WorkflowBuilder("Test")
        builder.add_trigger("manual", "Node1")
        builder.add_node("n8n-nodes-base.noOp", "Node2")
        builder.add_node("n8n-nodes-base.noOp", "Node3")

        # Check positions increase
        pos1 = builder.nodes[0]["position"]
        pos2 = builder.nodes[1]["position"]
        pos3 = builder.nodes[2]["position"]

        assert pos2[0] > pos1[0]  # X coordinate increases
        assert pos3[0] > pos2[0]


class TestTemplateLibrary:
    """Test suite for TemplateLibrary"""

    def test_webhook_to_email_template(self):
        """Test webhook to email template generation"""
        workflow = TemplateLibrary.webhook_to_email(
            webhook_path="test-webhook", email_to="test@example.com"
        )

        assert workflow["name"] == "Webhook to Email"
        assert len(workflow["nodes"]) == 2
        assert len(workflow["connections"]) > 0

    def test_http_request_transform_template(self):
        """Test HTTP request + transform template"""
        workflow = TemplateLibrary.http_request_transform(
            url="https://api.example.com/data", method="GET"
        )

        assert workflow["name"] == "HTTP Request + Transform"
        assert len(workflow["nodes"]) == 3  # Trigger, HTTP, Transform

    def test_etl_pipeline_template(self):
        """Test ETL pipeline template"""
        workflow = TemplateLibrary.etl_pipeline()

        assert workflow["name"] == "ETL Pipeline"
        assert len(workflow["nodes"]) == 4  # Trigger, Extract, Transform, Load

    def test_api_with_error_handling_template(self):
        """Test API with error handling template"""
        workflow = TemplateLibrary.api_with_error_handling(
            api_url="https://api.example.com/endpoint"
        )

        assert "API with Error Handling" in workflow["name"]
        # Should have trigger, API call, IF node, success/error handlers
        assert len(workflow["nodes"]) >= 4


class TestTemplateGeneration:
    """Test suite for template-based generation"""

    def test_generate_from_template_webhook_email(self):
        """Test generating from webhook_email template"""
        workflow = generate_from_template(
            "webhook_email", webhook_path="alerts", email_to="admin@example.com"
        )

        assert workflow is not None
        assert "nodes" in workflow
        assert len(workflow["nodes"]) > 0

    def test_generate_from_unknown_template(self):
        """Test error handling for unknown template"""
        with pytest.raises(ValueError):
            generate_from_template("unknown_template")


class TestWorkflowValidation:
    """Test suite for workflow validation during build"""

    def test_invalid_connection_source(self):
        """Test connecting from non-existent node"""
        builder = WorkflowBuilder("Test")
        builder.add_node("n8n-nodes-base.noOp", "Action")

        with pytest.raises(ValueError):
            builder.connect("NonExistent", "Action")

    def test_invalid_connection_target(self):
        """Test connecting to non-existent node"""
        builder = WorkflowBuilder("Test")
        builder.add_node("n8n-nodes-base.noOp", "Action")

        with pytest.raises(ValueError):
            builder.connect("Action", "NonExistent")


# Fixtures
@pytest.fixture
def builder():
    """Fixture providing a WorkflowBuilder instance"""
    return WorkflowBuilder("Test Workflow")


@pytest.fixture
def simple_workflow():
    """Fixture providing a simple generated workflow"""
    builder = WorkflowBuilder("Simple Test")
    builder.add_trigger("manual", "Start")
    builder.add_node("n8n-nodes-base.noOp", "End")
    builder.connect("Start", "End")
    return builder.build(validate=False)


# Integration tests
class TestWorkflowIntegration:
    """Integration tests for workflow generation"""

    def test_build_and_parse_roundtrip(self):
        """Test building a workflow and parsing it back"""
        # Build workflow
        builder = WorkflowBuilder("Roundtrip Test")
        builder.add_trigger("manual", "Start")
        builder.add_node("n8n-nodes-base.noOp", "Action")
        builder.connect("Start", "Action")
        workflow = builder.build(validate=False)

        # Parse it back
        try:
            from skills.parse_n8n_schema import parse_workflow_json

            parsed = parse_workflow_json(workflow, strict=False)

            assert parsed is not None
            assert len(parsed.nodes) == 2
            assert len(parsed.connections) == 1
        except ImportError:
            pytest.skip("parse_n8n_schema not available")


class TestWorkflowSchemaFields:
    """Test suite for new n8n 1.60+ workflow schema fields"""

    def test_workflow_has_id_field(self):
        """Test that generated workflows include id field"""
        builder = WorkflowBuilder("Schema Test")
        builder.add_trigger("manual", "Start")
        workflow = builder.build(validate=False)

        assert "id" in workflow
        assert workflow["id"] is not None
        assert len(workflow["id"]) > 0  # Should be a UUID

    def test_workflow_has_version_id_field(self):
        """Test that generated workflows include versionId field"""
        builder = WorkflowBuilder("Schema Test")
        builder.add_trigger("manual", "Start")
        workflow = builder.build(validate=False)

        assert "versionId" in workflow
        assert workflow["versionId"] is not None
        assert len(workflow["versionId"]) > 0  # Should be a UUID

    def test_workflow_has_meta_field(self):
        """Test that generated workflows include meta field"""
        builder = WorkflowBuilder("Schema Test")
        builder.add_trigger("manual", "Start")
        workflow = builder.build(validate=False)

        assert "meta" in workflow
        assert isinstance(workflow["meta"], dict)
        assert "templateCredsSetupCompleted" in workflow["meta"]
        assert "instanceId" in workflow["meta"]

    def test_workflow_has_pin_data_field(self):
        """Test that generated workflows include pinData field"""
        builder = WorkflowBuilder("Schema Test")
        builder.add_trigger("manual", "Start")
        workflow = builder.build(validate=False)

        assert "pinData" in workflow
        assert isinstance(workflow["pinData"], dict)

    def test_workflow_has_static_data_field(self):
        """Test that generated workflows include staticData field"""
        builder = WorkflowBuilder("Schema Test")
        builder.add_trigger("manual", "Start")
        workflow = builder.build(validate=False)

        assert "staticData" in workflow
        assert isinstance(workflow["staticData"], dict)

    def test_workflow_settings_complete(self):
        """Test that workflow settings include all recommended fields"""
        builder = WorkflowBuilder("Settings Test")
        builder.add_trigger("manual", "Start")
        workflow = builder.build(validate=False)

        assert "settings" in workflow
        settings = workflow["settings"]

        # Check all recommended settings are present
        assert "executionOrder" in settings
        assert "saveExecutionProgress" in settings
        assert "saveManualExecutions" in settings
        assert "timezone" in settings
        assert "callerPolicy" in settings

    def test_workflow_settings_values(self):
        """Test that workflow settings have correct default values"""
        builder = WorkflowBuilder("Settings Test")
        workflow = builder.build(validate=False)

        settings = workflow["settings"]
        assert settings["executionOrder"] == "v1"
        assert settings["saveExecutionProgress"] == False
        assert settings["saveManualExecutions"] == True
        assert settings["timezone"] == "UTC"
        assert settings["callerPolicy"] == "workflowsFromSameOwner"

    def test_node_type_version_can_be_set(self):
        """Test that nodes can have custom typeVersion"""
        builder = WorkflowBuilder("Type Version Test")
        builder.add_node(
            "n8n-nodes-base.emailSend",
            "Email Node",
            type_version=2,
            parameters={"fromEmail": "test@example.com"}
        )
        workflow = builder.build(validate=False)

        assert workflow["nodes"][0]["typeVersion"] == 2

    def test_multiple_workflows_have_unique_ids(self):
        """Test that each workflow gets unique IDs"""
        builder1 = WorkflowBuilder("Workflow 1")
        builder1.add_trigger("manual", "Start")
        workflow1 = builder1.build(validate=False)

        builder2 = WorkflowBuilder("Workflow 2")
        builder2.add_trigger("manual", "Start")
        workflow2 = builder2.build(validate=False)

        # Each workflow should have different IDs
        assert workflow1["id"] != workflow2["id"]
        assert workflow1["versionId"] != workflow2["versionId"]
        assert workflow1["meta"]["instanceId"] != workflow2["meta"]["instanceId"]


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
