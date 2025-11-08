# Project Automata: Autonomous n8n Workflow Builder

**Version:** 1.0.0-alpha
**Status:** Active Development
**Branch:** Cycle-01

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

### Current (v1.0.0-alpha)
- ✅ Parse n8n workflow schemas
- ✅ Generate workflow JSON from templates
- ✅ Validate node structure and dependencies
- ✅ Automated testing framework
- ✅ Multi-agent coordination framework

### Roadmap
- 🔄 Natural language → workflow generation
- 🔄 Advanced dependency resolution
- 🔄 Community pattern mining
- 🔄 Real-time workflow simulation
- 🔄 Self-improving evaluation metrics

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
