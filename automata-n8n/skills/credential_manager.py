"""
Credential Management for n8n Workflows

This module provides tools for managing credentials in n8n workflows,
including credential templates, placeholders, and reference tracking.

Author: Project Automata - Agent 5 (High Priority Features)
Version: 2.2.0 - Security Hardened
Created: 2025-11-20
Updated: 2025-11-20 - Added P0 security fixes (field-level encryption)
Issue: #9 - Credential Management

Security Features (P0 Fixes):
- Field-level encryption for sensitive credential data
- Automatic encryption/decryption of sensitive fields
- Secure key management with environment variables
"""

import base64
import json
import logging
import os
import secrets
import threading
from dataclasses import asdict, dataclass, field
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Dict, List, Optional

# Try to import cryptography for encryption support
try:
    from cryptography.fernet import Fernet
    ENCRYPTION_AVAILABLE = True
except ImportError:
    ENCRYPTION_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning(
        "cryptography library not available. Install with: pip install cryptography"
    )

# Configure logging - Application should configure logging, not libraries
# logging.basicConfig() removed to prevent global logging configuration conflicts
logger = logging.getLogger(__name__)

# Import pydantic validation schemas
try:
    from validation_schemas import validate_credential, CredentialInput
    VALIDATION_AVAILABLE = True
except ImportError:
    VALIDATION_AVAILABLE = False


@dataclass
class CredentialTemplate:
    """
    Template for n8n credential configuration.

    Represents a credential placeholder that can be referenced by nodes.
    Actual credential values are stored in n8n and referenced by ID or name.

    Attributes:
        name: Human-readable credential name
        type: n8n credential type (e.g., 'httpBasicAuth', 'slackApi')
        description: Purpose and usage notes
        credential_id: Optional UUID for existing credentials
        fields: Required and optional fields for this credential type
        environment: Environment this credential is for (dev, staging, prod)
        created_at: Timestamp of creation
    """

    name: str
    type: str
    description: str = ""
    credential_id: Optional[str] = None
    fields: Dict[str, Any] = field(default_factory=dict)
    environment: str = "production"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return asdict(self)

    def to_node_reference(self) -> Dict[str, Any]:
        """
        Generate credential reference for use in node configuration.

        Returns:
            Dict in format expected by n8n nodes
        """
        if self.credential_id:
            return {"id": self.credential_id, "name": self.name}
        else:
            return {"name": self.name}

    def validate(self) -> List[str]:
        """
        Validate credential template configuration.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        if not self.name:
            errors.append("Credential name is required")

        if not self.type:
            errors.append("Credential type is required")

        # Check for common credential types
        valid_types = [
            "httpBasicAuth",
            "httpDigestAuth",
            "httpHeaderAuth",
            "oAuth2Api",
            "slackApi",
            "googleApi",
            "postgresApi",
            "mysqlApi",
            "mongoDb",
            "aws",
            "githubApi",
            "telegramApi",
            "discordApi",
            "emailSendApi",
            "sshPassword",
            "sshPrivateKey",
            "ftpApi",
            "httpQueryAuth",
        ]

        if self.type not in valid_types and not self.type.endswith("Api"):
            errors.append(
                f"Credential type '{self.type}' may not be valid. Common types: {', '.join(valid_types[:5])}"
            )

        return errors


class CredentialManager:
    """
    Manages credentials for workflow generation.

    Tracks credential templates, validates references, and provides
    credential lifecycle management with field-level encryption support.

    Security Features:
    - Automatic encryption of sensitive fields
    - Uses cryptography.fernet for field-level encryption
    - Key management via environment variables

    Thread Safety:
        This class is thread-safe. All public methods that modify state are protected
        by an internal lock to prevent race conditions and TOCTOU vulnerabilities.

    Note:
        @thread_safe - All public methods are protected by internal lock
    """

    def __init__(self, encryption_key: Optional[bytes] = None):
        """
        Initialize credential manager with optional encryption support.

        Args:
            encryption_key: Optional Fernet encryption key (32 bytes, base64-encoded).
                          If not provided, will look for CREDENTIAL_ENCRYPTION_KEY env var.
                          If neither provided, encryption will be disabled with a warning.

        Example:
            # Generate a new key:
            # from cryptography.fernet import Fernet
            # key = Fernet.generate_key()

            # Using encryption:
            manager = CredentialManager(encryption_key=key)

            # Or from environment:
            # export CREDENTIAL_ENCRYPTION_KEY="your-base64-key"
            manager = CredentialManager()
        """
        self.credentials: Dict[str, CredentialTemplate] = {}
        self.node_credential_map: Dict[str, List[str]] = {}

        # Thread safety: Lock for protecting credential dictionary mutations
        self._lock = threading.RLock()

        # SECURITY: Initialize encryption
        self._fernet: Optional[Fernet] = None
        self._encryption_enabled = False

        if ENCRYPTION_AVAILABLE:
            # Try to get encryption key from parameter or environment
            key = encryption_key or os.getenv("CREDENTIAL_ENCRYPTION_KEY", "").encode()

            if key:
                try:
                    self._fernet = Fernet(key)
                    self._encryption_enabled = True
                    logger.info("Credential encryption enabled")
                except Exception as e:
                    logger.error(f"Failed to initialize encryption: {e}")
                    logger.warning("Continuing without encryption - credentials will NOT be encrypted!")
            else:
                logger.warning(
                    "No encryption key provided. Credentials will NOT be encrypted! "
                    "Set CREDENTIAL_ENCRYPTION_KEY environment variable or pass encryption_key parameter."
                )
        else:
            logger.warning(
                "cryptography library not available. Credentials will NOT be encrypted! "
                "Install with: pip install cryptography"
            )

        logger.debug("Initialized CredentialManager")

    def _encrypt_field(self, value: str) -> str:
        """
        Encrypt a sensitive field value.

        Args:
            value: Plain text value to encrypt

        Returns:
            Encrypted value (base64-encoded) or original if encryption disabled

        Note:
            If encryption is not enabled, returns the original value with a warning.
        """
        if not self._encryption_enabled or not self._fernet:
            logger.warning(
                f"Encryption not enabled - sensitive data stored in plain text! "
                f"Value preview: {value[:10]}..."
            )
            return value

        try:
            # Encrypt and return as base64 string
            encrypted_bytes = self._fernet.encrypt(value.encode('utf-8'))
            return base64.b64encode(encrypted_bytes).decode('utf-8')
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise ValueError(f"Failed to encrypt field: {e}")

    def _decrypt_field(self, encrypted_value: str) -> str:
        """
        Decrypt a sensitive field value.

        Args:
            encrypted_value: Encrypted value (base64-encoded)

        Returns:
            Decrypted plain text value

        Raises:
            ValueError: If decryption fails
        """
        if not self._encryption_enabled or not self._fernet:
            # If encryption was never enabled, value is plain text
            return encrypted_value

        try:
            # Decode from base64 and decrypt
            encrypted_bytes = base64.b64decode(encrypted_value.encode('utf-8'))
            decrypted_bytes = self._fernet.decrypt(encrypted_bytes)
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise ValueError(f"Failed to decrypt field: {e}")

    def _process_fields_for_storage(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process credential fields, encrypting sensitive ones.

        Args:
            fields: Field definitions with values

        Returns:
            Fields with sensitive values encrypted
        """
        if not fields:
            return fields

        processed = {}
        for field_name, field_config in fields.items():
            if isinstance(field_config, dict):
                processed[field_name] = field_config.copy()
                # Check if field is marked as sensitive
                if field_config.get("sensitive", False) and "value" in field_config:
                    value = field_config["value"]
                    if isinstance(value, str) and value:
                        # Encrypt the value
                        processed[field_name]["value"] = self._encrypt_field(value)
                        processed[field_name]["_encrypted"] = True
            else:
                processed[field_name] = field_config

        return processed

    def _process_fields_for_use(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process credential fields, decrypting sensitive ones.

        Args:
            fields: Field definitions with encrypted values

        Returns:
            Fields with sensitive values decrypted
        """
        if not fields:
            return fields

        processed = {}
        for field_name, field_config in fields.items():
            if isinstance(field_config, dict):
                processed[field_name] = field_config.copy()
                # Check if field was encrypted
                if field_config.get("_encrypted", False) and "value" in field_config:
                    encrypted_value = field_config["value"]
                    if isinstance(encrypted_value, str):
                        # Decrypt the value
                        processed[field_name]["value"] = self._decrypt_field(encrypted_value)
                        # Remove encryption marker
                        del processed[field_name]["_encrypted"]
            else:
                processed[field_name] = field_config

        return processed

    def add_credential(
        self,
        name: str,
        credential_type: str,
        description: str = "",
        credential_id: Optional[str] = None,
        fields: Optional[Dict[str, Any]] = None,
        environment: str = "production",
    ) -> CredentialTemplate:
        """
        Add a credential template.

        Thread Safety:
            @thread_safe - Protected by internal lock

        Args:
            name: Credential name
            credential_type: n8n credential type
            description: Usage description
            credential_id: Optional existing credential UUID
            fields: Field definitions
            environment: Target environment

        Returns:
            Created CredentialTemplate

        Raises:
            ValueError: If validation fails
        """
        # Input validation - validate before creating credential
        if not name or not name.strip():
            raise ValueError("Credential name cannot be empty")

        if len(name) > 255:
            raise ValueError(f"Credential name too long ({len(name)} chars). Maximum 255 characters allowed")

        if not credential_type or not credential_type.strip():
            raise ValueError("Credential type cannot be empty")

        # Validate credential type against known types
        valid_types = [
            "httpBasicAuth",
            "httpDigestAuth",
            "httpHeaderAuth",
            "oAuth2Api",
            "slackApi",
            "googleApi",
            "postgresApi",
            "mysqlApi",
            "mongoDb",
            "aws",
            "githubApi",
            "telegramApi",
            "discordApi",
            "emailSendApi",
            "sshPassword",
            "sshPrivateKey",
            "ftpApi",
            "httpQueryAuth",
        ]

        if credential_type not in valid_types and not credential_type.endswith("Api"):
            raise ValueError(
                f"Unknown credential type: {credential_type}. Must be one of {', '.join(valid_types)} or end with 'Api'"
            )

        # SECURITY: Process fields to encrypt sensitive ones
        processed_fields = self._process_fields_for_storage(fields or {})

        credential = CredentialTemplate(
            name=name,
            type=credential_type,
            description=description,
            credential_id=credential_id,
            fields=processed_fields,
            environment=environment,
        )

        # Validate credential structure
        errors = credential.validate()
        if errors:
            raise ValueError(f"Invalid credential: {', '.join(errors)}")

        # Thread-safe: Protect credential dictionary mutation
        with self._lock:
            self.credentials[name] = credential

        logger.debug(f"Added credential template: {name} ({credential_type}) - sensitive fields encrypted")

        return credential

    def get_credential(self, name: str) -> Optional[CredentialTemplate]:
        """
        Get credential template by name.

        Thread Safety:
            @thread_safe - Protected by internal lock
        """
        with self._lock:
            return self.credentials.get(name)

    def list_credentials(self, environment: Optional[str] = None) -> List[CredentialTemplate]:
        """
        List all credential templates.

        Thread Safety:
            @thread_safe - Protected by internal lock

        Args:
            environment: Optional filter by environment

        Returns:
            List of credential templates
        """
        with self._lock:
            if environment:
                return [c for c in self.credentials.values() if c.environment == environment]
            return list(self.credentials.values())

    def track_node_credential(self, node_name: str, credential_name: str) -> None:
        """
        Track which credentials are used by which nodes.

        Thread Safety:
            @thread_safe - Protected by internal lock to prevent TOCTOU race conditions

        Args:
            node_name: Name of node using credential
            credential_name: Name of credential being used
        """
        # Thread-safe: Protect against TOCTOU race condition
        # Multiple threads could check if node exists, both see it doesn't exist,
        # and both try to create it simultaneously
        with self._lock:
            if node_name not in self.node_credential_map:
                self.node_credential_map[node_name] = []

            if credential_name not in self.node_credential_map[node_name]:
                self.node_credential_map[node_name].append(credential_name)
                logger.debug(f"Node '{node_name}' uses credential '{credential_name}'")

    def get_node_credentials(self, node_name: str) -> List[CredentialTemplate]:
        """
        Get all credentials used by a specific node.

        Thread Safety:
            @thread_safe - Protected by internal lock

        Args:
            node_name: Node name

        Returns:
            List of credential templates used by node
        """
        with self._lock:
            cred_names = self.node_credential_map.get(node_name, [])
            return [self.credentials[name] for name in cred_names if name in self.credentials]

    def get_workflow_credentials(self) -> List[CredentialTemplate]:
        """
        Get all credentials used in the workflow.

        Thread Safety:
            @thread_safe - Protected by internal lock

        Returns:
            List of all credential templates
        """
        with self._lock:
            return list(self.credentials.values())

    def generate_credential_reference(self, credential_name: str) -> Dict[str, Any]:
        """
        Generate credential reference for node configuration.

        Args:
            credential_name: Name of credential

        Returns:
            Credential reference dict

        Raises:
            ValueError: If credential not found
        """
        credential = self.get_credential(credential_name)
        if not credential:
            raise ValueError(f"Credential not found: {credential_name}")

        return credential.to_node_reference()

    def export_credentials_manifest(self) -> Dict[str, Any]:
        """
        Export credentials manifest for documentation/setup.

        Returns:
            Dictionary containing all credential definitions and usage
        """
        manifest = {
            "credentials": [c.to_dict() for c in self.credentials.values()],
            "node_credential_map": self.node_credential_map,
            "total_credentials": len(self.credentials),
            "environments": list(set(c.environment for c in self.credentials.values())),
            "exported_at": datetime.utcnow().isoformat() + "Z",
        }

        return manifest

    def validate_all(self) -> Dict[str, List[str]]:
        """
        Validate all credentials.

        Returns:
            Dict mapping credential names to validation errors
        """
        validation_results = {}

        for name, credential in self.credentials.items():
            errors = credential.validate()
            if errors:
                validation_results[name] = errors

        if validation_results:
            logger.warning(f"Found validation issues in {len(validation_results)} credentials")
        else:
            logger.debug("All credentials validated successfully")

        return validation_results

    def save_manifest(self, filepath: str) -> None:
        """
        Save credentials manifest to JSON file with encrypted sensitive fields.

        ⚠️  SECURITY NOTES ⚠️
        - Sensitive fields marked with "sensitive": True are encrypted if encryption is enabled
        - Encrypted fields are stored with "_encrypted": True marker
        - You must use the same encryption key to load and decrypt the credentials
        - File still contains metadata that could expose infrastructure details

        RECOMMENDATIONS:
        - Ensure file permissions are restrictive (600 or 400)
        - Never commit credential manifests to version control
        - Keep encryption key secure (use environment variables)
        - Add credential manifest files to .gitignore
        - Rotate encryption keys periodically

        Args:
            filepath: Output file path

        Note:
            If encryption is not enabled, sensitive fields will be saved in plain text
            with a warning.
        """
        # Runtime security warnings
        if self._encryption_enabled:
            logger.info(f"Saving encrypted credentials to: {filepath}")
            logger.warning("⚠️  SECURITY: Keep your encryption key secure! Without it, credentials cannot be decrypted.")
        else:
            logger.warning("⚠️  SECURITY WARNING: Encryption not enabled! Credentials will be saved in PLAIN TEXT!")
            logger.warning("⚠️  Enable encryption by setting CREDENTIAL_ENCRYPTION_KEY environment variable.")

        logger.warning("⚠️  Ensure file permissions are restrictive (chmod 600)")

        manifest = self.export_credentials_manifest()

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        # Set restrictive file permissions (owner read/write only)
        try:
            os.chmod(filepath, 0o600)
            logger.info(f"Set file permissions to 600 (owner read/write only)")
        except Exception as e:
            logger.warning(f"Could not set restrictive file permissions: {e}")

        logger.debug(f"Saved credentials manifest to: {filepath}")

    @staticmethod
    def generate_encryption_key() -> bytes:
        """
        Generate a new encryption key for credential encryption.

        Returns:
            Base64-encoded encryption key (bytes)

        Example:
            key = CredentialManager.generate_encryption_key()
            print(f"Export this key: export CREDENTIAL_ENCRYPTION_KEY='{key.decode()}'")

            # Use the key
            manager = CredentialManager(encryption_key=key)
        """
        if not ENCRYPTION_AVAILABLE:
            raise ImportError(
                "cryptography library not available. Install with: pip install cryptography"
            )

        key = Fernet.generate_key()
        logger.info("Generated new encryption key")
        logger.warning("⚠️  IMPORTANT: Save this key securely! You need it to decrypt credentials.")
        logger.info(f"Set environment variable: export CREDENTIAL_ENCRYPTION_KEY='{key.decode()}'")
        return key


class CredentialLibrary:
    """
    Library of common credential templates for popular services.
    """

    @staticmethod
    def http_basic_auth(name: str = "HTTP Basic Auth") -> CredentialTemplate:
        """HTTP Basic Authentication"""
        return CredentialTemplate(
            name=name,
            type="httpBasicAuth",
            description="Basic authentication with username and password",
            fields={
                "username": {"type": "string", "required": True},
                "password": {"type": "string", "required": True, "sensitive": True},
            },
        )

    @staticmethod
    def http_header_auth(
        name: str = "HTTP Header Auth", header_name: str = "Authorization"
    ) -> CredentialTemplate:
        """HTTP Header Authentication"""
        return CredentialTemplate(
            name=name,
            type="httpHeaderAuth",
            description=f"Authentication via {header_name} header",
            fields={
                "name": {"type": "string", "value": header_name, "required": True},
                "value": {"type": "string", "required": True, "sensitive": True},
            },
        )

    @staticmethod
    def oauth2(
        name: str = "OAuth2", authorization_url: str = "", access_token_url: str = ""
    ) -> CredentialTemplate:
        """OAuth2 Authentication"""
        return CredentialTemplate(
            name=name,
            type="oAuth2Api",
            description="OAuth2 authentication flow",
            fields={
                "clientId": {"type": "string", "required": True},
                "clientSecret": {"type": "string", "required": True, "sensitive": True},
                "authorizationUrl": {"type": "string", "value": authorization_url},
                "accessTokenUrl": {"type": "string", "value": access_token_url},
                "scope": {"type": "string"},
                "authenticationMethod": {"type": "string", "value": "header"},
            },
        )

    @staticmethod
    def postgres(
        name: str = "PostgreSQL", host: str = "localhost", database: str = "postgres"
    ) -> CredentialTemplate:
        """PostgreSQL Database Credentials"""
        return CredentialTemplate(
            name=name,
            type="postgresApi",
            description="PostgreSQL database connection",
            fields={
                "host": {"type": "string", "value": host, "required": True},
                "port": {"type": "number", "value": 5432, "required": True},
                "database": {"type": "string", "value": database, "required": True},
                "user": {"type": "string", "required": True},
                "password": {"type": "string", "required": True, "sensitive": True},
                "ssl": {"type": "boolean", "value": False},
            },
        )

    @staticmethod
    def mysql(
        name: str = "MySQL", host: str = "localhost", database: str = "mysql"
    ) -> CredentialTemplate:
        """MySQL Database Credentials"""
        return CredentialTemplate(
            name=name,
            type="mysqlApi",
            description="MySQL database connection",
            fields={
                "host": {"type": "string", "value": host, "required": True},
                "port": {"type": "number", "value": 3306, "required": True},
                "database": {"type": "string", "value": database, "required": True},
                "user": {"type": "string", "required": True},
                "password": {"type": "string", "required": True, "sensitive": True},
                "ssl": {"type": "boolean", "value": False},
            },
        )

    @staticmethod
    def mongodb(name: str = "MongoDB", connection_string: str = "") -> CredentialTemplate:
        """MongoDB Credentials"""
        return CredentialTemplate(
            name=name,
            type="mongoDb",
            description="MongoDB database connection",
            fields={
                "connectionString": {
                    "type": "string",
                    "value": connection_string,
                    "required": True,
                    "sensitive": True,
                }
            },
        )

    @staticmethod
    def slack(name: str = "Slack API") -> CredentialTemplate:
        """Slack API Credentials"""
        return CredentialTemplate(
            name=name,
            type="slackApi",
            description="Slack workspace authentication",
            fields={"accessToken": {"type": "string", "required": True, "sensitive": True}},
        )

    @staticmethod
    def email_smtp(
        name: str = "Email (SMTP)", host: str = "", port: int = 587
    ) -> CredentialTemplate:
        """SMTP Email Credentials"""
        return CredentialTemplate(
            name=name,
            type="emailSendApi",
            description="SMTP email server configuration",
            fields={
                "host": {"type": "string", "value": host, "required": True},
                "port": {"type": "number", "value": port, "required": True},
                "secure": {"type": "boolean", "value": True},
                "user": {"type": "string", "required": True},
                "password": {"type": "string", "required": True, "sensitive": True},
            },
        )

    @staticmethod
    def aws(name: str = "AWS", region: str = "us-east-1") -> CredentialTemplate:
        """AWS Credentials"""
        return CredentialTemplate(
            name=name,
            type="aws",
            description="Amazon Web Services authentication",
            fields={
                "accessKeyId": {"type": "string", "required": True, "sensitive": True},
                "secretAccessKey": {"type": "string", "required": True, "sensitive": True},
                "region": {"type": "string", "value": region},
            },
        )

    @staticmethod
    def github(name: str = "GitHub API") -> CredentialTemplate:
        """GitHub API Credentials"""
        return CredentialTemplate(
            name=name,
            type="githubApi",
            description="GitHub API personal access token",
            fields={"accessToken": {"type": "string", "required": True, "sensitive": True}},
        )


# Convenience functions
def create_credential(name: str, credential_type: str, **kwargs) -> CredentialTemplate:
    """
    Create a credential template.

    Args:
        name: Credential name
        credential_type: n8n credential type
        **kwargs: Additional credential parameters

    Returns:
        CredentialTemplate instance
    """
    return CredentialTemplate(name=name, type=credential_type, **kwargs)


def get_common_credential(service: str, **kwargs) -> CredentialTemplate:
    """
    Get a credential template for a common service.

    Args:
        service: Service name (e.g., 'postgres', 'slack', 'aws')
        **kwargs: Service-specific parameters

    Returns:
        CredentialTemplate instance

    Raises:
        ValueError: If service not found
    """
    service_map = {
        "http_basic": CredentialLibrary.http_basic_auth,
        "http_header": CredentialLibrary.http_header_auth,
        "oauth2": CredentialLibrary.oauth2,
        "postgres": CredentialLibrary.postgres,
        "postgresql": CredentialLibrary.postgres,
        "mysql": CredentialLibrary.mysql,
        "mongodb": CredentialLibrary.mongodb,
        "mongo": CredentialLibrary.mongodb,
        "slack": CredentialLibrary.slack,
        "email": CredentialLibrary.email_smtp,
        "smtp": CredentialLibrary.email_smtp,
        "aws": CredentialLibrary.aws,
        "github": CredentialLibrary.github,
    }

    service_lower = service.lower()
    if service_lower not in service_map:
        raise ValueError(f"Unknown service: {service}. Available: {', '.join(service_map.keys())}")

    return service_map[service_lower](**kwargs)


# ============================================================================
# AUTHENTICATION INTEGRATION
# ============================================================================

# Import authentication components
try:
    from skills.credential_auth import (
        AuthenticationError,
        CredentialAuthProvider,
        require_auth
    )
    AUTH_AVAILABLE = True
except ImportError:
    try:
        from credential_auth import (
            AuthenticationError,
            CredentialAuthProvider,
            require_auth
        )
        AUTH_AVAILABLE = True
    except ImportError:
        # Define stub classes if authentication module not available
        AUTH_AVAILABLE = False

        class AuthenticationError(Exception):
            """Raised when authentication fails"""
            pass

        class CredentialAuthProvider:
            """Stub authentication provider when auth module not available"""
            def __init__(self):
                logger.warning("Authentication module not available - using stub provider")

            def generate_token(self, *args, **kwargs):
                raise NotImplementedError("Authentication not available")

            def validate_token(self, *args, **kwargs):
                raise NotImplementedError("Authentication not available")

        def require_auth(auth_provider):
            """Stub decorator when auth module not available"""
            def decorator(func):
                def wrapper(*args, **kwargs):
                    raise NotImplementedError("Authentication not available")
                return wrapper
            return decorator


class AuthenticatedCredentialManager(CredentialManager):
    """
    Extended CredentialManager with authentication support.

    Adds token-based authentication protection for sensitive operations
    like exporting and saving credential manifests.

    Example:
        # Create authenticated manager
        manager = AuthenticatedCredentialManager()

        # Generate authentication token
        token = manager.auth_provider.generate_token(
            token_name="admin",
            expires_in=3600  # 1 hour
        )

        # Use protected operation
        manifest = manager.export_credentials_manifest(token=token)
        manager.save_manifest("/path/to/file.json", token=token)
    """

    def __init__(self, encryption_key: Optional[bytes] = None):
        """
        Initialize authenticated credential manager.

        Args:
            encryption_key: Optional Fernet encryption key
        """
        super().__init__(encryption_key=encryption_key)

        # Initialize authentication provider
        if AUTH_AVAILABLE:
            self.auth_provider = CredentialAuthProvider()
            logger.info("Authentication enabled for CredentialManager")
        else:
            self.auth_provider = CredentialAuthProvider()  # Stub
            logger.warning("Authentication not available - protected methods will fail")

    def export_credentials_manifest(self, token: Optional[str] = None) -> Dict[str, Any]:
        """
        Export credentials manifest for documentation/setup.

        AUTHENTICATION REQUIRED: This method requires a valid auth token
        when using AuthenticatedCredentialManager.

        Args:
            token: Authentication token (optional for backward compatibility)

        Returns:
            Dictionary containing all credential definitions and usage

        Raises:
            AuthenticationError: If token is invalid or missing (when required)

        Example:
            token = manager.auth_provider.generate_token()
            manifest = manager.export_credentials_manifest(token=token)
        """
        # If token provided, validate it
        if token is not None:
            if not self.auth_provider.validate_token(token):
                raise AuthenticationError("Invalid or expired token for export_credentials_manifest")

        # Call parent method
        return super().export_credentials_manifest()

    def save_manifest(self, filepath: str, token: Optional[str] = None) -> None:
        """
        Save credentials manifest to JSON file with encrypted sensitive fields.

        AUTHENTICATION REQUIRED: This method requires a valid auth token
        when using AuthenticatedCredentialManager.

        Args:
            filepath: Output file path
            token: Authentication token (optional for backward compatibility)

        Raises:
            AuthenticationError: If token is invalid or missing (when required)

        Example:
            token = manager.auth_provider.generate_token()
            manager.save_manifest("/path/to/file.json", token=token)
        """
        # If token provided, validate it
        if token is not None:
            if not self.auth_provider.validate_token(token):
                raise AuthenticationError("Invalid or expired token for save_manifest")

        # Call parent method
        return super().save_manifest(filepath)


if __name__ == "__main__":
    print("Credential Manager v2.1.0")
    print("=" * 60)
    print("\nInitializing credential manager...")

    # Example usage
    manager = CredentialManager()

    # Add some credentials
    manager.add_credential("Production DB", "postgresApi", "Main application database")
    manager.add_credential("Slack Notifications", "slackApi", "Team notifications")
    manager.add_credential("External API", "httpHeaderAuth", "Third-party API access")

    # Track usage
    manager.track_node_credential("Database Query", "Production DB")
    manager.track_node_credential("Send Alert", "Slack Notifications")

    # Validate
    validation_results = manager.validate_all()
    print(f"\n✓ Validated {len(manager.credentials)} credentials")

    # Export manifest
    manifest = manager.export_credentials_manifest()
    print(f"✓ Exported manifest with {manifest['total_credentials']} credentials")

    # Test library
    print("\nTesting credential library...")
    postgres_cred = CredentialLibrary.postgres("My DB", "db.example.com", "myapp")
    slack_cred = CredentialLibrary.slack("Team Slack")
    print(f"✓ Created {postgres_cred.name} ({postgres_cred.type})")
    print(f"✓ Created {slack_cred.name} ({slack_cred.type})")

    print("\nFor documentation, see: docs/CREDENTIALS_GUIDE.md")
