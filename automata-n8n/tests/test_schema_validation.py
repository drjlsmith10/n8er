"""
Test Suite: Schema Validation

Tests for parse_n8n_schema.py module

Author: Project Automata - Tester Agent
Version: 1.0.0
"""

import json
import os
import sys

import pytest

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from skills.parse_n8n_schema import (
        N8nConnection,
        N8nNode,
        N8nSchemaParser,
        parse_workflow_file,
        parse_workflow_json,
    )
except ImportError:
    pytest.skip("parse_n8n_schema module not available", allow_module_level=True)


class TestN8nSchemaParser:
    """Test suite for N8nSchemaParser class"""

    def test_parser_initialization(self):
        """Test parser can be initialized"""
        parser = N8nSchemaParser(strict_mode=True)
        assert parser.strict_mode == True
        assert parser.errors == []
        assert parser.warnings == []

    def test_parse_valid_workflow(self):
        """Test parsing a valid minimal workflow"""
        workflow = {
            "name": "Test Workflow",
            "nodes": [
                {
                    "name": "Start",
                    "type": "n8n-nodes-base.manualTrigger",
                    "typeVersion": 1,
                    "position": [240, 300],
                    "parameters": {},
                }
            ],
            "connections": {},
        }

        parser = N8nSchemaParser(strict_mode=False)
        result = parser.parse_json(workflow)

        assert result is not None
        assert result.metadata.name == "Test Workflow"
        assert len(result.nodes) == 1
        assert "Start" in result.nodes

    def test_parse_missing_nodes_field(self):
        """Test parsing workflow without nodes field"""
        workflow = {"name": "Invalid Workflow"}

        parser = N8nSchemaParser(strict_mode=True)
        result = parser.parse_json(workflow)

        assert result is None
        assert len(parser.errors) > 0

    def test_node_is_trigger_detection(self):
        """Test trigger node detection"""
        node = N8nNode(
            id="trigger1",
            name="Webhook",
            type="n8n-nodes-base.webhook",
            type_version=1,
            position=(100, 100),
            parameters={},
        )

        assert node.is_trigger() == True

    def test_workflow_with_connections(self):
        """Test parsing workflow with connections"""
        workflow = {
            "name": "Connected Workflow",
            "nodes": [
                {
                    "name": "Trigger",
                    "type": "n8n-nodes-base.manualTrigger",
                    "typeVersion": 1,
                    "position": [240, 300],
                    "parameters": {},
                },
                {
                    "name": "Action",
                    "type": "n8n-nodes-base.noOp",
                    "typeVersion": 1,
                    "position": [580, 300],
                    "parameters": {},
                },
            ],
            "connections": {
                "Trigger": {"main": [[{"node": "Action", "type": "main", "index": 0}]]}
            },
        }

        parser = N8nSchemaParser(strict_mode=False)
        result = parser.parse_json(workflow)

        assert result is not None
        assert len(result.connections) == 1
        assert result.connections[0].source_node == "Trigger"
        assert result.connections[0].target_node == "Action"

    def test_circular_dependency_detection(self):
        """Test detection of circular dependencies"""
        workflow = {
            "name": "Circular Workflow",
            "nodes": [
                {
                    "name": "A",
                    "type": "n8n-nodes-base.manualTrigger",
                    "typeVersion": 1,
                    "position": [0, 0],
                    "parameters": {},
                },
                {
                    "name": "B",
                    "type": "n8n-nodes-base.noOp",
                    "typeVersion": 1,
                    "position": [100, 0],
                    "parameters": {},
                },
                {
                    "name": "C",
                    "type": "n8n-nodes-base.noOp",
                    "typeVersion": 1,
                    "position": [200, 0],
                    "parameters": {},
                },
            ],
            "connections": {
                "A": {"main": [[{"node": "B", "type": "main", "index": 0}]]},
                "B": {"main": [[{"node": "C", "type": "main", "index": 0}]]},
                "C": {"main": [[{"node": "B", "type": "main", "index": 0}]]},  # Creates cycle
            },
        }

        parser = N8nSchemaParser(strict_mode=False)
        result = parser.parse_json(workflow)

        if result:
            has_cycle, cycle_path = result.has_circular_dependencies()
            assert has_cycle == True

    def test_trigger_nodes_identification(self):
        """Test identification of trigger nodes"""
        workflow = {
            "name": "Multi-Trigger Workflow",
            "nodes": [
                {
                    "name": "Webhook",
                    "type": "n8n-nodes-base.webhook",
                    "typeVersion": 1,
                    "position": [0, 0],
                    "parameters": {},
                },
                {
                    "name": "Cron",
                    "type": "n8n-nodes-base.cron",
                    "typeVersion": 1,
                    "position": [0, 100],
                    "parameters": {},
                },
                {
                    "name": "Action",
                    "type": "n8n-nodes-base.noOp",
                    "typeVersion": 1,
                    "position": [200, 0],
                    "parameters": {},
                },
            ],
            "connections": {},
        }

        parser = N8nSchemaParser(strict_mode=False)
        result = parser.parse_json(workflow)

        assert result is not None
        assert len(result.trigger_nodes) == 2
        assert "Webhook" in result.trigger_nodes
        assert "Cron" in result.trigger_nodes


class TestWorkflowParsing:
    """Test suite for workflow parsing functions"""

    def test_parse_sample_workflows(self):
        """Test parsing all sample workflows"""
        workflow_dir = os.path.join(os.path.dirname(__file__), "..", "workflows")

        if not os.path.exists(workflow_dir):
            pytest.skip("Workflow directory not found")

        sample_files = [
            "sample_webhook_email.json",
            "sample_data_transform.json",
            "sample_api_integration.json",
        ]

        for filename in sample_files:
            filepath = os.path.join(workflow_dir, filename)
            if os.path.exists(filepath):
                result = parse_workflow_file(filepath, strict=False)
                assert result is not None, f"Failed to parse {filename}"
                assert result.node_count > 0, f"{filename} has no nodes"


class TestNodeClassification:
    """Test suite for node classification"""

    def test_trigger_classification(self):
        """Test trigger node classification"""
        node = N8nNode(
            id="1",
            name="Test",
            type="n8n-nodes-base.webhook",
            type_version=1,
            position=(0, 0),
            parameters={},
        )
        assert node.is_trigger() == True

    def test_action_classification(self):
        """Test action node classification"""
        node = N8nNode(
            id="1",
            name="Test",
            type="n8n-nodes-base.httpRequest",
            type_version=1,
            position=(0, 0),
            parameters={},
        )
        assert node.is_trigger() == False


# Test fixtures
@pytest.fixture
def valid_workflow():
    """Fixture providing a valid test workflow"""
    return {
        "name": "Test Workflow",
        "nodes": [
            {
                "name": "Start",
                "type": "n8n-nodes-base.manualTrigger",
                "typeVersion": 1,
                "position": [240, 300],
                "parameters": {},
            }
        ],
        "connections": {},
    }


@pytest.fixture
def parser():
    """Fixture providing a parser instance"""
    return N8nSchemaParser(strict_mode=False)


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
