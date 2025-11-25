"""
Keyword Pattern Matcher (formerly NLPromptParser)

Matches workflow descriptions to templates using keyword-based pattern matching.

IMPORTANT: This is NOT natural language understanding. It uses simple keyword
matching to identify triggers, actions, and suggest templates. It works well
for predefined phrases but may not understand complex or novel descriptions.

How it works:
- Searches prompt for predefined keywords (e.g., "webhook", "email", "slack")
- Counts matches to score trigger types and actions
- Suggests templates based on keyword combinations
- Does NOT use AI/ML or semantic understanding

Limitations:
- Only works well with prompts using expected keywords
- Cannot understand context or nuance
- May suggest wrong template for ambiguous descriptions
- Accuracy depends on how closely prompt matches keyword patterns

Author: Project Automata - Cycle 02
Version: 2.1.0 (Honest Naming Update)
"""

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from skills.knowledge_base import KnowledgeBase, WorkflowPattern


@dataclass
class ParsedIntent:
    """Represents the parsed user intent"""

    trigger_type: str  # webhook, scheduled, manual, email, etc.
    actions: List[str]  # List of actions to perform
    data_flow: str  # simple, transform, aggregate, branch
    error_handling: bool  # Whether error handling is required
    suggested_template: Optional[str] = None
    confidence: float = 0.0
    matched_patterns: List[WorkflowPattern] = None


class KeywordPatternMatcher:
    """
    Matches workflow descriptions to templates using keyword patterns.

    NOTE: This is keyword matching, NOT natural language understanding.
    It counts occurrences of predefined keywords to score matches.

    What it does:
    - Scans for trigger keywords (webhook, schedule, email, etc.)
    - Scans for action keywords (send email, save to database, etc.)
    - Suggests templates based on keyword combinations
    - Extracts parameters using regex patterns

    What it does NOT do:
    - Understand context or meaning
    - Handle synonyms or paraphrasing
    - Learn from new phrases
    - Provide semantic understanding

    Accuracy: Works well for prompts using expected keywords (~85% on test set).
    Novel or complex descriptions may not match correctly.
    """

    def __init__(self, knowledge_base: Optional[KnowledgeBase] = None):
        """Initialize parser with optional knowledge base"""
        self.kb = knowledge_base or KnowledgeBase()

        # Trigger keywords
        self.trigger_keywords = {
            "webhook": ["webhook", "http request", "api call", "receive data", "incoming"],
            "scheduled": ["every", "daily", "hourly", "schedule", "cron", "periodic"],
            "manual": ["manual", "button", "on demand", "when i click"],
            "email": ["when email", "email arrives", "new email", "email received"],
            "rss": ["rss", "feed", "blog posts", "news"],
            "database": ["database change", "new row", "database trigger"],
            "file": ["file upload", "new file", "file arrives"],
        }

        # Action keywords
        self.action_keywords = {
            "send_email": ["send email", "email to", "notify via email"],
            "slack": ["slack", "send message", "notify team", "slack notification"],
            "database": ["save to database", "store in", "insert into", "update database"],
            "http_request": ["call api", "http request", "fetch from", "post to"],
            "transform": ["transform", "convert", "parse", "extract", "map"],
            "filter": ["filter", "only if", "when", "if condition"],
            "aggregate": ["combine", "merge", "aggregate", "join"],
            "wait": ["wait", "delay", "pause", "schedule for later"],
        }

        # Data flow patterns
        self.flow_patterns = {
            "simple": ["simple", "basic", "straightforward", "direct"],
            "transform": ["transform", "etl", "process", "convert"],
            "branch": ["if", "conditional", "branch", "based on"],
            "loop": ["for each", "loop", "iterate", "repeat"],
            "aggregate": ["combine", "merge", "multiple", "parallel"],
        }

    def parse(self, prompt: str) -> ParsedIntent:
        """
        Parse natural language prompt into workflow intent.

        Args:
            prompt: Natural language description of desired workflow

        Returns:
            ParsedIntent with extracted information
        """
        prompt_lower = prompt.lower()

        # Identify trigger
        trigger = self._identify_trigger(prompt_lower)

        # Extract actions
        actions = self._extract_actions(prompt_lower)

        # Determine data flow
        flow = self._determine_flow(prompt_lower)

        # Check for error handling requirements
        error_handling = self._needs_error_handling(prompt_lower)

        # Find matching patterns from knowledge base
        matched_patterns = self._match_patterns(prompt_lower, trigger, actions)

        # Suggest template
        template, confidence = self._suggest_template(trigger, actions, flow, matched_patterns)

        return ParsedIntent(
            trigger_type=trigger,
            actions=actions,
            data_flow=flow,
            error_handling=error_handling,
            suggested_template=template,
            confidence=confidence,
            matched_patterns=matched_patterns,
        )

    def _identify_trigger(self, prompt: str) -> str:
        """Identify the trigger type from prompt"""
        # Score each trigger type
        scores = {}
        for trigger_type, keywords in self.trigger_keywords.items():
            score = sum(1 for keyword in keywords if keyword in prompt)
            if score > 0:
                scores[trigger_type] = score

        if not scores:
            return "manual"  # Default to manual trigger

        # Return trigger with highest score
        return max(scores, key=scores.get)

    def _extract_actions(self, prompt: str) -> List[str]:
        """Extract actions from prompt"""
        actions = []
        for action_type, keywords in self.action_keywords.items():
            if any(keyword in prompt for keyword in keywords):
                actions.append(action_type)

        return actions if actions else ["transform"]  # Default action

    def _determine_flow(self, prompt: str) -> str:
        """Determine data flow pattern"""
        scores = {}
        for flow_type, keywords in self.flow_patterns.items():
            score = sum(1 for keyword in keywords if keyword in prompt)
            if score > 0:
                scores[flow_type] = score

        if not scores:
            return "simple"

        return max(scores, key=scores.get)

    def _needs_error_handling(self, prompt: str) -> bool:
        """Check if error handling is required"""
        error_keywords = [
            "error",
            "fail",
            "retry",
            "fallback",
            "handle errors",
            "if fails",
            "on error",
            "catch",
        ]
        return any(keyword in prompt for keyword in error_keywords)

    def _match_patterns(
        self, prompt: str, trigger: str, actions: List[str]
    ) -> List[WorkflowPattern]:
        """Find matching patterns from knowledge base"""
        # Search knowledge base for relevant patterns
        all_patterns = list(self.kb.workflow_patterns.values())

        scored_patterns = []
        for pattern in all_patterns:
            score = 0

            # Check trigger match
            if any(trigger in node.lower() for node in pattern.nodes_used):
                score += 3

            # Check action matches
            for action in actions:
                if any(action in node.lower() for node in pattern.nodes_used):
                    score += 2

            # Check description match
            prompt_words = set(prompt.split())
            desc_words = set(pattern.description.lower().split())
            overlap = len(prompt_words & desc_words)
            score += overlap * 0.5

            if score > 0:
                scored_patterns.append((pattern, score))

        # Sort by score and return top 3
        scored_patterns.sort(key=lambda x: x[1], reverse=True)
        return [p[0] for p in scored_patterns[:3]]

    def _suggest_template(
        self, trigger: str, actions: List[str], flow: str, matched_patterns: List[WorkflowPattern]
    ) -> Tuple[str, float]:
        """
        Suggest best template based on intent.

        Returns: (template_name, confidence_score)
        """
        # Use matched patterns if available
        if matched_patterns:
            top_pattern = matched_patterns[0]

            # Map known patterns to templates
            pattern_to_template = {
                "Webhook → Database → Slack Notification": "webhook_db_slack",
                "Scheduled Data Sync with Retry": "scheduled_sync_retry",
                "RSS to Social Media Automation": "rss_social",
                "Google Sheets CRM Automation": "sheets_crm",
                "Multi-API Aggregation": "multi_api",
            }

            if top_pattern.name in pattern_to_template:
                return pattern_to_template[top_pattern.name], 0.85

        # Rule-based template selection
        if trigger == "webhook" and "slack" in actions and "database" in actions:
            return "webhook_db_slack", 0.75

        if trigger == "scheduled" and "http_request" in actions:
            return "scheduled_sync_retry", 0.70

        if trigger == "rss" and any(a in actions for a in ["slack", "http_request"]):
            return "rss_social", 0.70

        if "database" in actions and "send_email" in actions:
            return "sheets_crm", 0.65

        if flow == "aggregate" and "http_request" in actions:
            return "multi_api", 0.70

        # Default fallback based on trigger
        defaults = {
            "webhook": "webhook_email",
            "scheduled": "scheduled_sync_retry",
            "manual": "http_transform",
        }

        return defaults.get(trigger, "http_transform"), 0.50

    def extract_parameters(self, prompt: str) -> Dict:
        """
        Extract specific parameters from prompt.

        Examples:
        - URLs: https://api.example.com/endpoint
        - Email addresses: user@example.com
        - Channels: #slack-channel
        - Time intervals: every hour, daily
        """
        params = {}

        # Extract URLs
        url_pattern = r"https?://[^\s]+"
        urls = re.findall(url_pattern, prompt)
        if urls:
            params["urls"] = urls

        # Extract emails
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        emails = re.findall(email_pattern, prompt)
        if emails:
            params["emails"] = emails

        # Extract Slack channels
        channel_pattern = r"#[\w-]+"
        channels = re.findall(channel_pattern, prompt)
        if channels:
            params["slack_channels"] = channels

        # Extract time intervals
        time_patterns = {
            "hourly": r"\bevery hour\b|\bhourly\b",
            "daily": r"\bevery day\b|\bdaily\b",
            "weekly": r"\bevery week\b|\bweekly\b",
        }

        for interval, pattern in time_patterns.items():
            if re.search(pattern, prompt.lower()):
                params["schedule"] = interval

        return params

    def generate_workflow_spec(self, prompt: str) -> Dict:
        """
        Generate complete workflow specification from prompt.

        Returns structured spec ready for WorkflowBuilder.
        """
        intent = self.parse(prompt)
        params = self.extract_parameters(prompt)

        spec = {
            "name": self._generate_name(prompt),
            "trigger": {"type": intent.trigger_type, "parameters": {}},
            "actions": [{"type": action, "parameters": {}} for action in intent.actions],
            "flow_pattern": intent.data_flow,
            "error_handling": intent.error_handling,
            "suggested_template": intent.suggested_template,
            "confidence": intent.confidence,
            "extracted_params": params,
            "matched_patterns": [
                {"name": p.name, "description": p.description, "popularity": p.popularity_score}
                for p in (intent.matched_patterns or [])
            ],
        }

        return spec

    def _generate_name(self, prompt: str) -> str:
        """Generate a workflow name from prompt"""
        # Take first few words, capitalize
        words = prompt.split()[:5]
        name = " ".join(words).title()

        # Remove common words
        remove_words = ["The", "A", "An", "When", "If"]
        for word in remove_words:
            name = name.replace(word + " ", "")

        return name or "Generated Workflow"


# Backwards compatibility alias
NLPromptParser = KeywordPatternMatcher


# Convenience functions
def parse_prompt(prompt: str, kb: Optional[KnowledgeBase] = None) -> ParsedIntent:
    """Match prompt to workflow intent using keyword patterns."""
    matcher = KeywordPatternMatcher(knowledge_base=kb)
    return matcher.parse(prompt)


def prompt_to_spec(prompt: str, kb: Optional[KnowledgeBase] = None) -> Dict:
    """Convert prompt to workflow specification using keyword matching."""
    matcher = KeywordPatternMatcher(knowledge_base=kb)
    return matcher.generate_workflow_spec(prompt)


if __name__ == "__main__":
    # Test the keyword pattern matcher
    print("Keyword Pattern Matcher v2.1")
    print("=" * 70)
    print("NOTE: This uses KEYWORD MATCHING, not AI/NLP understanding.")
    print("      It works by counting occurrences of predefined keywords.")
    print("=" * 70)

    test_prompts = [
        "When I receive a webhook, save it to database and send a Slack notification",
        "Every hour, fetch data from API and sync to database with retry logic",
        "Monitor RSS feed and post new items to Twitter and LinkedIn",
        "When new lead added to Google Sheets, send welcome email and schedule follow-up",
        "Call three different APIs, merge the results, and transform the data",
    ]

    matcher = KeywordPatternMatcher()

    for prompt in test_prompts:
        print(f"\n📝 Prompt: {prompt}")
        spec = matcher.generate_workflow_spec(prompt)
        print(f"   ├─ Name: {spec['name']}")
        print(f"   ├─ Trigger: {spec['trigger']['type']}")
        print(f"   ├─ Actions: {', '.join([a['type'] for a in spec['actions']])}")
        print(f"   ├─ Flow: {spec['flow_pattern']}")
        print(f"   ├─ Template: {spec['suggested_template']} ({spec['confidence']:.0%})")
        if spec["matched_patterns"]:
            print(f"   └─ Matched: {spec['matched_patterns'][0]['name']}")
