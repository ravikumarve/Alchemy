"""
Trend-Jacker Agent - Contextualizer for ALCHEMY Content Transmutation Pipeline

This agent contextualizes evergreen content from the Archaeologist agent,
transforming it into modern, engaging narratives with attention-grabbing hooks.

Workflow Steps:
1. Package Analysis (5s) - Analyze incoming package from Archaeologist
2. Hook Generation (15s) - Create attention-grabbing hooks
3. Trend Mapping (20s) - Map content to current trends and frameworks
4. Narrative Structuring (25s) - Structure content for engagement
5. Attention Optimization (10s) - Optimize for retention metrics
6. Content Enhancement (5s) - Add modern context and examples
7. Output Generation (5s) - Create structured package for Visionary

Total Time Budget: 90 seconds (with safety margin)
"""

from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class ProcessingStatus(Enum):
    """Status of Trend-Jacker processing workflow"""
    PENDING = "pending"
    ANALYZING = "analyzing"
    GENERATING_HOOKS = "generating_hooks"
    MAPPING_TRENDS = "mapping_trends"
    STRUCTURING_NARRATIVE = "structuring_narrative"
    OPTIMIZING_ATTENTION = "optimizing_attention"
    ENHANCING_CONTENT = "enhancing_content"
    GENERATING_OUTPUT = "generating_output"
    COMPLETED = "completed"
    FAILED = "failed"


class HookType(Enum):
    """Types of content hooks"""
    QUESTION = "question"           # "Did you know that..."
    SURPRISE = "surprise"           # "You won't believe..."
    STORY = "story"                # "The story of how..."
    CONTROVERSY = "controversy"     # "Why everyone is talking about..."
    HOW_TO = "how_to"              # "How to master..."
    MISTAKE = "mistake"            # "The mistake that costs..."
    SECRET = "secret"              # "The secret to..."
    COMPARISON = "comparison"      # "X vs Y: Which is better?"


class EngagementLevel(Enum):
    """Engagement level assessment"""
    VIRAL = "viral"        # High viral potential
    HIGH = "high"         # Strong engagement expected
    MEDIUM = "medium"     # Moderate engagement
    LOW = "low"           # Low engagement potential
    POOR = "poor"         # Poor engagement expected


class TrendJackerState(TypedDict):
    """
    Shared state object for Trend-Jacker agent workflow.
    All LangGraph nodes share this state for coordination.
    """
    # Input parameters
    input_package: Dict[str, Any]           # Package from Archaeologist
    data_pack: Dict[str, Any]               # Alias for input_package (for compatibility)
    job_id: str                             # Unique job identifier
    timestamp: str                          # Processing start time (ISO format)

    # Processing state
    status: ProcessingStatus                # Current workflow status
    current_step: str                       # Current step name (for compatibility)
    current_step_num: int                   # Current step number (1-7)
    step_start_time: Optional[str]          # Start time of current step

    # Package analysis
    package_analysis: Optional[Dict[str, Any]]  # Analysis of input package
    content_chunks: List[Dict[str, Any]]    # Content chunks from data pack
    source_file: str                        # Source file path
    content_themes: List[str]               # Identified content themes
    evergreen_score: float                  # Overall evergreen score from input

    # Hook generation
    generated_hooks: List[Dict[str, Any]]   # Generated hooks with metadata
    selected_hooks: List[Dict[str, Any]]    # Best hooks selected
    hooks: List[Dict[str, Any]]             # Alias for generated_hooks (for compatibility)
    hook_variations: List[str]              # Different hook variations

    # Trend mapping
    trend_analysis: Optional[Dict[str, Any]]  # Trend analysis results
    mapped_trends: List[Dict[str, Any]]     # Mapped trends and frameworks
    trend_mappings: List[Dict[str, Any]]    # Alias for mapped_trends (for compatibility)
    trend_relevance: Dict[str, float]       # Relevance scores per trend
    modern_contexts: List[str]               # Modern contexts applied

    # Narrative structure
    narrative_structure: Optional[Dict[str, Any]]  # Structured narrative
    content_flow: List[Dict[str, Any]]      # Content flow and pacing
    engagement_points: List[Dict[str, Any]]   # Key engagement moments

    # Attention optimization
    attention_metrics: Dict[str, float]      # Attention and retention metrics
    optimized_content: List[Dict[str, Any]]   # Content after optimization
    retention_score: float                  # Overall retention score

    # Content enhancement
    enhanced_content: List[Dict[str, Any]]   # Final enhanced content
    enhancement_metrics: Dict[str, float]    # Enhancement metrics
    engagement_score: float                 # Overall engagement score
    modern_examples: List[str]               # Modern examples added
    contextual_notes: List[str]              # Contextual notes added

    # Final output
    output_package: Optional[Dict[str, Any]] # Final package for Visionary
    package: Optional[Dict[str, Any]]       # Alias for output_package (for compatibility)
    package_id: Optional[str]               # Package identifier
    processing_time: float                  # Total processing time
    step_times: Dict[str, float]             # Time spent per step

    # Error handling
    retry_count: int                         # Number of retries attempted
    max_retries: int                         # Maximum retry attempts
    error_message: Optional[str]             # Last error message
    error: Optional[Dict[str, Any]]          # Error details (for compatibility)
    fallback_triggered: bool                 # Whether fallback logic was used


def create_initial_state(input_package: Dict[str, Any], job_id: str) -> TrendJackerState:
    """
    Create initial state for Trend-Jacker workflow.

    Args:
        input_package: Package from Archaeologist agent
        job_id: Unique job identifier

    Returns:
        Initialized TrendJackerState
    """
    return TrendJackerState(
        # Input parameters
        input_package=input_package,
        data_pack=input_package,  # Alias for compatibility
        job_id=job_id,
        timestamp=datetime.utcnow().isoformat(),

        # Processing state
        status=ProcessingStatus.PENDING,
        current_step="",
        current_step_num=0,
        step_start_time=None,

        # Package analysis
        package_analysis=None,
        content_chunks=input_package.get('content_chunks', []),
        source_file=input_package.get('metadata', {}).get('source_file', 'unknown'),
        content_themes=[],
        evergreen_score=0.0,

        # Hook generation
        generated_hooks=[],
        selected_hooks=[],
        hooks=[],  # Alias for compatibility
        hook_variations=[],

        # Trend mapping
        trend_analysis=None,
        mapped_trends=[],
        trend_mappings=[],  # Alias for compatibility
        trend_relevance={},
        modern_contexts=[],

        # Narrative structure
        narrative_structure=None,
        content_flow=[],
        engagement_points=[],

        # Attention optimization
        attention_metrics={},
        optimized_content=[],
        retention_score=0.0,

        # Content enhancement
        enhanced_content=[],
        enhancement_metrics={},
        engagement_score=0.0,
        modern_examples=[],
        contextual_notes=[],

        # Final output
        output_package=None,
        package=None,  # Alias for compatibility
        package_id=None,
        processing_time=0.0,
        step_times={},

        # Error handling
        retry_count=0,
        max_retries=3,
        error_message=None,
        error=None,  # For compatibility
        fallback_triggered=False
    )


def update_step_timing(state: TrendJackerState, step_name: str) -> TrendJackerState:
    """
    Update timing information for a processing step.

    Args:
        state: Current TrendJackerState
        step_name: Name of the step being completed

    Returns:
        Updated state with timing information
    """
    if state['step_start_time']:
        step_start = datetime.fromisoformat(state['step_start_time'])
        step_end = datetime.utcnow()
        step_duration = (step_end - step_start).total_seconds()

        state['step_times'][step_name] = step_duration
        state['processing_time'] += step_duration

    return state


def calculate_engagement_score(
    hooks: List[Dict[str, Any]],
    narrative_structure: Dict[str, Any],
    attention_metrics: Dict[str, float]
) -> float:
    """
    Calculate overall engagement score for the content.

    Args:
        hooks: Generated hooks
        narrative_structure: Structured narrative
        attention_metrics: Attention metrics

    Returns:
        Engagement score between 0.0 (poor) and 1.0 (viral)
    """
    # Hook quality score
    if hooks:
        hook_score = sum(h.get('quality_score', 0.5) for h in hooks) / len(hooks)
    else:
        hook_score = 0.0

    # Narrative structure score
    if narrative_structure:
        structure_score = narrative_structure.get('coherence_score', 0.5)
    else:
        structure_score = 0.0

    # Attention metrics score
    if attention_metrics:
        attention_score = attention_metrics.get('retention_potential', 0.5)
    else:
        attention_score = 0.0

    # Weighted average
    engagement_score = (hook_score * 0.4 + structure_score * 0.3 + attention_score * 0.3)

    return max(0.0, min(1.0, engagement_score))


def assess_engagement_level(engagement_score: float) -> EngagementLevel:
    """
    Assess engagement level based on score.

    Args:
        engagement_score: Overall engagement score (0-1)

    Returns:
        Engagement level rating
    """
    if engagement_score >= 0.9:
        return EngagementLevel.VIRAL
    elif engagement_score >= 0.7:
        return EngagementLevel.HIGH
    elif engagement_score >= 0.5:
        return EngagementLevel.MEDIUM
    elif engagement_score >= 0.3:
        return EngagementLevel.LOW
    else:
        return EngagementLevel.POOR


# Hook patterns and templates
HOOK_PATTERNS = {
    HookType.QUESTION: [
        "Did you know that {topic}?",
        "What if I told you {statement}?",
        "Have you ever wondered why {phenomenon}?",
        "Why does everyone {action}?",
    ],
    HookType.SURPRISE: [
        "You won't believe what happens when {action}",
        "The truth about {topic} will shock you",
        "Nobody talks about this {aspect} of {topic}",
        "This {thing} changed everything",
    ],
    HookType.STORY: [
        "The story of how {subject} {action}",
        "Let me tell you about the time {event}",
        "Here's how {person} {achievement}",
        "The journey from {start} to {end}",
    ],
    HookType.CONTROVERSY: [
        "Why everyone is talking about {topic}",
        "The controversial truth about {subject}",
        "What nobody wants you to know about {topic}",
        "The debate that's dividing {community}",
    ],
    HookType.HOW_TO: [
        "How to master {skill} in {timeframe}",
        "The secret to {achievement}",
        "Step by step guide to {process}",
        "Master {skill} like a pro",
    ],
    HookType.MISTAKE: [
        "The mistake that costs {consequence}",
        "Why you're failing at {activity}",
        "The one thing you're doing wrong",
        "Stop making this {type} mistake",
    ],
    HookType.SECRET: [
        "The secret to {success} nobody tells you",
        "Hidden strategies for {goal}",
        "What experts don't want you to know",
        "The underground method for {result}",
    ],
    HookType.COMPARISON: [
        "{A} vs {B}: Which is better?",
        "Why {A} beats {B} every time",
        "The battle between {A} and {B}",
        "{A} or {B}? The answer might surprise you",
    ],
}

# Modern trends and frameworks
MODERN_TRENDS = {
    "technology": [
        "AI and machine learning",
        "Remote work revolution",
        "Digital transformation",
        "Automation and efficiency",
        "Data-driven decision making",
    ],
    "business": [
        "Side hustle economy",
        "Personal branding",
        "Content creation",
        "Passive income strategies",
        "Entrepreneurship mindset",
    ],
    "lifestyle": [
        "Work-life balance",
        "Minimalism",
        "Productivity hacks",
        "Mindfulness and wellness",
        "Sustainable living",
    ],
    "social": [
        "Social media algorithms",
        "Viral content strategies",
        "Community building",
        "Influencer marketing",
        "Authenticity over perfection",
    ],
}

# Engagement optimization techniques
ENGAGEMENT_TECHNIQUES = [
    "Pattern interrupt",
    "Curiosity gap",
    "Social proof",
    "Scarcity principle",
    "Authority bias",
    "Emotional connection",
    "Storytelling framework",
    "Call to action",
]
