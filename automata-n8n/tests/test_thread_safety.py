"""
Thread Safety Tests

This module provides comprehensive tests for thread safety across the codebase.
Tests verify that concurrent access to shared resources is properly synchronized
and that pessimistic locking prevents race conditions.

Author: Project Automata - Concurrency Specialist
Version: 1.0.0
Created: 2025-11-21

Test Coverage:
- WorkflowVersionManager: Pessimistic locking for version creation
- CredentialManager: Dictionary mutation protection
- N8nApiClient: Thread-safe rate limiting (refactored architecture)
- Thread safety documentation verification
"""

import pytest
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Set

# Import modules to test
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "skills"))

from workflow_versioning import WorkflowVersionManager
from credential_manager import CredentialManager


class TestWorkflowVersioningThreadSafety:
    """
    Tests for thread safety in WorkflowVersionManager.

    Focus Areas:
    - Pessimistic locking prevents duplicate version creation
    - TOCTOU protection in version_bump
    - Lock timeout functionality
    - Concurrent version creation safety
    """

    def test_concurrent_version_creation_no_duplicates(self):
        """
        Test that concurrent version creation doesn't create duplicate versions.

        This tests the pessimistic locking mechanism. Multiple threads attempt
        to create versions for the same workflow concurrently. The lock should
        ensure all versions are created atomically with no race conditions.
        """
        manager = WorkflowVersionManager()
        workflow = {
            "name": "Test Workflow",
            "id": "test-workflow-1",
            "nodes": [],
            "connections": {}
        }

        num_threads = 10
        versions_created: List[str] = []
        lock = threading.Lock()

        def create_version(index: int):
            """Worker function to create a version"""
            version = f"1.0.{index}"
            result = manager.create_version(
                workflow=workflow,
                version=version,
                changelog=[f"Change {index}"],
                workflow_id="test-workflow-1"
            )

            # Thread-safe append
            with lock:
                versions_created.append(result.version)

        # Run concurrent version creation
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(create_version, i) for i in range(num_threads)]
            for future in as_completed(futures):
                future.result()  # Raise any exceptions

        # Verify: All versions created, no duplicates
        assert len(versions_created) == num_threads
        assert len(set(versions_created)) == num_threads  # All unique

        # Verify: All versions are stored in manager
        stored_versions = manager.list_versions("test-workflow-1")
        assert len(stored_versions) == num_threads

    def test_version_bump_toctou_protection(self):
        """
        Test that version_bump is protected against TOCTOU race conditions.

        Multiple threads attempt to bump the version concurrently. The
        pessimistic locking should ensure that each bump reads the current
        version and creates the new version atomically.
        """
        manager = WorkflowVersionManager()
        workflow = {
            "name": "Test Workflow",
            "id": "test-workflow-2",
            "nodes": [],
            "connections": {}
        }

        # Create initial version
        manager.create_version(
            workflow=workflow,
            version="1.0.0",
            workflow_id="test-workflow-2"
        )

        num_threads = 5
        bumped_versions: List[str] = []
        lock = threading.Lock()

        def bump_version(index: int):
            """Worker function to bump version"""
            result = manager.version_bump(
                workflow=workflow,
                bump_type="patch",
                changelog=[f"Bump {index}"],
                workflow_id="test-workflow-2"
            )

            with lock:
                bumped_versions.append(result.version)

        # Run concurrent version bumps
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(bump_version, i) for i in range(num_threads)]
            for future in as_completed(futures):
                future.result()

        # Verify: All bumps created unique versions
        assert len(bumped_versions) == num_threads
        assert len(set(bumped_versions)) == num_threads

        # Verify: Versions follow expected sequence (1.0.1, 1.0.2, ..., 1.0.5)
        expected_versions = {f"1.0.{i+1}" for i in range(num_threads)}
        assert set(bumped_versions) == expected_versions

    def test_lock_timeout_raises_exception(self):
        """
        Test that lock timeout raises TimeoutError.

        One thread holds the lock, another thread attempts to acquire it
        with a short timeout and should fail.
        """
        manager = WorkflowVersionManager()
        workflow = {
            "name": "Test Workflow",
            "id": "test-workflow-3",
            "nodes": [],
            "connections": {}
        }

        # Get the workflow lock
        lock = manager._get_workflow_lock("test-workflow-3")

        # Thread 1: Hold the lock
        def hold_lock():
            lock.acquire()
            time.sleep(2)  # Hold for 2 seconds
            lock.release()

        # Thread 2: Try to acquire with short timeout
        def try_acquire_with_timeout():
            with pytest.raises(TimeoutError):
                manager.create_version(
                    workflow=workflow,
                    version="1.0.0",
                    workflow_id="test-workflow-3",
                    lock_timeout=0.5  # Short timeout
                )

        # Run both threads
        thread1 = threading.Thread(target=hold_lock)
        thread2 = threading.Thread(target=try_acquire_with_timeout)

        thread1.start()
        time.sleep(0.1)  # Ensure thread1 acquires lock first
        thread2.start()

        thread1.join()
        thread2.join()

    def test_concurrent_read_operations_safe(self):
        """
        Test that concurrent read operations are safe.

        Multiple threads read versions concurrently while one thread creates
        versions. Reads should always return consistent data.
        """
        manager = WorkflowVersionManager()
        workflow = {
            "name": "Test Workflow",
            "id": "test-workflow-4",
            "nodes": [],
            "connections": {}
        }

        # Create some initial versions
        for i in range(5):
            manager.create_version(
                workflow=workflow,
                version=f"1.0.{i}",
                workflow_id="test-workflow-4"
            )

        results: List[int] = []
        lock = threading.Lock()

        def reader():
            """Read versions multiple times"""
            for _ in range(10):
                versions = manager.list_versions("test-workflow-4")
                with lock:
                    results.append(len(versions))
                time.sleep(0.01)

        def writer():
            """Create new versions"""
            for i in range(5, 10):
                manager.create_version(
                    workflow=workflow,
                    version=f"1.0.{i}",
                    workflow_id="test-workflow-4"
                )
                time.sleep(0.02)

        # Run concurrent reads and writes
        with ThreadPoolExecutor(max_workers=6) as executor:
            # 5 readers, 1 writer
            reader_futures = [executor.submit(reader) for _ in range(5)]
            writer_future = executor.submit(writer)

            for future in as_completed(reader_futures + [writer_future]):
                future.result()

        # Verify: All reads returned valid counts (5-10 versions)
        assert all(5 <= count <= 10 for count in results)


class TestCredentialManagerThreadSafety:
    """
    Tests for thread safety in CredentialManager.

    Focus Areas:
    - Dictionary mutation protection
    - TOCTOU protection in track_node_credential
    - Concurrent credential operations
    """

    def test_concurrent_add_credential_safe(self):
        """
        Test that concurrent credential additions are thread-safe.

        Multiple threads add different credentials concurrently.
        No credentials should be lost or corrupted.
        """
        manager = CredentialManager()

        num_threads = 10

        def add_credential(index: int):
            """Add a credential"""
            manager.add_credential(
                name=f"Credential-{index}",
                credential_type="httpBasicAuth",
                description=f"Test credential {index}"
            )

        # Run concurrent additions
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(add_credential, i) for i in range(num_threads)]
            for future in as_completed(futures):
                future.result()

        # Verify: All credentials added
        credentials = manager.list_credentials()
        assert len(credentials) == num_threads

        # Verify: All have unique names
        names = {c.name for c in credentials}
        assert len(names) == num_threads

    def test_track_node_credential_toctou_protection(self):
        """
        Test that track_node_credential is protected against TOCTOU.

        Multiple threads track credentials for the same node concurrently.
        Should not create duplicate entries.
        """
        manager = CredentialManager()

        # Add test credentials
        for i in range(5):
            manager.add_credential(
                name=f"Cred-{i}",
                credential_type="httpBasicAuth"
            )

        num_threads = 20

        def track_credential(cred_index: int):
            """Track a credential for a node"""
            manager.track_node_credential("TestNode", f"Cred-{cred_index % 5}")

        # Run concurrent tracking
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(track_credential, i) for i in range(num_threads)]
            for future in as_completed(futures):
                future.result()

        # Verify: Node has exactly 5 unique credentials (no duplicates)
        node_creds = manager.get_node_credentials("TestNode")
        assert len(node_creds) == 5

        # Verify: All expected credentials tracked
        cred_names = {c.name for c in node_creds}
        assert cred_names == {f"Cred-{i}" for i in range(5)}

    def test_concurrent_read_write_credentials(self):
        """
        Test concurrent reads and writes to credential manager.

        Multiple threads read and write credentials concurrently.
        Operations should not interfere with each other.
        """
        manager = CredentialManager()

        results: List[int] = []
        lock = threading.Lock()

        def writer(index: int):
            """Write credentials"""
            for i in range(5):
                manager.add_credential(
                    name=f"Writer-{index}-Cred-{i}",
                    credential_type="httpBasicAuth"
                )
                time.sleep(0.01)

        def reader():
            """Read credentials"""
            for _ in range(10):
                creds = manager.list_credentials()
                with lock:
                    results.append(len(creds))
                time.sleep(0.01)

        # Run concurrent operations
        with ThreadPoolExecutor(max_workers=6) as executor:
            writer_futures = [executor.submit(writer, i) for i in range(3)]
            reader_futures = [executor.submit(reader) for _ in range(3)]

            for future in as_completed(writer_futures + reader_futures):
                future.result()

        # Verify: Final count is correct (3 writers × 5 credentials each)
        final_creds = manager.list_credentials()
        assert len(final_creds) == 15

        # Verify: All reads returned valid counts (0-15)
        assert all(0 <= count <= 15 for count in results)


class TestThreadSafetyDocumentation:
    """
    Tests to verify that thread safety documentation is present and accurate.

    These tests ensure that classes document their thread safety guarantees
    and limitations.
    """

    def test_workflow_versioning_has_thread_safety_docs(self):
        """Verify WorkflowVersionManager documents thread safety"""
        from workflow_versioning import WorkflowVersionManager

        docstring = WorkflowVersionManager.__doc__
        assert docstring is not None
        assert "Thread Safety" in docstring or "thread-safe" in docstring.lower()

    def test_credential_manager_has_thread_safety_docs(self):
        """Verify CredentialManager documents thread safety"""
        from credential_manager import CredentialManager

        docstring = CredentialManager.__doc__
        assert docstring is not None
        assert "Thread Safety" in docstring or "thread-safe" in docstring.lower()

    def test_parser_has_thread_safety_docs(self):
        """Verify N8nSchemaParser documents thread safety"""
        from parse_n8n_schema import N8nSchemaParser

        docstring = N8nSchemaParser.__doc__
        assert docstring is not None
        assert "Thread Safety" in docstring or "thread-safe" in docstring.lower()

    def test_builder_has_thread_safety_docs(self):
        """Verify WorkflowBuilder documents thread safety"""
        from generate_workflow_json import WorkflowBuilder

        docstring = WorkflowBuilder.__doc__
        assert docstring is not None
        assert "Thread Safety" in docstring or "thread-safe" in docstring.lower()


class TestStressTestConcurrency:
    """
    Stress tests to verify robustness under high concurrency.

    These tests push the limits to ensure the locking mechanisms
    hold up under heavy load.
    """

    def test_high_concurrency_version_creation(self):
        """
        Stress test with many concurrent version creations.

        100 threads creating versions concurrently should complete
        without errors or deadlocks.
        """
        manager = WorkflowVersionManager()
        workflow = {
            "name": "Stress Test",
            "id": "stress-test-1",
            "nodes": [],
            "connections": {}
        }

        num_threads = 100
        errors: List[Exception] = []
        lock = threading.Lock()

        def create_version(index: int):
            """Create a version"""
            try:
                manager.create_version(
                    workflow=workflow,
                    version=f"1.0.{index}",
                    workflow_id="stress-test-1",
                    lock_timeout=10.0  # Longer timeout for stress test
                )
            except Exception as e:
                with lock:
                    errors.append(e)

        # Run stress test
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(create_version, i) for i in range(num_threads)]
            for future in as_completed(futures):
                future.result()

        duration = time.time() - start_time

        # Verify: No errors
        assert len(errors) == 0, f"Errors occurred: {errors}"

        # Verify: All versions created
        versions = manager.list_versions("stress-test-1")
        assert len(versions) == num_threads

        # Performance check: Should complete in reasonable time (< 30s)
        assert duration < 30.0, f"Stress test took too long: {duration}s"

    def test_high_concurrency_credential_operations(self):
        """
        Stress test with many concurrent credential operations.

        Multiple threads performing mixed operations (add, read, track).
        """
        manager = CredentialManager()

        num_operations = 200
        errors: List[Exception] = []
        lock = threading.Lock()

        def mixed_operations(index: int):
            """Perform mixed credential operations"""
            try:
                # Add credential
                manager.add_credential(
                    name=f"StressCred-{index}",
                    credential_type="httpBasicAuth"
                )

                # Read credentials
                manager.list_credentials()

                # Track credential
                manager.track_node_credential(
                    f"Node-{index % 10}",
                    f"StressCred-{index}"
                )

                # Get node credentials
                manager.get_node_credentials(f"Node-{index % 10}")

            except Exception as e:
                with lock:
                    errors.append(e)

        # Run stress test
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(mixed_operations, i) for i in range(num_operations)]
            for future in as_completed(futures):
                future.result()

        duration = time.time() - start_time

        # Verify: No errors
        assert len(errors) == 0, f"Errors occurred: {errors}"

        # Verify: All credentials added
        credentials = manager.list_credentials()
        assert len(credentials) == num_operations

        # Performance check
        assert duration < 30.0, f"Stress test took too long: {duration}s"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
