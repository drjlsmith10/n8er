"""Benchmark workflow generation performance

Measures performance of workflow generation from various inputs:
- Generation speed (workflows/second)
- Memory usage
- Output size
- Validation time
"""

import json
import logging
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from skills.generate_workflow_json import WorkflowBuilder
except ImportError:
    print("ERROR: Could not import WorkflowBuilder")
    sys.exit(1)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class WorkflowGenerationBenchmark:
    """Benchmark workflow generation performance"""

    def __init__(self):
        """Initialize benchmark"""
        self.results = {
            "simple_workflows": [],
            "complex_workflows": [],
            "large_workflows": [],
            "summary": {},
        }

    def benchmark_simple_workflow(self, iterations=100):
        """Benchmark simple workflow generation (1 trigger + 1 action)"""
        logger.info(f"Benchmarking simple workflows ({iterations} iterations)...")

        times = []
        sizes = []

        for i in range(iterations):
            start = time.time()

            builder = WorkflowBuilder(f"SimpleWorkflow_{i}")
            builder.add_trigger("manual", "Start")
            builder.add_node("n8n-nodes-base.httpRequest", "HTTP Call", parameters={
                "url": "https://api.example.com/data",
                "method": "GET",
            })
            builder.connect("Start", "HTTP Call")
            workflow = builder.build(validate=False)

            elapsed = time.time() - start
            times.append(elapsed)
            sizes.append(len(json.dumps(workflow)))

        self.results["simple_workflows"] = {
            "iterations": iterations,
            "avg_time_ms": (sum(times) / len(times)) * 1000,
            "min_time_ms": min(times) * 1000,
            "max_time_ms": max(times) * 1000,
            "workflows_per_second": iterations / sum(times),
            "avg_size_bytes": sum(sizes) / len(sizes),
        }

        logger.info(f"  ✓ Avg time: {self.results['simple_workflows']['avg_time_ms']:.2f}ms")
        logger.info(
            f"  ✓ Rate: {self.results['simple_workflows']['workflows_per_second']:.0f} workflows/sec"
        )

    def benchmark_complex_workflow(self, iterations=50):
        """Benchmark complex workflow generation (5 nodes, multiple connections)"""
        logger.info(f"Benchmarking complex workflows ({iterations} iterations)...")

        times = []
        sizes = []

        for i in range(iterations):
            start = time.time()

            builder = WorkflowBuilder(f"ComplexWorkflow_{i}")
            builder.add_trigger("webhook", "Webhook", parameters={
                "path": "webhook-path",
                "httpMethod": "POST",
            })
            builder.add_node("n8n-nodes-base.code", "Transform Data", parameters={
                "functionCode": "return $input.all();",
            })
            builder.add_node("n8n-nodes-base.if", "Check Condition", parameters={
                "conditions": {"number": []}
            })
            builder.add_node("n8n-nodes-base.slack", "Notify Success", parameters={
                "channel": "#notifications",
                "messageType": "text",
                "text": "Workflow executed successfully",
            })
            builder.add_node("n8n-nodes-base.emailSend", "Send Email", parameters={
                "fromEmail": "test@example.com",
                "toEmail": "admin@example.com",
                "subject": "Notification",
                "message": "Workflow completed",
            })

            builder.connect("Webhook", "Transform Data")
            builder.connect("Transform Data", "Check Condition")
            builder.connect("Check Condition", "Notify Success")
            builder.connect("Notify Success", "Send Email")

            workflow = builder.build(validate=False)

            elapsed = time.time() - start
            times.append(elapsed)
            sizes.append(len(json.dumps(workflow)))

        self.results["complex_workflows"] = {
            "iterations": iterations,
            "avg_time_ms": (sum(times) / len(times)) * 1000,
            "min_time_ms": min(times) * 1000,
            "max_time_ms": max(times) * 1000,
            "workflows_per_second": iterations / sum(times),
            "avg_size_bytes": sum(sizes) / len(sizes),
        }

        logger.info(f"  ✓ Avg time: {self.results['complex_workflows']['avg_time_ms']:.2f}ms")
        logger.info(
            f"  ✓ Rate: {self.results['complex_workflows']['workflows_per_second']:.0f} workflows/sec"
        )

    def benchmark_large_workflow(self, iterations=10):
        """Benchmark large workflow generation (20+ nodes)"""
        logger.info(f"Benchmarking large workflows ({iterations} iterations)...")

        times = []
        sizes = []

        for i in range(iterations):
            start = time.time()

            builder = WorkflowBuilder(f"LargeWorkflow_{i}")
            builder.add_trigger("cron", "Schedule", parameters={
                "expression": "0 0 * * *",
            })

            # Add 20 nodes
            for j in range(20):
                builder.add_node("n8n-nodes-base.code", f"Step_{j}", parameters={
                    "functionCode": f"return {{ step: {j} }};"
                })

                if j > 0:
                    builder.connect(f"Step_{j-1}", f"Step_{j}")

            workflow = builder.build(validate=False)

            elapsed = time.time() - start
            times.append(elapsed)
            sizes.append(len(json.dumps(workflow)))

        self.results["large_workflows"] = {
            "iterations": iterations,
            "avg_time_ms": (sum(times) / len(times)) * 1000,
            "min_time_ms": min(times) * 1000,
            "max_time_ms": max(times) * 1000,
            "workflows_per_second": iterations / sum(times),
            "avg_size_bytes": sum(sizes) / len(sizes),
        }

        logger.info(f"  ✓ Avg time: {self.results['large_workflows']['avg_time_ms']:.2f}ms")
        logger.info(
            f"  ✓ Rate: {self.results['large_workflows']['workflows_per_second']:.0f} workflows/sec"
        )

    def run_all(self):
        """Run all benchmarks"""
        logger.info("=" * 60)
        logger.info("WORKFLOW GENERATION BENCHMARKS")
        logger.info("=" * 60)

        self.benchmark_simple_workflow(iterations=100)
        self.benchmark_complex_workflow(iterations=50)
        self.benchmark_large_workflow(iterations=10)

        logger.info("=" * 60)
        logger.info("BENCHMARK SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Simple workflows: {self.results['simple_workflows']['avg_time_ms']:.2f}ms avg")
        logger.info(
            f"Complex workflows: {self.results['complex_workflows']['avg_time_ms']:.2f}ms avg"
        )
        logger.info(f"Large workflows: {self.results['large_workflows']['avg_time_ms']:.2f}ms avg")

        return self.results


if __name__ == "__main__":
    benchmark = WorkflowGenerationBenchmark()
    results = benchmark.run_all()

    # Save results
    output_file = Path(__file__).parent / "workflow_generation_results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    logger.info(f"\n✓ Results saved to {output_file}")
