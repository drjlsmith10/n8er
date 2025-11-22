"""Benchmark knowledge base performance

Measures performance of knowledge base operations:
- Lookup speed
- Search performance
- Memory usage
- Export/import time
"""

import json
import logging
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from skills.knowledge_base import KnowledgeBase, WorkflowPattern, NodeInsight, ErrorPattern
except ImportError as e:
    print(f"ERROR: Could not import KnowledgeBase: {e}")
    sys.exit(1)

# Application should configure logging, not benchmark modules
# logging.basicConfig() removed to prevent global logging configuration conflicts
logger = logging.getLogger(__name__)


class KnowledgeBaseBenchmark:
    """Benchmark knowledge base performance"""

    def __init__(self):
        """Initialize benchmark"""
        self.kb = KnowledgeBase()
        self.results = {
            "insertion": {},
            "lookup": {},
            "search": {},
            "export": {},
            "summary": {},
        }
        self._populate_kb()

    def _populate_kb(self):
        """Populate knowledge base with test data"""
        # Add patterns
        for i in range(100):
            pattern = WorkflowPattern(
                name=f"pattern_{i}",
                description=f"Test pattern {i}",
                trigger=["webhook", "cron"][i % 2],
                actions=["slack", "email", "database"][i % 3:],
                use_cases=[f"use_case_{i}", f"use_case_{i+1}"],
            )
            self.kb.add_workflow_pattern(pattern)

        # Add node insights
        for i in range(50):
            insight = NodeInsight(
                node_type=f"n8n-nodes-base.node_{i}",
                typeVersion=i % 5 + 1,
                parameters=[f"param_{j}" for j in range(5)],
                common_mistakes=[f"mistake_{j}" for j in range(3)],
            )
            self.kb.add_node_insight(insight)

        # Add error patterns
        for i in range(50):
            error = ErrorPattern(
                error_type=f"error_type_{i}",
                common_causes=[f"cause_{j}" for j in range(3)],
                solutions=[f"solution_{j}" for j in range(2)],
            )
            self.kb.add_error_pattern(error)

    def benchmark_pattern_lookup(self, iterations=1000):
        """Benchmark pattern lookup performance"""
        logger.info(f"Benchmarking pattern lookup ({iterations} iterations)...")

        times = []
        pattern_names = [f"pattern_{i}" for i in range(100)]

        for _ in range(iterations):
            start = time.time()
            pattern = self.kb.get_workflow_pattern(pattern_names[_ % 100])
            times.append(time.time() - start)

        self.results["lookup"] = {
            "iterations": iterations,
            "avg_time_ms": (sum(times) / len(times)) * 1000,
            "min_time_ms": min(times) * 1000,
            "max_time_ms": max(times) * 1000,
            "lookups_per_second": iterations / sum(times),
        }

        logger.info(f"  ✓ Avg time: {self.results['lookup']['avg_time_ms']:.4f}ms")
        logger.info(f"  ✓ Rate: {self.results['lookup']['lookups_per_second']:.0f} lookups/sec")

    def benchmark_pattern_list(self, iterations=100):
        """Benchmark listing all patterns"""
        logger.info(f"Benchmarking pattern listing ({iterations} iterations)...")

        times = []

        for _ in range(iterations):
            start = time.time()
            patterns = self.kb.list_workflow_patterns()
            times.append(time.time() - start)

        self.results["search"] = {
            "iterations": iterations,
            "avg_time_ms": (sum(times) / len(times)) * 1000,
            "pattern_count": len(patterns),
        }

        logger.info(f"  ✓ Avg time: {self.results['search']['avg_time_ms']:.2f}ms")
        logger.info(f"  ✓ Patterns: {len(patterns)}")

    def benchmark_export(self, iterations=50):
        """Benchmark knowledge base export"""
        logger.info(f"Benchmarking export ({iterations} iterations)...")

        times = []
        sizes = []

        for _ in range(iterations):
            start = time.time()
            exported = self.kb.export_knowledge_base()
            elapsed = time.time() - start
            times.append(elapsed)
            sizes.append(len(json.dumps(exported)))

        self.results["export"] = {
            "iterations": iterations,
            "avg_time_ms": (sum(times) / len(times)) * 1000,
            "avg_size_bytes": sum(sizes) / len(sizes),
        }

        logger.info(f"  ✓ Avg time: {self.results['export']['avg_time_ms']:.2f}ms")
        logger.info(f"  ✓ Size: {self.results['export']['avg_size_bytes'] / 1024:.1f}KB")

    def benchmark_node_lookup(self, iterations=1000):
        """Benchmark node insight lookup"""
        logger.info(f"Benchmarking node lookup ({iterations} iterations)...")

        times = []
        node_types = [f"n8n-nodes-base.node_{i}" for i in range(50)]

        for _ in range(iterations):
            start = time.time()
            node = self.kb.get_node_insight(node_types[_ % 50])
            times.append(time.time() - start)

        logger.info(f"  ✓ Avg time: {(sum(times) / len(times)) * 1000:.4f}ms")
        logger.info(f"  ✓ Rate: {iterations / sum(times):.0f} lookups/sec")

    def run_all(self):
        """Run all benchmarks"""
        logger.info("=" * 60)
        logger.info("KNOWLEDGE BASE BENCHMARKS")
        logger.info("=" * 60)

        self.benchmark_pattern_lookup(iterations=1000)
        self.benchmark_node_lookup(iterations=1000)
        self.benchmark_pattern_list(iterations=100)
        self.benchmark_export(iterations=50)

        logger.info("=" * 60)
        logger.info("BENCHMARK SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Pattern lookup: {self.results['lookup']['avg_time_ms']:.4f}ms avg")
        logger.info(f"Pattern listing: {self.results['search']['avg_time_ms']:.2f}ms avg")
        logger.info(f"Export: {self.results['export']['avg_time_ms']:.2f}ms avg")

        return self.results


if __name__ == "__main__":
    benchmark = KnowledgeBaseBenchmark()
    results = benchmark.run_all()

    # Save results
    output_file = Path(__file__).parent / "knowledge_base_results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    logger.info(f"\n✓ Results saved to {output_file}")
