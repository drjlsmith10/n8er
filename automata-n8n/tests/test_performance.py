"""
Performance Tests for Project Automata

Tests for:
- Workflow generation speed
- Parsing speed
- Memory usage
- Scalability with increasing workflow complexity

Author: Project Automata - Tester Agent
Version: 1.0.0
Created: 2025-11-20
"""

import json
import logging
import sys
import time
from pathlib import Path
from typing import Tuple

import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from skills.generate_workflow_json import TemplateLibrary, WorkflowBuilder
from skills.nl_prompt_parser import parse_prompt
from skills.parse_n8n_schema import parse_workflow_json

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


class TestWorkflowGenerationPerformance:
    """Performance tests for workflow generation"""

    def test_simple_workflow_generation_speed(self):
        """
        Benchmark: Simple workflow generation (trigger + 1 action)
        Target: <100ms
        """
        builder = WorkflowBuilder("Simple Workflow")

        start_time = time.perf_counter()

        builder.add_trigger("webhook", "Start", {"path": "test"})
        builder.add_node("n8n-nodes-base.noOp", "Action")
        builder.connect("Start", "Action")
        workflow = builder.build(validate=False)

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        logger.info(f"Simple workflow generation: {elapsed_ms:.2f}ms")
        assert elapsed_ms < 100, f"Generation took {elapsed_ms:.2f}ms, expected <100ms"

    def test_complex_workflow_generation_speed(self):
        """
        Benchmark: Complex workflow generation (30 nodes, 30 connections)
        Target: <500ms
        """
        builder = WorkflowBuilder("Complex Workflow")

        start_time = time.perf_counter()

        # Add trigger
        builder.add_trigger("webhook", "Start", {"path": "test"})

        # Add 29 nodes
        for i in range(1, 30):
            builder.add_node(
                "n8n-nodes-base.set",
                f"Node{i}",
                {"values": {"string": [{"name": "field", "value": f"value{i}"}]}},
            )

        # Connect in chain
        prev_node = "Start"
        for i in range(1, 30):
            builder.connect(prev_node, f"Node{i}")
            prev_node = f"Node{i}"

        workflow = builder.build(validate=False)

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        logger.info(f"Complex workflow generation (30 nodes): {elapsed_ms:.2f}ms")
        assert elapsed_ms < 500, f"Generation took {elapsed_ms:.2f}ms, expected <500ms"
        assert len(workflow["nodes"]) == 30

    def test_large_workflow_generation_speed(self):
        """
        Benchmark: Large workflow generation (100 nodes)
        Target: <2000ms
        Stress test for scalability
        """
        builder = WorkflowBuilder("Large Workflow")

        start_time = time.perf_counter()

        # Add trigger
        builder.add_trigger("webhook", "Start", {"path": "test"})

        # Add 99 nodes
        for i in range(1, 100):
            builder.add_node(
                "n8n-nodes-base.set",
                f"Node{i}",
                {"values": {"string": [{"name": "field", "value": f"value{i}"}]}},
            )

        # Connect in chain
        prev_node = "Start"
        for i in range(1, 100):
            builder.connect(prev_node, f"Node{i}")
            prev_node = f"Node{i}"

        workflow = builder.build(validate=False)

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        logger.info(f"Large workflow generation (100 nodes): {elapsed_ms:.2f}ms")
        assert elapsed_ms < 2000, f"Generation took {elapsed_ms:.2f}ms, expected <2000ms"
        assert len(workflow["nodes"]) == 100

    def test_template_generation_speed(self):
        """
        Benchmark: Template-based workflow generation
        Target: <100ms per template
        """
        templates = [
            ("webhook_email", {}),
            ("http_transform", {"url": "https://api.example.com"}),
            ("etl", {}),
            ("api_error_handling", {"api_url": "https://api.example.com"}),
        ]

        for template_name, params in templates:
            start_time = time.perf_counter()

            # Generate based on template name
            if template_name == "webhook_email":
                workflow = TemplateLibrary.webhook_to_email()
            elif template_name == "http_transform":
                workflow = TemplateLibrary.http_request_transform(**params)
            elif template_name == "etl":
                workflow = TemplateLibrary.etl_pipeline()
            elif template_name == "api_error_handling":
                workflow = TemplateLibrary.api_with_error_handling(**params)

            elapsed_ms = (time.perf_counter() - start_time) * 1000

            logger.info(f"Template '{template_name}' generation: {elapsed_ms:.2f}ms")
            assert elapsed_ms < 100, f"Template generation took {elapsed_ms:.2f}ms, expected <100ms"


class TestParsingPerformance:
    """Performance tests for workflow parsing and validation"""

    def test_simple_workflow_parsing_speed(self):
        """
        Benchmark: Parse simple workflow JSON
        Target: <50ms
        """
        builder = WorkflowBuilder("Simple Workflow")
        builder.add_trigger("webhook", "Start", {"path": "test"})
        builder.add_node("n8n-nodes-base.noOp", "Action")
        builder.connect("Start", "Action")
        workflow = builder.build(validate=False)

        start_time = time.perf_counter()
        parsed = parse_workflow_json(workflow, strict=False)
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        logger.info(f"Simple workflow parsing: {elapsed_ms:.2f}ms")
        assert elapsed_ms < 50, f"Parsing took {elapsed_ms:.2f}ms, expected <50ms"
        assert parsed is not None

    def test_complex_workflow_parsing_speed(self):
        """
        Benchmark: Parse complex workflow JSON (30 nodes)
        Target: <200ms
        """
        builder = WorkflowBuilder("Complex Workflow")
        builder.add_trigger("webhook", "Start", {"path": "test"})

        for i in range(1, 30):
            builder.add_node("n8n-nodes-base.set", f"Node{i}", {"values": {}})

        prev_node = "Start"
        for i in range(1, 30):
            builder.connect(prev_node, f"Node{i}")
            prev_node = f"Node{i}"

        workflow = builder.build(validate=False)

        start_time = time.perf_counter()
        parsed = parse_workflow_json(workflow, strict=False)
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        logger.info(f"Complex workflow parsing (30 nodes): {elapsed_ms:.2f}ms")
        assert elapsed_ms < 200, f"Parsing took {elapsed_ms:.2f}ms, expected <200ms"
        assert parsed is not None


class TestNaturalLanguageParsingPerformance:
    """Performance tests for NL parsing"""

    def test_simple_prompt_parsing_speed(self):
        """
        Benchmark: Parse simple NL prompt
        Target: <100ms
        """
        prompt = "Create a webhook that sends data to Slack"

        start_time = time.perf_counter()
        result = parse_prompt(prompt)
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        logger.info(f"Simple prompt parsing: {elapsed_ms:.2f}ms")
        assert elapsed_ms < 100, f"Parsing took {elapsed_ms:.2f}ms, expected <100ms"
        assert result is not None

    def test_complex_prompt_parsing_speed(self):
        """
        Benchmark: Parse complex NL prompt with multiple conditions
        Target: <200ms
        """
        prompt = (
            "When a webhook receives POST data with 'id' and 'email' fields, "
            "validate that email is not empty, if valid save to database, "
            "otherwise send error notification to Slack"
        )

        start_time = time.perf_counter()
        result = parse_prompt(prompt)
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        logger.info(f"Complex prompt parsing: {elapsed_ms:.2f}ms")
        assert elapsed_ms < 200, f"Parsing took {elapsed_ms:.2f}ms, expected <200ms"
        assert result is not None


class TestMemoryUsage:
    """Memory usage tests"""

    def test_workflow_json_size_simple(self):
        """
        Test: JSON size for simple workflow
        Target: <5KB for simple workflow
        """
        builder = WorkflowBuilder("Simple Workflow")
        builder.add_trigger("webhook", "Start", {"path": "test"})
        builder.add_node("n8n-nodes-base.noOp", "Action")
        builder.connect("Start", "Action")
        workflow = builder.build(validate=False)

        json_str = json.dumps(workflow)
        size_kb = len(json_str.encode("utf-8")) / 1024

        logger.info(f"Simple workflow JSON size: {size_kb:.2f}KB")
        assert size_kb < 5, f"Simple workflow JSON is {size_kb:.2f}KB, expected <5KB"

    def test_workflow_json_size_complex(self):
        """
        Test: JSON size for complex workflow (30 nodes)
        Target: <50KB
        """
        builder = WorkflowBuilder("Complex Workflow")
        builder.add_trigger("webhook", "Start", {"path": "test"})

        for i in range(1, 30):
            builder.add_node(
                "n8n-nodes-base.set",
                f"Node{i}",
                {
                    "values": {
                        "string": [
                            {"name": "field1", "value": f"value{i}"},
                            {"name": "field2", "value": f"data{i}"},
                        ]
                    }
                },
            )

        prev_node = "Start"
        for i in range(1, 30):
            builder.connect(prev_node, f"Node{i}")
            prev_node = f"Node{i}"

        workflow = builder.build(validate=False)

        json_str = json.dumps(workflow)
        size_kb = len(json_str.encode("utf-8")) / 1024

        logger.info(f"Complex workflow (30 nodes) JSON size: {size_kb:.2f}KB")
        assert size_kb < 50, f"Complex workflow JSON is {size_kb:.2f}KB, expected <50KB"


class TestScalability:
    """Scalability tests"""

    @pytest.mark.parametrize("node_count", [10, 25, 50, 75, 100])
    def test_workflow_generation_scalability(self, node_count: int):
        """
        Test: Workflow generation scales linearly with node count
        Benchmark different node counts to measure scaling
        """
        builder = WorkflowBuilder(f"Workflow with {node_count} nodes")
        builder.add_trigger("webhook", "Start", {"path": "test"})

        start_time = time.perf_counter()

        for i in range(1, node_count):
            builder.add_node("n8n-nodes-base.set", f"Node{i}", {"values": {}})

        prev_node = "Start"
        for i in range(1, node_count):
            builder.connect(prev_node, f"Node{i}")
            prev_node = f"Node{i}"

        workflow = builder.build(validate=False)

        elapsed_ms = (time.perf_counter() - start_time) * 1000
        ms_per_node = elapsed_ms / node_count

        logger.info(
            f"Workflow with {node_count} nodes: {elapsed_ms:.2f}ms ({ms_per_node:.2f}ms per node)"
        )

        # Should scale roughly linearly, allow up to 10ms per node
        assert (
            ms_per_node < 10
        ), f"Generation scaled to {ms_per_node:.2f}ms/node, expected <10ms/node"


class TestCombinedOperations:
    """Test combined operations (generation + parsing)"""

    def test_roundtrip_performance(self):
        """
        Test: Generate → JSON → Parse roundtrip
        Target: <200ms for simple workflow
        """
        start_time = time.perf_counter()

        # Generate
        builder = WorkflowBuilder("Roundtrip Test")
        builder.add_trigger("webhook", "Start", {"path": "test"})
        builder.add_node("n8n-nodes-base.noOp", "Action")
        builder.connect("Start", "Action")
        workflow = builder.build(validate=False)

        # Convert to JSON and back
        json_str = json.dumps(workflow)
        workflow_loaded = json.loads(json_str)

        # Parse
        parsed = parse_workflow_json(workflow_loaded, strict=False)

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        logger.info(f"Roundtrip (generate → JSON → parse): {elapsed_ms:.2f}ms")
        assert elapsed_ms < 200, f"Roundtrip took {elapsed_ms:.2f}ms, expected <200ms"
        assert parsed is not None


# Performance benchmark summary
# Note: pytest hooks are now in conftest.py for proper registration


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
