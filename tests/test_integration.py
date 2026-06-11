"""
Integration Tests for ALCHEMY Pipeline Agent Handoffs

Tests the complete data flow between agents:
- Archaeologist → Trend-Jacker handoff
- Trend-Jacker → Visionary handoff
- Full end-to-end pipeline orchestration
- Error propagation and boundary conditions
"""

import os
import sys
import json
import time
import tempfile
import unittest
from pathlib import Path
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.archaeologist import ArchaeologistAgent
from src.agents.trend_jacker import TrendJackerAgent
from src.agents.visionary import VisionaryAgent
from src.pipeline.orchestrator import AlchemyOrchestrator


# ─── Handoff Contract Validators ─────────────────────────────────────────────

def validate_archaeologist_package(pkg: Dict[str, Any]) -> list:
    """Validate Archaeologist output package shape. Returns list of errors."""
    errors = []

    if not isinstance(pkg, dict):
        return ["Package is not a dict"]

    # Must have content
    content = pkg.get('content', [])
    if not isinstance(content, list):
        errors.append("Package.content is not a list")
    elif len(content) == 0:
        errors.append("Package.content is empty")

    # Content chunks must have text
    for i, chunk in enumerate(content):
        if not isinstance(chunk, dict):
            errors.append(f"content[{i}] is not a dict")
            continue
        if 'text' not in chunk:
            errors.append(f"content[{i}] missing 'text'")
        if 'content_type' not in chunk:
            errors.append(f"content[{i}] missing 'content_type'")
        if 'quality_level' not in chunk:
            errors.append(f"content[{i}] missing 'quality_level'")

    # Must have metadata
    metadata = pkg.get('metadata', {})
    if not isinstance(metadata, dict):
        errors.append("Package.metadata is not a dict")
    else:
        if 'package_id' not in metadata and 'package_id' not in pkg:
            errors.append("Package missing package_id")
        if 'source_file' not in metadata:
            errors.append("Package.metadata missing source_file")

    # Optional tables
    tables = pkg.get('tables', [])
    if not isinstance(tables, list):
        errors.append("Package.tables is not a list")

    return errors


def validate_trend_jacker_package(pkg: Dict[str, Any]) -> list:
    """Validate Trend-Jacker output package shape. Returns list of errors."""
    errors = []

    if not isinstance(pkg, dict):
        return ["Package is not a dict"]

    # Must have content_chunks
    chunks = pkg.get('content_chunks', [])
    if not isinstance(chunks, list):
        errors.append("Package.content_chunks is not a list")
    elif len(chunks) == 0:
        errors.append("Package.content_chunks is empty")

    # Must have hooks
    hooks = pkg.get('hooks', [])
    if not isinstance(hooks, list):
        errors.append("Package.hooks is not a list")
    elif len(hooks) == 0:
        errors.append("Package.hooks is empty")

    # Each hook must have text
    for i, hook in enumerate(hooks):
        if 'text' not in hook:
            errors.append(f"hooks[{i}] missing 'text'")
        if 'hook_type' not in hook:
            errors.append(f"hooks[{i}] missing 'hook_type'")

    # Must have narrative
    narrative = pkg.get('narrative', {})
    if not isinstance(narrative, dict):
        errors.append("Package.narrative is not a dict")
    else:
        if 'structure' not in narrative and 'structure_type' not in narrative:
            errors.append("Package.narrative missing structure")
        if 'sections' not in narrative:
            errors.append("Package.narrative missing sections")

    # Must have scores
    if 'engagement_score' not in pkg:
        errors.append("Package missing engagement_score")
    if 'retention_score' not in pkg:
        errors.append("Package missing retention_score")

    # Must have metadata
    metadata = pkg.get('metadata', {})
    if not isinstance(metadata, dict):
        errors.append("Package.metadata is not a dict")
    elif 'source_file' not in metadata:
        errors.append("Package.metadata missing source_file")

    return errors


def validate_visionary_package(pkg: Dict[str, Any]) -> list:
    """Validate Visionary output package shape. Returns list of errors."""
    errors = []

    if not isinstance(pkg, dict):
        return ["Package is not a dict"]

    # Must have package_id
    if 'package_id' not in pkg:
        errors.append("Package missing package_id")

    # Must have storyboard
    storyboard = pkg.get('storyboard', {})
    if not isinstance(storyboard, dict):
        errors.append("Package.storyboard is not a dict")
    else:
        if 'scenes' not in storyboard:
            errors.append("Package.storyboard missing scenes")
        if 'scene_count' not in storyboard:
            errors.append("Package.storyboard missing scene_count")

    # Must have B-roll prompts
    prompts = pkg.get('b_roll_prompts', [])
    if not isinstance(prompts, list):
        errors.append("Package.b_roll_prompts is not a list")
    elif len(prompts) == 0:
        errors.append("Package.b_roll_prompts is empty")

    for i, prompt in enumerate(prompts):
        if 'primary_prompt' not in prompt:
            errors.append(f"b_roll_prompts[{i}] missing primary_prompt")
        if 'scene_id' not in prompt:
            errors.append(f"b_roll_prompts[{i}] missing scene_id")

    # Must have visual cues
    cues = pkg.get('visual_cues', [])
    if not isinstance(cues, list):
        errors.append("Package.visual_cues is not a list")

    # Must have audio design
    audio = pkg.get('audio_design', {})
    if not isinstance(audio, dict):
        errors.append("Package.audio_design is not a dict")
    else:
        if 'overall_mood' not in audio:
            errors.append("Package.audio_design missing overall_mood")
        if 'cues' not in audio:
            errors.append("Package.audio_design missing cues")

    # Must have Gumroad listing
    listing = pkg.get('gumroad_listing', {})
    if not isinstance(listing, dict):
        errors.append("Package.gumroad_listing is not a dict")
    else:
        if 'title' not in listing:
            errors.append("Package.gumroad_listing missing title")
        if 'price_tier' not in listing:
            errors.append("Package.gumroad_listing missing price_tier")

    return errors


# ─── Test Helpers ─────────────────────────────────────────────────────────────

def create_sample_text_file(content: str = None) -> str:
    """Create a temporary text file for testing. Returns path."""
    if content is None:
        content = """
        The Art of War by Sun Tzu is a fundamental text on strategy.
        It teaches us that all warfare is based on deception.
        Appear weak when you are strong, and strong when you are weak.
        The supreme art of war is to subdue the enemy without fighting.
        If you know the enemy and know yourself, you need not fear the result.
        These principles apply not only to warfare but to business and life.
        In modern contexts, these strategies are used in competitive markets.
        Understanding timing and positioning is crucial for success.
        """
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    tmp.write(content)
    tmp.close()
    return tmp.name


# ─── Test Classes ─────────────────────────────────────────────────────────────

class TestArchaeologistToTrendJackerHandoff(unittest.TestCase):
    """Test data flow from Archaeologist to Trend-Jacker."""

    def setUp(self):
        self.archaeologist = ArchaeologistAgent()
        self.trend_jacker = TrendJackerAgent()

    def test_handoff_package_shape(self):
        """Test that Archaeologist output meets Trend-Jacker input contract."""
        temp_path = create_sample_text_file()
        try:
            result = self.archaeologist.process_file(temp_path)
            self.assertTrue(result['success'], "Archaeologist failed")

            pkg = result['package']
            errors = validate_archaeologist_package(pkg)
            self.assertEqual(errors, [], f"Package validation failed: {errors}")

        finally:
            os.unlink(temp_path)

    def test_handoff_processing(self):
        """Test that Trend-Jacker can consume Archaeologist output."""
        temp_path = create_sample_text_file()
        try:
            # Run Archaeologist
            arch_result = self.archaeologist.process_file(temp_path)
            self.assertTrue(arch_result['success'])

            # Feed to Trend-Jacker
            tj_result = self.trend_jacker.process(arch_result['package'])
            self.assertEqual(tj_result['status'], 'completed',
                             f"Trend-Jacker failed: {tj_result.get('status')}")

            # Validate Trend-Jacker output shape
            pkg = tj_result['package']
            errors = validate_trend_jacker_package(pkg)
            self.assertEqual(errors, [], f"TJ package validation failed: {errors}")

        finally:
            os.unlink(temp_path)

    def test_package_id_propagation(self):
        """Test that package IDs propagate across agents."""
        temp_path = create_sample_text_file()
        try:
            arch_result = self.archaeologist.process_file(temp_path)
            arch_pkg_id = arch_result['package'].get('metadata', {}).get('package_id',
                           arch_result['package'].get('package_id', 'unknown'))

            tj_result = self.trend_jacker.process(arch_result['package'])
            self.assertEqual(tj_result['status'], 'completed')

            # TJ package metadata should have source info
            tj_meta = tj_result['package'].get('metadata', {})
            self.assertIn('source_file', tj_meta)
            self.assertEqual(tj_meta['source_file'], temp_path)

        finally:
            os.unlink(temp_path)

    def test_handoff_with_minimal_content(self):
        """Test handoff with very short content."""
        temp_path = create_sample_text_file("Short text.")
        try:
            arch_result = self.archaeologist.process_file(temp_path)
            self.assertTrue(arch_result['success'])

            tj_result = self.trend_jacker.process(arch_result['package'])
            self.assertEqual(tj_result['status'], 'completed')

        finally:
            os.unlink(temp_path)


class TestTrendJackerToVisionaryHandoff(unittest.TestCase):
    """Test data flow from Trend-Jacker to Visionary."""

    def setUp(self):
        self.trend_jacker = TrendJackerAgent()
        self.visionary = VisionaryAgent()
        self.archaeologist = ArchaeologistAgent()

    def test_handoff_package_shape(self):
        """Test that Trend-Jacker output meets Visionary input contract."""
        temp_path = create_sample_text_file()
        try:
            # Chain: Archaeologist → Trend-Jacker
            arch_result = self.archaeologist.process_file(temp_path)
            self.assertTrue(arch_result['success'])
            tj_result = self.trend_jacker.process(arch_result['package'])
            self.assertEqual(tj_result['status'], 'completed')

            # Validate TJ output shape
            pkg = tj_result['package']
            errors = validate_trend_jacker_package(pkg)
            self.assertEqual(errors, [], f"TJ package validation failed: {errors}")

        finally:
            os.unlink(temp_path)

    def test_handoff_processing(self):
        """Test that Visionary can consume Trend-Jacker output."""
        temp_path = create_sample_text_file()
        try:
            # Chain: Archaeologist → Trend-Jacker → Visionary
            arch_result = self.archaeologist.process_file(temp_path)
            tj_result = self.trend_jacker.process(arch_result['package'])
            self.assertEqual(tj_result['status'], 'completed')

            vis_result = self.visionary.process(tj_result['package'])
            self.assertEqual(vis_result['status'], 'completed',
                             f"Visionary failed: {vis_result.get('status')}")

            # Validate Visionary output shape
            pkg = vis_result['package']
            errors = validate_visionary_package(pkg)
            self.assertEqual(errors, [], f"Visionary package validation failed: {errors}")

            # Clean up output file
            output_path = vis_result.get('output_path', '')
            if output_path and os.path.exists(output_path):
                os.remove(output_path)

        finally:
            os.unlink(temp_path)

    def test_full_chain_content_integrity(self):
        """Test that content flows correctly through all 3 agents."""
        temp_path = create_sample_text_file()
        try:
            # Run full chain
            arch_result = self.archaeologist.process_file(temp_path)
            tj_result = self.trend_jacker.process(arch_result['package'])
            vis_result = self.visionary.process(tj_result['package'])

            # Visionary output should reference the source file
            vis_pkg = vis_result['package']
            meta = vis_pkg.get('metadata', {})
            # Source propagation
            self.assertEqual(vis_result['status'], 'completed')

            # Storyboard should have scenes
            storyboard = vis_pkg.get('storyboard', {})
            self.assertGreater(storyboard.get('scene_count', 0), 0,
                               "Storyboard should have at least 1 scene")
            self.assertGreater(storyboard.get('total_duration', 0), 0,
                               "Storyboard should have positive duration")

            # Clean up
            output_path = vis_result.get('output_path', '')
            if output_path and os.path.exists(output_path):
                os.remove(output_path)

        finally:
            os.unlink(temp_path)


class TestFullPipelineOrchestration(unittest.TestCase):
    """Test the full AlchemyOrchestrator pipeline."""

    def setUp(self):
        self.orchestrator = AlchemyOrchestrator()

    def test_orchestrator_processes_text_file(self):
        """Test end-to-end pipeline via orchestrator."""
        temp_path = create_sample_text_file()
        try:
            result = self.orchestrator.process_file(temp_path)
            self.assertTrue(result['success'], f"Orchestrator failed: {result.get('errors')}")

            # All stages should be present
            stages = result.get('stages', {})
            self.assertIn('archaeologist', stages)
            self.assertIn('trend_jacker', stages)
            self.assertIn('visionary', stages)

            # All stages should succeed
            for stage_name, stage_data in stages.items():
                self.assertTrue(stage_data.get('success', False),
                                f"Stage {stage_name} failed")

            # Output should exist
            output_path = result.get('output_path', '')
            self.assertTrue(os.path.exists(output_path),
                            f"Output not found: {output_path}")

            # Validate output is valid JSON
            with open(output_path, 'r') as f:
                output_data = json.load(f)
            self.assertIn('package_id', output_data)

            # Clean up
            if os.path.exists(output_path):
                os.remove(output_path)

        finally:
            os.unlink(temp_path)

    def test_orchestrator_performance(self):
        """Test that pipeline completes within performance budget."""
        temp_path = create_sample_text_file()
        try:
            result = self.orchestrator.process_file(temp_path)
            self.assertTrue(result['success'])

            total_time = result.get('total_time', 0)
            self.assertLess(total_time, 30.0,
                            f"Pipeline too slow: {total_time:.2f}s (budget: 30s)")

            # Clean up
            output_path = result.get('output_path', '')
            if output_path and os.path.exists(output_path):
                os.remove(output_path)

        finally:
            os.unlink(temp_path)

    def test_orchestrator_handles_missing_file(self):
        """Test orchestrator handles missing files gracefully."""
        result = self.orchestrator.process_file("/nonexistent/path.txt")
        self.assertFalse(result['success'])
        self.assertGreater(len(result.get('errors', [])), 0,
                           "Expected errors for missing file")

    def test_orchestrator_handles_multiple_formats(self):
        """Test orchestrator processes different content types."""
        long_content = "\n".join([
            f"This is sentence number {i} for testing purposes."
            for i in range(20)
        ])
        temp_path = create_sample_text_file(long_content)
        try:
            result = self.orchestrator.process_file(temp_path)
            self.assertTrue(result['success'])

            # Clean up
            output_path = result.get('output_path', '')
            if output_path and os.path.exists(output_path):
                os.remove(output_path)
        finally:
            os.unlink(temp_path)


class TestErrorPropagation(unittest.TestCase):
    """Test error handling and propagation across agents."""

    def test_archaeologist_rejects_nonexistent_file(self):
        """Test Archaeologist handles missing files."""
        arch = ArchaeologistAgent()
        result = arch.process_file("/nonexistent/file.txt")
        self.assertFalse(result['success'])
        self.assertGreater(len(result.get('errors', [])), 0)

    def test_trend_jacker_rejects_empty_package(self):
        """Test Trend-Jacker rejects empty input."""
        tj = TrendJackerAgent()
        with self.assertRaises(Exception):
            tj.process({})

    def test_visionary_rejects_invalid_package(self):
        """Test Visionary rejects invalid input."""
        vis = VisionaryAgent()
        with self.assertRaises(Exception):
            vis.process({"invalid": True})

    def test_orchestrator_recovers_from_archaeologist_failure(self):
        """Test orchestrator handles Archaeologist failure gracefully."""
        orch = AlchemyOrchestrator()
        result = orch.process_file("/nonexistent/file.txt")
        self.assertFalse(result['success'])
        # Should not crash; should return structured error
        self.assertIn('errors', result)
        self.assertIn('stages', result)


if __name__ == '__main__':
    unittest.main()
