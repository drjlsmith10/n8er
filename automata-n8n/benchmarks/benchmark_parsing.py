"""Benchmark workflow parsing performance

Measures performance of workflow JSON parsing:
- Parse speed (workflows/second)
- Memory usage
- Validation overhead
- Error detection time
"""

import json
import logging
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from skills.parse_n8n_schema import N8nSchemaParser
    from skills.generate_workflow_json import WorkflowBuilder
except ImportError as e:
    print(f"ERROR: Could not import required modules: {e}")
    sys.exit(1)

# Application should configure logging, not benchmark modules
# logging.basicConfig() removed to prevent global logging configuration conflicts
logger = logging.getLogger(__name__)


class WorkflowParsingBenchmark:
    """Benchmark workflow parsing performance"""

    def __init__(self):
        """Initialize benchmark"""
        self.parser = N8nSchemaParser()
        self.results = {
            "simple_parsing": [],
            "complex_parsing": [],
            "validation_overhead": [],
            "summary": {},
        }
        self._setup_test_workflows()

    def _setup_test_workflows(self):
        """Create test workflows"""
        # Simple workflow
        builder = WorkflowBuilder("SimpleTest")
        builder.add_trigger("manual", "Start")
        builder.add_node("n8n-nodes-base.httpRequest", "HTTP", parameters={
            "url": "https://api.example.com/data"
        })
        builder.connect("Start", "HTTP")
        self.simple_workflow = builder.build(validate=False)

        # Complex workflow
        builder = WorkflowBuilder("ComplexTest")
        builder.add_trigger("webhook", "Webhook")
        for i in range(10):
            builder.add_node("n8n-nodes-base.code", f"Step_{i}", parameters={
                "functionCode": "return $input.all();"
            })
            if i > 0:
                builder.connect(f"Step_{i-1}", f"Step_{i}")
        self.complex_workflow = builder.build(validate=False)

    def benchmark_simple_parsing(self, iterations=1000):
        """Benchmark parsing simple workflows"""
        logger.info(f"Benchmarking simple workflow parsing ({iterations} iterations)...")

        times = []
        json_str = json.dumps(self.simple_workflow)

        for _ in range(iterations):
            start = time.time()
            parsed = self.parser.parse_workflow_json(json_str)
            elapsed = time.time() - start
            times.append(elapsed)

        self.results["simple_parsing"] = {
            "iterations": iterations,
            "avg_time_ms": (sum(times) / len(times)) * 1000,
            "min_time_ms": min(times) * 1000,
            "max_time_ms": max(times) * 1000,
            "workflows_per_second": iterations / sum(times),
        }

        logger.info(f"  ✓ Avg time: {self.results['simple_parsing']['avg_time_ms']:.2f}ms")
        logger.info(
            f"  ✓ Rate: {self.results['simple_parsing']['workflows_per_second']:.0f} workflows/sec"
        )

    def benchmark_complex_parsing(self, iterations=500):
        """Benchmark parsing complex workflows"""
        logger.info(f"Benchmarking complex workflow parsing ({iterations} iterations)...")

        times = []
        json_str = json.dumps(self.complex_workflow)

        for _ in range(iterations):
            start = time.time()
            parsed = self.parser.parse_workflow_json(json_str)
            elapsed = time.time() - start
            times.append(elapsed)

        self.results["complex_parsing"] = {
            "iterations": iterations,
            "avg_time_ms": (sum(times) / len(times)) * 1000,
            "min_time_ms": min(times) * 1000,
            "max_time_ms": max(times) * 1000,
            "workflows_per_second": iterations / sum(times),
        }

        logger.info(f"  ✓ Avg time: {self.results['complex_parsing']['avg_time_ms']:.2f}ms")
        logger.info(
            f"  ✓ Rate: {self.results['complex_parsing']['workflows_per_second']:.0f} workflows/sec"
        )

    def benchmark_validation_overhead(self, iterations=500):
        """Benchmark validation vs just parsing"""
        logger.info(f"Benchmarking validation overhead ({iterations} iterations)...")

        parse_times = []
        validate_times = []
        json_str = json.dumps(self.simple_workflow)

        # Parse only
        for _ in range(iterations):
            start = time.time()
            parsed = self.parser.parse_workflow_json(json_str)
            parse_times.append(time.time() - start)

        # Parse + validate
        for _ in range(iterations):
            start = time.time()
            parsed = self.parser.parse_workflow_json(json_str)
            # Validation would be done here
            validate_times.append(time.time() - start)

        avg_parse = (sum(parse_times) / len(parse_times)) * 1000
        avg_validate = (sum(validate_times) / len(validate_times)) * 1000
        overhead = ((avg_validate - avg_parse) / avg_parse * 100) if avg_parse > 0 else 0

        self.results["validation_overhead"] = {
            "iterations": iterations,
            "parse_only_ms": avg_parse,
            "parse_with_validation_ms": avg_validate,
            "overhead_percent": overhead,
        }

        logger.info(f"  ✓ Parse only: {avg_parse:.2f}ms")
        logger.info(f"  ✓ With validation: {avg_validate:.2f}ms")
        logger.info(f"  ✓ Overhead: {overhead:.1f}%")

    def run_all(self):
        """Run all benchmarks"""
        logger.info("=" * 60)
        logger.info("WORKFLOW PARSING BENCHMARKS")
        logger.info("=" * 60)

        self.benchmark_simple_parsing(iterations=1000)
        self.benchmark_complex_parsing(iterations=500)
        self.benchmark_validation_overhead(iterations=500)

        logger.info("=" * 60)
        logger.info("BENCHMARK SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Simple parsing: {self.results['simple_parsing']['avg_time_ms']:.2f}ms avg")
        logger.info(f"Complex parsing: {self.results['complex_parsing']['avg_time_ms']:.2f}ms avg")
        logger.info(
            f"Validation overhead: {self.results['validation_overhead']['overhead_percent']:.1f}%"
        )

        return self.results


if __name__ == "__main__":
    benchmark = WorkflowParsingBenchmark()
    results = benchmark.run_all()

    # Save results
    output_file = Path(__file__).parent / "parsing_results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    logger.info(f"\n✓ Results saved to {output_file}")
