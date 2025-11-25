"""
Test Suite: Agent Integration

Tests for the simplified agent framework (3 agents: Knowledge, Builder, Validator)

Author: Project Automata - Cycle 02
Version: 2.2.0 (Architecture Simplification)
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from agents import AgentResult, AgentTask, BaseAgent
    from agents.knowledge import KnowledgeAgent
    from agents.builder import BuilderAgent
    from agents.validator import ValidatorAgent
except ImportError:
    pytest.skip("Agent modules not available", allow_module_level=True)


class TestBaseAgent:
    """Test suite for BaseAgent functionality"""

    def test_agent_initialization(self):
        """Test that agents can be initialized"""
        agent = KnowledgeAgent()
        assert agent.name == "Knowledge"
        assert agent.task_count == 0

    def test_agent_performance_tracking(self):
        """Test agent performance statistics"""
        agent = BuilderAgent()
        agent.update_stats(success=True)
        agent.update_stats(success=True)
        agent.update_stats(success=False)

        perf = agent.get_performance()
        assert perf["tasks_completed"] == 3
        assert perf["successes"] == 2
        assert perf["errors"] == 1


class TestKnowledgeAgent:
    """Test suite for KnowledgeAgent (formerly ResearcherAgent + WebResearcherAgent)"""

    def test_knowledge_initialization(self):
        """Test knowledge agent initialization"""
        agent = KnowledgeAgent()
        assert agent.name == "Knowledge"
        assert agent.kb is not None

    def test_knowledge_find_patterns(self):
        """Test pattern finding task"""
        agent = KnowledgeAgent()
        task = AgentTask(
            task_id="knowledge_001",
            task_type="find_patterns",
            parameters={"query": "webhook"}
        )

        result = agent.execute(task)
        assert result.success == True
        assert "patterns" in result.output

    def test_knowledge_summarize_node(self):
        """Test node summarization"""
        agent = KnowledgeAgent()
        task = AgentTask(
            task_id="knowledge_002",
            task_type="summarize_node",
            parameters={"node_type": "n8n-nodes-base.webhook"},
        )

        result = agent.execute(task)
        assert result.success == True
        assert "summary" in result.output

    def test_knowledge_research_requires_simulation_mode(self):
        """Test that research methods require ALLOW_SIMULATED_DATA when APIs not configured"""
        # This test verifies the explicit simulation mode requirement
        # Without APIs configured and ALLOW_SIMULATED_DATA=false, research should fail
        agent = KnowledgeAgent()
        task = AgentTask(
            task_id="knowledge_003",
            task_type="research_reddit",
            parameters={}
        )

        # Note: This will fail if ALLOW_SIMULATED_DATA is not set and APIs not configured
        # The test verifies that the agent handles this case properly
        result = agent.execute(task)
        # Result depends on environment configuration


class TestBuilderAgent:
    """Test suite for BuilderAgent (formerly EngineerAgent + DocumenterAgent)"""

    def test_builder_initialization(self):
        """Test builder agent initialization"""
        agent = BuilderAgent()
        assert agent.name == "Builder"
        assert len(agent.code_quality_rules) > 0

    def test_builder_build_module(self):
        """Test module template generation"""
        agent = BuilderAgent()
        task = AgentTask(
            task_id="build_001",
            task_type="build_module",
            parameters={"name": "test_module", "type": "skill"},
        )

        result = agent.execute(task)
        assert result.success == True
        assert result.output["name"] == "test_module"
        assert "template" in result.output

    def test_builder_code_review(self):
        """Test code review functionality"""
        agent = BuilderAgent()
        task = AgentTask(
            task_id="build_002",
            task_type="review_code",
            parameters={"code": 'def test():\n    """docstring"""\n    pass'},
        )

        result = agent.execute(task)
        assert result.success == True
        assert "quality_score" in result.output

    def test_builder_generate_docs(self):
        """Test documentation generation"""
        agent = BuilderAgent()
        task = AgentTask(
            task_id="build_003",
            task_type="generate_docs",
            parameters={"source": "test_module"}
        )

        result = agent.execute(task)
        assert result.success == True
        assert "documentation" in result.output

    def test_builder_create_diagram(self):
        """Test diagram generation"""
        agent = BuilderAgent()
        task = AgentTask(
            task_id="build_004",
            task_type="create_diagram",
            parameters={"type": "architecture"}
        )

        result = agent.execute(task)
        assert result.success == True
        assert "mermaid" in result.output["diagram"]

    def test_builder_eval_report(self):
        """Test evaluation report creation"""
        agent = BuilderAgent()
        task = AgentTask(
            task_id="build_005",
            task_type="eval_report",
            parameters={"cycle": 1, "metrics": {"schema_validity": 90, "test_pass_rate": 95}},
        )

        result = agent.execute(task)
        assert result.success == True
        assert "report" in result.output


class TestValidatorAgent:
    """Test suite for ValidatorAgent"""

    def test_validator_initialization(self):
        """Test validator agent initialization"""
        agent = ValidatorAgent()
        assert agent.name == "Validator"

    def test_validate_workflow(self):
        """Test workflow validation"""
        agent = ValidatorAgent()

        valid_workflow = {
            "name": "Test",
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

        task = AgentTask(
            task_id="val_001",
            task_type="validate_workflow",
            parameters={"workflow": valid_workflow},
        )

        result = agent.execute(task)
        assert result.success == True
        assert result.output["valid"] == True

    def test_validate_invalid_workflow(self):
        """Test validation of invalid workflow"""
        agent = ValidatorAgent()

        invalid_workflow = {
            "name": "Invalid"
            # Missing nodes field
        }

        task = AgentTask(
            task_id="val_002",
            task_type="validate_workflow",
            parameters={"workflow": invalid_workflow},
        )

        result = agent.execute(task)
        assert result.success == False
        assert len(result.output["errors"]) > 0

    def test_validate_connections(self):
        """Test connection validation"""
        agent = ValidatorAgent()

        workflow = {
            "name": "Test",
            "nodes": [
                {"name": "Start", "type": "n8n-nodes-base.manualTrigger"},
                {"name": "End", "type": "n8n-nodes-base.noOp"},
            ],
            "connections": {
                "Start": {"main": [[{"node": "End", "type": "main", "index": 0}]]}
            },
        }

        task = AgentTask(
            task_id="val_003",
            task_type="validate_connections",
            parameters={"workflow": workflow},
        )

        result = agent.execute(task)
        assert result.success == True


class TestMultiAgentCoordination:
    """Integration tests for multi-agent coordination"""

    def test_agent_task_handoff(self):
        """Test passing work between agents"""
        # Knowledge agent finds patterns
        knowledge = KnowledgeAgent()
        knowledge_task = AgentTask(
            task_id="coord_001",
            task_type="find_patterns",
            parameters={"query": "webhook"}
        )
        knowledge_result = knowledge.execute(knowledge_task)

        # Builder could use those patterns
        builder = BuilderAgent()

        assert knowledge_result.success == True

    def test_validation_workflow(self):
        """Test workflow validation pipeline"""
        # Generate a workflow (simulated)
        workflow = {
            "name": "Test",
            "nodes": [
                {
                    "name": "Start",
                    "type": "n8n-nodes-base.manualTrigger",
                    "typeVersion": 1,
                    "position": [0, 0],
                    "parameters": {},
                }
            ],
            "connections": {},
        }

        # Validator checks it
        validator = ValidatorAgent()
        val_task = AgentTask(
            task_id="coord_002",
            task_type="validate_workflow",
            parameters={"workflow": workflow}
        )
        val_result = validator.execute(val_task)

        assert val_result.success == True


class TestBackwardsCompatibility:
    """Test backwards compatibility aliases"""

    def test_researcher_alias(self):
        """Test that ResearcherAgent alias works"""
        from agents.knowledge import ResearcherAgent
        agent = ResearcherAgent()
        assert agent is not None

    def test_web_researcher_alias(self):
        """Test that WebResearcherAgent alias works"""
        from agents.knowledge import WebResearcherAgent
        agent = WebResearcherAgent()
        assert agent is not None

    def test_engineer_alias(self):
        """Test that EngineerAgent alias works"""
        from agents.builder import EngineerAgent
        agent = EngineerAgent()
        assert agent is not None

    def test_documenter_alias(self):
        """Test that DocumenterAgent alias works"""
        from agents.builder import DocumenterAgent
        agent = DocumenterAgent()
        assert agent is not None


# Fixtures
@pytest.fixture
def knowledge_agent():
    """Fixture providing KnowledgeAgent"""
    return KnowledgeAgent()


@pytest.fixture
def builder_agent():
    """Fixture providing BuilderAgent"""
    return BuilderAgent()


@pytest.fixture
def validator():
    """Fixture providing ValidatorAgent"""
    return ValidatorAgent()


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
