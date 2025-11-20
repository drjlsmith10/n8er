"""
Credential Management for n8n Workflows

This module provides tools for managing credentials in n8n workflows,
including credential templates, placeholders, and reference tracking.

Author: Project Automata - Agent 5 (High Priority Features)
Version: 2.1.0
Created: 2025-11-20
Issue: #9 - Credential Management
"""

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


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

    def to_dict(self) -> Dict:
        """Convert to dictionary representation"""
        return asdict(self)

    def to_node_reference(self) -> Dict:
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
    credential lifecycle management.
    """

    def __init__(self):
        """Initialize credential manager"""
        self.credentials: Dict[str, CredentialTemplate] = {}
        self.node_credential_map: Dict[str, List[str]] = {}
        logger.debug("Initialized CredentialManager")

    def add_credential(
        self,
        name: str,
        credential_type: str,
        description: str = "",
        credential_id: Optional[str] = None,
        fields: Optional[Dict] = None,
        environment: str = "production",
    ) -> CredentialTemplate:
        """
        Add a credential template.

        Args:
            name: Credential name
            credential_type: n8n credential type
            description: Usage description
            credential_id: Optional existing credential UUID
            fields: Field definitions
            environment: Target environment

        Returns:
            Created CredentialTemplate
        """
        credential = CredentialTemplate(
            name=name,
            type=credential_type,
            description=description,
            credential_id=credential_id,
            fields=fields or {},
            environment=environment,
        )

        # Validate
        errors = credential.validate()
        if errors:
            logger.warning(f"Credential validation warnings: {', '.join(errors)}")

        self.credentials[name] = credential
        logger.debug(f"Added credential template: {name} ({credential_type})")

        return credential

    def get_credential(self, name: str) -> Optional[CredentialTemplate]:
        """Get credential template by name"""
        return self.credentials.get(name)

    def list_credentials(self, environment: Optional[str] = None) -> List[CredentialTemplate]:
        """
        List all credential templates.

        Args:
            environment: Optional filter by environment

        Returns:
            List of credential templates
        """
        if environment:
            return [c for c in self.credentials.values() if c.environment == environment]
        return list(self.credentials.values())

    def track_node_credential(self, node_name: str, credential_name: str) -> None:
        """
        Track which credentials are used by which nodes.

        Args:
            node_name: Name of node using credential
            credential_name: Name of credential being used
        """
        if node_name not in self.node_credential_map:
            self.node_credential_map[node_name] = []

        if credential_name not in self.node_credential_map[node_name]:
            self.node_credential_map[node_name].append(credential_name)
            logger.debug(f"Node '{node_name}' uses credential '{credential_name}'")

    def get_node_credentials(self, node_name: str) -> List[CredentialTemplate]:
        """
        Get all credentials used by a specific node.

        Args:
            node_name: Node name

        Returns:
            List of credential templates used by node
        """
        cred_names = self.node_credential_map.get(node_name, [])
        return [self.credentials[name] for name in cred_names if name in self.credentials]

    def get_workflow_credentials(self) -> List[CredentialTemplate]:
        """
        Get all credentials used in the workflow.

        Returns:
            List of all credential templates
        """
        return list(self.credentials.values())

    def generate_credential_reference(self, credential_name: str) -> Dict:
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

    def export_credentials_manifest(self) -> Dict:
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
        Save credentials manifest to JSON file.

        Args:
            filepath: Output file path
        """
        manifest = self.export_credentials_manifest()

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        logger.debug(f"Saved credentials manifest to: {filepath}")


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
