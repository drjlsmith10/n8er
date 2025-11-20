# n8n Expression Syntax Reference

**Version:** 2.0.0-alpha
**Last Updated:** 2025-11-20
**Compatible with:** n8n v1.50.0 - v1.70.x+

---

## Overview

n8n expressions allow you to dynamically set node parameters based on data from previous nodes, environment variables, or JavaScript logic. This document describes the expression syntax used by Project Automata when generating workflows.

---

## Expression Syntax

### Basic Syntax

Expressions in n8n use double curly braces: `{{ }}`

```javascript
{{ expression here }}
```

In parameter fields, expressions are prefixed with `=` to explicitly mark them as expressions:

```json
{
  "toEmail": "={{ $json.email }}",
  "subject": "={{ $json.subject }}",
  "timestamp": "={{ $now.toISO() }}"
}
```

### Key Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `$json` | Data from current item | `{{ $json.email }}` |
| `$node["NodeName"]` | Access data from specific node | `{{ $node["HTTP Request"].json.data }}` |
| `$()` | Shorthand for accessing nodes | `{{ $('HTTP Request').item.json.data }}` |
| `$items()` | Access all items from a node | `{{ $items('HTTP Request') }}` |
| `$now` | Current timestamp (Luxon DateTime) | `{{ $now.toISO() }}` |
| `$today` | Today's date at midnight | `{{ $today.toISO() }}` |
| `$workflow` | Workflow metadata | `{{ $workflow.name }}` |
| `$execution` | Execution metadata | `{{ $execution.id }}` |

---

## Common Expression Patterns

### 1. Accessing Current Item Data

```javascript
// Access field from current item
{{ $json.fieldName }}

// Access nested fields
{{ $json.user.email }}

// Access array elements
{{ $json.items[0].name }}
```

### 2. Accessing Data from Previous Nodes

```javascript
// Using $() shorthand
{{ $('Webhook').item.json.id }}
{{ $('HTTP Request').item.json.response }}

// Using $node array syntax
{{ $node["Webhook"].json[0].data }}

// Get all items from a node
{{ $items('HTTP Request')[0].json.result }}
```

### 3. String Operations

```javascript
// Concatenation
{{ $json.firstName + ' ' + $json.lastName }}

// Template literals (in function nodes)
`Welcome ${$json.name}!`

// String methods
{{ $json.email.toLowerCase() }}
{{ $json.title.substring(0, 100) }}
```

### 4. Date and Time

```javascript
// Current timestamp
{{ $now.toISO() }}

// Format dates
{{ $now.toFormat('yyyy-MM-dd') }}

// Date arithmetic
{{ $now.plus({ days: 7 }).toISO() }}
{{ $now.minus({ hours: 1 }).toISO() }}

// Parse dates
{{ DateTime.fromISO($json.createdAt).toFormat('MMM dd, yyyy') }}
```

### 5. Conditional Logic (IF Nodes)

```json
{
  "conditions": {
    "string": [{
      "value1": "={{ $json.status }}",
      "operation": "equal",
      "value2": "active"
    }],
    "number": [{
      "value1": "={{ $json.count }}",
      "operation": "largerEqual",
      "value2": 10
    }],
    "boolean": [{
      "value1": "={{ $json.isEnabled }}",
      "operation": "equal",
      "value2": true
    }]
  }
}
```

### 6. Array Operations

```javascript
// Map array
{{ $json.items.map(item => item.name) }}

// Filter array
{{ $json.items.filter(item => item.status === 'active') }}

// Get array length
{{ $json.items.length }}

// Join array
{{ $json.tags.join(', ') }}
```

---

## Function Node Code

Function nodes use plain JavaScript without `{{ }}` wrappers:

```javascript
// Access current item
const email = $json.email;
const data = $json.data;

// Access all items
for (const item of items) {
  console.log(item.json.name);
}

// Access specific node
const webhookData = $node["Webhook"].json;

// Return modified items
return items.map(item => ({
  json: {
    ...item.json,
    processed: true,
    timestamp: new Date().toISOString()
  }
}));
```

### Context API (Persistent Storage)

```javascript
// Store data across executions
$node.context.set('counter', 5);

// Retrieve stored data
const counter = $node.context.get('counter') || 0;

// Increment and store
$node.context.set('counter', counter + 1);
```

---

## Expression Examples from Project Automata

### 1. Email with Dynamic Content

```json
{
  "toEmail": "={{ $json.email }}",
  "subject": "Welcome {{ $json.name }}!",
  "text": "Hi {{ $json.name }},\n\nThank you for signing up on {{ $now.toFormat('MMMM dd, yyyy') }}."
}
```

### 2. Conditional Slack Notification

```json
{
  "channel": "#alerts",
  "text": "{{ $json.success ? '✅ Success' : '❌ Failed' }}",
  "attachments": [{
    "color": "{{ $json.success ? 'good' : 'danger' }}",
    "text": "Status: {{ $json.statusCode }}"
  }]
}
```

### 3. Dynamic Wait Duration

```json
{
  "amount": "={{ $json.delaySeconds }}",
  "unit": "seconds"
}
```

### 4. API URL with Parameters

```json
{
  "url": "https://api.example.com/users/{{ $json.userId }}/posts",
  "method": "GET",
  "qs": {
    "limit": "={{ $json.pageSize || 10 }}",
    "offset": "={{ $json.offset || 0 }}"
  }
}
```

### 5. Data Validation in Function Node

```javascript
// Validate required fields
const required = ['id', 'timestamp', 'data'];
const missing = required.filter(field => !$json[field]);

if (missing.length > 0) {
  throw new Error(`Missing required fields: ${missing.join(', ')}`);
}

// Pass through validated data
return [{ json: $json }];
```

### 6. Retry Logic with Exponential Backoff

```javascript
const context = $node.context;
const maxRetries = 3;
let retryCount = context.get('retryCount') || 0;

if (retryCount < maxRetries) {
  retryCount++;
  context.set('retryCount', retryCount);

  // Calculate exponential backoff delay (2^n seconds)
  const delaySeconds = Math.pow(2, retryCount);

  return [{
    json: {
      ...items[0].json,
      retryCount,
      delaySeconds,
      shouldRetry: true
    }
  }];
} else {
  return [{
    json: {
      ...items[0].json,
      shouldRetry: false,
      error: 'Max retries exceeded'
    }
  }];
}
```

---

## Best Practices

### 1. Always Handle Missing Data

```javascript
// Bad - will error if email is undefined
{{ $json.email }}

// Good - provide fallback
{{ $json.email || 'default@example.com' }}

// Good - check existence
{{ $json.email ? $json.email : 'N/A' }}
```

### 2. Use Type Coercion Carefully

```javascript
// Ensure numbers
{{ parseInt($json.count) || 0 }}
{{ parseFloat($json.price) || 0.0 }}

// Ensure strings
{{ String($json.value) }}

// Ensure arrays
{{ Array.isArray($json.items) ? $json.items : [] }}
```

### 3. Format Dates Consistently

```javascript
// ISO 8601 for APIs
{{ $now.toISO() }}

// Human-readable for displays
{{ $now.toFormat('MMMM dd, yyyy HH:mm') }}

// Unix timestamp
{{ $now.toSeconds() }}
```

### 4. Handle Errors Gracefully

```javascript
try {
  const data = JSON.parse($json.rawData);
  return [{ json: data }];
} catch (error) {
  return [{
    json: {
      error: 'Failed to parse JSON',
      message: error.message,
      raw: $json.rawData
    }
  }];
}
```

### 5. Keep Expressions Simple

```javascript
// Bad - too complex
{{ $json.items.filter(x => x.status === 'active').map(x => x.name).join(', ') }}

// Good - use Function node for complex logic
// In Function node:
const activeNames = items
  .filter(item => item.json.status === 'active')
  .map(item => item.json.name)
  .join(', ');

return [{ json: { activeNames } }];
```

---

## Common Pitfalls

### 1. Incorrect Node References

```javascript
// Wrong - quotes needed for node names with spaces
{{ $('HTTP Request').item.json.data }}

// Wrong - array syntax variation
{{ $node.HTTPRequest.json.data }}

// Correct
{{ $('HTTP Request').item.json.data }}
{{ $node["HTTP Request"].json[0].data }}
```

### 2. Mixing Expression Contexts

```javascript
// Wrong - {{ }} not needed in Function node code
const email = {{ $json.email }};  // Syntax error!

// Correct - direct access in Function nodes
const email = $json.email;
```

### 3. Forgetting Expression Prefix

```json
{
  // Wrong - treated as literal string
  "toEmail": "$json.email",

  // Correct - evaluated as expression
  "toEmail": "={{ $json.email }}"
}
```

---

## Resources

### Official n8n Documentation
- **Expressions Guide:** https://docs.n8n.io/code/expressions/
- **Expressions Cookbook:** https://docs.n8n.io/code/cookbook/expressions/
- **Built-in Methods:** https://docs.n8n.io/code/builtin/overview/

### Luxon (Date/Time Library)
- **Format Tokens:** https://moment.github.io/luxon/#/formatting
- **DateTime Methods:** https://moment.github.io/luxon/api-docs/index.html#datetime

### JavaScript References
- **MDN Web Docs:** https://developer.mozilla.org/en-US/docs/Web/JavaScript
- **Array Methods:** https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array

---

## Testing Expressions

### In n8n UI
1. Open workflow in n8n
2. Click on node with expression
3. Use "Execute Node" to see results
4. Check "Output" panel for evaluated expressions

### Using Project Automata
```bash
# Generate workflow with expressions
python skills/generate_workflow_json.py --template webhook_db_slack

# Validate expressions (future feature)
python skills/validate_expressions.py workflows/generated_workflow.json
```

---

## Version Compatibility

| n8n Version | Expression Syntax | Notes |
|-------------|-------------------|-------|
| 1.50.0+ | `{{ }}` with `=` prefix | Current standard |
| 1.30.0 - 1.49.x | `{{ }}` | Slight variations in function APIs |
| 1.0 - 1.29.x | `{{ }}` | Limited built-in methods |
| 0.x | Legacy syntax | Not supported |

**Project Automata Target:** n8n v1.50.0 - v1.70.x+

---

## Future Enhancements

Planned improvements for expression handling:

1. **Expression Validation:** Pre-flight validation of all expressions
2. **Type Checking:** Detect type mismatches before runtime
3. **Expression Builder:** UI helper for complex expressions
4. **Test Data:** Simulate expressions with sample data
5. **Performance Analysis:** Identify slow expressions

---

## Support

For questions or issues with expressions:

1. Check official n8n documentation
2. Review examples in this guide
3. Test in n8n UI with sample data
4. Open issue in Project Automata repository

---

**Document Version:** 1.0
**Maintained by:** Project Automata
**Last Updated:** 2025-11-20
