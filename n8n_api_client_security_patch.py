"""
Security Patch for n8n_api_client.py

This file contains all the security functions and modifications needed
for n8n_api_client.py. Apply these changes to implement P0 security fixes.

Usage:
  1. Add the imports at the top of n8n_api_client.py
  2. Add the security functions after the exception classes
  3. Update the N8nApiClient class methods as indicated

Or run: python3 apply_security_patch.py
"""

# ============================================================================
# SECTION 1: Additional Imports (add to top of file)
# ============================================================================

ADDITIONAL_IMPORTS = """
import ipaddress
import re
from urllib.parse import urlparse
"""

# ============================================================================
# SECTION 2: Security Validation Functions (add after exception classes)
# ============================================================================

SECURITY_FUNCTIONS = '''
def _validate_url_security(url: str) -> None:
    """
    Validate URL to prevent SSRF (Server-Side Request Forgery) attacks.

    Security checks:
    - Only allows http:// and https:// schemes
    - Blocks private IP ranges (10.x, 172.16-31.x, 192.168.x)
    - Blocks localhost and loopback addresses (127.x)
    - Blocks link-local addresses (169.254.x)
    - Blocks IPv6 private addresses

    Args:
        url: URL to validate

    Raises:
        N8nValidationError: If URL fails security validation
    """
    try:
        parsed = urlparse(url)

        # Check scheme - only allow http/https
        if parsed.scheme not in ['http', 'https']:
            raise N8nValidationError(
                f"Invalid URL scheme '{parsed.scheme}'. Only http:// and https:// are allowed."
            )

        # Extract hostname
        hostname = parsed.hostname
        if not hostname:
            raise N8nValidationError("URL must contain a valid hostname")

        # Try to resolve hostname to IP address
        try:
            # Check if it's already an IP address
            ip = ipaddress.ip_address(hostname)
        except ValueError:
            # It's a hostname - block obvious localhost references
            hostname_lower = hostname.lower()
            if hostname_lower in ['localhost', 'localhost.localdomain']:
                raise N8nValidationError(
                    "Access to localhost is not allowed for security reasons"
                )
            # Allow domain names - they will be validated at connection time
            return

        # If we have an IP address, validate it's not private/internal
        if ip.is_private:
            raise N8nValidationError(
                f"Access to private IP address {ip} is not allowed for security reasons"
            )

        if ip.is_loopback:
            raise N8nValidationError(
                f"Access to loopback address {ip} is not allowed for security reasons"
            )

        if ip.is_link_local:
            raise N8nValidationError(
                f"Access to link-local address {ip} is not allowed for security reasons"
            )

        if ip.is_reserved:
            raise N8nValidationError(
                f"Access to reserved IP address {ip} is not allowed for security reasons"
            )

    except N8nValidationError:
        raise
    except Exception as e:
        raise N8nValidationError(f"URL validation failed: {str(e)}")


def _sanitize_url(url: str) -> str:
    """
    Sanitize URL by removing credentials for safe logging.

    Removes username and password from URLs to prevent credential leakage in logs.
    Example: https://user:pass@example.com -> https://***:***@example.com

    Args:
        url: URL to sanitize

    Returns:
        Sanitized URL safe for logging
    """
    try:
        parsed = urlparse(url)
        if parsed.username or parsed.password:
            # Replace credentials with asterisks
            netloc = parsed.netloc
            if '@' in netloc:
                netloc = '***:***@' + netloc.split('@', 1)[1]
            # Reconstruct URL with sanitized netloc
            sanitized = parsed._replace(netloc=netloc)
            return sanitized.geturl()
        return url
    except Exception:
        # If sanitization fails, return a safe placeholder
        return "[URL REDACTED]"
'''

# ============================================================================
# SECTION 3: N8nApiClient Class Methods (add to class)
# ============================================================================

VALIDATION_METHODS = '''
    @staticmethod
    def _validate_api_key(api_key: str) -> None:
        """
        Validate API key format.

        Security checks:
        - Not empty
        - Reasonable length (between 8 and 512 characters)
        - String type

        Args:
            api_key: API key to validate

        Raises:
            N8nValidationError: If API key is invalid
        """
        if not isinstance(api_key, str):
            raise N8nValidationError("api_key must be a string")

        if not api_key or len(api_key.strip()) == 0:
            raise N8nValidationError("api_key cannot be empty")

        if len(api_key) < 8:
            raise N8nValidationError("api_key is too short (minimum 8 characters)")

        if len(api_key) > 512:
            raise N8nValidationError("api_key is too long (maximum 512 characters)")

    @staticmethod
    def _validate_workflow_id(workflow_id: str) -> None:
        """
        Validate workflow ID format.

        Security checks:
        - Not empty
        - Contains only alphanumeric characters, hyphens, and underscores
        - Reasonable length (max 100 characters)
        - Prevents path traversal attempts

        Args:
            workflow_id: Workflow ID to validate

        Raises:
            N8nValidationError: If workflow ID is invalid
        """
        if not isinstance(workflow_id, str):
            raise N8nValidationError("workflow_id must be a string")

        if not workflow_id or len(workflow_id.strip()) == 0:
            raise N8nValidationError("workflow_id cannot be empty")

        if len(workflow_id) > 100:
            raise N8nValidationError("workflow_id is too long (maximum 100 characters)")

        # Check for path traversal attempts
        if '..' in workflow_id or '/' in workflow_id or '\\\\' in workflow_id:
            raise N8nValidationError("workflow_id contains invalid characters (path traversal detected)")

        # Allow alphanumeric, hyphens, and underscores only
        if not re.match(r'^[a-zA-Z0-9\\-_]+$', workflow_id):
            raise N8nValidationError(
                "workflow_id must contain only alphanumeric characters, hyphens, and underscores"
            )
'''

# ============================================================================
# SECTION 4: Modifications to Existing Methods
# ============================================================================

INIT_MODIFICATIONS = """
# In __init__ method, add after api_url parameter check:

        # SECURITY: Validate input parameters
        if not api_url or not isinstance(api_url, str):
            raise N8nValidationError("api_url is required and must be a non-empty string")

        if api_key is not None:
            self._validate_api_key(api_key)

        # Clean up API URL
        self.base_url = api_url.rstrip("/")
        if self.base_url.endswith("/api/v1"):
            self.base_url = self.base_url[:-7]

        # SECURITY: Validate URL to prevent SSRF attacks
        _validate_url_security(self.base_url)

# In __init__ method, update logging line:
        # SECURITY: Use sanitized URL in logs to prevent credential leakage
        logger.debug(f"Initialized n8n API client for {_sanitize_url(self.api_url)}")
"""

REQUEST_MODIFICATIONS = """
# In _request method, update logging line:
        # SECURITY: Use sanitized URL in logs
        logger.debug(f"{method} {_sanitize_url(url)}")
"""

VERSION_MODIFICATIONS = """
# In get_n8n_version method, replace the version extraction code with:

            try:
                response = self.session.get(f"{self.base_url}/", timeout=self.timeout)
                if response.ok and "n8n" in response.text.lower():
                    # SECURITY: Limit response size to prevent ReDoS attacks
                    # Only process first 10KB of response
                    response_text = response.text[:10240]

                    # Try to extract version from HTML/response
                    # Using a simpler, safer regex pattern with limited backtracking
                    version_match = re.search(
                        r'version["\\\s:]+([0-9]+\\.[0-9]+(?:\\.[0-9]+)?)',
                        response_text,
                        re.IGNORECASE | re.MULTILINE
                    )
                    if version_match:
                        return {
                            "version": version_match.group(1),
                            "success": True,
                            "method": "root_endpoint",
                        }
            except Exception:
                pass
"""

WORKFLOW_VALIDATIONS = """
# Add validation at the start of these methods:

def get_workflow(self, workflow_id: str) -> Dict[str, Any]:
    # SECURITY: Validate workflow_id to prevent path traversal
    self._validate_workflow_id(workflow_id)
    # ... rest of method

def export_workflow(self, workflow_id: str) -> Dict[str, Any]:
    # SECURITY: Validate workflow_id
    self._validate_workflow_id(workflow_id)
    # ... rest of method

def update_workflow(self, workflow_id: str, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
    # SECURITY: Validate workflow_id
    self._validate_workflow_id(workflow_id)
    # ... rest of method

def delete_workflow(self, workflow_id: str) -> bool:
    # SECURITY: Validate workflow_id
    self._validate_workflow_id(workflow_id)
    # ... rest of method

def activate_workflow(self, workflow_id: str) -> Dict[str, Any]:
    # SECURITY: Validate workflow_id
    self._validate_workflow_id(workflow_id)
    # ... rest of method

def deactivate_workflow(self, workflow_id: str) -> Dict[str, Any]:
    # SECURITY: Validate workflow_id
    self._validate_workflow_id(workflow_id)
    # ... rest of method

def test_workflow_execution(self, workflow_id: str, input_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    # SECURITY: Validate workflow_id
    self._validate_workflow_id(workflow_id)
    # ... rest of method
"""

# ============================================================================
# SECTION 5: Application Instructions
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("n8n_api_client.py Security Patch")
    print("=" * 70)
    print()
    print("This file contains all security fixes for n8n_api_client.py")
    print()
    print("To apply manually:")
    print("  1. Add ADDITIONAL_IMPORTS to the imports section")
    print("  2. Add SECURITY_FUNCTIONS after exception classes")
    print("  3. Add VALIDATION_METHODS to N8nApiClient class")
    print("  4. Apply modifications from:")
    print("     - INIT_MODIFICATIONS")
    print("     - REQUEST_MODIFICATIONS")
    print("     - VERSION_MODIFICATIONS")
    print("     - WORKFLOW_VALIDATIONS")
    print()
    print("=" * 70)
    print()
    print("Code sections available as variables:")
    print("  - ADDITIONAL_IMPORTS")
    print("  - SECURITY_FUNCTIONS")
    print("  - VALIDATION_METHODS")
    print("  - INIT_MODIFICATIONS")
    print("  - REQUEST_MODIFICATIONS")
    print("  - VERSION_MODIFICATIONS")
    print("  - WORKFLOW_VALIDATIONS")
    print()
    print("=" * 70)
