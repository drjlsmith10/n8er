"""
Project Automata: Centralized Configuration Management

Loads configuration from environment variables with sensible defaults.
Uses python-dotenv to load from .env file.

Author: Project Automata
Version: 2.0.0
"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load .env file if it exists
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)


class Config:
    """Central configuration class"""

    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    # Paths
    BASE_DIR: Path = Path(__file__).parent
    KNOWLEDGE_BASE_DIR: Path = BASE_DIR / os.getenv("KNOWLEDGE_BASE_DIR", "knowledge_base")
    WORKFLOWS_DIR: Path = BASE_DIR / os.getenv("WORKFLOWS_DIR", "workflows")
    LOGS_DIR: Path = BASE_DIR / os.getenv("LOGS_DIR", "logs")

    # API Keys (optional)
    REDDIT_CLIENT_ID: Optional[str] = os.getenv("REDDIT_CLIENT_ID")
    REDDIT_CLIENT_SECRET: Optional[str] = os.getenv("REDDIT_CLIENT_SECRET")
    REDDIT_USER_AGENT: str = os.getenv("REDDIT_USER_AGENT", "ProjectAutomata/2.0")

    YOUTUBE_API_KEY: Optional[str] = os.getenv("YOUTUBE_API_KEY")

    TWITTER_API_KEY: Optional[str] = os.getenv("TWITTER_API_KEY")
    TWITTER_API_SECRET: Optional[str] = os.getenv("TWITTER_API_SECRET")
    TWITTER_ACCESS_TOKEN: Optional[str] = os.getenv("TWITTER_ACCESS_TOKEN")
    TWITTER_ACCESS_SECRET: Optional[str] = os.getenv("TWITTER_ACCESS_SECRET")

    GITHUB_TOKEN: Optional[str] = os.getenv("GITHUB_TOKEN")

    # n8n Integration
    N8N_API_URL: str = os.getenv("N8N_API_URL", "http://localhost:5678/api/v1")
    N8N_API_KEY: Optional[str] = os.getenv("N8N_API_KEY")

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "text")

    # Feature Flags
    ENABLE_WEB_RESEARCH: bool = os.getenv("ENABLE_WEB_RESEARCH", "false").lower() == "true"
    ENABLE_CACHING: bool = os.getenv("ENABLE_CACHING", "true").lower() == "true"
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "false").lower() == "true"

    # Simulation Mode - MUST be explicitly enabled to use built-in sample data
    # When False (default), APIs must be configured or operations will fail
    ALLOW_SIMULATED_DATA: bool = os.getenv("ALLOW_SIMULATED_DATA", "false").lower() == "true"

    # Workflow Size Limits
    MAX_WORKFLOW_NODES: int = int(os.getenv("MAX_WORKFLOW_NODES", "100"))
    MAX_WORKFLOW_COMPLEXITY: int = int(
        os.getenv("MAX_WORKFLOW_COMPLEXITY", "500")
    )  # Sum of node count + connection count
    WARN_WORKFLOW_NODES: int = int(os.getenv("WARN_WORKFLOW_NODES", "50"))
    WARN_WORKFLOW_COMPLEXITY: int = int(os.getenv("WARN_WORKFLOW_COMPLEXITY", "300"))

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", "60"))

    # Security
    SECRET_KEY: Optional[str] = os.getenv("SECRET_KEY")
    ALLOWED_HOSTS: list = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

    @classmethod
    def ensure_directories(cls):
        """Create required directories if they don't exist"""
        cls.KNOWLEDGE_BASE_DIR.mkdir(exist_ok=True)
        cls.WORKFLOWS_DIR.mkdir(exist_ok=True)
        cls.LOGS_DIR.mkdir(exist_ok=True)

    @classmethod
    def validate_n8n_connection(cls) -> tuple[bool, str]:
        """
        Validate n8n API connection if configured.

        Returns:
            Tuple of (success: bool, message: str)
        """
        if not cls.N8N_API_URL:
            return False, "N8N_API_URL not configured"

        if not cls.N8N_API_KEY:
            return False, "N8N_API_KEY not configured"

        try:
            # Import here to avoid circular dependency
            from skills.n8n_api_client import N8nApiClient

            client = N8nApiClient(api_url=cls.N8N_API_URL, api_key=cls.N8N_API_KEY)
            return client.test_connection()
        except ImportError:
            return False, "n8n_api_client module not available"
        except Exception as e:
            return False, f"Connection test failed: {str(e)}"

    @classmethod
    def validate(cls) -> list:
        """
        Validate configuration and return list of warnings/errors

        Returns:
            List of validation messages
        """
        messages = []

        # Check production requirements
        if cls.ENVIRONMENT == "production":
            if not cls.SECRET_KEY or len(cls.SECRET_KEY) < 32:
                messages.append("ERROR: SECRET_KEY must be at least 32 characters in production")

            if cls.DEBUG:
                messages.append("WARNING: DEBUG should be false in production")

            # Warn if web research disabled in production
            if not cls.ENABLE_WEB_RESEARCH:
                messages.append(
                    "WARNING: ENABLE_WEB_RESEARCH=false in production - using SIMULATED data"
                )

        # Check API keys if web research enabled
        if cls.ENABLE_WEB_RESEARCH:
            if not cls.REDDIT_CLIENT_ID:
                messages.append(
                    "WARNING: REDDIT_CLIENT_ID not set, Reddit research will use SIMULATED data"
                )

            if not cls.YOUTUBE_API_KEY:
                messages.append(
                    "WARNING: YOUTUBE_API_KEY not set, YouTube research will use SIMULATED data"
                )

            if not cls.TWITTER_API_KEY:
                messages.append(
                    "WARNING: TWITTER_API_KEY not set, Twitter research will use SIMULATED data"
                )
        else:
            # Prominently warn about simulation mode
            messages.append(
                "⚠️  SIMULATION MODE: ENABLE_WEB_RESEARCH=false - All web research uses SIMULATED data"
            )
            messages.append("   Set ENABLE_WEB_RESEARCH=true and configure API keys for real data")

        # Check n8n API configuration
        if cls.N8N_API_URL:
            # Validate URL format
            if not cls.N8N_API_URL.startswith(("http://", "https://")):
                messages.append("ERROR: N8N_API_URL must start with http:// or https://")

            # Warn if API key not set
            if not cls.N8N_API_KEY:
                messages.append("WARNING: N8N_API_KEY not set, n8n API integration will not work")

            # Check if localhost in production
            if cls.ENVIRONMENT == "production" and "localhost" in cls.N8N_API_URL:
                messages.append("WARNING: N8N_API_URL uses localhost in production environment")
        else:
            messages.append("INFO: N8N_API_URL not set, n8n integration features disabled")

        return messages

    @classmethod
    def get_summary(cls) -> str:
        """Get configuration summary (safe for logging)"""
        return f"""
Project Automata Configuration
==============================
Environment: {cls.ENVIRONMENT}
Debug: {cls.DEBUG}

Paths:
  Base: {cls.BASE_DIR}
  Knowledge Base: {cls.KNOWLEDGE_BASE_DIR}
  Workflows: {cls.WORKFLOWS_DIR}
  Logs: {cls.LOGS_DIR}

Features:
  Web Research: {cls.ENABLE_WEB_RESEARCH}
  Caching: {cls.ENABLE_CACHING}
  Metrics: {cls.ENABLE_METRICS}

Workflow Limits:
  Max Nodes: {cls.MAX_WORKFLOW_NODES}
  Max Complexity: {cls.MAX_WORKFLOW_COMPLEXITY}
  Warn at Nodes: {cls.WARN_WORKFLOW_NODES}
  Warn at Complexity: {cls.WARN_WORKFLOW_COMPLEXITY}

APIs Configured:
  Reddit: {'✓' if cls.REDDIT_CLIENT_ID else '✗'}
  YouTube: {'✓' if cls.YOUTUBE_API_KEY else '✗'}
  Twitter: {'✓' if cls.TWITTER_API_KEY else '✗'}
  GitHub: {'✓' if cls.GITHUB_TOKEN else '✗'}
  n8n: {'✓' if cls.N8N_API_KEY else '✗'} ({cls.N8N_API_URL if cls.N8N_API_URL else 'not configured'})

Rate Limiting:
  Enabled: {cls.RATE_LIMIT_ENABLED}
  Requests/min: {cls.RATE_LIMIT_REQUESTS_PER_MINUTE}
"""


# Create config instance
config = Config()

# Ensure directories exist
config.ensure_directories()


if __name__ == "__main__":
    # Print configuration summary
    print(config.get_summary())

    # Validate configuration
    messages = config.validate()
    if messages:
        print("\nConfiguration Validation:")
        for msg in messages:
            print(f"  {msg}")
    else:
        print("\n✓ Configuration valid")
