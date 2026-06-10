"""
Visionary Agent - Main Orchestration

Orchestrates the 7-step Visionary workflow for transforming
contextualized content into production-ready media assets.

Workflow Steps:
1. Package Reception (5s) - Receive and validate Trend-Jacker package
2. Storyboard Generation (20s) - Create visual storyboard from narrative
3. B-Roll Prompting (15s) - Generate AI image/video prompts for each scene
4. Visual Cue Mapping (10s) - Map visual cues to exact timestamps
5. Audio Design (10s) - Design audio mood, emphasis, and transitions
6. Asset Packaging (5s) - Bundle into Gumroad-ready ZIP package
7. Output Generation (5s) - Write final assets to processed_gold/

Total Time Budget: 70 seconds
"""

import time
import json
import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

# Try to import LangGraph, use fallback if not available
try:
    from langgraph.graph import StateGraph, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    logging.warning("LangGraph not available, using fallback mode")

# Import Visionary state
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VisionaryAgent:
    """
    Visionary Agent - Media Architect for content transmutation.

    Takes contextualized content packages from Trend-Jacker and transforms
    them into production-ready media assets with B-roll prompts, visual
    cues, storyboards, and Gumroad-ready asset packages.
    """

    def __init__(self):
        """Initialize VisionaryAgent with media generation configuration."""
        self.state = None
        self.total_timeout = 70.0  # 70 second total timeout
        self.target_duration = 60.0  # Target 60-second video

        # Output directory
        self.output_dir = Path("processed_gold")

        logger.info("VisionaryAgent initialized")

    def process(self, input_package: Dict[str, Any],
                asset_type: str = "youtube_short") -> Dict[str, Any]:
        """
        Process Trend-Jacker package through complete Visionary workflow.

        Args:
            input_package: Package from Trend-Jacker agent
            asset_type: Target asset type (youtube_short, tiktok, etc.)

        Returns:
            Dictionary containing:
            - package: Complete Gumroad-ready package
            - package_id: Unique package identifier
            - output_path: Path to saved output file
            - total_time: Total processing time
            - status: Processing status

        Raises:
            VisionaryError: If processing fails
        """
        start_time = time.time()

        logger.info(f"Starting Visionary workflow for asset_type={asset_type}")

        try:
            # Initialize state
            self.state = create_initial_state(
                input_package,
                f"vis_{int(time.time())}",
                asset_type
            )
            self.state['status'] = ProcessingStatus.RECEIVING

            # Execute workflow
            if LANGGRAPH_AVAILABLE:
                result = self._execute_with_langgraph()
            else:
                result = self._execute_fallback()

            total_time = time.time() - start_time

            # Check timeout
            if total_time > self.total_timeout:
                logger.warning(
                    f"Visionary workflow exceeded time budget: {total_time:.2f}s > {self.total_timeout}s"
                )
                self.state['status'] = ProcessingStatus.FAILED
                self.state['error_message'] = f"Timeout: {total_time:.2f}s > {self.total_timeout}s"
            else:
                self.state['status'] = ProcessingStatus.COMPLETED

            self.state['processing_time'] = total_time

            result['total_time'] = total_time
            result['status'] = self.state['status'].value

            logger.info(
                f"Visionary workflow completed in {total_time:.2f}s: "
                f"status={self.state['status'].value}, package_id={result.get('package_id', 'N/A')}"
            )

            return result

        except Exception as e:
            total_time = time.time() - start_time
            logger.error(f"Visionary workflow failed after {total_time:.2f}s: {str(e)}")

            if self.state:
                self.state['status'] = ProcessingStatus.FAILED
                self.state['error_message'] = str(e)

            raise Exception(f"Visionary processing failed: {str(e)}")

    def _execute_with_langgraph(self) -> Dict[str, Any]:
        """Execute workflow using LangGraph orchestration."""
        workflow = StateGraph(VisionaryState)

        workflow.add_node("receive_package", self._step_1_receive_package)
        workflow.add_node("generate_storyboard", self._step_2_generate_storyboard)
        workflow.add_node("generate_broll_prompts", self._step_3_generate_broll_prompts)
        workflow.add_node("map_visual_cues", self._step_4_map_visual_cues)
        workflow.add_node("design_audio", self._step_5_design_audio)
        workflow.add_node("package_assets", self._step_6_package_assets)
        workflow.add_node("generate_output", self._step_7_generate_output)

        workflow.set_entry_point("receive_package")
        workflow.add_edge("receive_package", "generate_storyboard")
        workflow.add_edge("generate_storyboard", "generate_broll_prompts")
        workflow.add_edge("generate_broll_prompts", "map_visual_cues")
        workflow.add_edge("map_visual_cues", "design_audio")
        workflow.add_edge("design_audio", "package_assets")
        workflow.add_edge("package_assets", "generate_output")
        workflow.add_edge("generate_output", END)

        app = workflow.compile()
        result = app.invoke(self.state)

        return {
            'package': result['output_package'],
            'package_id': result['package_id'],
            'output_path': result['output_path'],
            'workflow_mode': 'langgraph'
        }

    def _execute_fallback(self) -> Dict[str, Any]:
        """Execute workflow in fallback mode without LangGraph."""
        self._step_1_receive_package(self.state)
        self._step_2_generate_storyboard(self.state)
        self._step_3_generate_broll_prompts(self.state)
        self._step_4_map_visual_cues(self.state)
        self._step_5_design_audio(self.state)
        self._step_6_package_assets(self.state)
        self._step_7_generate_output(self.state)

        return {
            'package': self.state['output_package'],
            'package_id': self.state['package_id'],
            'output_path': self.state['output_path'],
            'workflow_mode': 'fallback'
        }

    # Step 1: Package Reception (5s)
    def _step_1_receive_package(self, state: VisionaryState) -> VisionaryState:
        """Step 1: Receive and validate Trend-Jacker package."""
        step_start = time.time()
        logger.info("Step 1: Receiving Trend-Jacker package")

        try:
            pkg = state['input_package']

            # Validate required fields
            required = ['content_chunks', 'hooks', 'narrative']
            for field in required:
                if field not in pkg:
                    raise ValueError(f"Missing required field in package: {field}")

            # Extract content
            state['content_chunks'] = pkg.get('content_chunks', [])
            state['hooks'] = pkg.get('hooks', [])
            state['narrative_structure'] = pkg.get('narrative', {})
            state['engagement_score'] = pkg.get('engagement_score', 0.0)
            state['retention_score'] = pkg.get('retention_score', 0.0)
            state['source_file'] = pkg.get('metadata', {}).get('source_file', 'unknown')

            # Determine visual style from content themes
            themes = pkg.get('metadata', {}).get('content_type', 'default')
            state['visual_style'] = CONTENT_STYLE_MAP.get(themes, VisualStyle.STOCK_FOOTAGE.value)

            # Inherit visual/audio cues from Trend-Jacker if available
            state['visual_cues'] = pkg.get('visual_cues', [])
            state['audio_cues'] = pkg.get('audio_cues', [])

            state['current_step'] = "receive_package"
            state['step_times']['receive_package'] = time.time() - step_start

            logger.info(
                f"Step 1 completed in {state['step_times']['receive_package']:.2f}s: "
                f"received {len(state['content_chunks'])} chunks, "
                f"{len(state['hooks'])} hooks, style={state['visual_style']}"
            )

            return state

        except Exception as e:
            step_time = time.time() - step_start
            logger.error(f"Step 1 failed after {step_time:.2f}s: {str(e)}")
            state['error_message'] = str(e)
            state['error'] = {'error_type': 'package_reception_error', 'message': str(e), 'step': 'receive_package'}
            raise

    # Step 2: Storyboard Generation (20s)
    def _step_2_generate_storyboard(self, state: VisionaryState) -> VisionaryState:
        """Step 2: Create visual storyboard from narrative structure."""
        step_start = time.time()
        logger.info("Step 2: Generating storyboard")

        try:
            narrative = state['narrative_structure'] or {}
            sections = narrative.get('sections', [])
            chunks = state['content_chunks']
            hooks = state['hooks']

            # Build scenes from narrative sections
            scenes = []
            cumulative_time = 0.0

            # If we have structured sections, use them
            if sections:
                for i, section in enumerate(sections):
                    section_name = section.get('name', f'scene_{i}')
                    section_chunks = [c for c in chunks if c.get('section') == section_name]

                    # Calculate scene duration
                    word_count = sum(len(c.get('text', '').split()) for c in section_chunks)
                    duration = max(3.0, word_count / 2.5)  # Min 3s per scene, 2.5 words/sec

                    scene = {
                        'scene_id': f"scene_{i:03d}",
                        'scene_number': i + 1,
                        'section': section_name,
                        'start_time': cumulative_time,
                        'duration': duration,
                        'end_time': cumulative_time + duration,
                        'word_count': word_count,
                        'chunk_count': len(section_chunks),
                        'visual_style': self._determine_scene_style(section_name),
                        'transition_in': SCENE_TRANSITIONS[i % len(SCENE_TRANSITIONS)] if i > 0 else "fade_from_black",
                        'transition_out': SCENE_TRANSITIONS[(i + 1) % len(SCENE_TRANSITIONS)] if i < len(sections) - 1 else "fade_to_black",
                        'text_summary': section_chunks[0]['text'][:100] if section_chunks else "",
                        'hook_text': hooks[i]['text'] if i < len(hooks) else ""
                    }
                    scenes.append(scene)
                    cumulative_time += duration
            else:
                # Fallback: create scenes from chunks directly
                for i, chunk in enumerate(chunks):
                    word_count = len(chunk.get('text', '').split())
                    duration = max(3.0, word_count / 2.5)

                    scene = {
                        'scene_id': f"scene_{i:03d}",
                        'scene_number': i + 1,
                        'section': chunk.get('section', 'body'),
                        'start_time': cumulative_time,
                        'duration': duration,
                        'end_time': cumulative_time + duration,
                        'word_count': word_count,
                        'chunk_count': 1,
                        'visual_style': state['visual_style'],
                        'transition_in': SCENE_TRANSITIONS[i % len(SCENE_TRANSITIONS)] if i > 0 else "fade_from_black",
                        'transition_out': SCENE_TRANSITIONS[(i + 1) % len(SCENE_TRANSITIONS)] if i < len(chunks) - 1 else "fade_to_black",
                        'text_summary': chunk.get('text', '')[:100],
                        'hook_text': hooks[i]['text'] if i < len(hooks) else ""
                    }
                    scenes.append(scene)
                    cumulative_time += duration

            # Build storyboard
            storyboard = {
                'storyboard_id': f"sb_{int(time.time())}",
                'total_duration': cumulative_time,
                'scene_count': len(scenes),
                'target_duration': state['total_duration'],
                'pacing_profile': self._determine_pacing(cumulative_time),
                'visual_style': state['visual_style'],
                'scenes': scenes,
                'generated_at': datetime.utcnow().isoformat()
            }

            state['storyboard'] = storyboard
            state['scenes'] = scenes
            state['scene_count'] = len(scenes)
            state['total_duration'] = cumulative_time
            state['pacing_profile'] = storyboard['pacing_profile']
            state['current_step'] = "generate_storyboard"
            state['step_times']['generate_storyboard'] = time.time() - step_start

            logger.info(
                f"Step 2 completed in {state['step_times']['generate_storyboard']:.2f}s: "
                f"{len(scenes)} scenes, {cumulative_time:.1f}s total duration"
            )

            return state

        except Exception as e:
            step_time = time.time() - step_start
            logger.error(f"Step 2 failed after {step_time:.2f}s: {str(e)}")
            state['error_message'] = str(e)
            state['error'] = {'error_type': 'storyboard_error', 'message': str(e), 'step': 'generate_storyboard'}
            raise

    # Step 3: B-Roll Prompting (15s)
    def _step_3_generate_broll_prompts(self, state: VisionaryState) -> VisionaryState:
        """Step 3: Generate AI image/video prompts for each scene."""
        step_start = time.time()
        logger.info("Step 3: Generating B-roll prompts")

        try:
            scenes = state['scenes']
            visual_style = state['visual_style']
            style_config = B_ROLL_TEMPLATES.get(visual_style, B_ROLL_TEMPLATES[VisualStyle.STOCK_FOOTAGE.value])

            b_roll_prompts = []

            for scene in scenes:
                # Build prompt from scene content
                text = scene.get('text_summary', '')
                section = scene.get('section', '')

                # Extract key visual concepts from text
                visual_concepts = self._extract_visual_concepts(text)

                # Generate primary prompt
                primary_prompt = f"{style_config['prefix']}{visual_concepts}{style_config['suffix']}"

                # Generate alternative prompts
                alternatives = self._generate_alternative_prompts(visual_concepts, style_config, section)

                prompt = {
                    'prompt_id': f"prompt_{scene['scene_id']}",
                    'scene_id': scene['scene_id'],
                    'scene_number': scene['scene_number'],
                    'timestamp': scene['start_time'],
                    'duration': scene['duration'],
                    'primary_prompt': primary_prompt,
                    'alternative_prompts': alternatives,
                    'negative_prompt': style_config['negative'],
                    'visual_style': visual_style,
                    'section': section,
                    'aspect_ratio': '9:16' if state['asset_type'] in ['youtube_short', 'tiktok', 'instagram_reel'] else '16:9',
                    'resolution': '1080x1920' if state['asset_type'] in ['youtube_short', 'tiktok', 'instagram_reel'] else '1920x1080',
                    'generation_params': {
                        'steps': 30,
                        'cfg_scale': 7.5,
                        'seed': hash(scene['scene_id']) % 2147483647
                    }
                }
                b_roll_prompts.append(prompt)

            state['b_roll_prompts'] = b_roll_prompts
            state['prompt_count'] = len(b_roll_prompts)
            state['prompt_style'] = visual_style
            state['current_step'] = "generate_broll_prompts"
            state['step_times']['generate_broll_prompts'] = time.time() - step_start

            logger.info(
                f"Step 3 completed in {state['step_times']['generate_broll_prompts']:.2f}s: "
                f"{len(b_roll_prompts)} prompts generated"
            )

            return state

        except Exception as e:
            step_time = time.time() - step_start
            logger.error(f"Step 3 failed after {step_time:.2f}s: {str(e)}")
            state['error_message'] = str(e)
            state['error'] = {'error_type': 'broll_prompt_error', 'message': str(e), 'step': 'generate_broll_prompts'}
            raise

    # Step 4: Visual Cue Mapping (10s)
    def _step_4_map_visual_cues(self, state: VisionaryState) -> VisionaryState:
        """Step 4: Map visual cues to exact timestamps."""
        step_start = time.time()
        logger.info("Step 4: Mapping visual cues")

        try:
            scenes = state['scenes']
            existing_cues = state['visual_cues']

            # Build transition map
            transition_map = []
            for i, scene in enumerate(scenes):
                transition = {
                    'transition_id': f"trans_{i:03d}",
                    'from_scene': scenes[i - 1]['scene_id'] if i > 0 else None,
                    'to_scene': scene['scene_id'],
                    'timestamp': scene['start_time'],
                    'type': scene['transition_in'],
                    'duration': 0.5  # Default 0.5s transition
                }
                transition_map.append(transition)

            # Merge existing cues from Trend-Jacker with new scene-based cues
            merged_cues = list(existing_cues) if existing_cues else []

            for scene in scenes:
                # Add scene-level visual cue
                cue = {
                    'cue_id': f"vc_{scene['scene_id']}",
                    'timestamp': scene['start_time'],
                    'duration': scene['duration'],
                    'scene_id': scene['scene_id'],
                    'visual_style': scene['visual_style'],
                    'transition': scene['transition_in'],
                    'text_overlay': scene.get('hook_text', '')[:60],
                    'b_roll_prompt_id': f"prompt_{scene['scene_id']}"
                }
                merged_cues.append(cue)

            state['visual_cues'] = merged_cues
            state['cue_count'] = len(merged_cues)
            state['transition_map'] = transition_map
            state['current_step'] = "map_visual_cues"
            state['step_times']['map_visual_cues'] = time.time() - step_start

            logger.info(
                f"Step 4 completed in {state['step_times']['map_visual_cues']:.2f}s: "
                f"{len(merged_cues)} cues, {len(transition_map)} transitions"
            )

            return state

        except Exception as e:
            step_time = time.time() - step_start
            logger.error(f"Step 4 failed after {step_time:.2f}s: {str(e)}")
            state['error_message'] = str(e)
            state['error'] = {'error_type': 'visual_cue_error', 'message': str(e), 'step': 'map_visual_cues'}
            raise

    # Step 5: Audio Design (10s)
    def _step_5_design_audio(self, state: VisionaryState) -> VisionaryState:
        """Step 5: Design audio mood, emphasis, and transitions."""
        step_start = time.time()
        logger.info("Step 5: Designing audio")

        try:
            scenes = state['scenes']
            engagement = state['engagement_score']

            # Determine overall mood from engagement score
            if engagement >= 0.8:
                mood = AudioMood.ENERGETIC.value
            elif engagement >= 0.6:
                mood = AudioMood.INSPIRING.value
            elif engagement >= 0.4:
                mood = AudioMood.CALM.value
            else:
                mood = AudioMood.MYSTERIOUS.value

            mood_config = AUDIO_MOOD_BPM.get(mood, AUDIO_MOOD_BPM[AudioMood.CALM.value])

            # Build audio cues per scene
            audio_cues = []
            for scene in scenes:
                section = scene.get('section', 'body')
                scene_mood = self._determine_scene_audio_mood(section, mood)

                audio_cue = {
                    'cue_id': f"ac_{scene['scene_id']}",
                    'timestamp': scene['start_time'],
                    'duration': scene['duration'],
                    'scene_id': scene['scene_id'],
                    'mood': scene_mood,
                    'bpm': mood_config['bpm'],
                    'genre': mood_config['genre'],
                    'instruments': mood_config['instruments'],
                    'volume': 0.8,
                    'fade_in': 0.3,
                    'fade_out': 0.5
                }
                audio_cues.append(audio_cue)

            # Build emphasis markers for key moments
            emphasis_markers = []
            for i, hook in enumerate(state['hooks']):
                if i < len(scenes):
                    marker = {
                        'marker_id': f"em_{i:03d}",
                        'timestamp': scenes[i]['start_time'],
                        'type': 'hook_emphasis',
                        'effect': 'volume_boost',
                        'intensity': 0.3,
                        'text': hook.get('text', '')[:50]
                    }
                    emphasis_markers.append(marker)

            # Build complete audio design
            audio_design = {
                'design_id': f"ad_{int(time.time())}",
                'overall_mood': mood,
                'background_mood': mood,
                'bpm': mood_config['bpm'],
                'genre': mood_config['genre'],
                'instruments': mood_config['instruments'],
                'total_duration': state['total_duration'],
                'cues': audio_cues,
                'emphasis_markers': emphasis_markers,
                'master_volume': 0.85,
                'generated_at': datetime.utcnow().isoformat()
            }

            state['audio_design'] = audio_design
            state['audio_cues'] = audio_cues
            state['background_mood'] = mood
            state['emphasis_markers'] = emphasis_markers
            state['current_step'] = "design_audio"
            state['step_times']['design_audio'] = time.time() - step_start

            logger.info(
                f"Step 5 completed in {state['step_times']['design_audio']:.2f}s: "
                f"mood={mood}, {len(audio_cues)} audio cues, {len(emphasis_markers)} emphasis markers"
            )

            return state

        except Exception as e:
            step_time = time.time() - step_start
            logger.error(f"Step 5 failed after {step_time:.2f}s: {str(e)}")
            state['error_message'] = str(e)
            state['error'] = {'error_type': 'audio_design_error', 'message': str(e), 'step': 'design_audio'}
            raise

    # Step 6: Asset Packaging (5s)
    def _step_6_package_assets(self, state: VisionaryState) -> VisionaryState:
        """Step 6: Bundle into Gumroad-ready package."""
        step_start = time.time()
        logger.info("Step 6: Packaging assets for Gumroad")

        try:
            package_id = f"vis_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

            # Generate thumbnail prompts
            thumbnail_prompts = self._generate_thumbnail_prompts(state)

            # Generate description copy
            description = self._generate_description_copy(state)

            # Generate hashtags
            hashtags = self._generate_hashtags(state)

            # Generate SEO keywords
            seo_keywords = self._generate_seo_keywords(state)

            # Build Gumroad-ready package
            output_package = {
                'package_id': package_id,
                'version': '1.0',
                'source_agent': 'visionary',
                'target': 'gumroad',
                'asset_type': state['asset_type'],
                'timestamp': datetime.utcnow().isoformat(),
                'metadata': {
                    'source_file': state['source_file'],
                    'total_duration': state['total_duration'],
                    'scene_count': state['scene_count'],
                    'visual_style': state['visual_style'],
                    'engagement_score': state['engagement_score'],
                    'retention_score': state['retention_score'],
                    'processing_time': state['processing_time']
                },
                'storyboard': state['storyboard'],
                'b_roll_prompts': state['b_roll_prompts'],
                'visual_cues': state['visual_cues'],
                'transition_map': state['transition_map'],
                'audio_design': state['audio_design'],
                'gumroad_listing': {
                    'title': self._generate_gumroad_title(state),
                    'description': description,
                    'thumbnail_prompts': thumbnail_prompts,
                    'hashtags': hashtags,
                    'seo_keywords': seo_keywords,
                    'price_tier': self._determine_price_tier(state),
                    'product_type': 'digital_asset_pack',
                    'file_format': 'json',
                    'compatible_with': ['midjourney', 'dalle', 'stable_diffusion', 'runway', 'pika']
                }
            }

            state['output_package'] = output_package
            state['package_id'] = package_id
            state['current_step'] = "package_assets"
            state['step_times']['package_assets'] = time.time() - step_start

            logger.info(
                f"Step 6 completed in {state['step_times']['package_assets']:.2f}s: "
                f"package_id={package_id}"
            )

            return state

        except Exception as e:
            step_time = time.time() - step_start
            logger.error(f"Step 6 failed after {step_time:.2f}s: {str(e)}")
            state['error_message'] = str(e)
            state['error'] = {'error_type': 'packaging_error', 'message': str(e), 'step': 'package_assets'}
            raise

    # Step 7: Output Generation (5s)
    def _step_7_generate_output(self, state: VisionaryState) -> VisionaryState:
        """Step 7: Write final assets to processed_gold/."""
        step_start = time.time()
        logger.info("Step 7: Generating output files")

        try:
            # Ensure output directory exists
            self.output_dir.mkdir(parents=True, exist_ok=True)

            # Generate output filename
            source_name = Path(state['source_file']).stem
            output_filename = f"{source_name}_{state['package_id']}.json"
            output_path = self.output_dir / output_filename

            # Write package to file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(state['output_package'], f, indent=2, ensure_ascii=False)

            state['output_path'] = str(output_path)
            state['current_step'] = "generate_output"
            state['step_times']['generate_output'] = time.time() - step_start

            logger.info(
                f"Step 7 completed in {state['step_times']['generate_output']:.2f}s: "
                f"output written to {output_path}"
            )

            return state

        except Exception as e:
            step_time = time.time() - step_start
            logger.error(f"Step 7 failed after {step_time:.2f}s: {str(e)}")
            state['error_message'] = str(e)
            state['error'] = {'error_type': 'output_error', 'message': str(e), 'step': 'generate_output'}
            raise

    # --- Helper Methods ---

    def _determine_scene_style(self, section: str) -> str:
        """Determine visual style for a scene based on its section."""
        style_map = {
            'hook': VisualStyle.CINEMATIC.value,
            'introduction': VisualStyle.MINIMALIST.value,
            'body': VisualStyle.STOCK_FOOTAGE.value,
            'conclusion': VisualStyle.CINEMATIC.value,
            'call_to_action': VisualStyle.SOCIAL_MEDIA.value
        }
        return style_map.get(section, VisualStyle.STOCK_FOOTAGE.value)

    def _determine_pacing(self, total_duration: float) -> str:
        """Determine pacing profile based on total duration."""
        if total_duration <= 30:
            return "fast"
        elif total_duration <= 60:
            return "medium"
        else:
            return "slow"

    def _extract_visual_concepts(self, text: str) -> str:
        """Extract key visual concepts from text for prompt generation."""
        # Extract nouns and key phrases
        words = text.split()
        if len(words) <= 5:
            return text
        # Take first meaningful chunk
        return ' '.join(words[:8])

    def _generate_alternative_prompts(self, concepts: str,
                                       style_config: Dict[str, str],
                                       section: str) -> List[str]:
        """Generate alternative prompt variations."""
        alternatives = []
        variations = [
            f"Wide angle establishing shot: {concepts}",
            f"Close-up detail shot: {concepts}",
            f"Drone aerial view: {concepts}"
        ]
        for var in variations[:2]:  # Limit to 2 alternatives
            alt = f"{var}{style_config['suffix']}"
            alternatives.append(alt)
        return alternatives

    def _determine_scene_audio_mood(self, section: str, default_mood: str) -> str:
        """Determine audio mood for a specific scene."""
        mood_map = {
            'hook': AudioMood.ENERGETIC.value,
            'introduction': AudioMood.CALM.value,
            'body': default_mood,
            'conclusion': AudioMood.INSPIRING.value,
            'call_to_action': AudioMood.URGENT.value
        }
        return mood_map.get(section, default_mood)

    def _generate_thumbnail_prompts(self, state: VisionaryState) -> List[Dict[str, str]]:
        """Generate YouTube thumbnail prompts."""
        hooks = state['hooks']
        thumbnail_prompts = []
        for i, hook in enumerate(hooks[:3]):  # Max 3 thumbnails
            prompt = {
                'variant': i + 1,
                'prompt': f"YouTube thumbnail, bold text '{hook.get('text', '')[:40]}', "
                          f"high contrast, vibrant colors, clickbait style, "
                          f"face close-up with expressive reaction, 1280x720",
                'style': 'youtube_thumbnail',
                'text_overlay': hook.get('text', '')[:40]
            }
            thumbnail_prompts.append(prompt)
        return thumbnail_prompts

    def _generate_description_copy(self, state: VisionaryState) -> str:
        """Generate Gumroad/YouTube description copy."""
        hooks = state['hooks']
        hook_text = hooks[0]['text'] if hooks else "Discover something amazing"

        return (
            f"{hook_text}\n\n"
            f"In this {state['asset_type'].replace('_', ' ')}, we explore fascinating insights "
            f"drawn from timeless wisdom and modern applications.\n\n"
            f"📦 What's Included:\n"
            f"• {state['scene_count']} scene storyboard\n"
            f"• {state['prompt_count']} AI-generated B-roll prompts\n"
            f"• Complete audio design with {len(state.get('audio_cues', []))} cues\n"
            f"• Visual transition map\n"
            f"• Thumbnail prompts\n\n"
            f"Perfect for content creators, YouTubers, and digital product sellers.\n\n"
            f"Generated by ALCHEMY - Temporal Content Transmuter"
        )

    def _generate_hashtags(self, state: VisionaryState) -> List[str]:
        """Generate relevant hashtags."""
        base_tags = ["content", "creator", "video", "broll", "prompts"]
        style_tags = {
            "cinematic": ["cinematic", "filmmaking", "broll"],
            "minimalist": ["minimalist", "aesthetic", "clean"],
            "social_media": ["viral", "trending", "fyp"],
            "documentary": ["documentary", "educational", "learn"],
            "corporate": ["business", "professional", "corporate"],
        }
        specific = style_tags.get(state['visual_style'], ["content", "creator"])
        return list(set(base_tags + specific))

    def _generate_seo_keywords(self, state: VisionaryState) -> List[str]:
        """Generate SEO keywords."""
        chunks = state['content_chunks']
        keywords = set()
        for chunk in chunks[:5]:
            text = chunk.get('text', '')
            words = [w.lower().strip('.,!?()[]{}":;') for w in text.split() if len(w) > 4]
            keywords.update(words[:5])
        return sorted(list(keywords))[:20]

    def _generate_gumroad_title(self, state: VisionaryState) -> str:
        """Generate Gumroad product title."""
        hooks = state['hooks']
        hook_text = hooks[0]['text'] if hooks else "Content Asset Pack"
        source = Path(state['source_file']).stem.replace('_', ' ').title()
        return f"{hook_text[:60]} | {source} | {state['scene_count']}-Scene Storyboard + B-Roll Prompts"

    def _determine_price_tier(self, state: VisionaryState) -> Dict[str, Any]:
        """Determine recommended price tier based on content quality."""
        score = (state['engagement_score'] + state['retention_score']) / 2
        if score >= 0.8:
            return {"tier": "premium", "recommended_price": 19.99, "currency": "USD"}
        elif score >= 0.6:
            return {"tier": "standard", "recommended_price": 12.99, "currency": "USD"}
        else:
            return {"tier": "basic", "recommended_price": 7.99, "currency": "USD"}

    def get_status(self) -> Dict[str, Any]:
        """Get current processing status."""
        if not self.state:
            return {
                'status': 'idle',
                'current_step': '',
                'package_id': None,
                'step_times': {},
                'error': None
            }

        return {
            'status': self.state['status'].value,
            'current_step': self.state['current_step'],
            'package_id': self.state['package_id'],
            'step_times': self.state['step_times'],
            'error': self.state['error']
        }


# Convenience function for quick Visionary processing
def process_visionary(input_package: Dict[str, Any],
                      asset_type: str = "youtube_short") -> Dict[str, Any]:
    """
    Convenience function to process Trend-Jacker package through Visionary workflow.

    Args:
        input_package: Package from Trend-Jacker agent
        asset_type: Target asset type

    Returns:
        Dictionary with processing results
    """
    agent = VisionaryAgent()
    return agent.process(input_package, asset_type)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python visionary.py <trend_jacker_package_path> [asset_type]")
        sys.exit(1)

    package_path = sys.argv[1]
    asset_type = sys.argv[2] if len(sys.argv) > 2 else "youtube_short"

    # Load Trend-Jacker package
    with open(package_path, 'r') as f:
        input_package = json.load(f)

    # Process through Visionary
    result = process_visionary(input_package, asset_type)

    # Print results
    print(f"Package ID: {result['package_id']}")
    print(f"Output Path: {result['output_path']}")
    print(f"Total Time: {result['total_time']:.2f}s")
    print(f"Status: {result['status']}")
    print(f"Workflow Mode: {result['workflow_mode']}")