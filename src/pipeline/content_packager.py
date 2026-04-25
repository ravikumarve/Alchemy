"""
Content Packager Module for Trend-Jacker Agent

Packages enhanced content for Visionary agent handoff.
Implements Step 7 of the Trend-Jacker workflow.

Time Budget: 5 seconds for packaging
"""

import json
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContentPackager:
    """
    Packages enhanced content for Visionary agent handoff.

    Creates a comprehensive package containing all the information
    the Visionary agent needs to generate media assets and B-roll.

    Time Budget: 5 seconds for packaging
    """

    def __init__(self):
        """Initialize ContentPackager with packaging configuration."""
        self.packaging_timeout = 5.0  # 5 second timeout

        # Package structure
        self.package_structure = {
            "metadata": {
                "package_id": str,
                "timestamp": str,
                "source_file": str,
                "content_type": str,
                "total_duration": float,
                "word_count": int,
                "chunk_count": int
            },
            "narrative": {
                "structure": dict,
                "sections": list,
                "coherence_score": float,
                "flow_score": float
            },
            "hooks": list,
            "content_chunks": list,
            "enhancement_metrics": dict,
            "engagement_score": float,
            "retention_score": float,
            "visual_cues": list,
            "audio_cues": list,
            "timing_markers": list
        }

    def package(self, enhanced_content: List[Dict[str, Any]], narrative_structure: Dict[str, Any], hooks: List[Dict[str, Any]], enhancement_metrics: Dict[str, float], engagement_score: float, retention_score: float, source_file: str) -> Dict[str, Any]:
        """
        Package enhanced content for Visionary agent.

        Args:
            enhanced_content: Enhanced content chunks
            narrative_structure: Structured narrative
            hooks: Generated hooks
            enhancement_metrics: Enhancement metrics
            engagement_score: Overall engagement score
            retention_score: Overall retention score
            source_file: Source file path

        Returns:
            Dictionary containing:
            - package: Complete package for Visionary
            - package_id: Unique package identifier
            - packaging_time: Time taken for packaging

        Raises:
            TimeoutError: If packaging exceeds time budget
        """
        start_time = time.time()

        logger.info("Starting content packaging for Visionary")

        try:
            # Generate package ID
            package_id = self._generate_package_id()

            # Create package metadata
            metadata = self._create_metadata(package_id, source_file, enhanced_content)

            # Extract visual cues
            visual_cues = self._extract_visual_cues(enhanced_content, narrative_structure)

            # Extract audio cues
            audio_cues = self._extract_audio_cues(enhanced_content, narrative_structure)

            # Create timing markers
            timing_markers = self._create_timing_markers(enhanced_content, narrative_structure)

            # Build complete package
            package = {
                'metadata': metadata,
                'narrative': {
                    'structure': narrative_structure.get('structure', {}),
                    'sections': narrative_structure.get('sections', []),
                    'coherence_score': narrative_structure.get('coherence_score', 0.0),
                    'flow_score': narrative_structure.get('flow_score', 0.0)
                },
                'hooks': hooks,
                'content_chunks': enhanced_content,
                'enhancement_metrics': enhancement_metrics,
                'engagement_score': engagement_score,
                'retention_score': retention_score,
                'visual_cues': visual_cues,
                'audio_cues': audio_cues,
                'timing_markers': timing_markers
            }

            packaging_time = time.time() - start_time

            # Check timeout
            if packaging_time > self.packaging_timeout:
                logger.warning(
                    f"Content packaging exceeded time budget: {packaging_time:.2f}s > {self.packaging_timeout}s"
                )

            result = {
                'package': package,
                'package_id': package_id,
                'packaging_time': packaging_time
            }

            logger.info(
                f"Content packaging completed in {packaging_time:.2f}s: "
                f"package_id={package_id}, chunks={len(enhanced_content)}, visual_cues={len(visual_cues)}"
            )

            return result

        except Exception as e:
            packaging_time = time.time() - start_time
            logger.error(f"Content packaging failed after {packaging_time:.2f}s: {str(e)}")
            raise

    def _generate_package_id(self) -> str:
        """
        Generate unique package identifier.

        Returns:
            Unique package ID
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"tj_{timestamp}"

    def _create_metadata(self, package_id: str, source_file: str, enhanced_content: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create package metadata.

        Args:
            package_id: Package identifier
            source_file: Source file path
            enhanced_content: Enhanced content chunks

        Returns:
            Package metadata
        """
        # Calculate total word count
        total_words = sum(len(chunk.get('text', '').split()) for chunk in enhanced_content)

        # Estimate total duration (assuming 150 words per minute)
        total_duration = total_words / 150.0 * 60.0  # in seconds

        return {
            'package_id': package_id,
            'timestamp': datetime.now().isoformat(),
            'source_file': source_file,
            'content_type': 'enhanced_narrative',
            'total_duration': total_duration,
            'word_count': total_words,
            'chunk_count': len(enhanced_content)
        }

    def _extract_visual_cues(self, enhanced_content: List[Dict[str, Any]], narrative_structure: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract visual cues for media generation.

        Args:
            enhanced_content: Enhanced content chunks
            narrative_structure: Narrative structure

        Returns:
            List of visual cues
        """
        visual_cues = []

        for i, chunk in enumerate(enhanced_content):
            text = chunk.get('text', '')
            section = chunk.get('section', '')

            # Extract visual descriptions
            visual_descriptions = self._extract_visual_descriptions(text)

            # Determine visual style based on section
            visual_style = self._determine_visual_style(section, narrative_structure)

            # Calculate timing for this visual
            timing = self._calculate_visual_timing(chunk, enhanced_content)

            if visual_descriptions or visual_style:
                visual_cue = {
                    'cue_id': f"vc_{i}",
                    'timestamp': timing['start'],
                    'duration': timing['duration'],
                    'section': section,
                    'visual_style': visual_style,
                    'descriptions': visual_descriptions,
                    'text_context': text[:100] + '...' if len(text) > 100 else text
                }
                visual_cues.append(visual_cue)

        return visual_cues

    def _extract_visual_descriptions(self, text: str) -> List[str]:
        """
        Extract visual descriptions from text.

        Args:
            text: Text content

        Returns:
            List of visual descriptions
        """
        descriptions = []

        # Look for visual keywords
        visual_keywords = [
            'imagine', 'picture', 'visualize', 'see', 'look',
            'show', 'display', 'appear', 'emerge', 'reveal',
            'bright', 'dark', 'color', 'shape', 'size'
        ]

        words = text.split()
        for i, word in enumerate(words):
            if word.lower() in visual_keywords:
                # Extract context around the visual keyword
                context_start = max(0, i - 3)
                context_end = min(len(words), i + 4)
                context = ' '.join(words[context_start:context_end])
                descriptions.append(context)

        return descriptions

    def _determine_visual_style(self, section: str, narrative_structure: Dict[str, Any]) -> str:
        """
        Determine visual style based on section.

        Args:
            section: Section name
            narrative_structure: Narrative structure

        Returns:
            Visual style
        """
        style_mapping = {
            'hook': 'dynamic_fast',
            'introduction': 'clean_professional',
            'body': 'engaging_varied',
            'conclusion': 'inspiring_uplifting',
            'call_to_action': 'motivational_energetic'
        }

        return style_mapping.get(section, 'neutral_balanced')

    def _calculate_visual_timing(self, chunk: Dict[str, Any], enhanced_content: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate timing for visual cue.

        Args:
            chunk: Content chunk
            enhanced_content: All enhanced content

        Returns:
            Dictionary with start time and duration
        """
        # Calculate cumulative timing
        chunk_index = enhanced_content.index(chunk)
        word_count = len(chunk.get('text', '').split())

        # Assume 2.5 words per second for speaking pace
        duration = word_count / 2.5

        # Calculate start time based on previous chunks
        start_time = 0.0
        for i in range(chunk_index):
            prev_word_count = len(enhanced_content[i].get('text', '').split())
            start_time += prev_word_count / 2.5

        return {
            'start': start_time,
            'duration': duration
        }

    def _extract_audio_cues(self, enhanced_content: List[Dict[str, Any]], narrative_structure: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract audio cues for media generation.

        Args:
            enhanced_content: Enhanced content chunks
            narrative_structure: Narrative structure

        Returns:
            List of audio cues
        """
        audio_cues = []

        for i, chunk in enumerate(enhanced_content):
            text = chunk.get('text', '')
            section = chunk.get('section', '')

            # Extract audio mood
            audio_mood = self._determine_audio_mood(section, narrative_structure)

            # Extract emphasis points
            emphasis_points = self._extract_emphasis_points(text)

            # Calculate timing for this audio
            timing = self._calculate_audio_timing(chunk, enhanced_content)

            if audio_mood or emphasis_points:
                audio_cue = {
                    'cue_id': f"ac_{i}",
                    'timestamp': timing['start'],
                    'duration': timing['duration'],
                    'section': section,
                    'audio_mood': audio_mood,
                    'emphasis_points': emphasis_points,
                    'text_context': text[:100] + '...' if len(text) > 100 else text
                }
                audio_cues.append(audio_cue)

        return audio_cues

    def _determine_audio_mood(self, section: str, narrative_structure: Dict[str, Any]) -> str:
        """
        Determine audio mood based on section.

        Args:
            section: Section name
            narrative_structure: Narrative structure

        Returns:
            Audio mood
        """
        mood_mapping = {
            'hook': 'energetic_attention',
            'introduction': 'warm_welcoming',
            'body': 'engaging_dynamic',
            'conclusion': 'inspiring_uplifting',
            'call_to_action': 'motivational_urgent'
        }

        return mood_mapping.get(section, 'neutral_balanced')

    def _extract_emphasis_points(self, text: str) -> List[str]:
        """
        Extract emphasis points from text.

        Args:
            text: Text content

        Returns:
            List of emphasis points
        """
        emphasis_points = []

        # Look for emphasis keywords
        emphasis_keywords = [
            'important', 'crucial', 'essential', 'key', 'critical',
            'remember', 'note', 'notice', 'realize', 'understand'
        ]

        words = text.split()
        for i, word in enumerate(words):
            if word.lower() in emphasis_keywords:
                # Extract context around the emphasis keyword
                context_start = max(0, i - 2)
                context_end = min(len(words), i + 3)
                context = ' '.join(words[context_start:context_end])
                emphasis_points.append(context)

        return emphasis_points

    def _calculate_audio_timing(self, chunk: Dict[str, Any], enhanced_content: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate timing for audio cue.

        Args:
            chunk: Content chunk
            enhanced_content: All enhanced content

        Returns:
            Dictionary with start time and duration
        """
        # Same timing calculation as visual
        return self._calculate_visual_timing(chunk, enhanced_content)

    def _create_timing_markers(self, enhanced_content: List[Dict[str, Any]], narrative_structure: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create timing markers for the entire content.

        Args:
            enhanced_content: Enhanced content chunks
            narrative_structure: Narrative structure

        Returns:
            List of timing markers
        """
        timing_markers = []

        # Create markers for each section
        sections = narrative_structure.get('sections', [])
        for section in sections:
            section_name = section.get('name', '')
            section_chunks = [c for c in enhanced_content if c.get('section') == section_name]

            if section_chunks:
                first_chunk = section_chunks[0]
                last_chunk = section_chunks[-1]

                start_time = self._calculate_visual_timing(first_chunk, enhanced_content)['start']
                end_time = self._calculate_visual_timing(last_chunk, enhanced_content)['start'] + \
                          self._calculate_visual_timing(last_chunk, enhanced_content)['duration']

                timing_marker = {
                    'marker_id': f"tm_{section_name}",
                    'section': section_name,
                    'start_time': start_time,
                    'end_time': end_time,
                    'duration': end_time - start_time,
                    'chunk_count': len(section_chunks)
                }
                timing_markers.append(timing_marker)

        return timing_markers

    def save_package(self, package: Dict[str, Any], output_path: str) -> None:
        """
        Save package to file.

        Args:
            package: Package to save
            output_path: Output file path
        """
        try:
            with open(output_path, 'w') as f:
                json.dump(package, f, indent=2)
            logger.info(f"Package saved to {output_path}")
        except Exception as e:
            logger.error(f"Failed to save package: {str(e)}")
            raise

    def load_package(self, input_path: str) -> Dict[str, Any]:
        """
        Load package from file.

        Args:
            input_path: Input file path

        Returns:
            Loaded package
        """
        try:
            with open(input_path, 'r') as f:
                package = json.load(f)
            logger.info(f"Package loaded from {input_path}")
            return package
        except Exception as e:
            logger.error(f"Failed to load package: {str(e)}")
            raise


# Convenience function for quick content packaging
def package_content(enhanced_content: List[Dict[str, Any]], narrative_structure: Dict[str, Any], hooks: List[Dict[str, Any]], enhancement_metrics: Dict[str, float], engagement_score: float, retention_score: float, source_file: str) -> Dict[str, Any]:
    """
    Convenience function to package content.

    Args:
        enhanced_content: Enhanced content chunks
        narrative_structure: Narrative structure
        hooks: Generated hooks
        enhancement_metrics: Enhancement metrics
        engagement_score: Overall engagement score
        retention_score: Overall retention score
        source_file: Source file path

    Returns:
        Dictionary with packaging results
    """
    packager = ContentPackager()
    return packager.package(enhanced_content, narrative_structure, hooks, enhancement_metrics, engagement_score, retention_score, source_file)
