# Automata Implementation Plan

**Created:** 2025-11-25
**Based on:** AUTOMATA_REVIEW_2025-11.md

---

## Overview

This plan addresses the critical issues identified in the November 2025 review. Work is organized into three phases, with each phase building on the previous.

**Rule:** Do not start Phase 2 until Phase 1 is complete. Do not start Phase 3 until Phase 2 is complete.

---

## PHASE 1: Fix n8n Compatibility (CRITICAL)

**Goal:** Generated workflows should import and execute correctly in n8n 1.60+

**Estimated Tasks:** 9
**Priority:** CRITICAL - Must complete before any other work

### Task 1.1: Create Node TypeVersion Mapping

**File:** `skills/n8n_node_versions.py` (NEW)

Create a centralized mapping of node types to their current typeVersion:

```python
NODE_TYPE_VERSIONS = {
    "n8n-nodes-base.webhook": 2,
    "n8n-nodes-base.httpRequest": 4,
    "n8n-nodes-base.function": 1,
    "n8n-nodes-base.if": 2,
    "n8n-nodes-base.switch": 3,
    "n8n-nodes-base.set": 3,
    "n8n-nodes-base.code": 2,
    "n8n-nodes-base.slack": 2,
    "n8n-nodes-base.emailSend": 2,
    "n8n-nodes-base.postgres": 2,
    "n8n-nodes-base.manualTrigger": 1,
    "n8n-nodes-base.cron": 1,
    "n8n-nodes-base.noOp": 1,
    "n8n-nodes-base.merge": 3,
    "n8n-nodes-base.splitInBatches": 3,
}

def get_node_version(node_type: str) -> int:
    return NODE_TYPE_VERSIONS.get(node_type, 1)
```

**Acceptance Criteria:**
- [ ] File created with at least 15 common node types
- [ ] Function `get_node_version()` exported
- [ ] Unit tests for version lookup

---

### Task 1.2: Add Missing Workflow Schema Fields

**File:** `skills/generate_workflow_json.py`

Add required fields to WorkflowBuilder `__init__`:

```python
def __init__(self, name: str = "Generated Workflow"):
    # ... existing code ...

    # ADD these fields:
    self.workflow_id = str(uuid.uuid4())
    self.version_id = str(uuid.uuid4())
    self.meta = {
        "templateCredsSetupCompleted": True,
        "instanceId": str(uuid.uuid4())
    }
    self.pin_data: Dict = {}
    self.static_data: Dict = {}
```

**Acceptance Criteria:**
- [ ] `workflow_id` generated as UUID
- [ ] `version_id` generated as UUID
- [ ] `meta` dict with required fields
- [ ] `pin_data` and `static_data` initialized as empty dicts

---

### Task 1.3: Update WorkflowBuilder.build()

**File:** `skills/generate_workflow_json.py`

Update the `build()` method to include all fields:

```python
def build(self, validate: bool = True) -> Dict:
    workflow = {
        "id": self.workflow_id,
        "name": self.name,
        "nodes": self.nodes,
        "connections": self.connections,
        "settings": {
            "executionOrder": "v1",
            "saveExecutionProgress": False,
            "saveManualExecutions": True,
            "timezone": "UTC",
            "callerPolicy": "workflowsFromSameOwner",
        },
        "versionId": self.version_id,
        "meta": self.meta,
        "pinData": self.pin_data,
        "staticData": self.static_data,
        **self.metadata,
    }
    # ... rest of method
```

**Acceptance Criteria:**
- [ ] All 5 new fields included in output
- [ ] Settings expanded with all required options
- [ ] Existing tests still pass
- [ ] New tests verify field presence

---

### Task 1.4: Fix IF Node to v2 Format

**File:** `skills/enhanced_templates.py`

Update IF node parameters from v1 to v2 format:

```python
# BEFORE (v1 - outdated):
"parameters": {
    "conditions": {
        "boolean": [],
        "number": [{"value1": "...", "operation": "largerEqual", "value2": 1}]
    }
}

# AFTER (v2 - current):
"parameters": {
    "conditions": {
        "options": {
            "caseSensitive": True,
            "leftValue": "",
            "typeValidation": "strict"
        },
        "conditions": [{
            "id": str(uuid.uuid4()),
            "leftValue": "={{ $json.rowCount }}",
            "rightValue": 1,
            "operator": {"type": "number", "operation": "gte"}
        }],
        "combinator": "and"
    }
}
```

**Acceptance Criteria:**
- [ ] All IF nodes use v2 parameter format
- [ ] typeVersion set to 2
- [ ] Tests updated for new format

---

### Task 1.5: Fix HTTP Request Node to v4 Format

**Files:** `skills/enhanced_templates.py`, `skills/generate_workflow_json.py`

Update HTTP Request nodes to use v4 format with proper structure.

**Acceptance Criteria:**
- [ ] typeVersion set to 4
- [ ] Parameter structure matches n8n 1.60+ expectations
- [ ] Authentication options properly structured

---

### Task 1.6: Fix emailSend Node to v2 Format

**Files:** `skills/enhanced_templates.py`, sample workflows

Update emailSend nodes:

```python
# v2 format:
{
    "type": "n8n-nodes-base.emailSend",
    "typeVersion": 2,
    "parameters": {
        "fromEmail": "...",
        "toEmail": "...",
        "subject": "...",
        "emailFormat": "text",
        "message": "...",
        "options": {}
    }
}
```

**Acceptance Criteria:**
- [ ] typeVersion set to 2
- [ ] `options` field present
- [ ] `emailFormat` specified

---

### Task 1.7: Pin n8n Version in Docker

**File:** `docker-compose.yml`

Change:
```yaml
# BEFORE:
image: n8nio/n8n:latest

# AFTER:
image: n8nio/n8n:1.60.1
```

**Acceptance Criteria:**
- [ ] Specific version pinned (not :latest)
- [ ] Version documented in README
- [ ] Tested that workflows import correctly

---

### Task 1.8: Add n8n Integration Test

**File:** `tests/test_n8n_integration.py`

Create integration test that:
1. Generates a workflow
2. Imports it to real n8n via API
3. Verifies import success
4. Cleans up (deletes workflow)

```python
@pytest.mark.integration
def test_workflow_imports_to_n8n():
    """Test that generated workflow can be imported to real n8n."""
    client = N8nApiClient.from_env()
    if not client:
        pytest.skip("n8n not configured")

    workflow = TemplateLibrary.webhook_to_email()

    # Import
    result = client.import_workflow(workflow)
    assert result.get("id") is not None

    # Cleanup
    client.delete_workflow(result["id"])
```

**Acceptance Criteria:**
- [ ] Test exists and passes when n8n available
- [ ] Test skips gracefully when n8n not configured
- [ ] At least one template tested

---

### Task 1.9: Update Templates to Use Version Mapping

**Files:** `skills/generate_workflow_json.py`, `skills/enhanced_templates.py`

Update `add_node()` to use version mapping:

```python
from skills.n8n_node_versions import get_node_version

def add_node(self, node_type: str, name: str, ...):
    # Auto-detect version if not specified
    if type_version is None:
        type_version = get_node_version(node_type)
```

**Acceptance Criteria:**
- [ ] Default typeVersion comes from mapping
- [ ] Manual override still works
- [ ] All templates produce correct versions

---

## PHASE 2: Simplify Architecture (HIGH PRIORITY)

**Goal:** Remove fake data, consolidate agents, honest documentation

**Estimated Tasks:** 9
**Priority:** HIGH - Complete after Phase 1

### Task 2.1: Remove Fake Source URLs

**File:** `agents/web_researcher.py`

Change hardcoded patterns:

```python
# BEFORE:
"source": "reddit",
"source_url": "https://reddit.com/r/n8n/comments/example1",

# AFTER:
"source": "automata_builtin",
"source_url": None,
"builtin": True,
```

**Acceptance Criteria:**
- [ ] No fake URLs in codebase
- [ ] Builtin patterns clearly marked
- [ ] Knowledge base load/save handles new format

---

### Task 2.2: Separate Builtin vs Learned Patterns

**Directory:** `knowledge_base/`

Restructure:
```
knowledge_base/
├── builtin/
│   ├── workflow_patterns.json
│   └── error_patterns.json
└── learned/
│   ├── .gitkeep
    └── (populated by actual API calls)
```

**Acceptance Criteria:**
- [ ] Directory structure created
- [ ] KnowledgeBase class updated to handle both
- [ ] Clear separation in code

---

### Task 2.3: Make Simulation Mode Explicit

**File:** `agents/web_researcher.py`, `config.py`

Require explicit flag for simulation:

```python
# config.py
ALLOW_SIMULATED_DATA: bool = os.getenv("ALLOW_SIMULATED_DATA", "false").lower() == "true"

# web_researcher.py
if not api_configured:
    if not config.ALLOW_SIMULATED_DATA:
        raise ConfigurationError(
            "Web research requires API keys. "
            "Set ALLOW_SIMULATED_DATA=true to use builtin patterns."
        )
    return self._get_builtin_patterns()
```

**Acceptance Criteria:**
- [ ] Simulation mode is opt-in, not default
- [ ] Clear error message when APIs missing
- [ ] Flag documented in .env.example

---

### Task 2.4: Consolidate Research Agents

**Files:** `agents/researcher.py`, `agents/web_researcher.py` → `agents/knowledge_agent.py`

Create single `KnowledgeAgent` that:
- Provides builtin patterns (always available)
- Fetches from APIs (when configured)
- Clearly indicates data source

**Acceptance Criteria:**
- [ ] Single agent replaces two
- [ ] Same functionality preserved
- [ ] Cleaner interface

---

### Task 2.5: Consolidate Builder Agents

**Files:** `agents/engineer.py`, `agents/documenter.py` → `agents/builder_agent.py`

Create single `BuilderAgent` that:
- Generates workflow JSON
- Generates documentation
- Handles code review tasks

**Acceptance Criteria:**
- [ ] Single agent replaces two
- [ ] Same functionality preserved

---

### Task 2.6: Remove Mock-Only Agents

**Files:** `agents/tester.py`, `agents/project_manager.py`

These agents return only mock data. Options:
1. Delete entirely
2. Keep as stubs with clear "NOT IMPLEMENTED" status

**Recommendation:** Delete. They add complexity without value.

**Acceptance Criteria:**
- [ ] Files removed or clearly marked as stubs
- [ ] No references in main code
- [ ] Agent count reduced from 7 to 3

---

### Task 2.7: Integrate Real Validation

**File:** `agents/validator.py`

Update ValidatorAgent to use N8nApiClient:

```python
def __init__(self, n8n_client: Optional[N8nApiClient] = None):
    self.client = n8n_client or N8nApiClient.from_env()

def _validate_workflow(self, params: Dict) -> Dict:
    # Local validation (fast)
    local_errors = self._local_check(workflow)

    # Real n8n validation (if client available)
    if self.client:
        is_valid, api_errors = self.client.validate_workflow_import(workflow)
        # Merge results
```

**Acceptance Criteria:**
- [ ] Uses N8nApiClient when available
- [ ] Falls back to local-only with warning
- [ ] Better error messages

---

### Task 2.8: Rename NL Parser Honestly

**File:** `skills/nl_prompt_parser.py` → `skills/keyword_pattern_matcher.py`

Rename class and update documentation:

```python
class KeywordPatternMatcher:
    """
    Matches workflow descriptions to templates using keyword patterns.

    NOTE: This is keyword matching, not natural language understanding.
    Works well for simple, predefined phrases. Complex or novel
    descriptions may not match correctly.
    """
```

**Acceptance Criteria:**
- [ ] File and class renamed
- [ ] Documentation is honest about capabilities
- [ ] All imports updated

---

### Task 2.9: Update README Honestly

**File:** `README.md`

Add "What Works / What's Limited" section:

```markdown
## Current Capabilities

### What Works Well
- Workflow JSON generation from templates
- Schema validation for common errors
- 5 production-tested workflow patterns

### What's Experimental
- Keyword-based prompt matching (not full NLP)
- Knowledge base (contains sample patterns, not community data)

### What Requires Configuration
- Real n8n validation (requires n8n instance)
- Web research (requires API keys)
```

**Acceptance Criteria:**
- [ ] Capabilities honestly documented
- [ ] "85% accuracy" claim removed or qualified
- [ ] Clear setup requirements

---

## PHASE 3: Future Enhancements

**Goal:** Add new capabilities on solid foundation

**Priority:** LOW - Only after Phase 1 & 2 complete

### Task 3.1: LLM Integration for Semantic Understanding

Replace keyword matching with LLM-based intent classification.

### Task 3.2: Expand Node Support

Add 45+ more node types to version mapping and templates.

### Task 3.3: Web Interface

Build simple web UI for workflow generation.

---

## Progress Tracking

| Phase | Tasks | Completed | Status |
|-------|-------|-----------|--------|
| Phase 1 | 9 | 9 | **COMPLETE** (2025-11-25) |
| Phase 2 | 9 | 9 | **COMPLETE** (2025-11-25) |
| Phase 3 | 3 | 0 | Ready to Start |

### Phase 1 Completion Notes

All 9 tasks completed:
- Task 1.1-1.3: Already implemented (schema fields, build method)
- Task 1.4: Fixed 3 IF nodes to v2 format
- Task 1.5: Added type_version=4 to 8 HTTP Request nodes
- Task 1.6: emailSend nodes already had v2 format
- Task 1.7: n8n already pinned to 1.60.1
- Task 1.8: Integration tests already comprehensive
- Task 1.9: Added auto-detection of typeVersion in WorkflowBuilder

### Phase 2 Completion Notes

All 9 tasks completed:
- Task 2.1: Removed all fake source URLs, replaced with `automata_builtin`
- Task 2.2: Created builtin/ and learned/ directories, updated dataclasses
- Task 2.3: Added ALLOW_SIMULATED_DATA config, SimulationModeError exception
- Task 2.4: Created KnowledgeAgent consolidating ResearcherAgent + WebResearcherAgent
- Task 2.5: Created BuilderAgent consolidating EngineerAgent + DocumenterAgent
- Task 2.6: Removed TesterAgent and ProjectManagerAgent (mock-only)
- Task 2.7: Integrated N8nApiClient into ValidatorAgent for real validation
- Task 2.8: Renamed NLPromptParser to KeywordPatternMatcher with honest docs
- Task 2.9: Updated README with honest capability documentation

Architecture simplified from 7 agents to 3:
- KnowledgeAgent (research + knowledge base)
- BuilderAgent (code + documentation)
- ValidatorAgent (schema + n8n validation)

---

## Definition of Done

A phase is complete when:
1. All tasks in the phase are done
2. All existing tests pass
3. New tests added for new functionality
4. Documentation updated
5. Changes committed and pushed

---

*Plan created 2025-11-25*
