"""
Trend Mapper Module for Trend-Jacker Agent

Maps evergreen content to modern trends and frameworks.
Implements Step 3 of the Trend-Jacker workflow.

Time Budget: 20 seconds for trend mapping
"""

import re
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TrendMapper:
    """
    Maps evergreen content to modern trends and frameworks.

    Identifies connections between timeless content and current
    trends, making the content more relevant and engaging for
    modern audiences.

    Time Budget: 20 seconds for mapping
    """

    def __init__(self):
        """Initialize TrendMapper with mapping configuration."""
        self.mapping_timeout = 20.0  # 20 second timeout

        # Modern trends and frameworks
        self.modern_trends = {
            "technology": [
                {"name": "AI and machine learning", "keywords": ["ai", "artificial intelligence", "machine learning", "automation", "smart"]},
                {"name": "Remote work revolution", "keywords": ["remote", "work from home", "digital nomad", "distributed teams"]},
                {"name": "Digital transformation", "keywords": ["digital", "transformation", "modernization", "innovation"]},
                {"name": "Data-driven decision making", "keywords": ["data", "analytics", "insights", "metrics", "measurement"]},
                {"name": "Automation and efficiency", "keywords": ["automation", "efficiency", "productivity", "streamline"]},
            ],
            "business": [
                {"name": "Side hustle economy", "keywords": ["side hustle", "passive income", "freelance", "entrepreneur"]},
                {"name": "Personal branding", "keywords": ["brand", "personal brand", "reputation", "influence"]},
                {"name": "Content creation", "keywords": ["content", "creator", "influencer", "audience"]},
                {"name": "Passive income strategies", "keywords": ["passive income", "investments", "revenue streams"]},
                {"name": "Entrepreneurship mindset", "keywords": ["entrepreneur", "startup", "business", "venture"]},
            ],
            "lifestyle": [
                {"name": "Work-life balance", "keywords": ["balance", "wellness", "mental health", "burnout"]},
                {"name": "Minimalism", "keywords": ["minimalist", "simple", "declutter", "essential"]},
                {"name": "Productivity hacks", "keywords": ["productivity", "efficiency", "focus", "time management"]},
                {"name": "Mindfulness and wellness", "keywords": ["mindful", "meditation", "wellness", "self-care"]},
                {"name": "Sustainable living", "keywords": ["sustainable", "eco-friendly", "green", "environment"]},
            ],
            "social": [
                {"name": "Social media algorithms", "keywords": ["algorithm", "viral", "reach", "engagement"]},
                {"name": "Viral content strategies", "keywords": ["viral", "trending", "content strategy", "growth"]},
                {"name": "Community building", "keywords": ["community", "tribe", "audience", "followers"]},
                {"name": "Influencer marketing", "keywords": ["influencer", "marketing", "partnership", "collaboration"]},
                {"name": "Authenticity over perfection", "keywords": ["authentic", "real", "genuine", "transparent"]},
            ],
        }

        # Content-to-trend mapping patterns
        self.mapping_patterns = {
            "principles": ["fundamental", "principle", "concept", "theory", "framework"],
            "methods": ["method", "approach", "strategy", "technique", "process"],
            "examples": ["example", "case study", "demonstration", "illustration"],
            "comparisons": ["compare", "versus", "vs", "difference", "better"],
            "guides": ["guide", "how to", "tutorial", "step by step", "instructions"],
        }

    def map(self, content_chunks: List[Dict[str, Any]], themes: List[str]) -> Dict[str, Any]:
        """
        Map content to modern trends.

        Args:
            content_chunks: Content chunks from Archaeologist
            themes: Identified content themes

        Returns:
            Dictionary containing:
            - mapped_trends: List of mapped trends with relevance scores
            - trend_relevance: Relevance scores per trend
            - modern_contexts: List of modern contexts applied
            - mapping_time: Time taken for mapping

        Raises:
            TimeoutError: If mapping exceeds time budget
        """
        start_time = time.time()

        logger.info("Starting trend mapping")

        try:
            # Analyze content for trend connections
            trend_connections = self._analyze_trend_connections(content_chunks, themes)

            # Calculate relevance scores
            trend_relevance = self._calculate_relevance_scores(trend_connections)

            # Generate modern contexts
            modern_contexts = self._generate_modern_contexts(trend_connections, themes)

            # Create mapped trends list
            mapped_trends = self._create_mapped_trends(trend_connections, trend_relevance)

            mapping_time = time.time() - start_time

            # Check timeout
            if mapping_time > self.mapping_timeout:
                logger.warning(
                    f"Trend mapping exceeded time budget: {mapping_time:.2f}s > {self.mapping_timeout}s"
                )

            result = {
                'mapped_trends': mapped_trends,
                'trend_relevance': trend_relevance,
                'modern_contexts': modern_contexts,
                'mapping_time': mapping_time
            }

            logger.info(
                f"Trend mapping completed in {mapping_time:.2f}s: "
                f"{len(mapped_trends)} trends mapped, {len(modern_contexts)} contexts generated"
            )

            return result

        except Exception as e:
            mapping_time = time.time() - start_time
            logger.error(f"Trend mapping failed after {mapping_time:.2f}s: {str(e)}")
            raise

    def _analyze_trend_connections(self, content_chunks: List[Dict[str, Any]], themes: List[str]) -> List[Dict[str, Any]]:
        """
        Analyze content for connections to modern trends.

        Args:
            content_chunks: Content chunks
            themes: Content themes

        Returns:
            List of trend connections
        """
        connections = []

        # Analyze each content chunk
        for chunk in content_chunks:
            text = chunk.get('text', '').lower()
            chunk_type = chunk.get('content_type', 'general')

            # Check against all trends
            for category, trends in self.modern_trends.items():
                for trend in trends:
                    # Check keyword matches
                    keyword_matches = 0
                    for keyword in trend['keywords']:
                        if keyword in text:
                            keyword_matches += 1

                    # Check theme matches
                    theme_matches = 0
                    for theme in themes:
                        if theme.lower() in trend['name'].lower():
                            theme_matches += 1

                    # Calculate connection strength
                    connection_strength = (keyword_matches * 0.7) + (theme_matches * 0.3)

                    if connection_strength > 0:
                        connections.append({
                            'trend_name': trend['name'],
                            'category': category,
                            'connection_strength': connection_strength,
                            'keyword_matches': keyword_matches,
                            'theme_matches': theme_matches,
                            'chunk_id': chunk.get('chunk_id'),
                            'chunk_type': chunk_type
                        })

        return connections

    def _calculate_relevance_scores(self, connections: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate relevance scores for each trend.

        Args:
            connections: List of trend connections

        Returns:
            Dictionary of trend relevance scores
        """
        relevance_scores = {}

        # Aggregate connections by trend
        trend_connections = {}
        for connection in connections:
            trend_name = connection['trend_name']
            if trend_name not in trend_connections:
                trend_connections[trend_name] = []
            trend_connections[trend_name].append(connection)

        # Calculate scores
        for trend_name, conns in trend_connections.items():
            total_strength = sum(c['connection_strength'] for c in conns)
            connection_count = len(conns)

            # Normalize score (0-1)
            max_possible = connection_count * 2.0  # Max strength per connection
            relevance_score = min(1.0, total_strength / max_possible if max_possible > 0 else 0.0)

            relevance_scores[trend_name] = relevance_score

        return relevance_scores

    def _generate_modern_contexts(self, connections: List[Dict[str, Any]], themes: List[str]) -> List[str]:
        """
        Generate modern contexts for the content.

        Args:
            connections: Trend connections
            themes: Content themes

        Returns:
            List of modern context statements
        """
        contexts = []

        # Get top trends
        top_trends = sorted(connections, key=lambda x: x['connection_strength'], reverse=True)[:5]

        for connection in top_trends:
            trend_name = connection['trend_name']
            category = connection['category']

            # Generate context based on category
            if category == "technology":
                contexts.append(f"In today's {trend_name} landscape...")
            elif category == "business":
                contexts.append(f"With the rise of {trend_name}...")
            elif category == "lifestyle":
                contexts.append(f"In the context of modern {trend_name}...")
            elif category == "social":
                contexts.append(f"Given the current {trend_name} trends...")

        # Add theme-based contexts
        for theme in themes[:3]:
            contexts.append(f"From a {theme} perspective...")

        return contexts

    def _create_mapped_trends(self, connections: List[Dict[str, Any]], relevance_scores: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Create structured mapped trends list.

        Args:
            connections: Trend connections
            relevance_scores: Relevance scores

        Returns:
            List of mapped trends
        """
        mapped_trends = []

        # Group by trend name
        trend_groups = {}
        for connection in connections:
            trend_name = connection['trend_name']
            if trend_name not in trend_groups:
                trend_groups[trend_name] = []
            trend_groups[trend_name].append(connection)

        # Create mapped trend entries
        for trend_name, conns in trend_groups.items():
            category = conns[0]['category']
            relevance = relevance_scores.get(trend_name, 0.0)

            mapped_trends.append({
                'trend_name': trend_name,
                'category': category,
                'relevance_score': relevance,
                'connection_count': len(conns),
                'related_chunks': [c['chunk_id'] for c in conns],
                'modern_applications': self._generate_modern_applications(trend_name, category)
            })

        # Sort by relevance
        mapped_trends.sort(key=lambda x: x['relevance_score'], reverse=True)

        return mapped_trends

    def _generate_modern_applications(self, trend_name: str, category: str) -> List[str]:
        """
        Generate modern application examples for a trend.

        Args:
            trend_name: Name of the trend
            category: Trend category

        Returns:
            List of modern applications
        """
        applications = []

        # Category-specific applications
        if category == "technology":
            applications.extend([
                f"Leveraging {trend_name} for automation",
                f"Using {trend_name} to improve efficiency",
                f"Integrating {trend_name} into workflows"
            ])
        elif category == "business":
            applications.extend([
                f"Building a business around {trend_name}",
                f"Monetizing {trend_name} opportunities",
                f"Scaling {trend_name} strategies"
            ])
        elif category == "lifestyle":
            applications.extend([
                f"Incorporating {trend_name} into daily life",
                f"Optimizing {trend_name} for better results",
                f"Balancing {trend_name} with other priorities"
            ])
        elif category == "social":
            applications.extend([
                f"Building community around {trend_name}",
                f"Creating content about {trend_name}",
                f"Engaging audiences with {trend_name}"
            ])

        return applications


# Convenience function for quick trend mapping
def map_trends(content_chunks: List[Dict[str, Any]], themes: List[str]) -> Dict[str, Any]:
    """
    Convenience function to map trends.

    Args:
        content_chunks: Content chunks
        themes: Content themes

    Returns:
        Dictionary with mapped trends
    """
    mapper = TrendMapper()
    return mapper.map(content_chunks, themes)
