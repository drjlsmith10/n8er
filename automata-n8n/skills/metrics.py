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
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

# Configure logging with structured format
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


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

    def __init__(self, app_name: str = "automata"):
        """Initialize metrics collector"""
        self.app_name = app_name
        self.metrics: Dict[str, Metric] = {}
        self.timers: Dict[str, List[float]] = {}
        logger.debug(f"Metrics collector initialized for {app_name}")

    # Counter Methods
    def increment_counter(self, name: str, value: float = 1.0, labels: Optional[Dict] = None):
        """Increment a counter metric"""
        full_name = f"{self.app_name}_{name}"
        if full_name not in self.metrics:
            self.metrics[full_name] = Metric(
                name=full_name, type=MetricType.COUNTER, value=0.0, labels=labels or {}
            )
        self.metrics[full_name].value += value

    def get_counter(self, name: str) -> float:
        """Get current counter value"""
        full_name = f"{self.app_name}_{name}"
        return self.metrics.get(full_name, Metric(full_name, MetricType.COUNTER)).value

    # Gauge Methods
    def set_gauge(self, name: str, value: float, labels: Optional[Dict] = None):
        """Set a gauge metric"""
        full_name = f"{self.app_name}_{name}"
        self.metrics[full_name] = Metric(
            name=full_name, type=MetricType.GAUGE, value=value, labels=labels or {}
        )

    def get_gauge(self, name: str) -> float:
        """Get current gauge value"""
        full_name = f"{self.app_name}_{name}"
        return self.metrics.get(full_name, Metric(full_name, MetricType.GAUGE)).value

    # Timer Methods
    def start_timer(self, name: str) -> float:
        """Start timing an operation"""
        return time.perf_counter()

    def stop_timer(self, name: str, start_time: float, labels: Optional[Dict] = None) -> float:
        """Stop timer and record duration"""
        duration_ms = (time.perf_counter() - start_time) * 1000

        full_name = f"{self.app_name}_{name}"
        if full_name not in self.timers:
            self.timers[full_name] = []

        self.timers[full_name].append(duration_ms)

        # Also record as metric
        if full_name not in self.metrics:
            self.metrics[full_name] = Metric(
                name=full_name, type=MetricType.HISTOGRAM, labels=labels or {}
            )

        return duration_ms

    def get_timer_stats(self, name: str) -> Dict:
        """Get statistics for a timer"""
        full_name = f"{self.app_name}_{name}"
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
    def record_histogram(self, name: str, value: float, labels: Optional[Dict] = None):
        """Record a value in a histogram"""
        full_name = f"{self.app_name}_{name}"
        if full_name not in self.timers:
            self.timers[full_name] = []
        self.timers[full_name].append(value)

    # Prometheus Format Export
    def export_prometheus(self) -> str:
        """Export metrics in Prometheus format"""
        output = []
        output.append(f"# HELP {self.app_name} Project Automata Metrics")
        output.append(f"# TYPE {self.app_name} gauge")
        output.append("")

        for metric_name, metric in self.metrics.items():
            # Add TYPE comment
            output.append(f"# TYPE {metric_name} {metric.type.value}")

            # Format labels
            label_str = ""
            if metric.labels:
                labels = [f'{k}="{v}"' for k, v in metric.labels.items()]
                label_str = "{" + ",".join(labels) + "}"

            # Add metric line
            output.append(f"{metric_name}{label_str} {metric.value}")

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


# Global metrics instance
_metrics = MetricsCollector()


# Convenience functions
def increment_counter(name: str, value: float = 1.0, labels: Optional[Dict] = None):
    """Increment a counter metric"""
    _metrics.increment_counter(name, value, labels)


def set_gauge(name: str, value: float, labels: Optional[Dict] = None):
    """Set a gauge metric"""
    _metrics.set_gauge(name, value, labels)


def start_timer(name: str) -> float:
    """Start a timer"""
    return _metrics.start_timer(name)


def stop_timer(name: str, start_time: float, labels: Optional[Dict] = None) -> float:
    """Stop a timer and return duration in ms"""
    return _metrics.stop_timer(name, start_time, labels)


def record_histogram(name: str, value: float, labels: Optional[Dict] = None):
    """Record a histogram value"""
    _metrics.record_histogram(name, value, labels)


def get_metrics() -> MetricsCollector:
    """Get global metrics instance"""
    return _metrics


def export_prometheus() -> str:
    """Export metrics in Prometheus format"""
    return _metrics.export_prometheus()


def log_summary():
    """Log metrics summary"""
    _metrics.log_summary()


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

    # Counter example
    metrics.increment_counter("workflows_generated", 5.0)
    metrics.increment_counter("workflows_generated", 3.0)
    print(f"Workflows generated: {metrics.get_counter('workflows_generated')}")

    # Gauge example
    metrics.set_gauge("active_tasks", 42)
    print(f"Active tasks: {metrics.get_gauge('active_tasks')}")

    # Timer example
    start = metrics.start_timer("workflow_generation")
    time.sleep(0.01)  # Simulate work
    duration = metrics.stop_timer("workflow_generation", start)
    print(f"Generation time: {duration:.2f}ms")

    # Get stats
    stats = metrics.get_timer_stats("workflow_generation")
    print(f"Generation stats: {stats}")

    # Export
    print("\nPrometheus Export:")
    print(metrics.export_prometheus())

    print("\nMetrics Summary:")
    import json

    print(json.dumps(metrics.get_summary(), indent=2))
