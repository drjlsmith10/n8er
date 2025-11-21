"""
Metrics Collection Module

Collects and exposes metrics for monitoring Project Automata.
Supports Prometheus metrics format and structured logging.

Metrics Collected:
- Workflow generation time
- Parsing success/failure rates
- Knowledge base queries
- Agent execution times
- Error rates and types

Author: Project Automata - Engineer Agent
Version: 1.0.0
Created: 2025-11-20
"""

import logging
import re
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

# Configure logging with structured format
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


# Prometheus naming validation patterns
METRIC_NAME_PATTERN = re.compile(r"^[a-zA-Z_:][a-zA-Z0-9_:]*$")
LABEL_NAME_PATTERN = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")


def sanitize_metric_name(name: str) -> str:
    """
    Sanitize metric name to comply with Prometheus naming rules.

    Rules:
    - Must match [a-zA-Z_:][a-zA-Z0-9_:]*
    - Replace dots with underscores
    - Replace dashes with underscores
    - Remove invalid characters
    """
    # Replace dots and dashes with underscores
    name = name.replace(".", "_").replace("-", "_")

    # Remove any character that's not alphanumeric, underscore, or colon
    name = re.sub(r"[^a-zA-Z0-9_:]", "", name)

    # Ensure it starts with a letter or underscore
    if name and not re.match(r"^[a-zA-Z_:]", name):
        name = "_" + name

    # If empty after sanitization, provide a default
    if not name:
        name = "unnamed_metric"

    return name


def sanitize_label_name(name: str) -> str:
    """
    Sanitize label name to comply with Prometheus naming rules.

    Rules:
    - Must match [a-zA-Z_][a-zA-Z0-9_]*
    - Replace dots with underscores
    - Replace dashes with underscores
    - Remove invalid characters
    """
    # Replace dots and dashes with underscores
    name = name.replace(".", "_").replace("-", "_")

    # Remove any character that's not alphanumeric or underscore
    name = re.sub(r"[^a-zA-Z0-9_]", "", name)

    # Ensure it starts with a letter or underscore
    if name and not re.match(r"^[a-zA-Z_]", name):
        name = "_" + name

    # If empty after sanitization, provide a default
    if not name:
        name = "unnamed_label"

    return name


class MetricType(Enum):
    """Types of metrics"""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


@dataclass
class Metric:
    """Represents a single metric"""

    name: str
    type: MetricType
    value: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    labels: Dict[str, str] = field(default_factory=dict)
    help_text: str = ""


class MetricsCollector:
    """
    Collects and aggregates metrics for monitoring.

    Provides:
    - Counter metrics (incremental counts)
    - Gauge metrics (instantaneous values)
    - Histogram metrics (distributions)
    - Timer metrics (duration tracking)
    """

    # Default histogram buckets (in seconds for timers)
    DEFAULT_BUCKETS = [0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0]

    def __init__(self, app_name: str = "automata"):
        """Initialize metrics collector"""
        self.app_name = sanitize_metric_name(app_name)
        self.metrics: Dict[str, Metric] = {}
        # Use deque with maxlen for bounded storage (prevents memory leak)
        self.timers: Dict[str, deque] = {}
        self.histogram_buckets: Dict[str, List[float]] = {}
        self._lock = threading.Lock()  # Thread safety for concurrent metric updates
        logger.debug(f"Metrics collector initialized for {self.app_name}")

    # Counter Methods
    def increment_counter(
        self, name: str, value: float = 1.0, labels: Optional[Dict] = None, help_text: str = ""
    ):
        """Increment a counter metric"""
        # Sanitize name and ensure _total suffix for counters
        sanitized_name = sanitize_metric_name(name)
        if not sanitized_name.endswith("_total"):
            sanitized_name += "_total"
        full_name = f"{self.app_name}_{sanitized_name}"

        # Sanitize labels
        sanitized_labels = {}
        if labels:
            sanitized_labels = {sanitize_label_name(k): str(v) for k, v in labels.items()}

        with self._lock:
            if full_name not in self.metrics:
                self.metrics[full_name] = Metric(
                    name=full_name,
                    type=MetricType.COUNTER,
                    value=0.0,
                    labels=sanitized_labels,
                    help_text=help_text or f"Counter metric for {sanitized_name}",
                )
            self.metrics[full_name].value += value

    def get_counter(self, name: str) -> float:
        """Get current counter value"""
        sanitized_name = sanitize_metric_name(name)
        if not sanitized_name.endswith("_total"):
            sanitized_name += "_total"
        full_name = f"{self.app_name}_{sanitized_name}"
        return self.metrics.get(full_name, Metric(full_name, MetricType.COUNTER)).value

    # Gauge Methods
    def set_gauge(self, name: str, value: float, labels: Optional[Dict] = None, help_text: str = ""):
        """Set a gauge metric"""
        # Sanitize name
        sanitized_name = sanitize_metric_name(name)
        full_name = f"{self.app_name}_{sanitized_name}"

        # Sanitize labels
        sanitized_labels = {}
        if labels:
            sanitized_labels = {sanitize_label_name(k): str(v) for k, v in labels.items()}

        with self._lock:
            self.metrics[full_name] = Metric(
                name=full_name,
                type=MetricType.GAUGE,
                value=value,
                labels=sanitized_labels,
                help_text=help_text or f"Gauge metric for {sanitized_name}",
            )

    def get_gauge(self, name: str) -> float:
        """Get current gauge value"""
        sanitized_name = sanitize_metric_name(name)
        full_name = f"{self.app_name}_{sanitized_name}"
        return self.metrics.get(full_name, Metric(full_name, MetricType.GAUGE)).value

    # Timer Methods
    def start_timer(self, name: str) -> float:
        """Start timing an operation"""
        return time.perf_counter()

    def stop_timer(
        self, name: str, start_time: float, labels: Optional[Dict] = None, help_text: str = ""
    ) -> float:
        """Stop timer and record duration in seconds"""
        duration_seconds = time.perf_counter() - start_time

        # Sanitize name and ensure _seconds suffix
        sanitized_name = sanitize_metric_name(name)
        if not sanitized_name.endswith("_seconds"):
            sanitized_name += "_seconds"
        full_name = f"{self.app_name}_{sanitized_name}"

        # Sanitize labels
        sanitized_labels = {}
        if labels:
            sanitized_labels = {sanitize_label_name(k): str(v) for k, v in labels.items()}

        with self._lock:
            if full_name not in self.timers:
                # Use deque with maxlen=1000 for bounded storage (prevents memory leak)
                self.timers[full_name] = deque(maxlen=1000)
                # Initialize histogram buckets
                self.histogram_buckets[full_name] = self.DEFAULT_BUCKETS.copy()

            self.timers[full_name].append(duration_seconds)

            # Also record as metric
            if full_name not in self.metrics:
                self.metrics[full_name] = Metric(
                    name=full_name,
                    type=MetricType.HISTOGRAM,
                    labels=sanitized_labels,
                    help_text=help_text or f"Histogram of {sanitized_name}",
                )

        return duration_seconds

    def get_timer_stats(self, name: str) -> Dict:
        """Get statistics for a timer"""
        sanitized_name = sanitize_metric_name(name)
        if not sanitized_name.endswith("_seconds"):
            sanitized_name += "_seconds"
        full_name = f"{self.app_name}_{sanitized_name}"

        if full_name not in self.timers or not self.timers[full_name]:
            return {}

        durations = self.timers[full_name]
        return {
            "count": len(durations),
            "min": min(durations),
            "max": max(durations),
            "avg": sum(durations) / len(durations),
            "total": sum(durations),
        }

    # Histogram Methods
    def record_histogram(
        self,
        name: str,
        value: float,
        labels: Optional[Dict] = None,
        buckets: Optional[List[float]] = None,
        help_text: str = "",
    ):
        """Record a value in a histogram"""
        # Sanitize name
        sanitized_name = sanitize_metric_name(name)
        full_name = f"{self.app_name}_{sanitized_name}"

        # Sanitize labels
        sanitized_labels = {}
        if labels:
            sanitized_labels = {sanitize_label_name(k): str(v) for k, v in labels.items()}

        with self._lock:
            if full_name not in self.timers:
                # Use deque with maxlen=1000 for bounded storage (prevents memory leak)
                self.timers[full_name] = deque(maxlen=1000)
                # Initialize histogram buckets
                self.histogram_buckets[full_name] = (
                    buckets.copy() if buckets else self.DEFAULT_BUCKETS.copy()
                )

            self.timers[full_name].append(value)

            # Also record as metric
            if full_name not in self.metrics:
                self.metrics[full_name] = Metric(
                    name=full_name,
                    type=MetricType.HISTOGRAM,
                    labels=sanitized_labels,
                    help_text=help_text or f"Histogram of {sanitized_name}",
                )

    # Prometheus Format Export
    def export_prometheus(self) -> str:
        """
        Export metrics in Prometheus exposition format.

        Format specification:
        - HELP: # HELP metric_name description
        - TYPE: # TYPE metric_name type
        - Metric: metric_name{label="value"} value
        - Histogram: includes _bucket{le="x"}, _sum, _count
        - Counter: should end with _total
        - Timer: should end with _seconds
        """
        output = []
        processed_metrics = set()

        with self._lock:
            # Sort metrics for consistent output
            sorted_metrics = sorted(self.metrics.items())

            for metric_name, metric in sorted_metrics:
                if metric_name in processed_metrics:
                    continue

                # Format labels helper
                def format_labels(labels_dict: Dict[str, str], extra_labels: Dict[str, str] = None) -> str:
                    """Format labels for Prometheus"""
                    all_labels = labels_dict.copy()
                    if extra_labels:
                        all_labels.update(extra_labels)

                    if not all_labels:
                        return ""

                    label_pairs = [f'{k}="{v}"' for k, v in sorted(all_labels.items())]
                    return "{" + ",".join(label_pairs) + "}"

                # Add HELP comment
                help_text = metric.help_text or f"{metric.type.value.capitalize()} metric"
                output.append(f"# HELP {metric_name} {help_text}")

                # Add TYPE comment
                output.append(f"# TYPE {metric_name} {metric.type.value}")

                # Export based on metric type
                if metric.type == MetricType.COUNTER:
                    # Counter: simple value
                    label_str = format_labels(metric.labels)
                    output.append(f"{metric_name}{label_str} {metric.value}")

                elif metric.type == MetricType.GAUGE:
                    # Gauge: simple value
                    label_str = format_labels(metric.labels)
                    output.append(f"{metric_name}{label_str} {metric.value}")

                elif metric.type == MetricType.HISTOGRAM:
                    # Histogram: needs buckets, sum, and count
                    if metric_name in self.timers and self.timers[metric_name]:
                        values = list(self.timers[metric_name])
                        buckets = self.histogram_buckets.get(metric_name, self.DEFAULT_BUCKETS)

                        # Calculate bucket counts
                        for bucket in buckets:
                            count = sum(1 for v in values if v <= bucket)
                            label_str = format_labels(metric.labels, {"le": str(bucket)})
                            output.append(f"{metric_name}_bucket{label_str} {count}")

                        # Add +Inf bucket
                        label_str = format_labels(metric.labels, {"le": "+Inf"})
                        output.append(f"{metric_name}_bucket{label_str} {len(values)}")

                        # Add sum
                        total = sum(values)
                        label_str = format_labels(metric.labels)
                        output.append(f"{metric_name}_sum{label_str} {total}")

                        # Add count
                        output.append(f"{metric_name}_count{label_str} {len(values)}")
                    else:
                        # Empty histogram
                        label_str = format_labels(metric.labels, {"le": "+Inf"})
                        output.append(f"{metric_name}_bucket{label_str} 0")
                        label_str = format_labels(metric.labels)
                        output.append(f"{metric_name}_sum{label_str} 0")
                        output.append(f"{metric_name}_count{label_str} 0")

                # Add blank line between metrics
                output.append("")

                processed_metrics.add(metric_name)

        return "\n".join(output)

    # Summary Export
    def get_summary(self) -> Dict:
        """Get summary of all metrics"""
        summary = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "app_name": self.app_name,
            "metrics_count": len(self.metrics),
            "timers_count": len(self.timers),
            "counters": {},
            "gauges": {},
            "histograms": {},
        }

        for name, metric in self.metrics.items():
            if metric.type == MetricType.COUNTER:
                summary["counters"][name] = metric.value
            elif metric.type == MetricType.GAUGE:
                summary["gauges"][name] = metric.value
            elif metric.type == MetricType.HISTOGRAM:
                summary["histograms"][name] = self.get_timer_stats(name)

        return summary

    def log_summary(self, level: int = logging.INFO):
        """Log metrics summary"""
        summary = self.get_summary()
        logger.log(level, f"Metrics Summary: {summary}")


# ========================================================================
# Factory Function (Recommended Approach)
# ========================================================================

def create_metrics_collector(app_name: str = "automata") -> MetricsCollector:
    """
    Factory function to create a new MetricsCollector instance.

    This is the recommended way to create metrics collectors for dependency
    injection and testing.

    Args:
        app_name: Application name prefix for metrics

    Returns:
        New MetricsCollector instance

    Example:
        # In your application initialization:
        metrics = create_metrics_collector("my_app")

        # Pass to components via dependency injection:
        my_service = MyService(metrics=metrics)
    """
    return MetricsCollector(app_name=app_name)


# ========================================================================
# Global Instance (Deprecated but maintained for backward compatibility)
# ========================================================================

_metrics: Optional[MetricsCollector] = None


def get_global_metrics() -> MetricsCollector:
    """
    Get or create global metrics instance (lazy initialization).

    WARNING: Global state is discouraged. Use create_metrics_collector()
    and dependency injection instead.

    Returns:
        Global MetricsCollector instance

    Deprecated:
        Use create_metrics_collector() with dependency injection instead.
    """
    global _metrics
    if _metrics is None:
        import warnings
        warnings.warn(
            "Using global metrics instance is deprecated. "
            "Use create_metrics_collector() with dependency injection instead.",
            DeprecationWarning,
            stacklevel=2
        )
        _metrics = MetricsCollector()
    return _metrics


# ========================================================================
# Convenience Functions (Deprecated but maintained for compatibility)
# ========================================================================

def increment_counter(name: str, value: float = 1.0, labels: Optional[Dict] = None, help_text: str = ""):
    """
    Increment a counter metric on global instance.

    DEPRECATED: Use dependency injection instead:
        metrics = create_metrics_collector()
        metrics.increment_counter(name, value, labels, help_text)
    """
    get_global_metrics().increment_counter(name, value, labels, help_text)


def set_gauge(name: str, value: float, labels: Optional[Dict] = None, help_text: str = ""):
    """
    Set a gauge metric on global instance.

    DEPRECATED: Use dependency injection instead:
        metrics = create_metrics_collector()
        metrics.set_gauge(name, value, labels, help_text)
    """
    get_global_metrics().set_gauge(name, value, labels, help_text)


def start_timer(name: str) -> float:
    """
    Start a timer on global instance.

    DEPRECATED: Use dependency injection instead:
        metrics = create_metrics_collector()
        start_time = metrics.start_timer(name)
    """
    return get_global_metrics().start_timer(name)


def stop_timer(name: str, start_time: float, labels: Optional[Dict] = None, help_text: str = "") -> float:
    """
    Stop a timer and return duration in seconds.

    DEPRECATED: Use dependency injection instead:
        metrics = create_metrics_collector()
        metrics.stop_timer(name, start_time, labels, help_text)
    """
    return get_global_metrics().stop_timer(name, start_time, labels, help_text)


def record_histogram(
    name: str,
    value: float,
    labels: Optional[Dict] = None,
    buckets: Optional[List[float]] = None,
    help_text: str = "",
):
    """
    Record a histogram value on global instance.

    DEPRECATED: Use dependency injection instead:
        metrics = create_metrics_collector()
        metrics.record_histogram(name, value, labels, buckets, help_text)
    """
    get_global_metrics().record_histogram(name, value, labels, buckets, help_text)


def get_metrics() -> MetricsCollector:
    """
    Get global metrics instance.

    DEPRECATED: Use create_metrics_collector() with dependency injection instead.
    """
    return get_global_metrics()


def export_prometheus() -> str:
    """
    Export metrics in Prometheus format from global instance.

    DEPRECATED: Use dependency injection instead:
        metrics = create_metrics_collector()
        prometheus_data = metrics.export_prometheus()
    """
    return get_global_metrics().export_prometheus()


def log_summary():
    """
    Log metrics summary from global instance.

    DEPRECATED: Use dependency injection instead:
        metrics = create_metrics_collector()
        metrics.log_summary()
    """
    get_global_metrics().log_summary()


# Structured logging helper
class StructuredLogger:
    """
    Structured logging that includes context and metrics.
    """

    def __init__(self, name: str):
        """Initialize structured logger"""
        self.logger = logging.getLogger(name)
        self.context = {}

    def set_context(self, **kwargs):
        """Set logging context"""
        self.context.update(kwargs)

    def clear_context(self):
        """Clear logging context"""
        self.context.clear()

    def info(self, message: str, **kwargs):
        """Log info with context"""
        context = {**self.context, **kwargs}
        self.logger.info(f"{message} | context={context}")

    def warning(self, message: str, **kwargs):
        """Log warning with context"""
        context = {**self.context, **kwargs}
        self.logger.warning(f"{message} | context={context}")

    def error(self, message: str, **kwargs):
        """Log error with context"""
        context = {**self.context, **kwargs}
        self.logger.error(f"{message} | context={context}")

    def debug(self, message: str, **kwargs):
        """Log debug with context"""
        context = {**self.context, **kwargs}
        self.logger.debug(f"{message} | context={context}")


if __name__ == "__main__":
    # Example usage
    print("Project Automata Metrics Module v1.0.0")
    print("=" * 60)

    # Create metrics
    metrics = MetricsCollector("automata")

    # Counter example (automatically adds _total suffix)
    metrics.increment_counter("workflows_generated", 5.0, help_text="Total number of workflows generated")
    metrics.increment_counter("workflows_generated", 3.0)
    print(f"Workflows generated: {metrics.get_counter('workflows_generated')}")

    # Gauge example
    metrics.set_gauge("active_tasks", 42, help_text="Number of currently active tasks")
    print(f"Active tasks: {metrics.get_gauge('active_tasks')}")

    # Timer example (automatically adds _seconds suffix and uses seconds)
    start = metrics.start_timer("workflow_generation")
    time.sleep(0.01)  # Simulate work
    duration = metrics.stop_timer(
        "workflow_generation", start, help_text="Time to generate workflows"
    )
    print(f"Generation time: {duration:.4f}s ({duration*1000:.2f}ms)")

    # Add more timer samples for histogram demonstration
    for i in range(10):
        start = metrics.start_timer("workflow_generation")
        time.sleep(0.001 * (i + 1))  # Variable duration
        metrics.stop_timer("workflow_generation", start)

    # Get stats
    stats = metrics.get_timer_stats("workflow_generation")
    print(f"Generation stats: {stats}")

    # Histogram example
    metrics.record_histogram(
        "request_size_bytes",
        1024.5,
        labels={"method": "POST", "endpoint": "/api/workflows"},
        help_text="Size of HTTP requests in bytes",
    )
    metrics.record_histogram("request_size_bytes", 2048.0, labels={"method": "POST", "endpoint": "/api/workflows"})
    metrics.record_histogram("request_size_bytes", 512.0, labels={"method": "GET", "endpoint": "/api/status"})

    # Export
    print("\n" + "=" * 60)
    print("Prometheus Export:")
    print("=" * 60)
    print(metrics.export_prometheus())

    print("\n" + "=" * 60)
    print("Metrics Summary:")
    print("=" * 60)
    import json

    print(json.dumps(metrics.get_summary(), indent=2))
