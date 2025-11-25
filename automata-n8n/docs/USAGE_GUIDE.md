# Automata Usage Guide

A comprehensive guide to using the Automata n8n workflow generator.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [Web Interface](#web-interface)
4. [Command Line Usage](#command-line-usage)
5. [Configuration](#configuration)
6. [Templates](#templates)
7. [LLM Integration](#llm-integration)
8. [Importing to n8n](#importing-to-n8n)
9. [Troubleshooting](#troubleshooting)

---

## Quick Start

```bash
# 1. Navigate to the automata directory
cd automata-n8n

# 2. Install dependencies
pip install -r requirements.txt
pip install flask  # For web interface

# 3. Start the web interface
python web/app.py

# 4. Open browser to http://localhost:5000
```

---

## Installation

### Prerequisites

- Python 3.8+
- pip package manager
- n8n instance (for importing workflows)

### Step-by-Step Installation

```bash
# Clone or navigate to the repository
cd /path/to/n8er/automata-n8n

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install core dependencies
pip install -r requirements.txt

# Install web interface dependencies
pip install flask

# (Optional) Install LLM providers for AI-powered generation
pip install openai      # For GPT-4 support
pip install anthropic   # For Claude support
```

### Verify Installation

```bash
# Test core functionality
python -c "from skills.generate_workflow_json import WorkflowBuilder; print('Core: OK')"

# Test node versions (should show 182 nodes)
python -c "from skills.n8n_node_versions import NODE_TYPE_VERSIONS; print(f'Nodes: {len(NODE_TYPE_VERSIONS)}')"

# Test templates
python -c "from skills.enhanced_templates import TEMPLATES; print('Templates: OK')"
```

---

## Web Interface

The web interface is the easiest way to generate workflows.

### Starting the Web Server

```bash
cd automata-n8n
python web/app.py
```

You'll see:
```
============================================================
AUTOMATA WEB INTERFACE
============================================================

Core modules: available
LLM support: available (or unavailable)
LLM provider: OpenAIProvider (or none configured)
Templates: 12

Starting server at http://localhost:5000
============================================================
```

### Using the Web Interface

1. **Open your browser** to `http://localhost:5000`

2. **Option A: Generate from Natural Language**
   - Type your workflow description in the text box
   - Example: "When I receive a webhook, save the data to PostgreSQL and send a Slack notification"
   - Check "Use AI for better understanding" if you have an LLM configured
   - Click **"Generate Workflow"**

3. **Option B: Use a Template**
   - Browse the 12 available template cards
   - Click on a template to select it (it will highlight)
   - Click **"Use Selected Template"**

4. **Download Your Workflow**
   - Review the generated JSON in the preview pane
   - Click **"Download JSON"** to save the file
   - Or click **"Copy to Clipboard"** to copy the JSON

### Available Templates

| Template | Description | Best For |
|----------|-------------|----------|
| `webhook_db_slack` | Webhook → Database → Slack | Data ingestion with notifications |
| `scheduled_sync_retry` | Scheduled sync with retry | ETL, periodic data sync |
| `rss_social` | RSS → Social Media | Content automation |
| `sheets_crm` | Google Sheets CRM | Sales automation |
| `multi_api` | Multi-API aggregation | Data aggregation |
| `webhook_advanced` | Advanced webhook responses | Custom API responses |
| `webhook_error_handling` | Error handling patterns | Production workflows |
| `circuit_breaker` | Circuit breaker pattern | Resilient API calls |
| `ai_content` | AI content processing | Content analysis with AI |
| `ecommerce_orders` | E-commerce order processor | Order notifications |
| `github_jira` | GitHub to Jira sync | DevOps automation |
| `cloud_backup` | Multi-cloud file backup | File synchronization |

---

## Command Line Usage

You can also generate workflows programmatically:

### Generate from Template

```python
from skills.enhanced_templates import get_template_by_name

# Generate webhook → database → slack workflow
workflow = get_template_by_name("webhook_db_slack")

# Save to file
import json
with open("my_workflow.json", "w") as f:
    json.dump(workflow, f, indent=2)
```

### Generate from Natural Language

```python
from skills.nl_prompt_parser import KeywordPatternMatcher
from skills.generate_workflow_json import WorkflowBuilder

# Parse user prompt
parser = KeywordPatternMatcher()
spec = parser.generate_workflow_spec(
    "When I receive a webhook, send an email notification"
)

print(f"Trigger: {spec['trigger']['type']}")
print(f"Actions: {[a['type'] for a in spec['actions']]}")
print(f"Suggested template: {spec['suggested_template']}")
```

### Generate with LLM (if configured)

```python
from skills.llm_prompt_parser import LLMPromptParser

parser = LLMPromptParser()

if parser.is_llm_available():
    spec = parser.generate_workflow_spec(
        "Create a workflow that monitors GitHub issues and creates Jira tickets"
    )
    print(f"LLM Provider: {spec['llm_provider']}")
    print(f"Confidence: {spec['confidence']}")
else:
    print("No LLM configured - using keyword matching")
```

### Build Custom Workflow

```python
from skills.generate_workflow_json import WorkflowBuilder

# Create a custom workflow
builder = WorkflowBuilder("My Custom Workflow")

# Add trigger
builder.add_trigger("webhook", "Webhook Trigger", parameters={
    "path": "my-webhook",
    "httpMethod": "POST"
})

# Add processing node
builder.add_node("n8n-nodes-base.set", "Process Data", parameters={
    "mode": "manual",
    "assignments": {
        "assignments": [
            {"name": "processed", "value": "={{ $json.data }}"}
        ]
    }
})

# Add notification
builder.add_node("n8n-nodes-base.slack", "Notify", parameters={
    "channel": "#alerts",
    "text": "New data received!"
})

# Connect nodes
builder.connect("Webhook Trigger", "Process Data")
builder.connect("Process Data", "Notify")

# Build and save
workflow = builder.build()

import json
with open("custom_workflow.json", "w") as f:
    json.dump(workflow, f, indent=2)
```

---

## Configuration

### Environment Variables

Create a `.env` file in the `automata-n8n` directory:

```bash
# n8n API Connection (for real validation)
N8N_API_URL=http://localhost:5678
N8N_API_KEY=your-n8n-api-key

# Simulation Mode (set to true for built-in sample patterns)
ALLOW_SIMULATED_DATA=false

# LLM Providers (configure one)
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
OLLAMA_HOST=http://localhost:11434

# Optional: Web Research APIs
REDDIT_CLIENT_ID=your-reddit-id
REDDIT_CLIENT_SECRET=your-reddit-secret
GITHUB_TOKEN=your-github-token
```

### Configuration Priority

1. **LLM Provider**: OpenAI → Anthropic → Ollama → Keyword Matching
2. **Validation**: Real n8n API → Local schema validation
3. **Patterns**: API data (if configured) → Built-in samples

---

## LLM Integration

### Setting Up OpenAI

```bash
pip install openai
export OPENAI_API_KEY=sk-your-key-here
```

### Setting Up Anthropic (Claude)

```bash
pip install anthropic
export ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### Setting Up Ollama (Local LLM)

```bash
# Install Ollama from https://ollama.ai
ollama pull llama3.2

# Automata will auto-detect at http://localhost:11434
```

### Verify LLM Setup

```python
from skills.llm_prompt_parser import get_available_provider

provider = get_available_provider()
if provider:
    print(f"LLM Ready: {provider}")
else:
    print("No LLM configured - using keyword matching")
```

---

## Importing to n8n

### Method 1: Copy/Paste

1. Generate workflow in Automata
2. Copy the JSON output
3. In n8n, go to **Workflows** → **Add Workflow** → **Import from URL or File**
4. Paste the JSON and click **Import**

### Method 2: File Import

1. Download the JSON file from Automata
2. In n8n, go to **Workflows** → **Add Workflow** → **Import from URL or File**
3. Select **Upload a File**
4. Choose your downloaded JSON file
5. Click **Import**

### Method 3: API Import (Advanced)

```python
from skills.n8n_api_client import N8nApiClient
from skills.enhanced_templates import get_template_by_name

# Generate workflow
workflow = get_template_by_name("webhook_db_slack")

# Import to n8n
client = N8nApiClient(
    api_url="http://localhost:5678",
    api_key="your-api-key"
)

result = client.import_workflow(workflow, activate=False)
print(f"Imported workflow ID: {result['id']}")
```

### After Importing

1. **Configure Credentials**: Click on nodes that need credentials (database, Slack, etc.)
2. **Update Parameters**: Modify webhook paths, email addresses, channel names
3. **Test**: Use the **Execute Workflow** button to test
4. **Activate**: Toggle the workflow to active when ready

---

## Troubleshooting

### Common Issues

**Issue: "Module not found" errors**
```bash
# Make sure you're in the right directory
cd automata-n8n

# Install dependencies
pip install -r requirements.txt
pip install flask
```

**Issue: Web interface won't start**
```bash
# Check if port 5000 is in use
lsof -i :5000

# Use a different port
python -c "from web.app import app; app.run(port=5001)"
```

**Issue: LLM not detected**
```bash
# Check API key is set
echo $OPENAI_API_KEY

# Test directly
python -c "from skills.llm_prompt_parser import get_available_provider; print(get_available_provider())"
```

**Issue: Workflow won't import to n8n**
- Check n8n version is 1.60.0+ (workflows use v2 node formats)
- Verify JSON is valid: `python -m json.tool workflow.json`
- Check for missing credentials in the error message

**Issue: Nodes show as "Unknown" in n8n**
- The node type might not exist in your n8n version
- Check the n8n documentation for available nodes

### Getting Help

1. Check the `docs/` folder for additional documentation
2. Review `docs/IMPLEMENTATION_PLAN.md` for system architecture
3. Review `docs/AUTOMATA_REVIEW_2025-11.md` for system capabilities

### Log Files

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## Quick Reference

### Generate Workflow (Web)
```
http://localhost:5000
```

### Generate Workflow (CLI)
```python
from skills.enhanced_templates import get_template_by_name
workflow = get_template_by_name("webhook_db_slack")
```

### Available Node Types
```python
from skills.n8n_node_versions import get_all_node_types
print(f"Supported nodes: {len(get_all_node_types())}")  # 182
```

### Check System Status
```bash
curl http://localhost:5000/api/status
```

---

*Guide version: 3.0.0 | Last updated: 2025-11-25*
