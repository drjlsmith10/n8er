# Project Automata: System Architecture

**Document Version:** 1.0
**Last Updated:** 2025-11-08
**Cycle:** 01

---

## Architectural Overview

Project Automata employs a **hierarchical multi-agent architecture** with a meta-controller (Automata-Prime) orchestrating specialized sub-agents in a closed learning loop.

```
┌─────────────────────────────────────────────────────────────────┐
│                        AUTOMATA-PRIME                           │
│                    (Meta-Controller Layer)                      │
│                                                                 │
│  • Coordinates all agents                                      │
│  • Evaluates performance metrics                               │
│  • Generates improvement directives                            │
│  • Manages learning cycles                                     │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│  Researcher  │      │   Engineer   │      │  Validator   │
│              │      │              │      │              │
│ • Mine docs  │      │ • Build code │      │ • Check      │
│ • Extract    │      │ • Refactor   │      │   schemas    │
│   patterns   │      │ • Optimize   │      │ • Verify     │
└──────────────┘      └──────────────┘      │   logic      │
        │                     │              └──────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│    Tester    │      │  Documenter  │      │ProjectManager│
│              │      │              │      │              │
│ • Run tests  │      │ • Generate   │      │ • Plan       │
│ • Validate   │      │   docs       │      │   iterations │
│ • Report     │      │ • Changelog  │      │ • Version    │
└──────────────┘      └──────────────┘      └──────────────┘
```

---

## Component Architecture

### 1. Agent Layer (`/agents`)

Each agent is a specialized module with:
- **Input schema**: Standardized request format
- **Processing logic**: Core capability implementation
- **Output schema**: Structured response format
- **Logging**: Inline reasoning traces

#### Agent Specifications

**Researcher Agent** (`agents/researcher.py`)
```python
Input:  {"task": "research", "target": "n8n HTTP Request node"}
Output: {"patterns": [...], "examples": [...], "summary": "..."}
```

**Engineer Agent** (`agents/engineer.py`)
```python
Input:  {"task": "build", "spec": {...}, "module": "skills/..."}
Output: {"code": "...", "tests": "...", "reasoning": "..."}
```

**Validator Agent** (`agents/validator.py`)
```python
Input:  {"workflow": {...}, "schema_version": "1.0"}
Output: {"valid": true, "errors": [], "warnings": [...]}
```

**Tester Agent** (`agents/tester.py`)
```python
Input:  {"test_suite": "workflows", "target": "all"}
Output: {"passed": 42, "failed": 1, "coverage": "95%"}
```

**Documenter Agent** (`agents/documenter.py`)
```python
Input:  {"source": "code", "format": "markdown"}
Output: {"docs": "...", "diagrams": [...]}
```

**ProjectManager Agent** (`agents/project_manager.py`)
```python
Input:  {"cycle": 1, "metrics": {...}}
Output: {"plan": [...], "priorities": [...], "version": "1.1.0"}
```

---

### 2. Skills Layer (`/skills`)

Reusable utilities and tools that agents invoke:

**parse_n8n_schema.py**
- Parses n8n workflow JSON structures
- Extracts node definitions, connections, credentials
- Validates against n8n schema specifications
- Returns structured node graph

**generate_workflow_json.py**
- Takes high-level workflow description
- Applies learned patterns and templates
- Generates valid n8n workflow JSON
- Includes metadata, versioning, dependencies

**validate_dependencies.py**
- Checks node connection validity
- Verifies data flow paths
- Detects circular dependencies
- Ensures credential requirements met

**shared_methods.py**
- Common utilities (logging, file I/O, JSON handling)
- Shared configuration management
- Error handling patterns

---

### 3. Workflow Layer (`/workflows`)

Generated and validated n8n workflows:

```
workflows/
├── sample_webhook_email.json
├── sample_data_transform.json
├── sample_api_integration.json
└── templates/
    ├── trigger_action.json
    ├── etl_pipeline.json
    └── api_workflow.json
```

---

### 4. Testing Layer (`/tests`)

Automated validation suites:

```
tests/
├── test_schema_validation.py
├── test_workflow_generation.py
├── test_dependency_resolution.py
├── test_agent_integration.py
└── fixtures/
    ├── valid_workflows/
    └── invalid_workflows/
```

**Testing Strategy:**
- Unit tests for each skill module
- Integration tests for agent coordination
- Schema validation tests
- Workflow simulation tests
- Performance benchmarks

---

### 5. Meta-Evaluation Loop

```
┌─────────────────────────────────────────────────────────────┐
│  CYCLE N                                                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. EXECUTE                                                 │
│     └─> Agents perform tasks                               │
│                                                             │
│  2. VALIDATE                                                │
│     └─> Run test suites, check metrics                     │
│                                                             │
│  3. EVALUATE                                                │
│     └─> Score agents against benchmarks                    │
│     └─> Identify improvement opportunities                 │
│                                                             │
│  4. CRITIQUE                                                │
│     └─> Generate eval_report.md                            │
│     └─> Document successes and failures                    │
│                                                             │
│  5. REFINE                                                  │
│     └─> Rewrite low-scoring modules                        │
│     └─> Extract lessons to shared_methods                  │
│                                                             │
│  6. DOCUMENT                                                │
│     └─> Update changelog with deltas                       │
│     └─> Version bump if targets met                        │
│                                                             │
│  7. REPEAT                                                  │
│     └─> Start CYCLE N+1                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### Workflow Generation Flow

```
User Prompt
    │
    ▼
Researcher ──────> Extract patterns from docs/examples
    │
    ▼
Engineer ────────> Apply patterns to generate workflow JSON
    │
    ▼
Validator ───────> Check schema, dependencies, logic
    │
    ▼
Tester ──────────> Simulate execution, validate outputs
    │
    ▼
Documenter ──────> Generate usage guide, reasoning log
    │
    ▼
ProjectManager ──> Log metrics, plan improvements
    │
    ▼
Automata-Prime ──> Evaluate cycle, trigger refinements
```

---

## Technology Stack

### Core
- **Language:** Python 3.9+ (primary), TypeScript (optional)
- **Schema Validation:** JSON Schema, Pydantic
- **Testing:** pytest, unittest
- **Documentation:** Markdown, Mermaid diagrams

### n8n Integration
- **n8n CLI:** For workflow import/export
- **n8n API:** For programmatic workflow management
- **Schema Definitions:** Based on n8n v1.x specification

### AI/ML Components
- **Pattern Mining:** NLP for documentation extraction
- **Code Generation:** Template-based with learned patterns
- **Evaluation:** Custom metrics framework

---

## n8n Node Coverage

### Currently Supported Nodes (v2.0.0-alpha)

Project Automata currently has deep integration and template support for **5 core n8n nodes**:

| Node Type | Purpose | Template Support | Knowledge Base |
|-----------|---------|------------------|----------------|
| `n8n-nodes-base.webhook` | HTTP webhook trigger | ✅ Full | Extensive |
| `n8n-nodes-base.httpRequest` | External API calls | ✅ Full | Extensive |
| `n8n-nodes-base.function` | JavaScript code execution | ✅ Full | Extensive |
| `n8n-nodes-base.if` | Conditional branching | ✅ Full | Moderate |
| `n8n-nodes-base.slack` | Slack notifications | ✅ Full | Moderate |

### Additional Nodes with Partial Support

The following nodes are referenced in templates but lack comprehensive documentation:

| Node Type | Status | Priority |
|-----------|--------|----------|
| `n8n-nodes-base.postgres` | Used in templates | HIGH |
| `n8n-nodes-base.cron` | Used in templates | HIGH |
| `n8n-nodes-base.wait` | Used in templates | MEDIUM |
| `n8n-nodes-base.emailSend` | Used in templates | HIGH |
| `n8n-nodes-base.merge` | Used in templates | MEDIUM |
| `n8n-nodes-base.googleSheets` | Used in templates | HIGH |
| `n8n-nodes-base.twitter` | Used in templates | LOW |
| `n8n-nodes-base.linkedIn` | Used in templates | LOW |

### Node Coverage Statistics

- **Total n8n Core Nodes:** 400+ available
- **Nodes with Full Support:** 5 (1.25%)
- **Nodes with Partial Support:** 8 (2%)
- **Target for v3.0:** 50+ nodes (12.5%)

### Expansion Roadmap

#### Phase 1: Core Integration Nodes (High Priority)
**Target:** Cycle-03 (Q1 2025)

Essential nodes for common workflow patterns:

1. **Database Nodes**
   - PostgreSQL, MySQL, MongoDB
   - Redis, Elasticsearch
   - Priority: CRITICAL - enables data persistence

2. **Communication Nodes**
   - Email (Send/Read)
   - Discord, Telegram
   - Priority: HIGH - common in automation workflows

3. **Data Transformation**
   - Code, Set, Item Lists
   - Split In Batches, Aggregate
   - Priority: HIGH - fundamental data operations

4. **Cloud Storage**
   - Google Drive, Dropbox, S3
   - Priority: MEDIUM - file handling capabilities

#### Phase 2: Business Automation Nodes (Medium Priority)
**Target:** Cycle-04 (Q2 2025)

Productivity and business tools:

1. **Productivity Suites**
   - Google Workspace (Sheets, Docs, Calendar)
   - Microsoft 365 (Excel, Outlook, Teams)
   - Notion, Airtable

2. **CRM & Sales**
   - Salesforce, HubSpot, Pipedrive
   - Zendesk, Intercom

3. **Project Management**
   - Jira, Trello, Asana
   - GitHub, GitLab

#### Phase 3: AI/ML & Advanced Integration (Low Priority)
**Target:** Cycle-05+ (Q3 2025)

Specialized and emerging nodes:

1. **AI/ML Services**
   - OpenAI, Anthropic (Claude)
   - HuggingFace, Stability AI
   - Vector databases (Pinecone, Weaviate)

2. **Cloud Providers**
   - AWS (Lambda, S3, DynamoDB)
   - GCP, Azure services

3. **Specialized Services**
   - Payment gateways (Stripe, PayPal)
   - Analytics (Google Analytics, Mixpanel)
   - Social media platforms

### Node Support Requirements

For a node to achieve "Full Support" status:

1. **Template Library**
   - At least 2 workflow templates using the node
   - Cover common use cases
   - Include error handling patterns

2. **Knowledge Base**
   - Common parameters documented
   - Known errors and solutions cataloged
   - Best practices and tips collected

3. **Test Coverage**
   - Unit tests for node parameter generation
   - Integration tests with real n8n
   - Validation tests for common patterns

4. **Documentation**
   - Node usage guide in EXPRESSION_SYNTAX.md or dedicated file
   - Examples in workflow samples
   - Troubleshooting section

### Community Contributions

We welcome contributions to expand node coverage:

1. **Share Workflows:** Submit real-world examples using nodes
2. **Document Patterns:** Contribute best practices and error solutions
3. **Write Templates:** Create reusable workflow patterns
4. **Test Integration:** Validate node compatibility with current n8n versions

See [CONTRIBUTING.md](../CONTRIBUTING.md) for details on adding node support.

### Node Type Version Tracking

**Important:** n8n nodes have version numbers (typeVersion) that affect compatibility:

| Node | Current typeVersion | Automata Support | Notes |
|------|---------------------|------------------|-------|
| webhook | 1.0 | ✅ v1 | Version 2.0 adds authentication options |
| httpRequest | 4.x | ⚠️ v1 | Need to update to v4 (see CRITICAL_REVIEW.md #1) |
| function | 1.0 | ✅ v1 | Stable across versions |
| if | 1.0 | ✅ v1 | Version 2.0 changes condition structure |
| slack | 2.x | ⚠️ v1 | Need to update to v2 |

**Action Item:** Cycle-03 will address typeVersion updates for all supported nodes.

---

## Security & Best Practices

1. **Schema Validation:** All workflows validated before output
2. **Credential Handling:** Never expose credentials in generated code
3. **Error Handling:** Comprehensive try-catch with logging
4. **Version Control:** All changes tracked with reasoning
5. **Code Quality:** PEP8 compliance, type hints, docstrings
6. **Testing Coverage:** Minimum 80% coverage target

---

## Performance Considerations

- **Caching:** Store parsed schemas and patterns
- **Parallel Processing:** Run independent validations concurrently
- **Incremental Learning:** Update patterns without full retraining
- **Lazy Loading:** Load modules only when needed

---

## Extension Points

The architecture supports:
- Adding new agent types
- Custom skill modules
- Alternative workflow formats (Zapier, Make, etc.)
- External knowledge sources (APIs, databases)
- Custom evaluation metrics

---

## Versioning Strategy

- **Major:** Breaking changes to architecture
- **Minor:** New agents, skills, or capabilities
- **Patch:** Bug fixes, refinements, documentation

---

## Future Enhancements

1. **Natural Language Understanding:** Advanced prompt parsing
2. **Real-time Simulation:** Execute workflows in sandbox
3. **Community Learning:** Mine GitHub, forums, Discord
4. **Multi-format Support:** Export to multiple automation platforms
5. **Visual Workflow Builder:** GUI for workflow editing
6. **Adaptive Learning:** Reinforcement learning for pattern optimization

---

**Document Maintained By:** Documenter Agent
**Architecture Approved By:** Automata-Prime
**Next Review:** Cycle-02
