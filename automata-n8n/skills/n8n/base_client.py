"""
Base n8n API Client

Provides common HTTP functionality for all n8n API clients.
Implements session management, error handling, and rate limiting.

Author: Project Automata
Version: 2.0.0
"""

import logging
import time
from typing import Any, Dict, List, Optional

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class N8nApiError(Exception):
    """Base exception for n8n API errors"""
    pass


class N8nAuthenticationError(N8nApiError):
    """Raised when authentication fails"""
    pass


class N8nConnectionError(N8nApiError):
    """Raised when connection to n8n fails"""
    pass


class N8nValidationError(N8nApiError):
    """Raised when workflow validation fails"""
    pass


class N8nRateLimitError(N8nApiError):
    """Raised when rate limit is exceeded"""
    pass


class BaseN8nClient:
    """
    Base client providing common HTTP functionality.

    Features:
    - Session management with automatic cleanup
    - Retry logic for transient failures
    - Rate limiting
    - Error handling
    """

    def __init__(
        self,
        api_url: str,
        api_key: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        rate_limit_requests: int = 60,
        rate_limit_period: int = 60,
    ):
        """
        Initialize base n8n API client.

        Args:
            api_url: Base URL of n8n API
            api_key: n8n API key
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            rate_limit_requests: Max requests per period
            rate_limit_period: Rate limit period in seconds
        """
        # Clean up API URL
        self.base_url = api_url.rstrip("/")
        if self.base_url.endswith("/api/v1"):
            self.base_url = self.base_url[:-7]

        self.api_url = f"{self.base_url}/api/v1"
        self.api_key = api_key
        self.timeout = timeout

        # Rate limiting
        self.rate_limit_requests = rate_limit_requests
        self.rate_limit_period = rate_limit_period
        self._request_times: List[float] = []

        # Configure session
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            # Only retry idempotent methods
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Set headers
        self.session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json"
        })

        if self.api_key:
            self.session.headers.update({"X-N8N-API-KEY": self.api_key})

        logger.debug(f"Initialized base n8n client for {self.api_url}")

    def __enter__(self) -> "BaseN8nClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - closes session."""
        self.close()
        return None

    def close(self) -> None:
        """Close HTTP session and release resources."""
        if self.session:
            self.session.close()
            logger.debug("Closed n8n client session")

    def _check_rate_limit(self) -> None:
        """Check and enforce rate limiting."""
        now = time.time()
        self._request_times = [
            t for t in self._request_times
            if now - t < self.rate_limit_period
        ]

        if len(self._request_times) >= self.rate_limit_requests:
            oldest = self._request_times[0]
            wait_time = self.rate_limit_period - (now - oldest)
            if wait_time > 0:
                raise N8nRateLimitError(
                    f"Rate limit exceeded. Wait {wait_time:.2f}s before retrying."
                )

        self._request_times.append(now)

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to n8n API.

        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request body
            params: Query parameters

        Returns:
            Response JSON

        Raises:
            N8nAuthenticationError: Authentication failed
            N8nConnectionError: Connection failed
            N8nApiError: Other API errors
        """
        self._check_rate_limit()
        url = f"{self.api_url}/{endpoint.lstrip('/')}"

        try:
            logger.debug(f"{method} {url}")
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=self.timeout
            )

            if response.status_code == 401:
                raise N8nAuthenticationError("Authentication failed. Check API key.")

            if response.status_code == 429:
                raise N8nRateLimitError("Rate limit exceeded.")

            response.raise_for_status()

            if response.content:
                return response.json()
            return {}

        except requests.exceptions.Timeout:
            raise N8nConnectionError(f"Request timeout after {self.timeout}s")

        except requests.exceptions.ConnectionError as e:
            raise N8nConnectionError(f"Connection failed: {e}")

        except requests.exceptions.HTTPError:
            error_msg = f"HTTP {response.status_code}: {response.text}"
            logger.error(error_msg)
            raise N8nApiError(error_msg)

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise N8nApiError(f"Unexpected error: {e}")
