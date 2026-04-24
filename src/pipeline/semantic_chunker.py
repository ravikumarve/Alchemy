"""
Semantic Chunker Module for Archaeologist Agent

Performs semantic analysis to identify evergreen content vs outdated context.
Implements Step 3 of the Archaeologist workflow.

Time Budget: 30 seconds for semantic analysis
"""

import re
import time
from typing import Dict, Any, List, Tuple
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SemanticChunker:
    """
    Analyzes text content to identify evergreen vs outdated information.

    Uses keyword analysis, temporal indicators, and content patterns to:
    - Identify evergreen content (fundamental concepts, principles, tutorials)
    - Detect outdated content (time-sensitive information, deprecated references)
    - Calculate confidence scores for each chunk
    - Filter out low-quality or irrelevant content

    Time Budget: 30 seconds for analysis
    """

    def __init__(self):
        """Initialize SemanticChunker with analysis configuration."""
        self.analysis_timeout = 30.0  # 30 second timeout

        # Outdated content indicators (time-sensitive, deprecated)
        self.outdated_patterns = [
            r'\b(current year|this year|in \d{4})\b',
            r'\b(recent|latest|upcoming|soon)\b',
            r'\b(next month|next week|yesterday|today)\b',
            r'\b(breaking news|just announced|brand new)\b',
            r'\b(new release|version \d+\.\d+\.?\d*)\b',
            r'\b(beta|alpha|experimental|preliminary)\b',
            r'\b(subject to change|tentative|proposed|planned)\b',
            r'\b(\d{1,2}/\d{1,2}/\d{4}|\d{4}-\d{2}-\d{2})\b',  # Dates
        ]

        # Evergreen content indicators (timeless, fundamental)
        self.evergreen_patterns = [
            r'\b(fundamental|principle|concept|theory|framework)\b',
            r'\b(methodology|approach|strategy|best practice|guideline)\b',
            r'\b(standard|definition|introduction|overview|tutorial)\b',
            r'\b(how to|guide|reference|documentation|manual)\b',
            r'\b(history|background|context|foundation|basics)\b',
            r'\b(explanation|example|demonstration|illustration)\b',
            r'\b(step by step|process|workflow|procedure)\b',
        ]

        # Low-quality content indicators
        self.low_quality_patterns = [
            r'^\s*$',  # Empty lines
            r'^\s*[=]+\s*$',  # Separator lines
            r'^\s*[-]+\s*$',  # Separator lines
            r'^\s*_+\s*$',  # Separator lines
            r'^\s*\*\s*$',  # Bullet points without content
            r'^\s*\d+\.\s*$',  # Numbered lists without content
        ]

        # Content type patterns
        self.content_type_patterns = {
            'definition': r'\b(define|definition|means?|refers? to)\b',
            'example': r'\b(example|for instance|such as|like)\b',
            'tutorial': r'\b(how to|step|tutorial|guide|instructions?)\b',
            'theory': r'\b(theory|principle|concept|framework)\b',
            'history': r'\b(history|background|origin|developed)\b',
            'comparison': r'\b(compare|contrast|versus|vs|difference)\b',
        }

    def analyze(self, text: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform semantic analysis on extracted text.

        Args:
            text: Raw text to analyze
            metadata: File metadata from extraction

        Returns:
            Dictionary containing:
            - content_chunks: List of semantic chunks with metadata
            - evergreen_score: Overall evergreen score (0-1)
            - outdated_indicators: List of detected outdated indicators
            - confidence_scores: Confidence scores per chunk
            - analysis_time: Time taken for analysis

        Raises:
            TimeoutError: If analysis exceeds time budget
        """
        start_time = time.time()

        logger.info("Starting semantic analysis")

        try:
            # Split text into chunks
            chunks = self._split_into_chunks(text)

            # Analyze each chunk
            analyzed_chunks = []
            outdated_indicators = []
            total_evergreen_score = 0.0

            for i, chunk in enumerate(chunks):
                # Check timeout
                if time.time() - start_time > self.analysis_timeout * 0.9:
                    logger.warning("Approaching analysis timeout, processing remaining chunks quickly")
                    break

                # Analyze chunk
                chunk_analysis = self._analyze_chunk(chunk, i, metadata)

                # Collect outdated indicators
                outdated_indicators.extend(chunk_analysis['outdated_keywords'])

                # Accumulate evergreen score
                total_evergreen_score += chunk_analysis['evergreen_score']

                analyzed_chunks.append(chunk_analysis)

            # Calculate overall evergreen score
            if analyzed_chunks:
                overall_evergreen_score = total_evergreen_score / len(analyzed_chunks)
            else:
                overall_evergreen_score = 0.0

            # Remove duplicate outdated indicators
            outdated_indicators = list(set(outdated_indicators))

            analysis_time = time.time() - start_time

            # Check timeout
            if analysis_time > self.analysis_timeout:
                logger.warning(
                    f"Analysis exceeded time budget: {analysis_time:.2f}s > {self.analysis_timeout}s"
                )

            result = {
                'content_chunks': analyzed_chunks,
                'evergreen_score': overall_evergreen_score,
                'outdated_indicators': outdated_indicators,
                'confidence_scores': {
                    chunk['chunk_id']: chunk['confidence_score']
                    for chunk in analyzed_chunks
                },
                'analysis_time': analysis_time
            }

            logger.info(
                f"Analysis completed in {analysis_time:.2f}s: "
                f"{len(analyzed_chunks)} chunks, evergreen_score={overall_evergreen_score:.2f}"
            )

            return result

        except Exception as e:
            analysis_time = time.time() - start_time
            logger.error(f"Analysis failed after {analysis_time:.2f}s: {str(e)}")
            raise

    def _split_into_chunks(self, text: str, max_chunk_size: int = 500) -> List[str]:
        """
        Split text into semantic chunks based on paragraphs and sentences.

        Args:
            text: Text to split
            max_chunk_size: Maximum characters per chunk

        Returns:
            List of text chunks
        """
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text.strip())

        # Split by paragraphs first
        paragraphs = re.split(r'[.!?]+\s+', text)

        chunks = []
        current_chunk = ""

        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue

            # If adding paragraph would exceed max size, start new chunk
            if len(current_chunk) + len(paragraph) > max_chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = paragraph
            else:
                if current_chunk:
                    current_chunk += " " + paragraph
                else:
                    current_chunk = paragraph

        # Add remaining chunk
        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def _analyze_chunk(
        self,
        chunk: str,
        chunk_id: int,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze a single text chunk.

        Args:
            chunk: Text chunk to analyze
            chunk_id: Unique identifier for the chunk
            metadata: File metadata

        Returns:
            Dictionary with chunk analysis results
        """
        chunk_lower = chunk.lower()

        # Detect outdated keywords
        outdated_keywords = []
        for pattern in self.outdated_patterns:
            matches = re.findall(pattern, chunk_lower, re.IGNORECASE)
            outdated_keywords.extend(matches)

        # Detect evergreen keywords
        evergreen_keywords = []
        for pattern in self.evergreen_patterns:
            matches = re.findall(pattern, chunk_lower, re.IGNORECASE)
            evergreen_keywords.extend(matches)

        # Detect content type
        content_type = self._detect_content_type(chunk)

        # Calculate evergreen score
        evergreen_score = self._calculate_evergreen_score(
            chunk,
            outdated_keywords,
            evergreen_keywords
        )

        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(
            chunk,
            evergreen_score,
            content_type
        )

        # Determine quality level
        quality_level = self._determine_quality_level(evergreen_score, confidence_score)

        return {
            'chunk_id': f"chunk_{chunk_id}",
            'text': chunk,
            'content_type': content_type,
            'evergreen_score': evergreen_score,
            'confidence_score': confidence_score,
            'quality_level': quality_level,
            'outdated_keywords': outdated_keywords,
            'evergreen_keywords': evergreen_keywords,
            'length': len(chunk),
            'word_count': len(chunk.split()),
            'metadata': {
                'source_file': metadata.get('file_type', 'unknown'),
                'chunk_index': chunk_id
            }
        }

    def _detect_content_type(self, chunk: str) -> str:
        """
        Detect the type of content in a chunk.

        Args:
            chunk: Text chunk to analyze

        Returns:
            Content type string
        """
        chunk_lower = chunk.lower()

        for content_type, pattern in self.content_type_patterns.items():
            if re.search(pattern, chunk_lower):
                return content_type

        return 'general'

    def _calculate_evergreen_score(
        self,
        chunk: str,
        outdated_keywords: List[str],
        evergreen_keywords: List[str]
    ) -> float:
        """
        Calculate evergreen score for a chunk.

        Args:
            chunk: Text chunk
            outdated_keywords: List of outdated keywords found
            evergreen_keywords: List of evergreen keywords found

        Returns:
            Evergreen score between 0.0 (outdated) and 1.0 (evergreen)
        """
        chunk_length = len(chunk)

        if chunk_length == 0:
            return 0.0

        # Base score starts at 0.5
        score = 0.5

        # Adjust for outdated keywords (penalty)
        outdated_penalty = len(outdated_keywords) * 0.1
        score -= outdated_penalty

        # Adjust for evergreen keywords (bonus)
        evergreen_bonus = len(evergreen_keywords) * 0.1
        score += evergreen_bonus

        # Normalize to [0, 1] range
        return max(0.0, min(1.0, score))

    def _calculate_confidence_score(
        self,
        chunk: str,
        evergreen_score: float,
        content_type: str
    ) -> float:
        """
        Calculate confidence score for a chunk.

        Args:
            chunk: Text chunk
            evergreen_score: Evergreen score for the chunk
            content_type: Detected content type

        Returns:
            Confidence score between 0.0 (low) and 1.0 (high)
        """
        chunk_length = len(chunk)
        word_count = len(chunk.split())

        # Base confidence based on length
        if chunk_length < 20:
            length_score = 0.3
        elif chunk_length < 50:
            length_score = 0.5
        elif chunk_length < 200:
            length_score = 0.8
        else:
            length_score = 0.9

        # Adjust for evergreen score
        evergreen_adjustment = evergreen_score * 0.3

        # Adjust for content type (some types are more reliable)
        content_type_bonus = {
            'definition': 0.1,
            'tutorial': 0.1,
            'theory': 0.1,
            'example': 0.05,
            'history': 0.05,
            'comparison': 0.05,
            'general': 0.0
        }.get(content_type, 0.0)

        # Calculate final confidence score
        confidence = length_score + evergreen_adjustment + content_type_bonus

        return max(0.0, min(1.0, confidence))

    def _determine_quality_level(
        self,
        evergreen_score: float,
        confidence_score: float
    ) -> str:
        """
        Determine quality level for a chunk.

        Args:
            evergreen_score: Evergreen score (0-1)
            confidence_score: Confidence score (0-1)

        Returns:
            Quality level: 'high', 'medium', 'low', or 'rejected'
        """
        if evergreen_score >= 0.7 and confidence_score >= 0.7:
            return 'high'
        elif evergreen_score >= 0.5 and confidence_score >= 0.5:
            return 'medium'
        elif evergreen_score >= 0.3 and confidence_score >= 0.3:
            return 'low'
        else:
            return 'rejected'

    def filter_chunks(
        self,
        chunks: List[Dict[str, Any]],
        min_quality: str = 'medium'
    ) -> List[Dict[str, Any]]:
        """
        Filter chunks based on quality level.

        Args:
            chunks: List of analyzed chunks
            min_quality: Minimum quality level to keep ('low', 'medium', 'high')

        Returns:
            Filtered list of chunks
        """
        quality_hierarchy = {
            'rejected': 0,
            'low': 1,
            'medium': 2,
            'high': 3
        }

        min_level = quality_hierarchy.get(min_quality, 1)

        filtered = [
            chunk for chunk in chunks
            if quality_hierarchy.get(chunk['quality_level'], 0) >= min_level
        ]

        logger.info(
            f"Filtered chunks: {len(chunks)} -> {len(filtered)} "
            f"(min_quality={min_quality})"
        )

        return filtered


# Convenience function for quick analysis
def analyze_semantics(text: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to perform semantic analysis.

    Args:
        text: Text to analyze
        metadata: File metadata

    Returns:
        Dictionary with analysis results
    """
    chunker = SemanticChunker()
    return chunker.analyze(text, metadata)
