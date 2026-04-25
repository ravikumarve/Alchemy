"""
Hook Generator Module for Trend-Jacker Agent

Generates attention-grabbing hooks for content to maximize engagement.
Implements Step 2 of the Trend-Jacker workflow.

Time Budget: 15 seconds for hook generation
"""

import re
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HookGenerator:
    """
    Generates attention-grabbing hooks for content.

    Uses proven hook patterns, psychological triggers, and
    engagement optimization techniques to create hooks that
    capture attention and drive engagement.

    Time Budget: 15 seconds for generation
    """

    def __init__(self):
        """Initialize HookGenerator with generation configuration."""
        self.generation_timeout = 15.0  # 15 second timeout

        # Hook quality indicators
        self.quality_indicators = {
            'curiosity': 0.3,      # Creates curiosity gap
            'surprise': 0.25,      # Element of surprise
            'relevance': 0.2,      # Relevance to audience
            'clarity': 0.15,       # Clear and understandable
            'actionability': 0.1   # Prompts action
        }

        # Hook patterns (from state)
        self.hook_patterns = {
            'question': [
                "Did you know that {topic}?",
                "What if I told you {statement}?",
                "Have you ever wondered why {phenomenon}?",
                "Why does everyone {action}?",
            ],
            'surprise': [
                "You won't believe what happens when {action}",
                "The truth about {topic} will shock you",
                "Nobody talks about this {aspect} of {topic}",
                "This {thing} changed everything",
            ],
            'story': [
                "The story of how {subject} {action}",
                "Let me tell you about the time {event}",
                "Here's how {person} {achievement}",
                "The journey from {start} to {end}",
            ],
            'controversy': [
                "Why everyone is talking about {topic}",
                "The controversial truth about {subject}",
                "What nobody wants you to know about {topic}",
                "The debate that's dividing {community}",
            ],
            'how_to': [
                "How to master {skill} in {timeframe}",
                "The secret to {achievement}",
                "Step by step guide to {process}",
                "Master {skill} like a pro",
            ],
            'mistake': [
                "The mistake that costs {consequence}",
                "Why you're failing at {activity}",
                "The one thing you're doing wrong",
                "Stop making this {type} mistake",
            ],
            'secret': [
                "The secret to {success} nobody tells you",
                "Hidden strategies for {goal}",
                "What experts don't want you to know",
                "The underground method for {result}",
            ],
            'comparison': [
                "{A} vs {B}: Which is better?",
                "Why {A} beats {B} every time",
                "The battle between {A} and {B}",
                "{A} or {B}? The answer might surprise you",
            ],
        }

    def generate(self, content_chunks: List[Dict[str, Any]], themes: List[str]) -> Dict[str, Any]:
        """
        Generate hooks for content.

        Args:
            content_chunks: Content chunks from Archaeologist
            themes: Identified content themes

        Returns:
            Dictionary containing:
            - generated_hooks: List of generated hooks with metadata
            - selected_hooks: Best hooks selected
            - hook_variations: Different hook variations
            - generation_time: Time taken for generation

        Raises:
            TimeoutError: If generation exceeds time budget
        """
        start_time = time.time()

        logger.info("Starting hook generation")

        try:
            # Extract key topics and concepts
            key_topics = self._extract_key_topics(content_chunks, themes)

            # Generate hooks for each pattern type
            all_hooks = []
            for pattern_type, patterns in self.hook_patterns.items():
                hooks = self._generate_hooks_for_pattern(
                    pattern_type,
                    patterns,
                    key_topics,
                    content_chunks
                )
                all_hooks.extend(hooks)

            # Score and rank hooks
            scored_hooks = self._score_hooks(all_hooks)

            # Select best hooks
            selected_hooks = self._select_best_hooks(scored_hooks)

            # Generate variations
            hook_variations = self._generate_variations(selected_hooks)

            generation_time = time.time() - start_time

            # Check timeout
            if generation_time > self.generation_timeout:
                logger.warning(
                    f"Hook generation exceeded time budget: {generation_time:.2f}s > {self.generation_timeout}s"
                )

            result = {
                'hooks': hooks,  # Changed from 'generated_hooks' to 'hooks' for consistency
                'generated_hooks': hooks,  # Keep for backward compatibility
                'selected_hooks': selected_hooks,
                'hook_variations': hook_variations,
                'generation_time': generation_time
            }

            logger.info(
                f"Hook generation completed in {generation_time:.2f}s: "
                f"{len(scored_hooks)} hooks generated, {len(selected_hooks)} selected"
            )

            return result

        except Exception as e:
            generation_time = time.time() - start_time
            logger.error(f"Hook generation failed after {generation_time:.2f}s: {str(e)}")
            raise

    def _extract_key_topics(self, content_chunks: List[Dict[str, Any]], themes: List[str]) -> List[str]:
        """
        Extract key topics and concepts from content.

        Args:
            content_chunks: Content chunks
            themes: Identified themes

        Returns:
            List of key topics
        """
        key_topics = []

        # Extract from themes
        key_topics.extend(themes)

        # Extract from content chunks
        for chunk in content_chunks:
            text = chunk.get('text', '')
            content_type = chunk.get('content_type', 'general')

            # Extract nouns and key terms (simplified)
            words = re.findall(r'\b[A-Z][a-z]+\b|\b[a-z]{4,}\b', text)
            key_topics.extend(words[:5])  # Top 5 words per chunk

        # Remove duplicates and limit
        key_topics = list(set(key_topics))[:20]

        return key_topics

    def _generate_hooks_for_pattern(
        self,
        pattern_type: str,
        patterns: List[str],
        key_topics: List[str],
        content_chunks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate hooks for a specific pattern type.

        Args:
            pattern_type: Type of hook pattern
            patterns: Pattern templates
            key_topics: Key topics to use
            content_chunks: Content chunks for context

        Returns:
            List of generated hooks
        """
        hooks = []

        for pattern in patterns:
            # Fill in pattern with topics
            for i in range(min(3, len(key_topics))):
                topic = key_topics[i]
                hook_text = self._fill_pattern(pattern, topic, content_chunks)

                if hook_text:
                    hooks.append({
                        'hook_type': pattern_type,
                        'text': hook_text,
                        'pattern': pattern,
                        'topic': topic,
                        'quality_score': 0.0,  # Will be scored later
                        'engagement_potential': 0.0  # Will be calculated later
                    })

        return hooks

    def _fill_pattern(self, pattern: str, topic: str, content_chunks: List[Dict[str, Any]]) -> Optional[str]:
        """
        Fill pattern template with topic and context.

        Args:
            pattern: Pattern template
            topic: Topic to fill in
            content_chunks: Content chunks for context

        Returns:
            Filled hook text or None if pattern can't be filled
        """
        try:
            # Simple pattern filling (can be enhanced with NLP)
            placeholders = re.findall(r'\{([^}]+)\}', pattern)

            replacements = {}
            for placeholder in placeholders:
                if placeholder == 'topic':
                    replacements[placeholder] = topic
                elif placeholder == 'statement':
                    replacements[placeholder] = f"{topic} is more important than you think"
                elif placeholder == 'phenomenon':
                    replacements[placeholder] = f"people are interested in {topic}"
                elif placeholder == 'action':
                    replacements[placeholder] = f"cares about {topic}"
                elif placeholder == 'thing':
                    replacements[placeholder] = topic
                elif placeholder == 'aspect':
                    replacements[placeholder] = f"the hidden side of {topic}"
                elif placeholder == 'subject':
                    replacements[placeholder] = topic
                elif placeholder == 'event':
                    replacements[placeholder] = f"the discovery of {topic}"
                elif placeholder == 'person':
                    replacements[placeholder] = "experts"
                elif placeholder == 'achievement':
                    replacements[placeholder] = f"understanding {topic}"
                elif placeholder == 'start':
                    replacements[placeholder] = "ignorance"
                elif placeholder == 'end':
                    replacements[placeholder] = f"mastery of {topic}"
                elif placeholder == 'skill':
                    replacements[placeholder] = topic
                elif placeholder == 'timeframe':
                    replacements[placeholder] = "record time"
                elif placeholder == 'success':
                    replacements[placeholder] = f"success with {topic}"
                elif placeholder == 'process':
                    replacements[placeholder] = f"learning {topic}"
                elif placeholder == 'activity':
                    replacements[placeholder] = f"understanding {topic}"
                elif placeholder == 'type':
                    replacements[placeholder] = "common"
                elif placeholder == 'goal':
                    replacements[placeholder] = f"mastery of {topic}"
                elif placeholder == 'result':
                    replacements[placeholder] = f"excellence in {topic}"
                elif placeholder == 'consequence':
                    replacements[placeholder] = f"opportunities in {topic}"
                elif placeholder == 'community':
                    replacements[placeholder] = "the industry"
                elif placeholder == 'A':
                    replacements[placeholder] = topic
                elif placeholder == 'B':
                    replacements[placeholder] = "traditional methods"
                else:
                    # Default replacement
                    replacements[placeholder] = topic

            # Fill in placeholders
            hook_text = pattern
            for placeholder, value in replacements.items():
                hook_text = hook_text.replace(f'{{{placeholder}}}', value)

            return hook_text

        except Exception as e:
            logger.warning(f"Failed to fill pattern: {str(e)}")
            return None

    def _score_hooks(self, hooks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Score hooks based on quality indicators.

        Args:
            hooks: List of hooks to score

        Returns:
            List of hooks with quality scores
        """
        for hook in hooks:
            quality_score = 0.0

            # Check for curiosity
            if '?' in hook['text'] or 'why' in hook['text'].lower():
                quality_score += self.quality_indicators['curiosity']

            # Check for surprise
            if any(word in hook['text'].lower() for word in ['shock', 'surprise', 'believe', 'truth']):
                quality_score += self.quality_indicators['surprise']

            # Check for relevance (based on topic)
            if hook['topic'] and len(hook['topic']) > 3:
                quality_score += self.quality_indicators['relevance']

            # Check for clarity (reasonable length)
            if 20 <= len(hook['text']) <= 100:
                quality_score += self.quality_indicators['clarity']

            # Check for actionability
            if any(word in hook['text'].lower() for word in ['how', 'master', 'learn', 'get']):
                quality_score += self.quality_indicators['actionability']

            hook['quality_score'] = min(1.0, quality_score)
            hook['engagement_potential'] = quality_score * 1.2  # Slightly optimistic

        # Sort by quality score
        hooks.sort(key=lambda x: x['quality_score'], reverse=True)

        return hooks

    def _select_best_hooks(self, scored_hooks: List[Dict[str, Any]], count: int = 5) -> List[Dict[str, Any]]:
        """
        Select best hooks from scored list.

        Args:
            scored_hooks: List of scored hooks
            count: Number of hooks to select

        Returns:
            List of best hooks
        """
        # Select top hooks with diversity
        selected = []
        used_types = set()

        for hook in scored_hooks:
            if len(selected) >= count:
                break

            # Ensure diversity in hook types
            if hook['hook_type'] not in used_types or len(selected) < 3:
                selected.append(hook)
                used_types.add(hook['hook_type'])

        return selected

    def _generate_variations(self, hooks: List[Dict[str, Any]]) -> List[str]:
        """
        Generate variations of selected hooks.

        Args:
            hooks: Selected hooks

        Returns:
            List of hook variations
        """
        variations = []

        for hook in hooks:
            original = hook['text']

            # Variation 1: Add emphasis
            variations.append(f"⚡ {original}")

            # Variation 2: Add curiosity
            if '?' not in original:
                variations.append(f"{original} - Here's why")

            # Variation 3: Add urgency
            variations.append(f"🔥 {original} right now")

        return variations


# Convenience function for quick hook generation
def generate_hooks(content_chunks: List[Dict[str, Any]], themes: List[str]) -> Dict[str, Any]:
    """
    Convenience function to generate hooks.

    Args:
        content_chunks: Content chunks
        themes: Content themes

    Returns:
        Dictionary with generated hooks
    """
    generator = HookGenerator()
    return generator.generate(content_chunks, themes)
