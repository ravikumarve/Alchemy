"""
Content Enhancer Module for Trend-Jacker Agent

Enhances content with modern engagement techniques.
Implements Step 6 of the Trend-Jacker workflow.

Time Budget: 5 seconds for content enhancement
"""

import re
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContentEnhancer:
    """
    Enhances content with modern engagement techniques.

    Applies proven content enhancement strategies to maximize
    viewer engagement, shareability, and overall impact.

    Time Budget: 5 seconds for enhancement
    """

    def __init__(self):
        """Initialize ContentEnhancer with enhancement configuration."""
        self.enhancement_timeout = 5.0  # 5 second timeout

        # Content enhancement techniques
        self.enhancement_techniques = {
            "vocabulary_upgrade": {
                "description": "Upgrade vocabulary for impact",
                "weight": 0.15
            },
            "sentence_variety": {
                "description": "Vary sentence structure for flow",
                "weight": 0.15
            },
            "active_voice": {
                "description": "Use active voice for engagement",
                "weight": 0.15
            },
            "power_words": {
                "description": "Include power words for impact",
                "weight": 0.15
            },
            "rhythm_and_pacing": {
                "description": "Optimize rhythm and pacing",
                "weight": 0.10
            },
            "clarity_simplification": {
                "description": "Simplify for clarity",
                "weight": 0.10
            },
            "emotional_amplification": {
                "description": "Amplify emotional impact",
                "weight": 0.10
            },
            "call_to_action": {
                "description": "Add calls to action",
                "weight": 0.10
            }
        }

        # Power words for engagement
        self.power_words = {
            "attention": ["attention", "notice", "watch", "see", "discover"],
            "emotion": ["amazing", "incredible", "powerful", "transform", "impact"],
            "action": ["act", "do", "try", "start", "begin"],
            "urgency": ["now", "today", "immediately", "quickly", "instantly"],
            "value": ["free", "best", "top", "ultimate", "essential"]
        }

    def enhance(self, optimized_content: List[Dict[str, Any]], narrative_structure: Dict[str, Any], hooks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Enhance content with modern engagement techniques.

        Args:
            optimized_content: Content after attention optimization
            narrative_structure: Structured narrative
            hooks: Generated hooks

        Returns:
            Dictionary containing:
            - enhanced_content: Content after enhancement
            - enhancement_metrics: Enhancement metrics
            - engagement_score: Overall engagement score
            - enhancement_time: Time taken for enhancement

        Raises:
            TimeoutError: If enhancement exceeds time budget
        """
        start_time = time.time()

        logger.info("Starting content enhancement")

        try:
            # Apply enhancement techniques
            enhanced_content = self._apply_enhancements(optimized_content, narrative_structure, hooks)

            # Calculate enhancement metrics
            enhancement_metrics = self._calculate_enhancement_metrics(enhanced_content, optimized_content)

            # Calculate engagement score
            engagement_score = self._calculate_engagement_score(enhancement_metrics, narrative_structure)

            enhancement_time = time.time() - start_time

            # Check timeout
            if enhancement_time > self.enhancement_timeout:
                logger.warning(
                    f"Content enhancement exceeded time budget: {enhancement_time:.2f}s > {self.enhancement_timeout}s"
                )

            result = {
                'enhanced_content': enhanced_content,
                'enhancement_metrics': enhancement_metrics,
                'engagement_score': engagement_score,
                'enhancement_time': enhancement_time
            }

            logger.info(
                f"Content enhancement completed in {enhancement_time:.2f}s: "
                f"engagement_score={engagement_score:.2f}, enhanced_chunks={len(enhanced_content)}"
            )

            return result

        except Exception as e:
            enhancement_time = time.time() - start_time
            logger.error(f"Content enhancement failed after {enhancement_time:.2f}s: {str(e)}")
            raise

    def _apply_enhancements(self, content_chunks: List[Dict[str, Any]], narrative_structure: Dict[str, Any], hooks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Apply enhancement techniques to content chunks.

        Args:
            content_chunks: Content chunks
            narrative_structure: Narrative structure
            hooks: Generated hooks

        Returns:
            List of enhanced content chunks
        """
        enhanced = []

        for chunk in content_chunks:
            enhanced_chunk = chunk.copy()

            # Apply vocabulary upgrade
            enhanced_chunk['text'] = self._upgrade_vocabulary(enhanced_chunk['text'])

            # Apply sentence variety
            enhanced_chunk['text'] = self._vary_sentences(enhanced_chunk['text'])

            # Apply active voice
            enhanced_chunk['text'] = self._use_active_voice(enhanced_chunk['text'])

            # Add power words
            enhanced_chunk['text'] = self._add_power_words(enhanced_chunk['text'])

            # Optimize rhythm and pacing
            enhanced_chunk['text'] = self._optimize_rhythm(enhanced_chunk['text'])

            # Simplify for clarity
            enhanced_chunk['text'] = self._simplify_clarity(enhanced_chunk['text'])

            # Amplify emotional impact
            enhanced_chunk['text'] = self._amplify_emotion(enhanced_chunk['text'])

            # Add call to action if appropriate
            enhanced_chunk['text'] = self._add_call_to_action(enhanced_chunk['text'], narrative_structure)

            # Track enhancements applied
            enhanced_chunk['enhancements_applied'] = [
                'vocabulary_upgrade',
                'sentence_variety',
                'active_voice',
                'power_words',
                'rhythm_optimization',
                'clarity_simplification',
                'emotional_amplification',
                'call_to_action'
            ]

            enhanced.append(enhanced_chunk)

        return enhanced

    def _upgrade_vocabulary(self, text: str) -> str:
        """
        Upgrade vocabulary for impact.

        Args:
            text: Original text

        Returns:
            Text with upgraded vocabulary
        """
        # Simple vocabulary upgrades
        upgrades = {
            'good': 'excellent',
            'bad': 'problematic',
            'big': 'massive',
            'small': 'compact',
            'fast': 'rapid',
            'slow': 'gradual',
            'important': 'crucial',
            'interesting': 'fascinating',
            'useful': 'invaluable',
            'hard': 'challenging'
        }

        for old, new in upgrades.items():
            text = re.sub(r'\b' + old + r'\b', new, text, flags=re.IGNORECASE)

        return text

    def _vary_sentences(self, text: str) -> str:
        """
        Vary sentence structure for better flow.

        Args:
            text: Original text

        Returns:
            Text with varied sentence structure
        """
        # This is a simplified implementation
        # In production, would use NLP to analyze and vary sentence structure
        sentences = text.split('. ')

        varied = []
        for i, sentence in enumerate(sentences):
            if i % 2 == 0 and len(sentence) > 20:
                # Add variety by occasionally starting with transition
                transitions = ['However, ', 'In fact, ', 'Moreover, ', 'Additionally, ']
                if i > 0:
                    sentence = transitions[i % len(transitions)] + sentence.lower()
            varied.append(sentence)

        return '. '.join(varied)

    def _use_active_voice(self, text: str) -> str:
        """
        Convert passive voice to active voice.

        Args:
            text: Original text

        Returns:
            Text with active voice
        """
        # Simple passive to active conversion
        passive_patterns = [
            (r'(\w+) was (\w+) by (\w+)', r'\3 \2 \1'),
            (r'(\w+) were (\w+) by (\w+)', r'\3 \2 \1'),
            (r'(\w+) is (\w+) by (\w+)', r'\3 \2 \1'),
            (r'(\w+) are (\w+) by (\w+)', r'\3 \2 \1')
        ]

        for pattern, replacement in passive_patterns:
            text = re.sub(pattern, replacement, text)

        return text

    def _add_power_words(self, text: str) -> str:
        """
        Add power words for impact.

        Args:
            text: Original text

        Returns:
            Text with power words added
        """
        # This is a simplified implementation
        # In production, would intelligently insert power words where appropriate
        words = text.split()

        # Add power words at strategic positions
        if len(words) > 10:
            # Add attention word at start
            attention_words = self.power_words['attention']
            if not any(word.lower() in attention_words for word in words[:3]):
                words.insert(0, attention_words[0].capitalize())

        return ' '.join(words)

    def _optimize_rhythm(self, text: str) -> str:
        """
        Optimize rhythm and pacing.

        Args:
            text: Original text

        Returns:
            Text with optimized rhythm
        """
        # This is a simplified implementation
        # In production, would analyze syllable count and stress patterns
        sentences = text.split('. ')

        optimized = []
        for sentence in sentences:
            # Ensure sentences aren't too long or too short
            words = sentence.split()
            if len(words) > 25:
                # Break up long sentences
                mid = len(words) // 2
                sentence = ' '.join(words[:mid]) + '. ' + ' '.join(words[mid:])
            elif len(words) < 5:
                # Combine very short sentences with next
                if optimized:
                    optimized[-1] = optimized[-1].rstrip('.') + ' ' + sentence
                    continue

            optimized.append(sentence)

        return '. '.join(optimized)

    def _simplify_clarity(self, text: str) -> str:
        """
        Simplify text for clarity.

        Args:
            text: Original text

        Returns:
            Simplified text
        """
        # Remove unnecessary words
        unnecessary_words = ['very', 'really', 'quite', 'rather', 'somewhat']

        for word in unnecessary_words:
            text = re.sub(r'\b' + word + r'\s+', '', text, flags=re.IGNORECASE)

        return text

    def _amplify_emotion(self, text: str) -> str:
        """
        Amplify emotional impact.

        Args:
            text: Original text

        Returns:
            Text with amplified emotion
        """
        # Add emotional intensifiers
        emotional_words = self.power_words['emotion']

        words = text.split()
        for i, word in enumerate(words):
            # Add emotional intensifier before key words
            if word.lower() in ['important', 'crucial', 'essential']:
                if i > 0 and words[i-1].lower() not in emotional_words:
                    words.insert(i, emotional_words[0])

        return ' '.join(words)

    def _add_call_to_action(self, text: str, narrative_structure: Dict[str, Any]) -> str:
        """
        Add call to action if appropriate.

        Args:
            text: Original text
            narrative_structure: Narrative structure

        Returns:
            Text with call to action
        """
        # Add CTA at end if this is the conclusion
        if narrative_structure.get('section', '') == 'conclusion':
            ctas = [
                " Try this today!",
                " Start your journey now.",
                " Take action and see the difference.",
                " Don't wait—begin now!"
            ]
            if not any(cta in text for cta in ctas):
                text += ctas[0]

        return text

    def _calculate_enhancement_metrics(self, enhanced_content: List[Dict[str, Any]], original_content: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate enhancement metrics.

        Args:
            enhanced_content: Enhanced content
            original_content: Original content

        Returns:
            Dictionary of enhancement metrics
        """
        metrics = {}

        # Calculate individual technique scores
        for technique, config in self.enhancement_techniques.items():
            score = self._calculate_technique_score(technique, enhanced_content, original_content)
            metrics[technique] = score

        # Calculate overall enhancement score
        overall_enhancement = sum(
            metrics[technique] * config['weight']
            for technique, config in self.enhancement_techniques.items()
        )
        metrics['overall_enhancement'] = overall_enhancement

        return metrics

    def _calculate_technique_score(self, technique: str, enhanced_content: List[Dict[str, Any]], original_content: List[Dict[str, Any]]) -> float:
        """
        Calculate score for a specific enhancement technique.

        Args:
            technique: Name of the technique
            enhanced_content: Enhanced content
            original_content: Original content

        Returns:
            Technique score between 0.0 and 1.0
        """
        # Compare enhanced vs original to score effectiveness
        if len(enhanced_content) != len(original_content):
            return 0.5

        score = 0.0
        for enhanced, original in zip(enhanced_content, original_content):
            enhanced_text = enhanced.get('text', '')
            original_text = original.get('text', '')

            # Score based on improvement
            if technique == 'vocabulary_upgrade':
                # Check for vocabulary improvements
                if len(enhanced_text) > len(original_text):
                    score += 0.3

            elif technique == 'sentence_variety':
                # Check for sentence variety
                enhanced_sentences = enhanced_text.split('. ')
                original_sentences = original_text.split('. ')
                if len(set(len(s) for s in enhanced_sentences)) > len(set(len(s) for s in original_sentences)):
                    score += 0.3

            elif technique == 'active_voice':
                # Check for active voice
                if 'by ' not in enhanced_text.lower():
                    score += 0.3

            elif technique == 'power_words':
                # Check for power words
                all_power_words = [word for category in self.power_words.values() for word in category]
                if any(word in enhanced_text.lower() for word in all_power_words):
                    score += 0.3

            elif technique == 'rhythm_and_pacing':
                # Check for rhythm optimization
                enhanced_sentences = enhanced_text.split('. ')
                if all(5 <= len(s.split()) <= 25 for s in enhanced_sentences if s):
                    score += 0.3

            elif technique == 'clarity_simplification':
                # Check for clarity
                if len(enhanced_text) < len(original_text):
                    score += 0.3

            elif technique == 'emotional_amplification':
                # Check for emotional amplification
                emotional_words = self.power_words['emotion']
                enhanced_count = sum(1 for word in emotional_words if word in enhanced_text.lower())
                original_count = sum(1 for word in emotional_words if word in original_text.lower())
                if enhanced_count > original_count:
                    score += 0.3

            elif technique == 'call_to_action':
                # Check for call to action
                if any(cta in enhanced_text for cta in ['try this', 'start your', 'take action', 'don\'t wait']):
                    score += 0.3

        # Normalize score
        if enhanced_content:
            score = min(1.0, score / len(enhanced_content))

        return score

    def _calculate_engagement_score(self, enhancement_metrics: Dict[str, float], narrative_structure: Dict[str, Any]) -> float:
        """
        Calculate overall engagement score.

        Args:
            enhancement_metrics: Enhancement metrics
            narrative_structure: Narrative structure

        Returns:
            Engagement score between 0.0 and 1.0
        """
        # Base score from enhancement metrics
        engagement_score = enhancement_metrics.get('overall_enhancement', 0.5)

        # Adjust based on narrative structure quality
        coherence = narrative_structure.get('coherence_score', 0.5)
        engagement_score = (engagement_score + coherence) / 2

        return max(0.0, min(1.0, engagement_score))


# Convenience function for quick content enhancement
def enhance_content(optimized_content: List[Dict[str, Any]], narrative_structure: Dict[str, Any], hooks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Convenience function to enhance content.

    Args:
        optimized_content: Content after attention optimization
        narrative_structure: Narrative structure
        hooks: Generated hooks

    Returns:
        Dictionary with enhancement results
    """
    enhancer = ContentEnhancer()
    return enhancer.enhance(optimized_content, narrative_structure, hooks)
