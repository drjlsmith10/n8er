"""
LLM-based Prompt Parser

Uses Large Language Models to understand workflow descriptions and extract
structured intent with semantic understanding.

This module provides an alternative to the keyword-based KeywordPatternMatcher,
offering better understanding of natural language descriptions.

Supported LLM Providers:
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- Local models via Ollama

Configuration:
    Set one of these environment variables:
    - OPENAI_API_KEY: For OpenAI models
    - ANTHROPIC_API_KEY: For Claude models
    - OLLAMA_HOST: For local Ollama models (default: http://localhost:11434)

Author: Project Automata - Cycle 02
Version: 3.0.0 (Phase 3 - LLM Integration)
"""

import json
import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class LLMParsedIntent:
    """Structured workflow intent parsed from natural language."""

    trigger_type: str
    trigger_config: Dict[str, Any]
    actions: List[Dict[str, Any]]
    flow_pattern: str  # linear, conditional, parallel, loop
    error_handling: Dict[str, Any]
    suggested_nodes: List[str]
    workflow_name: str
    description: str
    confidence: float
    llm_provider: str
    reasoning: str


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def parse_prompt(self, prompt: str, system_prompt: str) -> Tuple[Dict, str]:
        """
        Parse a user prompt using the LLM.

        Args:
            prompt: User's workflow description
            system_prompt: System instructions for the LLM

        Returns:
            Tuple of (parsed_json, raw_response)
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this provider is configured and available."""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider."""

    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self.api_key = os.getenv("OPENAI_API_KEY")

    def is_available(self) -> bool:
        return self.api_key is not None

    def parse_prompt(self, prompt: str, system_prompt: str) -> Tuple[Dict, str]:
        try:
            import openai

            client = openai.OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
            )

            raw_response = response.choices[0].message.content
            parsed = json.loads(raw_response)
            return parsed, raw_response

        except ImportError:
            raise RuntimeError("openai package not installed. Run: pip install openai")
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider."""

    def __init__(self, model: str = "claude-3-haiku-20240307"):
        self.model = model
        self.api_key = os.getenv("ANTHROPIC_API_KEY")

    def is_available(self) -> bool:
        return self.api_key is not None

    def parse_prompt(self, prompt: str, system_prompt: str) -> Tuple[Dict, str]:
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=self.api_key)
            response = client.messages.create(
                model=self.model,
                max_tokens=2048,
                system=system_prompt,
                messages=[{"role": "user", "content": prompt}],
            )

            raw_response = response.content[0].text

            # Extract JSON from response (Claude might add explanation text)
            json_start = raw_response.find("{")
            json_end = raw_response.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                json_str = raw_response[json_start:json_end]
                parsed = json.loads(json_str)
                return parsed, raw_response
            else:
                raise ValueError("No JSON found in response")

        except ImportError:
            raise RuntimeError("anthropic package not installed. Run: pip install anthropic")
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise


class OllamaProvider(LLMProvider):
    """Local Ollama provider for self-hosted models."""

    def __init__(self, model: str = "llama3.2", host: str = None):
        self.model = model
        self.host = host or os.getenv("OLLAMA_HOST", "http://localhost:11434")

    def is_available(self) -> bool:
        try:
            import requests

            response = requests.get(f"{self.host}/api/tags", timeout=2)
            return response.status_code == 200
        except Exception:
            return False

    def parse_prompt(self, prompt: str, system_prompt: str) -> Tuple[Dict, str]:
        try:
            import requests

            response = requests.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": f"{system_prompt}\n\nUser request: {prompt}\n\nRespond with JSON only:",
                    "stream": False,
                    "format": "json",
                },
                timeout=60,
            )

            if response.status_code != 200:
                raise RuntimeError(f"Ollama error: {response.text}")

            result = response.json()
            raw_response = result.get("response", "")

            # Parse JSON from response
            json_start = raw_response.find("{")
            json_end = raw_response.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                json_str = raw_response[json_start:json_end]
                parsed = json.loads(json_str)
                return parsed, raw_response
            else:
                raise ValueError("No JSON found in Ollama response")

        except ImportError:
            raise RuntimeError("requests package not installed. Run: pip install requests")
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            raise


# System prompt for workflow intent extraction
WORKFLOW_EXTRACTION_PROMPT = """You are an n8n workflow expert. Your task is to analyze natural language descriptions of automation workflows and extract structured information.

Given a user's description of a desired workflow, extract the following information and return it as JSON:

{
    "trigger_type": "webhook" | "scheduled" | "manual" | "email" | "rss" | "database" | "file" | "form" | "other",
    "trigger_config": {
        "description": "what triggers the workflow",
        "parameters": {}
    },
    "actions": [
        {
            "type": "action type (e.g., send_email, http_request, database_write, slack_message)",
            "description": "what this action does",
            "parameters": {},
            "order": 1
        }
    ],
    "flow_pattern": "linear" | "conditional" | "parallel" | "loop",
    "error_handling": {
        "needed": true/false,
        "strategy": "retry" | "fallback" | "notify" | "ignore" | null,
        "description": "error handling approach"
    },
    "suggested_nodes": ["list of n8n node types to use"],
    "workflow_name": "suggested name for the workflow",
    "description": "brief description of what the workflow does",
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation of your interpretation"
}

n8n node types follow the format "n8n-nodes-base.nodeName". Common nodes:
- Triggers: webhook, manualTrigger, cron, emailTrigger, rssFeedTrigger
- HTTP: httpRequest
- Communication: slack, discord, telegram, emailSend
- Database: postgres, mysql, mongodb, airtable, googleSheets
- Flow Control: if, switch, merge, splitInBatches, wait
- Transform: set, code, function

Only respond with valid JSON. No additional text."""


class LLMPromptParser:
    """
    LLM-based prompt parser for workflow intent extraction.

    Uses semantic understanding via LLMs to parse natural language
    workflow descriptions into structured specifications.

    Falls back to keyword matching if no LLM is available.
    """

    def __init__(
        self,
        provider: Optional[LLMProvider] = None,
        fallback_to_keywords: bool = True,
    ):
        """
        Initialize the LLM prompt parser.

        Args:
            provider: Specific LLM provider to use (auto-detects if None)
            fallback_to_keywords: Fall back to KeywordPatternMatcher if LLM unavailable
        """
        self.provider = provider or self._auto_detect_provider()
        self.fallback_to_keywords = fallback_to_keywords
        self._keyword_parser = None

    def _auto_detect_provider(self) -> Optional[LLMProvider]:
        """Auto-detect available LLM provider."""
        # Try providers in order of preference
        providers = [
            OpenAIProvider(),
            AnthropicProvider(),
            OllamaProvider(),
        ]

        for provider in providers:
            if provider.is_available():
                logger.info(f"Auto-detected LLM provider: {provider.__class__.__name__}")
                return provider

        logger.warning("No LLM provider available")
        return None

    def is_llm_available(self) -> bool:
        """Check if an LLM provider is available."""
        return self.provider is not None and self.provider.is_available()

    def _get_keyword_parser(self):
        """Lazy-load keyword parser for fallback."""
        if self._keyword_parser is None:
            from skills.nl_prompt_parser import KeywordPatternMatcher

            self._keyword_parser = KeywordPatternMatcher()
        return self._keyword_parser

    def parse(self, prompt: str) -> LLMParsedIntent:
        """
        Parse a natural language workflow description.

        Args:
            prompt: Natural language description of the desired workflow

        Returns:
            LLMParsedIntent with extracted information
        """
        if not self.is_llm_available():
            if self.fallback_to_keywords:
                logger.info("Falling back to keyword-based parsing")
                return self._parse_with_keywords(prompt)
            else:
                raise RuntimeError("No LLM provider available and fallback disabled")

        try:
            parsed, raw_response = self.provider.parse_prompt(
                prompt, WORKFLOW_EXTRACTION_PROMPT
            )

            return LLMParsedIntent(
                trigger_type=parsed.get("trigger_type", "manual"),
                trigger_config=parsed.get("trigger_config", {}),
                actions=parsed.get("actions", []),
                flow_pattern=parsed.get("flow_pattern", "linear"),
                error_handling=parsed.get("error_handling", {"needed": False}),
                suggested_nodes=parsed.get("suggested_nodes", []),
                workflow_name=parsed.get("workflow_name", "Generated Workflow"),
                description=parsed.get("description", ""),
                confidence=parsed.get("confidence", 0.8),
                llm_provider=self.provider.__class__.__name__,
                reasoning=parsed.get("reasoning", ""),
            )

        except Exception as e:
            logger.error(f"LLM parsing failed: {e}")
            if self.fallback_to_keywords:
                logger.info("Falling back to keyword-based parsing due to error")
                return self._parse_with_keywords(prompt)
            raise

    def _parse_with_keywords(self, prompt: str) -> LLMParsedIntent:
        """Parse using keyword matcher as fallback."""
        parser = self._get_keyword_parser()
        result = parser.parse(prompt)
        params = parser.extract_parameters(prompt)

        # Convert to LLMParsedIntent format
        return LLMParsedIntent(
            trigger_type=result.trigger_type,
            trigger_config={"parameters": params},
            actions=[{"type": action, "order": i + 1} for i, action in enumerate(result.actions)],
            flow_pattern=result.data_flow,
            error_handling={"needed": result.error_handling, "strategy": "notify" if result.error_handling else None},
            suggested_nodes=self._actions_to_nodes(result.trigger_type, result.actions),
            workflow_name=parser._generate_name(prompt),
            description=prompt[:100],
            confidence=result.confidence,
            llm_provider="KeywordPatternMatcher (fallback)",
            reasoning="Parsed using keyword matching (no LLM available)",
        )

    def _actions_to_nodes(self, trigger: str, actions: List[str]) -> List[str]:
        """Convert action types to suggested n8n nodes."""
        trigger_nodes = {
            "webhook": "n8n-nodes-base.webhook",
            "scheduled": "n8n-nodes-base.cron",
            "manual": "n8n-nodes-base.manualTrigger",
            "email": "n8n-nodes-base.emailTrigger",
            "rss": "n8n-nodes-base.rssFeedTrigger",
        }

        action_nodes = {
            "send_email": "n8n-nodes-base.emailSend",
            "slack": "n8n-nodes-base.slack",
            "database": "n8n-nodes-base.postgres",
            "http_request": "n8n-nodes-base.httpRequest",
            "transform": "n8n-nodes-base.set",
            "filter": "n8n-nodes-base.if",
            "aggregate": "n8n-nodes-base.merge",
        }

        nodes = []

        # Add trigger node
        if trigger in trigger_nodes:
            nodes.append(trigger_nodes[trigger])

        # Add action nodes
        for action in actions:
            if action in action_nodes:
                nodes.append(action_nodes[action])

        return nodes

    def generate_workflow_spec(self, prompt: str) -> Dict:
        """
        Generate a complete workflow specification from a prompt.

        Returns a spec ready for WorkflowBuilder.
        """
        intent = self.parse(prompt)

        return {
            "name": intent.workflow_name,
            "description": intent.description,
            "trigger": {
                "type": intent.trigger_type,
                "config": intent.trigger_config,
            },
            "actions": intent.actions,
            "flow_pattern": intent.flow_pattern,
            "error_handling": intent.error_handling,
            "suggested_nodes": intent.suggested_nodes,
            "confidence": intent.confidence,
            "llm_provider": intent.llm_provider,
            "reasoning": intent.reasoning,
        }


# Convenience functions
def parse_with_llm(prompt: str) -> LLMParsedIntent:
    """Parse a prompt using available LLM (with keyword fallback)."""
    parser = LLMPromptParser()
    return parser.parse(prompt)


def get_available_provider() -> Optional[str]:
    """Get the name of the available LLM provider."""
    parser = LLMPromptParser()
    if parser.provider:
        return parser.provider.__class__.__name__
    return None


if __name__ == "__main__":
    print("LLM Prompt Parser")
    print("=" * 70)

    parser = LLMPromptParser()

    if parser.is_llm_available():
        print(f"✓ LLM Provider: {parser.provider.__class__.__name__}")
    else:
        print("✗ No LLM provider available (will use keyword fallback)")

    print()

    test_prompts = [
        "When I receive a webhook, save the data to PostgreSQL and send a Slack notification",
        "Every hour, check for new orders in Shopify and send email confirmations",
        "When a new GitHub issue is created, create a Jira ticket and notify the team on Discord",
        "Parse incoming emails, extract attachments, and upload them to Google Drive",
    ]

    for prompt in test_prompts:
        print(f"📝 Prompt: {prompt}")
        try:
            spec = parser.generate_workflow_spec(prompt)
            print(f"   ├─ Name: {spec['name']}")
            print(f"   ├─ Trigger: {spec['trigger']['type']}")
            print(f"   ├─ Actions: {len(spec['actions'])} action(s)")
            print(f"   ├─ Flow: {spec['flow_pattern']}")
            print(f"   ├─ Confidence: {spec['confidence']:.0%}")
            print(f"   ├─ Provider: {spec['llm_provider']}")
            if spec["suggested_nodes"]:
                print(f"   └─ Nodes: {', '.join(spec['suggested_nodes'][:3])}...")
        except Exception as e:
            print(f"   └─ Error: {e}")
        print()
