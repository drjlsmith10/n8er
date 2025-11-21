# n8n Compatibility Matrix

**Last Updated:** 2025-11-20
**Project Version:** 2.0.0-alpha
**Target n8n Version:** 1.60.0+

---

## Overview

This document outlines the compatibility requirements between Project Automata-n8n and various n8n versions. All generated workflows are optimized for **n8n 1.60.0** and later versions.

## Supported n8n Versions

| n8n Version | Status | Notes |
|-------------|--------|-------|
| **1.60.0 - 1.70.x** | ✅ **Fully Supported** | Recommended version range |
| **1.50.0 - 1.59.x** | ⚠️ **Partial Support** | Most features work, some node typeVersions may differ |
| **1.30.0 - 1.49.x** | ⚠️ **Limited Support** | Significant differences in node typeVersions and workflow schema |
| **1.0.0 - 1.29.x** | ❌ **Not Supported** | Major schema differences, incompatible |
| **0.x** | ❌ **Not Supported** | Incompatible workflow structure |
| **Latest (> 1.70.x)** | ⚠️ **Unknown** | May work but not tested - verify node versions |

### Tested Versions

Project Automata-n8n has been tested and verified with:
- ✅ n8n 1.60.0 (September 2024)
- ✅ n8n 1.60.1 (September 2024)
- ✅ n8n 1.61.0 (October 2024)
- ✅ n8n 1.62.0 (October 2024)

---

## Node TypeVersion Compatibility

### Critical Node TypeVersions

The following node types require specific typeVersions for compatibility with n8n 1.60.0+:

| Node Type | typeVersion (1.60.0+) | typeVersion (Legacy) | Breaking Changes |
|-----------|----------------------|----------------------|------------------|
| **Webhook** | 2.0 | 1.0 | Response modes, authentication |
| **HTTP Request** | 4.2 | 1.0 | Enhanced auth, retry logic, error handling |
| **Slack** | 2.3 | 1.0 | Blocks API, interactive components |
| **PostgreSQL** | 2.6 | 1.0 | Query builder, connection pooling |
| **Code** | 2.0 | 1.0 (Function node) | Sandbox improvements, permissions |
| **Set** | 3.3 | 1.0 | Type handling, multi-value support |
| **IF** | 2.0 | 1.0 | Condition types, operators |
| **Switch** | 3.0 | 1.0 | Routing logic, fallback handling |
| **Merge** | 2.1 | 1.0 | Wait modes, data combining |
| **Gmail** | 2.1 | 1.0 | Threading, labels, attachments |
| **Google Sheets** | 4.5 | 1.0 | Advanced operations, batching |
| **Email Send** | 2.1 | 1.0 | Formatting options, templates |
| **Cron** | 1.2 | 1.0 | Advanced scheduling options |

### Complete Node Mapping

For a comprehensive mapping of all supported node types and their typeVersions, see:
- `skills/n8n_node_versions.py` - Complete programmatic mapping (100+ nodes)
- Includes: Triggers, HTTP, Databases, Communication, Cloud Services, AI/ML, and more

---

## Workflow Schema Compatibility

### Required Fields (n8n 1.60.0+)

Generated workflows include all required and recommended fields for modern n8n:

```json
{
  "id": "uuid",                    // ✅ Workflow unique identifier
  "name": "Workflow Name",         // ✅ Required
  "nodes": [...],                  // ✅ Required
  "connections": {...},            // ✅ Required
  "settings": {                    // ✅ Required
    "executionOrder": "v1",
    "saveExecutionProgress": false,
    "saveManualExecutions": true,
    "timezone": "UTC",
    "callerPolicy": "workflowsFromSameOwner"
  },
  "versionId": "uuid",             // ✅ Version tracking
  "meta": {...},                   // ✅ Workflow metadata
  "pinData": {},                   // ✅ Test data support
  "staticData": {},                // ✅ Persistent workflow data
  "createdAt": "ISO8601",          // ✅ Timestamps
  "updatedAt": "ISO8601",
  "tags": [...]                    // ✅ Organization
}
```

### Legacy Schema Differences

Older n8n versions (< 1.50.0) may not support:
- `versionId` field
- `meta` object
- `pinData` for testing
- `staticData` persistence
- Advanced `settings` options (timezone, callerPolicy, etc.)

---

## Breaking Changes by Version

### n8n 1.60.0 (September 2024)

**Major Changes:**
- HTTP Request node updated to v4.2 with enhanced authentication
- Webhook node v2 with improved response handling
- Set node v3.3 with better type coercion

**Impact on Project Automata:**
- ✅ All templates updated to use correct typeVersions
- ✅ Automatic version detection in WorkflowBuilder
- ✅ Validation ensures compatibility

### n8n 1.50.0 (June 2024)

**Major Changes:**
- Expression syntax updates
- New workflow settings fields
- Improved error handling

**Impact:**
- ⚠️ Expression syntax may differ in some templates
- ⚠️ Some settings fields may be ignored by older versions

### n8n 1.30.0 (March 2024)

**Major Changes:**
- Workflow structure changes
- Node parameter updates
- Connection format updates

**Impact:**
- ⚠️ Minimal backwards compatibility
- ❌ Generated workflows may fail import

---

## Version Detection & Validation

### Automatic TypeVersion Detection

Project Automata automatically detects and uses the correct typeVersion for each node:

```python
from skills.n8n_node_versions import get_node_version, validate_node_version

# Get recommended version for a node type
version = get_node_version('n8n-nodes-base.webhook')  # Returns 2.0

# Validate a specific version
is_valid, message = validate_node_version('n8n-nodes-base.webhook', 1.0)
# Returns: (True, "Version 1.0 is supported but 2.0 is recommended")
```

### Version Validation in WorkflowBuilder

The `WorkflowBuilder` class automatically:
1. Detects correct typeVersion if not specified
2. Validates provided typeVersions against supported range
3. Logs warnings for outdated versions
4. Ensures compatibility with target n8n version

---

## Migration Guide

### Upgrading from typeVersion 1 to Latest

If you have existing workflows with `typeVersion: 1`, here's how to upgrade:

#### 1. Identify Nodes to Update

Use the node version checker:

```bash
python -c "from skills.n8n_node_versions import get_node_version_info; \
print(get_node_version_info('n8n-nodes-base.webhook'))"
```

#### 2. Update Workflow JSON

**Before (Legacy):**
```json
{
  "name": "My Workflow",
  "nodes": [
    {
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 1,  // ❌ Outdated
      "parameters": {...}
    }
  ]
}
```

**After (Modern):**
```json
{
  "id": "uuid",
  "name": "My Workflow",
  "nodes": [
    {
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 2,  // ✅ Current
      "parameters": {...}
    }
  ],
  "versionId": "uuid",
  "meta": {...},
  // ... other fields
}
```

#### 3. Test in n8n

1. Import updated workflow to n8n
2. Check for import warnings
3. Test execution
4. Verify all node parameters are recognized

---

## Deployment Recommendations

### Docker Deployment

**Recommended:** Pin to specific n8n version

```yaml
# docker-compose.yml
services:
  n8n:
    image: n8nio/n8n:1.60.1  # ✅ Pinned version
    # NOT: n8nio/n8n:latest  # ❌ Unpredictable
```

### Self-Hosted Deployment

**Check n8n version before deploying:**

```bash
# Check installed n8n version
n8n --version

# Verify compatibility
python -c "from skills.n8n_node_versions import N8N_VERSION_COMPATIBILITY; \
print(f\"Target version: {N8N_VERSION_COMPATIBILITY['target_version']}\")"
```

### Cloud Deployment (n8n Cloud)

**n8n Cloud Compatibility:**
- ✅ n8n Cloud typically runs latest stable version
- ⚠️ Version updates automatic - may introduce breaking changes
- ✅ Recommended to test workflows before production deployment

---

## Troubleshooting

### Common Issues

#### Issue: "Unrecognized node type"

**Cause:** typeVersion mismatch
**Solution:** Check node typeVersion against target n8n version

```python
from skills.n8n_node_versions import validate_node_version
is_valid, msg = validate_node_version('n8n-nodes-base.webhook', 1.0)
print(msg)  # Shows if version is outdated
```

#### Issue: "Missing node parameters"

**Cause:** Node parameters changed between typeVersions
**Solution:**
1. Check n8n documentation for current node parameters
2. Update workflow JSON to match
3. Test in n8n UI before automation

#### Issue: "Workflow import failed"

**Cause:** Missing required workflow fields
**Solution:** Ensure workflow includes all modern schema fields (id, versionId, meta, etc.)

---

## API Compatibility

### n8n REST API

Project Automata is compatible with n8n REST API v1.x:

**Supported Operations:**
- ✅ GET /workflows - List workflows
- ✅ POST /workflows - Create workflow
- ✅ PUT /workflows/:id - Update workflow
- ✅ DELETE /workflows/:id - Delete workflow
- ✅ POST /workflows/:id/activate - Activate workflow
- ✅ POST /workflows/:id/deactivate - Deactivate workflow
- ✅ GET /executions - List executions
- ✅ POST /workflows/run - Manual execution

**API Version Detection:**
```bash
curl http://localhost:5678/rest/version
```

---

## Future Compatibility

### Planned Support

- **n8n 1.70.x+:** Testing in progress
- **n8n 2.0.x:** Will be evaluated when released

### Monitoring n8n Updates

**Resources:**
- Official Release Notes: https://docs.n8n.io/release-notes/
- GitHub Releases: https://github.com/n8n-io/n8n/releases
- Community Forum: https://community.n8n.io

**Best Practices:**
1. Subscribe to n8n release notifications
2. Test new versions in staging before production
3. Review breaking changes in release notes
4. Update Project Automata node mappings as needed

---

## Version History

| Date | n8n Version | Automata Version | Changes |
|------|-------------|------------------|---------|
| 2025-11-20 | 1.60.0+ | 2.0.0-alpha | Initial compatibility matrix |
| 2025-11-08 | 1.50.0+ | 1.0.0 | Original release (outdated typeVersions) |

---

## Support

For compatibility issues or questions:
- **GitHub Issues:** https://github.com/drjlsmith10/n8er/issues
- **Documentation:** `/docs` directory
- **n8n Community:** https://community.n8n.io

---

## Summary

✅ **Target n8n Version:** 1.60.0+
✅ **100+ Nodes Mapped:** Complete typeVersion coverage
✅ **Automatic Detection:** No manual version management needed
✅ **Validation Built-in:** Ensures compatibility at workflow generation time
✅ **Future-Proof:** Easy to update as n8n evolves

**Recommendation:** Always pin to specific n8n version (1.60.1 recommended) and test workflows before production deployment.
