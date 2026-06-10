"""
Unit Tests for Visionary Agent

Tests all components of the Visionary workflow:
- VisionaryState management
- Package reception and validation
- Storyboard generation
- B-roll prompt generation
- Visual cue mapping
- Audio design
- Asset packaging
- Output generation
- Main Visionary orchestration
"""

import unittest
import json
import tempfile
import os
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.agents.visionary_state import (
    VisionaryState,
    ProcessingStatus,
    VisualStyle,
    AudioMood,
    AssetType,
    create_initial_state,
    update_step_timing,
    B_ROLL_TEMPLATES,
    SCENE_TRANSITIONS,
    AUDIO_MOOD_BPM,
    CONTENT_STYLE_MAP,
    GUMROAD_PRODUCT_TEMPLATE
)
from src.agents.visionary import VisionaryAgent, process_visionary


class TestVisionaryState(unittest.TestCase):
    """Test VisionaryState class."""

    def test_initial_state(self):
        """Test initial state values."""
        sample_package = {
            'content_chunks': [],
            'hooks': [],
            'narrative': {},
            'metadata': {'source_file': 'test.txt'}
        }
        state = create_initial_state(sample_package, 'test_job')

        self.assertEqual(state['status'], ProcessingStatus.PENDING)
        self.assertEqual(state['job_id'], 'test_job')
        self.assertEqual(state['asset_type'], 'youtube_short')
        self.assertEqual(state['current_step'], '')
        self.assertEqual(state['current_step_num'], 0)
        self.assertEqual(state['source_file'], 'test.txt')
        self.assertEqual(state['total_duration'], 60.0)
        self.assertEqual(state['scene_count'], 0)
        self.assertEqual(state['prompt_count'], 0)
        self.assertEqual(state['cue_count'], 0)
        self.assertEqual(state['processing_time'], 0.0)
        self.assertEqual(state['retry_count'], 0)
        self.assertEqual(state['max_retries'], 3)
        self.assertIsNone(state['package_analysis'])
        self.assertIsNone(state['storyboard'])
        self.assertIsNone(state['audio_design'])
        self.assertIsNone(state['output_package'])
        self.assertIsNone(state['package_id'])
        self.assertEqual(state['visual_style'], 'cinematic')
        self.assertEqual(state['background_mood'], 'inspiring')

    def test_state_transitions(self):
        """Test state transitions."""
        sample_package = {'content_chunks': [], 'hooks': [], 'narrative': {}}
        state = create_initial_state(sample_package, 'test_job')

        state['status'] = ProcessingStatus.RECEIVING
        self.assertEqual(state['status'], ProcessingStatus.RECEIVING)

        state['status'] = ProcessingStatus.STORYBOARDING
        self.assertEqual(state['status'], ProcessingStatus.STORYBOARDING)

        state['status'] = ProcessingStatus.COMPLETED
        self.assertEqual(state['status'], ProcessingStatus.COMPLETED)

        state['status'] = ProcessingStatus.FAILED
        self.assertEqual(state['status'], ProcessingStatus.FAILED)

    def test_create_initial_state_with_asset_type(self):
        """Test creating initial state with custom asset type."""
        sample_package = {'content_chunks': [], 'hooks': [], 'narrative': {}}
        state = create_initial_state(sample_package, 'test_job', asset_type='tiktok')
        self.assertEqual(state['asset_type'], 'tiktok')

    def test_update_step_timing(self):
        """Test step timing update."""
        sample_package = {'content_chunks': [], 'hooks': [], 'narrative': {}}
        state = create_initial_state(sample_package, 'test_job')
        state['step_start_time'] = datetime.utcnow().isoformat()

        updated = update_step_timing(state, 'test_step')
        self.assertIn('test_step', updated['step_times'])


class TestVisionaryAgent(unittest.TestCase):
    """Test VisionaryAgent class."""

    def setUp(self):
        """Set up test fixtures."""
        self.agent = VisionaryAgent()
        self.sample_package = {
            'content_chunks': [
                {
                    'text': 'This is about productivity and time management.',
                    'content_type': 'advice',
                    'quality_level': 'high',
                    'length': 50
                },
                {
                    'text': 'Main content about getting things done efficiently.',
                    'content_type': 'body',
                    'quality_level': 'high',
                    'length': 55
                }
            ],
            'hooks': [
                {
                    'text': 'Want to double your productivity?',
                    'hook_type': 'question',
                    'quality_score': 0.8
                }
            ],
            'narrative': {
                'structure_type': 'problem_solution',
                'sections': [
                    {'name': 'hook', 'section_name': 'hook', 'start': 0, 'end': 1},
                    {'name': 'problem', 'section_name': 'problem', 'start': 1, 'end': 2}
                ],
                'coherence_score': 0.8,
                'flow_score': 0.7
            },
            'engagement_score': 0.75,
            'retention_score': 0.6,
            'metadata': {
                'source_file': 'test_source.txt',
                'content_type': 'productivity',
                'package_id': 'tj_12345'
            },
            'visual_cues': [],
            'audio_cues': []
        }

    def test_initial_state(self):
        """Test agent initial state."""
        self.assertIsNone(self.agent.state)
        self.assertEqual(self.agent.total_timeout, 70.0)
        self.assertEqual(self.agent.target_duration, 60.0)

    def test_process(self):
        """Test processing through complete Visionary workflow."""
        result = self.agent.process(self.sample_package)

        self.assertIn('package', result)
        self.assertIn('package_id', result)
        self.assertIn('output_path', result)
        self.assertIn('total_time', result)
        self.assertIn('status', result)
        self.assertEqual(result['status'], 'completed')

        # Check package structure
        package = result['package']
        self.assertIn('package_id', package)
        self.assertIn('storyboard', package)
        self.assertIn('b_roll_prompts', package)
        self.assertIn('visual_cues', package)
        self.assertIn('audio_design', package)
        self.assertIn('gumroad_listing', package)

    def test_process_with_different_asset_types(self):
        """Test processing with different asset types."""
        for asset_type in ['youtube_short', 'tiktok', 'instagram_reel']:
            agent = VisionaryAgent()
            result = agent.process(self.sample_package, asset_type)
            self.assertEqual(result['status'], 'completed',
                             f"Failed for asset_type={asset_type}")
            self.assertIn('package', result)
            self.assertIn('package_id', result)

    def test_process_invalid_package(self):
        """Test processing with invalid package."""
        invalid_package = {'invalid': True}
        with self.assertRaises(Exception):
            self.agent.process(invalid_package)

    def test_process_missing_required_fields(self):
        """Test processing with missing required fields."""
        incomplete = {
            'content_chunks': [],
            'hooks': []
            # Missing 'narrative'
        }
        with self.assertRaises(Exception):
            self.agent.process(incomplete)

    def test_workflow_steps_executed(self):
        """Test that all workflow steps are executed."""
        result = self.agent.process(self.sample_package)

        step_times = self.agent.state['step_times']
        expected_steps = [
            'receive_package',
            'generate_storyboard',
            'generate_broll_prompts',
            'map_visual_cues',
            'design_audio',
            'package_assets',
            'generate_output'
        ]

        for step in expected_steps:
            self.assertIn(step, step_times,
                          f"Step '{step}' not found in step_times")

    def test_get_status(self):
        """Test getting agent status."""
        status = self.agent.get_status()
        self.assertIn('status', status)
        self.assertEqual(status['status'], 'idle')

        # Status after processing
        self.agent.process(self.sample_package)
        status = self.agent.get_status()
        self.assertIn('status', status)
        self.assertIn('current_step', status)
        self.assertIn('package_id', status)
        self.assertIn('step_times', status)

    def test_storyboard_structure(self):
        """Test storyboard structure in output."""
        result = self.agent.process(self.sample_package)
        package = result['package']
        storyboard = package['storyboard']

        self.assertIn('storyboard_id', storyboard)
        self.assertIn('total_duration', storyboard)
        self.assertIn('scene_count', storyboard)
        self.assertIn('pacing_profile', storyboard)
        self.assertIn('visual_style', storyboard)
        self.assertIn('scenes', storyboard)

        # Check scenes
        scenes = storyboard['scenes']
        self.assertGreater(len(scenes), 0)
        for scene in scenes:
            self.assertIn('scene_id', scene)
            self.assertIn('start_time', scene)
            self.assertIn('duration', scene)
            self.assertIn('end_time', scene)
            self.assertIn('visual_style', scene)

    def test_b_roll_prompts_structure(self):
        """Test B-roll prompts structure in output."""
        result = self.agent.process(self.sample_package)
        package = result['package']
        prompts = package['b_roll_prompts']

        self.assertGreater(len(prompts), 0)
        for prompt in prompts:
            self.assertIn('prompt_id', prompt)
            self.assertIn('scene_id', prompt)
            self.assertIn('primary_prompt', prompt)
            self.assertIn('alternative_prompts', prompt)
            self.assertIn('negative_prompt', prompt)
            self.assertIn('aspect_ratio', prompt)
            self.assertIn('resolution', prompt)

    def test_visual_cues_structure(self):
        """Test visual cues structure in output."""
        result = self.agent.process(self.sample_package)
        package = result['package']
        cues = package['visual_cues']

        self.assertGreater(len(cues), 0)
        for cue in cues:
            self.assertIn('cue_id', cue)
            self.assertIn('timestamp', cue)
            self.assertIn('duration', cue)
            self.assertIn('visual_style', cue)

    def test_audio_design_structure(self):
        """Test audio design structure in output."""
        result = self.agent.process(self.sample_package)
        package = result['package']
        audio = package['audio_design']

        self.assertIn('design_id', audio)
        self.assertIn('overall_mood', audio)
        self.assertIn('bpm', audio)
        self.assertIn('genre', audio)
        self.assertIn('instruments', audio)
        self.assertIn('total_duration', audio)
        self.assertIn('cues', audio)
        self.assertIn('emphasis_markers', audio)

    def test_gumroad_listing_structure(self):
        """Test Gumroad listing structure in output."""
        result = self.agent.process(self.sample_package)
        package = result['package']
        listing = package['gumroad_listing']

        self.assertIn('title', listing)
        self.assertIn('description', listing)
        self.assertIn('thumbnail_prompts', listing)
        self.assertIn('hashtags', listing)
        self.assertIn('seo_keywords', listing)
        self.assertIn('price_tier', listing)
        self.assertIn('compatible_with', listing)
        self.assertIn('product_type', listing)

    def test_output_file_written(self):
        """Test that output file is written to disk."""
        result = self.agent.process(self.sample_package)
        output_path = result['output_path']

        self.assertTrue(os.path.exists(output_path),
                        f"Output file not found: {output_path}")

        # Verify output is valid JSON
        with open(output_path, 'r') as f:
            saved_data = json.load(f)
        self.assertIn('package_id', saved_data)

        # Clean up
        os.remove(output_path)

    def test_visual_style_determination(self):
        """Test visual style determined from content type."""
        # Productivity content should map to kinetic_typography
        result = self.agent.process(self.sample_package)
        package = result['package']
        self.assertIn('visual_style', package['metadata'])

    def test_pricing_based_on_scores(self):
        """Test pricing tier determination."""
        result = self.agent.process(self.sample_package)
        package = result['package']
        price_tier = package['gumroad_listing']['price_tier']
        self.assertIn('tier', price_tier)
        self.assertIn('recommended_price', price_tier)

    def test_engagement_score_impact_on_audio(self):
        """Test that engagement score affects audio mood."""
        result = self.agent.process(self.sample_package)
        package = result['package']
        audio = package['audio_design']

        # With engagement 0.75, mood should be 'inspiring'
        self.assertIn(audio['overall_mood'], ['inspiring', 'energetic'])

    def test_empty_content_chunks(self):
        """Test processing with empty but valid package."""
        minimal_package = {
            'content_chunks': [],
            'hooks': [{'text': 'Test hook', 'hook_type': 'question', 'quality_score': 0.5}],
            'narrative': {'structure_type': 'simple', 'sections': []},
            'engagement_score': 0.5,
            'retention_score': 0.5,
            'metadata': {
                'source_file': 'minimal.txt',
                'content_type': 'default'
            }
        }

        result = self.agent.process(minimal_package)
        self.assertEqual(result['status'], 'completed')

    def test_single_chunk_processing(self):
        """Test processing with a single content chunk."""
        single_package = {
            'content_chunks': [
                {'text': 'Single chunk of content.', 'content_type': 'advice'}
            ],
            'hooks': [{'text': 'Test?', 'hook_type': 'question', 'quality_score': 0.5}],
            'narrative': {'structure_type': 'simple', 'sections': []},
            'engagement_score': 0.5,
            'retention_score': 0.5,
            'metadata': {
                'source_file': 'single.txt',
                'content_type': 'default'
            }
        }

        result = self.agent.process(single_package)
        self.assertEqual(result['status'], 'completed')
        self.assertGreater(len(result['package']['b_roll_prompts']), 0)


class TestVisionaryHelpers(unittest.TestCase):
    """Test Visionary helper methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.agent = VisionaryAgent()
        # Initialize state for helper tests
        self.agent.state = create_initial_state(
            {
                'content_chunks': [{'text': 'Test content for prompt generation.'}],
                'hooks': [{'text': 'Test hook?', 'hook_type': 'question', 'quality_score': 0.7}],
                'narrative': {'structure_type': 'simple', 'sections': []},
                'engagement_score': 0.7,
                'retention_score': 0.6,
                'metadata': {'source_file': 'test.txt', 'content_type': 'technology'}
            },
            'test_helper_job'
        )

    def test_extract_visual_concepts(self):
        """Test visual concept extraction."""
        concepts = self.agent._extract_visual_concepts(
            "This is a test sentence for visual extraction."
        )
        self.assertIsInstance(concepts, str)
        self.assertGreater(len(concepts), 0)

    def test_determine_pacing(self):
        """Test pacing determination."""
        self.assertEqual(self.agent._determine_pacing(30), 'fast')
        self.assertEqual(self.agent._determine_pacing(45), 'medium')
        self.assertEqual(self.agent._determine_pacing(60), 'medium')
        self.assertEqual(self.agent._determine_pacing(90), 'slow')

    def test_determine_price_tier(self):
        """Test price tier determination."""
        self.agent.state['engagement_score'] = 0.9
        self.agent.state['retention_score'] = 0.9
        tier = self.agent._determine_price_tier(self.agent.state)
        self.assertEqual(tier['tier'], 'premium')

        self.agent.state['engagement_score'] = 0.7
        self.agent.state['retention_score'] = 0.6
        tier = self.agent._determine_price_tier(self.agent.state)
        self.assertEqual(tier['tier'], 'standard')

        self.agent.state['engagement_score'] = 0.4
        self.agent.state['retention_score'] = 0.3
        tier = self.agent._determine_price_tier(self.agent.state)
        self.assertEqual(tier['tier'], 'basic')

    def test_generate_hashtags(self):
        """Test hashtag generation."""
        hashtags = self.agent._generate_hashtags(self.agent.state)
        self.assertIsInstance(hashtags, list)
        self.assertGreater(len(hashtags), 0)

    def test_generate_seo_keywords(self):
        """Test SEO keyword generation."""
        keywords = self.agent._generate_seo_keywords(self.agent.state)
        self.assertIsInstance(keywords, list)

    def test_generate_gumroad_title(self):
        """Test Gumroad title generation."""
        title = self.agent._generate_gumroad_title(self.agent.state)
        self.assertIsInstance(title, str)
        self.assertGreater(len(title), 0)


class TestConvenienceFunctions(unittest.TestCase):
    """Test Visionary convenience functions."""

    def test_process_visionary(self):
        """Test process_visionary convenience function."""
        sample_package = {
            'content_chunks': [
                {'text': 'Test content.', 'content_type': 'advice'}
            ],
            'hooks': [{'text': 'Test?', 'hook_type': 'question', 'quality_score': 0.5}],
            'narrative': {'structure_type': 'simple', 'sections': []},
            'engagement_score': 0.5,
            'retention_score': 0.5,
            'metadata': {
                'source_file': 'test.txt',
                'content_type': 'default'
            }
        }

        result = process_visionary(sample_package)

        self.assertIn('package', result)
        self.assertIn('package_id', result)
        self.assertIn('output_path', result)
        self.assertIn('total_time', result)
        self.assertIn('status', result)

        # Clean up output file
        output_path = result['output_path']
        if os.path.exists(output_path):
            os.remove(output_path)

    def test_process_visionary_with_asset_type(self):
        """Test process_visionary with custom asset type."""
        sample_package = {
            'content_chunks': [{'text': 'Test.', 'content_type': 'advice'}],
            'hooks': [{'text': 'Test?', 'hook_type': 'question', 'quality_score': 0.5}],
            'narrative': {'structure_type': 'simple', 'sections': []},
            'engagement_score': 0.5,
            'retention_score': 0.5,
            'metadata': {'source_file': 'test.txt', 'content_type': 'default'}
        }

        result = process_visionary(sample_package, asset_type='tiktok')

        self.assertEqual(result['status'], 'completed')
        self.assertIn('package', result)

        # Clean up
        output_path = result['output_path']
        if os.path.exists(output_path):
            os.remove(output_path)


class TestVisualStyleMapping(unittest.TestCase):
    """Test visual style mapping."""

    def test_content_style_map(self):
        """Test content-to-visual-style mapping."""
        self.assertEqual(CONTENT_STYLE_MAP['technology'], 'kinetic_typography')
        self.assertEqual(CONTENT_STYLE_MAP['business'], 'corporate')
        self.assertEqual(CONTENT_STYLE_MAP['lifestyle'], 'social_media')
        self.assertEqual(CONTENT_STYLE_MAP['history'], 'documentary')
        self.assertEqual(CONTENT_STYLE_MAP['education'], 'animated_infographic')

    def test_b_roll_templates(self):
        """Test B-roll prompt templates."""
        for style in VisualStyle:
            style_value = style.value
            self.assertIn(style_value, B_ROLL_TEMPLATES)
            template = B_ROLL_TEMPLATES[style_value]
            self.assertIn('prefix', template)
            self.assertIn('suffix', template)
            self.assertIn('negative', template)

    def test_audio_mood_bpm(self):
        """Test audio mood BPM mappings."""
        for mood in AudioMood:
            mood_value = mood.value
            self.assertIn(mood_value, AUDIO_MOOD_BPM)
            config = AUDIO_MOOD_BPM[mood_value]
            self.assertIn('bpm', config)
            self.assertIn('genre', config)
            self.assertIn('instruments', config)

    def test_gumroad_product_template(self):
        """Test Gumroad product template."""
        self.assertIn('product_type', GUMROAD_PRODUCT_TEMPLATE)
        self.assertEqual(GUMROAD_PRODUCT_TEMPLATE['product_type'], 'digital_asset_pack')
        self.assertIn('contents', GUMROAD_PRODUCT_TEMPLATE)
        self.assertIn('video_script', GUMROAD_PRODUCT_TEMPLATE['contents'])
        self.assertIn('b_roll_prompts', GUMROAD_PRODUCT_TEMPLATE['contents'])
        self.assertIn('storyboard', GUMROAD_PRODUCT_TEMPLATE['contents'])
        self.assertIn('thumbnail_prompts', GUMROAD_PRODUCT_TEMPLATE['contents'])


if __name__ == '__main__':
    unittest.main()
