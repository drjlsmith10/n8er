"""
Enhanced Template Library - Community-Learned Patterns

This module extends the base template library with real-world patterns
learned from Reddit, YouTube, and Twitter communities.

Author: Project Automata - Cycle 02
Version: 2.0.0
"""

from typing import Dict, Optional

from skills.generate_workflow_json import WorkflowBuilder
from skills.knowledge_base import KnowledgeBase


class CommunityTemplateLibrary:
    """
    Extended template library with production-ready workflow patterns.

    NOTE: These are built-in sample templates curated by Automata developers.
    They are NOT scraped from external sources. The patterns are based on
    common n8n use cases and best practices.

    For actual community-sourced patterns, configure API keys and enable
    ENABLE_WEB_RESEARCH in .env.
    """

    def __init__(self, knowledge_base: Optional[KnowledgeBase] = None):
        """Initialize with optional knowledge base"""
        self.kb = knowledge_base

    @staticmethod
    def webhook_database_slack() -> Dict:
        """
        Pattern: Webhook → Database → Slack Notification
        Source: Automata built-in template

        Receive webhook, store in database, send Slack notification
        on success/error with proper error handling.
        """
        builder = WorkflowBuilder("Webhook DB Slack")

        # Webhook trigger
        builder.add_trigger(
            "webhook",
            "Webhook",
            parameters={
                "path": "data-ingestion",
                "httpMethod": "POST",
                "responseMode": "onReceived",
            },
        )

        # Validate payload
        builder.add_node(
            "n8n-nodes-base.function",
            "Validate Payload",
            parameters={
                "functionCode": """
// Validate required fields
const required = ['id', 'timestamp', 'data'];
const missing = required.filter(field => !$json[field]);

if (missing.length > 0) {
  throw new Error(`Missing required fields: ${missing.join(', ')}`);
}

// Pass through validated data
return [{ json: $json }];
"""
            },
        )

        # Store in database
        builder.add_node(
            "n8n-nodes-base.postgres",
            "Store in DB",
            type_version=2,
            parameters={
                "operation": "insert",
                "schema": "public",
                "table": "events",
                "columns": "id,timestamp,data",
                "options": {"queryBatching": "independently"},
            },
        )

        # Check if DB insert succeeded
        builder.add_node(
            "n8n-nodes-base.if",
            "Check DB Success",
            type_version=2,
            parameters={
                "conditions": {
                    "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
                    "conditions": [
                        {
                            "id": "condition-1",
                            "leftValue": "={{ $json.rowCount }}",
                            "rightValue": 1,
                            "operator": {"type": "number", "operation": "gte"},
                        }
                    ],
                    "combinator": "and",
                }
            },
        )

        # Success notification
        builder.add_node(
            "n8n-nodes-base.slack",
            "Success Slack",
            parameters={
                "channel": "#data-ingestion",
                "text": "✅ Data stored successfully",
                "attachments": [{"color": "good", "text": "ID: {{ $('Webhook').item.json.id }}"}],
            },
        )

        # Error notification
        builder.add_node(
            "n8n-nodes-base.slack",
            "Error Slack",
            parameters={
                "channel": "#alerts",
                "text": "❌ Database insert failed",
                "attachments": [{"color": "danger", "text": "Error: {{ $json.error }}"}],
            },
        )

        # Connect workflow
        builder.connect("Webhook", "Validate Payload")
        builder.connect("Validate Payload", "Store in DB")
        builder.connect("Store in DB", "Check DB Success")
        builder.connect("Check DB Success", "Success Slack", source_output=0)  # True
        builder.connect("Check DB Success", "Error Slack", source_output=1)  # False

        return builder.build()

    @staticmethod
    def scheduled_sync_with_retry() -> Dict:
        """
        Pattern: Scheduled Data Sync with Exponential Backoff Retry
        Source: Automata built-in template

        Sync data between systems with proper retry logic and error handling.
        """
        builder = WorkflowBuilder("Scheduled Sync with Retry")

        # Schedule trigger (every hour)
        builder.add_trigger(
            "cron", "Schedule", parameters={"triggerTimes": {"item": [{"mode": "everyHour"}]}}
        )

        # Fetch data from source API
        builder.add_node(
            "n8n-nodes-base.httpRequest",
            "Fetch Source Data",
            type_version=4,
            parameters={
                "url": "https://api.source.com/data",
                "method": "GET",
                "options": {
                    "timeout": 30000,
                    "retry": {"enabled": True, "maxRetries": 3, "waitBetween": 2000},
                },
            },
        )

        # Transform data
        builder.add_node(
            "n8n-nodes-base.function",
            "Transform",
            parameters={
                "functionCode": """
// Transform to destination format
const transformed = items.map(item => ({
  json: {
    id: item.json.source_id,
    name: item.json.source_name,
    timestamp: new Date().toISOString()
  }
}));

return transformed;
"""
            },
        )

        # Send to destination
        builder.add_node(
            "n8n-nodes-base.httpRequest",
            "Send to Destination",
            type_version=4,
            parameters={
                "url": "https://api.destination.com/data",
                "method": "POST",
                "options": {"timeout": 30000},
            },
        )

        # Check success
        builder.add_node(
            "n8n-nodes-base.if",
            "Check Success",
            type_version=2,
            parameters={
                "conditions": {
                    "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
                    "conditions": [
                        {
                            "id": "condition-2",
                            "leftValue": "={{ $json.statusCode }}",
                            "rightValue": 200,
                            "operator": {"type": "number", "operation": "equals"},
                        }
                    ],
                    "combinator": "and",
                }
            },
        )

        # Retry logic
        builder.add_node(
            "n8n-nodes-base.function",
            "Retry Counter",
            parameters={
                "functionCode": """
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
"""
            },
        )

        # Wait before retry
        builder.add_node(
            "n8n-nodes-base.wait",
            "Wait Before Retry",
            parameters={"amount": "={{ $json.delaySeconds }}", "unit": "seconds"},
        )

        # Connect workflow
        builder.connect_chain(
            "Schedule", "Fetch Source Data", "Transform", "Send to Destination", "Check Success"
        )
        builder.connect("Check Success", "Retry Counter", source_output=1)  # Failed
        builder.connect("Retry Counter", "Wait Before Retry")
        builder.connect("Wait Before Retry", "Fetch Source Data")  # Retry loop

        return builder.build()

    @staticmethod
    def rss_to_social() -> Dict:
        """
        Pattern: RSS to Social Media Automation
        Source: Automata built-in template

        Monitor RSS feed and automatically post to Twitter/LinkedIn.
        """
        builder = WorkflowBuilder("RSS to Social Media")

        # RSS trigger
        builder.add_trigger(
            "n8n-nodes-base.rssFeedTrigger",
            "RSS Feed",
            parameters={"feedUrl": "https://example.com/feed.xml"},
        )

        # Check if already posted (deduplication)
        builder.add_node(
            "n8n-nodes-base.function",
            "Check Duplicate",
            parameters={
                "functionCode": """
// In production, check against database of posted items
// For now, simple check
const itemId = $json.guid || $json.id;
const context = $node.context;
const postedIds = context.get('postedIds') || [];

if (postedIds.includes(itemId)) {
  return []; // Skip duplicate
}

postedIds.push(itemId);
context.set('postedIds', postedIds.slice(-100)); // Keep last 100

return [{ json: $json }];
"""
            },
        )

        # Format for Twitter
        builder.add_node(
            "n8n-nodes-base.function",
            "Format Tweet",
            parameters={
                "functionCode": """
let title = $json.title || '';
const url = $json.link || '';

// Truncate to fit Twitter limits (280 chars, reserve ~30 for URL)
const maxLength = 240;
if (title.length > maxLength) {
  title = title.substring(0, maxLength - 3) + '...';
}

// Add hashtags
const hashtags = ['automation', 'n8n'];
const text = `${title}\\n\\n${url}\\n\\n${hashtags.map(h => '#' + h).join(' ')}`;

return [{ json: { text }}];
"""
            },
        )

        # Post to Twitter
        builder.add_node(
            "n8n-nodes-base.twitter", "Post Tweet", parameters={"text": "={{ $json.text }}"}
        )

        # Wait to avoid spam detection
        builder.add_node("n8n-nodes-base.wait", "Wait", parameters={"amount": 5, "unit": "minutes"})

        # Post to LinkedIn
        builder.add_node(
            "n8n-nodes-base.linkedIn",
            "Post LinkedIn",
            parameters={"text": "={{ $('Format Tweet').item.json.text }}"},
        )

        # Connect workflow
        builder.connect_chain(
            "RSS Feed", "Check Duplicate", "Format Tweet", "Post Tweet", "Wait", "Post LinkedIn"
        )

        return builder.build()

    @staticmethod
    def google_sheets_crm() -> Dict:
        """
        Pattern: Google Sheets CRM Automation
        Source: Automata built-in template

        Manage leads in Google Sheets with automated follow-ups.
        """
        builder = WorkflowBuilder("Google Sheets CRM")

        # Trigger on new row
        builder.add_trigger(
            "n8n-nodes-base.googleSheetsTrigger",
            "New Lead",
            parameters={"sheetName": "Leads", "triggerOn": "rowAdded"},
        )

        # Validate email
        builder.add_node(
            "n8n-nodes-base.function",
            "Validate Email",
            parameters={
                "functionCode": """
const email = $json.email;
const emailRegex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;

if (!emailRegex.test(email)) {
  throw new Error('Invalid email address: ' + email);
}

return [{ json: $json }];
"""
            },
        )

        # Send welcome email
        builder.add_node(
            "n8n-nodes-base.emailSend",
            "Send Welcome",
            type_version=2,
            parameters={
                "fromEmail": "sales@example.com",
                "toEmail": "={{ $json.email }}",
                "subject": "Welcome to our platform!",
                "emailFormat": "text",
                "message": "Hi {{ $json.name }},\\n\\nThank you for your interest!",
                "options": {},
            },
        )

        # Check if sent successfully
        builder.add_node(
            "n8n-nodes-base.if",
            "Email Sent?",
            type_version=2,
            parameters={
                "conditions": {
                    "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
                    "conditions": [
                        {
                            "id": "condition-3",
                            "leftValue": "={{ $json.success }}",
                            "rightValue": True,
                            "operator": {"type": "boolean", "operation": "true"},
                        }
                    ],
                    "combinator": "and",
                }
            },
        )

        # Update status in sheet
        builder.add_node(
            "n8n-nodes-base.googleSheets",
            "Update Status",
            parameters={
                "operation": "update",
                "sheetName": "Leads",
                "range": "Status",
                "valueInputOption": "USER_ENTERED",
                "values": "Contacted",
            },
        )

        # Schedule follow-up (wait 3 days)
        builder.add_node(
            "n8n-nodes-base.wait", "Wait 3 Days", parameters={"amount": 3, "unit": "days"}
        )

        # Send follow-up email
        builder.add_node(
            "n8n-nodes-base.emailSend",
            "Follow-up Email",
            type_version=2,
            parameters={
                "fromEmail": "sales@example.com",
                "toEmail": "={{ $json.email }}",
                "subject": "Quick follow-up",
                "emailFormat": "text",
                "message": "Hi {{ $json.name }},\\n\\nJust checking in!",
                "options": {},
            },
        )

        # Connect workflow
        builder.connect_chain("New Lead", "Validate Email", "Send Welcome", "Email Sent?")
        builder.connect("Email Sent?", "Update Status", source_output=0)  # Success
        builder.connect("Update Status", "Wait 3 Days")
        builder.connect("Wait 3 Days", "Follow-up Email")

        return builder.build()

    @staticmethod
    def webhook_with_response_modes() -> Dict:
        """
        Pattern: Advanced Webhook with Multiple Response Modes
        Source: Issue #10 - Webhook Response Handling

        Demonstrates webhook responseMode options:
        - onReceived: Respond immediately before processing
        - lastNode: Respond with data from last executed node
        - responseNode: Respond with data from specific node

        Also shows responseCode, responseData, and responseHeaders configuration.
        """
        builder = WorkflowBuilder("Advanced Webhook Response")

        # Webhook with lastNode response mode
        builder.add_trigger(
            "webhook",
            "Webhook Advanced",
            parameters={
                "path": "advanced-webhook",
                "httpMethod": "POST",
                "responseMode": "lastNode",  # Wait for workflow to complete
                "responseCode": 200,
                "responseData": "allEntries",  # Return all data
                "options": {
                    "responseHeaders": {
                        "entries": [
                            {"name": "Content-Type", "value": "application/json"},
                            {"name": "X-Custom-Header", "value": "n8n-workflow"}
                        ]
                    }
                }
            }
        )

        # Validate incoming data
        builder.add_node(
            "n8n-nodes-base.if",
            "Validate Input",
            type_version=2,
            parameters={
                "conditions": {
                    "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
                    "conditions": [
                        {
                            "id": "condition-validate-input",
                            "leftValue": "={{ $json.action }}",
                            "rightValue": "",
                            "operator": {"type": "string", "operation": "notEmpty"},
                        }
                    ],
                    "combinator": "and",
                }
            }
        )

        # Process valid data
        builder.add_node(
            "n8n-nodes-base.function",
            "Process Data",
            parameters={
                "functionCode": """
// Process the incoming webhook data
const action = $json.action;
const data = $json.data || {};

return [{
  json: {
    status: 'success',
    action: action,
    processed_at: new Date().toISOString(),
    result: data
  }
}];
"""
            }
        )

        # Handle validation failure
        builder.add_node(
            "n8n-nodes-base.function",
            "Error Response",
            parameters={
                "functionCode": """
// Return error response
return [{
  json: {
    status: 'error',
    message: 'Invalid input: action field is required',
    timestamp: new Date().toISOString()
  }
}];
"""
            }
        )

        # Connect workflow
        builder.connect("Webhook Advanced", "Validate Input")
        builder.connect("Validate Input", "Process Data", source_output=0)  # Valid
        builder.connect("Validate Input", "Error Response", source_output=1)  # Invalid

        return builder.build()

    @staticmethod
    def webhook_with_error_handling() -> Dict:
        """
        Pattern: Webhook with Comprehensive Error Handling
        Source: Issue #11 - Enhanced Error Patterns

        Demonstrates:
        - Input validation
        - Try-catch error handling
        - Error logging
        - Graceful error responses
        """
        builder = WorkflowBuilder("Webhook Error Handling")

        # Webhook trigger
        builder.add_trigger(
            "webhook",
            "Webhook",
            parameters={
                "path": "error-handled",
                "httpMethod": "POST",
                "responseMode": "lastNode"
            }
        )

        # Validate and sanitize input
        builder.add_node(
            "n8n-nodes-base.function",
            "Validate Input",
            parameters={
                "functionCode": """
try {
  // Required fields validation
  const required = ['email', 'name'];
  const missing = required.filter(field => !$json[field]);

  if (missing.length > 0) {
    throw new Error(`Missing required fields: ${missing.join(', ')}`);
  }

  // Email format validation
  const emailRegex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;
  if (!emailRegex.test($json.email)) {
    throw new Error('Invalid email format');
  }

  // Sanitize data
  return [{
    json: {
      email: $json.email.trim().toLowerCase(),
      name: $json.name.trim(),
      data: $json.data || {},
      validated_at: new Date().toISOString()
    }
  }];
} catch (error) {
  return [{
    json: {
      error: true,
      message: error.message,
      original_data: $json
    }
  }];
}
"""
            }
        )

        # Check for validation errors
        builder.add_node(
            "n8n-nodes-base.if",
            "Check Valid",
            type_version=2,
            parameters={
                "conditions": {
                    "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
                    "conditions": [
                        {
                            "id": "condition-check-valid",
                            "leftValue": "={{ $json.error }}",
                            "rightValue": True,
                            "operator": {"type": "boolean", "operation": "notEquals"},
                        }
                    ],
                    "combinator": "and",
                }
            }
        )

        # Process valid data
        builder.add_node(
            "n8n-nodes-base.httpRequest",
            "API Call",
            type_version=4,
            parameters={
                "url": "https://api.example.com/process",
                "method": "POST",
                "options": {
                    "timeout": 10000,
                    "retry": {
                        "enabled": True,
                        "maxRetries": 3,
                        "waitBetween": 1000
                    }
                },
                "sendBody": True,
                "bodyParameters": {
                    "parameters": [
                        {
                            "name": "email",
                            "value": "={{ $json.email }}"
                        },
                        {
                            "name": "name",
                            "value": "={{ $json.name }}"
                        }
                    ]
                }
            }
        )

        # Success response
        builder.add_node(
            "n8n-nodes-base.function",
            "Success Response",
            parameters={
                "functionCode": """
return [{
  json: {
    success: true,
    message: 'Data processed successfully',
    email: $json.email,
    timestamp: new Date().toISOString()
  }
}];
"""
            }
        )

        # Error response
        builder.add_node(
            "n8n-nodes-base.function",
            "Error Response",
            parameters={
                "functionCode": """
return [{
  json: {
    success: false,
    error: $json.message || 'Validation failed',
    timestamp: new Date().toISOString()
  }
}];
"""
            }
        )

        # Log errors (optional - send to monitoring service)
        builder.add_node(
            "n8n-nodes-base.httpRequest",
            "Log Error",
            type_version=4,
            parameters={
                "url": "https://logging.example.com/errors",
                "method": "POST",
                "sendBody": True,
                "ignoreResponseCode": True,
                "options": {"timeout": 5000}
            }
        )

        # Connect workflow
        builder.connect("Webhook", "Validate Input")
        builder.connect("Validate Input", "Check Valid")
        builder.connect("Check Valid", "API Call", source_output=0)  # Valid
        builder.connect("API Call", "Success Response")
        builder.connect("Check Valid", "Error Response", source_output=1)  # Invalid
        builder.connect("Error Response", "Log Error")

        return builder.build()

    @staticmethod
    def circuit_breaker_pattern() -> Dict:
        """
        Pattern: Circuit Breaker for External APIs
        Source: Issue #11 - Error Handling Patterns

        Prevents cascading failures by tracking failure rates
        and temporarily stopping requests to failing services.
        """
        builder = WorkflowBuilder("Circuit Breaker Pattern")

        # Manual trigger for testing
        builder.add_trigger("manual", "Start")

        # Check circuit breaker state
        builder.add_node(
            "n8n-nodes-base.function",
            "Check Circuit",
            parameters={
                "functionCode": """
// Circuit breaker configuration
const maxFailures = 5;
const resetTimeout = 300000; // 5 minutes in ms

// Get circuit state from workflow static data
const context = $node.context;
const failures = context.get('failureCount') || 0;
const lastFailure = context.get('lastFailureTime') || 0;
const circuitOpen = context.get('circuitOpen') || false;
const now = Date.now();

// Check if circuit should be reset
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
      message: 'Service temporarily unavailable (circuit breaker)',
      failures: failures,
      retry_after: Math.ceil((resetTimeout - (now - lastFailure)) / 1000)
    }
  }];
}

// Circuit is closed, allow request
return [{
  json: {
    circuit_open: false,
    failures: failures
  }
}];
"""
            }
        )

        # Check circuit state
        builder.add_node(
            "n8n-nodes-base.if",
            "Is Circuit Open",
            type_version=2,
            parameters={
                "conditions": {
                    "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
                    "conditions": [
                        {
                            "id": "condition-circuit-open",
                            "leftValue": "={{ $json.circuit_open }}",
                            "rightValue": True,
                            "operator": {"type": "boolean", "operation": "equals"},
                        }
                    ],
                    "combinator": "and",
                }
            }
        )

        # Make API call
        builder.add_node(
            "n8n-nodes-base.httpRequest",
            "External API",
            type_version=4,
            parameters={
                "url": "https://api.example.com/data",
                "method": "GET",
                "options": {
                    "timeout": 10000
                }
            }
        )

        # Handle success
        builder.add_node(
            "n8n-nodes-base.function",
            "On Success",
            parameters={
                "functionCode": """
// Reset failure count on success
const context = $node.context;
context.set('failureCount', 0);
context.set('circuitOpen', false);

return [{
  json: {
    success: true,
    data: $json,
    timestamp: new Date().toISOString()
  }
}];
"""
            }
        )

        # Handle failure
        builder.add_node(
            "n8n-nodes-base.function",
            "On Failure",
            parameters={
                "functionCode": """
// Increment failure count
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
    error: 'API request failed',
    failures: failures,
    circuit_open: failures >= maxFailures
  }
}];
"""
            }
        )

        # Circuit open response
        builder.add_node(
            "n8n-nodes-base.noOp",
            "Circuit Open Response"
        )

        # Connect workflow
        builder.connect("Start", "Check Circuit")
        builder.connect("Check Circuit", "Is Circuit Open")
        builder.connect("Is Circuit Open", "External API", source_output=1)  # Circuit closed
        builder.connect("Is Circuit Open", "Circuit Open Response", source_output=0)  # Circuit open
        builder.connect("External API", "On Success")
        # Note: On Failure would be triggered by error handling in n8n

        return builder.build()

    @staticmethod
    def multi_api_aggregation() -> Dict:
        """
        Pattern: Multi-API Aggregation
        Source: Automata built-in template

        Call multiple APIs in parallel, merge results, transform.
        """
        builder = WorkflowBuilder("Multi-API Aggregation")

        # Manual trigger
        builder.add_trigger("manual", "Start")

        # API 1
        builder.add_node(
            "n8n-nodes-base.httpRequest",
            "API 1",
            type_version=4,
            parameters={
                "url": "https://api1.example.com/data",
                "method": "GET",
                "options": {"timeout": 10000},
            },
        )

        # API 2
        builder.add_node(
            "n8n-nodes-base.httpRequest",
            "API 2",
            type_version=4,
            parameters={
                "url": "https://api2.example.com/data",
                "method": "GET",
                "options": {"timeout": 10000},
            },
        )

        # API 3
        builder.add_node(
            "n8n-nodes-base.httpRequest",
            "API 3",
            type_version=4,
            parameters={
                "url": "https://api3.example.com/data",
                "method": "GET",
                "options": {"timeout": 10000},
            },
        )

        # Merge results
        builder.add_node("n8n-nodes-base.merge", "Merge APIs", parameters={"mode": "multiplex"})

        # Transform merged data
        builder.add_node(
            "n8n-nodes-base.function",
            "Transform",
            parameters={
                "functionCode": """
// Aggregate data from all APIs
const aggregated = items.map(item => ({
  json: {
    source: item.json.source || 'unknown',
    data: item.json.data,
    timestamp: new Date().toISOString()
  }
}));

return aggregated;
"""
            },
        )

        # Output
        builder.add_node("n8n-nodes-base.noOp", "Output")

        # Connect workflow (parallel API calls, then merge)
        builder.connect("Start", "API 1")
        builder.connect("Start", "API 2")
        builder.connect("Start", "API 3")
        builder.connect("API 1", "Merge APIs")
        builder.connect("API 2", "Merge APIs")
        builder.connect("API 3", "Merge APIs")
        builder.connect_chain("Merge APIs", "Transform", "Output")

        return builder.build()

    @staticmethod
    def ai_content_processor() -> Dict:
        """
        Pattern: Webhook → AI Processing → Multi-destination Output
        Source: Automata built-in template

        Receive content, process with AI, distribute to multiple channels.
        Showcases AI/ML nodes integration.
        """
        builder = WorkflowBuilder("AI Content Processor")

        # Webhook trigger
        builder.add_trigger(
            "webhook",
            "Content Webhook",
            parameters={
                "path": "process-content",
                "httpMethod": "POST",
                "responseMode": "responseNode",
            },
        )

        # Process with OpenAI
        builder.add_node(
            "n8n-nodes-base.openAi",
            "AI Analysis",
            parameters={
                "resource": "chat",
                "operation": "message",
                "model": "gpt-4o-mini",
                "messages": {
                    "values": [
                        {
                            "content": "Analyze this content and provide: 1) Summary 2) Sentiment 3) Key topics. Content: {{ $json.content }}"
                        }
                    ]
                },
            },
        )

        # Parse AI response
        builder.add_node(
            "n8n-nodes-base.set",
            "Parse Response",
            type_version=3,
            parameters={
                "mode": "manual",
                "duplicateItem": False,
                "assignments": {
                    "assignments": [
                        {"name": "original_content", "value": "={{ $('Content Webhook').item.json.content }}"},
                        {"name": "ai_analysis", "value": "={{ $json.message.content }}"},
                        {"name": "processed_at", "value": "={{ $now.toISO() }}"},
                    ]
                },
            },
        )

        # Send to Slack
        builder.add_node(
            "n8n-nodes-base.slack",
            "Post to Slack",
            type_version=2,
            parameters={
                "resource": "message",
                "operation": "post",
                "channel": "#content-analysis",
                "text": "New content analyzed:\n{{ $json.ai_analysis }}",
            },
        )

        # Respond to webhook
        builder.add_node(
            "n8n-nodes-base.respondToWebhook",
            "Send Response",
            parameters={
                "respondWith": "json",
                "responseBody": '={{ JSON.stringify({ success: true, analysis: $json.ai_analysis }) }}',
            },
        )

        # Connect nodes
        builder.connect("Content Webhook", "AI Analysis")
        builder.connect("AI Analysis", "Parse Response")
        builder.connect("Parse Response", "Post to Slack")
        builder.connect("Post to Slack", "Send Response")

        return builder.build()

    @staticmethod
    def ecommerce_order_processor() -> Dict:
        """
        Pattern: Shopify Trigger → Process → Email + Slack + Database
        Source: Automata built-in template

        Handle new orders from e-commerce, notify team, update database.
        Showcases payment/e-commerce nodes.
        """
        builder = WorkflowBuilder("E-commerce Order Processor")

        # Shopify trigger (manual for now, real would use shopifyTrigger)
        builder.add_trigger(
            "webhook",
            "Order Webhook",
            parameters={
                "path": "shopify-order",
                "httpMethod": "POST",
            },
        )

        # Transform order data
        builder.add_node(
            "n8n-nodes-base.set",
            "Parse Order",
            type_version=3,
            parameters={
                "mode": "manual",
                "assignments": {
                    "assignments": [
                        {"name": "order_id", "value": "={{ $json.id }}"},
                        {"name": "customer_email", "value": "={{ $json.email }}"},
                        {"name": "customer_name", "value": "={{ $json.customer.first_name }} {{ $json.customer.last_name }}"},
                        {"name": "total", "value": "={{ $json.total_price }}"},
                        {"name": "items_count", "value": "={{ $json.line_items.length }}"},
                    ]
                },
            },
        )

        # Send confirmation email
        builder.add_node(
            "n8n-nodes-base.emailSend",
            "Send Confirmation",
            type_version=2,
            parameters={
                "fromEmail": "orders@example.com",
                "toEmail": "={{ $json.customer_email }}",
                "subject": "Order #{{ $json.order_id }} Confirmed!",
                "text": "Thank you {{ $json.customer_name }} for your order of ${{ $json.total }}!",
            },
        )

        # Notify team on Slack
        builder.add_node(
            "n8n-nodes-base.slack",
            "Notify Team",
            type_version=2,
            parameters={
                "resource": "message",
                "operation": "post",
                "channel": "#orders",
                "text": ":package: New order #{{ $json.order_id }} - ${{ $json.total }} ({{ $json.items_count }} items)",
            },
        )

        # Store in database
        builder.add_node(
            "n8n-nodes-base.postgres",
            "Log to DB",
            type_version=2,
            parameters={
                "operation": "insert",
                "table": "orders",
                "columns": "order_id,customer_email,total,items_count,created_at",
            },
        )

        # Connect nodes
        builder.connect("Order Webhook", "Parse Order")
        builder.connect("Parse Order", "Send Confirmation")
        builder.connect("Parse Order", "Notify Team")
        builder.connect("Parse Order", "Log to DB")

        return builder.build()

    @staticmethod
    def github_jira_sync() -> Dict:
        """
        Pattern: GitHub Issue → Transform → Jira Ticket
        Source: Automata built-in template

        Sync GitHub issues to Jira for project management.
        Showcases project management nodes.
        """
        builder = WorkflowBuilder("GitHub to Jira Sync")

        # GitHub webhook trigger
        builder.add_trigger(
            "webhook",
            "GitHub Webhook",
            parameters={
                "path": "github-issues",
                "httpMethod": "POST",
            },
        )

        # Filter for new issues only
        builder.add_node(
            "n8n-nodes-base.if",
            "Is New Issue",
            type_version=2,
            parameters={
                "conditions": {
                    "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
                    "conditions": [
                        {
                            "id": "check-action",
                            "leftValue": "={{ $json.action }}",
                            "rightValue": "opened",
                            "operator": {"type": "string", "operation": "equals"},
                        }
                    ],
                    "combinator": "and",
                },
            },
        )

        # Transform to Jira format
        builder.add_node(
            "n8n-nodes-base.set",
            "Map to Jira",
            type_version=3,
            parameters={
                "mode": "manual",
                "assignments": {
                    "assignments": [
                        {"name": "summary", "value": "[GitHub] {{ $json.issue.title }}"},
                        {"name": "description", "value": "{{ $json.issue.body }}\n\n---\nGitHub: {{ $json.issue.html_url }}"},
                        {"name": "labels", "value": "={{ $json.issue.labels.map(l => l.name) }}"},
                        {"name": "github_id", "value": "={{ $json.issue.number }}"},
                    ]
                },
            },
        )

        # Create Jira ticket
        builder.add_node(
            "n8n-nodes-base.jira",
            "Create Jira Issue",
            parameters={
                "resource": "issue",
                "operation": "create",
                "project": "PROJ",
                "issueType": "Task",
                "summary": "={{ $json.summary }}",
                "description": "={{ $json.description }}",
            },
        )

        # Connect nodes
        builder.connect("GitHub Webhook", "Is New Issue")
        builder.connect("Is New Issue", "Map to Jira", "true")
        builder.connect("Map to Jira", "Create Jira Issue")

        return builder.build()

    @staticmethod
    def cloud_file_processor() -> Dict:
        """
        Pattern: Google Drive Trigger → Process → Multi-cloud Backup
        Source: Automata built-in template

        Process files from Google Drive, backup to S3 and Dropbox.
        Showcases cloud storage nodes.
        """
        builder = WorkflowBuilder("Cloud File Processor")

        # Manual trigger (real would use googleDriveTrigger)
        builder.add_trigger(
            "manual",
            "Start",
        )

        # Get files from Google Drive
        builder.add_node(
            "n8n-nodes-base.googleDrive",
            "Get Drive Files",
            type_version=3,
            parameters={
                "operation": "list",
                "folderId": "root",
                "filter": {"mimeType": "application/pdf"},
            },
        )

        # Split for batch processing
        builder.add_node(
            "n8n-nodes-base.splitInBatches",
            "Split Batches",
            type_version=3,
            parameters={"batchSize": 5},
        )

        # Download file
        builder.add_node(
            "n8n-nodes-base.googleDrive",
            "Download File",
            type_version=3,
            parameters={
                "operation": "download",
                "fileId": "={{ $json.id }}",
            },
        )

        # Upload to S3
        builder.add_node(
            "n8n-nodes-base.awsS3",
            "Upload to S3",
            parameters={
                "operation": "upload",
                "bucketName": "backup-bucket",
                "fileName": "={{ $json.name }}",
            },
        )

        # Upload to Dropbox
        builder.add_node(
            "n8n-nodes-base.dropbox",
            "Upload to Dropbox",
            type_version=2,
            parameters={
                "operation": "upload",
                "path": "/backups/{{ $json.name }}",
            },
        )

        # Connect nodes
        builder.connect("Start", "Get Drive Files")
        builder.connect("Get Drive Files", "Split Batches")
        builder.connect("Split Batches", "Download File")
        builder.connect("Download File", "Upload to S3")
        builder.connect("Download File", "Upload to Dropbox")

        return builder.build()


# Integration function
def get_template_by_name(template_name: str, kb: Optional[KnowledgeBase] = None) -> Dict:
    """
    Get workflow template by name.

    Supports both original and community templates.
    """
    community_templates = {
        "webhook_db_slack": CommunityTemplateLibrary.webhook_database_slack,
        "scheduled_sync_retry": CommunityTemplateLibrary.scheduled_sync_with_retry,
        "rss_social": CommunityTemplateLibrary.rss_to_social,
        "sheets_crm": CommunityTemplateLibrary.google_sheets_crm,
        "multi_api": CommunityTemplateLibrary.multi_api_aggregation,
        # Issue #10 - Webhook Response Handling
        "webhook_advanced": CommunityTemplateLibrary.webhook_with_response_modes,
        # Issue #11 - Enhanced Error Handling
        "webhook_error_handling": CommunityTemplateLibrary.webhook_with_error_handling,
        "circuit_breaker": CommunityTemplateLibrary.circuit_breaker_pattern,
        # Phase 3 - New templates
        "ai_content": CommunityTemplateLibrary.ai_content_processor,
        "ecommerce_orders": CommunityTemplateLibrary.ecommerce_order_processor,
        "github_jira": CommunityTemplateLibrary.github_jira_sync,
        "cloud_backup": CommunityTemplateLibrary.cloud_file_processor,
    }

    # Try community templates first
    if template_name in community_templates:
        return community_templates[template_name]()

    # Fall back to original templates
    from skills.generate_workflow_json import generate_from_template

    try:
        return generate_from_template(template_name)
    except ValueError:
        raise ValueError(f"Unknown template: {template_name}")


if __name__ == "__main__":
    # Test templates
    print("Enhanced Template Library - Cycle 02")
    print("=" * 60)

    templates = [
        "webhook_db_slack",
        "scheduled_sync_retry",
        "rss_social",
        "sheets_crm",
        "multi_api",
    ]

    for template_name in templates:
        workflow = get_template_by_name(template_name)
        print(f"✓ {workflow['name']}: {len(workflow['nodes'])} nodes")
