# Security Policy

## Supported Versions

Project Automata is currently in alpha release. We provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 2.0.x   | :white_check_mark: |
| < 2.0   | :x:                |

## Reporting a Vulnerability

We take the security of Project Automata seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### Please Do Not

- **Do not** open a public GitHub issue for security vulnerabilities
- **Do not** disclose the vulnerability publicly until we have addressed it
- **Do not** exploit the vulnerability for malicious purposes

### Please Do

**Report security vulnerabilities via GitHub Security Advisories:**

1. Go to the [Security tab](https://github.com/drjlsmith10/n8er/security) of our repository
2. Click "Report a vulnerability"
3. Fill out the vulnerability report form with:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if you have one)

**Or email us directly:**

- Email: security@projectautomata.dev (if available)
- Include "[SECURITY]" in the subject line
- Provide detailed information about the vulnerability

### What to Include in Your Report

Please provide as much information as possible:

- **Type of vulnerability** (e.g., SQL injection, XSS, command injection, etc.)
- **Full paths** of source file(s) related to the vulnerability
- **Location** of the affected source code (tag/branch/commit or direct URL)
- **Step-by-step instructions** to reproduce the issue
- **Proof-of-concept or exploit code** (if possible)
- **Impact** of the issue, including how an attacker might exploit it

### Response Timeline

- **Initial Response**: Within 48 hours, we will acknowledge receipt of your vulnerability report
- **Investigation**: Within 7 days, we will provide an initial assessment of the vulnerability
- **Fix Timeline**: Depending on complexity, we aim to:
  - Critical vulnerabilities: Fix within 7 days
  - High severity: Fix within 14 days
  - Medium/Low severity: Fix within 30 days
- **Disclosure**: We will coordinate with you on public disclosure timing

### Security Update Process

When a security vulnerability is fixed:

1. We will release a security patch
2. We will publish a security advisory on GitHub
3. We will credit the reporter (unless they prefer to remain anonymous)
4. We will update the changelog with security fix details

## Security Best Practices for Users

### API Key Management

**Critical: Never commit API keys to version control**

- Always use environment variables for sensitive credentials
- Use the provided `.env.example` as a template
- Ensure `.env` is in `.gitignore`
- Rotate API keys regularly
- Use separate keys for development and production

### Configuration Security

**Review these settings in your `.env` file:**

```bash
# Use strong, unique values
SECRET_KEY=<generate-strong-random-value>

# Restrict access in production
ALLOWED_HOSTS=yourdomain.com

# Disable debug in production
DEBUG=false
ENVIRONMENT=production

# Use HTTPS in production
FORCE_HTTPS=true
```

### Deployment Security

**Docker Deployment:**
- Run containers as non-root user
- Use read-only file systems where possible
- Limit container resources (CPU, memory)
- Keep base images updated
- Scan images for vulnerabilities

**Server Deployment:**
- Use the provided systemd service with security hardening
- Enable firewall rules to restrict access
- Keep system packages updated
- Use fail2ban or similar to prevent brute force
- Enable audit logging

### Workflow Security

**When generating workflows:**

- **Review all generated workflows** before deploying to production
- **Validate credentials** used in workflows are scoped appropriately
- **Test workflows** in isolated environments first
- **Monitor workflow execution** for unexpected behavior
- **Limit webhook endpoints** to trusted sources

### Network Security

- **Use HTTPS** for all external API calls
- **Validate SSL certificates** (don't disable certificate validation)
- **Implement rate limiting** on webhook endpoints
- **Use VPN or private networks** when connecting to internal services
- **Whitelist IP addresses** for sensitive endpoints

## Known Security Considerations

### AI-Generated Workflows

Project Automata uses AI to generate n8n workflows. Be aware:

- **AI-generated code should always be reviewed** before production use
- **Workflows may contain logic errors** that could expose data
- **Validate all user inputs** in generated workflows
- **Test error handling** to prevent information leakage
- **Review permissions** granted to workflow credentials

### Third-Party Dependencies

We regularly monitor and update dependencies. Current considerations:

- All dependencies are from PyPI trusted sources
- We use `safety` to scan for known vulnerabilities
- Dependencies are pinned to specific versions in `requirements.txt`
- We review dependency updates before merging

### API Integrations

The project integrates with third-party APIs:

- **Reddit API**: Read-only access, minimal permissions
- **YouTube API**: Public data only, no user data
- **Twitter API**: Read-only, public tweets only
- **n8n API**: Full workflow access (required for functionality)

**Recommendation**: Create separate API credentials for Project Automata with minimal required permissions.

## Vulnerability Disclosure Policy

We follow **coordinated disclosure**:

1. Security researchers report vulnerabilities privately
2. We acknowledge and investigate reports promptly
3. We develop and test fixes
4. We coordinate disclosure timing with the reporter
5. We publicly disclose after fixes are released
6. We credit reporters in security advisories

## Security Hall of Fame

We appreciate security researchers who help keep Project Automata secure. Contributors who responsibly disclose vulnerabilities will be listed here:

- _No vulnerabilities reported yet_

## Security Checklist for Contributors

Before submitting code:

- [ ] No hardcoded secrets, API keys, or passwords
- [ ] User inputs are validated and sanitized
- [ ] SQL queries use parameterized statements (if applicable)
- [ ] File paths are validated to prevent directory traversal
- [ ] External commands are properly escaped
- [ ] Error messages don't leak sensitive information
- [ ] Dependencies are from trusted sources
- [ ] Security best practices are followed

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [n8n Security Documentation](https://docs.n8n.io/hosting/security/)

## Contact

For security concerns that are not vulnerabilities (questions, clarifications, etc.):
- Open a discussion on GitHub
- Tag with `security` label
- Email: support@projectautomata.dev

---

**Last Updated**: 2025-11-09
**Version**: 2.0.0-alpha
