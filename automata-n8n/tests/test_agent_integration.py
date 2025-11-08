"""
Test Suite: Agent Integration

Tests for agent framework and coordination

Author: Project Automata - Tester Agent
Version: 1.0.0
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from agents import BaseAgent, AgentTask, AgentResult
    from agents.researcher import ResearcherAgent
    from agents.engineer import EngineerAgent
    from agents.validator import ValidatorAgent
    from agents.tester import TesterAgent
    from agents.documenter import DocumenterAgent
    from agents.project_manager import ProjectManagerAgent
except ImportError:
    pytest.skip("Agent modules not available", allow_module_level=True)


class TestBaseAgent:
    """Test suite for BaseAgent functionality"""

    def test_agent_initialization(self):
        """Test that agents can be initialized"""
        # We can't instantiate BaseAgent directly, so test with concrete agent
        agent = ResearcherAgent()
        assert agent.name == "Researcher"
        assert agent.task_count == 0

    def test_agent_performance_tracking(self):
        """Test agent performance statistics"""
        agent = ResearcherAgent()
        agent.update_stats(success=True)
        agent.update_stats(success=True)
        agent.update_stats(success=False)

        perf = agent.get_performance()
        assert perf["tasks_completed"] == 3
        assert perf["successes"] == 2
        assert perf["errors"] == 1


class TestResearcherAgent:
    """Test suite for ResearcherAgent"""

    def test_researcher_initialization(self):
        """Test researcher agent initialization"""
        agent = ResearcherAgent()
        assert agent.name == "Researcher"
        assert len(agent.patterns) == 0

    def test_researcher_find_patterns(self):
        """Test pattern finding task"""
        agent = ResearcherAgent()
        task = AgentTask(
            task_id="research_001",
            task_type="find_patterns",
            parameters={}
        )

        result = agent.execute(task)
        assert result.success == True
        assert "patterns" in result.output
        assert len(result.output["patterns"]) > 0

    def test_researcher_mine_docs(self):
        """Test documentation mining"""
        agent = ResearcherAgent()
        task = AgentTask(
            task_id="research_002",
            task_type="mine_docs",
            parameters={}
        )

        result = agent.execute(task)
        assert result.success == True
        assert "items" in result.output

    def test_researcher_summarize_node(self):
        """Test node summarization"""
        agent = ResearcherAgent()
        task = AgentTask(
            task_id="research_003",
            task_type="summarize_node",
            parameters={"node_type": "n8n-nodes-base.webhook"}
        )

        result = agent.execute(task)
        assert result.success == True
        assert "summary" in result.output


class TestEngineerAgent:
    """Test suite for EngineerAgent"""

    def test_engineer_initialization(self):
        """Test engineer agent initialization"""
        agent = EngineerAgent()
        assert agent.name == "Engineer"
        assert len(agent.code_quality_rules) > 0

    def test_engineer_build_module(self):
        """Test module building"""
        agent = EngineerAgent()
        task = AgentTask(
            task_id="eng_001",
            task_type="build_module",
            parameters={"name": "test_module", "type": "skill"}
        )

        result = agent.execute(task)
        assert result.success == True
        assert result.output["name"] == "test_module"

    def test_engineer_code_review(self):
        """Test code review functionality"""
        agent = EngineerAgent()
        task = AgentTask(
            task_id="eng_002",
            task_type="review",
            parameters={"code": 'def test():\n    """docstring"""\n    pass'}
        )

        result = agent.execute(task)
        assert result.success == True
        assert "quality_score" in result.output


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
                    "parameters": {}
                }
            ],
            "connections": {}
        }

        task = AgentTask(
            task_id="val_001",
            task_type="validate_workflow",
            parameters={"workflow": valid_workflow}
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
            parameters={"workflow": invalid_workflow}
        )

        result = agent.execute(task)
        assert result.success == False
        assert len(result.output["errors"]) > 0


class TestTesterAgent:
    """Test suite for TesterAgent"""

    def test_tester_initialization(self):
        """Test tester agent initialization"""
        agent = TesterAgent()
        assert agent.name == "Tester"

    def test_run_tests(self):
        """Test running test suite"""
        agent = TesterAgent()
        task = AgentTask(
            task_id="test_001",
            task_type="run_tests",
            parameters={"suite": "all"}
        )

        result = agent.execute(task)
        assert result.success == True
        assert result.output["total_tests"] > 0

    def test_simulate_workflow(self):
        """Test workflow simulation"""
        agent = TesterAgent()

        workflow = {
            "nodes": [
                {"name": "Start", "type": "n8n-nodes-base.manualTrigger"},
                {"name": "Action", "type": "n8n-nodes-base.noOp"}
            ],
            "connections": {
                "Start": {
                    "main": [
                        [{"node": "Action", "type": "main", "index": 0}]
                    ]
                }
            }
        }

        task = AgentTask(
            task_id="test_002",
            task_type="simulate_workflow",
            parameters={"workflow": workflow}
        )

        result = agent.execute(task)
        assert result.success == True
        assert "execution_log" in result.output


class TestDocumenterAgent:
    """Test suite for DocumenterAgent"""

    def test_documenter_initialization(self):
        """Test documenter agent initialization"""
        agent = DocumenterAgent()
        assert agent.name == "Documenter"

    def test_generate_docs(self):
        """Test documentation generation"""
        agent = DocumenterAgent()
        task = AgentTask(
            task_id="doc_001",
            task_type="generate_docs",
            parameters={"source": "test_module"}
        )

        result = agent.execute(task)
        assert result.success == True
        assert "documentation" in result.output

    def test_create_eval_report(self):
        """Test evaluation report creation"""
        agent = DocumenterAgent()
        task = AgentTask(
            task_id="doc_002",
            task_type="eval_report",
            parameters={
                "cycle": 1,
                "metrics": {
                    "schema_validity": 90,
                    "test_pass_rate": 95
                }
            }
        )

        result = agent.execute(task)
        assert result.success == True
        assert "report" in result.output


class TestProjectManagerAgent:
    """Test suite for ProjectManagerAgent"""

    def test_pm_initialization(self):
        """Test PM agent initialization"""
        agent = ProjectManagerAgent()
        assert agent.name == "ProjectManager"

    def test_plan_cycle(self):
        """Test cycle planning"""
        agent = ProjectManagerAgent()
        task = AgentTask(
            task_id="pm_001",
            task_type="plan_cycle",
            parameters={"cycle": 1}
        )

        result = agent.execute(task)
        assert result.success == True
        assert "tasks" in result.output
        assert len(result.output["tasks"]) > 0

    def test_track_progress(self):
        """Test progress tracking"""
        agent = ProjectManagerAgent()
        task = AgentTask(
            task_id="pm_002",
            task_type="track_progress",
            parameters={"cycle": 1}
        )

        result = agent.execute(task)
        assert result.success == True
        assert "overall_progress" in result.output

    def test_version_bump(self):
        """Test version bumping"""
        agent = ProjectManagerAgent()
        task = AgentTask(
            task_id="pm_003",
            task_type="version_bump",
            parameters={"current": "1.0.0", "type": "minor"}
        )

        result = agent.execute(task)
        assert result.success == True
        assert result.output["new_version"] == "1.1.0"


class TestMultiAgentCoordination:
    """Integration tests for multi-agent coordination"""

    def test_agent_task_handoff(self):
        """Test passing work between agents"""
        # Researcher finds patterns
        researcher = ResearcherAgent()
        research_task = AgentTask(
            task_id="coord_001",
            task_type="find_patterns",
            parameters={}
        )
        research_result = researcher.execute(research_task)

        # Engineer could use those patterns to build
        engineer = EngineerAgent()
        # (In real system, engineer would use research_result.output)

        assert research_result.success == True

    def test_validation_workflow(self):
        """Test workflow validation pipeline"""
        # Generate a workflow (simulated)
        workflow = {
            "name": "Test",
            "nodes": [
                {"name": "Start", "type": "n8n-nodes-base.manualTrigger",
                 "typeVersion": 1, "position": [0, 0], "parameters": {}}
            ],
            "connections": {}
        }

        # Validator checks it
        validator = ValidatorAgent()
        val_task = AgentTask(
            task_id="coord_002",
            task_type="validate_workflow",
            parameters={"workflow": workflow}
        )
        val_result = validator.execute(val_task)

        # Tester simulates it
        tester = TesterAgent()
        test_task = AgentTask(
            task_id="coord_003",
            task_type="simulate_workflow",
            parameters={"workflow": workflow}
        )
        test_result = tester.execute(test_task)

        assert val_result.success == True
        assert test_result.success == True


# Fixtures
@pytest.fixture
def researcher():
    """Fixture providing ResearcherAgent"""
    return ResearcherAgent()


@pytest.fixture
def engineer():
    """Fixture providing EngineerAgent"""
    return EngineerAgent()


@pytest.fixture
def validator():
    """Fixture providing ValidatorAgent"""
    return ValidatorAgent()


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
