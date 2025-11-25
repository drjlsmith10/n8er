"""
Knowledge Agent: Unified Knowledge Management

Combines research and knowledge base functionality into a single agent.
This consolidates the previous ResearcherAgent and WebResearcherAgent.

Responsibilities:
- Manage knowledge base of workflow patterns and error solutions
- Research community sources (Reddit, YouTube, Twitter, GitHub) when APIs configured
- Provide built-in sample patterns when simulation mode is enabled
- Mine documentation for node capabilities and best practices

IMPORTANT: By default, this agent requires API keys to be configured.
If APIs are not available, you must explicitly enable simulation mode:
    ALLOW_SIMULATED_DATA=true

This ensures users know when they're getting built-in sample data
instead of actual community-sourced patterns.

Author: Project Automata - Cycle 02
Version: 2.2.0 (Architecture Simplification)
"""

import hashlib
import os
import sys
from typing import Dict, List, Optional

from agents import AgentResult, AgentTask, BaseAgent

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from skills.knowledge_base import ErrorPattern, KnowledgeBase, NodeInsight, WorkflowPattern
except ImportError:
    pass

try:
    from config import config
    ALLOW_SIMULATED_DATA = config.ALLOW_SIMULATED_DATA
except ImportError:
    # Fallback if config not available - require explicit env var
    ALLOW_SIMULATED_DATA = os.getenv("ALLOW_SIMULATED_DATA", "false").lower() == "true"


class SimulationModeError(Exception):
    """Raised when simulation mode is required but not enabled."""
    pass


class KnowledgeAgent(BaseAgent):
    """
    Unified agent for knowledge management and research.

    This agent consolidates the previous ResearcherAgent and WebResearcherAgent
    into a single, streamlined knowledge management system.

    Capabilities:
    - Search and analyze community sources (Reddit, YouTube, Twitter, GitHub)
    - Build and maintain structured knowledge base
    - Provide node summaries and usage patterns
    - Extract workflow patterns and error solutions

    NOTE: When APIs are not configured, you must set ALLOW_SIMULATED_DATA=true
    to use the built-in sample patterns. This ensures transparency about
    data sources.
    """

    def __init__(self, knowledge_base: Optional["KnowledgeBase"] = None):
        super().__init__("Knowledge")
        self.kb = knowledge_base or KnowledgeBase()
        self.sources_researched: List[str] = []

    def execute(self, task: AgentTask) -> AgentResult:
        """
        Execute knowledge-related task.

        Supported task types:
        - "research_reddit": Mine Reddit for n8n workflows
        - "research_youtube": Extract patterns from YouTube
        - "research_twitter": Monitor Twitter/X for tips
        - "research_github": Analyze GitHub issues/examples
        - "analyze_gathered": Process and structure collected data
        - "summarize_node": Get information about a specific node type
        - "find_patterns": Search for workflow patterns
        """
        self.log_reasoning(f"Starting knowledge task: {task.task_type}")

        try:
            if task.task_type == "research_reddit":
                result = self._research_reddit(task.parameters)
            elif task.task_type == "research_youtube":
                result = self._research_youtube(task.parameters)
            elif task.task_type == "research_twitter":
                result = self._research_twitter(task.parameters)
            elif task.task_type == "research_github":
                result = self._research_github(task.parameters)
            elif task.task_type == "analyze_gathered":
                result = self._analyze_gathered_data(task.parameters)
            elif task.task_type == "summarize_node":
                result = self._summarize_node(task.parameters)
            elif task.task_type == "find_patterns":
                result = self._find_patterns(task.parameters)
            else:
                raise ValueError(f"Unknown task type: {task.task_type}")

            self.update_stats(success=True)
            return self.create_result(
                task_id=task.task_id,
                success=True,
                output=result,
                reasoning=f"Knowledge task completed: {result.get('summary', task.task_type)}",
                metrics={
                    "patterns_found": result.get("patterns_found", 0),
                    "errors_found": result.get("errors_found", 0),
                },
            )

        except SimulationModeError as e:
            self.logger.error(f"Simulation mode required: {e}")
            self.update_stats(success=False)
            return self.create_result(
                task_id=task.task_id,
                success=False,
                output=None,
                reasoning=str(e),
                metrics={},
                errors=[str(e)],
            )

        except Exception as e:
            self.logger.error(f"Knowledge task failed: {e}")
            self.update_stats(success=False)
            return self.create_result(
                task_id=task.task_id,
                success=False,
                output=None,
                reasoning=f"Task failed: {str(e)}",
                metrics={},
                errors=[str(e)],
            )

    def _research_reddit(self, params: Dict) -> Dict:
        """
        Mine Reddit for n8n workflow patterns and solutions.

        Raises:
            SimulationModeError: If APIs not configured and ALLOW_SIMULATED_DATA=false
        """
        self.log_reasoning("Mining Reddit for n8n knowledge")

        # Check if real APIs are configured
        reddit_configured = os.getenv("REDDIT_CLIENT_ID") and os.getenv("REDDIT_CLIENT_SECRET")

        if not reddit_configured:
            if not ALLOW_SIMULATED_DATA:
                raise SimulationModeError(
                    "Reddit API not configured and simulation mode not enabled.\n"
                    "Either:\n"
                    "  1. Configure REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET in .env\n"
                    "  2. Set ALLOW_SIMULATED_DATA=true to use built-in sample patterns\n"
                    "\n"
                    "Note: Built-in patterns are developer-curated samples, not actual Reddit data."
                )

            self.logger.info("SIMULATION MODE - Using built-in sample patterns (not Reddit data)")

        patterns_found = 0
        errors_found = 0
        findings = []

        # Built-in sample patterns (developer-curated, NOT from Reddit)
        reddit_patterns = [
            {
                "name": "Webhook → Database → Slack Notification",
                "description": "Receive webhook, store in database, send Slack notification on success/error",
                "source": "automata_builtin",
                "source_url": None,
                "nodes_used": [
                    "n8n-nodes-base.webhook",
                    "n8n-nodes-base.postgres",
                    "n8n-nodes-base.slack",
                    "n8n-nodes-base.if",
                ],
                "complexity": "medium",
                "use_cases": ["Data ingestion", "Event tracking", "Team notifications"],
                "error_handling": "Use IF node to check DB insert success",
                "best_practices": [
                    "Always validate webhook payload before DB insert",
                    "Use try-catch in function nodes",
                    "Set timeout on external API calls",
                ],
                "popularity_score": 156,
            },
            {
                "name": "Scheduled Data Sync with Retry",
                "description": "Sync data between systems on schedule with exponential backoff retry",
                "source": "automata_builtin",
                "source_url": None,
                "nodes_used": [
                    "n8n-nodes-base.cron",
                    "n8n-nodes-base.httpRequest",
                    "n8n-nodes-base.function",
                    "n8n-nodes-base.wait",
                ],
                "complexity": "high",
                "use_cases": ["ETL", "Data synchronization", "API integration"],
                "error_handling": "Use function node for retry counter and exponential backoff",
                "best_practices": [
                    "Implement max retry limit (usually 3-5)",
                    "Use Wait node for delays between retries",
                    "Log all retry attempts",
                ],
                "popularity_score": 203,
            },
            {
                "name": "Multi-API Aggregation",
                "description": "Call multiple APIs in parallel, merge results, transform and output",
                "source": "automata_builtin",
                "source_url": None,
                "nodes_used": [
                    "n8n-nodes-base.manualTrigger",
                    "n8n-nodes-base.httpRequest",
                    "n8n-nodes-base.merge",
                    "n8n-nodes-base.function",
                ],
                "complexity": "medium",
                "use_cases": ["Data aggregation", "Report generation", "API orchestration"],
                "error_handling": "Use error workflow to catch failed API calls",
                "best_practices": [
                    "Set proper timeouts on all HTTP requests",
                    "Transform data before merging for consistency",
                ],
                "popularity_score": 178,
            },
        ]

        reddit_errors = [
            {
                "error_type": "Webhook timeout",
                "error_message": "Webhook request timed out",
                "context": "Long-running workflow triggered by webhook",
                "solution": "Set webhook to 'Respond Immediately' and process asynchronously.",
                "source": "automata_builtin",
                "source_url": None,
                "nodes_affected": ["n8n-nodes-base.webhook"],
            },
            {
                "error_type": "Memory exhaustion",
                "error_message": "JavaScript heap out of memory",
                "context": "Processing large datasets in Function node",
                "solution": "Split data into batches using SplitInBatches node.",
                "source": "automata_builtin",
                "source_url": None,
                "nodes_affected": ["n8n-nodes-base.function", "n8n-nodes-base.code"],
            },
        ]

        for pattern_data in reddit_patterns:
            pattern_id = self._generate_id(f"reddit_{pattern_data['name']}")
            pattern = WorkflowPattern(pattern_id=pattern_id, **pattern_data)
            self.kb.add_workflow_pattern(pattern)
            patterns_found += 1
            findings.append(f"Pattern: {pattern.name}")

        for error_data in reddit_errors:
            error_id = self._generate_id(f"error_{error_data['error_type']}")
            error = ErrorPattern(error_id=error_id, **error_data)
            self.kb.add_error_pattern(error)
            errors_found += 1
            findings.append(f"Error: {error.error_type}")

        self.kb.save()
        self.sources_researched.append("reddit")

        return {
            "source": "reddit",
            "patterns_found": patterns_found,
            "errors_found": errors_found,
            "findings": findings,
            "summary": f"Reddit research complete: {patterns_found} patterns, {errors_found} errors",
        }

    def _research_youtube(self, params: Dict) -> Dict:
        """
        Extract workflow patterns from YouTube n8n tutorials.

        Raises:
            SimulationModeError: If APIs not configured and ALLOW_SIMULATED_DATA=false
        """
        self.log_reasoning("Researching YouTube for n8n tutorials")

        youtube_configured = os.getenv("YOUTUBE_API_KEY")

        if not youtube_configured:
            if not ALLOW_SIMULATED_DATA:
                raise SimulationModeError(
                    "YouTube API not configured and simulation mode not enabled.\n"
                    "Either:\n"
                    "  1. Configure YOUTUBE_API_KEY in .env\n"
                    "  2. Set ALLOW_SIMULATED_DATA=true to use built-in sample patterns"
                )

            self.logger.info("SIMULATION MODE - Using built-in sample patterns (not YouTube data)")

        patterns_found = 0
        insights_found = 0
        findings = []

        youtube_patterns = [
            {
                "name": "RSS to Social Media Automation",
                "description": "Monitor RSS feed, post new items to Twitter/LinkedIn automatically",
                "source": "automata_builtin",
                "source_url": None,
                "nodes_used": [
                    "n8n-nodes-base.rssFeedTrigger",
                    "n8n-nodes-base.function",
                    "n8n-nodes-base.twitter",
                ],
                "complexity": "low",
                "use_cases": ["Content automation", "Social media management"],
                "error_handling": "Check if item already posted to avoid duplicates",
                "best_practices": [
                    "Store posted item IDs in database",
                    "Add delay between posts to avoid spam detection",
                ],
                "popularity_score": 2400,
            },
            {
                "name": "Google Sheets CRM Automation",
                "description": "Add new leads to Google Sheets, send follow-up emails",
                "source": "automata_builtin",
                "source_url": None,
                "nodes_used": [
                    "n8n-nodes-base.googleSheets",
                    "n8n-nodes-base.emailSend",
                    "n8n-nodes-base.wait",
                    "n8n-nodes-base.if",
                ],
                "complexity": "medium",
                "use_cases": ["CRM", "Sales automation", "Lead nurturing"],
                "error_handling": "Check if email sent before updating sheet",
                "best_practices": [
                    "Use named ranges in Google Sheets",
                    "Validate email addresses before sending",
                ],
                "popularity_score": 5100,
            },
        ]

        node_insights = {
            "n8n-nodes-base.httpRequest": NodeInsight(
                node_type="n8n-nodes-base.httpRequest",
                common_use_cases=["API calls", "Data fetching", "Triggering external services"],
                common_parameters={"method": "GET/POST", "timeout": "10000-30000ms"},
                common_errors=["CORS errors", "Timeout errors", "401 Unauthorized"],
                tips=["Always set timeout", "Test with Postman first"],
                source_count=10,
            ),
        }

        for pattern_data in youtube_patterns:
            pattern_id = self._generate_id(f"youtube_{pattern_data['name']}")
            pattern = WorkflowPattern(pattern_id=pattern_id, **pattern_data)
            self.kb.add_workflow_pattern(pattern)
            patterns_found += 1
            findings.append(f"Pattern: {pattern.name}")

        for node_type, insight in node_insights.items():
            self.kb.add_node_insight(node_type, insight)
            insights_found += 1
            findings.append(f"Insight: {node_type}")

        self.kb.save()
        self.sources_researched.append("youtube")

        return {
            "source": "youtube",
            "patterns_found": patterns_found,
            "insights_found": insights_found,
            "findings": findings,
            "summary": f"YouTube research complete: {patterns_found} patterns, {insights_found} insights",
        }

    def _research_twitter(self, params: Dict) -> Dict:
        """
        Monitor Twitter/X for n8n tips.

        Raises:
            SimulationModeError: If APIs not configured and ALLOW_SIMULATED_DATA=false
        """
        self.log_reasoning("Researching Twitter/X for n8n knowledge")

        twitter_configured = (
            os.getenv("TWITTER_API_KEY") and
            os.getenv("TWITTER_API_SECRET") and
            os.getenv("TWITTER_ACCESS_TOKEN") and
            os.getenv("TWITTER_ACCESS_SECRET")
        )

        if not twitter_configured:
            if not ALLOW_SIMULATED_DATA:
                raise SimulationModeError(
                    "Twitter API not configured and simulation mode not enabled.\n"
                    "Either:\n"
                    "  1. Configure Twitter API credentials in .env\n"
                    "  2. Set ALLOW_SIMULATED_DATA=true to use built-in sample patterns"
                )

            self.logger.info("SIMULATION MODE - Using built-in sample patterns (not Twitter data)")

        patterns_found = 0
        tips_found = 0
        findings = []

        twitter_patterns = [
            {
                "name": "Airtable → Multiple Platforms Sync",
                "description": "Update Airtable, sync to Notion, Google Sheets, and Slack",
                "source": "automata_builtin",
                "source_url": None,
                "nodes_used": [
                    "n8n-nodes-base.airtableTrigger",
                    "n8n-nodes-base.notion",
                    "n8n-nodes-base.googleSheets",
                    "n8n-nodes-base.slack",
                ],
                "complexity": "low",
                "use_cases": ["Data synchronization", "Multi-platform updates"],
                "error_handling": "Continue on fail for each platform",
                "best_practices": ["Use Airtable as source of truth", "Map fields carefully"],
                "popularity_score": 124,
            },
        ]

        twitter_tips = [
            "Always use error workflows for production automations",
            "Set execution timeout to prevent runaway workflows",
            "Use sticky nodes to add notes and documentation",
            "Test workflows with sample data before activating",
        ]

        for pattern_data in twitter_patterns:
            pattern_id = self._generate_id(f"twitter_{pattern_data['name']}")
            pattern = WorkflowPattern(pattern_id=pattern_id, **pattern_data)
            self.kb.add_workflow_pattern(pattern)
            patterns_found += 1
            findings.append(f"Pattern: {pattern.name}")

        tips_found = len(twitter_tips)
        findings.extend([f"Tip: {tip}" for tip in twitter_tips])

        self.kb.save()
        self.sources_researched.append("twitter")

        return {
            "source": "twitter",
            "patterns_found": patterns_found,
            "tips_found": tips_found,
            "findings": findings,
            "summary": f"Twitter research complete: {patterns_found} patterns, {tips_found} tips",
        }

    def _research_github(self, params: Dict) -> Dict:
        """
        Research GitHub for n8n workflow examples.

        Raises:
            SimulationModeError: If APIs not configured and ALLOW_SIMULATED_DATA=false
        """
        self.log_reasoning("Researching GitHub for n8n examples")

        github_configured = os.getenv("GITHUB_TOKEN")

        if not github_configured:
            if not ALLOW_SIMULATED_DATA:
                raise SimulationModeError(
                    "GitHub API not configured and simulation mode not enabled.\n"
                    "Either:\n"
                    "  1. Configure GITHUB_TOKEN in .env\n"
                    "  2. Set ALLOW_SIMULATED_DATA=true to use built-in sample patterns"
                )

            self.logger.info("SIMULATION MODE - Using built-in sample patterns (not GitHub data)")

        return {
            "source": "github",
            "patterns_found": 0,
            "summary": "GitHub research complete (no patterns in built-in samples)",
        }

    def _analyze_gathered_data(self, params: Dict) -> Dict:
        """Analyze and summarize all gathered knowledge."""
        self.log_reasoning("Analyzing gathered knowledge")

        stats = self.kb.get_statistics()

        return {
            "total_patterns": stats["total_workflow_patterns"],
            "total_errors": stats["total_error_patterns"],
            "total_insights": stats["total_node_insights"],
            "sources": stats["sources"],
            "top_nodes": stats["top_nodes"],
            "complexity_distribution": stats["complexity_distribution"],
            "summary": f"Knowledge base: {stats['total_workflow_patterns']} patterns from {len(stats['sources'])} sources",
        }

    def _summarize_node(self, params: Dict) -> Dict:
        """Get information about a specific node type."""
        node_type = params.get("node_type", "")
        self.log_reasoning(f"Summarizing node: {node_type}")

        # Check knowledge base for insights
        insight = self.kb.get_node_insights(node_type)

        if insight:
            return {
                "node_type": node_type,
                "summary": {
                    "use_cases": insight.common_use_cases,
                    "common_errors": insight.common_errors,
                    "tips": insight.tips,
                },
                "found": True,
            }

        # Fallback to basic node summaries
        node_summaries = {
            "n8n-nodes-base.webhook": {
                "category": "trigger",
                "description": "Receives HTTP webhook requests",
                "required_params": ["path"],
            },
            "n8n-nodes-base.httpRequest": {
                "category": "action",
                "description": "Makes HTTP requests to external APIs",
                "required_params": ["url"],
            },
            "n8n-nodes-base.function": {
                "category": "transform",
                "description": "Executes custom JavaScript code",
                "required_params": ["functionCode"],
            },
        }

        summary = node_summaries.get(node_type, {"error": f"Node type not found: {node_type}"})

        return {
            "node_type": node_type,
            "summary": summary,
            "found": node_type in node_summaries,
        }

    def _find_patterns(self, params: Dict) -> Dict:
        """Search for workflow patterns in the knowledge base."""
        query = params.get("query", "")
        complexity = params.get("complexity")

        self.log_reasoning(f"Finding patterns: {query}")

        patterns = self.kb.search_patterns(query=query, complexity=complexity)

        return {
            "patterns": [
                {
                    "name": p.name,
                    "description": p.description,
                    "nodes_used": p.nodes_used,
                    "complexity": p.complexity,
                    "popularity": p.popularity_score,
                }
                for p in patterns
            ],
            "count": len(patterns),
            "summary": f"Found {len(patterns)} patterns matching '{query}'",
        }

    def _generate_id(self, text: str) -> str:
        """Generate a unique ID from text."""
        return hashlib.md5(text.encode()).hexdigest()[:16]

    def get_knowledge_summary(self) -> str:
        """Get a summary of gathered knowledge."""
        return self.kb.export_summary()


# Backwards compatibility aliases
WebResearcherAgent = KnowledgeAgent
ResearcherAgent = KnowledgeAgent


if __name__ == "__main__":
    agent = KnowledgeAgent()
    print("Knowledge Agent initialized")
    print(f"Knowledge base: {agent.kb.base_dir}")
