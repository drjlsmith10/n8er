"""
Automata Web Interface

A simple web UI for generating n8n workflows from natural language prompts.

Features:
- Natural language workflow generation
- Template-based workflow selection
- Live workflow preview
- JSON download

Author: Project Automata - Cycle 02
Version: 3.0.0 (Phase 3 - Web Interface)

Usage:
    python web/app.py

Then open http://localhost:5000 in your browser.
"""

import json
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask, jsonify, render_template, request, send_file
from io import BytesIO

# Import Automata components
try:
    from skills.nl_prompt_parser import KeywordPatternMatcher
    from skills.enhanced_templates import get_template_by_name, CommunityTemplateLibrary
    from skills.generate_workflow_json import WorkflowBuilder
    HAS_CORE = True
except ImportError as e:
    print(f"Warning: Could not import core modules: {e}")
    HAS_CORE = False

try:
    from skills.llm_prompt_parser import LLMPromptParser, get_available_provider
    HAS_LLM = True
except ImportError:
    HAS_LLM = False
    LLMPromptParser = None

app = Flask(__name__)


# Available templates
TEMPLATES = {
    "webhook_db_slack": {
        "name": "Webhook → Database → Slack",
        "description": "Receive webhook, store in database, send Slack notification",
        "category": "data",
    },
    "scheduled_sync_retry": {
        "name": "Scheduled Sync with Retry",
        "description": "Sync data on schedule with exponential backoff retry",
        "category": "sync",
    },
    "rss_social": {
        "name": "RSS to Social Media",
        "description": "Monitor RSS feed and post to social media",
        "category": "social",
    },
    "sheets_crm": {
        "name": "Google Sheets CRM",
        "description": "CRM automation with Google Sheets",
        "category": "crm",
    },
    "multi_api": {
        "name": "Multi-API Aggregation",
        "description": "Call multiple APIs and merge results",
        "category": "api",
    },
    "webhook_advanced": {
        "name": "Advanced Webhook",
        "description": "Webhook with multiple response modes",
        "category": "webhook",
    },
    "webhook_error_handling": {
        "name": "Webhook + Error Handling",
        "description": "Comprehensive error handling pattern",
        "category": "error",
    },
    "circuit_breaker": {
        "name": "Circuit Breaker Pattern",
        "description": "Resilient API calls with circuit breaker",
        "category": "resilience",
    },
    "ai_content": {
        "name": "AI Content Processor",
        "description": "Process content with AI and distribute",
        "category": "ai",
    },
    "ecommerce_orders": {
        "name": "E-commerce Order Processor",
        "description": "Handle orders: email + Slack + database",
        "category": "ecommerce",
    },
    "github_jira": {
        "name": "GitHub to Jira Sync",
        "description": "Sync GitHub issues to Jira tickets",
        "category": "devops",
    },
    "cloud_backup": {
        "name": "Cloud File Backup",
        "description": "Backup Google Drive files to S3 and Dropbox",
        "category": "storage",
    },
}


@app.route("/")
def index():
    """Render the main page."""
    llm_status = "available" if (HAS_LLM and get_available_provider()) else "unavailable"
    return render_template(
        "index.html",
        templates=TEMPLATES,
        llm_status=llm_status,
        has_core=HAS_CORE,
    )


@app.route("/api/generate", methods=["POST"])
def generate_workflow():
    """Generate a workflow from prompt or template."""
    if not HAS_CORE:
        return jsonify({"error": "Core modules not available"}), 500

    data = request.json
    prompt = data.get("prompt", "")
    template_name = data.get("template", "")
    use_llm = data.get("use_llm", False)

    try:
        if template_name:
            # Generate from template
            workflow = get_template_by_name(template_name)
            method = "template"
        elif prompt:
            # Generate from prompt
            if use_llm and HAS_LLM:
                parser = LLMPromptParser()
                spec = parser.generate_workflow_spec(prompt)
                method = f"llm ({spec.get('llm_provider', 'unknown')})"
            else:
                parser = KeywordPatternMatcher()
                spec = parser.generate_workflow_spec(prompt)
                method = "keywords"

            # Build workflow from spec
            workflow = build_workflow_from_spec(spec)
        else:
            return jsonify({"error": "Please provide a prompt or select a template"}), 400

        return jsonify({
            "success": True,
            "workflow": workflow,
            "method": method,
            "node_count": len(workflow.get("nodes", [])),
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def build_workflow_from_spec(spec: dict) -> dict:
    """Build a workflow from a parsed spec."""
    builder = WorkflowBuilder(spec.get("name", "Generated Workflow"))

    # Add trigger
    trigger_type = spec.get("trigger", {}).get("type", "manual")
    trigger_map = {
        "webhook": ("webhook", {"path": "auto-generated", "httpMethod": "POST"}),
        "scheduled": ("cron", {"cronExpression": "0 * * * *"}),
        "manual": ("manual", {}),
        "email": ("emailTrigger", {}),
        "rss": ("rssFeedTrigger", {"feedUrl": "https://example.com/feed"}),
    }

    trigger_key, trigger_params = trigger_map.get(trigger_type, ("manual", {}))
    builder.add_trigger(trigger_key, "Trigger", parameters=trigger_params)

    # Add actions based on spec
    actions = spec.get("actions", [])
    prev_node = "Trigger"

    for i, action in enumerate(actions):
        action_type = action.get("type", "transform")
        node_name = f"Action {i + 1}"

        action_nodes = {
            "send_email": ("n8n-nodes-base.emailSend", {"toEmail": "user@example.com"}),
            "slack": ("n8n-nodes-base.slack", {"channel": "#general"}),
            "database": ("n8n-nodes-base.postgres", {"operation": "insert"}),
            "http_request": ("n8n-nodes-base.httpRequest", {"url": "https://api.example.com"}),
            "transform": ("n8n-nodes-base.set", {"mode": "manual"}),
            "filter": ("n8n-nodes-base.if", {}),
        }

        node_type, params = action_nodes.get(action_type, ("n8n-nodes-base.noOp", {}))
        builder.add_node(node_type, node_name, parameters=params)
        builder.connect(prev_node, node_name)
        prev_node = node_name

    return builder.build()


@app.route("/api/download", methods=["POST"])
def download_workflow():
    """Download workflow as JSON file."""
    data = request.json
    workflow = data.get("workflow", {})

    # Create JSON file
    json_bytes = json.dumps(workflow, indent=2).encode("utf-8")
    buffer = BytesIO(json_bytes)

    filename = f"{workflow.get('name', 'workflow').replace(' ', '_')}.json"

    return send_file(
        buffer,
        mimetype="application/json",
        as_attachment=True,
        download_name=filename,
    )


@app.route("/api/templates")
def list_templates():
    """List available templates."""
    return jsonify({"templates": TEMPLATES})


@app.route("/api/status")
def status():
    """Get system status."""
    llm_provider = None
    if HAS_LLM:
        llm_provider = get_available_provider()

    return jsonify({
        "core_available": HAS_CORE,
        "llm_available": HAS_LLM and llm_provider is not None,
        "llm_provider": llm_provider,
        "template_count": len(TEMPLATES),
    })


if __name__ == "__main__":
    print("=" * 60)
    print("AUTOMATA WEB INTERFACE")
    print("=" * 60)
    print()
    print(f"Core modules: {'available' if HAS_CORE else 'MISSING'}")
    print(f"LLM support: {'available' if HAS_LLM else 'unavailable'}")
    if HAS_LLM:
        provider = get_available_provider()
        print(f"LLM provider: {provider or 'none configured'}")
    print(f"Templates: {len(TEMPLATES)}")
    print()
    print("Starting server at http://localhost:5000")
    print("=" * 60)

    app.run(debug=True, host="0.0.0.0", port=5000)
