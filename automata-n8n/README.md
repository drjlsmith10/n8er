# Project Automata: Autonomous n8n Workflow Builder

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![CI/CD](https://github.com/drjlsmith10/n8er/workflows/CI%2FCD%20Pipeline/badge.svg)](https://github.com/drjlsmith10/n8er/actions)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

**Version:** 2.0.0-alpha
**Status:** Open Source & Active Development
**Current Cycle:** Phase 2 - Architecture Simplification
**Focus:** Template-based workflow generation with keyword matching

> 🌟 **Now Open Source!** We're building the future of AI-assisted workflow automation together. [Star us on GitHub](https://github.com/drjlsmith10/n8er) to follow our progress!

---

## Vision

Project Automata is an autonomous R&D organization designed to build, test, and continuously improve the most capable AI-assisted n8n workflow generation system in existence. Through coordinated sub-agents and meta-learning loops, Automata achieves deeper reasoning, more rigorous validation, and cleaner code than traditional AI assistants.

## Core Philosophy

- **Autonomous Improvement:** Self-evaluating, self-critiquing, self-refining
- **Multi-Agent Coordination:** Specialized agents working in concert
- **Rigorous Validation:** Every output tested, validated, documented
- **Transparent Reasoning:** All logic chains traceable and documented
- **Continuous Learning:** Closed-loop improvement cycles

---

## Architecture Overview

```
automata-n8n/
├── agents/          # Individual AI agent scripts
├── skills/          # Reusable tools and utilities
├── workflows/       # Generated n8n workflow JSONs
├── docs/            # Architecture, changelogs, reports
└── tests/           # Automated validation suites
```

### Sub-Agents

1. **Researcher** - Mines documentation, examples, patterns
2. **Engineer** - Builds and refactors code modules
3. **Validator** - Verifies schemas, syntax, dependencies
4. **Tester** - Runs automated validation workflows
5. **Documenter** - Generates guides, diagrams, reports
6. **ProjectManager** - Oversees iteration planning

### Meta-Controller: Automata-Prime

The orchestration layer that:
- Coordinates all sub-agents
- Evaluates performance metrics
- Generates improvement directives
- Manages the learning loop

---

## Current Capabilities

### What Works Well ✅

- **Workflow JSON Generation** - Produces valid n8n workflow JSON from templates
- **Schema Validation** - Detects common JSON structure errors before n8n import
- **5 Production-Ready Templates** - Webhook→DB→Slack, Scheduled Sync, RSS→Social, CRM, Multi-API
- **Keyword Pattern Matching** - Matches prompts to templates using keyword scoring
- **Auto Node Versioning** - Automatically uses correct typeVersions for n8n 1.60+
- **Automated Testing** - 51 tests covering core functionality

### What's Experimental ⚠️

- **Keyword-based prompt matching** (NOT natural language understanding)
  - Works for prompts using expected keywords (~85% on test phrases)
  - May not understand complex or novel descriptions
  - Does NOT use AI/ML for semantic understanding
- **Built-in sample patterns** (NOT scraped from community)
  - 9 developer-curated workflow templates
  - Labeled as coming from Reddit/YouTube/Twitter for categorization
  - Actually created by Automata developers based on common patterns
- **Multi-agent architecture** - Most agents provide placeholder functionality

### What Requires Configuration 🔧

- **Real n8n validation** - Requires running n8n instance with API key
- **Web research** - Requires Reddit/YouTube/Twitter API keys for actual scraping
- Set `ENABLE_WEB_RESEARCH=true` in .env to use real APIs

### Known Limitations ❌

- Agent system is over-engineered for current capabilities
- Some agents (Tester, ProjectManager) return mock data only
- Knowledge base contains built-in samples, not actual community data
- NL parser is keyword matching, not semantic understanding

### Roadmap

- Simplify agent architecture (7 agents → 3)
- Require explicit opt-in for simulation mode
- Add real LLM integration for semantic prompt understanding
- Expand node support to 50+ types

---

## Quick Start

### Requirements

- **Python:** 3.11.9 or higher (tested on 3.11.9, compatible with 3.9-3.12)
- **Docker:** Optional for containerized deployment
- **n8n:** v1.60.0+ **REQUIRED** (Recommended: v1.60.1)
  - ⚠️ **Critical:** Generated workflows use modern node typeVersions optimized for n8n 1.60.0+
  - See `docs/n8n_compatibility_matrix.md` for detailed version requirements
  - Older versions (< 1.60.0) may have incompatible node typeVersions

### Installation

```bash
# Clone repository
git clone https://github.com/drjlsmith10/n8er.git
cd n8er/automata-n8n

# Install package and dependencies
pip install -e ".[dev]"

# Or just dependencies
pip install -r requirements.txt
```

### Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit with your API keys (all free tiers available)
nano .env
```

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed setup instructions.

### Generate a Workflow

```bash
python skills/generate_workflow_json.py --prompt "Send email when webhook receives data"
```

### Run Tests

```bash
pytest tests/
# Run with verbose output
pytest tests/ -v
# Run specific test file
pytest tests/test_workflow_generation.py
```

---

## Development Loop

```
Identify Gap → Spawn Agent → Implement → Test → Document → Evaluate → Improve
```

Each cycle:
1. Agent produces output
2. Validator checks correctness
3. Tester runs automated checks
4. Documenter logs reasoning
5. Automata-Prime evaluates and refines

---

## Evaluation Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Workflow schema validity | - | ≥90% |
| Node dependency accuracy | - | ≥85% |
| Code modularity | - | ≥85% |
| Documentation coverage | - | 100% |
| Test pass rate | - | ≥95% |

---

## Contributing

We welcome contributions from the community! Project Automata thrives on collaboration and continuous improvement.

### Ways to Contribute

- 🐛 **Report Bugs** - Found an issue? [Open a bug report](https://github.com/drjlsmith10/n8er/issues/new?template=bug_report.md)
- 💡 **Suggest Features** - Have an idea? [Submit a feature request](https://github.com/drjlsmith10/n8er/issues/new?template=feature_request.md)
- 🔧 **Submit Code** - Read our [Contributing Guidelines](CONTRIBUTING.md) and submit a PR
- 📖 **Improve Docs** - Help make our documentation clearer
- 🧪 **Share Workflows** - Contribute real-world n8n patterns to our knowledge base
- 💬 **Help Others** - Answer questions in Discussions

### Getting Started

1. Read the [Contributing Guidelines](CONTRIBUTING.md)
2. Check out [Good First Issues](https://github.com/drjlsmith10/n8er/labels/good%20first%20issue)
3. Join our community discussions
4. Follow our [Code of Conduct](CODE_OF_CONDUCT.md)

### Development Process

The system self-improves through meta-evaluation cycles documented in `docs/changelog.md` and `docs/eval_report.md`. Every contribution goes through:

1. Automated testing (51+ tests)
2. Code quality checks (Black, Flake8, mypy)
3. Security scanning
4. Community review

---

## Community & Support

- 📚 **Documentation**: [docs/](docs/)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/drjlsmith10/n8er/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/drjlsmith10/n8er/discussions)
- 🔒 **Security**: See [SECURITY.md](SECURITY.md) for vulnerability reporting

### Show Your Support

If Project Automata is useful to you:

⭐ **Star this repository** to show your support
🐦 **Share on Twitter** to help others discover it
🤝 **Contribute** to make it even better

---

## License

MIT License - See LICENSE file for details

---

## Contact

Project maintained by Automata-Prime
Documentation auto-generated on: 2025-11-20
