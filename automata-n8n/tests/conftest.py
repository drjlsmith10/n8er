"""
Pytest Configuration and Hooks

This file contains pytest hooks and configuration for the test suite.

Author: Project Automata - Test Framework
Version: 1.0.0
Created: 2025-11-21
"""

import logging
import pytest

# Configure logging for tests
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


def pytest_runtest_makereport(item, call):
    """
    Hook to add performance metrics to test reports.

    This hook is called after each test phase (setup, call, teardown) and
    logs a warning for slow tests that take longer than 0.5 seconds.

    Args:
        item: The test item being executed
        call: The call object containing timing information
    """
    if "test_" in item.name and call.when == "call":
        duration = call.stop - call.start
        if duration > 0.5:
            logger.warning(f"SLOW TEST: {item.name} took {duration:.3f}s")


def pytest_configure(config):
    """
    Configure pytest with custom markers.

    Registers custom markers used in the test suite.
    """
    config.addinivalue_line(
        "markers", "integration: mark test as requiring integration with external services"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow (takes > 1 second)"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test (no external dependencies)"
    )


def pytest_collection_modifyitems(config, items):
    """
    Modify test items during collection.

    Automatically adds 'unit' marker to tests that don't have integration or slow markers.
    """
    for item in items:
        if "integration" not in item.keywords and "slow" not in item.keywords:
            item.add_marker(pytest.mark.unit)
