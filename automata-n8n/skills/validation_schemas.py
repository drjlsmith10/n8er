"""
Pydantic Validation Schemas for n8n Workflow Components

This module provides comprehensive input validation using pydantic for all n8n workflow
components including workflows, nodes, credentials, executions, and versions.

Author: Project Automata - Input Validation Specialist
Version: 1.0.0
Created: 2025-11-21

Features:
- String length validation (names ≤255, descriptions ≤2048, ids ≤128)
- Path traversal prevention (../, \\, etc)
- SQL injection pattern detection
- Control character filtering
- Semantic versioning validation
- Node type validation
- URL validation (http/https only)
"""

import re
from typing import Any, Dict, List, Optional, Set, Tuple
from pydantic import BaseModel, Field, field_validator, model_validator
from enum import Enum


# Known n8n node types for validation
KNOWN_NODE_TYPES = {
    # Triggers
    "n8n-nodes-base.webhook",
    "n8n-nodes-base.manualTrigger",
    "n8n-nodes-base.cron",
    "n8n-nodes-base.emailTrigger",
    "n8n-nodes-base.start",
    # Actions
    "n8n-nodes-base.httpRequest",
    "n8n-nodes-base.emailSend",
    "n8n-nodes-base.slack",
    "n8n-nodes-base.github",
    "n8n-nodes-base.mysql",
    "n8n-nodes-base.postgres",
    "n8n-nodes-base.mongodb",
    # Transform
    "n8n-nodes-base.set",
    "n8n-nodes-base.function",
    "n8n-nodes-base.code",
    "n8n-nodes-base.itemLists",
    # Logic
    "n8n-nodes-base.if",
    "n8n-nodes-base.switch",
    "n8n-nodes-base.merge",
    "n8n-nodes-base.splitInBatches",
    "n8n-nodes-base.noOp",
}

# SQL injection patterns to detect
SQL_INJECTION_PATTERNS = [
    r"(\bunion\b.*\bselect\b)",
    r"(\bdrop\b.*\btable\b)",
    r"(\binsert\b.*\binto\b)",
    r"(\bdelete\b.*\bfrom\b)",
    r"(\bupdate\b.*\bset\b)",
    r"(--\s*$)",
    r"(/\*.*\*/)",
    r"(\bor\b\s+\d+\s*=\s*\d+)",
    r"(\band\b\s+\d+\s*=\s*\d+)",
    r"(;\s*(drop|delete|update|insert))",
]

# Path traversal patterns
PATH_TRAVERSAL_PATTERNS = [
    r"\.\./",
    r"\.\.",
    r"\\\\",
    r"%2e%2e",
    r"%252e%252e",
]


class ExecutionOrder(str, Enum):
    """Valid n8n execution order values"""
    V0 = "v0"
    V1 = "v1"


class CallerPolicy(str, Enum):
    """Valid n8n caller policy values"""
    ANY = "any"
    WORKFLOWS_FROM_SAME_OWNER = "workflowsFromSameOwner"
    WORKFLOWS_FROM_LIST = "workflowsFromAList"
    NONE = "none"


# Validation Helper Functions
def validate_no_control_chars(value: str, field_name: str) -> str:
    """
    Validate that string contains no control characters.

    Args:
        value: String to validate
        field_name: Name of field for error messages

    Returns:
        Original value if valid

    Raises:
        ValueError: If control characters found
    """
    # Control characters are 0x00-0x1F (except \t, \n, \r) and 0x7F
    control_chars = [chr(i) for i in range(32) if i not in (9, 10, 13)] + [chr(127)]

    for char in control_chars:
        if char in value:
            raise ValueError(
                f"{field_name} contains control character: 0x{ord(char):02x}. "
                "Control characters are not allowed."
            )

    return value


def validate_no_path_traversal(value: str, field_name: str) -> str:
    """
    Validate that string contains no path traversal sequences.

    Args:
        value: String to validate
        field_name: Name of field for error messages

    Returns:
        Original value if valid

    Raises:
        ValueError: If path traversal patterns found
    """
    for pattern in PATH_TRAVERSAL_PATTERNS:
        if re.search(pattern, value, re.IGNORECASE):
            raise ValueError(
                f"{field_name} contains path traversal pattern: {pattern}. "
                "Path traversal sequences are not allowed for security."
            )

    return value


def validate_no_sql_injection(value: str, field_name: str) -> str:
    """
    Validate that string contains no SQL injection patterns.

    Args:
        value: String to validate
        field_name: Name of field for error messages

    Returns:
        Original value if valid

    Raises:
        ValueError: If SQL injection patterns found
    """
    for pattern in SQL_INJECTION_PATTERNS:
        if re.search(pattern, value, re.IGNORECASE):
            raise ValueError(
                f"{field_name} contains potential SQL injection pattern: {pattern}. "
                "SQL keywords and patterns are not allowed."
            )

    return value


def validate_string_security(value: str, field_name: str, allow_sql: bool = False) -> str:
    """
    Comprehensive string security validation.

    Args:
        value: String to validate
        field_name: Name of field for error messages
        allow_sql: If True, skip SQL injection check

    Returns:
        Original value if valid

    Raises:
        ValueError: If validation fails
    """
    if not isinstance(value, str):
        return value

    # Check control characters
    validate_no_control_chars(value, field_name)

    # Check path traversal
    validate_no_path_traversal(value, field_name)

    # Check SQL injection (unless explicitly allowed, e.g., for SQL query parameters)
    if not allow_sql:
        validate_no_sql_injection(value, field_name)

    return value


# Pydantic Models

class WorkflowSettingsInput(BaseModel):
    """Workflow settings validation"""
    executionOrder: ExecutionOrder = Field(default=ExecutionOrder.V1)
    saveExecutionProgress: bool = Field(default=False)
    saveManualExecutions: bool = Field(default=True)
    timezone: str = Field(default="UTC", max_length=64)
    callerPolicy: CallerPolicy = Field(default=CallerPolicy.WORKFLOWS_FROM_SAME_OWNER)

    @field_validator('timezone')
    @classmethod
    def validate_timezone(cls, v: str) -> str:
        """Validate timezone string"""
        if not v:
            raise ValueError("Timezone cannot be empty")

        # Basic validation - check for control characters and path traversal
        validate_string_security(v, "timezone")

        return v

    class Config:
        use_enum_values = True


class NodePositionInput(BaseModel):
    """Node position validation"""
    x: float = Field(ge=-10000, le=10000)
    y: float = Field(ge=-10000, le=10000)

    @model_validator(mode='after')
    def validate_position(self) -> 'NodePositionInput':
        """Validate position values are reasonable"""
        if self.x == 0 and self.y == 0:
            raise ValueError("Node position cannot be (0, 0) - this may cause rendering issues")
        return self


class NodeInput(BaseModel):
    """
    Validation schema for n8n workflow nodes.

    Validates:
    - Node name, type, and parameters
    - String lengths and security
    - Node type validity
    - Type version constraints
    """
    name: str = Field(..., min_length=1, max_length=255)
    type: str = Field(..., min_length=1, max_length=255)
    typeVersion: int = Field(default=1, ge=1, le=10)
    position: List[float] = Field(..., min_length=2, max_length=2)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    credentials: Optional[Dict[str, Any]] = None
    disabled: bool = Field(default=False)
    notes: str = Field(default="", max_length=2048)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate node name"""
        if not v.strip():
            raise ValueError("Node name cannot be empty or whitespace")

        # Security validation
        validate_string_security(v, "name")

        return v.strip()

    @field_validator('type')
    @classmethod
    def validate_type(cls, v: str) -> str:
        """Validate node type"""
        if not v.strip():
            raise ValueError("Node type cannot be empty")

        # Security validation
        validate_string_security(v, "type")

        # Check if it's a known type or follows n8n naming convention
        if v not in KNOWN_NODE_TYPES and not v.startswith("n8n-nodes-"):
            raise ValueError(
                f"Unknown node type: {v}. Must be a known n8n node type or "
                "start with 'n8n-nodes-' prefix."
            )

        return v

    @field_validator('notes')
    @classmethod
    def validate_notes(cls, v: str) -> str:
        """Validate node notes"""
        if v:
            validate_string_security(v, "notes")
        return v

    @field_validator('position')
    @classmethod
    def validate_position(cls, v: List[float]) -> List[float]:
        """Validate position array"""
        if len(v) != 2:
            raise ValueError("Position must be [x, y] with exactly 2 coordinates")

        x, y = v
        if not (-10000 <= x <= 10000) or not (-10000 <= y <= 10000):
            raise ValueError("Position coordinates must be between -10000 and 10000")

        return v


class ConnectionInput(BaseModel):
    """Validation schema for node connections"""
    source_node: str = Field(..., min_length=1, max_length=255)
    target_node: str = Field(..., min_length=1, max_length=255)
    source_output: int = Field(default=0, ge=0, le=100)
    target_input: int = Field(default=0, ge=0, le=100)
    connection_type: str = Field(default="main", max_length=64)

    @field_validator('source_node', 'target_node')
    @classmethod
    def validate_node_names(cls, v: str) -> str:
        """Validate node names in connections"""
        validate_string_security(v, "node_name")
        return v

    @field_validator('connection_type')
    @classmethod
    def validate_connection_type(cls, v: str) -> str:
        """Validate connection type"""
        validate_string_security(v, "connection_type")

        # Valid connection types in n8n
        valid_types = {"main", "ai_tool", "ai_chain", "ai_languageModel"}
        if v not in valid_types:
            raise ValueError(
                f"Invalid connection type: {v}. Must be one of {valid_types}"
            )

        return v

    @model_validator(mode='after')
    def validate_not_self_connection(self) -> 'ConnectionInput':
        """Prevent self-connections"""
        if self.source_node == self.target_node:
            raise ValueError(
                f"Self-connection detected: {self.source_node} -> {self.target_node}. "
                "Nodes cannot connect to themselves."
            )
        return self


class WorkflowInput(BaseModel):
    """
    Validation schema for n8n workflows.

    Validates:
    - Workflow name and metadata
    - Nodes and connections
    - Settings and configuration
    - String security and lengths
    """
    name: str = Field(..., min_length=1, max_length=255)
    nodes: List[NodeInput] = Field(..., min_length=1)
    connections: Dict[str, Any] = Field(default_factory=dict)
    settings: Optional[WorkflowSettingsInput] = Field(default_factory=WorkflowSettingsInput)
    active: bool = Field(default=False)
    tags: List[str] = Field(default_factory=list, max_length=50)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate workflow name"""
        if not v.strip():
            raise ValueError("Workflow name cannot be empty or whitespace")

        # Security validation
        validate_string_security(v, "name")

        return v.strip()

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: List[str]) -> List[str]:
        """Validate workflow tags"""
        validated_tags = []
        for tag in v:
            if not tag or not tag.strip():
                raise ValueError("Tag cannot be empty or whitespace")

            if len(tag) > 128:
                raise ValueError(f"Tag too long: {len(tag)} chars. Maximum 128 characters allowed")

            # Security validation
            validate_string_security(tag, "tag")
            validated_tags.append(tag.strip())

        return validated_tags

    @model_validator(mode='after')
    def validate_workflow_structure(self) -> 'WorkflowInput':
        """Validate workflow has at least one trigger node"""
        trigger_keywords = ['trigger', 'webhook', 'cron', 'manual', 'start']
        has_trigger = any(
            any(keyword in node.type.lower() for keyword in trigger_keywords)
            for node in self.nodes
        )

        if not has_trigger:
            raise ValueError(
                "Workflow must have at least one trigger node (webhook, cron, manual, etc.)"
            )

        return self


class CredentialInput(BaseModel):
    """
    Validation schema for n8n credentials.

    Validates:
    - Credential name, type, and data
    - String security and lengths
    - Credential type validity
    """
    name: str = Field(..., min_length=1, max_length=255)
    type: str = Field(..., min_length=1, max_length=255)
    data: Dict[str, Any] = Field(default_factory=dict)
    description: str = Field(default="", max_length=2048)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate credential name"""
        if not v.strip():
            raise ValueError("Credential name cannot be empty or whitespace")

        # Security validation
        validate_string_security(v, "name")

        return v.strip()

    @field_validator('type')
    @classmethod
    def validate_type(cls, v: str) -> str:
        """Validate credential type"""
        if not v.strip():
            raise ValueError("Credential type cannot be empty")

        # Security validation
        validate_string_security(v, "type")

        # Known credential types
        known_types = {
            "httpBasicAuth", "httpDigestAuth", "httpHeaderAuth", "oAuth2Api",
            "slackApi", "googleApi", "postgresApi", "mysqlApi", "mongoDb",
            "aws", "githubApi", "telegramApi", "discordApi", "emailSendApi",
            "sshPassword", "sshPrivateKey", "ftpApi", "httpQueryAuth"
        }

        if v not in known_types and not v.endswith("Api"):
            raise ValueError(
                f"Unknown credential type: {v}. Must be a known type or end with 'Api'"
            )

        return v

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Validate credential description"""
        if v:
            validate_string_security(v, "description")
        return v


class ExecutionInput(BaseModel):
    """
    Validation schema for workflow executions.

    Validates:
    - Workflow ID
    - Execution data
    - String security
    """
    workflowId: str = Field(..., min_length=1, max_length=128)
    data: Optional[Dict[str, Any]] = None
    mode: str = Field(default="manual", max_length=64)

    @field_validator('workflowId')
    @classmethod
    def validate_workflow_id(cls, v: str) -> str:
        """Validate workflow ID"""
        if not v.strip():
            raise ValueError("Workflow ID cannot be empty")

        # Security validation
        validate_string_security(v, "workflowId")

        # Check if it looks like a valid UUID or ID format
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError(
                f"Invalid workflow ID format: {v}. Must contain only alphanumeric, "
                "underscore, and hyphen characters."
            )

        return v

    @field_validator('mode')
    @classmethod
    def validate_mode(cls, v: str) -> str:
        """Validate execution mode"""
        validate_string_security(v, "mode")

        valid_modes = {"manual", "trigger", "webhook", "retry"}
        if v not in valid_modes:
            raise ValueError(
                f"Invalid execution mode: {v}. Must be one of {valid_modes}"
            )

        return v


class VersionInput(BaseModel):
    """
    Validation schema for semantic versions.

    Validates:
    - Semantic versioning format (MAJOR.MINOR.PATCH)
    - Version component constraints
    """
    version: str = Field(..., min_length=5, max_length=32)

    @field_validator('version')
    @classmethod
    def validate_semantic_version(cls, v: str) -> str:
        """
        Validate semantic version format.

        Format: MAJOR.MINOR.PATCH
        Example: 1.2.3, 10.0.5, 2.1.0
        """
        if not v.strip():
            raise ValueError("Version cannot be empty")

        # Security validation
        validate_string_security(v, "version")

        # Validate semantic versioning format
        pattern = r'^(\d+)\.(\d+)\.(\d+)$'
        match = re.match(pattern, v)

        if not match:
            raise ValueError(
                f"Invalid semantic version: {v}. Must follow MAJOR.MINOR.PATCH format "
                "(e.g., 1.2.3)"
            )

        # Extract components
        major, minor, patch = map(int, match.groups())

        # Validate component ranges
        if major > 999:
            raise ValueError(f"Major version too large: {major}. Maximum is 999")
        if minor > 999:
            raise ValueError(f"Minor version too large: {minor}. Maximum is 999")
        if patch > 9999:
            raise ValueError(f"Patch version too large: {patch}. Maximum is 9999")

        return v

    def get_components(self) -> Tuple[int, int, int]:
        """Extract version components as (major, minor, patch)"""
        match = re.match(r'^(\d+)\.(\d+)\.(\d+)$', self.version)
        if match:
            return tuple(map(int, match.groups()))
        raise ValueError(f"Invalid version format: {self.version}")


class UrlInput(BaseModel):
    """
    Validation schema for URLs.

    Validates:
    - URL format
    - Protocol (http/https only)
    - No malicious patterns
    """
    url: str = Field(..., min_length=1, max_length=2048)

    @field_validator('url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate URL format and security"""
        if not v.strip():
            raise ValueError("URL cannot be empty")

        # Basic security validation
        validate_string_security(v, "url")

        # Check protocol
        if not v.startswith(('http://', 'https://')):
            raise ValueError(
                f"Invalid URL protocol: {v}. Only http:// and https:// are allowed"
            )

        # Check for localhost/internal IPs (optional security check)
        internal_patterns = [
            r'localhost',
            r'127\.0\.0\.1',
            r'0\.0\.0\.0',
            r'::1',
            r'192\.168\.',
            r'10\.',
            r'172\.(1[6-9]|2[0-9]|3[0-1])\.',
        ]

        for pattern in internal_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                # This is a warning, not an error - may be valid in dev environments
                pass

        return v


class ApiKeyInput(BaseModel):
    """
    Validation schema for API keys.

    Validates:
    - Key format
    - Length constraints
    - No malicious patterns
    """
    api_key: str = Field(..., min_length=8, max_length=512)

    @field_validator('api_key')
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Validate API key format"""
        if not v.strip():
            raise ValueError("API key cannot be empty")

        # Security validation (but allow more characters for keys)
        validate_no_control_chars(v, "api_key")
        validate_no_path_traversal(v, "api_key")

        # Check for common dummy/test keys that should not be used
        dummy_keys = ["test", "dummy", "placeholder", "example", "your-api-key"]
        if any(dummy in v.lower() for dummy in dummy_keys):
            raise ValueError(
                f"API key appears to be a placeholder: {v}. Please use a real API key"
            )

        return v


# Convenience validation functions
def validate_workflow(workflow_data: Dict[str, Any]) -> WorkflowInput:
    """
    Validate workflow data.

    Args:
        workflow_data: Workflow dictionary

    Returns:
        Validated WorkflowInput instance

    Raises:
        ValueError: If validation fails
    """
    return WorkflowInput(**workflow_data)


def validate_node(node_data: Dict[str, Any]) -> NodeInput:
    """
    Validate node data.

    Args:
        node_data: Node dictionary

    Returns:
        Validated NodeInput instance

    Raises:
        ValueError: If validation fails
    """
    return NodeInput(**node_data)


def validate_credential(cred_data: Dict[str, Any]) -> CredentialInput:
    """
    Validate credential data.

    Args:
        cred_data: Credential dictionary

    Returns:
        Validated CredentialInput instance

    Raises:
        ValueError: If validation fails
    """
    return CredentialInput(**cred_data)


def validate_execution(exec_data: Dict[str, Any]) -> ExecutionInput:
    """
    Validate execution data.

    Args:
        exec_data: Execution dictionary

    Returns:
        Validated ExecutionInput instance

    Raises:
        ValueError: If validation fails
    """
    return ExecutionInput(**exec_data)


def validate_version(version_str: str) -> VersionInput:
    """
    Validate version string.

    Args:
        version_str: Version string

    Returns:
        Validated VersionInput instance

    Raises:
        ValueError: If validation fails
    """
    return VersionInput(version=version_str)


def validate_url(url_str: str) -> UrlInput:
    """
    Validate URL string.

    Args:
        url_str: URL string

    Returns:
        Validated UrlInput instance

    Raises:
        ValueError: If validation fails
    """
    return UrlInput(url=url_str)


if __name__ == "__main__":
    print("Pydantic Validation Schemas v1.0.0")
    print("=" * 60)

    # Example: Validate a workflow
    workflow_data = {
        "name": "Test Workflow",
        "nodes": [
            {
                "name": "Start",
                "type": "n8n-nodes-base.manualTrigger",
                "position": [240, 300],
                "parameters": {},
            }
        ],
        "connections": {},
    }

    try:
        validated = validate_workflow(workflow_data)
        print(f"✓ Workflow validated: {validated.name} ({len(validated.nodes)} nodes)")
    except ValueError as e:
        print(f"✗ Validation failed: {e}")

    # Example: Validate a version
    try:
        version = validate_version("1.2.3")
        print(f"✓ Version validated: {version.version}")
        major, minor, patch = version.get_components()
        print(f"  Components: {major}.{minor}.{patch}")
    except ValueError as e:
        print(f"✗ Version validation failed: {e}")

    # Example: Test security validation
    try:
        # This should fail - path traversal
        malicious_workflow = {
            "name": "../../etc/passwd",
            "nodes": [{"name": "Test", "type": "n8n-nodes-base.start", "position": [0, 0]}],
        }
        validate_workflow(malicious_workflow)
        print("✗ Security validation failed - should have caught path traversal")
    except ValueError as e:
        print(f"✓ Security validation working: {e}")

    print("\nFor documentation, see module docstring")
