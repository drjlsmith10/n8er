# Project Automata: Deployment Guide

**Version:** 2.0.0-alpha
**Last Updated:** 2025-11-08
**Status:** Development → Staging → Production

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Configuration](#configuration)
4. [API Keys & Subscriptions](#api-keys--subscriptions)
5. [Running the System](#running-the-system)
6. [Testing](#testing)
7. [Production Deployment](#production-deployment)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

| Software | Minimum Version | Purpose | Install Link |
|----------|----------------|---------|--------------|
| **Python** | 3.9+ | Runtime environment | https://python.org |
| **pip** | 21.0+ | Package manager | Included with Python |
| **git** | 2.30+ | Version control | https://git-scm.com |
| **virtualenv** | 20.0+ (recommended) | Isolation | `pip install virtualenv` |

### Recommended Software

| Software | Version | Purpose | Install Link |
|----------|---------|---------|--------------|
| **Docker** | Latest | Containerization | https://docker.com |
| **n8n** | **1.60.0+** (Recommended: 1.60.1) | Workflow testing | https://n8n.io |
| **VS Code** | Latest | Development | https://code.visualstudio.com |

⚠️ **Critical n8n Version Requirement:**
- **Minimum:** n8n 1.60.0
- **Recommended:** n8n 1.60.1
- **Maximum Tested:** n8n 1.70.x
- **Not Supported:** n8n < 1.60.0 (incompatible node typeVersions)

Generated workflows use modern node typeVersions (e.g., HTTP Request v4.2, Webhook v2.0) that require n8n 1.60.0 or later. See `docs/n8n_compatibility_matrix.md` for complete version compatibility information.

### System Requirements

**Development:**
- OS: Linux, macOS, Windows WSL2
- RAM: 2GB minimum, 4GB recommended
- Disk: 1GB free space

**Production:**
- OS: Linux (Ubuntu 20.04+ recommended)
- RAM: 4GB minimum, 8GB recommended
- Disk: 10GB free space
- CPU: 2 cores minimum

---

## Local Development Setup

### Step 1: Clone Repository

```bash
git clone https://github.com/drjlsmith10/n8er.git
cd n8er/automata-n8n
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install core dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Optional: Install development tools
pip install -e ".[dev]"

# Optional: Install API integrations (for real web research)
pip install -e ".[api]"
```

### Step 4: Verify Installation

```bash
# Test imports
python -c "from skills.knowledge_base import KnowledgeBase; print('✓ Installation successful')"

# Run tests
pytest tests/ -v

# Check configuration
python config.py
```

**Expected Output:**
```
✓ Installation successful
============================= test session starts =============================
collected 45 items

tests/test_schema_validation.py ............            [ 26%]
tests/test_workflow_generation.py ...............       [ 60%]
tests/test_agent_integration.py ..................      [100%]

============================== 45 passed in 2.34s =============================

Project Automata Configuration
==============================
Environment: development
Debug: True
...
✓ Configuration valid
```

---

## Configuration

### Step 1: Create Environment File

```bash
# Copy example environment file
cp .env.example .env

# Edit with your favorite editor
nano .env  # or vim, code, etc.
```

### Step 2: Basic Configuration

**Minimum required (development):**

```bash
# .env
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
```

### Step 3: Advanced Configuration

**For production:**

```bash
# .env
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# Security (generate secure key: python -c "import secrets; print(secrets.token_urlsafe(32))")
SECRET_KEY=your_generated_32_character_secret_key_here

# Paths (optional, defaults work for most cases)
KNOWLEDGE_BASE_DIR=./knowledge_base
WORKFLOWS_DIR=./workflows
LOGS_DIR=./logs
```

### Configuration Validation

```bash
# Validate configuration
python config.py

# Should show all settings and validation status
```

---

## API Keys & Subscriptions

**Note:** API keys are **optional** for development. The system uses simulated data by default. Real API integration required only for production web research.

### Free Tier Available

All required APIs offer free tiers sufficient for development and light production use.

---

### 1. Reddit API (Optional - Free)

**Purpose:** Research n8n workflows and discussions from r/n8n, r/automation

**Free Tier:** 60 requests/minute

**Steps to Get API Key:**

1. **Create Reddit Account**
   - Go to https://www.reddit.com
   - Sign up (free)

2. **Create Application**
   - Visit https://www.reddit.com/prefs/apps
   - Click "Create App" or "Create Another App"
   - Fill in:
     - **Name:** Project Automata
     - **App type:** Script
     - **Description:** n8n workflow research
     - **Redirect URI:** http://localhost:8080
   - Click "Create app"

3. **Get Credentials**
   - **Client ID:** Under app name (14 characters)
   - **Client Secret:** Click "secret" to reveal

4. **Add to .env**
   ```bash
   REDDIT_CLIENT_ID=your_14_char_client_id
   REDDIT_CLIENT_SECRET=your_secret_here
   REDDIT_USER_AGENT=ProjectAutomata/2.0
   ENABLE_WEB_RESEARCH=true
   ```

**Cost:** FREE (60 req/min limit)

---

### 2. YouTube Data API (Optional - Free)

**Purpose:** Research n8n tutorial videos for workflow patterns

**Free Tier:** 10,000 quota units/day (~100 video searches)

**Steps to Get API Key:**

1. **Create Google Cloud Project**
   - Go to https://console.cloud.google.com
   - Sign in with Google account
   - Click "Select a project" → "New Project"
   - Name: "Project Automata"
   - Click "Create"

2. **Enable YouTube Data API**
   - In dashboard, go to "APIs & Services" → "Library"
   - Search "YouTube Data API v3"
   - Click on it → Click "Enable"

3. **Create API Key**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "API Key"
   - Copy the generated key
   - (Optional) Click "Restrict Key" for security:
     - API restrictions → "YouTube Data API v3"
     - Application restrictions → "None" (for local dev)

4. **Add to .env**
   ```bash
   YOUTUBE_API_KEY=your_api_key_here
   ENABLE_WEB_RESEARCH=true
   ```

**Cost:** FREE (10K quota/day)

---

### 3. Twitter API (Optional - Free with limits)

**Purpose:** Monitor #n8n, #automation hashtags for tips

**Free Tier:** Basic tier available (500K tweets/month read)

**Steps to Get API Key:**

1. **Apply for Developer Account**
   - Go to https://developer.twitter.com
   - Sign in with Twitter account
   - Click "Apply" for developer access
   - Fill out application (hobby/learning project)
   - Wait for approval (usually instant to 24 hours)

2. **Create App**
   - Go to Developer Portal → "Projects & Apps"
   - Create new app: "Project Automata"
   - Select "Read" permissions

3. **Get Keys**
   - In app settings, go to "Keys and tokens"
   - Generate:
     - API Key
     - API Key Secret
     - Access Token
     - Access Token Secret

4. **Add to .env**
   ```bash
   TWITTER_API_KEY=your_api_key
   TWITTER_API_SECRET=your_api_secret
   TWITTER_ACCESS_TOKEN=your_access_token
   TWITTER_ACCESS_SECRET=your_access_secret
   ENABLE_WEB_RESEARCH=true
   ```

**Cost:** FREE Basic tier, $100/month for enhanced

---

### 4. GitHub API (Optional - Free)

**Purpose:** Research n8n workflow examples from GitHub repositories

**Free Tier:** 5,000 requests/hour (authenticated)

**Steps to Get Token:**

1. **Create Personal Access Token**
   - Go to https://github.com/settings/tokens
   - Click "Generate new token" → "Generate new token (classic)"
   - Name: "Project Automata"
   - Select scopes:
     - [x] `public_repo` (read public repositories)
   - Click "Generate token"
   - **Copy token immediately** (shown only once)

2. **Add to .env**
   ```bash
   GITHUB_TOKEN=your_token_here
   ENABLE_WEB_RESEARCH=true
   ```

**Cost:** FREE (5K req/hour)

---

### 5. n8n API (Optional - Free for self-hosted)

**Purpose:** Test generated workflows in real n8n instance

**Free Options:**
- Self-hosted (free, unlimited executions)
- n8n Cloud (execution-based pricing, see below)

**Setup:**

**Option A: Self-Hosted (Recommended for development)**

```bash
# Using Docker
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n

# Or using npm
npm install -g n8n
n8n start
```

**Option B: n8n Cloud**

1. Sign up at https://n8n.io
2. Create workspace
3. Go to Settings → API
4. Generate API key

**Add to .env:**
```bash
N8N_API_URL=http://localhost:5678/api/v1  # or cloud URL
N8N_API_KEY=your_api_key_here
```

**Cost (2025 Pricing):**
- **Self-hosted:** FREE (unlimited workflows & executions)
- **n8n Cloud:** Execution-based pricing (see details below)

#### n8n Cloud Pricing Tiers (2025)

**Note:** n8n now charges based on **workflow executions**, not workflow count. One execution = one complete workflow run, regardless of complexity or number of nodes.

| Plan | Monthly Cost | Executions Included | Key Features |
|------|--------------|---------------------|--------------|
| **Starter** | $20/month | 2,500 executions | Basic support, 5 concurrent executions, 320MiB RAM |
| **Pro** | $50/month | 10,000 executions | Priority support, environment variables, webhook auth |
| **Business** | Custom | 300,000+ executions | Advanced features, overage: 4,000 EUR per 300K executions |
| **Enterprise** | Custom | Custom limits | Dedicated support, SSO, SLA, custom infrastructure |

**Important Notes:**
- Unlimited workflows and users across all plans (no workflow count limits)
- If you exceed your execution quota, workflows continue running but overage charges apply
- Free trial available for testing (limited executions)
- For current pricing, always check: https://n8n.io/pricing

---

### Summary: API Costs

| Service | Free Tier | Paid Tier | Recommended For |
|---------|-----------|-----------|-----------------|
| Reddit | 60 req/min | N/A | Development & Production |
| YouTube | 10K quota/day | Pay as you go | Development & Production |
| Twitter | 500K tweets/month | $100/month | Development only |
| GitHub | 5K req/hour | N/A | Development & Production |
| n8n (self-hosted) | Unlimited | N/A | Development & Production |
| n8n (cloud) | Trial available | $20-$50+/month (execution-based) | Production (managed) |

**Total Cost for Development (Self-Hosted n8n):** $0 (all free tiers)
**Total Cost for Development (n8n Cloud):** $20+/month (depending on execution volume)
**Total Cost for Production:** $0-$170/month (depending on features & n8n hosting choice)

---

## Running the System

### Development Mode

```bash
# Activate virtual environment
source venv/bin/activate

# Run web research (simulated by default)
python scripts/run_web_research.py

# Test NL parser
python -m skills.nl_prompt_parser

# Generate workflow from template
python -c "
from skills.enhanced_templates import get_template_by_name
import json
workflow = get_template_by_name('webhook_db_slack')
print(json.dumps(workflow, indent=2))
" > workflows/test_workflow.json

# Validate workflow
python -c "
from skills.parse_n8n_schema import parse_workflow_file
workflow = parse_workflow_file('workflows/test_workflow.json')
print(f'Valid: {workflow is not None}')
print(f'Nodes: {workflow.node_count}')
"
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_schema_validation.py -v

# Run with coverage
pytest tests/ --cov=skills --cov=agents --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Interactive Python Shell

```bash
# Start Python shell with project imports
python

>>> from skills.knowledge_base import KnowledgeBase
>>> from skills.nl_prompt_parser import NLPromptParser
>>>
>>> # Load knowledge base
>>> kb = KnowledgeBase()
>>> print(kb.get_statistics())
>>>
>>> # Parse natural language
>>> parser = NLPromptParser(kb)
>>> result = parser.parse("When webhook arrives, save to database")
>>> print(result.suggested_template)
'webhook_db_slack'
```

---

## Testing

### Unit Tests

```bash
# Schema validation tests
pytest tests/test_schema_validation.py -v

# Workflow generation tests
pytest tests/test_workflow_generation.py -v

# Agent integration tests
pytest tests/test_agent_integration.py -v
```

### Integration Tests

```bash
# Test full workflow generation pipeline
python -c "
from skills.nl_prompt_parser import NLPromptParser
from skills.enhanced_templates import get_template_by_name
from skills.parse_n8n_schema import parse_workflow_json

# Parse prompt
parser = NLPromptParser()
spec = parser.generate_workflow_spec('When webhook arrives, save to database and send Slack notification')
print(f'Template: {spec[\"suggested_template\"]}')

# Generate workflow
workflow = get_template_by_name(spec['suggested_template'])

# Validate
parsed = parse_workflow_json(workflow)
print(f'Valid: {parsed is not None}')
print(f'Nodes: {parsed.node_count}')
"
```

### Manual Testing

```bash
# 1. Generate workflows from NL prompts
python -c "
from skills.nl_prompt_parser import NLPromptParser
prompts = [
    'When I receive a webhook, save to database and send Slack',
    'Every hour, sync data from API with retry logic',
    'Monitor RSS feed and post to Twitter'
]
parser = NLPromptParser()
for prompt in prompts:
    spec = parser.generate_workflow_spec(prompt)
    print(f'{prompt}')
    print(f'  → {spec[\"suggested_template\"]} ({spec[\"confidence\"]:.0%})')
"

# 2. Validate all sample workflows
python -c "
from pathlib import Path
from skills.parse_n8n_schema import parse_workflow_file

workflows_dir = Path('workflows')
for workflow_file in workflows_dir.glob('*.json'):
    result = parse_workflow_file(str(workflow_file))
    status = '✓' if result else '✗'
    print(f'{status} {workflow_file.name}')
"

# 3. Test knowledge base
python scripts/run_web_research.py
```

---

## Production Deployment

### Option 1: Direct Server Deployment

**Requirements:**
- Ubuntu 20.04+ server
- Python 3.9+
- sudo access

```bash
# 1. SSH into server
ssh user@your-server.com

# 2. Install dependencies
sudo apt update
sudo apt install python3.9 python3.9-venv python3-pip git

# 3. Clone repository
git clone https://github.com/drjlsmith10/n8er.git
cd n8er/automata-n8n

# 4. Setup virtual environment
python3.9 -m venv venv
source venv/bin/activate

# 5. Install dependencies
pip install -r requirements.txt
pip install -e .

# 6. Configure environment
cp .env.example .env
nano .env
# Set ENVIRONMENT=production, add API keys, set SECRET_KEY

# 7. Run initial setup
python config.py  # Verify configuration
pytest tests/ -v  # Run tests

# 8. Start service (systemd)
sudo cp deployment/automata.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable automata
sudo systemctl start automata
sudo systemctl status automata
```

### Option 2: Docker Deployment

**Prerequisites:** Docker installed

**Create Dockerfile** (if not exists):

```dockerfile
# Save as: Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .
RUN pip install -e .

# Create necessary directories
RUN mkdir -p knowledge_base workflows logs

# Run configuration check
RUN python config.py

# Expose ports (if running web API in future)
# EXPOSE 8000

# Default command
CMD ["python", "scripts/run_web_research.py"]
```

**Build and run:**

```bash
# Build image
docker build -t project-automata:2.0.0 .

# Run container
docker run -it --rm \
  -v $(pwd)/knowledge_base:/app/knowledge_base \
  -v $(pwd)/workflows:/app/workflows \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/.env:/app/.env \
  project-automata:2.0.0

# Or using docker-compose
docker-compose up -d
```

**docker-compose.yml:**

```yaml
version: '3.8'

services:
  automata:
    build: .
    image: project-automata:2.0.0
    container_name: automata
    volumes:
      - ./knowledge_base:/app/knowledge_base
      - ./workflows:/app/workflows
      - ./logs:/app/logs
      - ./.env:/app/.env
    environment:
      - ENVIRONMENT=production
    restart: unless-stopped
```

### Option 3: Cloud Platform Deployment

#### AWS Lambda (Serverless)

```bash
# Package application
pip install -r requirements.txt -t package/
cp -r skills agents package/
cd package && zip -r ../automata.zip .

# Deploy to Lambda
aws lambda create-function \
  --function-name project-automata \
  --runtime python3.11 \
  --handler lambda_handler.main \
  --zip-file fileb://automata.zip \
  --role arn:aws:iam::YOUR_ACCOUNT:role/lambda-role
```

#### Heroku

```bash
# Install Heroku CLI
# Create Procfile
echo "worker: python scripts/run_web_research.py" > Procfile

# Deploy
heroku create project-automata
git push heroku main
heroku ps:scale worker=1
```

#### Google Cloud Run

```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT_ID/automata
gcloud run deploy automata \
  --image gcr.io/PROJECT_ID/automata \
  --platform managed
```

---

## Security Checklist (Production)

- [ ] Set strong SECRET_KEY (32+ characters)
- [ ] Set DEBUG=false
- [ ] Set ENVIRONMENT=production
- [ ] Rotate API keys regularly
- [ ] Use HTTPS/TLS for all connections
- [ ] Enable rate limiting
- [ ] Set up firewall rules
- [ ] Enable logging and monitoring
- [ ] Regular security updates
- [ ] Backup knowledge base regularly

---

## Monitoring & Maintenance

### Logs

```bash
# View logs
tail -f logs/automata.log

# Search logs
grep ERROR logs/automata.log

# Rotate logs (in production)
logrotate /etc/logrotate.d/automata
```

### Health Checks

```bash
# Check if system is running
ps aux | grep python

# Check knowledge base
python -c "
from skills.knowledge_base import KnowledgeBase
kb = KnowledgeBase()
print(kb.get_statistics())
"

# Test workflow generation
python -c "
from skills.nl_prompt_parser import NLPromptParser
parser = NLPromptParser()
spec = parser.generate_workflow_spec('test webhook')
print(f'System healthy: {spec is not None}')
"
```

### Backups

```bash
# Backup knowledge base
tar -czf backup-$(date +%Y%m%d).tar.gz knowledge_base/

# Restore from backup
tar -xzf backup-20251108.tar.gz
```

---

## Troubleshooting

### Common Issues

#### Issue: "ModuleNotFoundError"

```bash
# Solution: Install dependencies
pip install -r requirements.txt
pip install -e .
```

#### Issue: "Permission denied" on logs directory

```bash
# Solution: Create logs directory
mkdir -p logs
chmod 755 logs
```

#### Issue: Tests failing

```bash
# Solution: Check Python version
python --version  # Should be 3.9+

# Reinstall dependencies
pip install -r requirements.txt --upgrade

# Run tests with verbose output
pytest tests/ -v --tb=short
```

#### Issue: API rate limiting

```bash
# Solution: Check .env settings
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_MINUTE=60

# Reduce request frequency or upgrade API tier
```

#### Issue: Knowledge base not found

```bash
# Solution: Run research script to populate
python scripts/run_web_research.py

# Or check KNOWLEDGE_BASE_DIR in .env
```

### Getting Help

1. **Check documentation:** `docs/` directory
2. **Review code:** `docs/CODE_REVIEW.md`
3. **Run diagnostics:** `python config.py`
4. **Check logs:** `tail -f logs/automata.log`
5. **GitHub Issues:** https://github.com/drjlsmith10/n8er/issues

---

## Next Steps

After deployment:

1. ✅ **Run web research** to populate knowledge base
2. ✅ **Test NL parsing** with your own prompts
3. ✅ **Generate workflows** and validate them
4. ✅ **Import to n8n** for real testing
5. ✅ **Monitor logs** for issues
6. ✅ **Schedule research** for continuous learning

---

**Deployment Guide Version:** 2.0.0-alpha
**Last Updated:** 2025-11-08
**Maintained By:** Project Automata Team
