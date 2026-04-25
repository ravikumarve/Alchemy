"""
Narrative Structurer Module for Trend-Jacker Agent

Structures content for engagement and storytelling flow.
Implements Step 4 of the Trend-Jacker workflow.

Time Budget: 25 seconds for narrative structuring
"""

import re
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NarrativeStructurer:
    """
    Structures content for engagement and storytelling flow.

    Organizes content chunks into a compelling narrative structure
    with proper pacing, engagement points, and storytelling elements.

    Time Budget: 25 seconds for structuring
    """

    def __init__(self):
        """Initialize NarrativeStructurer with structuring configuration."""
        self.structuring_timeout = 25.0  # 25 second timeout

        # Narrative structures
        self.narrative_structures = {
            "problem_solution": {
                "sections": ["hook", "problem", "agitation", "solution", "benefit", "cta"],
                "description": "Problem-Agitation-Solution framework"
            },
            "story_based": {
                "sections": ["hook", "background", "conflict", "climax", "resolution", "lesson"],
                "description": "Story-based narrative arc"
            },
            "educational": {
                "sections": ["hook", "concept", "explanation", "example", "application", "summary"],
                "description": "Educational content structure"
            },
            "listicle": {
                "sections": ["hook", "intro", "item1", "item2", "item3", "item4", "item5", "conclusion"],
                "description": "List-based content structure"
            },
            "comparison": {
                "sections": ["hook", "intro", "option_a", "option_b", "comparison", "recommendation", "cta"],
                "description": "Comparison-based structure"
            }
        }

        # Engagement elements
        self.engagement_elements = {
            "pattern_interrupt": "Break the pattern to grab attention",
            "curiosity_gap": "Create information gap to maintain interest",
            "social_proof": "Use social proof to build credibility",
            "emotional_connection": "Create emotional resonance",
            "storytelling": "Use narrative elements for engagement",
            "actionable_insights": "Provide actionable takeaways",
            "visual_descriptions": "Include vivid descriptions",
            "relatable_examples": "Use relatable examples and analogies"
        }

    def structure(self, content_chunks: List[Dict[str, Any]], hooks: List[Dict[str, Any]], trends: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Structure content for engagement.

        Args:
            content_chunks: Content chunks from Archaeologist
            hooks: Generated hooks
            trends: Mapped trends

        Returns:
            Dictionary containing:
            - narrative_structure: Structured narrative
            - content_flow: Content flow and pacing
            - engagement_points: Key engagement moments
            - structuring_time: Time taken for structuring

        Raises:
            TimeoutError: If structuring exceeds time budget
        """
        start_time = time.time()

        logger.info("Starting narrative structuring")

        try:
            # Determine best narrative structure
            best_structure = self._determine_best_structure(content_chunks, hooks)

            # Organize content into narrative sections
            organized_content = self._organize_content(content_chunks, best_structure)

            # Create content flow
            content_flow = self._create_content_flow(organized_content, best_structure)

            # Identify engagement points
            engagement_points = self._identify_engagement_points(organized_content, hooks)

            # Calculate coherence score
            coherence_score = self._calculate_coherence_score(organized_content, content_flow)

            narrative_structure = {
                'structure_type': best_structure,
                'sections': organized_content,
                'coherence_score': coherence_score,
                'total_sections': len(organized_content),
                'estimated_duration': self._estimate_duration(organized_content)
            }

            structuring_time = time.time() - start_time

            # Check timeout
            if structuring_time > self.structuring_timeout:
                logger.warning(
                    f"Narrative structuring exceeded time budget: {structuring_time:.2f}s > {self.structuring_timeout}s"
                )

            result = {
                'narrative_structure': narrative_structure,
                'content_flow': content_flow,
                'engagement_points': engagement_points,
                'structuring_time': structuring_time
            }

            logger.info(
                f"Narrative structuring completed in {structuring_time:.2f}s: "
                f"structure={best_structure}, sections={len(organized_content)}, coherence={coherence_score:.2f}"
            )

            return result

        except Exception as e:
            structuring_time = time.time() - start_time
            logger.error(f"Narrative structuring failed after {structuring_time:.2f}s: {str(e)}")
            raise

    def _determine_best_structure(self, content_chunks: List[Dict[str, Any]], hooks: List[Dict[str, Any]]) -> str:
        """
        Determine the best narrative structure for the content.

        Args:
            content_chunks: Content chunks
            hooks: Generated hooks

        Returns:
            Best structure type
        """
        # Analyze content characteristics
        content_types = [chunk.get('content_type', 'general') for chunk in content_chunks]

        # Count content types
        type_counts = {}
        for content_type in content_types:
            type_counts[content_type] = type_counts.get(content_type, 0) + 1

        # Determine structure based on content
        if 'tutorial' in type_counts or 'how to' in type_counts:
            return 'educational'
        elif 'example' in type_counts and type_counts.get('example', 0) > 2:
            return 'story_based'
        elif 'comparison' in type_counts:
            return 'comparison'
        elif len(content_chunks) >= 5:
            return 'listicle'
        else:
            return 'problem_solution'

    def _organize_content(self, content_chunks: List[Dict[str, Any]], structure_type: str) -> List[Dict[str, Any]]:
        """
        Organize content into narrative sections.

        Args:
            content_chunks: Content chunks
            structure_type: Type of narrative structure

        Returns:
            List of organized sections
        """
        structure_def = self.narrative_structures.get(structure_type, self.narrative_structures['problem_solution'])
        sections = structure_def['sections']

        organized = []

        # Distribute content chunks across sections
        chunks_per_section = max(1, len(content_chunks) // len(sections))

        for i, section_name in enumerate(sections):
            start_idx = i * chunks_per_section
            end_idx = start_idx + chunks_per_section

            section_chunks = content_chunks[start_idx:end_idx]

            if section_chunks:
                organized.append({
                    'section_name': section_name,
                    'chunks': section_chunks,
                    'chunk_count': len(section_chunks),
                    'total_length': sum(len(chunk.get('text', '')) for chunk in section_chunks),
                    'purpose': self._get_section_purpose(section_name)
                })

        return organized

    def _get_section_purpose(self, section_name: str) -> str:
        """
        Get the purpose of a narrative section.

        Args:
            section_name: Name of the section

        Returns:
            Purpose description
        """
        purposes = {
            'hook': 'Grab attention and create curiosity',
            'problem': 'Identify the problem or pain point',
            'agitation': 'Amplify the problem and create urgency',
            'solution': 'Present the solution or approach',
            'benefit': 'Highlight benefits and outcomes',
            'cta': 'Call to action or next steps',
            'background': 'Provide context and background',
            'conflict': 'Introduce conflict or tension',
            'climax': 'Build to the peak moment',
            'resolution': 'Resolve the conflict',
            'lesson': 'Extract key lessons and insights',
            'concept': 'Introduce the core concept',
            'explanation': 'Explain how it works',
            'example': 'Provide concrete examples',
            'application': 'Show how to apply it',
            'summary': 'Summarize key points',
            'intro': 'Introduce the topic',
            'item1': 'First key point',
            'item2': 'Second key point',
            'item3': 'Third key point',
            'item4': 'Fourth key point',
            'item5': 'Fifth key point',
            'conclusion': 'Wrap up and provide final thoughts',
            'option_a': 'Present first option',
            'option_b': 'Present second option',
            'comparison': 'Compare options directly',
            'recommendation': 'Provide recommendation',
        }

        return purposes.get(section_name, 'Support the narrative flow')

    def _create_content_flow(self, organized_content: List[Dict[str, Any]], structure_type: str) -> List[Dict[str, Any]]:
        """
        Create content flow and pacing information.

        Args:
            organized_content: Organized content sections
            structure_type: Type of narrative structure

        Returns:
            List of content flow elements
        """
        flow = []

        for i, section in enumerate(organized_content):
            flow.append({
                'section_index': i,
                'section_name': section['section_name'],
                'estimated_duration': self._estimate_section_duration(section),
                'engagement_level': self._estimate_section_engagement(section, i),
                'transition_to': organized_content[i + 1]['section_name'] if i + 1 < len(organized_content) else None,
                'key_message': self._extract_key_message(section)
            })

        return flow

    def _estimate_section_duration(self, section: Dict[str, Any]) -> float:
        """
        Estimate duration of a section in seconds.

        Args:
            section: Content section

        Returns:
            Estimated duration in seconds
        """
        total_length = section.get('total_length', 0)
        # Average reading speed: 200 words per minute
        # Average word length: 5 characters
        words = total_length / 5
        minutes = words / 200
        return minutes * 60  # Convert to seconds

    def _estimate_section_engagement(self, section: Dict[str, Any], section_index: int) -> str:
        """
        Estimate engagement level of a section.

        Args:
            section: Content section
            section_index: Index of the section

        Returns:
            Engagement level (high, medium, low)
        """
        section_name = section['section_name'].lower()

        # Hook and conclusion sections typically have high engagement
        if section_name in ['hook', 'climax', 'cta', 'conclusion']:
            return 'high'
        # Middle sections have medium engagement
        elif section_index > 0 and section_index < len(section) - 1:
            return 'medium'
        # Other sections have low engagement
        else:
            return 'low'

    def _extract_key_message(self, section: Dict[str, Any]) -> str:
        """
        Extract key message from a section.

        Args:
            section: Content section

        Returns:
            Key message summary
        """
        chunks = section.get('chunks', [])
        if not chunks:
            return "No content"

        # Get first chunk's text as key message
        first_chunk = chunks[0]
        text = first_chunk.get('text', '')

        # Truncate to reasonable length
        if len(text) > 100:
            text = text[:97] + '...'

        return text

    def _identify_engagement_points(self, organized_content: List[Dict[str, Any]], hooks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Identify key engagement points in the narrative.

        Args:
            organized_content: Organized content sections
            hooks: Generated hooks

        Returns:
            List of engagement points
        """
        engagement_points = []

        # Add hooks as engagement points
        for i, hook in enumerate(hooks[:3]):  # Top 3 hooks
            engagement_points.append({
                'type': 'hook',
                'position': 'opening',
                'content': hook['text'],
                'hook_type': hook['hook_type'],
                'quality_score': hook['quality_score']
            })

        # Add section transitions as engagement points
        for i, section in enumerate(organized_content):
            if i > 0:  # Skip first section
                engagement_points.append({
                    'type': 'transition',
                    'position': f'section_{i}',
                    'content': f"Moving to {section['section_name']}",
                    'engagement_level': self._estimate_section_engagement(section, i)
                })

        # Add conclusion as engagement point
        if organized_content:
            last_section = organized_content[-1]
            engagement_points.append({
                'type': 'conclusion',
                'position': 'closing',
                'content': 'Final thoughts and call to action',
                'engagement_level': 'high'
            })

        return engagement_points

    def _calculate_coherence_score(self, organized_content: List[Dict[str, Any]], content_flow: List[Dict[str, Any]]) -> float:
        """
        Calculate coherence score for the narrative.

        Args:
            organized_content: Organized content sections
            content_flow: Content flow

        Returns:
            Coherence score between 0.0 and 1.0
        """
        if not organized_content:
            return 0.0

        # Base score
        coherence_score = 0.5

        # Check for logical flow
        if len(organized_content) > 1:
            coherence_score += 0.2

        # Check for engagement distribution
        high_engagement = sum(1 for point in content_flow if point['engagement_level'] == 'high')
        if high_engagement >= 2:
            coherence_score += 0.2

        # Check for balanced sections
        section_lengths = [section['total_length'] for section in organized_content]
        if section_lengths:
            avg_length = sum(section_lengths) / len(section_lengths)
            balanced = all(abs(length - avg_length) < avg_length * 0.5 for length in section_lengths)
            if balanced:
                coherence_score += 0.1

        return min(1.0, coherence_score)

    def _estimate_duration(self, organized_content: List[Dict[str, Any]]) -> float:
        """
        Estimate total duration of the narrative.

        Args:
            organized_content: Organized content sections

        Returns:
            Estimated duration in seconds
        """
        total_duration = sum(self._estimate_section_duration(section) for section in organized_content)
        return total_duration


# Convenience function for quick narrative structuring
def structure_narrative(content_chunks: List[Dict[str, Any]], hooks: List[Dict[str, Any]], trends: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Convenience function to structure narrative.

    Args:
        content_chunks: Content chunks
        hooks: Generated hooks
        trends: Mapped trends

    Returns:
        Dictionary with structured narrative
    """
    structurer = NarrativeStructurer()
    return structurer.structure(content_chunks, hooks, trends)
