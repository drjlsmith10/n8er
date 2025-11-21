"""
Base n8n API Client

Provides shared functionality for all specialized clients:
- HTTP request handling
- Rate limiting
- Session management
- Error handling

Author: Project Automata - Architecture Specialist
Version: 2.0.0
Created: 2025-11-21
"""

import logging
import time
from typing import Any, Dict, List, Optional

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Configure logging
logger = logging.getLogger(__name__)


# Exception classes (shared across all clients)
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
    Base client providing shared HTTP and session management.

    This class handles:
    - Session configuration with retry logic
    - Rate limiting
    - HTTP request handling with error handling
    - Authentication

    Specialized clients inherit from this to get HTTP capabilities.
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
        Initialize base n8n client.

        Args:
            api_url: Base URL of n8n API (e.g., "http://localhost:5678")
            api_key: n8n API key (from Settings > n8n API)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            rate_limit_requests: Maximum requests per period
            rate_limit_period: Rate limit period in seconds
        """
        # Clean up API URL - remove trailing slash and /api/v1 if present
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

        # Configure session with retry logic
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST", "PATCH"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Set default headers
        self.session.headers.update(
            {"Accept": "application/json", "Content-Type": "application/json"}
        )

        if self.api_key:
            self.session.headers.update({"X-N8N-API-KEY": self.api_key})

        logger.debug(f"Initialized base n8n client for {self.api_url}")

    def _check_rate_limit(self):
        """Check and enforce rate limiting."""
        now = time.time()

        # Remove requests outside the current period
        self._request_times = [t for t in self._request_times if now - t < self.rate_limit_period]

        # Check if we've exceeded the limit
        if len(self._request_times) >= self.rate_limit_requests:
            oldest_request = self._request_times[0]
            wait_time = self.rate_limit_period - (now - oldest_request)
            if wait_time > 0:
                logger.warning(f"Rate limit reached, waiting {wait_time:.2f}s")
                raise N8nRateLimitError(
                    f"Rate limit exceeded. Wait {wait_time:.2f}s before retrying."
                )

        # Record this request
        self._request_times.append(now)

    def _request(
        self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to n8n API with error handling.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, PATCH)
            endpoint: API endpoint (without /api/v1 prefix)
            data: Request body data
            params: Query parameters

        Returns:
            Response JSON data

        Raises:
            N8nAuthenticationError: If authentication fails
            N8nConnectionError: If connection fails
            N8nApiError: For other API errors
        """
        self._check_rate_limit()

        url = f"{self.api_url}/{endpoint.lstrip('/')}"

        try:
            logger.debug(f"{method} {url}")
            response = self.session.request(
                method=method, url=url, json=data, params=params, timeout=self.timeout
            )

            # Handle authentication errors
            if response.status_code == 401:
                raise N8nAuthenticationError("Authentication failed. Check your API key.")

            # Handle rate limiting
            if response.status_code == 429:
                raise N8nRateLimitError("Rate limit exceeded. Please wait before retrying.")

            # Raise for other HTTP errors
            response.raise_for_status()

            # Return JSON response if available
            if response.content:
                return response.json()
            return {}

        except requests.exceptions.Timeout:
            raise N8nConnectionError(f"Request timeout after {self.timeout}s")

        except requests.exceptions.ConnectionError as e:
            raise N8nConnectionError(f"Connection failed: {str(e)}")

        except requests.exceptions.HTTPError:
            error_msg = f"HTTP {response.status_code}: {response.text}"
            logger.error(error_msg)
            raise N8nApiError(error_msg)

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise N8nApiError(f"Unexpected error: {str(e)}")
