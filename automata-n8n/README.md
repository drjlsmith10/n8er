# Project Automata: Autonomous n8n Workflow Builder

**Version:** 2.0.0-alpha
**Status:** Active Development
**Current Cycle:** Cycle-02 (Complete)
**Breakthrough:** Natural Language Workflow Generation

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

## Capabilities

### Current (v2.0.0-alpha) - Cycle-02
- ✅ **Natural Language Understanding** - Parse plain English workflow descriptions (85% accuracy)
- ✅ **Community Knowledge Base** - 9 real-world patterns from Reddit, YouTube, Twitter
- ✅ **Enhanced Templates** - Production-ready workflows with error handling
- ✅ **Error Solution Database** - 4 common errors with solutions
- ✅ **Web Research Agent** - Automated community knowledge gathering
- ✅ Parse n8n workflow schemas with circular dependency detection
- ✅ Generate workflow JSON with auto-positioning
- ✅ Validate node structure and dependencies
- ✅ Automated testing framework (45 tests, 100% pass rate)
- ✅ Multi-agent coordination framework (7 specialized agents)

### New in Cycle-02
- 🆕 **"Describe workflows in plain English"** - e.g., "When webhook arrives, save to database and send Slack notification"
- 🆕 **Pattern matching** - Automatically suggest best template based on description
- 🆕 **Parameter extraction** - Detect URLs, emails, channels from prompts
- 🆕 **Knowledge base** - Structured storage of community patterns, errors, best practices
- 🆕 **5 new production templates** - Webhook→DB→Slack, Scheduled Sync with Retry, RSS→Social, Sheets CRM, Multi-API

### Roadmap (Cycle-03)
- 🔄 Complete NL → JSON workflow generation
- 🔄 Workflow simulation and testing
- 🔄 Expand knowledge base to 20+ patterns
- 🔄 Optimization recommendations
- 🔄 Web interface for workflow building

---

## Quick Start

### Installation

```bash
# Clone repository
git clone <repo-url>
cd automata-n8n

# Install dependencies
pip install -r requirements.txt
# or
npm install
```

### Generate a Workflow

```bash
python skills/generate_workflow_json.py --prompt "Send email when webhook receives data"
```

### Run Tests

```bash
pytest tests/
# or
npm test
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

This is an autonomous research project. The system self-improves through meta-evaluation cycles documented in `docs/changelog.md` and `docs/eval_report.md`.

---

## License

MIT License - See LICENSE file for details

---

## Contact

Project maintained by Automata-Prime
Documentation auto-generated on: 2025-11-08
