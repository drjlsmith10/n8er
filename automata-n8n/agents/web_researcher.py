"""
Web Researcher Agent: Community Knowledge Mining

Specialized agent for gathering n8n workflow patterns, error solutions,
and best practices from Reddit, YouTube, Twitter, GitHub, and community forums.

Author: Project Automata - Cycle 02
Version: 2.0.0
"""

import hashlib
import os
import sys
from typing import Dict

from agents import AgentResult, AgentTask, BaseAgent

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from skills.knowledge_base import ErrorPattern, KnowledgeBase, NodeInsight, WorkflowPattern
except ImportError:
    pass


class WebResearcherAgent(BaseAgent):
    """
    Specialized agent for web-based n8n knowledge gathering.

    Capabilities:
    - Search and analyze Reddit discussions
    - Extract workflow patterns from YouTube tutorials
    - Monitor Twitter/X for n8n tips and solutions
    - Parse GitHub issues and examples
    - Build structured knowledge base
    """

    def __init__(self, knowledge_base: "KnowledgeBase" = None):
        super().__init__("WebResearcher")
        self.kb = knowledge_base or KnowledgeBase()
        self.sources_researched = []

    def execute(self, task: AgentTask) -> AgentResult:
        """
        Execute web research task.

        Supported task types:
        - "research_reddit": Mine Reddit for n8n workflows
        - "research_youtube": Extract patterns from YouTube
        - "research_twitter": Monitor Twitter/X for tips
        - "research_github": Analyze GitHub issues/examples
        - "analyze_gathered": Process and structure collected data
        """
        self.log_reasoning(f"Starting web research: {task.task_type}")

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
            else:
                raise ValueError(f"Unknown research type: {task.task_type}")

            self.update_stats(success=True)
            return self.create_result(
                task_id=task.task_id,
                success=True,
                output=result,
                reasoning=f"Web research completed: {result.get('summary')}",
                metrics={
                    "patterns_found": result.get("patterns_found", 0),
                    "errors_found": result.get("errors_found", 0),
                },
            )

        except Exception as e:
            self.logger.error(f"Web research failed: {e}")
            self.update_stats(success=False)
            return self.create_result(
                task_id=task.task_id,
                success=False,
                output=None,
                reasoning=f"Research failed: {str(e)}",
                metrics={},
                errors=[str(e)],
            )

    def _research_reddit(self, params: Dict) -> Dict:
        """
        Mine Reddit for n8n workflow patterns and solutions.

        Strategy:
        - Search r/n8n, r/nocode, r/automation
        - Look for workflow shares, error solutions, best practices
        - Extract patterns and add to knowledge base
        """
        self.log_reasoning("Mining Reddit for n8n knowledge")

        # ⚠️ SIMULATION MODE WARNING ⚠️
        self.logger.warning("=" * 80)
        self.logger.warning("⚠️  USING SIMULATED DATA - Reddit API not configured")
        self.logger.warning("=" * 80)
        self.logger.warning("Real data requires REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET")
        self.logger.warning("Set ENABLE_WEB_RESEARCH=true in .env to use real APIs")
        self.logger.warning("=" * 80)

        # Search queries to use
        # Note: queries variable is prepared for production use
        # In production, would use WebSearch/WebFetch with these queries

        patterns_found = 0
        errors_found = 0
        findings = []

        # SIMULATING Reddit research - using curated sample data
        # For production, integrate with Reddit API via WebSearch/WebFetch

        # Built-in sample patterns (NOT from actual Reddit scraping)
        # These are developer-curated examples based on common community patterns
        reddit_patterns = [
            {
                "name": "Webhook → Database → Slack Notification",
                "description": "Receive webhook, store in database, send Slack notification on success/error",
                "source": "automata_builtin",
                "source_url": None,  # No real source - this is a built-in sample
                "nodes_used": [
                    "n8n-nodes-base.webhook",
                    "n8n-nodes-base.postgres",
                    "n8n-nodes-base.slack",
                    "n8n-nodes-base.if",
                ],
                "complexity": "medium",
                "use_cases": ["Data ingestion", "Event tracking", "Team notifications"],
                "error_handling": "Use IF node to check DB insert success, send different Slack messages",
                "best_practices": [
                    "Always validate webhook payload before DB insert",
                    "Use try-catch in function nodes",
                    "Set timeout on external API calls",
                    "Log errors to separate channel",
                ],
                "popularity_score": 156,
            },
            {
                "name": "Scheduled Data Sync with Retry",
                "description": "Sync data between systems on schedule with exponential backoff retry",
                "source": "automata_builtin",
                "source_url": None,  # No real source - this is a built-in sample
                "nodes_used": [
                    "n8n-nodes-base.cron",
                    "n8n-nodes-base.httpRequest",
                    "n8n-nodes-base.function",
                    "n8n-nodes-base.wait",
                ],
                "complexity": "high",
                "use_cases": ["ETL", "Data synchronization", "API integration"],
                "error_handling": "Use function node to implement retry counter and exponential backoff",
                "best_practices": [
                    "Implement max retry limit (usually 3-5)",
                    "Use Wait node for delays between retries",
                    "Log all retry attempts",
                    "Send alert after max retries exceeded",
                ],
                "popularity_score": 203,
            },
            {
                "name": "Multi-API Aggregation",
                "description": "Call multiple APIs in parallel, merge results, transform and output",
                "source": "automata_builtin",
                "source_url": None,  # No real source - this is a built-in sample
                "nodes_used": [
                    "n8n-nodes-base.manualTrigger",
                    "n8n-nodes-base.httpRequest",
                    "n8n-nodes-base.merge",
                    "n8n-nodes-base.function",
                    "n8n-nodes-base.set",
                ],
                "complexity": "medium",
                "use_cases": ["Data aggregation", "Report generation", "API orchestration"],
                "error_handling": "Use error workflow to catch failed API calls",
                "best_practices": [
                    "Set proper timeouts on all HTTP requests",
                    "Use Merge node mode: 'Keep Key Matches'",
                    "Transform data before merging for consistency",
                    "Handle partial failures gracefully",
                ],
                "popularity_score": 178,
            },
            {
                "name": "Email Processing Pipeline",
                "description": "Monitor email, parse attachments, process data, send results",
                "source": "automata_builtin",
                "source_url": None,  # No real source - this is a built-in sample
                "nodes_used": [
                    "n8n-nodes-base.emailTrigger",
                    "n8n-nodes-base.emailReadImap",
                    "n8n-nodes-base.function",
                    "n8n-nodes-base.spreadsheetFile",
                    "n8n-nodes-base.emailSend",
                ],
                "complexity": "high",
                "use_cases": ["Document processing", "Email automation", "Report handling"],
                "error_handling": "Move failed emails to separate folder, send error notification",
                "best_practices": [
                    "Mark processed emails as read",
                    "Move to processed folder",
                    "Validate file formats before processing",
                    "Keep audit trail of all processed emails",
                ],
                "popularity_score": 142,
            },
        ]

        # Built-in error patterns (NOT from actual Reddit scraping)
        # These are developer-curated examples based on common community issues
        reddit_errors = [
            {
                "error_type": "Webhook timeout",
                "error_message": "Webhook request timed out",
                "context": "Long-running workflow triggered by webhook",
                "solution": "Set webhook to 'Respond Immediately' and process asynchronously. Use Queue node for long operations.",
                "source": "automata_builtin",
                "source_url": None,  # No real source - this is a built-in sample
                "nodes_affected": ["n8n-nodes-base.webhook"],
            },
            {
                "error_type": "Memory exhaustion",
                "error_message": "JavaScript heap out of memory",
                "context": "Processing large datasets in Function node",
                "solution": "Split data into batches using SplitInBatches node. Process smaller chunks instead of entire dataset.",
                "source": "automata_builtin",
                "source_url": None,  # No real source - this is a built-in sample
                "nodes_affected": ["n8n-nodes-base.function", "n8n-nodes-base.code"],
            },
            {
                "error_type": "Rate limiting",
                "error_message": "429 Too Many Requests",
                "context": "Making rapid API calls in loop",
                "solution": "Add Wait node between iterations. Use rate limiter pattern with counter and delay.",
                "source": "automata_builtin",
                "source_url": None,  # No real source - this is a built-in sample
                "nodes_affected": ["n8n-nodes-base.httpRequest"],
            },
            {
                "error_type": "Credentials not found",
                "error_message": "Could not find credentials",
                "context": "Workflow imported from another instance",
                "solution": "Re-create credentials in new instance. Cannot export actual credentials for security.",
                "source": "automata_builtin",
                "source_url": None,  # No real source - this is a built-in sample
                "nodes_affected": ["*"],
            },
        ]

        # Add patterns to knowledge base
        for pattern_data in reddit_patterns:
            pattern_id = self._generate_id(f"reddit_{pattern_data['name']}")
            pattern = WorkflowPattern(pattern_id=pattern_id, **pattern_data)
            self.kb.add_workflow_pattern(pattern)
            patterns_found += 1
            findings.append(f"Pattern: {pattern.name}")

        # Add errors to knowledge base
        for error_data in reddit_errors:
            error_id = self._generate_id(f"reddit_error_{error_data['error_type']}")
            error = ErrorPattern(error_id=error_id, **error_data)
            self.kb.add_error_pattern(error)
            errors_found += 1
            findings.append(f"Error: {error.error_type}")

        # Save knowledge base
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

        Strategy:
        - Search for n8n tutorial videos
        - Analyze descriptions and comments for workflow patterns
        - Extract common use cases and tips
        """
        self.log_reasoning("Researching YouTube for n8n tutorials")

        # ⚠️ SIMULATION MODE WARNING ⚠️
        self.logger.warning("=" * 80)
        self.logger.warning("⚠️  USING SIMULATED DATA - YouTube API not configured")
        self.logger.warning("=" * 80)
        self.logger.warning("Real data requires YOUTUBE_API_KEY")
        self.logger.warning("Set ENABLE_WEB_RESEARCH=true in .env to use real APIs")
        self.logger.warning("=" * 80)

        patterns_found = 0
        insights_found = 0
        findings = []

        # Built-in sample patterns (NOT from actual YouTube scraping)
        # These are developer-curated examples based on common tutorial patterns
        youtube_patterns = [
            {
                "name": "RSS to Social Media Automation",
                "description": "Monitor RSS feed, post new items to Twitter/LinkedIn automatically",
                "source": "automata_builtin",
                "source_url": None,  # No real source - this is a built-in sample
                "nodes_used": [
                    "n8n-nodes-base.rssFeedTrigger",
                    "n8n-nodes-base.function",
                    "n8n-nodes-base.twitter",
                    "n8n-nodes-base.linkedIn",
                ],
                "complexity": "low",
                "use_cases": ["Content automation", "Social media management", "Marketing"],
                "error_handling": "Check if item already posted to avoid duplicates",
                "best_practices": [
                    "Store posted item IDs in database",
                    "Add delay between posts to avoid spam detection",
                    "Truncate long titles to fit character limits",
                    "Add hashtags automatically",
                ],
                "popularity_score": 2400,  # Views
            },
            {
                "name": "GitHub to Discord Notifications",
                "description": "Send Discord notifications for GitHub events (PR, issues, commits)",
                "source": "automata_builtin",
                "source_url": None,  # No real source - this is a built-in sample
                "nodes_used": [
                    "n8n-nodes-base.githubTrigger",
                    "n8n-nodes-base.switch",
                    "n8n-nodes-base.discord",
                    "n8n-nodes-base.function",
                ],
                "complexity": "medium",
                "use_cases": ["DevOps", "Team collaboration", "CI/CD monitoring"],
                "error_handling": "Use Switch node to handle different event types",
                "best_practices": [
                    "Filter events you care about",
                    "Format messages with Discord markdown",
                    "Include direct links to GitHub items",
                    "Use different channels for different event types",
                ],
                "popularity_score": 3200,
            },
            {
                "name": "Google Sheets CRM Automation",
                "description": "Add new leads to Google Sheets, send follow-up emails, update status",
                "source": "automata_builtin",
                "source_url": None,  # No real source - this is a built-in sample
                "nodes_used": [
                    "n8n-nodes-base.googleSheets",
                    "n8n-nodes-base.emailSend",
                    "n8n-nodes-base.wait",
                    "n8n-nodes-base.if",
                ],
                "complexity": "medium",
                "use_cases": ["CRM", "Sales automation", "Lead nurturing"],
                "error_handling": "Check if email sent successfully before updating sheet",
                "best_practices": [
                    "Use named ranges in Google Sheets",
                    "Validate email addresses before sending",
                    "Log all email sends in separate sheet",
                    "Use Wait node for follow-up delays",
                ],
                "popularity_score": 5100,
            },
        ]

        # Node insights from YouTube tutorials
        node_insights = {
            "n8n-nodes-base.httpRequest": NodeInsight(
                node_type="n8n-nodes-base.httpRequest",
                common_use_cases=[
                    "API calls",
                    "Webhooks to external services",
                    "Data fetching",
                    "Triggering external workflows",
                ],
                common_parameters={
                    "method": "GET/POST most common",
                    "authentication": "Bearer Token or API Key",
                    "timeout": "10000-30000ms recommended",
                },
                common_errors=[
                    "CORS errors (use proxy)",
                    "Timeout errors (increase timeout)",
                    "401 Unauthorized (check credentials)",
                ],
                tips=[
                    "Always set timeout to prevent hanging",
                    "Use response format 'autodetect' for flexibility",
                    "Test with Postman first",
                    "Log request/response for debugging",
                ],
                source_count=10,
            ),
            "n8n-nodes-base.function": NodeInsight(
                node_type="n8n-nodes-base.function",
                common_use_cases=[
                    "Data transformation",
                    "Complex logic",
                    "Calculations",
                    "Custom parsing",
                ],
                common_parameters={"functionCode": "JavaScript ES6 supported"},
                common_errors=[
                    "Syntax errors (test code separately)",
                    "Undefined variable (check $json structure)",
                    "Memory issues (process in batches)",
                ],
                tips=[
                    "Return array of items: [{json: {}}]",
                    "Access input with $input.item.json",
                    "Use console.log for debugging (shows in logs)",
                    "Keep functions simple, split complex logic",
                ],
                source_count=15,
            ),
        }

        # Add patterns
        for pattern_data in youtube_patterns:
            pattern_id = self._generate_id(f"youtube_{pattern_data['name']}")
            pattern = WorkflowPattern(pattern_id=pattern_id, **pattern_data)
            self.kb.add_workflow_pattern(pattern)
            patterns_found += 1
            findings.append(f"Pattern: {pattern.name}")

        # Add node insights
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
        Monitor Twitter/X for n8n tips, workflows, and solutions.

        Strategy:
        - Search for #n8n, #automation hashtags
        - Find user-shared workflows
        - Extract quick tips and tricks
        """
        self.log_reasoning("Researching Twitter/X for n8n knowledge")

        # ⚠️ SIMULATION MODE WARNING ⚠️
        self.logger.warning("=" * 80)
        self.logger.warning("⚠️  USING SIMULATED DATA - Twitter/X API not configured")
        self.logger.warning("=" * 80)
        self.logger.warning("Real data requires TWITTER_API_KEY and related credentials")
        self.logger.warning("Set ENABLE_WEB_RESEARCH=true in .env to use real APIs")
        self.logger.warning("=" * 80)

        patterns_found = 0
        tips_found = 0
        findings = []

        # Built-in sample patterns (NOT from actual Twitter scraping)
        # These are developer-curated examples based on common use cases
        twitter_patterns = [
            {
                "name": "Twitter Monitoring & Auto-Reply",
                "description": "Monitor mentions, analyze sentiment, auto-reply based on content",
                "source": "automata_builtin",
                "source_url": None,  # No real source - this is a built-in sample
                "nodes_used": [
                    "n8n-nodes-base.twitterTrigger",
                    "n8n-nodes-base.sentimentAnalysis",
                    "n8n-nodes-base.if",
                    "n8n-nodes-base.twitter",
                ],
                "complexity": "medium",
                "use_cases": ["Social media management", "Customer service", "Brand monitoring"],
                "error_handling": "Rate limit handling with queue",
                "best_practices": [
                    "Filter out retweets and spam",
                    "Don't auto-reply to everything (spam detection)",
                    "Add human review step for sensitive replies",
                    "Track conversation threads",
                ],
                "popularity_score": 89,  # Retweets
            },
            {
                "name": "Airtable → Multiple Platforms Sync",
                "description": "Update Airtable, sync to Notion, Google Sheets, and Slack",
                "source": "automata_builtin",
                "source_url": None,  # No real source - this is a built-in sample
                "nodes_used": [
                    "n8n-nodes-base.airtableTrigger",
                    "n8n-nodes-base.notion",
                    "n8n-nodes-base.googleSheets",
                    "n8n-nodes-base.slack",
                ],
                "complexity": "low",
                "use_cases": [
                    "Data synchronization",
                    "Multi-platform updates",
                    "Team coordination",
                ],
                "error_handling": "Continue on fail for each platform",
                "best_practices": [
                    "Use Airtable as source of truth",
                    "Map fields carefully between platforms",
                    "Add timestamp tracking",
                    "Test with small dataset first",
                ],
                "popularity_score": 124,
            },
        ]

        # Common tips from Twitter
        twitter_tips = [
            "Always use error workflows for production automations",
            "Set execution timeout to prevent runaway workflows",
            "Use sticky nodes to add notes and documentation",
            "Enable workflow versioning to track changes",
            "Test workflows with sample data before activating",
            "Use environment variables for credentials",
            "Split complex workflows into sub-workflows",
            "Add monitoring/alerting for critical workflows",
        ]

        # Add patterns
        for pattern_data in twitter_patterns:
            pattern_id = self._generate_id(f"twitter_{pattern_data['name']}")
            pattern = WorkflowPattern(pattern_id=pattern_id, **pattern_data)
            self.kb.add_workflow_pattern(pattern)
            patterns_found += 1
            findings.append(f"Pattern: {pattern.name}")

        # Store tips as best practices
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
        """Research GitHub for n8n workflow examples and issues"""
        self.log_reasoning("Researching GitHub for n8n examples")

        # ⚠️ SIMULATION MODE WARNING ⚠️
        self.logger.warning("=" * 80)
        self.logger.warning("⚠️  USING SIMULATED DATA - GitHub API not configured")
        self.logger.warning("=" * 80)
        self.logger.warning("Real data requires GITHUB_TOKEN")
        self.logger.warning("Set ENABLE_WEB_RESEARCH=true in .env to use real APIs")
        self.logger.warning("=" * 80)

        # Placeholder for GitHub research
        # In production, would search n8n-io/n8n repo for workflow examples

        return {
            "source": "github",
            "patterns_found": 0,
            "summary": "GitHub research (SIMULATED - API not configured)",
        }

    def _analyze_gathered_data(self, params: Dict) -> Dict:
        """Analyze and summarize all gathered knowledge"""
        self.log_reasoning("Analyzing gathered knowledge")

        stats = self.kb.get_statistics()

        analysis = {
            "total_patterns": stats["total_workflow_patterns"],
            "total_errors": stats["total_error_patterns"],
            "total_insights": stats["total_node_insights"],
            "sources": stats["sources"],
            "top_nodes": stats["top_nodes"],
            "complexity_distribution": stats["complexity_distribution"],
            "summary": f"Knowledge base contains {stats['total_workflow_patterns']} patterns from {len(stats['sources'])} sources",
        }

        return analysis

    def _generate_id(self, text: str) -> str:
        """Generate a unique ID from text"""
        return hashlib.md5(text.encode()).hexdigest()[:16]

    def get_knowledge_summary(self) -> str:
        """Get a summary of gathered knowledge"""
        return self.kb.export_summary()


if __name__ == "__main__":
    # Test the web researcher
    agent = WebResearcherAgent()
    print("Web Researcher Agent initialized")
    print(f"Knowledge base: {agent.kb.base_dir}")
