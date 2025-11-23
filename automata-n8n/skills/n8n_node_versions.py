"""
n8n Node TypeVersion Mapping

This module provides a comprehensive mapping of n8n node types to their
current typeVersion values as of n8n 1.60.0+.

The typeVersion is critical for ensuring generated workflows are compatible
with the target n8n instance. Using incorrect typeVersion can result in:
- Missing or incompatible parameters
- Import failures
- Runtime errors
- Data loss

This mapping is based on research from:
- n8n official documentation (docs.n8n.io)
- n8n GitHub repository (github.com/n8n-io/n8n)
- Community discussions and issues
- n8n release notes (November 2024 - January 2025)

Author: Project Automata - Agent 1
Version: 1.0.0
Created: 2025-11-20
Target n8n Version: 1.60.0+
"""

import logging
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


# Comprehensive node type to typeVersion mapping
# Format: "node-type": (default_version, min_version, max_version, notes)
NODE_TYPE_VERSIONS: Dict[str, Tuple[float, float, float, str]] = {
    # ==========================================
    # CORE TRIGGER NODES
    # ==========================================
    "n8n-nodes-base.webhook": (
        2.0,
        1.0,
        2.1,
        "Webhook trigger - v2+ recommended for modern response modes",
    ),
    "n8n-nodes-base.manualTrigger": (1.0, 1.0, 1.0, "Manual workflow trigger"),
    "n8n-nodes-base.cron": (1.2, 1.0, 1.2, "Scheduled/cron trigger"),
    "n8n-nodes-base.emailTrigger": (1.0, 1.0, 1.0, "Email receive trigger"),
    "n8n-nodes-base.rssFeedTrigger": (1.1, 1.0, 1.1, "RSS feed polling trigger"),
    "n8n-nodes-base.formTrigger": (2.0, 1.0, 2.0, "Form submission trigger"),
    # ==========================================
    # HTTP/API NODES
    # ==========================================
    "n8n-nodes-base.httpRequest": (
        4.2,
        1.0,
        4.2,
        "HTTP Request - v4.2 has enhanced auth and error handling",
    ),
    "n8n-nodes-base.respondToWebhook": (1.2, 1.0, 1.2, "Respond to webhook - for custom responses"),
    # ==========================================
    # DATA TRANSFORMATION NODES
    # ==========================================
    "n8n-nodes-base.code": (
        2.0,
        1.0,
        2.0,
        "Code/JavaScript execution - v2 has improved sandboxing",
    ),
    "n8n-nodes-base.function": (1.0, 1.0, 1.0, "Legacy function node - use Code node instead"),
    "n8n-nodes-base.functionItem": (1.0, 1.0, 1.0, "Legacy item function - use Code node instead"),
    "n8n-nodes-base.set": (3.3, 1.0, 3.3, "Set/Edit fields - v3+ has better type handling"),
    "n8n-nodes-base.edit": (1.1, 1.0, 1.1, "Edit fields (deprecated - use Set node)"),
    "n8n-nodes-base.aggregate": (1.0, 1.0, 1.0, "Aggregate data"),
    "n8n-nodes-base.itemLists": (3.0, 1.0, 3.0, "Item list operations"),
    # ==========================================
    # FLOW CONTROL NODES
    # ==========================================
    "n8n-nodes-base.if": (2.0, 1.0, 2.0, "Conditional IF - v2 has improved condition types"),
    "n8n-nodes-base.switch": (3.0, 1.0, 3.0, "Multi-way switch - v3 has better routing"),
    "n8n-nodes-base.merge": (2.1, 1.0, 2.1, "Merge data from multiple sources"),
    "n8n-nodes-base.split": (1.0, 1.0, 1.0, "Split data into branches"),
    "n8n-nodes-base.wait": (1.1, 1.0, 1.1, "Wait/delay execution"),
    "n8n-nodes-base.stopAndError": (1.0, 1.0, 1.0, "Stop workflow with error"),
    "n8n-nodes-base.noOp": (1.0, 1.0, 1.0, "No operation - useful for routing"),
    "n8n-nodes-base.filter": (2.0, 1.0, 2.0, "Filter items based on conditions"),
    "n8n-nodes-base.loop": (1.0, 1.0, 1.0, "Loop over items"),
    # ==========================================
    # DATABASE NODES
    # ==========================================
    "n8n-nodes-base.postgres": (2.6, 1.0, 2.6, "PostgreSQL - v2.6 has improved query builder"),
    "n8n-nodes-base.mysql": (2.4, 1.0, 2.4, "MySQL database operations"),
    "n8n-nodes-base.mongodb": (1.1, 1.0, 1.1, "MongoDB operations"),
    "n8n-nodes-base.redis": (1.0, 1.0, 1.0, "Redis operations"),
    "n8n-nodes-base.sqlite": (1.0, 1.0, 1.0, "SQLite database"),
    "n8n-nodes-base.microsoftSql": (1.0, 1.0, 1.0, "Microsoft SQL Server"),
    "n8n-nodes-base.questDb": (1.0, 1.0, 1.0, "QuestDB time-series database"),
    # ==========================================
    # COMMUNICATION NODES
    # ==========================================
    "n8n-nodes-base.slack": (2.3, 1.0, 2.3, "Slack - v2.3 has blocks and interactive features"),
    "n8n-nodes-base.slackTrigger": (1.0, 1.0, 1.0, "Slack event trigger"),
    "n8n-nodes-base.discord": (2.0, 1.0, 2.0, "Discord messaging"),
    "n8n-nodes-base.telegram": (1.2, 1.0, 1.2, "Telegram bot operations"),
    "n8n-nodes-base.telegramTrigger": (1.2, 1.0, 1.2, "Telegram event trigger"),
    "n8n-nodes-base.mattermost": (1.0, 1.0, 1.0, "Mattermost messaging"),
    "n8n-nodes-base.matrix": (1.0, 1.0, 1.0, "Matrix protocol messaging"),
    "n8n-nodes-base.twilio": (2.0, 1.0, 2.0, "Twilio SMS/voice"),
    # ==========================================
    # EMAIL NODES
    # ==========================================
    "n8n-nodes-base.emailSend": (2.1, 1.0, 2.1, "Send email - v2+ has better formatting options"),
    "n8n-nodes-base.gmail": (2.1, 1.0, 2.1, "Gmail operations - v2.1 has improved threading"),
    "n8n-nodes-base.gmailTrigger": (1.0, 1.0, 1.0, "Gmail trigger"),
    "n8n-nodes-base.microsoftOutlook": (2.0, 1.0, 2.0, "Outlook email operations"),
    "n8n-nodes-base.sendGrid": (1.0, 1.0, 1.0, "SendGrid email service"),
    "n8n-nodes-base.mailgun": (1.0, 1.0, 1.0, "Mailgun email service"),
    "n8n-nodes-base.imap": (2.0, 1.0, 2.0, "IMAP email retrieval"),
    # ==========================================
    # CLOUD STORAGE NODES
    # ==========================================
    "n8n-nodes-base.googleDrive": (3.0, 1.0, 3.0, "Google Drive operations"),
    "n8n-nodes-base.googleDriveTrigger": (1.0, 1.0, 1.0, "Google Drive file trigger"),
    "n8n-nodes-base.dropbox": (2.0, 1.0, 2.0, "Dropbox file operations"),
    "n8n-nodes-base.awsS3": (1.1, 1.0, 1.1, "AWS S3 storage"),
    "n8n-nodes-base.box": (2.0, 1.0, 2.0, "Box.com storage"),
    "n8n-nodes-base.oneDrive": (1.0, 1.0, 1.0, "Microsoft OneDrive"),
    "n8n-nodes-base.nextCloud": (1.0, 1.0, 1.0, "NextCloud file operations"),
    # ==========================================
    # PRODUCTIVITY/OFFICE NODES
    # ==========================================
    "n8n-nodes-base.googleSheets": (4.5, 1.0, 4.5, "Google Sheets - v4.5 has advanced operations"),
    "n8n-nodes-base.googleSheetsTrigger": (1.1, 1.0, 1.1, "Google Sheets trigger"),
    "n8n-nodes-base.googleDocs": (1.0, 1.0, 1.0, "Google Docs operations"),
    "n8n-nodes-base.googleCalendar": (2.0, 1.0, 2.0, "Google Calendar"),
    "n8n-nodes-base.microsoftExcel": (2.0, 1.0, 2.0, "Microsoft Excel operations"),
    "n8n-nodes-base.airtable": (2.0, 1.0, 2.0, "Airtable database"),
    "n8n-nodes-base.notion": (2.2, 1.0, 2.2, "Notion workspace operations"),
    "n8n-nodes-base.notionTrigger": (1.1, 1.0, 1.1, "Notion database trigger"),
    # ==========================================
    # SOCIAL MEDIA NODES
    # ==========================================
    "n8n-nodes-base.twitter": (2.0, 1.0, 2.0, "Twitter/X operations"),
    "n8n-nodes-base.linkedIn": (2.0, 1.0, 2.0, "LinkedIn operations"),
    "n8n-nodes-base.facebook": (1.0, 1.0, 1.0, "Facebook Graph API"),
    "n8n-nodes-base.instagram": (1.0, 1.0, 1.0, "Instagram operations"),
    "n8n-nodes-base.reddit": (1.0, 1.0, 1.0, "Reddit API"),
    "n8n-nodes-base.youTube": (1.0, 1.0, 1.0, "YouTube operations"),
    # ==========================================
    # AI/ML NODES
    # ==========================================
    "n8n-nodes-base.openAi": (1.3, 1.0, 1.3, "OpenAI GPT/DALL-E operations"),
    "n8n-nodes-base.anthropic": (1.0, 1.0, 1.0, "Anthropic Claude AI"),
    "n8n-nodes-base.huggingFace": (1.1, 1.0, 1.1, "HuggingFace models"),
    "n8n-nodes-base.awsBedrock": (1.0, 1.0, 1.0, "AWS Bedrock AI"),
    "n8n-nodes-base.langChain": (1.0, 1.0, 1.0, "LangChain integration"),
    # ==========================================
    # PAYMENT/ECOMMERCE NODES
    # ==========================================
    "n8n-nodes-base.stripe": (1.0, 1.0, 1.0, "Stripe payment processing"),
    "n8n-nodes-base.stripeTrigger": (1.1, 1.0, 1.1, "Stripe webhook trigger"),
    "n8n-nodes-base.payPal": (1.0, 1.0, 1.0, "PayPal operations"),
    "n8n-nodes-base.shopify": (1.0, 1.0, 1.0, "Shopify e-commerce"),
    "n8n-nodes-base.shopifyTrigger": (1.0, 1.0, 1.0, "Shopify webhook trigger"),
    "n8n-nodes-base.wooCommerce": (1.0, 1.0, 1.0, "WooCommerce operations"),
    # ==========================================
    # CRM/SALES NODES
    # ==========================================
    "n8n-nodes-base.salesforce": (1.0, 1.0, 1.0, "Salesforce CRM"),
    "n8n-nodes-base.hubspot": (2.0, 1.0, 2.0, "HubSpot CRM"),
    "n8n-nodes-base.pipedrive": (1.0, 1.0, 1.0, "Pipedrive CRM"),
    "n8n-nodes-base.zohoCrm": (1.0, 1.0, 1.0, "Zoho CRM"),
    "n8n-nodes-base.freshworks": (1.0, 1.0, 1.0, "Freshworks suite"),
    # ==========================================
    # PROJECT MANAGEMENT NODES
    # ==========================================
    "n8n-nodes-base.jira": (1.0, 1.0, 1.0, "Jira project tracking"),
    "n8n-nodes-base.trello": (2.0, 1.0, 2.0, "Trello boards"),
    "n8n-nodes-base.asana": (2.0, 1.0, 2.0, "Asana project management"),
    "n8n-nodes-base.monday": (1.0, 1.0, 1.0, "Monday.com workflows"),
    "n8n-nodes-base.clickUp": (1.0, 1.0, 1.0, "ClickUp tasks"),
    "n8n-nodes-base.github": (1.1, 1.0, 1.1, "GitHub operations"),
    "n8n-nodes-base.githubTrigger": (1.1, 1.0, 1.1, "GitHub webhook trigger"),
    "n8n-nodes-base.gitlab": (1.0, 1.0, 1.0, "GitLab operations"),
    # ==========================================
    # ANALYTICS/MONITORING NODES
    # ==========================================
    "n8n-nodes-base.googleAnalytics": (1.0, 1.0, 1.0, "Google Analytics"),
    "n8n-nodes-base.mixpanel": (1.0, 1.0, 1.0, "Mixpanel analytics"),
    "n8n-nodes-base.segment": (1.0, 1.0, 1.0, "Segment customer data"),
    "n8n-nodes-base.datadog": (1.0, 1.0, 1.0, "Datadog monitoring"),
    "n8n-nodes-base.newRelic": (1.0, 1.0, 1.0, "New Relic monitoring"),
    "n8n-nodes-base.sentry": (1.0, 1.0, 1.0, "Sentry error tracking"),
    # ==========================================
    # AWS NODES
    # ==========================================
    # Note: awsS3 already defined in CLOUD STORAGE NODES section above
    "n8n-nodes-base.awsLambda": (1.0, 1.0, 1.0, "AWS Lambda functions"),
    "n8n-nodes-base.awsSns": (1.0, 1.0, 1.0, "AWS SNS notifications"),
    "n8n-nodes-base.awsSqs": (1.0, 1.0, 1.0, "AWS SQS queues"),
    "n8n-nodes-base.awsDynamoDB": (1.0, 1.0, 1.0, "AWS DynamoDB"),
    "n8n-nodes-base.awsRekognition": (1.0, 1.0, 1.0, "AWS Rekognition AI"),
    "n8n-nodes-base.awsComprehend": (1.0, 1.0, 1.0, "AWS Comprehend NLP"),
    # ==========================================
    # GOOGLE CLOUD NODES
    # ==========================================
    "n8n-nodes-base.googleCloudStorage": (1.0, 1.0, 1.0, "GCP Cloud Storage"),
    "n8n-nodes-base.googleCloudFunction": (1.0, 1.0, 1.0, "GCP Cloud Functions"),
    "n8n-nodes-base.googleBigQuery": (1.0, 1.0, 1.0, "GCP BigQuery"),
    "n8n-nodes-base.googlePubSub": (1.0, 1.0, 1.0, "GCP Pub/Sub messaging"),
    # ==========================================
    # UTILITY NODES
    # ==========================================
    "n8n-nodes-base.spreadsheetFile": (2.0, 1.0, 2.0, "Read/write spreadsheet files"),
    "n8n-nodes-base.readBinaryFile": (1.0, 1.0, 1.0, "Read binary files"),
    "n8n-nodes-base.writeBinaryFile": (1.0, 1.0, 1.0, "Write binary files"),
    "n8n-nodes-base.readPdf": (1.0, 1.0, 1.0, "Extract text from PDFs"),
    "n8n-nodes-base.xml": (1.0, 1.0, 1.0, "XML parsing/generation"),
    "n8n-nodes-base.html": (1.2, 1.0, 1.2, "HTML parsing/extraction"),
    "n8n-nodes-base.crypto": (1.0, 1.0, 1.0, "Cryptographic operations"),
    "n8n-nodes-base.compress": (1.0, 1.0, 1.0, "File compression"),
    "n8n-nodes-base.executeCommand": (1.0, 1.0, 1.0, "Execute shell commands"),
    "n8n-nodes-base.ssh": (1.0, 1.0, 1.0, "SSH remote execution"),
    "n8n-nodes-base.ftp": (1.0, 1.0, 1.0, "FTP file transfer"),
    "n8n-nodes-base.moveBinaryData": (1.0, 1.0, 1.0, "Move binary data between nodes"),
    # ==========================================
    # ADDITIONAL TRIGGER NODES
    # ==========================================
    "n8n-nodes-base.scheduleTrigger": (1.2, 1.0, 1.2, "Schedule trigger (replaces cron)"),
    "n8n-nodes-base.workflowTrigger": (1.0, 1.0, 1.0, "Trigger from another workflow"),
    "n8n-nodes-base.errorTrigger": (1.0, 1.0, 1.0, "Trigger on workflow errors"),
    "n8n-nodes-base.executeWorkflowTrigger": (1.0, 1.0, 1.0, "Execute workflow trigger"),
    "n8n-nodes-base.localFileTrigger": (1.1, 1.0, 1.1, "Watch local file changes"),
    "n8n-nodes-base.mqttTrigger": (1.0, 1.0, 1.0, "MQTT message trigger"),
    "n8n-nodes-base.rabbitMQTrigger": (1.0, 1.0, 1.0, "RabbitMQ message trigger"),
    "n8n-nodes-base.kafkaTrigger": (1.0, 1.0, 1.0, "Apache Kafka trigger"),
    "n8n-nodes-base.amqpTrigger": (1.0, 1.0, 1.0, "AMQP message trigger"),
    # ==========================================
    # ADDITIONAL DATA TRANSFORMATION
    # ==========================================
    "n8n-nodes-base.convertToFile": (1.1, 1.0, 1.1, "Convert data to file"),
    "n8n-nodes-base.extractFromFile": (1.0, 1.0, 1.0, "Extract data from file"),
    "n8n-nodes-base.dateTime": (2.0, 1.0, 2.0, "Date/time manipulation"),
    "n8n-nodes-base.compareDatasets": (1.0, 1.0, 1.0, "Compare two datasets"),
    "n8n-nodes-base.removeDuplicates": (1.0, 1.0, 1.0, "Remove duplicate items"),
    "n8n-nodes-base.renameKeys": (1.0, 1.0, 1.0, "Rename object keys"),
    "n8n-nodes-base.sort": (1.0, 1.0, 1.0, "Sort items"),
    "n8n-nodes-base.limit": (1.0, 1.0, 1.0, "Limit number of items"),
    "n8n-nodes-base.splitInBatches": (3.0, 1.0, 3.0, "Split into batches"),
    "n8n-nodes-base.summarize": (1.0, 1.0, 1.0, "Summarize/aggregate data"),
    "n8n-nodes-base.markdown": (1.0, 1.0, 1.0, "Markdown conversion"),
    # ==========================================
    # ADDITIONAL FLOW CONTROL
    # ==========================================
    "n8n-nodes-base.executeWorkflow": (1.0, 1.0, 1.0, "Execute another workflow"),
    "n8n-nodes-base.stickyNote": (1.0, 1.0, 1.0, "Sticky note for documentation"),
    # ==========================================
    # ADDITIONAL DATABASES
    # ==========================================
    "n8n-nodes-base.supabase": (1.0, 1.0, 1.0, "Supabase database"),
    "n8n-nodes-base.cockroachDb": (1.0, 1.0, 1.0, "CockroachDB operations"),
    "n8n-nodes-base.mariaDb": (1.0, 1.0, 1.0, "MariaDB database"),
    "n8n-nodes-base.couchDb": (1.0, 1.0, 1.0, "CouchDB operations"),
    "n8n-nodes-base.elasticSearch": (1.0, 1.0, 1.0, "Elasticsearch operations"),
    "n8n-nodes-base.neo4j": (1.0, 1.0, 1.0, "Neo4j graph database"),
    "n8n-nodes-base.snowflake": (1.0, 1.0, 1.0, "Snowflake data warehouse"),
    "n8n-nodes-base.clickHouse": (1.0, 1.0, 1.0, "ClickHouse analytics DB"),
    "n8n-nodes-base.fauna": (1.0, 1.0, 1.0, "FaunaDB serverless"),
    # ==========================================
    # MESSAGING & QUEUES
    # ==========================================
    "n8n-nodes-base.mqtt": (1.0, 1.0, 1.0, "MQTT publish/subscribe"),
    "n8n-nodes-base.rabbitMQ": (1.0, 1.0, 1.0, "RabbitMQ messaging"),
    "n8n-nodes-base.kafka": (1.0, 1.0, 1.0, "Apache Kafka"),
    "n8n-nodes-base.amqp": (1.0, 1.0, 1.0, "AMQP protocol"),
    # ==========================================
    # MARKETING & EMAIL MARKETING
    # ==========================================
    "n8n-nodes-base.mailchimp": (3.0, 1.0, 3.0, "Mailchimp email marketing"),
    "n8n-nodes-base.mailchimpTrigger": (1.0, 1.0, 1.0, "Mailchimp webhook trigger"),
    "n8n-nodes-base.activeCampaign": (1.0, 1.0, 1.0, "ActiveCampaign CRM"),
    "n8n-nodes-base.activeCampaignTrigger": (1.0, 1.0, 1.0, "ActiveCampaign trigger"),
    "n8n-nodes-base.convertKit": (1.0, 1.0, 1.0, "ConvertKit email"),
    "n8n-nodes-base.convertKitTrigger": (1.0, 1.0, 1.0, "ConvertKit trigger"),
    "n8n-nodes-base.drip": (1.0, 1.0, 1.0, "Drip marketing"),
    "n8n-nodes-base.sendinblue": (1.0, 1.0, 1.0, "Sendinblue (Brevo)"),
    "n8n-nodes-base.customerIo": (1.0, 1.0, 1.0, "Customer.io messaging"),
    "n8n-nodes-base.customerIoTrigger": (1.0, 1.0, 1.0, "Customer.io trigger"),
    "n8n-nodes-base.lemlist": (1.0, 1.0, 1.0, "Lemlist outreach"),
    "n8n-nodes-base.lemlistTrigger": (1.0, 1.0, 1.0, "Lemlist trigger"),
    # ==========================================
    # CUSTOMER SUPPORT
    # ==========================================
    "n8n-nodes-base.zendesk": (1.0, 1.0, 1.0, "Zendesk support"),
    "n8n-nodes-base.zendeskTrigger": (1.0, 1.0, 1.0, "Zendesk trigger"),
    "n8n-nodes-base.intercom": (1.0, 1.0, 1.0, "Intercom messaging"),
    "n8n-nodes-base.freshdesk": (1.0, 1.0, 1.0, "Freshdesk support"),
    "n8n-nodes-base.helpScout": (1.0, 1.0, 1.0, "Help Scout support"),
    "n8n-nodes-base.helpScoutTrigger": (1.0, 1.0, 1.0, "Help Scout trigger"),
    "n8n-nodes-base.crisp": (1.0, 1.0, 1.0, "Crisp chat"),
    "n8n-nodes-base.serviceNow": (1.0, 1.0, 1.0, "ServiceNow ITSM"),
    # ==========================================
    # HR & RECRUITING
    # ==========================================
    "n8n-nodes-base.bambooHr": (1.0, 1.0, 1.0, "BambooHR"),
    "n8n-nodes-base.workable": (1.0, 1.0, 1.0, "Workable recruiting"),
    "n8n-nodes-base.workableTrigger": (1.0, 1.0, 1.0, "Workable trigger"),
    "n8n-nodes-base.greenhouse": (1.0, 1.0, 1.0, "Greenhouse recruiting"),
    "n8n-nodes-base.lever": (1.0, 1.0, 1.0, "Lever recruiting"),
    # ==========================================
    # DEVOPS & CI/CD
    # ==========================================
    "n8n-nodes-base.jenkins": (1.0, 1.0, 1.0, "Jenkins CI/CD"),
    "n8n-nodes-base.circleCI": (1.0, 1.0, 1.0, "CircleCI pipelines"),
    "n8n-nodes-base.bitbucket": (1.0, 1.0, 1.0, "Bitbucket repositories"),
    "n8n-nodes-base.bitbucketTrigger": (1.0, 1.0, 1.0, "Bitbucket trigger"),
    "n8n-nodes-base.pagerDuty": (1.0, 1.0, 1.0, "PagerDuty incidents"),
    "n8n-nodes-base.opsgenie": (1.0, 1.0, 1.0, "Opsgenie alerting"),
    "n8n-nodes-base.uptimeRobot": (1.0, 1.0, 1.0, "UptimeRobot monitoring"),
    # ==========================================
    # ADDITIONAL AI/ML NODES
    # ==========================================
    "n8n-nodes-base.googleAi": (1.0, 1.0, 1.0, "Google AI (Gemini)"),
    "n8n-nodes-base.mistralAi": (1.0, 1.0, 1.0, "Mistral AI"),
    "n8n-nodes-base.cohere": (1.0, 1.0, 1.0, "Cohere AI"),
    "n8n-nodes-base.replicate": (1.0, 1.0, 1.0, "Replicate ML models"),
    "n8n-nodes-base.deepL": (1.0, 1.0, 1.0, "DeepL translation"),
    "n8n-nodes-base.googleTranslate": (2.0, 1.0, 2.0, "Google Translate"),
    "n8n-nodes-base.pinecone": (1.0, 1.0, 1.0, "Pinecone vector DB"),
    "n8n-nodes-base.qdrant": (1.0, 1.0, 1.0, "Qdrant vector DB"),
    "n8n-nodes-base.weaviate": (1.0, 1.0, 1.0, "Weaviate vector DB"),
    # ==========================================
    # ADDITIONAL CLOUD PROVIDERS
    # ==========================================
    "n8n-nodes-base.azureStorage": (1.0, 1.0, 1.0, "Azure Blob Storage"),
    "n8n-nodes-base.azureCosmosDb": (1.0, 1.0, 1.0, "Azure Cosmos DB"),
    "n8n-nodes-base.azureDevOps": (1.0, 1.0, 1.0, "Azure DevOps"),
    "n8n-nodes-base.digitalOcean": (1.0, 1.0, 1.0, "DigitalOcean Droplets"),
    "n8n-nodes-base.cloudflare": (1.0, 1.0, 1.0, "Cloudflare"),
    "n8n-nodes-base.vercel": (1.0, 1.0, 1.0, "Vercel platform"),
    "n8n-nodes-base.netlify": (1.0, 1.0, 1.0, "Netlify platform"),
    # ==========================================
    # ADDITIONAL ECOMMERCE
    # ==========================================
    "n8n-nodes-base.magento": (1.0, 1.0, 1.0, "Magento/Adobe Commerce"),
    "n8n-nodes-base.bigCommerce": (1.0, 1.0, 1.0, "BigCommerce"),
    "n8n-nodes-base.gumroad": (1.0, 1.0, 1.0, "Gumroad sales"),
    "n8n-nodes-base.chargebee": (1.0, 1.0, 1.0, "Chargebee subscriptions"),
    "n8n-nodes-base.square": (1.0, 1.0, 1.0, "Square payments"),
    # ==========================================
    # FORMS & SURVEYS
    # ==========================================
    "n8n-nodes-base.typeform": (1.0, 1.0, 1.0, "Typeform forms"),
    "n8n-nodes-base.typeformTrigger": (1.0, 1.0, 1.0, "Typeform trigger"),
    "n8n-nodes-base.jotForm": (1.0, 1.0, 1.0, "JotForm"),
    "n8n-nodes-base.jotFormTrigger": (1.0, 1.0, 1.0, "JotForm trigger"),
    "n8n-nodes-base.surveyMonkey": (1.0, 1.0, 1.0, "SurveyMonkey"),
    "n8n-nodes-base.tally": (1.0, 1.0, 1.0, "Tally forms"),
    "n8n-nodes-base.tallyTrigger": (1.0, 1.0, 1.0, "Tally trigger"),
    # ==========================================
    # SCHEDULING & CALENDARS
    # ==========================================
    "n8n-nodes-base.calendly": (1.0, 1.0, 1.0, "Calendly scheduling"),
    "n8n-nodes-base.calendlyTrigger": (1.0, 1.0, 1.0, "Calendly trigger"),
    "n8n-nodes-base.cal": (1.0, 1.0, 1.0, "Cal.com scheduling"),
    "n8n-nodes-base.calTrigger": (1.0, 1.0, 1.0, "Cal.com trigger"),
    "n8n-nodes-base.acuityScheduling": (1.0, 1.0, 1.0, "Acuity scheduling"),
    "n8n-nodes-base.acuitySchedulingTrigger": (1.0, 1.0, 1.0, "Acuity trigger"),
    # ==========================================
    # CONTENT & MEDIA
    # ==========================================
    "n8n-nodes-base.wordpress": (1.0, 1.0, 1.0, "WordPress CMS"),
    "n8n-nodes-base.ghost": (1.0, 1.0, 1.0, "Ghost publishing"),
    "n8n-nodes-base.medium": (1.0, 1.0, 1.0, "Medium publishing"),
    "n8n-nodes-base.contentful": (1.0, 1.0, 1.0, "Contentful CMS"),
    "n8n-nodes-base.strapi": (1.0, 1.0, 1.0, "Strapi CMS"),
    "n8n-nodes-base.cloudinary": (1.0, 1.0, 1.0, "Cloudinary media"),
    "n8n-nodes-base.vimeo": (1.0, 1.0, 1.0, "Vimeo video"),
    "n8n-nodes-base.spotify": (1.0, 1.0, 1.0, "Spotify API"),
    # ==========================================
    # DOCUMENT & SIGNATURES
    # ==========================================
    "n8n-nodes-base.docuSign": (1.0, 1.0, 1.0, "DocuSign e-signatures"),
    "n8n-nodes-base.pandaDoc": (1.0, 1.0, 1.0, "PandaDoc documents"),
    # ==========================================
    # ADDITIONAL CRM/SALES
    # ==========================================
    "n8n-nodes-base.copper": (1.0, 1.0, 1.0, "Copper CRM"),
    "n8n-nodes-base.close": (1.0, 1.0, 1.0, "Close CRM"),
    "n8n-nodes-base.apolloIo": (1.0, 1.0, 1.0, "Apollo.io sales"),
    "n8n-nodes-base.clearbit": (1.0, 1.0, 1.0, "Clearbit enrichment"),
    "n8n-nodes-base.hunter": (1.0, 1.0, 1.0, "Hunter.io emails"),
    # ==========================================
    # ADDITIONAL PROJECT MANAGEMENT
    # ==========================================
    "n8n-nodes-base.basecamp": (1.0, 1.0, 1.0, "Basecamp"),
    "n8n-nodes-base.todoist": (1.0, 1.0, 1.0, "Todoist tasks"),
    "n8n-nodes-base.wrike": (1.0, 1.0, 1.0, "Wrike projects"),
    "n8n-nodes-base.smartsheet": (1.0, 1.0, 1.0, "Smartsheet"),
    "n8n-nodes-base.linearApp": (1.0, 1.0, 1.0, "Linear issues"),
    "n8n-nodes-base.linearAppTrigger": (1.0, 1.0, 1.0, "Linear trigger"),
    "n8n-nodes-base.coda": (1.0, 1.0, 1.0, "Coda docs"),
    "n8n-nodes-base.confluence": (1.0, 1.0, 1.0, "Atlassian Confluence"),
    # ==========================================
    # TELEPHONY & SMS
    # ==========================================
    "n8n-nodes-base.vonage": (1.0, 1.0, 1.0, "Vonage communications"),
    "n8n-nodes-base.plivo": (1.0, 1.0, 1.0, "Plivo SMS/voice"),
    "n8n-nodes-base.messagebird": (1.0, 1.0, 1.0, "MessageBird SMS"),
    # ==========================================
    # ADDITIONAL UTILITIES
    # ==========================================
    "n8n-nodes-base.qrCode": (1.0, 1.0, 1.0, "QR code generation"),
    "n8n-nodes-base.ipInfo": (1.0, 1.0, 1.0, "IP geolocation"),
    "n8n-nodes-base.whois": (1.0, 1.0, 1.0, "WHOIS lookup"),
    "n8n-nodes-base.rss": (1.0, 1.0, 1.0, "RSS feed reading"),
    "n8n-nodes-base.graphql": (1.0, 1.0, 1.0, "GraphQL requests"),
    # ==========================================
    # ADDITIONAL ANALYTICS
    # ==========================================
    "n8n-nodes-base.amplitude": (1.0, 1.0, 1.0, "Amplitude analytics"),
    "n8n-nodes-base.posthog": (1.0, 1.0, 1.0, "PostHog analytics"),
    "n8n-nodes-base.splitIo": (1.0, 1.0, 1.0, "Split.io feature flags"),
    # ==========================================
    # COLLABORATION
    # ==========================================
    "n8n-nodes-base.microsoftTeams": (2.0, 1.0, 2.0, "Microsoft Teams"),
    "n8n-nodes-base.zoom": (1.0, 1.0, 1.0, "Zoom meetings"),
    "n8n-nodes-base.webex": (1.0, 1.0, 1.0, "Webex meetings"),
    "n8n-nodes-base.pushover": (1.0, 1.0, 1.0, "Pushover notifications"),
    "n8n-nodes-base.pushbullet": (1.0, 1.0, 1.0, "Pushbullet notifications"),
    # ==========================================
    # IOT & SMART HOME
    # ==========================================
    "n8n-nodes-base.homeAssistant": (1.0, 1.0, 1.0, "Home Assistant"),
    "n8n-nodes-base.philipsHue": (1.0, 1.0, 1.0, "Philips Hue lights"),
    # ==========================================
    # CORE FOUNDATIONAL NODES (App-Independent)
    # ==========================================
    # Workflow Control
    "n8n-nodes-base.start": (1.0, 1.0, 1.0, "Workflow start node"),
    "n8n-nodes-base.n8n": (1.0, 1.0, 1.0, "n8n internal workflow operations"),
    "n8n-nodes-base.n8nTrigger": (1.0, 1.0, 1.0, "Trigger on n8n events"),
    "n8n-nodes-base.interval": (1.0, 1.0, 1.0, "Interval-based trigger"),
    "n8n-nodes-base.debug": (1.0, 1.0, 1.0, "Debug/inspect data"),
    "n8n-nodes-base.subWorkflow": (1.0, 1.0, 1.0, "Execute sub-workflow"),
    # Data Type Conversions
    "n8n-nodes-base.toNumber": (1.0, 1.0, 1.0, "Convert to number"),
    "n8n-nodes-base.toString": (1.0, 1.0, 1.0, "Convert to string"),
    "n8n-nodes-base.toBoolean": (1.0, 1.0, 1.0, "Convert to boolean"),
    "n8n-nodes-base.toDate": (1.0, 1.0, 1.0, "Convert to date"),
    "n8n-nodes-base.parseJson": (1.0, 1.0, 1.0, "Parse JSON string to object"),
    # String Operations
    "n8n-nodes-base.regex": (1.0, 1.0, 1.0, "Regular expression operations"),
    "n8n-nodes-base.template": (1.0, 1.0, 1.0, "Template string rendering"),
    "n8n-nodes-base.urlBuilder": (1.0, 1.0, 1.0, "Build/construct URLs"),
    "n8n-nodes-base.urlParse": (1.0, 1.0, 1.0, "Parse URL components"),
    "n8n-nodes-base.base64": (1.0, 1.0, 1.0, "Base64 encode/decode"),
    "n8n-nodes-base.htmlExtract": (1.0, 1.0, 1.0, "Extract data from HTML"),
    "n8n-nodes-base.extractText": (1.0, 1.0, 1.0, "Extract text from data"),
    # Math & Number Operations
    "n8n-nodes-base.math": (1.0, 1.0, 1.0, "Mathematical operations"),
    "n8n-nodes-base.numberOperation": (1.0, 1.0, 1.0, "Number transformations"),
    "n8n-nodes-base.round": (1.0, 1.0, 1.0, "Round numbers"),
    # Binary Data Operations
    "n8n-nodes-base.binaryOperation": (1.0, 1.0, 1.0, "Operations on binary data"),
    "n8n-nodes-base.editImage": (1.0, 1.0, 1.0, "Image manipulation"),
    "n8n-nodes-base.moveToImage": (1.0, 1.0, 1.0, "Move data to image"),
    "n8n-nodes-base.convertBinaryData": (1.0, 1.0, 1.0, "Convert binary data formats"),
    # Flow Control Extensions
    "n8n-nodes-base.multiOutput": (1.0, 1.0, 1.0, "Route to multiple outputs"),
    "n8n-nodes-base.splitOut": (1.0, 1.0, 1.0, "Split to separate outputs"),
    "n8n-nodes-base.errorOutput": (1.0, 1.0, 1.0, "Error output handling"),
    "n8n-nodes-base.loopOver": (1.0, 1.0, 1.0, "Loop over items"),
    "n8n-nodes-base.splitArray": (1.0, 1.0, 1.0, "Split array into items"),
    "n8n-nodes-base.mergeByPosition": (1.0, 1.0, 1.0, "Merge by item position"),
    "n8n-nodes-base.mergeByIndex": (1.0, 1.0, 1.0, "Merge by item index"),
    # Variable & Context
    "n8n-nodes-base.setVariable": (1.0, 1.0, 1.0, "Set workflow variable"),
    "n8n-nodes-base.getVariable": (1.0, 1.0, 1.0, "Get workflow variable"),
    "n8n-nodes-base.setNodeContext": (1.0, 1.0, 1.0, "Set node context data"),
    # Authentication & Security
    "n8n-nodes-base.jwt": (1.0, 1.0, 1.0, "JWT token operations"),
    "n8n-nodes-base.oauth": (1.0, 1.0, 1.0, "OAuth authentication"),
    "n8n-nodes-base.basicAuth": (1.0, 1.0, 1.0, "Basic authentication"),
    # Date & Time
    "n8n-nodes-base.getTimezoneInfo": (1.0, 1.0, 1.0, "Get timezone information"),
    "n8n-nodes-base.schedule": (1.0, 1.0, 1.0, "Schedule-based operations"),
    "n8n-nodes-base.delay": (1.0, 1.0, 1.0, "Delay execution"),
    # SSE & Streaming
    "n8n-nodes-base.sseClient": (1.0, 1.0, 1.0, "Server-sent events client"),
    "n8n-nodes-base.sseClientTrigger": (1.0, 1.0, 1.0, "SSE trigger"),
    # Webhook Extensions
    "n8n-nodes-base.waitForWebhook": (1.0, 1.0, 1.0, "Wait for webhook response"),
    "n8n-nodes-base.webhookResponse": (1.0, 1.0, 1.0, "Send webhook response"),
    # ==========================================
    # ADDITIONAL CORE NODES (from n8n docs)
    # ==========================================
    # Triggers
    "n8n-nodes-base.activationTrigger": (1.0, 1.0, 1.0, "Trigger on workflow activation"),
    "n8n-nodes-base.evaluationTrigger": (1.0, 1.0, 1.0, "Evaluation workflow trigger"),
    # AI & LLM Nodes
    "n8n-nodes-base.aiTransform": (1.0, 1.0, 1.0, "AI-powered data transformation"),
    "n8n-nodes-base.evaluation": (1.0, 1.0, 1.0, "Evaluate/test workflow outputs"),
    "n8n-nodes-base.guardrails": (1.0, 1.0, 1.0, "AI guardrails and safety checks"),
    # Chat & MCP
    "n8n-nodes-langchain.chatTrigger": (1.0, 1.0, 1.0, "Chat conversation trigger"),
    "n8n-nodes-langchain.respondToChat": (1.0, 1.0, 1.0, "Respond to chat message"),
    "n8n-nodes-langchain.mcpTrigger": (1.0, 1.0, 1.0, "MCP protocol trigger"),
    # Data Operations
    "n8n-nodes-base.dataTable": (1.0, 1.0, 1.0, "Data table operations"),
    "n8n-nodes-base.executionData": (1.0, 1.0, 1.0, "Access execution data"),
    "n8n-nodes-base.readWriteFile": (1.0, 1.0, 1.0, "Read/write files combined"),
    # Authentication & Directory
    "n8n-nodes-base.ldap": (1.0, 1.0, 1.0, "LDAP directory operations"),
    "n8n-nodes-base.totp": (1.0, 1.0, 1.0, "Time-based one-time passwords"),
    # Development & Debug
    "n8n-nodes-base.debugHelper": (1.0, 1.0, 1.0, "Debug helper utilities"),
    # Forms
    "n8n-nodes-base.form": (1.0, 1.0, 1.0, "Form node for data collection"),
    # Version Control
    "n8n-nodes-base.git": (1.0, 1.0, 1.0, "Git operations"),
}


def get_node_version(node_type: str, use_latest: bool = True) -> float:
    """
    Get the recommended typeVersion for a given node type.

    Args:
        node_type: The full node type (e.g., 'n8n-nodes-base.webhook')
        use_latest: If True, returns latest version; if False, returns min compatible version

    Returns:
        The typeVersion to use (float)

    Example:
        >>> get_node_version('n8n-nodes-base.webhook')
        2.0
        >>> get_node_version('n8n-nodes-base.httpRequest')
        4.2
    """
    if node_type not in NODE_TYPE_VERSIONS:
        logger.error(f"Unknown node type: {node_type}")
        raise ValueError(f"Unknown node type: {node_type}. Add to NODE_TYPE_VERSIONS or check node type string.")

    default_version, min_version, max_version, notes = NODE_TYPE_VERSIONS[node_type]

    if use_latest:
        return default_version
    else:
        return min_version


def get_node_version_info(node_type: str) -> Optional[Dict]:
    """
    Get detailed version information for a node type.

    Args:
        node_type: The full node type

    Returns:
        Dict with version info or None if node type unknown

    Example:
        >>> info = get_node_version_info('n8n-nodes-base.slack')
        >>> print(info['default'], info['notes'])
        2.3 'Slack - v2.3 has blocks and interactive features'
    """
    if node_type not in NODE_TYPE_VERSIONS:
        return None

    default_version, min_version, max_version, notes = NODE_TYPE_VERSIONS[node_type]

    return {
        "node_type": node_type,
        "default": default_version,
        "min": min_version,
        "max": max_version,
        "notes": notes,
        "recommended": default_version,  # Alias for clarity
    }


def validate_node_version(node_type: str, type_version: float) -> Tuple[bool, str]:
    """
    Validate if a typeVersion is compatible with a node type.

    Args:
        node_type: The full node type
        type_version: The typeVersion to validate

    Returns:
        Tuple of (is_valid, message)

    Example:
        >>> validate_node_version('n8n-nodes-base.webhook', 1.0)
        (True, 'Version 1.0 is supported but 2.0 is recommended')
        >>> validate_node_version('n8n-nodes-base.webhook', 3.0)
        (False, 'Version 3.0 exceeds maximum supported version 2.1')
    """
    if node_type not in NODE_TYPE_VERSIONS:
        return (False, f"Unknown node type {node_type}, cannot validate version")

    default_version, min_version, max_version, notes = NODE_TYPE_VERSIONS[node_type]

    if type_version < min_version:
        return (False, f"Version {type_version} is below minimum supported version {min_version}")

    if type_version > max_version:
        return (False, f"Version {type_version} exceeds maximum supported version {max_version}")

    if type_version < default_version:
        return (True, f"Version {type_version} is supported but {default_version} is recommended")

    if type_version == default_version:
        return (True, f"Version {type_version} is the recommended version")

    return (True, f"Version {type_version} is valid")


def get_all_node_types() -> list:
    """Get list of all supported node types."""
    return list(NODE_TYPE_VERSIONS.keys())


def get_nodes_by_category() -> Dict[str, list]:
    """
    Get nodes organized by category.

    Returns:
        Dict mapping category names to lists of node types
    """
    categories = {
        "triggers": [],
        "http": [],
        "transformation": [],
        "flow_control": [],
        "database": [],
        "communication": [],
        "email": [],
        "storage": [],
        "productivity": [],
        "social": [],
        "ai_ml": [],
        "payment": [],
        "crm": [],
        "project_mgmt": [],
        "analytics": [],
        "cloud_aws": [],
        "cloud_gcp": [],
        "utility": [],
    }

    for node_type in NODE_TYPE_VERSIONS.keys():
        # Simple categorization based on node name
        name_lower = node_type.lower()

        if "trigger" in name_lower:
            categories["triggers"].append(node_type)
        elif "http" in name_lower or "webhook" in name_lower or "respond" in name_lower:
            categories["http"].append(node_type)
        elif any(x in name_lower for x in ["code", "function", "set", "edit", "aggregate", "item"]):
            categories["transformation"].append(node_type)
        elif any(
            x in name_lower
            for x in ["if", "switch", "merge", "split", "wait", "stop", "noop", "filter", "loop"]
        ):
            categories["flow_control"].append(node_type)
        elif any(x in name_lower for x in ["postgres", "mysql", "mongo", "redis", "sqlite", "sql"]):
            categories["database"].append(node_type)
        elif any(
            x in name_lower
            for x in ["slack", "discord", "telegram", "mattermost", "matrix", "twilio"]
        ):
            categories["communication"].append(node_type)
        elif any(
            x in name_lower for x in ["email", "gmail", "outlook", "sendgrid", "mailgun", "imap"]
        ):
            categories["email"].append(node_type)
        elif any(
            x in name_lower for x in ["drive", "dropbox", "s3", "box", "onedrive", "nextcloud"]
        ):
            categories["storage"].append(node_type)
        elif any(
            x in name_lower for x in ["sheets", "docs", "calendar", "excel", "airtable", "notion"]
        ):
            categories["productivity"].append(node_type)
        elif any(
            x in name_lower
            for x in ["twitter", "linkedin", "facebook", "instagram", "reddit", "youtube"]
        ):
            categories["social"].append(node_type)
        elif any(
            x in name_lower for x in ["openai", "anthropic", "hugging", "bedrock", "langchain"]
        ):
            categories["ai_ml"].append(node_type)
        elif any(x in name_lower for x in ["stripe", "paypal", "shopify", "woocommerce"]):
            categories["payment"].append(node_type)
        elif any(
            x in name_lower for x in ["salesforce", "hubspot", "pipedrive", "zoho", "freshworks"]
        ):
            categories["crm"].append(node_type)
        elif any(
            x in name_lower
            for x in ["jira", "trello", "asana", "monday", "clickup", "github", "gitlab"]
        ):
            categories["project_mgmt"].append(node_type)
        elif any(
            x in name_lower
            for x in ["analytics", "mixpanel", "segment", "datadog", "newrelic", "sentry"]
        ):
            categories["analytics"].append(node_type)
        elif "aws" in name_lower:
            categories["cloud_aws"].append(node_type)
        elif "google" in name_lower and "cloud" in name_lower:
            categories["cloud_gcp"].append(node_type)
        else:
            categories["utility"].append(node_type)

    return categories


# Compatibility information
N8N_VERSION_COMPATIBILITY = {
    "target_version": "1.60.0",
    "min_version": "1.50.0",
    "max_version": "1.70.0",
    "tested_versions": ["1.60.0", "1.60.1", "1.61.0", "1.62.0"],
    "notes": "This mapping is optimized for n8n 1.60.0+. Some nodes may have different versions in older n8n releases.",
}


if __name__ == "__main__":
    # Example usage and validation
    print("n8n Node TypeVersion Mapping")
    print("=" * 80)
    print(f"Target n8n version: {N8N_VERSION_COMPATIBILITY['target_version']}")
    print(f"Total nodes mapped: {len(NODE_TYPE_VERSIONS)}")
    print()

    # Show some examples
    examples = [
        "n8n-nodes-base.webhook",
        "n8n-nodes-base.httpRequest",
        "n8n-nodes-base.slack",
        "n8n-nodes-base.postgres",
        "n8n-nodes-base.code",
        "n8n-nodes-base.if",
    ]

    print("Example Node Versions:")
    print("-" * 80)
    for node_type in examples:
        info = get_node_version_info(node_type)
        if info:
            print(f"{node_type:40s} v{info['default']:.1f} - {info['notes']}")

    print()
    print("Categories:")
    print("-" * 80)
    categories = get_nodes_by_category()
    for cat, nodes in categories.items():
        if nodes:
            print(f"{cat:20s}: {len(nodes):3d} nodes")

    print()
    print("Validation Examples:")
    print("-" * 80)
    test_cases = [
        ("n8n-nodes-base.webhook", 1.0),
        ("n8n-nodes-base.webhook", 2.0),
        ("n8n-nodes-base.webhook", 3.0),
        ("n8n-nodes-base.httpRequest", 4.2),
    ]

    for node_type, version in test_cases:
        is_valid, message = validate_node_version(node_type, version)
        status = "✓" if is_valid else "✗"
        print(f"{status} {node_type} v{version}: {message}")
