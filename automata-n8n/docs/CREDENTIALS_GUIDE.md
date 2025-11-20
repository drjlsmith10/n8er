# Credentials Management Guide

**Author:** Project Automata - Agent 5 (High Priority Features)
**Version:** 2.1.0
**Date:** 2025-11-20
**Issue:** #9 - Credential Management

---

## Overview

This guide covers credential management in Project Automata, including how to define, track, and use credentials in generated n8n workflows.

**Why Credential Management Matters:**
- Workflows often need to connect to external services (APIs, databases, cloud services)
- Credentials contain sensitive information (passwords, API keys, tokens)
- n8n cannot export actual credential values for security reasons
- Proper credential tracking ensures workflows can be deployed correctly

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Core Concepts](#core-concepts)
3. [Using the Credential Manager](#using-the-credential-manager)
4. [Credential Templates](#credential-templates)
5. [Workflow Integration](#workflow-integration)
6. [Best Practices](#best-practices)
7. [Common Credential Types](#common-credential-types)
8. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Basic Example

```python
from skills.credential_manager import CredentialManager, CredentialLibrary
from skills.generate_workflow_json import WorkflowBuilder

# 1. Create credential manager
cred_manager = CredentialManager()

# 2. Add credentials
postgres_cred = cred_manager.add_credential(
    name="Production Database",
    credential_type="postgresApi",
    description="Main application database",
    environment="production"
)

slack_cred = cred_manager.add_credential(
    name="Slack Notifications",
    credential_type="slackApi",
    description="Team notification channel"
)

# 3. Build workflow with credentials
builder = WorkflowBuilder("Data Pipeline")

builder.add_node(
    "n8n-nodes-base.postgres",
    "Query Database",
    parameters={"operation": "select", "table": "users"},
    credentials={
        "postgres": postgres_cred.to_node_reference()
    }
)

builder.add_node(
    "n8n-nodes-base.slack",
    "Send Notification",
    parameters={"channel": "#alerts", "text": "Query completed"},
    credentials={
        "slackApi": slack_cred.to_node_reference()
    }
)

workflow = builder.build()

# 4. Export credentials manifest
manifest = cred_manager.export_credentials_manifest()
cred_manager.save_manifest("credentials_required.json")
```

---

## Core Concepts

### Credential Template

A `CredentialTemplate` represents a credential placeholder that references actual credentials stored in n8n.

**Key Properties:**
- `name`: Human-readable identifier
- `type`: n8n credential type (e.g., `postgresApi`, `slackApi`)
- `description`: What this credential is used for
- `credential_id`: Optional UUID if referencing existing n8n credential
- `fields`: Field definitions and requirements
- `environment`: Target environment (dev, staging, production)

### Credential Manager

The `CredentialManager` class tracks credentials used across a workflow:
- Maintains credential registry
- Tracks node-to-credential mappings
- Validates credential configurations
- Exports credential manifests for deployment

### Credential Reference

When adding a node with credentials, use `to_node_reference()` to generate the proper format:

```python
credential.to_node_reference()
# Returns: {"name": "Production Database"}
# Or: {"id": "uuid-here", "name": "Production Database"}
```

---

## Using the Credential Manager

### Creating Credentials

#### Method 1: Direct Creation

```python
manager = CredentialManager()

credential = manager.add_credential(
    name="API Key",
    credential_type="httpHeaderAuth",
    description="External API authentication",
    fields={
        "name": {"type": "string", "value": "Authorization"},
        "value": {"type": "string", "required": True, "sensitive": True}
    }
)
```

#### Method 2: Using Credential Library

```python
# Pre-defined templates for common services
postgres_cred = CredentialLibrary.postgres(
    name="App Database",
    host="db.example.com",
    database="myapp"
)

aws_cred = CredentialLibrary.aws(
    name="AWS Production",
    region="us-east-1"
)

slack_cred = CredentialLibrary.slack(name="Team Slack")
```

#### Method 3: Convenience Function

```python
from skills.credential_manager import get_common_credential

# Quick credential creation
db_cred = get_common_credential(
    'postgres',
    name="Development DB",
    host="localhost",
    database="dev_db"
)
```

### Tracking Credential Usage

The credential manager automatically tracks which nodes use which credentials:

```python
# Add nodes with credentials
builder.add_node(
    "n8n-nodes-base.postgres",
    "Database Query",
    credentials={"postgres": db_cred.to_node_reference()}
)

# Later, retrieve tracking information
manifest = manager.get_credentials_manifest()
print(manifest)
# {
#     "credentials_used": {"Database Query": "App Database"},
#     "total_nodes_with_credentials": 1,
#     "unique_credentials": ["App Database"]
# }
```

### Validating Credentials

```python
# Validate all credentials
validation_results = manager.validate_all()

if validation_results:
    print("Validation errors found:")
    for cred_name, errors in validation_results.items():
        print(f"  {cred_name}: {errors}")
else:
    print("All credentials valid!")
```

### Exporting Credentials Manifest

For deployment and documentation:

```python
# Export complete manifest
manifest = manager.export_credentials_manifest()

# Save to file
manager.save_manifest("deployment/credentials_required.json")

# Manifest contents:
# {
#     "credentials": [...],  # All credential definitions
#     "node_credential_map": {...},  # Node usage mapping
#     "total_credentials": 3,
#     "environments": ["production", "staging"],
#     "exported_at": "2025-11-20T..."
# }
```

---

## Credential Templates

### Structure

```python
@dataclass
class CredentialTemplate:
    name: str  # "Production Database"
    type: str  # "postgresApi"
    description: str = ""
    credential_id: Optional[str] = None  # UUID if exists
    fields: Dict[str, Any] = field(default_factory=dict)
    environment: str = "production"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    metadata: Dict[str, Any] = field(default_factory=dict)
```

### Field Definitions

Fields describe the structure and requirements of a credential:

```python
fields = {
    "host": {
        "type": "string",
        "value": "db.example.com",
        "required": True
    },
    "password": {
        "type": "string",
        "required": True,
        "sensitive": True  # Mark as sensitive data
    },
    "port": {
        "type": "number",
        "value": 5432
    }
}
```

---

## Workflow Integration

### Adding Credentials to Nodes

```python
builder = WorkflowBuilder("Authenticated Workflow")

# Database node with credentials
builder.add_node(
    "n8n-nodes-base.postgres",
    "Query Users",
    parameters={
        "operation": "select",
        "table": "users"
    },
    credentials={
        "postgres": {
            "name": "Production Database"
        }
    }
)

# HTTP Request with authentication
builder.add_node(
    "n8n-nodes-base.httpRequest",
    "API Call",
    parameters={
        "url": "https://api.example.com/data",
        "method": "GET"
    },
    credentials={
        "httpHeaderAuth": {
            "name": "API Key"
        }
    }
)
```

### Workflow with Multiple Credentials

```python
# Create manager
manager = CredentialManager()

# Add credentials
db_cred = manager.add_credential("Database", "postgresApi")
api_cred = manager.add_credential("API", "httpHeaderAuth")
slack_cred = manager.add_credential("Slack", "slackApi")

# Build workflow
builder = WorkflowBuilder("Multi-Service Workflow")

# Each node uses appropriate credentials
builder.add_node(
    "n8n-nodes-base.postgres", "Fetch Data",
    credentials={"postgres": db_cred.to_node_reference()}
)

builder.add_node(
    "n8n-nodes-base.httpRequest", "Process",
    credentials={"httpHeaderAuth": api_cred.to_node_reference()}
)

builder.add_node(
    "n8n-nodes-base.slack", "Notify",
    credentials={"slackApi": slack_cred.to_node_reference()}
)

# Track credentials used
manager.track_node_credential("Fetch Data", "Database")
manager.track_node_credential("Process", "API")
manager.track_node_credential("Notify", "Slack")
```

### Environment-Specific Credentials

```python
# Development credentials
dev_db = manager.add_credential(
    "Dev Database",
    "postgresApi",
    environment="development"
)

# Production credentials
prod_db = manager.add_credential(
    "Prod Database",
    "postgresApi",
    environment="production"
)

# List by environment
dev_creds = manager.list_credentials(environment="development")
prod_creds = manager.list_credentials(environment="production")
```

---

## Best Practices

### 1. Use Descriptive Names

```python
# Good
"Production Database"
"Slack Team Notifications"
"AWS S3 Bucket Access"

# Bad
"DB1"
"cred"
"test"
```

### 2. Always Add Descriptions

```python
manager.add_credential(
    name="Customer Database",
    credential_type="postgresApi",
    description="Read-only access to customer data for reporting"  # Good!
)
```

### 3. Separate by Environment

```python
# Don't mix environments
dev_api = manager.add_credential(
    "Development API", "httpHeaderAuth", environment="development"
)

prod_api = manager.add_credential(
    "Production API", "httpHeaderAuth", environment="production"
)
```

### 4. Document Required Credentials

Always export and version control your credentials manifest:

```python
# After building workflow
manager.save_manifest("docs/credentials_required.json")
```

### 5. Validate Before Deployment

```python
# Before exporting workflow
validation_errors = manager.validate_all()
if validation_errors:
    raise ValueError(f"Invalid credentials: {validation_errors}")
```

### 6. Use Credential Library for Common Services

```python
# Don't manually create common credentials
postgres_cred = CredentialLibrary.postgres("My DB", "host", "database")
slack_cred = CredentialLibrary.slack("Team Slack")
aws_cred = CredentialLibrary.aws("AWS Account", "us-east-1")
```

---

## Common Credential Types

### HTTP Authentication

#### Basic Auth
```python
CredentialLibrary.http_basic_auth("API Basic Auth")
# Fields: username, password
```

#### Header Auth
```python
CredentialLibrary.http_header_auth(
    "API Key",
    header_name="X-API-Key"
)
# Fields: name, value
```

#### OAuth2
```python
CredentialLibrary.oauth2(
    "Google OAuth",
    authorization_url="https://accounts.google.com/o/oauth2/auth",
    access_token_url="https://oauth2.googleapis.com/token"
)
# Fields: clientId, clientSecret, authorizationUrl, accessTokenUrl
```

### Database Credentials

#### PostgreSQL
```python
CredentialLibrary.postgres(
    "PostgreSQL DB",
    host="db.example.com",
    database="myapp"
)
# Fields: host, port, database, user, password, ssl
```

#### MySQL
```python
CredentialLibrary.mysql(
    "MySQL DB",
    host="db.example.com",
    database="myapp"
)
# Fields: host, port, database, user, password, ssl
```

#### MongoDB
```python
CredentialLibrary.mongodb(
    "MongoDB",
    connection_string="mongodb://user:pass@host:27017/db"
)
# Fields: connectionString
```

### Cloud Services

#### AWS
```python
CredentialLibrary.aws(
    "AWS Production",
    region="us-east-1"
)
# Fields: accessKeyId, secretAccessKey, region
```

### Communication Services

#### Slack
```python
CredentialLibrary.slack("Slack Workspace")
# Fields: accessToken
```

#### Email (SMTP)
```python
CredentialLibrary.email_smtp(
    "SMTP Server",
    host="smtp.example.com",
    port=587
)
# Fields: host, port, secure, user, password
```

#### GitHub
```python
CredentialLibrary.github("GitHub API")
# Fields: accessToken
```

---

## Troubleshooting

### Error: "Credential type may not be valid"

**Problem:** Unrecognized credential type

**Solution:**
```python
# Check valid types
valid_types = [
    'httpBasicAuth', 'httpHeaderAuth', 'oAuth2Api',
    'postgresApi', 'mysqlApi', 'mongoDb',
    'slackApi', 'aws', 'githubApi'
]

# Or use Credential Library for common types
credential = CredentialLibrary.postgres(...)  # Always valid
```

### Error: "Credentials not found" in n8n

**Problem:** Workflow imported but credentials missing

**Solution:**
1. Export credentials manifest: `manager.save_manifest("creds.json")`
2. Review required credentials
3. Create credentials in target n8n instance
4. Use exact same names as in manifest

### Credential Reference Not Working

**Problem:** Node doesn't connect to service

**Solution:**
```python
# Ensure correct credential type for node
builder.add_node(
    "n8n-nodes-base.postgres",  # PostgreSQL node
    "Query",
    credentials={
        "postgres": cred.to_node_reference()  # Must match node's expected type
    }
)
```

### Missing Credentials in Exported Workflow

**Problem:** Workflow exports without credential references

**Solution:**
```python
# Use to_node_reference() method
credentials={
    "postgres": db_cred.to_node_reference()  # Correct
}

# Don't do this:
credentials={"postgres": "Database"}  # Wrong
```

---

## Advanced Topics

### Custom Credential Types

```python
custom_cred = CredentialTemplate(
    name="Custom Service",
    type="customApi",
    description="Custom authentication",
    fields={
        "apiKey": {"type": "string", "required": True, "sensitive": True},
        "apiSecret": {"type": "string", "required": True, "sensitive": True},
        "endpoint": {"type": "string", "value": "https://api.custom.com"}
    }
)
```

### Credential Inheritance

```python
class CustomCredentialManager(CredentialManager):
    def add_custom_credential(self, name: str, api_key: str):
        return self.add_credential(
            name=name,
            credential_type="httpHeaderAuth",
            fields={
                "name": {"value": "X-API-Key"},
                "value": {"value": api_key, "sensitive": True}
            }
        )
```

### Programmatic Credential Discovery

```python
# Find all PostgreSQL credentials
pg_creds = [
    cred for cred in manager.list_credentials()
    if cred.type == "postgresApi"
]

# Find credentials by environment
prod_creds = manager.list_credentials(environment="production")
```

---

## Related Documentation

- [n8n Credentials Documentation](https://docs.n8n.io/credentials/)
- [ERROR_HANDLING_PATTERNS.md](./ERROR_HANDLING_PATTERNS.md) - Error handling with credentials
- [DEPLOYMENT.md](./DEPLOYMENT.md) - Deploying workflows with credentials

---

## Examples Repository

See `examples/credentials/` for complete working examples:
- `basic_credentials.py` - Simple credential usage
- `multi_service_workflow.py` - Workflow with multiple credentials
- `environment_specific.py` - Dev/staging/prod credentials
- `custom_credentials.py` - Custom credential types

---

**Questions or Issues?**
- GitHub Issues: https://github.com/drjlsmith10/n8er/issues
- Documentation: `/docs`
- Examples: `/examples/credentials`
