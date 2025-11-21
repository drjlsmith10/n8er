# Prometheus Format Examples

This document shows the **correct Prometheus exposition format** output from the fixed `metrics.py`.

---

## Example 1: Counter Metric

### Code
```python
from skills.metrics import MetricsCollector

metrics = MetricsCollector('demo')
metrics.increment_counter(
    'http_requests',
    42,
    labels={'method': 'GET', 'status': '200'},
    help_text='Total HTTP requests'
)
```

### Output
```prometheus
# HELP demo_http_requests_total Total HTTP requests
# TYPE demo_http_requests_total counter
demo_http_requests_total{method="GET",status="200"} 42.0
```

### Key Features
✅ HELP comment with description
✅ TYPE comment with metric type
✅ Automatic `_total` suffix for counters
✅ Labels sorted alphabetically
✅ Labels properly quoted

---

## Example 2: Gauge Metric

### Code
```python
metrics.set_gauge('temperature_celsius', 23.5, help_text='Current temperature')
```

### Output
```prometheus
# HELP demo_temperature_celsius Current temperature
# TYPE demo_temperature_celsius gauge
demo_temperature_celsius 23.5
```

### Key Features
✅ Simple value format for gauges
✅ HELP and TYPE comments

---

## Example 3: Histogram Metric

### Code
```python
for val in [0.01, 0.05, 0.1, 0.5]:
    metrics.record_histogram(
        'latency_seconds',
        val,
        buckets=[0.005, 0.01, 0.05, 0.1, 0.5, 1.0],
        help_text='Request latency'
    )
```

### Output
```prometheus
# HELP demo_latency_seconds Request latency
# TYPE demo_latency_seconds histogram
demo_latency_seconds_bucket{le="0.005"} 0
demo_latency_seconds_bucket{le="0.01"} 1
demo_latency_seconds_bucket{le="0.05"} 2
demo_latency_seconds_bucket{le="0.1"} 3
demo_latency_seconds_bucket{le="0.5"} 4
demo_latency_seconds_bucket{le="1.0"} 4
demo_latency_seconds_bucket{le="+Inf"} 4
demo_latency_seconds_sum 0.66
demo_latency_seconds_count 4
```

### Key Features
✅ Bucket lines with `le` label
✅ Cumulative bucket counts (1, 2, 3, 4...)
✅ +Inf bucket with total count
✅ _sum line with total sum
✅ _count line with observation count

---

## Example 4: Timer Metric

### Code
```python
import time

start = metrics.start_timer('operation')
time.sleep(0.001)
metrics.stop_timer(
    'operation',
    start,
    labels={'type': 'database'},
    help_text='Operation duration'
)
```

### Output
```prometheus
# HELP demo_operation_seconds Operation duration
# TYPE demo_operation_seconds histogram
demo_operation_seconds_bucket{le="0.005",type="database"} 1
demo_operation_seconds_bucket{le="0.01",type="database"} 1
demo_operation_seconds_bucket{le="0.025",type="database"} 1
demo_operation_seconds_bucket{le="0.05",type="database"} 1
demo_operation_seconds_bucket{le="0.075",type="database"} 1
demo_operation_seconds_bucket{le="0.1",type="database"} 1
demo_operation_seconds_bucket{le="0.25",type="database"} 1
demo_operation_seconds_bucket{le="0.5",type="database"} 1
demo_operation_seconds_bucket{le="0.75",type="database"} 1
demo_operation_seconds_bucket{le="1.0",type="database"} 1
demo_operation_seconds_bucket{le="2.5",type="database"} 1
demo_operation_seconds_bucket{le="5.0",type="database"} 1
demo_operation_seconds_bucket{le="7.5",type="database"} 1
demo_operation_seconds_bucket{le="10.0",type="database"} 1
demo_operation_seconds_bucket{le="+Inf",type="database"} 1
demo_operation_seconds_sum{type="database"} 0.0014699030000429048
demo_operation_seconds_count{type="database"} 1
```

### Key Features
✅ Automatic `_seconds` suffix for timers
✅ Uses seconds (not milliseconds)
✅ Exported as histogram with default buckets
✅ Labels properly included in all lines

---

## Example 5: Multiple Metrics

### Code
```python
# Counter
metrics.increment_counter('requests', 100, help_text='Total requests')

# Gauge
metrics.set_gauge('active_connections', 42, help_text='Active connections')

# Histogram
metrics.record_histogram('request_size_bytes', 1024, help_text='Request size')
```

### Output
```prometheus
# HELP demo_active_connections Active connections
# TYPE demo_active_connections gauge
demo_active_connections 42

# HELP demo_request_size_bytes Request size
# TYPE demo_request_size_bytes histogram
demo_request_size_bytes_bucket{le="0.005"} 0
demo_request_size_bytes_bucket{le="0.01"} 0
...
demo_request_size_bytes_bucket{le="+Inf"} 1
demo_request_size_bytes_sum 1024
demo_request_size_bytes_count 1

# HELP demo_requests_total Total requests
# TYPE demo_requests_total counter
demo_requests_total 100.0

```

### Key Features
✅ Blank line between metric families
✅ Each metric has its own HELP and TYPE
✅ Metrics sorted alphabetically

---

## Example 6: Special Characters (Sanitization)

### Code
```python
# Metric names with dots and dashes
metrics.increment_counter('workflow.execution.success', 10)
metrics.set_gauge('queue-depth', 5)

# Labels with special characters
metrics.increment_counter(
    'api_calls',
    1,
    labels={'endpoint': '/api/v1/users', 'status-code': '200'}
)
```

### Output
```prometheus
# HELP demo_api_calls_total Counter metric for api_calls_total
# TYPE demo_api_calls_total counter
demo_api_calls_total{endpoint="/api/v1/users",status_code="200"} 1.0

# HELP demo_queue_depth Gauge metric for queue_depth
# TYPE demo_queue_depth gauge
demo_queue_depth 5

# HELP demo_workflow_execution_success_total Counter metric for workflow_execution_success_total
# TYPE demo_workflow_execution_success_total counter
demo_workflow_execution_success_total 10.0

```

### Key Features
✅ Dots replaced with underscores: `workflow.execution` → `workflow_execution`
✅ Dashes replaced with underscores: `queue-depth` → `queue_depth`
✅ Label names sanitized: `status-code` → `status_code`
✅ Special characters in label values preserved: `/api/v1/users`

---

## Validation

All output can be validated using `prometheus_client`:

```python
from prometheus_client.parser import text_string_to_metric_families

output = metrics.export_prometheus()
families = list(text_string_to_metric_families(output))

print(f"✅ Successfully parsed {len(families)} metric families")
```

---

## Prometheus Query Examples

Once scraped by Prometheus, you can query these metrics:

```promql
# Counter - rate of requests per second
rate(demo_http_requests_total[5m])

# Gauge - current value
demo_temperature_celsius

# Histogram - 95th percentile latency
histogram_quantile(0.95, rate(demo_latency_seconds_bucket[5m]))

# Histogram - average latency
rate(demo_latency_seconds_sum[5m]) / rate(demo_latency_seconds_count[5m])
```

---

## References

- [Prometheus Exposition Format](https://prometheus.io/docs/instrumenting/exposition_formats/)
- [Prometheus Metric Naming Best Practices](https://prometheus.io/docs/practices/naming/)
- [Prometheus Metric Types](https://prometheus.io/docs/concepts/metric_types/)
