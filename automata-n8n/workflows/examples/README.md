# Workflow Examples

This directory contains 10 diverse, real-world workflow examples for Project Automata/n8n. Each example demonstrates different automation patterns and integrations.

## Available Examples

### 1. **Google Sheets to Slack Integration**
- **File:** `google_sheets_to_slack.json`
- **Description:** Automatically fetch data from Google Sheets and send formatted updates to Slack
- **Key Features:**
  - Scheduled cron trigger (every 6 hours)
  - Google Sheets integration
  - Code node for data formatting
  - Slack notifications
- **Use Case:** Team dashboards, regular reporting, data synchronization

### 2. **GitHub Issue Tracker**
- **File:** `github_issue_tracker.json`
- **Description:** Monitor GitHub repository issues and notify teams about new issues
- **Key Features:**
  - Cron-based polling (every 2 hours)
  - GitHub API integration
  - Conditional filtering
  - Slack alerts
- **Use Case:** Project management, issue tracking, team alerts

### 3. **Email to Database**
- **File:** `email_to_database.json`
- **Description:** Extract data from incoming emails and automatically store in a database
- **Key Features:**
  - Email trigger
  - Data extraction using code node
  - PostgreSQL storage
  - Automatic processing
- **Use Case:** Data ingestion, inbox processing, automated CRM updates

### 4. **Scheduled Database Backup**
- **File:** `scheduled_backup.json`
- **Description:** Regularly backup database and upload to cloud storage with confirmations
- **Key Features:**
  - Scheduled execution (daily at 2 AM)
  - PostgreSQL export
  - AWS S3 upload
  - Email notifications
- **Use Case:** Data protection, compliance, disaster recovery

### 5. **API Health Monitoring**
- **File:** `api_monitoring.json`
- **Description:** Monitor API endpoints for availability and alert on failures
- **Key Features:**
  - Frequent health checks (every 5 minutes)
  - HTTP request testing
  - Conditional branching
  - Database logging
  - Slack alerts
- **Use Case:** Service monitoring, SLA tracking, incident response

### 6. **Data Enrichment Pipeline**
- **File:** `data_enrichment.json`
- **Description:** Enrich customer data with information from external sources
- **Key Features:**
  - Database queries
  - External API integration (Clearbit)
  - Data transformation
  - Database updates
- **Use Case:** CRM enhancement, data quality improvement, customer intelligence

### 7. **Multi-Step Approval Workflow**
- **File:** `multi_step_approval.json`
- **Description:** Route requests through multiple approval stages with notifications
- **Key Features:**
  - Webhook trigger
  - Slack notifications
  - Wait nodes for human interaction
  - Conditional routing
  - Email notifications
- **Use Case:** Process automation, approvals, request management

### 8. **Error Notification System**
- **File:** `error_notification.json`
- **Description:** Catch API errors and notify teams with retry logic
- **Key Features:**
  - Error handling patterns
  - Retry logic
  - Database logging
  - Slack alerts
- **Use Case:** Error monitoring, debugging, incident management

### 9. **RSS Feed Aggregator**
- **File:** `rss_aggregator.json`
- **Description:** Aggregate multiple RSS feeds and send daily digests
- **Key Features:**
  - Scheduled execution (daily at 8 AM)
  - RSS feed integration
  - Content aggregation
  - Email digests
- **Use Case:** Content curation, news aggregation, team communication

### 10. **Form Submission Handler**
- **File:** `form_submission_handler.json`
- **Description:** Handle form submissions with validation, storage, and notifications
- **Key Features:**
  - Form trigger
  - Input validation
  - Database storage
  - Email confirmations
  - Admin notifications
- **Use Case:** Lead capture, contact forms, survey collection

## How to Use These Examples

### 1. **Import into n8n**
- Copy the JSON content of any example workflow
- In n8n, go to **Workflows** → **Import**
- Paste the JSON and click **Import**

### 2. **Customize for Your Use Case**
Each workflow is a template that requires customization:
- **Replace API keys and credentials** with your own
- **Update email addresses** to your recipients
- **Modify database table names** and queries
- **Adjust scheduling** based on your needs
- **Change Slack channels** to your team channels

### 3. **Configuration Checklist**
Before activating any workflow:
- [ ] Verify all API credentials are configured
- [ ] Check database connection settings
- [ ] Update email addresses and Slack channels
- [ ] Test with a small dataset first
- [ ] Set appropriate scheduling (if applicable)
- [ ] Enable error logging and monitoring

## Credential Setup Guide

### Common Credentials Needed

#### Google Sheets
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a service account
3. Generate JSON key file
4. Add credentials to n8n

#### Slack
1. Create a [Slack App](https://api.slack.com/apps)
2. Add Bot Token Scopes: `chat:write`, `channels:read`
3. Install app to workspace
4. Copy Bot User OAuth Token

#### GitHub
1. Create [Personal Access Token](https://github.com/settings/tokens)
2. Select scopes: `repo`, `gist`
3. Add token to n8n as "GitHub Token"

#### PostgreSQL
1. Ensure PostgreSQL instance is accessible
2. Create database user with appropriate permissions
3. Note connection details (host, port, database, user, password)

#### AWS S3
1. Create IAM user with S3 access
2. Generate Access Key ID and Secret Access Key
3. Add to n8n as AWS credentials

#### Clearbit
1. Sign up at [clearbit.com](https://clearbit.com)
2. Get API key from dashboard
3. Add to n8n

## Best Practices

### 1. **Error Handling**
- Always add error handling paths
- Log errors to database or monitoring system
- Set up alerts for critical failures

### 2. **Rate Limiting**
- Consider API rate limits
- Add delays between requests if needed
- Implement exponential backoff for retries

### 3. **Data Security**
- Never hardcode sensitive data
- Use n8n credentials vault
- Encrypt sensitive fields
- Audit data access logs

### 4. **Performance**
- Use batch operations when possible
- Filter data early to reduce processing
- Consider resource usage and costs
- Monitor execution times

### 5. **Testing**
- Test with small datasets first
- Verify error scenarios
- Check edge cases
- Document assumptions

## Extending the Examples

These examples can be combined and extended:
- Add multiple data sources
- Create branching logic for different data types
- Implement feedback loops
- Add human-in-the-loop approvals
- Create escalation paths

## Troubleshooting

### Common Issues

**Authentication Failures**
- Verify credentials are correctly configured
- Check credential expiration dates
- Ensure proper scopes/permissions are granted

**Data Formatting Errors**
- Check expected data structure
- Add validation before processing
- Use code nodes to transform data

**Timeout Issues**
- Increase timeout values
- Break large operations into smaller batches
- Consider asynchronous processing

**Rate Limiting**
- Add delays between API calls
- Implement retry logic with exponential backoff
- Consider using webhooks instead of polling

## Learning Resources

- [n8n Documentation](https://docs.n8n.io)
- [n8n Community Forum](https://community.n8n.io)
- [n8n Discord](https://discord.gg/n8n)
- [Project Automata Docs](../docs/)

## Contributing

To contribute new workflow examples:
1. Create a new `.json` file with a descriptive name
2. Follow the structure of existing examples
3. Add comprehensive documentation in comments
4. Test thoroughly before submitting
5. Include setup instructions for required credentials

## License

These workflow examples are provided under the same license as Project Automata (MIT License).

---

**Last Updated:** 2025-11-20
**Version:** 1.0
**Maintainer:** Project Automata Team
