"""
Researcher Agent - Web Research & Synthesis for ALCHEMY Content Pipeline

This agent researches a user topic via web search and synthesizes the results
into an Archaeologist-compatible data package. Implements 5-step workflow.

Workflow Steps:
1. Query Generation (1s)  - Generate 3-5 search queries from user topic
2. Web Search (5-15s)      - Run queries via Tavily (or offline corpus)
3. Content Synthesis (5s)  - Extract key concepts into content chunks
4. Quality Filter (3s)     - Remove low-quality or irrelevant chunks
5. Package Generation (2s) - Output package matching ArchaeologistState schema

Total Time Budget: ~30-60 seconds (dominated by web search latency)
"""

from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class ResearchStatus(Enum):
    """Status of research workflow"""
    PENDING = "pending"
    GENERATING_QUERIES = "generating_queries"
    SEARCHING = "searching"
    SYNTHESIZING = "synthesizing"
    FILTERING = "filtering"
    PACKAGING = "packaging"
    COMPLETED = "completed"
    FAILED = "failed"


class ResearcherState(TypedDict):
    """
    Shared state object for Researcher agent workflow.
    All LangGraph nodes share this state for coordination.
    """
    # Input parameters
    topic: str                        # User topic string
    job_id: str                       # Unique job identifier
    timestamp: str                    # Processing start time (ISO format)

    # Processing state
    status: ResearchStatus            # Current workflow status
    current_step: str                 # Current step name
    step_times: Dict[str, float]      # Time spent per step

    # Search results
    search_queries: List[str]         # Generated search queries
    search_results: List[Dict[str, Any]]  # Raw search results
    search_backend: str               # Backend used ('tavily' or 'local')

    # Synthesized content
    content_chunks: List[Dict[str, Any]]  # Synthesized chunks (Archaeologist schema)
    filtered_content: List[Dict[str, Any]]  # Chunks after quality filtering

    # Final output
    output_package: Optional[Dict[str, Any]]  # Package for Trend-Jacker
    processing_time: float            # Total processing time in seconds

    # Error handling
    retry_count: int                  # Number of retries attempted
    max_retries: int                  # Maximum retry attempts
    error_message: Optional[str]      # Last error message
    errors: List[str]                 # All collected errors
    fallback_triggered: bool          # Whether fallback logic was used


def create_initial_state(topic: str, job_id: str) -> ResearcherState:
    """
    Create initial state for Researcher workflow.

    Args:
        topic: User topic to research
        job_id: Unique job identifier

    Returns:
        Initialized ResearcherState
    """
    return ResearcherState(
        # Input parameters
        topic=topic,
        job_id=job_id,
        timestamp=datetime.utcnow().isoformat(),

        # Processing state
        status=ResearchStatus.PENDING,
        current_step="",
        step_times={},

        # Search results
        search_queries=[],
        search_results=[],
        search_backend="local",

        # Synthesized content
        content_chunks=[],
        filtered_content=[],

        # Final output
        output_package=None,
        processing_time=0.0,

        # Error handling
        retry_count=0,
        max_retries=2,
        error_message=None,
        errors=[],
        fallback_triggered=False,
    )
