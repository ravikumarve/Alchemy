"""
Web Researcher Module for the Researcher Agent

Performs web research on a user topic and synthesizes the results into
an Archaeologist-compatible data package (same schema), so Trend-Jacker
and Visionary require ZERO changes.

Two search backends:
  1. Tavily API  — real web search (requires TAVILY_API_KEY env var)
  2. Local corpus — deterministic offline fallback (tests / CPU-only demo)

Design philosophy: deterministic rule-based synthesis (no LLM runtime),
consistent with the rest of the ALCHEMY pipeline on CPU-only hardware.

Time Budget: ~30-60s (dominated by web search latency)
"""

import os
import re
import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

try:
    import requests  # type: ignore[import-untyped]
    REQUESTS_AVAILABLE = True
except ImportError:  # pragma: no cover
    REQUESTS_AVAILABLE = False

from src.agents.archaeologist_state import OUTDATED_KEYWORDS, EVERGREEN_KEYWORDS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TAVILY_API_URL = "https://api.tavily.com/search"


# ---------------------------------------------------------------------------
# Query Generation
# ---------------------------------------------------------------------------

QUERY_MODIFIERS = [
    "principles",
    "examples",
    "history",
    "guide",
    "tips",
    "key concepts",
]


def generate_queries(topic: str, max_queries: int = 5) -> List[str]:
    """
    Generate 3-5 search queries from a user topic.

    Args:
        topic: User topic string (e.g., "Stoicism for modern entrepreneurs")
        max_queries: Maximum number of queries to generate

    Returns:
        List of search query strings
    """
    topic = topic.strip().lower()
    if not topic:
        return []

    # Base query is the topic itself
    queries = [topic]

    # Add modified queries
    for modifier in QUERY_MODIFIERS:
        if len(queries) >= max_queries:
            break
        modified = f"{topic} {modifier}"
        if modified not in queries:
            queries.append(modified)

    # Trim to max_queries
    return queries[:max_queries]


# ---------------------------------------------------------------------------
# Search Backends
# ---------------------------------------------------------------------------


class LocalCorpusBackend:
    """
    Deterministic offline search backend.

    Contains a small built-in evergreen corpus used for tests, demos, and
    CPU-only operation when no TAVILY_API_KEY is configured.
    """

    def __init__(self):
        """Initialize the local corpus."""
        self.corpus = self._build_corpus()

    def _build_corpus(self) -> List[Dict[str, Any]]:
        """Build a small deterministic evergreen corpus."""
        return [
            {
                "title": "Timeless Principles of Focus",
                "content": (
                    "The fundamental principle of deep work is that attention is a "
                    "limited resource. The framework of deliberate practice shows that "
                    "focused effort over time compounds into mastery. A key strategy is "
                    "to eliminate distractions before beginning a task. The concept of "
                    "flow describes the state of complete immersion in an activity. "
                    "This methodology has been validated across disciplines."
                ),
                "score": 0.95,
            },
            {
                "title": "How Habits Shape Outcomes",
                "content": (
                    "A core principle of behavior change is that habits form through "
                    "repetition and reward. The definition of a habit is an automatic "
                    "behavior triggered by context. An example is brushing teeth before "
                    "bed. The best practice is to start with a tiny version of the "
                    "behavior and build gradually. This approach is supported by decades "
                    "of research in psychology."
                ),
                "score": 0.92,
            },
            {
                "title": "The Art of Decision Making",
                "content": (
                    "A foundational concept in decision theory is the trade-off between "
                    "exploration and exploitation. The principle of opportunity cost "
                    "states that choosing one option forfeits others. A practical guide "
                    "is to list criteria before evaluating options. The framework of "
                    "first principles thinking breaks problems down to their basics. "
                    "These concepts remain relevant across eras."
                ),
                "score": 0.90,
            },
            {
                "title": "Ancient Wisdom for Modern Life",
                "content": (
                    "Stoic philosophy teaches that we control only our judgments and "
                    "actions. The principle of negative visualization prepares the mind "
                    "for setbacks. Marcus Aurelius wrote about focusing on the present "
                    "moment rather than worrying about the future. The definition of "
                    "virtue in this tradition is living in accordance with reason. "
                    "These lessons have endured for two thousand years."
                ),
                "score": 0.93,
            },
            {
                "title": "Effective Communication Basics",
                "content": (
                    "The fundamental concept in communication is that clarity beats "
                    "complexity. An effective technique is to structure messages with a "
                    "clear point first. The principle of active listening requires "
                    "genuine attention to the speaker. A common mistake is assuming "
                    "the listener shares your context. These best practices apply to "
                    "written and spoken communication alike."
                ),
                "score": 0.88,
            },
        ]

    def search(self, query: str, max_results: int = 3) -> List[Dict[str, Any]]:
        """
        Search the local corpus using keyword overlap scoring.

        Args:
            query: Search query
            max_results: Maximum results to return

        Returns:
            List of search result dictionaries
        """
        query_terms = set(re.findall(r"[a-z]{4,}", query.lower()))
        scored = []

        for item in self.corpus:
            corpus_terms = set(re.findall(r"[a-z]{4,}", item["content"].lower()))
            overlap: float = float(len(query_terms & corpus_terms))
            # Slight boost for overlapping with title
            title_terms = set(re.findall(r"[a-z]{4,}", item["title"].lower()))
            overlap += 0.5 * len(query_terms & title_terms)
            if overlap > 0:
                scored.append((overlap, item))

        scored.sort(key=lambda x: x[0], reverse=True)

        results = []
        for _, item in scored[:max_results]:
            results.append({
                "title": item["title"],
                "url": "local://corpus",
                "content": item["content"],
                "score": item["score"],
            })

        # If nothing matches, return the first few corpus entries as fallback
        if not results:
            for item in self.corpus[:max_results]:
                results.append({
                    "title": item["title"],
                    "url": "local://corpus",
                    "content": item["content"],
                    "score": item["score"],
                })

        return results


class TavilySearchBackend:
    """
    Real web search backend using the Tavily API.

    Requires TAVILY_API_KEY environment variable.
    """

    def __init__(self, api_key: Optional[str] = None, max_tokens: int = 1500):
        """
        Initialize Tavily backend.

        Args:
            api_key: Tavily API key (defaults to TAVILY_API_KEY env var)
            max_tokens: Max tokens of content per result
        """
        self.api_key = api_key or os.getenv("TAVILY_API_KEY", "")
        self.max_tokens = max_tokens

    @property
    def available(self) -> bool:
        """Whether the backend is usable (API key present + requests installed)."""
        return bool(self.api_key) and REQUESTS_AVAILABLE

    def search(self, query: str, max_results: int = 3) -> List[Dict[str, Any]]:
        """
        Search the web via Tavily API.

        Args:
            query: Search query
            max_results: Maximum results to return

        Returns:
            List of search result dictionaries
        """
        if not self.available:
            raise RuntimeError("Tavily backend unavailable: missing API key or requests")

        payload = {
            "query": query,
            "max_results": max_results,
            "search_depth": "basic",
            "include_answer": False,
            "max_tokens": self.max_tokens,
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}

        response = requests.post(TAVILY_API_URL, json=payload, headers=headers, timeout=20)
        response.raise_for_status()
        data = response.json()

        results = []
        for item in data.get("results", [])[:max_results]:
            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "content": item.get("content", ""),
                "score": float(item.get("score", 0.0)),
            })
        return results


class WebSearchClient:
    """
    Unified web search client with backend selection.

    Uses Tavily when available, otherwise falls back to the local corpus.
    """

    def __init__(self, api_key: Optional[str] = None, force_offline: bool = False):
        """
        Initialize the search client.

        Args:
            api_key: Tavily API key (defaults to env var)
            force_offline: Force the local corpus backend (tests/demos)
        """
        self.tavily = TavilySearchBackend(api_key=api_key)
        self.local = LocalCorpusBackend()
        self.force_offline = force_offline or os.getenv("ALCHEMY_OFFLINE", "").lower() == "1"
        self.backend_used = "local" if (self.force_offline or not self.tavily.available) else "tavily"

    def search(self, query: str, max_results: int = 3) -> List[Dict[str, Any]]:
        """
        Search using the selected backend.

        Args:
            query: Search query
            max_results: Maximum results to return

        Returns:
            List of search result dictionaries
        """
        if self.backend_used == "tavily":
            try:
                results = self.tavily.search(query, max_results)
                if results:
                    return results
                logger.warning("Tavily returned no results, falling back to local corpus")
            except Exception as e:
                logger.warning(f"Tavily search failed ({e}), falling back to local corpus")
        return self.local.search(query, max_results)


# ---------------------------------------------------------------------------
# Content Synthesis (deterministic, rule-based)
# ---------------------------------------------------------------------------

CONTENT_TYPE_PATTERNS = {
    "definition": r"\b(define|definition|means?|refers? to)\b",
    "example": r"\b(example|for instance|such as|like)\b",
    "tutorial": r"\b(how to|step|tutorial|guide|instructions?)\b",
    "theory": r"\b(theory|principle|concept|framework)\b",
    "history": r"\b(history|background|origin|developed)\b",
    "comparison": r"\b(compare|contrast|versus|vs|difference)\b",
}


def classify_content_type(text: str) -> str:
    """
    Classify text into a content type using keyword patterns.

    Args:
        text: Text to classify

    Returns:
        Content type string (default: 'general')
    """
    text_lower = text.lower()
    best_type = "general"
    best_count = 0

    for content_type, pattern in CONTENT_TYPE_PATTERNS.items():
        matches = re.findall(pattern, text_lower)
        if len(matches) > best_count:
            best_count = len(matches)
            best_type = content_type

    return best_type


def score_evergreen(text: str) -> float:
    """
    Score how evergreen a text is (0-1).

    Uses the same outdated/evergreen keyword lists as the Archaeologist
    SemanticChunker for consistency across the pipeline.

    Args:
        text: Text to score

    Returns:
        Evergreen score between 0.0 and 1.0
    """
    if not text:
        return 0.0

    text_lower = text.lower()

    outdated_count = sum(
        1 for kw in OUTDATED_KEYWORDS if kw.lower() in text_lower
    )
    evergreen_count = sum(
        1 for kw in EVERGREEN_KEYWORDS if kw.lower() in text_lower
    )

    # Evergreen keywords boost, outdated keywords penalize
    score = 0.5 + (0.1 * evergreen_count) - (0.15 * outdated_count)
    return max(0.0, min(1.0, score))


def score_confidence(source_score: float, source_count: int) -> float:
    """
    Compute a confidence score from source quality and redundancy.

    Args:
        source_score: Search engine relevance score (0-1)
        source_count: Number of sources supporting the chunk

    Returns:
        Confidence score between 0.0 and 1.0
    """
    return max(0.0, min(1.0, 0.4 * source_score + 0.15 * min(source_count, 4)))


def synthesize_chunks(
    topic: str, results: List[Dict[str, Any]], max_chunks: int = 8
) -> List[Dict[str, Any]]:
    """
    Synthesize search results into content chunks matching the
    Archaeologist chunk schema.

    Args:
        topic: Original user topic
        results: Search result dictionaries
        max_chunks: Maximum chunks to produce

    Returns:
        List of content chunk dictionaries with keys:
        chunk_id, text, content_type, evergreen_score, confidence_score,
        quality_level, length, word_count, metadata
    """
    chunks: List[Dict[str, Any]] = []
    seen_texts = set()

    for idx, result in enumerate(results):
        content = (result.get("content") or "").strip()
        if not content or len(content) < 40:
            continue

        # Deduplicate
        normalized = re.sub(r"\s+", " ", content).lower()[:200]
        if normalized in seen_texts:
            continue
        seen_texts.add(normalized)

        evergreen_score = score_evergreen(content)
        source_score = result.get("score", 0.5)
        confidence_score = score_confidence(source_score, 1)

        # Quality level based on scores
        if evergreen_score >= 0.7 and confidence_score >= 0.5:
            quality_level = "high"
        elif evergreen_score >= 0.4 and confidence_score >= 0.3:
            quality_level = "medium"
        else:
            quality_level = "low"

        chunk = {
            "chunk_id": f"research_{idx + 1}",
            "text": content,
            "content_type": classify_content_type(content),
            "evergreen_score": round(evergreen_score, 3),
            "confidence_score": round(confidence_score, 3),
            "quality_level": quality_level,
            "length": len(content),
            "word_count": len(content.split()),
            "metadata": {
                "source_title": result.get("title", ""),
                "source_url": result.get("url", ""),
                "research_topic": topic,
            },
        }
        chunks.append(chunk)

    return chunks[:max_chunks]


def filter_chunks(chunks: List[Dict[str, Any]], min_quality: str = "medium") -> List[Dict[str, Any]]:
    """
    Filter chunks to keep only acceptable quality.

    Args:
        chunks: List of content chunks
        min_quality: Minimum quality level to keep ('high', 'medium', 'low')

    Returns:
        Filtered list of chunks
    """
    quality_rank = {"high": 3, "medium": 2, "low": 1, "rejected": 0}
    min_rank = quality_rank.get(min_quality, 2)
    return [c for c in chunks if quality_rank.get(c.get("quality_level", "low"), 0) >= min_rank]


# ---------------------------------------------------------------------------
# Package Generation (Archaeologist-compatible schema)
# ---------------------------------------------------------------------------


def build_package(
    topic: str,
    chunks: List[Dict[str, Any]],
    queries: List[str],
    search_time: float,
    job_id: str,
) -> Dict[str, Any]:
    """
    Build an Archaeologist-compatible package for Trend-Jacker handoff.

    Mirrors the DataPackager schema so downstream agents require zero changes.

    Args:
        topic: Original user topic
        chunks: Synthesized content chunks
        queries: Search queries used
        search_time: Total research time in seconds
        job_id: Unique job identifier

    Returns:
        Complete package dictionary
    """
    package_id = f"pkg_{job_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

    if chunks:
        avg_evergreen = sum(c.get("evergreen_score", 0) for c in chunks) / len(chunks)
        avg_confidence = sum(c.get("confidence_score", 0) for c in chunks) / len(chunks)
        quality_distribution = {
            "high": sum(1 for c in chunks if c.get("quality_level") == "high"),
            "medium": sum(1 for c in chunks if c.get("quality_level") == "medium"),
            "low": sum(1 for c in chunks if c.get("quality_level") == "low"),
            "rejected": 0,
        }
    else:
        avg_evergreen = 0.0
        avg_confidence = 0.0
        quality_distribution = {"high": 0, "medium": 0, "low": 0, "rejected": 0}

    if avg_evergreen >= 0.7 and avg_confidence >= 0.5:
        overall_quality = "high"
    elif avg_evergreen >= 0.4 and avg_confidence >= 0.3:
        overall_quality = "medium"
    else:
        overall_quality = "low"

    package = {
        "version": "1.0",
        "source_agent": "researcher",
        "target_agent": "trend_jacker",
        "timestamp": datetime.utcnow().isoformat(),
        "package_id": package_id,
        "metadata": {
            "source_file": f"topic: {topic}",
            "file_type": "web_research",
            "file_size": sum(c.get("length", 0) for c in chunks),
            "extraction_method": "tavily_web_search",
            "processing_time": round(search_time, 3),
            "step_times": {
                "query_generation": 0.0,
                "web_search": round(search_time, 3),
                "content_synthesis": 0.0,
                "quality_filter": 0.0,
                "package_generation": 0.0,
            },
            "retry_count": 0,
            "fallback_triggered": False,
            "search_queries": queries,
        },
        "content": chunks,
        "tables": [],
        "quality": {
            "overall_evergreen_score": round(avg_evergreen, 3),
            "overall_quality": overall_quality,
            "average_evergreen_score": round(avg_evergreen, 3),
            "average_confidence_score": round(avg_confidence, 3),
            "quality_distribution": quality_distribution,
            "total_chunks": len(chunks),
            "outdated_indicators": [],
        },
        "handoff": {
            "processing_complete": True,
            "ready_for_contextualization": True,
            "suggested_hooks": [
                "Timeless principles with modern application",
                "What experts agree on about this topic",
                "Key concepts explained simply",
            ],
            "content_themes": sorted(
                {c.get("content_type", "general") for c in chunks}
            ),
            "processing_notes": [
                "Content researched from web sources on user topic",
                "Evergreen scoring applied for durability",
                "Ready for trend-jacking and contextualization",
            ],
        },
    }
    return package


def research_topic(
    topic: str,
    job_id: str,
    max_queries: int = 5,
    max_results_per_query: int = 3,
    force_offline: bool = False,
) -> Dict[str, Any]:
    """
    Run the full web research pipeline for a topic.

    Args:
        topic: User topic string
        job_id: Unique job identifier
        max_queries: Number of search queries to run
        max_results_per_query: Results per query
        force_offline: Force local corpus backend

    Returns:
        Dictionary with:
        - success: Whether research succeeded
        - package: Archaeologist-compatible package
        - queries: List of queries used
        - backend: Backend used ('tavily' or 'local')
        - processing_time: Total research time
        - errors: List of errors
    """
    start_time = time.time()
    errors: List[str] = []

    try:
        client = WebSearchClient(force_offline=force_offline)
        queries = generate_queries(topic, max_queries)

        if not queries:
            raise ValueError("Topic is empty")

        # Run searches
        all_results: List[Dict[str, Any]] = []
        for query in queries:
            try:
                results = client.search(query, max_results_per_query)
                all_results.extend(results)
            except Exception as e:
                errors.append(f"Search '{query}' failed: {str(e)}")

        # Synthesize and filter
        chunks = synthesize_chunks(topic, all_results)
        chunks = filter_chunks(chunks)

        if not chunks:
            raise ValueError("No usable content found for topic")

        search_time = time.time() - start_time
        package = build_package(topic, chunks, queries, search_time, job_id)

        return {
            "success": True,
            "package": package,
            "queries": queries,
            "backend": client.backend_used,
            "processing_time": search_time,
            "errors": errors,
        }

    except Exception as e:
        search_time = time.time() - start_time
        logger.error(f"Research failed after {search_time:.2f}s: {str(e)}")
        return {
            "success": False,
            "package": None,
            "queries": [],
            "backend": "unknown",
            "processing_time": search_time,
            "errors": errors + [str(e)],
        }
