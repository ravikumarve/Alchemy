"""
Unit Tests for Researcher Agent Components

Tests the core functionality of the Researcher agent including:
- Query generation
- Search backends (local corpus + Tavily client setup)
- Content synthesis
- Quality filtering
- Package generation (Archaeologist-compatible schema)
- End-to-end workflow (offline)
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest

from src.agents.researcher_state import (
    ResearcherState,
    ResearchStatus,
    create_initial_state,
)
from src.agents.researcher import ResearcherAgent
from src.pipeline.web_researcher import (
    generate_queries,
    LocalCorpusBackend,
    TavilySearchBackend,
    WebSearchClient,
    synthesize_chunks,
    filter_chunks,
    build_package,
    score_evergreen,
    classify_content_type,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_topic() -> str:
    return "Stoicism for modern entrepreneurs"


@pytest.fixture
def sample_results() -> list:
    return [
        {
            "title": "Stoic Principles",
            "url": "https://example.com/stoic",
            "content": (
                "The fundamental principle of Stoicism is that we control only our "
                "judgments and actions. The framework of negative visualization "
                "prepares the mind for setbacks. Marcus Aurelius wrote about focusing "
                "on the present moment. These lessons have endured for two thousand years."
            ),
            "score": 0.9,
        },
        {
            "title": "Modern Business Lessons",
            "url": "https://example.com/business",
            "content": (
                "An example of Stoic practice in business is separating what you can "
                "control from what you cannot. The best practice is to prepare for "
                "worst-case scenarios while pursuing ambitious goals. This methodology "
                "remains relevant for modern entrepreneurs."
            ),
            "score": 0.85,
        },
        {
            "title": "Outdated News",
            "url": "https://example.com/news",
            "content": (
                "Breaking news today: the latest release version 2.0 of the new "
                "platform was just announced this year with upcoming features coming "
                "soon next month. Stay tuned for new release details."
            ),
            "score": 0.7,
        },
    ]


# ---------------------------------------------------------------------------
# State Management Tests
# ---------------------------------------------------------------------------

class TestStateManagement:
    """Test ResearcherState creation and initialization."""

    def test_create_initial_state(self):
        """Test initial state creation."""
        state = create_initial_state("test topic", "job-123")

        assert state["topic"] == "test topic"
        assert state["job_id"] == "job-123"
        assert state["status"] == ResearchStatus.PENDING
        assert state["search_queries"] == []
        assert state["search_results"] == []
        assert state["content_chunks"] == []
        assert state["filtered_content"] == []
        assert state["output_package"] is None
        assert state["max_retries"] == 2
        assert state["errors"] == []
        assert state["fallback_triggered"] is False
        assert state["timestamp"]  # ISO timestamp present

    def test_state_is_typed_dict(self):
        """Test that ResearcherState is a TypedDict-compatible dict."""
        state = create_initial_state("x", "y")
        assert isinstance(state, dict)


# ---------------------------------------------------------------------------
# Query Generation Tests
# ---------------------------------------------------------------------------

class TestQueryGeneration:
    """Test search query generation."""

    def test_generates_multiple_queries(self, sample_topic):
        """Test that multiple queries are generated from a topic."""
        queries = generate_queries(sample_topic)
        assert len(queries) >= 3
        assert len(queries) <= 5

    def test_base_query_included(self, sample_topic):
        """Test that the topic itself is the first query."""
        queries = generate_queries(sample_topic)
        assert queries[0] == sample_topic.lower()

    def test_no_duplicates(self, sample_topic):
        """Test that queries are unique."""
        queries = generate_queries(sample_topic, 10)
        assert len(queries) == len(set(queries))

    def test_empty_topic(self):
        """Test empty topic returns empty list."""
        assert generate_queries("") == []

    def test_max_queries_respected(self, sample_topic):
        """Test max_queries limit is respected."""
        queries = generate_queries(sample_topic, max_queries=3)
        assert len(queries) <= 3


# ---------------------------------------------------------------------------
# Search Backend Tests
# ---------------------------------------------------------------------------

class TestSearchBackends:
    """Test search backend implementations."""

    def test_local_corpus_search_returns_results(self):
        """Test local corpus backend returns results."""
        backend = LocalCorpusBackend()
        results = backend.search("stoicism")
        assert len(results) > 0
        assert results[0]["content"]
        assert results[0]["url"] == "local://corpus"

    def test_local_corpus_has_scores(self):
        """Test local corpus entries have relevance scores."""
        backend = LocalCorpusBackend()
        results = backend.search("habits")
        assert all(r["score"] > 0 for r in results)

    def test_local_corpus_never_empty(self):
        """Test local corpus always returns fallback results."""
        backend = LocalCorpusBackend()
        results = backend.search("zzzznonexistentzzzz")
        assert len(results) > 0

    def test_tavily_backend_requires_key(self, monkeypatch):
        """Test Tavily backend is unavailable without API key."""
        monkeypatch.delenv("TAVILY_API_KEY", raising=False)
        backend = TavilySearchBackend(api_key="")
        assert backend.available is False

    def test_tavily_backend_available_with_key(self, monkeypatch):
        """Test Tavily backend is available with API key."""
        monkeypatch.setenv("TAVILY_API_KEY", "test-key")
        backend = TavilySearchBackend()
        assert backend.available is True

    def test_web_search_client_defaults_local(self, monkeypatch):
        """Test client defaults to local backend without API key."""
        monkeypatch.delenv("TAVILY_API_KEY", raising=False)
        monkeypatch.delenv("ALCHEMY_OFFLINE", raising=False)
        client = WebSearchClient()
        assert client.backend_used == "local"

    def test_web_search_client_force_offline(self, monkeypatch):
        """Test force_offline forces local backend."""
        monkeypatch.setenv("TAVILY_API_KEY", "test-key")
        client = WebSearchClient(force_offline=True)
        assert client.backend_used == "local"

    def test_web_search_client_env_offline(self, monkeypatch):
        """Test ALCHEMY_OFFLINE env var forces local backend."""
        monkeypatch.setenv("TAVILY_API_KEY", "test-key")
        monkeypatch.setenv("ALCHEMY_OFFLINE", "1")
        client = WebSearchClient()
        assert client.backend_used == "local"

    def test_client_search_returns_results(self):
        """Test WebSearchClient.search returns results."""
        client = WebSearchClient(force_offline=True)
        results = client.search("stoicism")
        assert len(results) > 0


# ---------------------------------------------------------------------------
# Content Synthesis Tests
# ---------------------------------------------------------------------------

class TestContentSynthesis:
    """Test content synthesis from search results."""

    def test_synthesize_creates_chunks(self, sample_results):
        """Test synthesis produces chunks from results."""
        chunks = synthesize_chunks("stoicism", sample_results)
        assert len(chunks) > 0

    def test_chunk_schema_matches_archaeologist(self, sample_results):
        """Test chunk schema matches Archaeologist DataPackager expectations."""
        chunks = synthesize_chunks("stoicism", sample_results)
        required_keys = {
            "chunk_id", "text", "content_type", "evergreen_score",
            "confidence_score", "quality_level", "length", "word_count", "metadata"
        }
        for chunk in chunks:
            assert required_keys.issubset(chunk.keys())

    def test_outdated_content_filtered_to_low(self, sample_results):
        """Test outdated content is scored low."""
        chunks = synthesize_chunks("stoicism", sample_results)
        outdated_chunk = next(
            (c for c in chunks if "Breaking news" in c.get("text", "")), None
        )
        if outdated_chunk:
            assert outdated_chunk["quality_level"] == "low"

    def test_evergreen_content_scored_high(self, sample_results):
        """Test evergreen content is scored high."""
        chunks = synthesize_chunks("stoicism", sample_results)
        stoic_chunk = next(
            (c for c in chunks if "Marcus Aurelius" in c.get("text", "")), None
        )
        if stoic_chunk:
            assert stoic_chunk["evergreen_score"] >= 0.7

    def test_metadata_has_research_topic(self, sample_results):
        """Test chunk metadata includes research topic."""
        chunks = synthesize_chunks("my topic", sample_results)
        for chunk in chunks:
            assert chunk["metadata"]["research_topic"] == "my topic"

    def test_short_content_skipped(self):
        """Test very short content is skipped."""
        results = [{"title": "x", "url": "u", "content": "too short", "score": 0.9}]
        chunks = synthesize_chunks("t", results)
        assert len(chunks) == 0

    def test_deduplication(self):
        """Test duplicate content is deduplicated."""
        content = "The fundamental principle of focus is a limited resource."
        results = [
            {"title": "a", "url": "u1", "content": content, "score": 0.9},
            {"title": "b", "url": "u2", "content": content, "score": 0.9},
        ]
        chunks = synthesize_chunks("t", results)
        assert len(chunks) == 1

    def test_evergreen_score_range(self):
        """Test evergreen scores stay within 0-1."""
        assert 0.0 <= score_evergreen("evergreen principle") <= 1.0
        assert 0.0 <= score_evergreen("") <= 1.0

    def test_content_type_classification(self):
        """Test content type classification."""
        assert classify_content_type("A definition of X means...") == "definition"
        assert classify_content_type("An example such as...") == "example"
        assert classify_content_type("A general sentence about things.") == "general"


# ---------------------------------------------------------------------------
# Quality Filter Tests
# ---------------------------------------------------------------------------

class TestQualityFilter:
    """Test quality filtering."""

    def test_filter_keeps_high_medium(self, sample_results):
        """Test filter keeps high and medium quality chunks."""
        chunks = synthesize_chunks("stoicism", sample_results)
        filtered = filter_chunks(chunks)
        assert all(c["quality_level"] in ("high", "medium") for c in filtered)

    def test_filter_min_quality(self, sample_results):
        """Test min_quality parameter."""
        chunks = synthesize_chunks("stoicism", sample_results)
        filtered = filter_chunks(chunks, min_quality="high")
        assert all(c["quality_level"] == "high" for c in filtered)

    def test_empty_input(self):
        """Test empty input returns empty list."""
        assert filter_chunks([]) == []


# ---------------------------------------------------------------------------
# Package Generation Tests
# ---------------------------------------------------------------------------

class TestPackageGeneration:
    """Test Archaeologist-compatible package generation."""

    def test_package_schema_matches_archaeologist(self, sample_results):
        """Test package matches DataPackager handoff schema."""
        chunks = synthesize_chunks("stoicism", sample_results)
        package = build_package("stoicism", chunks, ["stoicism"], 2.5, "job-123")

        required_fields = [
            "version", "source_agent", "target_agent", "timestamp",
            "package_id", "metadata", "content", "tables", "quality", "handoff"
        ]
        for field in required_fields:
            assert field in package

        assert package["source_agent"] == "researcher"
        assert package["target_agent"] == "trend_jacker"
        assert package["version"] == "1.0"
        assert isinstance(package["content"], list)
        assert isinstance(package["tables"], list)
        assert isinstance(package["quality"], dict)
        assert isinstance(package["handoff"], dict)

    def test_package_content_has_chunks(self, sample_results):
        """Test package content contains synthesized chunks."""
        chunks = synthesize_chunks("stoicism", sample_results)
        package = build_package("stoicism", chunks, ["stoicism"], 1.0, "job-123")
        assert len(package["content"]) == len(chunks)

    def test_package_metadata(self, sample_results):
        """Test package metadata fields."""
        chunks = synthesize_chunks("stoicism", sample_results)
        package = build_package("stoicism", chunks, ["stoicism"], 2.5, "job-123")
        assert "topic: stoicism" in package["metadata"]["source_file"]
        assert package["metadata"]["file_type"] == "web_research"
        assert "search_queries" in package["metadata"]

    def test_package_quality_section(self, sample_results):
        """Test package quality assessment."""
        chunks = synthesize_chunks("stoicism", sample_results)
        package = build_package("stoicism", chunks, ["stoicism"], 1.0, "job-123")
        assert "overall_evergreen_score" in package["quality"]
        assert "quality_distribution" in package["quality"]
        assert package["quality"]["total_chunks"] == len(chunks)

    def test_package_handoff(self, sample_results):
        """Test package handoff section."""
        chunks = synthesize_chunks("stoicism", sample_results)
        package = build_package("stoicism", chunks, ["stoicism"], 1.0, "job-123")
        assert package["handoff"]["processing_complete"] is True
        assert package["handoff"]["ready_for_contextualization"] is True

    def test_empty_chunks_package(self):
        """Test package generation with no chunks (graceful)."""
        package = build_package("topic", [], [], 1.0, "job-123")
        assert package["content"] == []
        assert package["quality"]["total_chunks"] == 0

    def test_package_json_serializable(self, sample_results):
        """Test package can be serialized to JSON."""
        chunks = synthesize_chunks("stoicism", sample_results)
        package = build_package("stoicism", chunks, ["stoicism"], 1.0, "job-123")
        json.dumps(package)  # Should not raise


# ---------------------------------------------------------------------------
# End-to-End Workflow Tests (offline)
# ---------------------------------------------------------------------------

class TestResearcherAgent:
    """Test the full Researcher agent workflow offline."""

    def test_agent_process_topic(self, sample_topic):
        """Test full agent workflow with offline backend."""
        agent = ResearcherAgent(force_offline=True)
        result = agent.process_topic(sample_topic)

        assert result["success"] is True
        assert result["package"] is not None
        assert len(result["package"]["content"]) > 0
        assert result["processing_time"] > 0

    def test_agent_package_consumable_by_trend_jacker(self, sample_topic):
        """Test package has 'content' key that Trend-Jacker reads."""
        agent = ResearcherAgent(force_offline=True)
        result = agent.process_topic(sample_topic)
        assert "content" in result["package"]

    def test_agent_empty_topic_raises(self):
        """Test empty topic raises ValueError."""
        agent = ResearcherAgent(force_offline=True)
        with pytest.raises(ValueError):
            agent.process_topic("")

    def test_agent_backend_reported(self, sample_topic):
        """Test agent reports backend used."""
        agent = ResearcherAgent(force_offline=True)
        result = agent.process_topic(sample_topic)
        state = result["state"]
        assert state["search_backend"] == "local"

    def test_agent_deterministic_output(self, sample_topic):
        """Test offline output is deterministic."""
        agent = ResearcherAgent(force_offline=True)
        r1 = agent.process_topic(sample_topic)
        r2 = agent.process_topic(sample_topic)
        assert r1["package"]["content"] == r2["package"]["content"]

    def test_agent_all_steps_completed(self, sample_topic):
        """Test workflow reaches COMPLETED status."""
        agent = ResearcherAgent(force_offline=True)
        result = agent.process_topic(sample_topic)
        assert result["state"]["status"] == ResearchStatus.COMPLETED
        assert result["state"]["current_step"] == "generate_package"

    def test_agent_step_times_recorded(self, sample_topic):
        """Test step timing is recorded."""
        agent = ResearcherAgent(force_offline=True)
        result = agent.process_topic(sample_topic)
        step_times = result["state"]["step_times"]
        assert "generate_queries" in step_times
        assert "web_search" in step_times
        assert "synthesize_content" in step_times
        assert "quality_filter" in step_times
        assert "generate_package" in step_times
