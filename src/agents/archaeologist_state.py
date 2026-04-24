"""
Archaeologist Agent - Data Miner for ALCHEMY Content Transmutation Pipeline

This agent extracts evergreen data from legacy content (PDFs, TXT, HTML) while
ignoring outdated context. Implements 7-step workflow with <60s total time budget.

Workflow Steps:
1. File Validation (5s) - Verify file format and integrity
2. Content Extraction (2s) - Extract raw text using unstructured.io
3. Semantic Analysis (30s) - Identify evergreen vs outdated content
4. Data Structuring (20s) - Organize into chunks and tables
5. Quality Filtering (15s) - Filter low-quality or irrelevant content
6. Metadata Enrichment (5s) - Add source, timestamp, confidence scores
7. Package Generation (3s) - Create JSON package for Trend-Jacker

Total Time Budget: 80 seconds (with safety margin)
"""

from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class ProcessingStatus(Enum):
    """Status of processing workflow"""
    PENDING = "pending"
    VALIDATING = "validating"
    EXTRACTING = "extracting"
    ANALYZING = "analyzing"
    STRUCTURING = "structuring"
    FILTERING = "filtering"
    ENRICHING = "enriching"
    PACKAGING = "packaging"
    COMPLETED = "completed"
    FAILED = "failed"


class ContentType(Enum):
    """Types of content extracted"""
    TEXT = "text"
    TABLE = "table"
    METADATA = "metadata"
    MIXED = "mixed"


class ExtractionQuality(Enum):
    """Quality assessment of extracted content"""
    HIGH = "high"      # Evergreen, high confidence, well-structured
    MEDIUM = "medium"  # Mostly evergreen, moderate confidence
    LOW = "low"        # Outdated, low confidence, poorly structured
    REJECTED = "rejected"  # Should be filtered out


class ArchaeologistState(TypedDict):
    """
    Shared state object for Archaeologist agent workflow.
    All LangGraph nodes share this state for coordination.
    """
    # Input parameters
    file_path: str                    # Path to input file (PDF/TXT/HTML)
    job_id: str                       # Unique job identifier
    timestamp: str                   # Processing start time (ISO format)

    # Processing state
    status: ProcessingStatus          # Current workflow status
    current_step: int                 # Current step number (1-7)
    step_start_time: Optional[str]    # Start time of current step

    # Extracted content
    raw_text: Optional[str]           # Raw text extracted from file
    file_metadata: Optional[Dict[str, Any]]  # File metadata (size, type, etc.)
    extraction_errors: List[str]      # List of extraction errors

    # Semantic analysis results
    content_chunks: List[Dict[str, Any]]  # Semantic chunks with metadata
    extracted_tables: List[Dict[str, Any]]  # Extracted table data
    evergreen_score: float            # Overall evergreen content score (0-1)
    outdated_indicators: List[str]    # Keywords/phrases indicating outdated content

    # Quality assessment
    quality_assessment: ExtractionQuality  # Overall quality rating
    confidence_scores: Dict[str, float]    # Confidence scores per chunk
    filtered_content: List[Dict[str, Any]]  # Content after quality filtering

    # Final output
    output_package: Optional[Dict[str, Any]]  # Final package for Trend-Jacker
    processing_time: float            # Total processing time in seconds
    step_times: Dict[str, float]      # Time spent per step

    # Error handling
    retry_count: int                   # Number of retries attempted
    max_retries: int                   # Maximum retry attempts
    error_message: Optional[str]       # Last error message
    fallback_triggered: bool           # Whether fallback logic was used


def create_initial_state(file_path: str, job_id: str) -> ArchaeologistState:
    """
    Create initial state for Archaeologist workflow.

    Args:
        file_path: Path to input file
        job_id: Unique job identifier

    Returns:
        Initialized ArchaeologistState
    """
    return ArchaeologistState(
        # Input parameters
        file_path=file_path,
        job_id=job_id,
        timestamp=datetime.utcnow().isoformat(),

        # Processing state
        status=ProcessingStatus.PENDING,
        current_step=0,
        step_start_time=None,

        # Extracted content
        raw_text=None,
        file_metadata=None,
        extraction_errors=[],

        # Semantic analysis results
        content_chunks=[],
        extracted_tables=[],
        evergreen_score=0.0,
        outdated_indicators=[],

        # Quality assessment
        quality_assessment=ExtractionQuality.LOW,
        confidence_scores={},
        filtered_content=[],

        # Final output
        output_package=None,
        processing_time=0.0,
        step_times={},

        # Error handling
        retry_count=0,
        max_retries=3,
        error_message=None,
        fallback_triggered=False
    )


def update_step_timing(state: ArchaeologistState, step_name: str) -> ArchaeologistState:
    """
    Update timing information for a processing step.

    Args:
        state: Current ArchaeologistState
        step_name: Name of the step being completed

    Returns:
        Updated state with timing information
    """
    if state.step_start_time:
        step_start = datetime.fromisoformat(state.step_start_time)
        step_end = datetime.utcnow()
        step_duration = (step_end - step_start).total_seconds()

        state["step_times"][step_name] = step_duration
        state["processing_time"] += step_duration

    return state


def calculate_evergreen_score(content: str, outdated_keywords: List[str]) -> float:
    """
    Calculate evergreen score for content based on outdated indicators.

    Args:
        content: Text content to analyze
        outdated_keywords: List of keywords indicating outdated content

    Returns:
        Evergreen score between 0.0 (outdated) and 1.0 (evergreen)
    """
    if not content:
        return 0.0

    content_lower = content.lower()
    outdated_count = 0

    for keyword in outdated_keywords:
        if keyword.lower() in content_lower:
            outdated_count += 1

    # Calculate score: fewer outdated indicators = higher evergreen score
    if len(outdated_keywords) == 0:
        return 1.0

    evergreen_score = 1.0 - (outdated_count / len(outdated_keywords))
    return max(0.0, min(1.0, evergreen_score))


def assess_quality(
    evergreen_score: float,
    confidence_scores: Dict[str, float],
    content_length: int
) -> ExtractionQuality:
    """
    Assess overall quality of extracted content.

    Args:
        evergreen_score: Overall evergreen content score (0-1)
        confidence_scores: Confidence scores per chunk
        content_length: Total length of extracted content

    Returns:
        Quality assessment rating
    """
    # Calculate average confidence
    if confidence_scores:
        avg_confidence = sum(confidence_scores.values()) / len(confidence_scores)
    else:
        avg_confidence = 0.0

    # Quality thresholds
    if evergreen_score >= 0.8 and avg_confidence >= 0.7 and content_length > 100:
        return ExtractionQuality.HIGH
    elif evergreen_score >= 0.5 and avg_confidence >= 0.5 and content_length > 50:
        return ExtractionQuality.MEDIUM
    elif evergreen_score >= 0.3 and avg_confidence >= 0.3:
        return ExtractionQuality.LOW
    else:
        return ExtractionQuality.REJECTED


# Common outdated content indicators
OUTDATED_KEYWORDS = [
    "current year", "this year", "recent", "latest", "upcoming",
    "soon", "next month", "next week", "yesterday", "today",
    "breaking news", "just announced", "brand new", "new release",
    "version 1.0", "beta", "alpha", "experimental", "preliminary",
    "subject to change", "tentative", "proposed", "planned"
]

# Common evergreen content indicators
EVERGREEN_KEYWORDS = [
    "fundamental", "principle", "concept", "theory", "framework",
    "methodology", "approach", "strategy", "best practice", "guideline",
    "standard", "definition", "introduction", "overview", "tutorial",
    "how to", "guide", "reference", "documentation", "manual",
    "history", "background", "context", "foundation", "basics"
]
