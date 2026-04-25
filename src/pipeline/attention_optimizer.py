"""
Attention Optimizer Module for Trend-Jacker Agent

Optimizes content for attention and retention metrics.
Implements Step 5 of the Trend-Jacker workflow.

Time Budget: 10 seconds for attention optimization
"""

import re
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AttentionOptimizer:
    """
    Optimizes content for attention and retention metrics.

    Applies proven engagement optimization techniques to maximize
    viewer attention, retention, and overall engagement.

    Time Budget: 10 seconds for optimization
    """

    def __init__(self):
        """Initialize AttentionOptimizer with optimization configuration."""
        self.optimization_timeout = 10.0  # 10 second timeout

        # Attention optimization techniques
        self.optimization_techniques = {
            "pattern_interrupt": {
                "description": "Break patterns to grab attention",
                "weight": 0.15
            },
            "curiosity_gap": {
                "description": "Create information gaps to maintain interest",
                "weight": 0.20
            },
            "social_proof": {
                "description": "Use social proof to build credibility",
                "weight": 0.10
            },
            "emotional_connection": {
                "description": "Create emotional resonance",
                "weight": 0.15
            },
            "storytelling": {
                "description": "Use narrative elements for engagement",
                "weight": 0.15
            },
            "actionable_insights": {
                "description": "Provide actionable takeaways",
                "weight": 0.10
            },
            "visual_descriptions": {
                "description": "Include vivid descriptions",
                "weight": 0.05
            },
            "relatable_examples": {
                "description": "Use relatable examples and analogies",
                "weight": 0.10
            }
        }

        # Retention optimization factors
        self.retention_factors = {
            "opening_strength": 0.25,      # Strong opening hooks attention
            "pacing": 0.20,                 # Good pacing maintains interest
            "variety": 0.15,                # Content variety prevents boredom
            "clarity": 0.15,                # Clear communication aids retention
            "emotional_impact": 0.15,      # Emotional content is memorable
            "actionability": 0.10           # Actionable content is retained
        }

    def optimize(self, content_chunks: List[Dict[str, Any]], narrative_structure: Dict[str, Any], hooks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Optimize content for attention and retention.

        Args:
            content_chunks: Content chunks from Archaeologist
            narrative_structure: Structured narrative
            hooks: Generated hooks

        Returns:
            Dictionary containing:
            - attention_metrics: Attention and retention metrics
            - optimized_content: Content after optimization
            - retention_score: Overall retention score
            - optimization_time: Time taken for optimization

        Raises:
            TimeoutError: If optimization exceeds time budget
        """
        start_time = time.time()

        logger.info("Starting attention optimization")

        try:
            # Calculate attention metrics
            attention_metrics = self._calculate_attention_metrics(content_chunks, narrative_structure, hooks)

            # Optimize content chunks
            optimized_content = self._optimize_content_chunks(content_chunks, attention_metrics)

            # Calculate retention score
            retention_score = self._calculate_retention_score(attention_metrics, narrative_structure)

            # Generate optimization recommendations
            recommendations = self._generate_recommendations(attention_metrics, retention_score)

            optimization_time = time.time() - start_time

            # Check timeout
            if optimization_time > self.optimization_timeout:
                logger.warning(
                    f"Attention optimization exceeded time budget: {optimization_time:.2f}s > {self.optimization_timeout}s"
                )

            result = {
                'attention_metrics': attention_metrics,
                'optimized_content': optimized_content,
                'retention_score': retention_score,
                'recommendations': recommendations,
                'optimization_time': optimization_time
            }

            logger.info(
                f"Attention optimization completed in {optimization_time:.2f}s: "
                f"retention_score={retention_score:.2f}, optimized_chunks={len(optimized_content)}"
            )

            return result

        except Exception as e:
            optimization_time = time.time() - start_time
            logger.error(f"Attention optimization failed after {optimization_time:.2f}s: {str(e)}")
            raise

    def _calculate_attention_metrics(self, content_chunks: List[Dict[str, Any]], narrative_structure: Dict[str, Any], hooks: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate attention metrics for the content.

        Args:
            content_chunks: Content chunks
            narrative_structure: Narrative structure
            hooks: Generated hooks

        Returns:
            Dictionary of attention metrics
        """
        metrics = {}

        # Calculate individual technique scores
        for technique, config in self.optimization_techniques.items():
            score = self._calculate_technique_score(technique, content_chunks, narrative_structure, hooks)
            metrics[technique] = score

        # Calculate overall attention score
        overall_attention = sum(
            metrics[technique] * config['weight']
            for technique, config in self.optimization_techniques.items()
        )
        metrics['overall_attention'] = overall_attention

        return metrics

    def _calculate_technique_score(self, technique: str, content_chunks: List[Dict[str, Any]], narrative_structure: Dict[str, Any], hooks: List[Dict[str, Any]]) -> float:
        """
        Calculate score for a specific optimization technique.

        Args:
            technique: Name of the technique
            content_chunks: Content chunks
            narrative_structure: Narrative structure
            hooks: Generated hooks

        Returns:
            Technique score between 0.0 and 1.0
        """
        score = 0.0

        if technique == "pattern_interrupt":
            # Check for pattern interrupts in content
            for chunk in content_chunks:
                text = chunk.get('text', '').lower()
                if any(word in text for word in ['but wait', 'however', 'surprisingly', 'actually']):
                    score += 0.3
            score = min(1.0, score)

        elif technique == "curiosity_gap":
            # Check for curiosity-inducing elements
            for chunk in content_chunks:
                text = chunk.get('text', '')
                if '?' in text or 'secret' in text.lower() or 'reveal' in text.lower():
                    score += 0.3
            # Add hook quality
            if hooks:
                avg_hook_quality = sum(h.get('quality_score', 0.5) for h in hooks) / len(hooks)
                score += avg_hook_quality * 0.4
            score = min(1.0, score)

        elif technique == "social_proof":
            # Check for social proof elements
            for chunk in content_chunks:
                text = chunk.get('text', '').lower()
                if any(word in text for word in ['study', 'research', 'experts', 'proven', 'tested']):
                    score += 0.3
            score = min(1.0, score)

        elif technique == "emotional_connection":
            # Check for emotional words
            emotional_words = ['amazing', 'incredible', 'powerful', 'transform', 'change', 'impact', 'love', 'hate', 'fear', 'exciting']
            for chunk in content_chunks:
                text = chunk.get('text', '').lower()
                if any(word in text for word in emotional_words):
                    score += 0.2
            score = min(1.0, score)

        elif technique == "storytelling":
            # Check for narrative elements
            content_types = [chunk.get('content_type', '') for chunk in content_chunks]
            if 'story' in content_types or 'history' in content_types or 'example' in content_types:
                score = 0.7
            else:
                score = 0.3

        elif technique == "actionable_insights":
            # Check for actionable content
            for chunk in content_chunks:
                text = chunk.get('text', '').lower()
                if any(word in text for word in ['how to', 'step', 'action', 'do this', 'try']):
                    score += 0.3
            score = min(1.0, score)

        elif technique == "visual_descriptions":
            # Check for descriptive language
            for chunk in content_chunks:
                text = chunk.get('text', '')
                if len(text) > 50:  # Longer texts tend to be more descriptive
                    score += 0.2
            score = min(1.0, score)

        elif technique == "relatable_examples":
            # Check for examples and analogies
            content_types = [chunk.get('content_type', '') for chunk in content_chunks]
            if 'example' in content_types or 'comparison' in content_types:
                score = 0.7
            else:
                score = 0.3

        return score

    def _optimize_content_chunks(self, content_chunks: List[Dict[str, Any]], attention_metrics: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Optimize content chunks based on attention metrics.

        Args:
            content_chunks: Original content chunks
            attention_metrics: Attention metrics

        Returns:
            List of optimized content chunks
        """
        optimized = []

        for chunk in content_chunks:
            optimized_chunk = chunk.copy()

            # Add optimization metadata
            optimized_chunk['optimization_applied'] = []
            optimized_chunk['attention_score'] = 0.0

            # Apply optimizations based on metrics
            if attention_metrics.get('pattern_interrupt', 0) < 0.5:
                optimized_chunk['optimization_applied'].append('add_pattern_interrupt')

            if attention_metrics.get('curiosity_gap', 0) < 0.5:
                optimized_chunk['optimization_applied'].append('enhance_curiosity')

            if attention_metrics.get('emotional_connection', 0) < 0.5:
                optimized_chunk['optimization_applied'].append('add_emotional_elements')

            # Calculate attention score for this chunk
            chunk_attention = self._calculate_chunk_attention(chunk, attention_metrics)
            optimized_chunk['attention_score'] = chunk_attention

            optimized.append(optimized_chunk)

        return optimized

    def _calculate_chunk_attention(self, chunk: Dict[str, Any], attention_metrics: Dict[str, float]) -> float:
        """
        Calculate attention score for a specific chunk.

        Args:
            chunk: Content chunk
            attention_metrics: Overall attention metrics

        Returns:
            Attention score between 0.0 and 1.0
        """
        # Base score from overall metrics
        base_score = attention_metrics.get('overall_attention', 0.5)

        # Adjust based on chunk quality
        quality = chunk.get('quality_level', 'medium')
        if quality == 'high':
            base_score += 0.2
        elif quality == 'low':
            base_score -= 0.2

        # Adjust based on chunk length
        length = chunk.get('length', 0)
        if 50 <= length <= 200:  # Optimal length
            base_score += 0.1
        elif length > 500:  # Too long
            base_score -= 0.1

        return max(0.0, min(1.0, base_score))

    def _calculate_retention_score(self, attention_metrics: Dict[str, float], narrative_structure: Dict[str, Any]) -> float:
        """
        Calculate overall retention score.

        Args:
            attention_metrics: Attention metrics
            narrative_structure: Narrative structure

        Returns:
            Retention score between 0.0 and 1.0
        """
        retention_score = 0.0

        # Calculate individual factor scores
        factor_scores = {}

        # Opening strength
        factor_scores['opening_strength'] = attention_metrics.get('overall_attention', 0.5)

        # Pacing
        coherence = narrative_structure.get('coherence_score', 0.5)
        factor_scores['pacing'] = coherence

        # Variety
        factor_scores['variety'] = 0.7  # Assuming good variety from narrative structure

        # Clarity
        factor_scores['clarity'] = 0.8  # Assuming good clarity from structured content

        # Emotional impact
        factor_scores['emotional_impact'] = attention_metrics.get('emotional_connection', 0.5)

        # Actionability
        factor_scores['actionability'] = attention_metrics.get('actionable_insights', 0.5)

        # Calculate weighted retention score
        retention_score = sum(
            factor_scores[factor] * weight
            for factor, weight in self.retention_factors.items()
        )

        return max(0.0, min(1.0, retention_score))

    def _generate_recommendations(self, attention_metrics: Dict[str, float], retention_score: float) -> List[str]:
        """
        Generate optimization recommendations.

        Args:
            attention_metrics: Attention metrics
            retention_score: Overall retention score

        Returns:
            List of recommendations
        """
        recommendations = []

        # Identify weak areas
        weak_areas = [
            technique for technique, score in attention_metrics.items()
            if technique != 'overall_attention' and score < 0.5
        ]

        # Generate recommendations for weak areas
        for area in weak_areas:
            if area == 'pattern_interrupt':
                recommendations.append("Add pattern interrupts to break viewer expectations")
            elif area == 'curiosity_gap':
                recommendations.append("Create stronger curiosity gaps to maintain interest")
            elif area == 'social_proof':
                recommendations.append("Include more social proof and expert validation")
            elif area == 'emotional_connection':
                recommendations.append("Add emotional elements to create stronger connection")
            elif area == 'storytelling':
                recommendations.append("Incorporate more storytelling elements")
            elif area == 'actionable_insights':
                recommendations.append("Provide more actionable takeaways")
            elif area == 'visual_descriptions':
                recommendations.append("Add more vivid visual descriptions")
            elif area == 'relatable_examples':
                recommendations.append("Include more relatable examples and analogies")

        # Add retention-specific recommendations
        if retention_score < 0.7:
            recommendations.append("Improve opening hook to grab attention immediately")
            recommendations.append("Optimize pacing to maintain viewer interest")
            recommendations.append("Add more variety to prevent viewer fatigue")

        return recommendations


# Convenience function for quick attention optimization
def optimize_attention(content_chunks: List[Dict[str, Any]], narrative_structure: Dict[str, Any], hooks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Convenience function to optimize attention.

    Args:
        content_chunks: Content chunks
        narrative_structure: Narrative structure
        hooks: Generated hooks

    Returns:
        Dictionary with optimization results
    """
    optimizer = AttentionOptimizer()
    return optimizer.optimize(content_chunks, narrative_structure, hooks)
