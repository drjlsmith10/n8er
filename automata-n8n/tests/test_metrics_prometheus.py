"""
Unit tests for Prometheus metrics format compliance.

Tests that metrics.py outputs valid Prometheus exposition format
that can be parsed by prometheus_client and actual Prometheus servers.

Author: Project Automata - Engineer Agent
Version: 1.0.0
Created: 2025-11-21
"""

import re
import time
import unittest
from unittest.mock import patch

import sys
import os

# Add parent directory to path to import metrics
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from skills.metrics import (
    MetricsCollector,
    sanitize_metric_name,
    sanitize_label_name,
    METRIC_NAME_PATTERN,
    LABEL_NAME_PATTERN,
)


class TestPrometheusNaming(unittest.TestCase):
    """Test Prometheus naming rules compliance"""

    def test_sanitize_metric_name_valid(self):
        """Test that valid metric names are unchanged"""
        valid_names = ["http_requests_total", "cpu_usage", "app:service:latency"]
        for name in valid_names:
            sanitized = sanitize_metric_name(name)
            self.assertEqual(name, sanitized)
            self.assertIsNotNone(METRIC_NAME_PATTERN.match(sanitized))

    def test_sanitize_metric_name_dots(self):
        """Test that dots are replaced with underscores"""
        self.assertEqual(sanitize_metric_name("http.requests.total"), "http_requests_total")

    def test_sanitize_metric_name_dashes(self):
        """Test that dashes are replaced with underscores"""
        self.assertEqual(sanitize_metric_name("http-requests-total"), "http_requests_total")

    def test_sanitize_metric_name_invalid_chars(self):
        """Test that invalid characters are removed"""
        self.assertEqual(sanitize_metric_name("http@requests#total"), "httprequeststotal")

    def test_sanitize_metric_name_starts_with_number(self):
        """Test that names starting with numbers are prefixed"""
        result = sanitize_metric_name("123_requests")
        self.assertTrue(result.startswith("_"))
        self.assertIsNotNone(METRIC_NAME_PATTERN.match(result))

    def test_sanitize_label_name_valid(self):
        """Test that valid label names are unchanged"""
        valid_names = ["method", "status_code", "endpoint"]
        for name in valid_names:
            sanitized = sanitize_label_name(name)
            self.assertEqual(name, sanitized)
            self.assertIsNotNone(LABEL_NAME_PATTERN.match(sanitized))

    def test_sanitize_label_name_invalid(self):
        """Test that invalid label names are sanitized"""
        self.assertEqual(sanitize_label_name("status-code"), "status_code")
        self.assertEqual(sanitize_label_name("status.code"), "status_code")

    def test_sanitize_label_name_no_colon(self):
        """Test that colons are removed from label names"""
        # Colons are allowed in metric names but not label names
        self.assertEqual(sanitize_label_name("app:service"), "appservice")


class TestPrometheusFormat(unittest.TestCase):
    """Test Prometheus exposition format compliance"""

    def setUp(self):
        """Create a fresh metrics collector for each test"""
        self.metrics = MetricsCollector("test_app")

    def test_counter_format(self):
        """Test counter format with HELP and TYPE"""
        self.metrics.increment_counter("requests", 5, help_text="Total HTTP requests")
        output = self.metrics.export_prometheus()

        # Check HELP line
        self.assertIn("# HELP test_app_requests_total Total HTTP requests", output)

        # Check TYPE line
        self.assertIn("# TYPE test_app_requests_total counter", output)

        # Check metric line
        self.assertIn("test_app_requests_total 5", output)

    def test_counter_suffix(self):
        """Test that counters automatically get _total suffix"""
        self.metrics.increment_counter("requests", 1)
        output = self.metrics.export_prometheus()

        # Should have _total suffix
        self.assertIn("test_app_requests_total", output)
        self.assertNotIn("test_app_requests ", output)

    def test_counter_with_labels(self):
        """Test counter with labels"""
        self.metrics.increment_counter(
            "requests", 5, labels={"method": "GET", "status": "200"}, help_text="HTTP requests"
        )
        output = self.metrics.export_prometheus()

        # Check metric line with labels
        self.assertIn('test_app_requests_total{method="GET",status="200"} 5', output)

    def test_gauge_format(self):
        """Test gauge format"""
        self.metrics.set_gauge("temperature", 23.5, help_text="Current temperature")
        output = self.metrics.export_prometheus()

        # Check HELP and TYPE
        self.assertIn("# HELP test_app_temperature Current temperature", output)
        self.assertIn("# TYPE test_app_temperature gauge", output)
        self.assertIn("test_app_temperature 23.5", output)

    def test_histogram_format(self):
        """Test histogram format with buckets"""
        # Record some values
        for value in [0.001, 0.005, 0.01, 0.05, 0.1]:
            self.metrics.record_histogram(
                "request_duration_seconds",
                value,
                buckets=[0.005, 0.01, 0.05, 0.1, 0.5, 1.0],
                help_text="Request duration",
            )

        output = self.metrics.export_prometheus()

        # Check HELP and TYPE
        self.assertIn(
            "# HELP test_app_request_duration_seconds Request duration", output
        )
        self.assertIn("# TYPE test_app_request_duration_seconds histogram", output)

        # Check bucket lines
        self.assertIn('test_app_request_duration_seconds_bucket{le="0.005"}', output)
        self.assertIn('test_app_request_duration_seconds_bucket{le="0.01"}', output)
        self.assertIn('test_app_request_duration_seconds_bucket{le="+Inf"}', output)

        # Check sum and count
        self.assertIn("test_app_request_duration_seconds_sum", output)
        self.assertIn("test_app_request_duration_seconds_count 5", output)

    def test_histogram_bucket_counts(self):
        """Test histogram bucket counts are cumulative"""
        # Record values: 0.003, 0.007, 0.015
        for value in [0.003, 0.007, 0.015]:
            self.metrics.record_histogram(
                "latency_seconds", value, buckets=[0.005, 0.01, 0.05]
            )

        output = self.metrics.export_prometheus()

        # le="0.005" should have 1 (0.003)
        self.assertIn('test_app_latency_seconds_bucket{le="0.005"} 1', output)

        # le="0.01" should have 2 (0.003, 0.007)
        self.assertIn('test_app_latency_seconds_bucket{le="0.01"} 2', output)

        # le="0.05" should have 3 (all values)
        self.assertIn('test_app_latency_seconds_bucket{le="0.05"} 3', output)

        # le="+Inf" should have 3 (all values)
        self.assertIn('test_app_latency_seconds_bucket{le="+Inf"} 3', output)

    def test_histogram_sum(self):
        """Test histogram sum is correct"""
        values = [1.0, 2.0, 3.0]
        for value in values:
            self.metrics.record_histogram("values", value)

        output = self.metrics.export_prometheus()

        # Sum should be 6.0
        self.assertIn("test_app_values_sum 6.0", output)

    def test_timer_uses_seconds(self):
        """Test that timers use seconds, not milliseconds"""
        start = self.metrics.start_timer("operation")
        time.sleep(0.01)  # Sleep 10ms
        duration = self.metrics.stop_timer("operation", start)

        # Duration should be around 0.01 seconds
        self.assertGreater(duration, 0.009)
        self.assertLess(duration, 0.015)

        # Check suffix
        output = self.metrics.export_prometheus()
        self.assertIn("test_app_operation_seconds", output)

    def test_multiple_metrics(self):
        """Test multiple metrics in one export"""
        self.metrics.increment_counter("requests", 10)
        self.metrics.set_gauge("active_connections", 5)
        self.metrics.record_histogram("latency_seconds", 0.1)

        output = self.metrics.export_prometheus()

        # Should have all three metrics
        self.assertIn("test_app_requests_total", output)
        self.assertIn("test_app_active_connections", output)
        self.assertIn("test_app_latency_seconds", output)

    def test_label_sorting(self):
        """Test that labels are sorted alphabetically"""
        self.metrics.increment_counter(
            "requests", 1, labels={"method": "GET", "endpoint": "/api", "status": "200"}
        )
        output = self.metrics.export_prometheus()

        # Labels should be sorted: endpoint, method, status
        self.assertIn('endpoint="/api",method="GET",status="200"', output)

    def test_metric_name_validation(self):
        """Test that all exported metric names are valid"""
        # Add various metrics
        self.metrics.increment_counter("test.counter", 1)
        self.metrics.set_gauge("test-gauge", 1)
        self.metrics.record_histogram("test_histogram", 1)

        output = self.metrics.export_prometheus()

        # Extract all metric names from output
        metric_lines = [
            line
            for line in output.split("\n")
            if line and not line.startswith("#") and not line.strip() == ""
        ]

        for line in metric_lines:
            # Extract metric name (before { or space)
            if "{" in line:
                metric_name = line.split("{")[0]
            else:
                metric_name = line.split()[0]

            # Remove suffixes
            base_name = metric_name
            for suffix in ["_bucket", "_sum", "_count", "_total"]:
                if base_name.endswith(suffix):
                    base_name = base_name[: -len(suffix)]

            # Validate against Prometheus pattern
            self.assertIsNotNone(
                METRIC_NAME_PATTERN.match(metric_name),
                f"Invalid metric name: {metric_name}",
            )

    def test_empty_histogram(self):
        """Test that empty histograms are exported correctly"""
        self.metrics.record_histogram("empty_hist", 0)
        # Clear the values
        self.metrics.timers["test_app_empty_hist"].clear()

        output = self.metrics.export_prometheus()

        # Should still have bucket, sum, and count lines with 0 values
        self.assertIn('test_app_empty_hist_bucket{le="+Inf"} 0', output)
        self.assertIn("test_app_empty_hist_sum 0", output)
        self.assertIn("test_app_empty_hist_count 0", output)

    def test_help_text_escaping(self):
        """Test that help text is properly formatted"""
        self.metrics.increment_counter(
            "requests", 1, help_text="Total HTTP requests received"
        )
        output = self.metrics.export_prometheus()

        self.assertIn("# HELP test_app_requests_total Total HTTP requests received", output)

    def test_no_duplicate_metrics(self):
        """Test that metrics are not duplicated in output"""
        self.metrics.increment_counter("requests", 1)
        self.metrics.increment_counter("requests", 1)

        output = self.metrics.export_prometheus()

        # Count how many times the metric appears
        count = output.count("test_app_requests_total 2")
        self.assertEqual(count, 1, "Metric should appear exactly once")


class TestPrometheusParserCompatibility(unittest.TestCase):
    """Test compatibility with prometheus_client parser"""

    def setUp(self):
        """Create a fresh metrics collector for each test"""
        self.metrics = MetricsCollector("test_app")

    def test_parse_with_prometheus_client(self):
        """Test that output can be parsed by prometheus_client"""
        try:
            from prometheus_client.parser import text_string_to_metric_families
        except ImportError:
            self.skipTest("prometheus_client not installed")

        # Generate some metrics
        self.metrics.increment_counter("requests", 42, help_text="Total requests")
        self.metrics.set_gauge("temperature", 23.5, help_text="Current temperature")
        self.metrics.record_histogram("latency_seconds", 0.1, help_text="Request latency")

        output = self.metrics.export_prometheus()

        # Try to parse with prometheus_client
        try:
            families = list(text_string_to_metric_families(output))
            self.assertGreater(len(families), 0, "Should parse at least one metric family")

            # Verify metric types
            metric_types = {f.name: f.type for f in families}
            self.assertIn("counter", metric_types.values())
            self.assertIn("gauge", metric_types.values())
            self.assertIn("histogram", metric_types.values())

        except Exception as e:
            self.fail(f"prometheus_client failed to parse output: {e}\n\nOutput:\n{output}")

    def test_histogram_parsing(self):
        """Test that histograms are parsed correctly"""
        try:
            from prometheus_client.parser import text_string_to_metric_families
        except ImportError:
            self.skipTest("prometheus_client not installed")

        # Create histogram with known values
        for value in [0.005, 0.01, 0.05]:
            self.metrics.record_histogram("request_duration_seconds", value)

        output = self.metrics.export_prometheus()

        families = list(text_string_to_metric_families(output))
        histogram_family = next(
            (f for f in families if f.name == "test_app_request_duration_seconds"), None
        )

        self.assertIsNotNone(histogram_family, "Histogram metric family should exist")
        self.assertEqual(histogram_family.type, "histogram")

        # Check that samples exist
        if histogram_family.samples:
            sample = histogram_family.samples[0]
            self.assertGreater(sample.value, 0, "Histogram should have values")


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""

    def setUp(self):
        """Create a fresh metrics collector for each test"""
        self.metrics = MetricsCollector("test_app")

    def test_special_characters_in_labels(self):
        """Test that special characters in labels are handled"""
        self.metrics.increment_counter(
            "requests", 1, labels={"endpoint": "/api/v1/users", "method": "POST"}
        )
        output = self.metrics.export_prometheus()

        # Should contain properly formatted labels
        self.assertIn('endpoint="/api/v1/users"', output)

    def test_numeric_label_values(self):
        """Test that numeric label values are converted to strings"""
        self.metrics.increment_counter("requests", 1, labels={"status_code": 200})
        output = self.metrics.export_prometheus()

        # Should be quoted as string
        self.assertIn('status_code="200"', output)

    def test_app_name_sanitization(self):
        """Test that app name is sanitized"""
        metrics = MetricsCollector("my-app.test")
        metrics.increment_counter("requests", 1)
        output = metrics.export_prometheus()

        # Should be sanitized to my_app_test
        self.assertIn("my_app_test_requests_total", output)

    def test_concurrent_access(self):
        """Test thread safety of metrics collection"""
        import threading

        def increment():
            for _ in range(100):
                self.metrics.increment_counter("requests", 1)

        threads = [threading.Thread(target=increment) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Should have 1000 total
        self.assertEqual(self.metrics.get_counter("requests"), 1000)


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2)
