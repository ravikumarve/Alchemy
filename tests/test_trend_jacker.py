"""
Unit Tests for Trend-Jacker Agent

Tests all components of the Trend-Jacker workflow:
- Trend Mapper
- Hook Generator
- Narrative Structurer
- Attention Optimizer
- Content Enhancer
- Content Packager
- Main Trend-Jacker orchestration
"""

import unittest
import json
import tempfile
import os
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

# Import Trend-Jacker components
from src.agents.trend_jacker_state import (
    TrendJackerState,
    ProcessingStatus,
    create_initial_state
)
from src.agents.trend_jacker import TrendJackerAgent, process_trend_jacker
from src.pipeline.trend_mapper import TrendMapper, map_trends
from src.pipeline.hook_generator import HookGenerator, generate_hooks
from src.pipeline.narrative_structurer import NarrativeStructurer, structure_narrative
from src.pipeline.attention_optimizer import AttentionOptimizer, optimize_attention
from src.pipeline.content_enhancer import ContentEnhancer, enhance_content
from src.pipeline.content_packager import ContentPackager, package_content


class TestTrendJackerState(unittest.TestCase):
    """Test TrendJackerState class."""

    def test_initial_state(self):
        """Test initial state values."""
        state = create_initial_state({'content_chunks': []}, 'test_job')

        self.assertEqual(state['status'], ProcessingStatus.PENDING)
        self.assertEqual(state['current_step'], "")
        self.assertEqual(state['current_step_num'], 0)
        self.assertEqual(state['input_package'], {'content_chunks': []})
        self.assertEqual(state['data_pack'], {'content_chunks': []})
        self.assertEqual(state['job_id'], 'test_job')
        self.assertEqual(len(state['content_chunks']), 0)
        self.assertEqual(state['source_file'], 'unknown')
        self.assertIsNone(state['package_analysis'])
        self.assertEqual(len(state['content_themes']), 0)
        self.assertEqual(state['evergreen_score'], 0.0)
        self.assertEqual(len(state['generated_hooks']), 0)
        self.assertEqual(len(state['selected_hooks']), 0)
        self.assertEqual(len(state['hooks']), 0)
        self.assertEqual(len(state['hook_variations']), 0)
        self.assertIsNone(state['trend_analysis'])
        self.assertEqual(len(state['mapped_trends']), 0)
        self.assertEqual(len(state['trend_mappings']), 0)
        self.assertEqual(len(state['trend_relevance']), 0)
        self.assertEqual(len(state['modern_contexts']), 0)
        self.assertIsNone(state['narrative_structure'])
        self.assertEqual(len(state['content_flow']), 0)
        self.assertEqual(len(state['engagement_points']), 0)
        self.assertEqual(len(state['attention_metrics']), 0)
        self.assertEqual(len(state['optimized_content']), 0)
        self.assertEqual(state['retention_score'], 0.0)
        self.assertEqual(len(state['enhanced_content']), 0)
        self.assertEqual(len(state['enhancement_metrics']), 0)
        self.assertEqual(state['engagement_score'], 0.0)
        self.assertEqual(len(state['modern_examples']), 0)
        self.assertEqual(len(state['contextual_notes']), 0)
        self.assertIsNone(state['output_package'])
        self.assertIsNone(state['package'])
        self.assertIsNone(state['package_id'])
        self.assertEqual(state['processing_time'], 0.0)
        self.assertEqual(len(state['step_times']), 0)
        self.assertEqual(state['retry_count'], 0)
        self.assertEqual(state['max_retries'], 3)
        self.assertIsNone(state['error_message'])
        self.assertIsNone(state['error'])
        self.assertEqual(state['fallback_triggered'], False)

    def test_state_transitions(self):
        """Test state transitions."""
        state = create_initial_state({'content_chunks': []}, 'test_job')

        # Transition to analyzing
        state['status'] = ProcessingStatus.ANALYZING
        self.assertEqual(state['status'], ProcessingStatus.ANALYZING)

        # Transition to completed
        state['status'] = ProcessingStatus.COMPLETED
        self.assertEqual(state['status'], ProcessingStatus.COMPLETED)

        # Transition to failed
        state['status'] = ProcessingStatus.FAILED
        self.assertEqual(state['status'], ProcessingStatus.FAILED)


class TestTrendMapper(unittest.TestCase):
    """Test TrendMapper class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mapper = TrendMapper()
        self.sample_chunks = [
            {
                'text': 'This is about productivity and time management.',
                'content_type': 'advice',
                'quality_level': 'high',
                'length': 50
            },
            {
                'text': 'Another chunk about efficiency.',
                'content_type': 'tips',
                'quality_level': 'medium',
                'length': 30
            }
        ]

    def test_analyze_trends(self):
        """Test trend analysis."""
        result = self.mapper.map(self.sample_chunks, ['productivity', 'efficiency'])

        self.assertIn('mapped_trends', result)
        self.assertIn('trend_relevance', result)
        self.assertIn('mapping_time', result)

        # Check trend mappings
        trend_mappings = result['mapped_trends']
        self.assertIsInstance(trend_mappings, list)

    def test_trend_mapping_structure(self):
        """Test trend mapping structure."""
        result = self.mapper.map(self.sample_chunks, ['productivity', 'efficiency'])
        trend_mappings = result['mapped_trends']

        if trend_mappings:
            mapping = trend_mappings[0]
            self.assertIn('trend_name', mapping)
            self.assertIn('category', mapping)
            self.assertIn('relevance_score', mapping)


class TestHookGenerator(unittest.TestCase):
    """Test HookGenerator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = HookGenerator()
        self.sample_chunks = [
            {
                'text': 'This is about productivity and time management.',
                'content_type': 'advice',
                'quality_level': 'high',
                'length': 50
            }
        ]
        self.sample_trend_analysis = {
            'dominant_trends': ['productivity', 'efficiency'],
            'trend_confidence': 0.8,
            'relevance_score': 0.7
        }

    def test_generate_hooks(self):
        """Test hook generation."""
        result = self.generator.generate(
            self.sample_chunks,
            ['productivity', 'efficiency']
        )

        self.assertIn('hooks', result)
        self.assertIn('generation_time', result)

        # Check hooks structure
        hooks = result['hooks']
        self.assertIsInstance(hooks, list)

        if hooks:
            hook = hooks[0]
            self.assertIn('text', hook)
            self.assertIn('hook_type', hook)
            self.assertIn('quality_score', hook)

    def test_hook_types(self):
        """Test different hook types."""
        result = self.generator.generate(
            self.sample_chunks,
            ['productivity', 'efficiency']
        )

        hooks = result['hooks']
        hook_types = [hook.get('hook_type') for hook in hooks]

        # Check for expected hook types
        expected_types = ['question', 'statement', 'statistic', 'story']
        for hook_type in expected_types:
            self.assertIn(hook_type, hook_types)


class TestNarrativeStructurer(unittest.TestCase):
    """Test NarrativeStructurer class."""

    def setUp(self):
        """Set up test fixtures."""
        self.structurer = NarrativeStructurer()
        self.sample_chunks = [
            {
                'text': 'Introduction to productivity.',
                'content_type': 'introduction',
                'quality_level': 'high',
                'length': 30
            },
            {
                'text': 'Main content about time management.',
                'content_type': 'body',
                'quality_level': 'high',
                'length': 50
            },
            {
                'text': 'Conclusion and call to action.',
                'content_type': 'conclusion',
                'quality_level': 'high',
                'length': 40
            }
        ]
        self.sample_trend_mappings = [
            {
                'original_content': 'productivity',
                'mapped_trend': 'productivity_hacks',
                'confidence': 0.8,
                'modern_framework': 'modern_productivity'
            }
        ]
        self.sample_hooks = [
            {
                'text': 'Want to double your productivity?',
                'hook_type': 'question',
                'quality_score': 0.8,
                'attention_score': 0.9
            }
        ]

    def test_structure_narrative(self):
        """Test narrative structuring."""
        result = self.structurer.structure(
            self.sample_chunks,
            self.sample_hooks,
            self.sample_trend_mappings
        )

        self.assertIn('narrative_structure', result)
        self.assertIn('structuring_time', result)

        # Check narrative structure
        narrative_structure = result['narrative_structure']
        self.assertIn('structure', narrative_structure)
        self.assertIn('sections', narrative_structure)
        self.assertIn('coherence_score', narrative_structure)
        self.assertIn('flow_score', narrative_structure)

    def test_narrative_sections(self):
        """Test narrative sections."""
        result = self.structurer.structure(
            self.sample_chunks,
            self.sample_hooks,
            self.sample_trend_mappings
        )

        sections = result['narrative_structure']['sections']
        self.assertIsInstance(sections, list)

        # Check for expected sections
        section_names = [section.get('name') for section in sections]
        expected_sections = ['hook', 'introduction', 'body', 'conclusion']
        for section in expected_sections:
            self.assertIn(section, section_names)


class TestAttentionOptimizer(unittest.TestCase):
    """Test AttentionOptimizer class."""

    def setUp(self):
        """Set up test fixtures."""
        self.optimizer = AttentionOptimizer()
        self.sample_chunks = [
            {
                'text': 'This is about productivity and time management.',
                'content_type': 'advice',
                'quality_level': 'high',
                'length': 50
            }
        ]
        self.sample_narrative_structure = {
            'structure': {'type': 'linear'},
            'sections': [
                {'name': 'hook', 'start': 0, 'end': 10},
                {'name': 'body', 'start': 10, 'end': 50}
            ],
            'coherence_score': 0.8,
            'flow_score': 0.7
        }
        self.sample_hooks = [
            {
                'text': 'Want to double your productivity?',
                'hook_type': 'question',
                'quality_score': 0.8,
                'attention_score': 0.9
            }
        ]

    def test_optimize_attention(self):
        """Test attention optimization."""
        result = self.optimizer.optimize(
            self.sample_chunks,
            self.sample_narrative_structure,
            self.sample_hooks
        )

        self.assertIn('attention_metrics', result)
        self.assertIn('optimized_content', result)
        self.assertIn('retention_score', result)
        self.assertIn('optimization_time', result)

        # Check attention metrics
        attention_metrics = result['attention_metrics']
        self.assertIn('overall_attention', attention_metrics)

        # Check optimized content
        optimized_content = result['optimized_content']
        self.assertEqual(len(optimized_content), len(self.sample_chunks))

    def test_retention_score_range(self):
        """Test retention score is in valid range."""
        result = self.optimizer.optimize(
            self.sample_chunks,
            self.sample_narrative_structure,
            self.sample_hooks
        )

        retention_score = result['retention_score']
        self.assertGreaterEqual(retention_score, 0.0)
        self.assertLessEqual(retention_score, 1.0)


class TestContentEnhancer(unittest.TestCase):
    """Test ContentEnhancer class."""

    def setUp(self):
        """Set up test fixtures."""
        self.enhancer = ContentEnhancer()
        self.sample_optimized_content = [
            {
                'text': 'This is about productivity and time management.',
                'content_type': 'advice',
                'quality_level': 'high',
                'length': 50,
                'attention_score': 0.7
            }
        ]
        self.sample_narrative_structure = {
            'structure': {'type': 'linear'},
            'sections': [
                {'name': 'hook', 'start': 0, 'end': 10},
                {'name': 'body', 'start': 10, 'end': 50}
            ],
            'coherence_score': 0.8,
            'flow_score': 0.7
        }
        self.sample_hooks = [
            {
                'text': 'Want to double your productivity?',
                'hook_type': 'question',
                'quality_score': 0.8,
                'attention_score': 0.9
            }
        ]

    def test_enhance_content(self):
        """Test content enhancement."""
        result = self.enhancer.enhance(
            self.sample_optimized_content,
            self.sample_narrative_structure,
            self.sample_hooks
        )

        self.assertIn('enhanced_content', result)
        self.assertIn('enhancement_metrics', result)
        self.assertIn('engagement_score', result)
        self.assertIn('enhancement_time', result)

        # Check enhanced content
        enhanced_content = result['enhanced_content']
        self.assertEqual(len(enhanced_content), len(self.sample_optimized_content))

        # Check that enhancements were applied
        if enhanced_content:
            self.assertIn('enhancements_applied', enhanced_content[0])

    def test_engagement_score_range(self):
        """Test engagement score is in valid range."""
        result = self.enhancer.enhance(
            self.sample_optimized_content,
            self.sample_narrative_structure,
            self.sample_hooks
        )

        engagement_score = result['engagement_score']
        self.assertGreaterEqual(engagement_score, 0.0)
        self.assertLessEqual(engagement_score, 1.0)


class TestContentPackager(unittest.TestCase):
    """Test ContentPackager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.packager = ContentPackager()
        self.sample_enhanced_content = [
            {
                'text': 'This is about productivity and time management.',
                'content_type': 'advice',
                'quality_level': 'high',
                'length': 50,
                'attention_score': 0.7,
                'enhancements_applied': ['vocabulary_upgrade', 'sentence_variety']
            }
        ]
        self.sample_narrative_structure = {
            'structure': {'type': 'linear'},
            'sections': [
                {'name': 'hook', 'start': 0, 'end': 10},
                {'name': 'body', 'start': 10, 'end': 50}
            ],
            'coherence_score': 0.8,
            'flow_score': 0.7
        }
        self.sample_hooks = [
            {
                'text': 'Want to double your productivity?',
                'hook_type': 'question',
                'quality_score': 0.8,
                'attention_score': 0.9
            }
        ]
        self.sample_enhancement_metrics = {
            'vocabulary_upgrade': 0.7,
            'sentence_variety': 0.8,
            'overall_enhancement': 0.75
        }

    def test_package_content(self):
        """Test content packaging."""
        result = self.packager.package(
            self.sample_enhanced_content,
            self.sample_narrative_structure,
            self.sample_hooks,
            self.sample_enhancement_metrics,
            0.8,  # engagement_score
            0.7,  # retention_score
            'test_source.txt'
        )

        self.assertIn('package', result)
        self.assertIn('package_id', result)
        self.assertIn('packaging_time', result)

        # Check package structure
        package = result['package']
        self.assertIn('metadata', package)
        self.assertIn('narrative', package)
        self.assertIn('hooks', package)
        self.assertIn('content_chunks', package)
        self.assertIn('enhancement_metrics', package)
        self.assertIn('engagement_score', package)
        self.assertIn('retention_score', package)
        self.assertIn('visual_cues', package)
        self.assertIn('audio_cues', package)
        self.assertIn('timing_markers', package)

    def test_package_metadata(self):
        """Test package metadata."""
        result = self.packager.package(
            self.sample_enhanced_content,
            self.sample_narrative_structure,
            self.sample_hooks,
            self.sample_enhancement_metrics,
            0.8,  # engagement_score
            0.7,  # retention_score
            'test_source.txt'
        )

        metadata = result['package']['metadata']
        self.assertIn('package_id', metadata)
        self.assertIn('timestamp', metadata)
        self.assertIn('source_file', metadata)
        self.assertEqual(metadata['source_file'], 'test_source.txt')

    def test_save_and_load_package(self):
        """Test saving and loading package."""
        # Create package
        result = self.packager.package(
            self.sample_enhanced_content,
            self.sample_narrative_structure,
            self.sample_hooks,
            self.sample_enhancement_metrics,
            0.8,  # engagement_score
            0.7,  # retention_score
            'test_source.txt'
        )

        # Save to temp file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name

        try:
            self.packager.save_package(result['package'], temp_path)

            # Load package
            loaded_package = self.packager.load_package(temp_path)

            # Verify loaded package matches original
            self.assertEqual(loaded_package['metadata']['package_id'], result['package']['metadata']['package_id'])
            self.assertEqual(loaded_package['metadata']['source_file'], result['package']['metadata']['source_file'])

        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)


class TestTrendJackerAgent(unittest.TestCase):
    """Test TrendJackerAgent class."""

    def setUp(self):
        """Set up test fixtures."""
        self.agent = TrendJackerAgent()
        self.sample_data_pack = {
            'metadata': {
                'package_id': 'arch_20240101_120000',
                'source_file': 'test_source.txt',
                'content_type': 'evergreen_content'
            },
            'content_chunks': [
                {
                    'text': 'This is about productivity and time management.',
                    'content_type': 'advice',
                    'quality_level': 'high',
                    'length': 50
                },
                {
                    'text': 'Another chunk about efficiency.',
                    'content_type': 'tips',
                    'quality_level': 'medium',
                    'length': 30
                }
            ]
        }

    def test_initial_state(self):
        """Test agent initial state."""
        self.assertIsNone(self.agent.state)
        self.assertEqual(self.agent.total_timeout, 90.0)

    def test_process_data_pack(self):
        """Test processing data pack."""
        result = self.agent.process(self.sample_data_pack)

        self.assertIn('package', result)
        self.assertIn('package_id', result)
        self.assertIn('total_time', result)
        self.assertIn('status', result)

        # Check package structure
        package = result['package']
        self.assertIn('metadata', package)
        self.assertIn('narrative', package)
        self.assertIn('hooks', package)
        self.assertIn('content_chunks', package)

    def test_workflow_steps(self):
        """Test that all workflow steps are executed."""
        result = self.agent.process(self.sample_data_pack)

        # Check that all steps were executed
        step_times = self.agent.state.step_times
        expected_steps = [
            'receive_data_pack',
            'analyze_trends',
            'generate_hooks',
            'structure_narrative',
            'optimize_attention',
            'enhance_content',
            'package_for_visionary'
        ]

        for step in expected_steps:
            self.assertIn(step, step_times)

    def test_get_status(self):
        """Test getting agent status."""
        status = self.agent.get_status()

        self.assertIn('status', status)
        self.assertIn('current_step', status)
        self.assertIn('package_id', status)
        self.assertIn('step_times', status)
        self.assertIn('error', status)


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions."""

    def test_map_trends(self):
        """Test map_trends convenience function."""
        sample_chunks = [
            {
                'text': 'This is about productivity.',
                'content_type': 'advice',
                'quality_level': 'high',
                'length': 30
            }
        ]
        sample_themes = ['productivity', 'efficiency']

        result = map_trends(sample_chunks, sample_themes)

        self.assertIn('mapped_trends', result)
        self.assertIn('trend_relevance', result)

    def test_generate_hooks(self):
        """Test generate_hooks convenience function."""
        sample_chunks = [
            {
                'text': 'This is about productivity.',
                'content_type': 'advice',
                'quality_level': 'high',
                'length': 30
            }
        ]
        sample_themes = ['productivity', 'efficiency']

        result = generate_hooks(sample_chunks, sample_themes)

        self.assertIn('hooks', result)

    def test_structure_narrative(self):
        """Test structure_narrative convenience function."""
        sample_chunks = [
            {
                'text': 'This is about productivity.',
                'content_type': 'advice',
                'quality_level': 'high',
                'length': 30
            }
        ]
        sample_trend_mappings = [
            {
                'original_content': 'productivity',
                'mapped_trend': 'productivity_hacks',
                'confidence': 0.8,
                'modern_framework': 'modern_productivity'
            }
        ]
        sample_hooks = [
            {
                'text': 'Want to be more productive?',
                'hook_type': 'question',
                'quality_score': 0.8,
                'attention_score': 0.9
            }
        ]

        result = structure_narrative(sample_chunks, sample_hooks, sample_trend_mappings)

        self.assertIn('narrative_structure', result)

    def test_optimize_attention(self):
        """Test optimize_attention convenience function."""
        sample_chunks = [
            {
                'text': 'This is about productivity.',
                'content_type': 'advice',
                'quality_level': 'high',
                'length': 30
            }
        ]
        sample_narrative_structure = {
            'structure': {'type': 'linear'},
            'sections': [],
            'coherence_score': 0.8,
            'flow_score': 0.7
        }
        sample_hooks = [
            {
                'text': 'Want to be more productive?',
                'hook_type': 'question',
                'quality_score': 0.8,
                'attention_score': 0.9
            }
        ]

        result = optimize_attention(sample_chunks, sample_narrative_structure, sample_hooks)

        self.assertIn('attention_metrics', result)
        self.assertIn('optimized_content', result)
        self.assertIn('retention_score', result)

    def test_enhance_content(self):
        """Test enhance_content convenience function."""
        sample_chunks = [
            {
                'text': 'This is about productivity.',
                'content_type': 'advice',
                'quality_level': 'high',
                'length': 30,
                'attention_score': 0.7
            }
        ]
        sample_narrative_structure = {
            'structure': {'type': 'linear'},
            'sections': [],
            'coherence_score': 0.8,
            'flow_score': 0.7
        }
        sample_hooks = [
            {
                'text': 'Want to be more productive?',
                'hook_type': 'question',
                'quality_score': 0.8,
                'attention_score': 0.9
            }
        ]

        result = enhance_content(sample_chunks, sample_narrative_structure, sample_hooks)

        self.assertIn('enhanced_content', result)
        self.assertIn('enhancement_metrics', result)
        self.assertIn('engagement_score', result)

    def test_package_content(self):
        """Test package_content convenience function."""
        sample_chunks = [
            {
                'text': 'This is about productivity.',
                'content_type': 'advice',
                'quality_level': 'high',
                'length': 30,
                'attention_score': 0.7,
                'enhancements_applied': []
            }
        ]
        sample_narrative_structure = {
            'structure': {'type': 'linear'},
            'sections': [],
            'coherence_score': 0.8,
            'flow_score': 0.7
        }
        sample_hooks = [
            {
                'text': 'Want to be more productive?',
                'hook_type': 'question',
                'quality_score': 0.8,
                'attention_score': 0.9
            }
        ]
        sample_enhancement_metrics = {
            'vocabulary_upgrade': 0.7,
            'overall_enhancement': 0.75
        }

        result = package_content(
            sample_chunks,
            sample_narrative_structure,
            sample_hooks,
            sample_enhancement_metrics,
            0.8,  # engagement_score
            0.7,  # retention_score
            'test_source.txt'
        )

        self.assertIn('package', result)
        self.assertIn('package_id', result)

    def test_process_trend_jacker(self):
        """Test process_trend_jacker convenience function."""
        sample_data_pack = {
            'metadata': {
                'package_id': 'arch_20240101_120000',
                'source_file': 'test_source.txt'
            },
            'content_chunks': [
                {
                    'text': 'This is about productivity.',
                    'content_type': 'advice',
                    'quality_level': 'high',
                    'length': 30
                }
            ]
        }

        result = process_trend_jacker(sample_data_pack)

        self.assertIn('package', result)
        self.assertIn('package_id', result)
        self.assertIn('total_time', result)
        self.assertIn('status', result)


if __name__ == '__main__':
    unittest.main()
