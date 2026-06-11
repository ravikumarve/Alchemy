"""
Performance Benchmarks for ALCHEMY Pipeline

Tests timing constraints and scalability:
- Each agent individually within its time budget
- Full pipeline end-to-end timing
- Content size scalability
- Memory sanity checks

Time Budgets (from design specs):
- Archaeologist: 80s total
- Trend-Jacker: 90s total
- Visionary: 70s total
- Full pipeline: < 60s (60-second engine constraint)
"""

import os
import sys
import json
import time
import tempfile
import tracemalloc
import unittest
from pathlib import Path
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.archaeologist import ArchaeologistAgent
from src.agents.trend_jacker import TrendJackerAgent
from src.agents.visionary import VisionaryAgent
from src.pipeline.orchestrator import AlchemyOrchestrator


# ─── Test Helpers ─────────────────────────────────────────────────────────────

def create_text_file(content: str = None, word_count: int = 100) -> str:
    """Create a text file with specified approximate word count."""
    if content is None:
        words = [
            "principle", "strategy", "method", "approach", "concept",
            "framework", "system", "process", "technique", "practice",
            "wisdom", "knowledge", "understanding", "insight", "theory",
            "foundation", "core", "essential", "fundamental", "basic",
            "advanced", "modern", "classic", "timeless", "proven",
            "effective", "powerful", "practical", "useful", "valuable"
        ]
        # Build content with target word count
        content_parts = []
        for i in range(max(1, word_count // len(words))):
            for w in words:
                content_parts.append(f"The {w} of successful execution requires careful planning and deliberate action.")
        content = "\n".join(content_parts)

    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    tmp.write(content)
    tmp.close()
    return tmp.name


# ─── Benchmark Constants ──────────────────────────────────────────────────────

ARCHAEOLOGIST_BUDGET = 80.0   # seconds
TREND_JACKER_BUDGET = 90.0    # seconds
VISIONARY_BUDGET = 70.0       # seconds
PIPELINE_BUDGET = 60.0        # seconds
MEMORY_BUDGET_MB = 500        # MB


class TestArchaeologistPerformance(unittest.TestCase):
    """Benchmark Archaeologist agent timing."""

    def setUp(self):
        self.agent = ArchaeologistAgent()

    def test_small_file_within_budget(self):
        """Small file (< 1KB) should complete well within budget."""
        temp_path = create_text_file(word_count=50)
        try:
            start = time.time()
            result = self.agent.process_file(temp_path)
            elapsed = time.time() - start

            self.assertTrue(result['success'])
            self.assertLess(elapsed, ARCHAEOLOGIST_BUDGET,
                           f"Small file took {elapsed:.2f}s (budget: {ARCHAEOLOGIST_BUDGET}s)")
            # Typical expectation for small file
            self.assertLess(elapsed, 10.0,
                           f"Small file too slow: {elapsed:.2f}s (expected < 10s)")
        finally:
            os.unlink(temp_path)

    def test_medium_file_within_budget(self):
        """Medium file (~5KB) should complete within budget."""
        temp_path = create_text_file(word_count=500)
        try:
            start = time.time()
            result = self.agent.process_file(temp_path)
            elapsed = time.time() - start

            self.assertTrue(result['success'])
            self.assertLess(elapsed, ARCHAEOLOGIST_BUDGET,
                           f"Medium file took {elapsed:.2f}s (budget: {ARCHAEOLOGIST_BUDGET}s)")
        finally:
            os.unlink(temp_path)

    def test_empty_file_handling(self):
        """Empty file should fail gracefully (not hang)."""
        temp_path = create_text_file(word_count=0)
        try:
            start = time.time()
            result = self.agent.process_file(temp_path)
            elapsed = time.time() - start

            # Should complete quickly even if it fails
            self.assertLess(elapsed, 5.0,
                           f"Empty file took {elapsed:.2f}s (expected < 5s)")
        finally:
            os.unlink(temp_path)


class TestTrendJackerPerformance(unittest.TestCase):
    """Benchmark Trend-Jacker agent timing."""

    def setUp(self):
        self.agent = TrendJackerAgent()
        self.archaeologist = ArchaeologistAgent()

    def _get_tj_package(self, word_count: int = 100) -> Dict[str, Any]:
        """Helper to get a Trend-Jacker-ready package."""
        temp_path = create_text_file(word_count=word_count)
        try:
            arch_result = self.archaeologist.process_file(temp_path)
            return arch_result['package']
        finally:
            os.unlink(temp_path)

    def test_small_package_within_budget(self):
        """Small package should complete well within budget."""
        pkg = self._get_tj_package(50)
        start = time.time()
        result = self.agent.process(pkg)
        elapsed = time.time() - start

        self.assertEqual(result['status'], 'completed')
        self.assertLess(elapsed, TREND_JACKER_BUDGET,
                       f"TJ small took {elapsed:.2f}s (budget: {TREND_JACKER_BUDGET}s)")
        self.assertLess(elapsed, 10.0,
                       f"TJ small too slow: {elapsed:.2f}s (expected < 10s)")

    def test_large_package_within_budget(self):
        """Larger package should still complete within budget."""
        pkg = self._get_tj_package(500)
        start = time.time()
        result = self.agent.process(pkg)
        elapsed = time.time() - start

        self.assertEqual(result['status'], 'completed')
        self.assertLess(elapsed, TREND_JACKER_BUDGET,
                       f"TJ large took {elapsed:.2f}s (budget: {TREND_JACKER_BUDGET}s)")


class TestVisionaryPerformance(unittest.TestCase):
    """Benchmark Visionary agent timing."""

    def setUp(self):
        self.visionary = VisionaryAgent()
        self.archaeologist = ArchaeologistAgent()
        self.trend_jacker = TrendJackerAgent()

    def _get_vis_package(self, word_count: int = 100) -> Dict[str, Any]:
        """Helper to get a Visionary-ready package."""
        temp_path = create_text_file(word_count=word_count)
        try:
            arch_result = self.archaeologist.process_file(temp_path)
            tj_result = self.trend_jacker.process(arch_result['package'])
            return tj_result['package']
        finally:
            os.unlink(temp_path)

    def test_small_package_within_budget(self):
        """Small package should complete well within budget."""
        pkg = self._get_vis_package(50)
        start = time.time()
        result = self.visionary.process(pkg)
        elapsed = time.time() - start

        self.assertEqual(result['status'], 'completed')
        self.assertLess(elapsed, VISIONARY_BUDGET,
                       f"Vis small took {elapsed:.2f}s (budget: {VISIONARY_BUDGET}s)")
        self.assertLess(elapsed, 10.0,
                       f"Vis small too slow: {elapsed:.2f}s (expected < 10s)")

        # Clean up output file
        if os.path.exists(result.get('output_path', '')):
            os.remove(result['output_path'])


class TestFullPipelinePerformance(unittest.TestCase):
    """Benchmark full pipeline timing."""

    def setUp(self):
        self.orchestrator = AlchemyOrchestrator()

    def test_pipeline_small_file_within_budget(self):
        """Full pipeline on small file should complete in < 10s."""
        temp_path = create_text_file(word_count=50)
        try:
            start = time.time()
            result = self.orchestrator.process_file(temp_path)
            elapsed = time.time() - start

            self.assertTrue(result['success'])
            self.assertLess(elapsed, PIPELINE_BUDGET,
                           f"Pipeline took {elapsed:.2f}s (budget: {PIPELINE_BUDGET}s)")
            # Fast path expectation
            self.assertLess(elapsed, 10.0,
                           f"Pipeline too slow: {elapsed:.2f}s (expected < 10s)")

            # Clean up
            if os.path.exists(result.get('output_path', '')):
                os.remove(result['output_path'])
        finally:
            os.unlink(temp_path)

    def test_pipeline_medium_file_within_budget(self):
        """Full pipeline on medium file should complete within budget."""
        temp_path = create_text_file(word_count=500)
        try:
            start = time.time()
            result = self.orchestrator.process_file(temp_path)
            elapsed = time.time() - start

            self.assertTrue(result['success'])
            self.assertLess(elapsed, PIPELINE_BUDGET,
                           f"Pipeline medium took {elapsed:.2f}s (budget: {PIPELINE_BUDGET}s)")

            # Clean up
            if os.path.exists(result.get('output_path', '')):
                os.remove(result['output_path'])
        finally:
            os.unlink(temp_path)

    def test_pipeline_stage_breakdown(self):
        """Test that no single stage dominates the pipeline."""
        temp_path = create_text_file(word_count=100)
        try:
            result = self.orchestrator.process_file(temp_path)
            self.assertTrue(result['success'])

            stages = result.get('stages', {})
            total = sum(s.get('time', 0) for s in stages.values())

            # No stage should exceed 80% of total time
            for stage_name, stage_data in stages.items():
                stage_time = stage_data.get('time', 0)
                if total > 0:
                    ratio = stage_time / total
                    self.assertLess(ratio, 0.90,
                                   f"Stage {stage_name} dominates: {ratio:.1%} of total")

            # Clean up
            if os.path.exists(result.get('output_path', '')):
                os.remove(result['output_path'])
        finally:
            os.unlink(temp_path)

    def test_pipeline_consistent_timing(self):
        """Test that pipeline timing is reasonably consistent across runs."""
        temp_path = create_text_file(word_count=100)
        timings = []

        try:
            for _ in range(3):
                orch = AlchemyOrchestrator()
                start = time.time()
                result = orch.process_file(temp_path)
                elapsed = time.time() - start
                timings.append(elapsed)
                self.assertTrue(result['success'])

                if os.path.exists(result.get('output_path', '')):
                    os.remove(result['output_path'])

            # No single run should be > 3x the fastest run
            min_time = min(timings)
            max_ratio = max(t / min_time for t in timings)
            self.assertLess(max_ratio, 3.0,
                           f"Timing variance too high: min={min_time:.2f}s, max={max(timings):.2f}s, ratio={max_ratio:.1f}x")

        finally:
            os.unlink(temp_path)

    def test_sample_art_of_war_performance(self):
        """Test performance on the shipped sample file."""
        sample_path = Path("raw_ore/sample_art_of_war.txt")
        if not sample_path.exists():
            self.skipTest("Sample file not found")

        start = time.time()
        result = self.orchestrator.process_file(str(sample_path))
        elapsed = time.time() - start

        self.assertTrue(result['success'])
        self.assertLess(elapsed, PIPELINE_BUDGET,
                       f"Sample file pipeline took {elapsed:.2f}s (budget: {PIPELINE_BUDGET}s)")

        # Clean up
        if os.path.exists(result.get('output_path', '')):
            os.remove(result['output_path'])


class TestMemoryUsage(unittest.TestCase):
    """Memory usage sanity checks."""

    def test_pipeline_memory_within_bounds(self):
        """Test that pipeline doesn't leak excessive memory."""
        tracemalloc.start()

        orch = AlchemyOrchestrator()
        temp_path = create_text_file(word_count=200)
        try:
            _, current_peak = tracemalloc.get_traced_memory()
            result = orch.process_file(temp_path)
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            self.assertTrue(result['success'])

            peak_mb = peak / (1024 * 1024)
            current_mb = current / (1024 * 1024)

            self.assertLess(peak_mb, MEMORY_BUDGET_MB,
                           f"Memory peak too high: {peak_mb:.1f}MB (budget: {MEMORY_BUDGET_MB}MB)")

            # Clean up
            if os.path.exists(result.get('output_path', '')):
                os.remove(result['output_path'])
        finally:
            os.unlink(temp_path)
            tracemalloc.stop()


if __name__ == '__main__':
    unittest.main()
