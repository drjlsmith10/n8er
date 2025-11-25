# Project Automata: n8n Workflow Generator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

**Version:** 3.0.0
**Status:** All 3 implementation phases complete
**Nodes Supported:** 182 n8n node types

Generate n8n workflows from natural language prompts or templates.

---

## Quick Start

```bash
# 1. Install dependencies
cd automata-n8n
pip install -r requirements.txt
pip install flask

# 2. Start the web interface
python web/app.py

# 3. Open browser
open http://localhost:5000
```

That's it! You can now:
- Type a workflow description and click "Generate Workflow"
- Or select a template and click "Use Selected Template"
- Download the JSON and import it into n8n

---

## Features

### Web Interface
- Natural language workflow generation
- 12 built-in templates
- Live JSON preview
- One-click download

### 182 Node Types Supported
- Triggers: Webhook, Cron, Email, RSS, Form
- Communication: Slack, Discord, Telegram, Teams, WhatsApp
- Databases: PostgreSQL, MySQL, MongoDB, Supabase, Firebase
- AI/ML: OpenAI, Anthropic, Groq, Mistral, Cohere
- Cloud: AWS, Google Cloud, Vercel, Netlify
- And 150+ more...

### Optional LLM Integration
Better understanding with AI (configure one):
```bash
export OPENAI_API_KEY=sk-your-key      # GPT-4
export ANTHROPIC_API_KEY=sk-ant-key    # Claude
# Or use local Ollama at http://localhost:11434
```

---

## Usage

### Option 1: Web Interface (Recommended)

```bash
python web/app.py
# Open http://localhost:5000
```

### Option 2: Command Line

```python
from skills.enhanced_templates import get_template_by_name

# Generate from template
workflow = get_template_by_name("webhook_db_slack")

# Save to file
import json
with open("workflow.json", "w") as f:
    json.dump(workflow, f, indent=2)
```

### Option 3: Custom Workflow

```python
from skills.generate_workflow_json import WorkflowBuilder

builder = WorkflowBuilder("My Workflow")
builder.add_trigger("webhook", "Start", parameters={"path": "my-hook"})
builder.add_node("n8n-nodes-base.slack", "Notify", parameters={"channel": "#alerts"})
builder.connect("Start", "Notify")

workflow = builder.build()
```

---

## Available Templates

| Template | Description |
|----------|-------------|
| `webhook_db_slack` | Webhook → Database → Slack notification |
| `scheduled_sync_retry` | Scheduled sync with retry logic |
| `rss_social` | RSS feed → Social media posting |
| `sheets_crm` | Google Sheets CRM automation |
| `multi_api` | Multi-API aggregation |
| `ai_content` | AI-powered content processing |
| `ecommerce_orders` | E-commerce order handling |
| `github_jira` | GitHub → Jira issue sync |
| `cloud_backup` | Multi-cloud file backup |
| `webhook_error_handling` | Comprehensive error handling |
| `circuit_breaker` | Resilient API calls |
| `webhook_advanced` | Advanced webhook responses |

---

## Importing to n8n

1. Generate workflow in Automata
2. Download or copy the JSON
3. In n8n: **Workflows** → **Import from File**
4. Select your JSON file
5. Configure credentials for connected services
6. Activate and run!

**Note:** Workflows are compatible with n8n 1.60.0+

---

## Project Structure

```
automata-n8n/
├── web/                 # Web interface (Flask)
│   ├── app.py          # Main application
│   └── templates/      # HTML templates
├── agents/             # Simplified agent system (3 agents)
│   ├── knowledge.py    # Research & knowledge base
│   ├── builder.py      # Code & documentation
│   └── validator.py    # Workflow validation
├── skills/             # Core functionality
│   ├── generate_workflow_json.py   # Workflow builder
│   ├── enhanced_templates.py       # 12 templates
│   ├── n8n_node_versions.py        # 182 node types
│   ├── nl_prompt_parser.py         # Keyword matching
│   └── llm_prompt_parser.py        # LLM integration
├── docs/               # Documentation
│   ├── USAGE_GUIDE.md  # Detailed usage guide
│   └── IMPLEMENTATION_PLAN.md
└── tests/              # Test suite
```

---

## Configuration

Create `.env` file (optional):

```bash
# LLM Provider (choose one)
OPENAI_API_KEY=sk-your-key
ANTHROPIC_API_KEY=sk-ant-your-key
OLLAMA_HOST=http://localhost:11434

# n8n API (for real validation)
N8N_API_URL=http://localhost:5678
N8N_API_KEY=your-api-key

# Enable simulation mode for sample data
ALLOW_SIMULATED_DATA=false
```

---

## Documentation

- **[Usage Guide](docs/USAGE_GUIDE.md)** - Detailed instructions
- **[Implementation Plan](docs/IMPLEMENTATION_PLAN.md)** - Architecture details

---

## Requirements

- Python 3.9+
- Flask (for web interface)
- n8n 1.60.0+ (for importing workflows)
- Optional: OpenAI, Anthropic, or Ollama for LLM features

---

## License

MIT License - See [LICENSE](LICENSE) for details.

---

## Quick Reference

| Action | Command |
|--------|---------|
| Start web UI | `python web/app.py` |
| Generate template | `get_template_by_name("webhook_db_slack")` |
| Count nodes | `len(NODE_TYPE_VERSIONS)` → 182 |
| Check LLM | `get_available_provider()` |

---

*Project Automata v3.0.0 - All phases complete*
