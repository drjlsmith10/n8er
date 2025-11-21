#!/usr/bin/env python3
"""
n8n Connection Test Script

Tests connectivity to n8n instance and validates API configuration.
Useful for debugging and verifying n8n setup.

Usage:
    python scripts/test_n8n_connection.py

    # Or with custom URL and key:
    N8N_API_URL=http://localhost:5678 N8N_API_KEY=your-key python scripts/test_n8n_connection.py

Author: Project Automata - Agent 3
Version: 1.0.0
Created: 2025-11-20
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from skills.n8n_api_client import N8nApiClient, create_client_from_env


def print_header(title: str):
    """Print formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_status(label: str, status: str, details: str = ""):
    """Print formatted status line."""
    status_symbols = {
        "ok": "✓",
        "error": "✗",
        "warning": "⚠",
        "info": "ℹ"
    }
    symbol = status_symbols.get(status.lower(), "•")

    if status.lower() == "ok":
        status_text = f"\033[92m{symbol} {label}\033[0m"  # Green
    elif status.lower() == "error":
        status_text = f"\033[91m{symbol} {label}\033[0m"  # Red
    elif status.lower() == "warning":
        status_text = f"\033[93m{symbol} {label}\033[0m"  # Yellow
    else:
        status_text = f"{symbol} {label}"

    print(f"  {status_text}")
    if details:
        print(f"    {details}")


def test_environment_variables():
    """Test if environment variables are configured."""
    print_header("Environment Variables")

    api_url = os.getenv("N8N_API_URL")
    api_key = os.getenv("N8N_API_KEY")

    if api_url:
        print_status("N8N_API_URL", "ok", api_url)
    else:
        print_status("N8N_API_URL", "error", "Not set")

    if api_key:
        masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
        print_status("N8N_API_KEY", "ok", f"Set ({masked_key})")
    else:
        print_status("N8N_API_KEY", "error", "Not set")

    return bool(api_url and api_key)


def test_client_creation():
    """Test creating n8n API client."""
    print_header("Client Creation")

    try:
        client = create_client_from_env()
        if client:
            print_status("Client creation", "ok", f"Connected to {client.api_url}")
            return client
        else:
            print_status("Client creation", "error", "Could not create client")
            return None
    except Exception as e:
        print_status("Client creation", "error", str(e))
        return None


def test_connection(client: N8nApiClient):
    """Test connection to n8n."""
    print_header("Connection Test")

    try:
        ok, msg = client.test_connection()
        if ok:
            print_status("Connection", "ok", msg)
            return True
        else:
            print_status("Connection", "error", msg)
            return False
    except Exception as e:
        print_status("Connection", "error", str(e))
        return False


def test_version_detection(client: N8nApiClient):
    """Test n8n version detection."""
    print_header("Version Detection")

    try:
        version_info = client.get_n8n_version()

        if version_info.get("success"):
            print_status(
                "Version detection",
                "ok",
                f"Version: {version_info.get('version')} (method: {version_info.get('method')})"
            )
            if version_info.get("note"):
                print_status("Note", "info", version_info["note"])
        else:
            print_status(
                "Version detection",
                "warning",
                f"Could not detect exact version: {version_info.get('error', 'Unknown error')}"
            )
    except Exception as e:
        print_status("Version detection", "error", str(e))


def test_workflow_access(client: N8nApiClient):
    """Test workflow listing."""
    print_header("Workflow Access")

    try:
        workflows = client.list_workflows(limit=5)
        print_status("Workflow listing", "ok", f"Found {len(workflows)} workflow(s)")

        if workflows:
            print("\n  Recent workflows:")
            for wf in workflows[:3]:
                status = "active" if wf.get("active") else "inactive"
                print(f"    • {wf.get('name', 'Unknown')} (ID: {wf.get('id')}, {status})")
        else:
            print_status("Info", "info", "No workflows found (this is normal for new instances)")

        return True
    except Exception as e:
        print_status("Workflow listing", "error", str(e))
        return False


def test_health_check(client: N8nApiClient):
    """Run comprehensive health check."""
    print_header("Health Check")

    try:
        health = client.health_check()

        overall = health.get("overall_status", "unknown")
        if overall == "healthy":
            print_status("Overall health", "ok", overall.upper())
        else:
            print_status("Overall health", "warning", overall.upper())

        print("\n  Component checks:")
        for check_name, check_result in health.get("checks", {}).items():
            status = check_result.get("status", "unknown")
            message = check_result.get("message", "")
            version = check_result.get("version", "")

            details = message or version or ""
            print_status(f"{check_name.capitalize()}", status, details)

        return overall == "healthy"
    except Exception as e:
        print_status("Health check", "error", str(e))
        return False


def print_recommendations(all_ok: bool):
    """Print recommendations based on test results."""
    print_header("Recommendations")

    if all_ok:
        print_status("Status", "ok", "All tests passed! n8n integration is ready.")
        print("\n  Next steps:")
        print("    1. Run integration tests: pytest tests/test_n8n_integration.py -v -m integration")
        print("    2. Import a workflow: python -c \"from skills.n8n_api_client import *; ...\"")
        print("    3. Check documentation: docs/N8N_API_INTEGRATION.md")
    else:
        print_status("Status", "warning", "Some tests failed. Please review the errors above.")
        print("\n  Troubleshooting:")
        print("    1. Check n8n is running: curl http://localhost:5678")
        print("    2. Verify API key in n8n: Settings > n8n API")
        print("    3. Check .env file has correct N8N_API_URL and N8N_API_KEY")
        print("    4. Review logs for detailed errors")
        print("\n  For more help, see: docs/N8N_API_INTEGRATION.md")


def main():
    """Main test runner."""
    print("\n" + "=" * 70)
    print("  n8n Connection Test")
    print("  Project Automata - n8n API Integration")
    print("=" * 70)

    # Track overall success
    all_ok = True

    # Test 1: Environment variables
    env_ok = test_environment_variables()
    if not env_ok:
        print_header("Test Failed")
        print_status("Error", "error", "Environment variables not configured")
        print("\n  Please set the following environment variables:")
        print("    N8N_API_URL=http://localhost:5678    # Your n8n instance URL")
        print("    N8N_API_KEY=your-api-key-here         # From n8n Settings > n8n API")
        print("\n  You can set these in .env file or export them in your shell.")
        sys.exit(1)

    # Test 2: Client creation
    client = test_client_creation()
    if not client:
        all_ok = False
        print_recommendations(False)
        sys.exit(1)

    # Test 3: Connection
    conn_ok = test_connection(client)
    all_ok = all_ok and conn_ok

    if not conn_ok:
        print_recommendations(False)
        sys.exit(1)

    # Test 4: Version detection
    test_version_detection(client)

    # Test 5: Workflow access
    wf_ok = test_workflow_access(client)
    all_ok = all_ok and wf_ok

    # Test 6: Health check
    health_ok = test_health_check(client)
    all_ok = all_ok and health_ok

    # Print recommendations
    print_recommendations(all_ok)

    print("\n" + "=" * 70)
    print()

    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\n\nUnexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
