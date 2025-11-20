# n8n Workflow Schema Specification

**Version:** 2.0 (n8n 1.60+)
**Last Updated:** 2025-11-20
**Project:** Automata-n8n

This document provides a complete specification for the n8n workflow JSON schema used by Automata-n8n, aligned with n8n version 1.60 and later.

---

## Table of Contents

1. [Overview](#overview)
2. [Complete Workflow Schema](#complete-workflow-schema)
3. [Top-Level Fields](#top-level-fields)
4. [Workflow Settings](#workflow-settings)
5. [Node Structure](#node-structure)
6. [Node Type Versions](#node-type-versions)
7. [Node Parameter Structures](#node-parameter-structures)
8. [Connections](#connections)
9. [Validation Rules](#validation-rules)
10. [Migration Guide](#migration-guide)

---

## Overview

The n8n workflow schema has evolved significantly through versions. This specification documents the complete schema required for n8n 1.60+ compatibility, including:

- Required workflow-level identifiers (id, versionId)
- Metadata fields (meta, pinData, staticData)
- Complete settings configuration
- Modern node parameter structures
- Proper node typeVersion mappings

---

## Complete Workflow Schema

### Minimal Valid Workflow

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "name": "My Workflow",
  "nodes": [
    {
      "name": "Start",
      "type": "n8n-nodes-base.manualTrigger",
      "typeVersion": 1,
      "position": [240, 300],
      "parameters": {}
    }
  ],
  "connections": {},
  "settings": {
    "executionOrder": "v1",
    "saveExecutionProgress": false,
    "saveManualExecutions": true,
    "timezone": "UTC",
    "callerPolicy": "workflowsFromSameOwner"
  },
  "versionId": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "meta": {
    "templateCredsSetupCompleted": true,
    "instanceId": "c3d4e5f6-a7b8-9012-cdef-123456789012"
  },
  "pinData": {},
  "staticData": {},
  "createdAt": "2025-11-20T12:00:00.000Z",
  "updatedAt": "2025-11-20T12:00:00.000Z",
  "tags": []
}
```

---

## Top-Level Fields

### Required Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string (UUID) | Yes | Unique workflow identifier |
| `name` | string | Yes | Human-readable workflow name |
| `nodes` | array | Yes | Array of workflow nodes |
| `connections` | object | Yes | Node connection mappings |
| `settings` | object | Yes | Workflow execution settings |
| `versionId` | string (UUID) | Yes | Workflow version identifier |

### Optional Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `meta` | object | Recommended | Workflow metadata |
| `pinData` | object | Optional | Pinned test data for nodes |
| `staticData` | object | Optional | Persistent workflow storage |
| `active` | boolean | Optional | Workflow activation status (default: false) |
| `createdAt` | string (ISO 8601) | Optional | Creation timestamp |
| `updatedAt` | string (ISO 8601) | Optional | Last update timestamp |
| `tags` | array of strings | Optional | Workflow tags for organization |

### Field Details

#### `id`
- **Format:** UUID v4
- **Example:** `"a1b2c3d4-e5f6-7890-abcd-ef1234567890"`
- **Purpose:** Uniquely identifies the workflow across n8n instances
- **Notes:** Must be globally unique; used for workflow references

#### `versionId`
- **Format:** UUID v4
- **Example:** `"b2c3d4e5-f6a7-8901-bcde-f12345678901"`
- **Purpose:** Tracks workflow versions for change management
- **Notes:** Should change when workflow is modified

#### `meta`
- **Structure:**
  ```json
  {
    "templateCredsSetupCompleted": true,
    "instanceId": "c3d4e5f6-a7b8-9012-cdef-123456789012"
  }
  ```
- **Fields:**
  - `templateCredsSetupCompleted` (boolean): Whether credentials are configured
  - `instanceId` (string UUID): n8n instance identifier

#### `pinData`
- **Purpose:** Stores pinned execution data for testing
- **Structure:** Object mapping node names to their pinned data
- **Example:**
  ```json
  {
    "HTTP Request": [
      {
        "json": {
          "data": "test value"
        }
      }
    ]
  }
  ```

#### `staticData`
- **Purpose:** Persistent storage accessible across workflow executions
- **Structure:** Arbitrary JSON object
- **Use Cases:** Counters, state tracking, rate limiting

---

## Workflow Settings

### Complete Settings Schema

```json
{
  "executionOrder": "v1",
  "saveExecutionProgress": false,
  "saveManualExecutions": true,
  "timezone": "UTC",
  "callerPolicy": "workflowsFromSameOwner",
  "executionTimeout": 3600,
  "maxExecutionTime": 7200
}
```

### Settings Field Reference

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `executionOrder` | string | Yes | "v1" | Execution order algorithm version |
| `saveExecutionProgress` | boolean | Recommended | false | Save intermediate execution data |
| `saveManualExecutions` | boolean | Recommended | true | Save manual test executions |
| `timezone` | string | Recommended | "UTC" | Workflow timezone (IANA format) |
| `callerPolicy` | string | Recommended | "workflowsFromSameOwner" | Caller permission policy |
| `executionTimeout` | number | Optional | - | Timeout in seconds (per node) |
| `maxExecutionTime` | number | Optional | - | Maximum total execution time (seconds) |

### Caller Policy Values

- `workflowsFromSameOwner`: Only workflows from same owner can call this workflow
- `workflowsFromAList`: Only workflows in specified list can call
- `any`: Any workflow can call this workflow
- `none`: No workflows can call this workflow

---

## Node Structure

### Basic Node Schema

```json
{
  "name": "Node Name",
  "type": "n8n-nodes-base.nodeName",
  "typeVersion": 2,
  "position": [240, 300],
  "parameters": {
    // Node-specific parameters
  },
  "credentials": {
    "credentialType": {
      "id": "credential-id",
      "name": "My Credential"
    }
  },
  "disabled": false,
  "notes": "Optional node description"
}
```

### Node Field Reference

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Unique node name within workflow |
| `type` | string | Yes | Node type identifier |
| `typeVersion` | number | Yes | Node type version |
| `position` | array [x, y] | Yes | Canvas position coordinates |
| `parameters` | object | Yes | Node configuration parameters |
| `credentials` | object | Optional | Credential references |
| `disabled` | boolean | Optional | Whether node is disabled |
| `notes` | string | Optional | Node documentation |

---

## Node Type Versions

### Current Type Versions (n8n 1.60+)

| Node Type | Type Version | Notes |
|-----------|--------------|-------|
| `n8n-nodes-base.emailSend` | 2.1 | Send Email node |
| `n8n-nodes-base.if` | 2.2 | IF conditional node |
| `n8n-nodes-base.postgres` | 2.6 | PostgreSQL database node |
| `n8n-nodes-base.httpRequest` | 4.x | HTTP Request node |
| `n8n-nodes-base.webhook` | 2.x | Webhook trigger |
| `n8n-nodes-base.slack` | 2.x | Slack integration |
| `n8n-nodes-base.manualTrigger` | 1 | Manual trigger |
| `n8n-nodes-base.function` | 1 | Function node |

**Important:** Always use the latest typeVersion for each node type to ensure compatibility.

---

## Node Parameter Structures

### Email Send Node (typeVersion 2.1)

```json
{
  "type": "n8n-nodes-base.emailSend",
  "typeVersion": 2.1,
  "parameters": {
    "fromEmail": "sender@example.com",
    "toEmail": "recipient@example.com",
    "subject": "Email Subject",
    "emailFormat": "text",
    "message": "Email message body",
    "options": {
      "ccEmail": "",
      "bccEmail": "",
      "replyTo": "",
      "allowUnauthorizedCerts": false,
      "appendAttribution": true
    }
  }
}
```

**Key Changes from v1:**
- `text` → `message` (parameter renamed)
- `emailFormat` field added (values: "text", "html", "both")
- `options` object for additional settings

### IF Node (typeVersion 2.2)

```json
{
  "type": "n8n-nodes-base.if",
  "typeVersion": 2.2,
  "parameters": {
    "conditions": {
      "options": {
        "caseSensitive": true,
        "leftValue": "",
        "typeValidation": "strict"
      },
      "conditions": [
        {
          "id": "condition-1",
          "leftValue": "={{ $json.value }}",
          "rightValue": 100,
          "operator": {
            "type": "number",
            "operation": "gte"
          }
        }
      ],
      "combinator": "and"
    }
  }
}
```

**Key Changes from v1:**
- Complete restructure from `boolean`/`number`/`string` arrays
- New `conditions` array with explicit `operator` objects
- `combinator` field for AND/OR logic
- Each condition requires unique `id`

**Operator Types:**
- `number`: operations = `equals`, `notEquals`, `gt`, `gte`, `lt`, `lte`
- `string`: operations = `equals`, `notEquals`, `contains`, `notContains`, `startsWith`, `endsWith`, `regex`
- `boolean`: operations = `true`, `false`
- `dateTime`: operations = `after`, `before`, `between`

### PostgreSQL Node (typeVersion 2.6)

```json
{
  "type": "n8n-nodes-base.postgres",
  "typeVersion": 2.6,
  "parameters": {
    "operation": "insert",
    "schema": "public",
    "table": "events",
    "columns": "id,timestamp,data",
    "options": {
      "queryBatching": "independently",
      "connectionTimeout": 30,
      "outputLargeFormatNumbers": "numbers",
      "replaceEmptyStrings": false
    }
  }
}
```

**Query Batching Options:**
- `single`: Single query for all items
- `independently`: One query per item
- `transaction`: All queries in a transaction

### HTTP Request Node (typeVersion 4.x)

```json
{
  "type": "n8n-nodes-base.httpRequest",
  "typeVersion": 4,
  "parameters": {
    "url": "https://api.example.com/endpoint",
    "method": "POST",
    "authentication": "genericCredentialType",
    "responseFormat": "json",
    "options": {
      "timeout": 10000,
      "retry": {
        "enabled": true,
        "maxRetries": 3,
        "waitBetween": 2000
      },
      "redirect": {
        "followRedirects": true
      }
    }
  }
}
```

### Webhook Node (typeVersion 2.x)

```json
{
  "type": "n8n-nodes-base.webhook",
  "typeVersion": 2,
  "parameters": {
    "path": "webhook-path",
    "httpMethod": "POST",
    "responseMode": "onReceived",
    "responseCode": 200,
    "responseData": "firstEntryJson",
    "options": {
      "responseHeaders": {}
    }
  }
}
```

**Response Modes:**
- `onReceived`: Respond immediately before processing
- `lastNode`: Respond with last node's output
- `responseNode`: Use specific response node

---

## Connections

### Connection Structure

```json
{
  "connections": {
    "Source Node": {
      "main": [
        [
          {
            "node": "Target Node",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

### Connection Types

- `main`: Standard execution flow
- `ai_languageModel`: AI model connection
- `ai_memory`: AI memory connection
- `ai_tool`: AI tool connection

### Multiple Outputs (IF Node Example)

```json
{
  "connections": {
    "IF Node": {
      "main": [
        [
          {
            "node": "True Branch Node",
            "type": "main",
            "index": 0
          }
        ],
        [
          {
            "node": "False Branch Node",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

---

## Validation Rules

### Workflow-Level Validation

1. **Required Fields**: Must include `id`, `name`, `nodes`, `connections`, `settings`, `versionId`
2. **UUID Format**: `id`, `versionId`, and `meta.instanceId` must be valid UUIDs
3. **Unique Node Names**: All node names must be unique within the workflow
4. **Valid Connections**: All connection references must point to existing nodes
5. **No Circular Dependencies**: Workflow must not contain circular execution paths

### Node-Level Validation

1. **Type Version Compatibility**: Use current typeVersion for each node type
2. **Required Parameters**: Each node type has specific required parameters
3. **Position Array**: Must be `[x, y]` with numeric coordinates
4. **Parameter Structure**: Must match node type's expected parameter schema

### Settings Validation

1. **Execution Order**: Must be "v1" (only supported version)
2. **Timezone**: Must be valid IANA timezone identifier
3. **Caller Policy**: Must be one of allowed values
4. **Numeric Limits**: Timeout values must be positive integers

---

## Migration Guide

### Migrating from Old Schema to New Schema

#### 1. Add Missing Top-Level Fields

**Before:**
```json
{
  "name": "My Workflow",
  "nodes": [...],
  "connections": {...},
  "settings": {
    "executionOrder": "v1"
  }
}
```

**After:**
```json
{
  "id": "generated-uuid-1",
  "name": "My Workflow",
  "nodes": [...],
  "connections": {...},
  "settings": {
    "executionOrder": "v1",
    "saveExecutionProgress": false,
    "saveManualExecutions": true,
    "timezone": "UTC",
    "callerPolicy": "workflowsFromSameOwner"
  },
  "versionId": "generated-uuid-2",
  "meta": {
    "templateCredsSetupCompleted": true,
    "instanceId": "generated-uuid-3"
  },
  "pinData": {},
  "staticData": {}
}
```

#### 2. Update Node TypeVersions

Check each node's current typeVersion and update to latest:

```python
# Python example using Automata-n8n
from skills.generate_workflow_json import WorkflowBuilder

builder = WorkflowBuilder("Updated Workflow")
builder.add_node(
    "n8n-nodes-base.emailSend",
    "Send Email",
    type_version=2,  # Updated from 1
    parameters={...}
)
```

#### 3. Update Node Parameters

**Email Send Node - Old (v1):**
```json
{
  "parameters": {
    "toEmail": "user@example.com",
    "subject": "Hello",
    "text": "Message body",
    "fromEmail": "sender@example.com"
  }
}
```

**Email Send Node - New (v2.1):**
```json
{
  "parameters": {
    "fromEmail": "sender@example.com",
    "toEmail": "user@example.com",
    "subject": "Hello",
    "emailFormat": "text",
    "message": "Message body",
    "options": {}
  }
}
```

**IF Node - Old (v1):**
```json
{
  "parameters": {
    "conditions": {
      "boolean": [],
      "number": [
        {
          "value1": "={{ $json.count }}",
          "operation": "equal",
          "value2": 10
        }
      ]
    }
  }
}
```

**IF Node - New (v2.2):**
```json
{
  "parameters": {
    "conditions": {
      "options": {
        "caseSensitive": true,
        "leftValue": "",
        "typeValidation": "strict"
      },
      "conditions": [
        {
          "id": "condition-1",
          "leftValue": "={{ $json.count }}",
          "rightValue": 10,
          "operator": {
            "type": "number",
            "operation": "equals"
          }
        }
      ],
      "combinator": "and"
    }
  }
}
```

---

## Best Practices

### 1. Always Use Latest TypeVersions
Keep nodes updated to their latest typeVersion to ensure compatibility and access to new features.

### 2. Include All Recommended Settings
Even if optional, include all recommended settings with sensible defaults.

### 3. Generate Unique IDs
Use UUID v4 for all ID fields (`id`, `versionId`, `instanceId`).

### 4. Validate Before Import
Use `parse_n8n_schema.py` to validate workflows before importing to n8n.

### 5. Document Complex Workflows
Use node `notes` field and workflow tags for documentation.

### 6. Test Parameter Structures
Verify node parameters match expected structure for each typeVersion.

---

## References

- [n8n Official Documentation](https://docs.n8n.io/)
- [n8n Workflow Structure](https://docs.n8n.io/workflows/)
- [n8n Expression Language](https://docs.n8n.io/code/expressions/)
- [n8n Node Reference](https://docs.n8n.io/integrations/)

---

## Changelog

### 2025-11-20 - Version 2.0
- Initial comprehensive specification
- Added n8n 1.60+ schema requirements
- Documented modern node parameter structures
- Added migration guide
- Included validation rules

---

**Document Status:** ✅ Complete
**Target n8n Version:** 1.60+
**Maintained By:** Automata-n8n Project
