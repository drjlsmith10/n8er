"""
Authentication Layer for Credential Manager

Provides token-based authentication for protecting sensitive credential operations.

Author: Security Team
Version: 1.0.0
Date: 2025-11-21
"""

import logging
import secrets
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    """Raised when authentication fails"""
    pass


class CredentialAuthProvider:
    """
    Token-based authentication provider for credential operations.

    Provides secure token generation and validation for protecting
    sensitive credential operations.

    Security Features:
    - Cryptographically secure token generation using secrets.token_urlsafe()
    - Token expiration support
    - Token revocation
    - Multiple token support for different access levels

    Example:
        auth_provider = CredentialAuthProvider()
        token = auth_provider.generate_token()

        # Later, validate token
        if auth_provider.validate_token(token):
            # Perform protected operation
            pass
    """

    def __init__(self):
        """Initialize authentication provider with empty token store"""
        self._valid_tokens: Dict[str, Dict[str, Any]] = {}
        logger.debug("Initialized CredentialAuthProvider")

    def generate_token(
        self,
        token_name: str = "default",
        expires_in: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a new authentication token.

        Args:
            token_name: Human-readable token identifier
            expires_in: Token expiration time in seconds (None = no expiration)
            metadata: Optional metadata to associate with token

        Returns:
            Secure random token string (URL-safe, 43 characters)

        Example:
            token = auth_provider.generate_token(
                token_name="admin_token",
                expires_in=3600,  # 1 hour
                metadata={"user": "admin", "scope": "full"}
            )
        """
        # Generate cryptographically secure random token
        token = secrets.token_urlsafe(32)

        # Store token with metadata
        token_data = {
            "name": token_name,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "expires_in": expires_in,
            "metadata": metadata or {}
        }

        if expires_in:
            expiry = datetime.utcnow().timestamp() + expires_in
            token_data["expires_at"] = expiry

        self._valid_tokens[token] = token_data

        logger.info(f"Generated authentication token: {token_name}")
        if expires_in:
            logger.debug(f"Token expires in {expires_in} seconds")

        return token

    def validate_token(self, token: str) -> bool:
        """
        Validate an authentication token.

        Args:
            token: Token to validate

        Returns:
            True if token is valid and not expired, False otherwise
        """
        if not token or token not in self._valid_tokens:
            logger.warning("Invalid token provided")
            return False

        token_data = self._valid_tokens[token]

        # Check expiration
        if "expires_at" in token_data:
            if datetime.utcnow().timestamp() > token_data["expires_at"]:
                logger.warning(f"Token '{token_data['name']}' has expired")
                # Remove expired token
                del self._valid_tokens[token]
                return False

        return True

    def revoke_token(self, token: str) -> bool:
        """
        Revoke an authentication token.

        Args:
            token: Token to revoke

        Returns:
            True if token was revoked, False if token didn't exist
        """
        if token in self._valid_tokens:
            token_name = self._valid_tokens[token].get("name", "unknown")
            del self._valid_tokens[token]
            logger.info(f"Revoked authentication token: {token_name}")
            return True

        return False

    def revoke_all_tokens(self) -> int:
        """
        Revoke all authentication tokens.

        Returns:
            Number of tokens revoked
        """
        count = len(self._valid_tokens)
        self._valid_tokens.clear()
        logger.info(f"Revoked all authentication tokens ({count} tokens)")
        return count

    def list_tokens(self) -> List[Dict[str, Any]]:
        """
        List all active tokens (without exposing the actual token values).

        Returns:
            List of token metadata (excludes actual token strings)
        """
        return [
            {
                "name": data["name"],
                "created_at": data["created_at"],
                "expires_in": data.get("expires_in"),
                "metadata": data.get("metadata", {})
            }
            for data in self._valid_tokens.values()
        ]


def require_auth(auth_provider: CredentialAuthProvider):
    """
    Decorator to require authentication for credential operations.

    Args:
        auth_provider: CredentialAuthProvider instance to use for validation

    Returns:
        Decorator function

    Example:
        auth_provider = CredentialAuthProvider()

        @require_auth(auth_provider)
        def protected_operation(self, token: str):
            # This will only execute if token is valid
            return "Success"

    Usage:
        token = auth_provider.generate_token()
        result = obj.protected_operation(token=token)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract token from kwargs
            token = kwargs.get('token') or kwargs.get('auth_token')

            if not token:
                raise AuthenticationError(
                    f"Authentication required for {func.__name__}. "
                    f"Provide 'token' or 'auth_token' parameter."
                )

            # Validate token
            if not auth_provider.validate_token(token):
                raise AuthenticationError(
                    f"Invalid or expired authentication token for {func.__name__}"
                )

            # Remove token from kwargs before calling function
            # (so it doesn't interfere with function signature)
            kwargs_copy = kwargs.copy()
            kwargs_copy.pop('token', None)
            kwargs_copy.pop('auth_token', None)

            return func(*args, **kwargs_copy)

        return wrapper
    return decorator
