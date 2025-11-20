# n8n API Integration

**Version:** 1.0.0
**Last Updated:** 2025-11-20
**Status:** Production Ready

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [API Client Usage](#api-client-usage)
6. [Integration Testing](#integration-testing)
7. [CI/CD Integration](#cicd-integration)
8. [Troubleshooting](#troubleshooting)
9. [API Reference](#api-reference)
10. [Best Practices](#best-practices)

---

## Overview

Project Automata now includes full integration with n8n's REST API, enabling:

- **Workflow Import/Export**: Programmatically import and export workflows
- **Version Detection**: Automatically detect n8n instance version
- **Validation**: Validate workflows before import
- **Health Monitoring**: Monitor n8n instance health
- **Rate Limiting**: Built-in rate limiting to prevent API abuse
- **Error Handling**: Comprehensive error handling with retry logic

### Features

- ✅ Full CRUD operations on workflows
- ✅ n8n version detection
- ✅ Connection testing and health checks
- ✅ Workflow validation
- ✅ Rate limiting and retry logic
- ✅ Integration tests
- ✅ CI/CD support

### Architecture

```
┌─────────────────────┐
│ Project Automata    │
│  - Generate         │
│  - Validate         │
│  - Transform        │
└──────────┬──────────┘
           │
           │ n8n_api_client.py
           │
           ▼
┌─────────────────────┐
│   n8n REST API      │
│  - /api/v1/         │
│  - Workflows        │
│  - Authentication   │
└─────────────────────┘
```

---

## Quick Start

### 1. Get n8n API Key

In your n8n instance:

1. Go to **Settings** → **n8n API**
2. Click **Create API Key**
3. Copy the generated key

### 2. Configure Environment

Create or update `.env` file:

```bash
# n8n API Configuration
N8N_API_URL=http://localhost:5678
N8N_API_KEY=your-api-key-here
```

### 3. Test Connection

```bash
python scripts/test_n8n_connection.py
```

### 4. Use in Code

```python
from skills.n8n_api_client import create_client_from_env

# Create client
client = create_client_from_env()

# Test connection
ok, msg = client.test_connection()
print(f"Connection: {msg}")

# List workflows
workflows = client.list_workflows(limit=5)
print(f"Found {len(workflows)} workflows")
```

---

## Installation

### Prerequisites

- Python 3.9+
- n8n instance (self-hosted or cloud)
- n8n API access enabled

### Install Dependencies

```bash
# Install Project Automata with dev dependencies
pip install -e ".[dev]"

# Or install just the required packages
pip install requests python-dotenv
```

### Verify Installation

```bash
python -c "from skills.n8n_api_client import N8nApiClient; print('✓ Installation successful')"
```

---

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `N8N_API_URL` | Yes | `http://localhost:5678` | Base URL of n8n instance |
| `N8N_API_KEY` | Yes | None | API key from n8n Settings |
| `RATE_LIMIT_ENABLED` | No | `true` | Enable rate limiting |
| `RATE_LIMIT_REQUESTS_PER_MINUTE` | No | `60` | Max requests per minute |

### n8n Configuration

#### Self-Hosted n8n

No additional configuration needed. API is enabled by default.

#### n8n Cloud

Requires a **paid plan**. Free tier does not have API access.

### Validation

Run configuration validation:

```bash
python -c "from config import config; msgs = config.validate(); print('\n'.join(msgs))"
```

Or test n8n connection specifically:

```bash
python -c "from config import config; ok, msg = config.validate_n8n_connection(); print(msg)"
```

---

## API Client Usage

### Creating a Client

#### From Environment Variables

```python
from skills.n8n_api_client import create_client_from_env

client = create_client_from_env()
```

#### Manual Configuration

```python
from skills.n8n_api_client import N8nApiClient

client = N8nApiClient(
    api_url="http://localhost:5678",
    api_key="your-api-key",
    timeout=30,
    max_retries=3,
    rate_limit_requests=60,
    rate_limit_period=60
)
```

### Connection Testing

```python
# Simple test
ok, msg = client.test_connection()
if ok:
    print("Connected successfully!")
else:
    print(f"Connection failed: {msg}")

# Comprehensive health check
health = client.health_check()
print(f"Overall: {health['overall_status']}")
for check_name, result in health['checks'].items():
    print(f"  {check_name}: {result['status']}")
```

### Version Detection

```python
version_info = client.get_n8n_version()
print(f"n8n version: {version_info['version']}")
print(f"Detection method: {version_info['method']}")
```

### Workflow Operations

#### List Workflows

```python
# Get all workflows (default limit)
workflows = client.list_workflows()

# Get first 10 workflows
workflows = client.list_workflows(limit=10)

# Get only active workflows
active = client.list_workflows(active=True)

# Filter by tags
tagged = client.list_workflows(tags=["production", "critical"])
```

#### Get Workflow

```python
workflow = client.get_workflow("workflow-id-here")
print(f"Name: {workflow['name']}")
print(f"Nodes: {len(workflow['nodes'])}")
```

#### Import Workflow

```python
# Prepare workflow data
workflow_data = {
    "name": "My Workflow",
    "nodes": [
        {
            "name": "Start",
            "type": "n8n-nodes-base.start",
            "typeVersion": 1,
            "position": [250, 300],
            "parameters": {}
        }
    ],
    "connections": {},
    "settings": {"executionOrder": "v1"}
}

# Import
result = client.import_workflow(workflow_data)
print(f"Imported workflow ID: {result['id']}")

# Import and activate
result = client.import_workflow(workflow_data, activate=True)
```

#### Export Workflow

```python
workflow = client.export_workflow("workflow-id")

# Save to file
import json
with open("workflow.json", "w") as f:
    json.dump(workflow, f, indent=2)
```

#### Update Workflow

```python
# Get workflow
workflow = client.get_workflow("workflow-id")

# Modify
workflow['name'] = "Updated Name"

# Update
updated = client.update_workflow("workflow-id", workflow)
```

#### Delete Workflow

```python
success = client.delete_workflow("workflow-id")
if success:
    print("Workflow deleted")
```

#### Activate/Deactivate

```python
# Activate
client.activate_workflow("workflow-id")

# Deactivate
client.deactivate_workflow("workflow-id")
```

### Workflow Validation

```python
# Validate before import
is_valid, errors = client.validate_workflow_import(workflow_data)

if is_valid:
    print("Workflow is valid")
else:
    print("Validation errors:")
    for error in errors:
        print(f"  - {error}")
```

### Error Handling

```python
from skills.n8n_api_client import (
    N8nApiError,
    N8nAuthenticationError,
    N8nConnectionError,
    N8nValidationError,
    N8nRateLimitError
)

try:
    workflow = client.get_workflow("invalid-id")
except N8nAuthenticationError:
    print("Authentication failed - check API key")
except N8nConnectionError:
    print("Connection failed - is n8n running?")
except N8nValidationError:
    print("Workflow validation failed")
except N8nRateLimitError:
    print("Rate limit exceeded - wait before retrying")
except N8nApiError as e:
    print(f"API error: {e}")
```

---

## Integration Testing

### Running Tests

#### All Tests (Skip if n8n Not Configured)

```bash
pytest tests/test_n8n_integration.py -v
```

Tests will automatically skip if `N8N_API_URL` or `N8N_API_KEY` are not set.

#### Force Run Integration Tests

```bash
# Set environment variables
export N8N_API_URL=http://localhost:5678
export N8N_API_KEY=your-api-key

# Run tests
pytest tests/test_n8n_integration.py -v -m integration
```

#### Run Specific Test Class

```bash
pytest tests/test_n8n_integration.py::TestWorkflowOperations -v
```

#### Run Single Test

```bash
pytest tests/test_n8n_integration.py::TestWorkflowOperations::test_import_workflow -v
```

### Test Coverage

The integration test suite covers:

- ✅ Connection and authentication
- ✅ Version detection
- ✅ Workflow listing with filters
- ✅ Workflow import/export cycle
- ✅ Workflow CRUD operations
- ✅ Workflow activation/deactivation
- ✅ Validation (valid and invalid workflows)
- ✅ Error handling
- ✅ Rate limiting
- ✅ Health checks

### Test Fixtures

Tests automatically:
- Create test workflows
- Clean up after tests
- Skip if n8n not configured
- Verify connection before running

---

## CI/CD Integration

### GitHub Actions

The CI/CD pipeline includes optional n8n integration tests.

#### Configure Secrets

In your GitHub repository:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Add **Repository Variables**:
   - `N8N_API_URL`: Your n8n instance URL
3. Add **Repository Secrets**:
   - `N8N_API_KEY`: Your n8n API key

#### Workflow Configuration

The workflow automatically:
- Runs on push to main/develop
- Tests n8n connection
- Runs integration tests
- Continues even if tests fail (optional tests)

To make tests required:
```yaml
# In .github/workflows/ci.yml
- name: Run n8n integration tests
  run: pytest tests/test_n8n_integration.py -v -m integration
  # Remove this line to make tests required:
  continue-on-error: false
```

### Local CI Testing

```bash
# Simulate CI environment
export N8N_API_URL=http://localhost:5678
export N8N_API_KEY=your-api-key
export PYTHONPATH=$PWD

# Run connection test
python scripts/test_n8n_connection.py

# Run integration tests
pytest tests/test_n8n_integration.py -v -m integration
```

---

## Troubleshooting

### Connection Issues

#### Error: "Connection failed: Connection refused"

**Cause**: n8n is not running or URL is incorrect

**Solution**:
```bash
# Check if n8n is running
curl http://localhost:5678

# Verify n8n URL in .env
echo $N8N_API_URL
```

#### Error: "Authentication failed"

**Cause**: Invalid or missing API key

**Solution**:
1. Verify API key in n8n: Settings → n8n API
2. Check `.env` file has correct `N8N_API_KEY`
3. API key should not have extra spaces or quotes

```bash
# Test API key
curl -H "X-N8N-API-KEY: your-key" http://localhost:5678/api/v1/workflows
```

#### Error: "Request timeout"

**Cause**: n8n is slow to respond

**Solution**:
```python
# Increase timeout
client = N8nApiClient(
    api_url="http://localhost:5678",
    api_key="your-key",
    timeout=60  # Increase to 60 seconds
)
```

### Import Issues

#### Error: "Missing required field: nodes"

**Cause**: Workflow JSON is invalid

**Solution**:
```python
# Validate before import
is_valid, errors = client.validate_workflow_import(workflow_data)
print(errors)
```

#### Error: "Workflow execution failed"

**Cause**: Node parameters are incorrect or nodes incompatible

**Solution**:
1. Check node `typeVersion` matches n8n version
2. Verify all required parameters are set
3. Test workflow manually in n8n first

### Version Detection Issues

#### Warning: "Could not detect exact version"

**Cause**: n8n doesn't expose version in older versions

**Impact**: Low - API still works

**Solution**: This is expected. Client will report "1.x" as version.

### Rate Limiting

#### Error: "Rate limit exceeded"

**Cause**: Too many requests in short time

**Solution**:
```python
# Adjust rate limits
client = N8nApiClient(
    api_url="http://localhost:5678",
    api_key="your-key",
    rate_limit_requests=30,  # Reduce to 30/min
    rate_limit_period=60
)
```

### Test Issues

#### Tests Skip with "n8n not configured"

**Cause**: Environment variables not set

**Solution**:
```bash
# Set in terminal
export N8N_API_URL=http://localhost:5678
export N8N_API_KEY=your-api-key

# Or in .env file
echo "N8N_API_URL=http://localhost:5678" >> .env
echo "N8N_API_KEY=your-api-key" >> .env
```

---

## API Reference

### N8nApiClient

#### Constructor

```python
N8nApiClient(
    api_url: str,
    api_key: Optional[str] = None,
    timeout: int = 30,
    max_retries: int = 3,
    rate_limit_requests: int = 60,
    rate_limit_period: int = 60
)
```

#### Methods

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `test_connection()` | None | `(bool, str)` | Test API connection |
| `get_n8n_version()` | None | `Dict` | Detect n8n version |
| `list_workflows()` | `limit`, `active`, `tags` | `List[Dict]` | List workflows |
| `get_workflow()` | `workflow_id` | `Dict` | Get workflow by ID |
| `import_workflow()` | `workflow_data`, `activate` | `Dict` | Import/create workflow |
| `export_workflow()` | `workflow_id` | `Dict` | Export workflow |
| `update_workflow()` | `workflow_id`, `workflow_data` | `Dict` | Update workflow |
| `delete_workflow()` | `workflow_id` | `bool` | Delete workflow |
| `activate_workflow()` | `workflow_id` | `Dict` | Activate workflow |
| `deactivate_workflow()` | `workflow_id` | `Dict` | Deactivate workflow |
| `validate_workflow_import()` | `workflow_data` | `(bool, List[str])` | Validate workflow |
| `test_workflow_execution()` | `workflow_id`, `input_data` | `Dict` | Test execute workflow |
| `health_check()` | None | `Dict` | Comprehensive health check |

### Helper Functions

```python
create_client_from_env() -> Optional[N8nApiClient]
```

Creates client from environment variables (`N8N_API_URL`, `N8N_API_KEY`).

### Exceptions

- `N8nApiError`: Base exception for all n8n API errors
- `N8nAuthenticationError`: Authentication failed
- `N8nConnectionError`: Connection failed
- `N8nValidationError`: Workflow validation failed
- `N8nRateLimitError`: Rate limit exceeded

---

## Best Practices

### Security

1. **Never commit API keys** to version control
2. **Use environment variables** for sensitive data
3. **Rotate API keys** periodically
4. **Use HTTPS** in production
5. **Restrict API key scope** if possible

### Performance

1. **Use rate limiting** to avoid overloading n8n
2. **Batch operations** when possible
3. **Cache workflow data** if read frequently
4. **Use pagination** for large workflow lists
5. **Set appropriate timeouts** based on workflow complexity

### Error Handling

1. **Always validate** workflows before import
2. **Handle specific exceptions** (don't catch all)
3. **Log errors** with context
4. **Implement retries** for transient failures
5. **Provide clear error messages** to users

### Testing

1. **Use test fixtures** for cleanup
2. **Mock external calls** in unit tests
3. **Use real n8n** for integration tests
4. **Test error cases** explicitly
5. **Skip tests** when n8n unavailable

### Code Examples

#### Production-Ready Import

```python
from skills.n8n_api_client import (
    create_client_from_env,
    N8nValidationError,
    N8nApiError
)
import logging

logger = logging.getLogger(__name__)

def import_workflow_safe(workflow_data):
    """Safely import workflow with validation and error handling."""
    client = create_client_from_env()
    if not client:
        logger.error("n8n client not configured")
        return None

    try:
        # 1. Validate workflow
        is_valid, errors = client.validate_workflow_import(workflow_data)
        if not is_valid:
            logger.error(f"Workflow validation failed: {errors}")
            raise N8nValidationError(f"Invalid workflow: {errors}")

        # 2. Import workflow
        result = client.import_workflow(workflow_data)
        logger.info(f"Imported workflow {result['id']}: {result['name']}")

        return result

    except N8nValidationError as e:
        logger.error(f"Validation error: {e}")
        raise
    except N8nApiError as e:
        logger.error(f"Import failed: {e}")
        raise
    except Exception as e:
        logger.exception("Unexpected error during import")
        raise
```

#### Batch Export

```python
def export_all_workflows(output_dir="./workflows"):
    """Export all workflows to directory."""
    import json
    from pathlib import Path

    client = create_client_from_env()
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Get all workflows
    workflows = client.list_workflows()
    print(f"Exporting {len(workflows)} workflows...")

    for wf in workflows:
        # Export full workflow
        full_wf = client.export_workflow(wf['id'])

        # Save to file
        filename = f"{wf['id']}_{wf['name'].replace(' ', '_')}.json"
        filepath = output_path / filename

        with open(filepath, 'w') as f:
            json.dump(full_wf, f, indent=2)

        print(f"  ✓ {filename}")

    print(f"\nExported {len(workflows)} workflows to {output_path}")
```

---

## Additional Resources

- **n8n API Documentation**: https://docs.n8n.io/api/
- **n8n Community Forum**: https://community.n8n.io
- **Project Automata Docs**: `/docs` directory
- **CRITICAL_REVIEW.md**: Known issues and improvements

---

## Support

For issues related to:
- **n8n API Client**: Open issue on GitHub
- **n8n API**: Check n8n documentation
- **Authentication**: Verify n8n Settings → n8n API

---

**Last Updated**: 2025-11-20
**Version**: 1.0.0
**Author**: Project Automata - Agent 3
