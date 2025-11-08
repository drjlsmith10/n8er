# Project Automata: Quick Start Guide

Get up and running in 5 minutes!

---

## 1. Install (2 minutes)

```bash
# Clone and navigate
git clone https://github.com/drjlsmith10/n8er.git
cd n8er/automata-n8n

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e .
```

## 2. Configure (1 minute)

```bash
# Copy environment template
cp .env.example .env

# Edit if needed (optional for basic use)
# nano .env
```

**For basic use, defaults work fine!** No API keys needed for development.

## 3. Run (2 minutes)

### Populate Knowledge Base

```bash
# Run web research (uses simulated data by default)
python scripts/run_web_research.py
```

**Output:**
```
✅ Reddit: 4 patterns, 4 errors
✅ YouTube: 3 patterns, 2 insights
✅ Twitter: 2 patterns, 8 tips
✅ Knowledge base contains 9 patterns from 3 sources
```

### Test Natural Language Parsing

```bash
python -m skills.nl_prompt_parser
```

**Output:**
```
📝 Prompt: When I receive a webhook, save to database and send Slack
   ├─ Template: webhook_db_slack (85% confidence)
   └─ Matched: Webhook → Database → Slack Notification
```

### Generate a Workflow

```bash
python -c "
from skills.enhanced_templates import get_template_by_name
import json

workflow = get_template_by_name('webhook_db_slack')
print(json.dumps(workflow, indent=2))
" > my_workflow.json

echo "✓ Workflow saved to my_workflow.json"
```

## 4. Verify

```bash
# Run tests
pytest tests/ -v

# Check configuration
python config.py

# View knowledge base summary
cat knowledge_base/summary.md
```

---

## What You Can Do Now

### 1. Parse Natural Language to Workflows

```python
from skills.nl_prompt_parser import NLPromptParser

parser = NLPromptParser()
spec = parser.generate_workflow_spec(
    "When I receive a webhook, save to database and send Slack notification"
)

print(f"Template: {spec['suggested_template']}")
print(f"Confidence: {spec['confidence']:.0%}")
# Output: Template: webhook_db_slack, Confidence: 85%
```

### 2. Generate Production Workflows

```python
from skills.enhanced_templates import get_template_by_name

# Available templates:
# - webhook_db_slack
# - scheduled_sync_retry
# - rss_social
# - sheets_crm
# - multi_api

workflow = get_template_by_name('rss_social')
print(f"Workflow: {workflow['name']}")
print(f"Nodes: {len(workflow['nodes'])}")
```

### 3. Access Community Knowledge

```python
from skills.knowledge_base import KnowledgeBase

kb = KnowledgeBase()
print(kb.get_statistics())

# Get top patterns
top_patterns = kb.get_top_patterns(5)
for pattern in top_patterns:
    print(f"{pattern.name} ({pattern.popularity_score} popularity)")
```

---

## Next Steps

1. **Read full documentation:** `docs/DEPLOYMENT.md`
2. **Get API keys** (optional): See API Keys section in deployment docs
3. **Run real research:** Set `ENABLE_WEB_RESEARCH=true` in .env
4. **Test with n8n:** Install n8n and import generated workflows
5. **Contribute patterns:** Add your own workflows to knowledge base

---

## Common Commands

```bash
# Run web research
python scripts/run_web_research.py

# Test NL parsing
python -m skills.nl_prompt_parser

# Run tests
pytest tests/ -v

# Generate specific workflow
python -c "from skills.enhanced_templates import get_template_by_name; import json; print(json.dumps(get_template_by_name('webhook_db_slack'), indent=2))"

# Check configuration
python config.py

# View knowledge base
cat knowledge_base/summary.md
```

---

## Troubleshooting

**Issue:** ModuleNotFoundError
```bash
# Solution:
pip install -r requirements.txt
pip install -e .
```

**Issue:** Permission denied on directories
```bash
# Solution:
mkdir -p knowledge_base workflows logs
chmod 755 knowledge_base workflows logs
```

**Issue:** Tests failing
```bash
# Solution:
python --version  # Check 3.9+
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

---

## Get Help

- **Documentation:** `docs/` directory
- **Deployment:** `docs/DEPLOYMENT.md`
- **Code Review:** `docs/CODE_REVIEW.md`
- **Architecture:** `docs/architecture.md`

---

**You're ready to build AI-powered n8n workflows! 🚀**
