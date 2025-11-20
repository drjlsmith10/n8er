# Error Handling Patterns Guide

**Author:** Project Automata - Agent 5 (High Priority Features)
**Version:** 2.1.0
**Date:** 2025-11-20
**Issue:** #11 - Expanded Error Handling Patterns

---

## Overview

This guide provides comprehensive error handling patterns for n8n workflows, covering 20+ common error scenarios and proven solutions. Proper error handling is critical for production workflows to ensure reliability, debuggability, and graceful degradation.

**Why Error Handling Matters:**
- Prevents workflow failures from cascading
- Provides clear debugging information
- Enables automatic recovery from transient failures
- Improves user experience with meaningful error messages
- Reduces manual intervention requirements

---

## Table of Contents

1. [Error Handling Principles](#error-handling-principles)
2. [Common Error Patterns](#common-error-patterns)
3. [Retry Strategies](#retry-strategies)
4. [Circuit Breaker Pattern](#circuit-breaker-pattern)
5. [Dead Letter Queue Pattern](#dead-letter-queue-pattern)
6. [Input Validation](#input-validation)
7. [Error Logging and Monitoring](#error-logging-and-monitoring)
8. [Best Practices](#best-practices)
9. [Pattern Reference](#pattern-reference)

---

## Error Handling Principles

### 1. Fail Gracefully

Always provide meaningful error responses:

```javascript
// Good - Informative error response
return [{
  json: {
    success: false,
    error: 'Invalid email format',
    field: 'email',
    provided_value: $json.email
  }
}];

// Bad - Generic error
throw new Error('Error');
```

### 2. Use Try-Catch Blocks

Wrap risky operations in try-catch:

```javascript
try {
  const result = JSON.parse($json.data);
  return [{ json: result }];
} catch (error) {
  return [{
    json: {
      error: true,
      message: error.message,
      original_data: $json.data
    }
  }];
}
```

### 3. Validate Early

Check inputs before processing:

```javascript
// Validate required fields
const required = ['email', 'name', 'action'];
const missing = required.filter(field => !$json[field]);

if (missing.length > 0) {
  throw new Error(`Missing required fields: ${missing.join(', ')}`);
}
```

### 4. Log Errors

Always log errors for debugging:

```javascript
// Log and pass through error
console.error('API call failed:', error.message);
console.error('Stack:', error.stack);
console.error('Data:', $json);

return [{ json: { error: true, message: error.message } }];
```

### 5. Provide Retry Logic

Implement retries for transient failures:

```javascript
const context = $node.context;
let retryCount = context.get('retryCount') || 0;
const maxRetries = 3;

if (retryCount < maxRetries) {
  retryCount++;
  context.set('retryCount', retryCount);
  // Retry logic
} else {
  // Give up and handle failure
}
```

---

## Common Error Patterns

### 1. Webhook Timeout

**Problem:** Long-running workflow exceeds webhook timeout

**Solution:**
```python
builder.add_trigger(
    "webhook",
    "Webhook",
    parameters={
        "path": "long-process",
        "httpMethod": "POST",
        "responseMode": "onReceived"  # Respond immediately
    }
)

# Process asynchronously
builder.add_node(
    "n8n-nodes-base.function",
    "Long Process",
    parameters={
        "functionCode": """
// Process in background
// Use Queue or separate workflow for long operations
"""
    }
)
```

### 2. Memory Exhaustion

**Problem:** Processing large datasets causes out-of-memory errors

**Solution:**
```python
# Use SplitInBatches node
builder.add_node(
    "n8n-nodes-base.splitInBatches",
    "Batch Data",
    parameters={
        "batchSize": 100,
        "options": {}
    }
)

# Process in smaller chunks
builder.add_node(
    "n8n-nodes-base.function",
    "Process Batch",
    parameters={
        "functionCode": """
// Process only current batch
const batch = items.map(item => ({
  json: processItem(item.json)
}));
return batch;
"""
    }
)
```

### 3. Rate Limiting (429 Errors)

**Problem:** API returns 429 Too Many Requests

**Solution:**
```python
builder.add_node(
    "n8n-nodes-base.httpRequest",
    "API Call",
    parameters={
        "url": "https://api.example.com/data",
        "method": "GET",
        "options": {
            "retry": {
                "enabled": True,
                "maxRetries": 5,
                "waitBetween": 2000  # Start with 2 second delay
            }
        }
    }
)

# Add exponential backoff logic
builder.add_node(
    "n8n-nodes-base.function",
    "Calculate Backoff",
    parameters={
        "functionCode": """
const context = $node.context;
const retryCount = context.get('retryCount') || 0;

// Exponential backoff: 2^n seconds
const delaySeconds = Math.pow(2, retryCount);
const maxDelay = 300; // Cap at 5 minutes

return [{
  json: {
    delay: Math.min(delaySeconds, maxDelay),
    retryCount: retryCount
  }
}];
"""
    }
)
```

### 4. Database Connection Failure

**Problem:** Cannot connect to database

**Solution:**
```python
builder.add_node(
    "n8n-nodes-base.postgres",
    "Database Query",
    parameters={
        "operation": "select",
        "table": "users",
        "options": {
            "timeout": 10000,  # 10 second timeout
            "queryTimeout": 30000
        }
    }
)

# Add connection retry logic
builder.add_node(
    "n8n-nodes-base.function",
    "Connection Retry",
    parameters={
        "functionCode": """
const context = $node.context;
const maxRetries = 3;
let retryCount = context.get('dbRetryCount') || 0;

if (retryCount < maxRetries) {
  retryCount++;
  context.set('dbRetryCount', retryCount);

  // Wait before retry: 2, 4, 8 seconds
  const delay = Math.pow(2, retryCount);

  return [{
    json: {
      shouldRetry: true,
      delay: delay,
      attempt: retryCount
    }
  }];
} else {
  // Max retries exhausted
  return [{
    json: {
      shouldRetry: false,
      error: 'Database connection failed after ' + maxRetries + ' attempts'
    }
  }];
}
"""
    }
)
```

### 5. Authentication Errors (401/403)

**Problem:** API returns unauthorized or forbidden

**Solution:**
```javascript
// Check response status
if ($json.statusCode === 401 || $json.statusCode === 403) {
  console.error('Authentication failed:', $json.statusCode);

  // Try to refresh token if using OAuth
  const context = $node.context;
  const tokenRefreshed = context.get('tokenRefreshed') || false;

  if (!tokenRefreshed) {
    context.set('tokenRefreshed', true);
    return [{
      json: {
        action: 'refreshToken',
        originalRequest: $json
      }
    }];
  }

  // Token refresh failed, report error
  return [{
    json: {
      error: 'Authentication failed',
      statusCode: $json.statusCode,
      message: 'Credentials may be expired or invalid'
    }
  }];
}
```

### 6. Network Timeouts

**Problem:** Requests timeout waiting for response

**Solution:**
```python
builder.add_node(
    "n8n-nodes-base.httpRequest",
    "API Call with Timeout",
    parameters={
        "url": "https://slow-api.example.com/data",
        "method": "GET",
        "options": {
            "timeout": 30000,  # 30 second timeout
            "retry": {
                "enabled": True,
                "maxRetries": 3,
                "waitBetween": 5000
            }
        }
    }
)

# Fallback on timeout
builder.add_node(
    "n8n-nodes-base.function",
    "Timeout Handler",
    parameters={
        "functionCode": """
// Check if request timed out
if ($json.error && $json.error.code === 'ETIMEDOUT') {
  console.warn('Request timed out, using cached data');

  // Return cached data or default
  return [{
    json: {
      cached: true,
      data: getCachedData(),
      warning: 'Using cached data due to timeout'
    }
  }];
}

return [{ json: $json }];
"""
    }
)
```

### 7. JSON Parse Errors

**Problem:** Invalid JSON in API response

**Solution:**
```javascript
// Safely parse JSON
let data;
try {
  data = JSON.parse($json.body);
} catch (error) {
  console.error('JSON parse error:', error.message);
  console.error('Raw body:', $json.body);

  return [{
    json: {
      error: true,
      message: 'Invalid JSON response',
      raw_body: $json.body.substring(0, 200),  // First 200 chars
      parse_error: error.message
    }
  }];
}

return [{ json: data }];
```

### 8. Null/Undefined Data Errors

**Problem:** Accessing properties on null/undefined

**Solution:**
```javascript
// Use optional chaining and nullish coalescing

// Good - Safe access
const email = $json?.user?.email ?? 'no-email@example.com';
const name = $json?.user?.profile?.name ?? 'Unknown';
const age = $json?.user?.age ?? 0;

// Field existence check
if (!$json?.user?.email) {
  throw new Error('User email is required');
}

// Safe array access
const items = $json?.items ?? [];
const firstItem = items[0] ?? null;
```

---

## Retry Strategies

### Exponential Backoff

```javascript
const context = $node.context;
const maxRetries = 5;
let retryCount = context.get('retryCount') || 0;

if (retryCount < maxRetries) {
  retryCount++;
  context.set('retryCount', retryCount);

  // Calculate exponential backoff delay
  const baseDelay = 1000; // 1 second
  const delayMs = baseDelay * Math.pow(2, retryCount - 1);
  const maxDelay = 60000; // Cap at 1 minute

  const actualDelay = Math.min(delayMs, maxDelay);

  console.log(`Retry ${retryCount}/${maxRetries} after ${actualDelay}ms`);

  return [{
    json: {
      shouldRetry: true,
      delaySeconds: Math.ceil(actualDelay / 1000),
      attempt: retryCount
    }
  }];
} else {
  console.error('Max retries exceeded');
  return [{
    json: {
      shouldRetry: false,
      error: 'Operation failed after ' + maxRetries + ' retries'
    }
  }];
}
```

### Linear Backoff

```javascript
const context = $node.context;
const maxRetries = 3;
const delaySeconds = 5; // Fixed 5 second delay
let retryCount = context.get('retryCount') || 0;

if (retryCount < maxRetries) {
  retryCount++;
  context.set('retryCount', retryCount);

  return [{
    json: {
      shouldRetry: true,
      delaySeconds: delaySeconds,
      attempt: retryCount
    }
  }];
} else {
  return [{
    json: {
      shouldRetry: false,
      error: 'Max retries exceeded'
    }
  }];
}
```

### Jittered Backoff

```javascript
// Exponential backoff with jitter (randomization)
const context = $node.context;
let retryCount = context.get('retryCount') || 0;
retryCount++;
context.set('retryCount', retryCount);

const baseDelay = 1000;
const exponentialDelay = baseDelay * Math.pow(2, retryCount - 1);

// Add jitter: random between 0 and exponentialDelay
const jitter = Math.random() * exponentialDelay;
const delayMs = exponentialDelay + jitter;

return [{
  json: {
    delaySeconds: Math.ceil(delayMs / 1000),
    attempt: retryCount
  }
}];
```

---

## Circuit Breaker Pattern

Prevents cascading failures by stopping requests to failing services.

### Implementation

```python
# See enhanced_templates.py: circuit_breaker_pattern()

builder = WorkflowBuilder("Circuit Breaker")

# Check circuit state
builder.add_node(
    "n8n-nodes-base.function",
    "Check Circuit",
    parameters={
        "functionCode": """
const maxFailures = 5;
const resetTimeout = 300000; // 5 minutes

const context = $node.context;
const failures = context.get('failureCount') || 0;
const lastFailure = context.get('lastFailureTime') || 0;
const circuitOpen = context.get('circuitOpen') || false;
const now = Date.now();

// Reset circuit if timeout passed
if (circuitOpen && (now - lastFailure) > resetTimeout) {
  context.set('circuitOpen', false);
  context.set('failureCount', 0);
  console.log('Circuit breaker reset');
}

// Check if circuit is open
if (context.get('circuitOpen')) {
  return [{
    json: {
      circuit_open: true,
      message: 'Service temporarily unavailable',
      retry_after: Math.ceil((resetTimeout - (now - lastFailure)) / 1000)
    }
  }];
}

return [{ json: { circuit_open: false } }];
"""
    }
)

# On API success - reset counter
builder.add_node(
    "n8n-nodes-base.function",
    "On Success",
    parameters={
        "functionCode": """
const context = $node.context;
context.set('failureCount', 0);
context.set('circuitOpen', false);

return [{ json: { success: true, data: $json } }];
"""
    }
)

# On API failure - increment counter
builder.add_node(
    "n8n-nodes-base.function",
    "On Failure",
    parameters={
        "functionCode": """
const context = $node.context;
const maxFailures = 5;
let failures = (context.get('failureCount') || 0) + 1;

context.set('failureCount', failures);
context.set('lastFailureTime', Date.now());

// Open circuit if threshold exceeded
if (failures >= maxFailures) {
  context.set('circuitOpen', true);
  console.log('Circuit breaker opened after ' + failures + ' failures');
}

return [{
  json: {
    success: false,
    failures: failures,
    circuit_open: failures >= maxFailures
  }
}];
"""
    }
)
```

---

## Dead Letter Queue Pattern

Handle permanently failed items separately for manual review.

```python
builder = WorkflowBuilder("Dead Letter Queue")

# Try to process item
builder.add_node(
    "n8n-nodes-base.httpRequest",
    "Process Item",
    parameters={
        "url": "https://api.example.com/process",
        "method": "POST",
        "options": {
            "retry": {
                "enabled": True,
                "maxRetries": 3,
                "waitBetween": 1000
            }
        }
    }
)

# Check if processing failed
builder.add_node(
    "n8n-nodes-base.if",
    "Check Success",
    parameters={
        "conditions": {
            "number": [{
                "value1": "={{ $json.statusCode }}",
                "operation": "equal",
                "value2": 200
            }]
        }
    }
)

# Send failed items to dead letter queue
builder.add_node(
    "n8n-nodes-base.postgres",
    "Dead Letter Queue",
    parameters={
        "operation": "insert",
        "table": "failed_items",
        "columns": "item_id,error_message,original_data,failed_at,retry_count",
        "values": """
={{ $json.id }},
={{ $json.error }},
={{ JSON.stringify($json.original) }},
={{ new Date().toISOString() }},
={{ $json.retryCount }}
"""
    }
)

# Log success
builder.add_node(
    "n8n-nodes-base.function",
    "Success Log",
    parameters={
        "functionCode": """
console.log('Item processed successfully:', $json.id);
return [{ json: $json }];
"""
    }
)

builder.connect("Process Item", "Check Success")
builder.connect("Check Success", "Success Log", source_output=0)  # Success
builder.connect("Check Success", "Dead Letter Queue", source_output=1)  # Failure
```

---

## Input Validation

### Comprehensive Validation Example

```javascript
// Validate incoming webhook data
try {
  // 1. Check required fields
  const required = ['email', 'name', 'action'];
  const missing = required.filter(field => !$json[field]);

  if (missing.length > 0) {
    throw new Error(`Missing required fields: ${missing.join(', ')}`);
  }

  // 2. Validate email format
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test($json.email)) {
    throw new Error('Invalid email format');
  }

  // 3. Validate field types
  if (typeof $json.name !== 'string') {
    throw new Error('Name must be a string');
  }

  // 4. Validate allowed values
  const allowedActions = ['create', 'update', 'delete'];
  if (!allowedActions.includes($json.action)) {
    throw new Error(`Invalid action. Allowed: ${allowedActions.join(', ')}`);
  }

  // 5. Sanitize data
  const sanitized = {
    email: $json.email.trim().toLowerCase(),
    name: $json.name.trim(),
    action: $json.action.toLowerCase(),
    metadata: $json.metadata || {},
    validated_at: new Date().toISOString()
  };

  return [{ json: sanitized }];

} catch (error) {
  return [{
    json: {
      error: true,
      message: error.message,
      field: extractFieldFromError(error.message),
      original_data: $json
    }
  }];
}
```

---

## Error Logging and Monitoring

### Log to External Service

```python
builder.add_node(
    "n8n-nodes-base.httpRequest",
    "Log Error",
    parameters={
        "url": "https://logging.example.com/errors",
        "method": "POST",
        "sendBody": True,
        "ignoreResponseCode": True,  # Don't fail if logging fails
        "options": {
            "timeout": 5000  # Quick timeout
        },
        "bodyParameters": {
            "parameters": [
                {"name": "level", "value": "error"},
                {"name": "workflow", "value": "={{ $workflow.name }}"},
                {"name": "node", "value": "={{ $node.name }}"},
                {"name": "error", "value": "={{ $json.error }}"},
                {"name": "timestamp", "value": "={{ new Date().toISOString() }}"}
            ]
        }
    }
)
```

### Structured Error Object

```javascript
// Create comprehensive error object
const errorInfo = {
  success: false,
  error: {
    type: 'ValidationError',
    message: error.message,
    code: 'VAL_001',
    field: 'email'
  },
  context: {
    workflow: $workflow.name,
    node: $node.name,
    execution_id: $execution.id,
    timestamp: new Date().toISOString()
  },
  data: {
    input: $json,
    user_id: $json.userId
  }
};

return [{ json: errorInfo }];
```

---

## Best Practices

### 1. Always Validate Input

```javascript
// ✅ Good
if (!$json.email || !$json.name) {
  throw new Error('Email and name are required');
}

// ❌ Bad
// Assuming data exists
const user = processUser($json.email, $json.name);
```

### 2. Use Appropriate Timeout Values

```python
# ✅ Good
"options": {
    "timeout": 10000  # Reasonable 10 second timeout
}

# ❌ Bad
"options": {
    "timeout": 300000  # 5 minutes - too long
}
```

### 3. Limit Retry Attempts

```javascript
// ✅ Good
const maxRetries = 3;

// ❌ Bad
const maxRetries = 100;  // Will retry forever
```

### 4. Log Errors with Context

```javascript
// ✅ Good
console.error('API call failed', {
  url: $json.url,
  method: 'POST',
  error: error.message,
  statusCode: $json.statusCode,
  timestamp: new Date().toISOString()
});

// ❌ Bad
console.error('Error');
```

### 5. Fail Fast for Invalid Input

```javascript
// ✅ Good - Validate immediately
if (!isValidEmail($json.email)) {
  throw new Error('Invalid email');
}

// ❌ Bad - Process then fail
const result = await processData($json);
if (!isValidEmail(result.email)) {
  throw new Error('Invalid email');
}
```

### 6. Use Circuit Breakers for External Services

```javascript
// ✅ Good - Check circuit state first
if (isCircuitOpen()) {
  return failFast();
}

// ❌ Bad - Always try request
const result = await makeRequest();
```

### 7. Clean Up on Errors

```javascript
// ✅ Good - Clean up resources
try {
  const file = openFile();
  const result = process(file);
  closeFile(file);
  return result;
} catch (error) {
  closeFile(file);  // Clean up
  throw error;
}

// ❌ Bad - Leave resources open
const file = openFile();
const result = process(file);  // May throw
closeFile(file);
```

---

## Pattern Reference

Quick reference to all 20+ error patterns in knowledge base:

1. **Webhook Timeout** - Respond immediately, process async
2. **Memory Exhaustion** - Use SplitInBatches
3. **Rate Limiting** - Implement exponential backoff
4. **Credentials Not Found** - Document required credentials
5. **Database Connection Failure** - Retry with backoff
6. **Database Query Timeout** - Optimize queries, increase timeout
7. **Authentication Error** - Check credentials, refresh tokens
8. **API Timeout** - Set reasonable timeouts, retry
9. **Network Error** - Retry with increasing delays
10. **JSON Parse Error** - Validate and handle parse failures
11. **Data Validation Failed** - Validate early, provide defaults
12. **Service Unavailable** - Circuit breaker pattern
13. **Quota Exceeded** - Track usage, implement rate limiting
14. **Circuit Breaker** - Stop requests to failing services
15. **Exponential Backoff** - Increase delay between retries
16. **Dead Letter Queue** - Store permanently failed items
17. **Batch Processing Error** - Process items individually
18. **SSL Certificate Error** - Fix certificates, don't disable validation
19. **File Not Found** - Check file existence before processing
20. **Workflow Execution Timeout** - Optimize or split workflows
21. **Null Pointer Error** - Use optional chaining and defaults

See `knowledge_base/error_patterns.json` for detailed solutions.

---

## Examples Repository

Complete working examples in `examples/error_handling/`:
- `basic_validation.py` - Input validation patterns
- `retry_strategies.py` - Exponential and linear backoff
- `circuit_breaker.py` - Circuit breaker implementation
- `dead_letter_queue.py` - Failed item handling
- `webhook_error_handling.py` - Webhook-specific patterns

---

## Related Documentation

- [CREDENTIALS_GUIDE.md](./CREDENTIALS_GUIDE.md) - Managing credentials securely
- [DEPLOYMENT.md](./DEPLOYMENT.md) - Production deployment best practices
- [architecture.md](./architecture.md) - System architecture

---

**Questions or Issues?**
- GitHub Issues: https://github.com/drjlsmith10/n8er/issues
- Knowledge Base: `/knowledge_base/error_patterns.json`
- Templates: `/skills/enhanced_templates.py`
