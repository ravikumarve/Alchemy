"""
Visionary Agent - Media Architect for ALCHEMY Content Transmutation Pipeline

This agent transforms contextualized content from the Trend-Jacker agent
into production-ready media assets with B-roll prompts, visual cues,
storyboards, and Gumroad-ready asset packages.

Workflow Steps:
1. Package Reception (5s) - Receive and validate Trend-Jacker package
2. Storyboard Generation (20s) - Create visual storyboard from narrative
3. B-Roll Prompting (15s) - Generate AI image/video prompts for each scene
4. Visual Cue Mapping (10s) - Map visual cues to exact timestamps
5. Audio Design (10s) - Design audio mood, emphasis, and transitions
6. Asset Packaging (5s) - Bundle into Gumroad-ready ZIP package
7. Output Generation (5s) - Write final assets to processed_gold/

Total Time Budget: 70 seconds (with safety margin)
"""

from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class ProcessingStatus(Enum):
    """Status of Visionary processing workflow"""
    PENDING = "pending"
    RECEIVING = "receiving"
    STORYBOARDING = "storyboarding"
    PROMPTING = "prompting"
    MAPPING_CUES = "mapping_cues"
    DESIGNING_AUDIO = "designing_audio"
    PACKAGING = "packaging"
    GENERATING_OUTPUT = "generating_output"
    COMPLETED = "completed"
    FAILED = "failed"


class VisualStyle(Enum):
    """Visual styles for B-roll generation"""
    CINEMATIC = "cinematic"
    MINIMALIST = "minimalist"
    KINETIC_TYPOGRAPHY = "kinetic_typography"
    STOCK_FOOTAGE = "stock_footage"
    ANIMATED_INFOGRAPHIC = "animated_infographic"
    DOCUMENTARY = "documentary"
    SOCIAL_MEDIA = "social_media"
    CORPORATE = "corporate"


class AudioMood(Enum):
    """Audio moods for background music and sound design"""
    ENERGETIC = "energetic"
    INSPIRING = "inspiring"
    SUSPENSEFUL = "suspenseful"
    CALM = "calm"
    URGENT = "urgent"
    NOSTALGIC = "nostalgic"
    TRIUMPHANT = "triumphant"
    MYSTERIOUS = "mysterious"


class AssetType(Enum):
    """Types of assets the Visionary can produce"""
    YOUTUBE_SHORT = "youtube_short"       # 60-second vertical video
    TIKTOK = "tiktok"                     # TikTok-optimized
    INSTAGRAM_REEL = "instagram_reel"     # Instagram Reel
    GUMROAD_PACK = "gumroad_pack"         # Full Gumroad product
    B_ROLL_LIBRARY = "b_roll_library"     # Collection of B-roll prompts


class VisionaryState(TypedDict):
    """
    Shared state object for Visionary agent workflow.
    All LangGraph nodes share this state for coordination.
    """
    # Input parameters
    input_package: Dict[str, Any]           # Package from Trend-Jacker
    job_id: str                             # Unique job identifier
    timestamp: str                          # Processing start time (ISO format)
    asset_type: str                         # Target asset type (default: youtube_short)

    # Processing state
    status: ProcessingStatus                # Current workflow status
    current_step: str                       # Current step name
    current_step_num: int                   # Current step number (1-7)
    step_start_time: Optional[str]          # Start time of current step

    # Package analysis
    package_analysis: Optional[Dict[str, Any]]  # Analysis of input package
    content_chunks: List[Dict[str, Any]]    # Content chunks from Trend-Jacker
    hooks: List[Dict[str, Any]]             # Hooks from Trend-Jacker
    narrative_structure: Optional[Dict[str, Any]]  # Narrative structure
    engagement_score: float                 # Engagement score from Trend-Jacker
    retention_score: float                  # Retention score from Trend-Jacker
    source_file: str                        # Original source file

    # Storyboard
    storyboard: Optional[Dict[str, Any]]    # Complete storyboard
    scenes: List[Dict[str, Any]]            # Individual scenes
    scene_count: int                        # Number of scenes
    total_duration: float                   # Total video duration in seconds
    pacing_profile: str                     # Pacing profile (fast/medium/slow)

    # B-Roll prompts
    b_roll_prompts: List[Dict[str, Any]]    # AI image/video generation prompts
    prompt_count: int                       # Number of prompts generated
    prompt_style: str                       # Overall prompt style
    visual_style: str                       # Selected visual style

    # Visual cues
    visual_cues: List[Dict[str, Any]]       # Timestamped visual cues
    cue_count: int                          # Number of visual cues
    transition_map: List[Dict[str, Any]]    # Scene transition definitions

    # Audio design
    audio_design: Optional[Dict[str, Any]]  # Complete audio design
    audio_cues: List[Dict[str, Any]]        # Timestamped audio cues
    background_mood: str                    # Overall background mood
    emphasis_markers: List[Dict[str, Any]]  # Audio emphasis points

    # Final output
    output_package: Optional[Dict[str, Any]] # Final Gumroad-ready package
    package_id: Optional[str]               # Package identifier
    output_path: str                        # Path to output file
    processing_time: float                  # Total processing time
    step_times: Dict[str, float]            # Time spent per step

    # Error handling
    retry_count: int                        # Number of retries attempted
    max_retries: int                        # Maximum retry attempts
    error_message: Optional[str]            # Last error message
    error: Optional[Dict[str, Any]]         # Error details
    fallback_triggered: bool                # Whether fallback logic was used


def create_initial_state(input_package: Dict[str, Any], job_id: str,
                         asset_type: str = "youtube_short") -> VisionaryState:
    """
    Create initial state for Visionary workflow.

    Args:
        input_package: Package from Trend-Jacker agent
        job_id: Unique job identifier
        asset_type: Target asset type

    Returns:
        Initialized VisionaryState
    """
    return VisionaryState(
        # Input parameters
        input_package=input_package,
        job_id=job_id,
        timestamp=datetime.utcnow().isoformat(),
        asset_type=asset_type,

        # Processing state
        status=ProcessingStatus.PENDING,
        current_step="",
        current_step_num=0,
        step_start_time=None,

        # Package analysis
        package_analysis=None,
        content_chunks=input_package.get('content_chunks', []),
        hooks=input_package.get('hooks', []),
        narrative_structure=input_package.get('narrative', None),
        engagement_score=input_package.get('engagement_score', 0.0),
        retention_score=input_package.get('retention_score', 0.0),
        source_file=input_package.get('metadata', {}).get('source_file', 'unknown'),

        # Storyboard
        storyboard=None,
        scenes=[],
        scene_count=0,
        total_duration=60.0,  # Default 60-second target
        pacing_profile="medium",

        # B-Roll prompts
        b_roll_prompts=[],
        prompt_count=0,
        prompt_style="cinematic",
        visual_style="cinematic",

        # Visual cues
        visual_cues=[],
        cue_count=0,
        transition_map=[],

        # Audio design
        audio_design=None,
        audio_cues=[],
        background_mood="inspiring",
        emphasis_markers=[],

        # Final output
        output_package=None,
        package_id=None,
        output_path="",
        processing_time=0.0,
        step_times={},

        # Error handling
        retry_count=0,
        max_retries=3,
        error_message=None,
        error=None,
        fallback_triggered=False
    )


def update_step_timing(state: VisionaryState, step_name: str) -> VisionaryState:
    """
    Update timing information for a processing step.

    Args:
        state: Current VisionaryState
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


# B-Roll prompt templates by visual style
B_ROLL_TEMPLATES = {
    VisualStyle.CINEMATIC.value: {
        "prefix": "Cinematic 4K footage, shallow depth of field, golden hour lighting: ",
        "suffix": ", professional color grading, 24fps film look, anamorphic lens",
        "negative": "text, watermark, low quality, blurry, overexposed"
    },
    VisualStyle.MINIMALIST.value: {
        "prefix": "Clean minimalist composition, soft natural light, white space: ",
        "suffix": ", simple geometric shapes, pastel color palette, zen aesthetic",
        "negative": "clutter, busy background, dark shadows, chaos"
    },
    VisualStyle.KINETIC_TYPOGRAPHY.value: {
        "prefix": "Dynamic kinetic typography animation, bold fonts: ",
        "suffix": ", smooth motion graphics, text reveal effects, modern design",
        "negative": "static, boring, serif fonts, low contrast"
    },
    VisualStyle.STOCK_FOOTAGE.value: {
        "prefix": "Professional stock footage style, natural lighting: ",
        "suffix": ", diverse representation, authentic moments, commercial quality",
        "negative": "staged, artificial, low resolution, watermarked"
    },
    VisualStyle.ANIMATED_INFOGRAPHIC.value: {
        "prefix": "Clean animated infographic, flat design: ",
        "suffix": ", smooth transitions, data visualization, modern UI elements",
        "negative": "cluttered, 3D, realistic, photorealistic"
    },
    VisualStyle.DOCUMENTARY.value: {
        "prefix": "Documentary style footage, natural available light: ",
        "suffix": ", handheld camera feel, authentic moments, archival texture",
        "negative": "studio lighting, artificial, staged, commercial"
    },
    VisualStyle.SOCIAL_MEDIA.value: {
        "prefix": "Vertical 9:16 social media content, vibrant colors: ",
        "suffix": ", trending aesthetic, Gen Z style, TikTok/Reels optimized",
        "negative": "horizontal, cinematic, slow paced, corporate"
    },
    VisualStyle.CORPORATE.value: {
        "prefix": "Professional corporate video, clean office environment: ",
        "suffix": ", modern workspace, diverse team, polished presentation",
        "negative": "casual, messy, unprofessional, dark"
    }
}

# Scene transition types
SCENE_TRANSITIONS = [
    "cut",
    "fade_to_black",
    "cross_dissolve",
    "wipe_left",
    "wipe_right",
    "zoom_in",
    "zoom_out",
    "slide_up",
    "slide_down",
    "match_cut"
]

# Audio mood to BPM mapping
AUDIO_MOOD_BPM = {
    AudioMood.ENERGETIC.value: {"bpm": 140, "genre": "electronic_pop", "instruments": ["synth", "drums", "bass"]},
    AudioMood.INSPIRING.value: {"bpm": 120, "genre": "cinematic_orchestral", "instruments": ["strings", "piano", "choir"]},
    AudioMood.SUSPENSEFUL.value: {"bpm": 90, "genre": "ambient_tension", "instruments": ["bass", "drone", "percussion"]},
    AudioMood.CALM.value: {"bpm": 80, "genre": "lo_fi_chill", "instruments": ["guitar", "piano", "soft_beats"]},
    AudioMood.URGENT.value: {"bpm": 160, "genre": "intense_hybrid", "instruments": ["drums", "bass", "synth_brass"]},
    AudioMood.NOSTALGIC.value: {"bpm": 100, "genre": "vintage_vinyl", "instruments": ["piano", "strings", "vinyl_crackle"]},
    AudioMood.TRIUMPHANT.value: {"bpm": 130, "genre": "epic_orchestral", "instruments": ["brass", "strings", "timpani"]},
    AudioMood.MYSTERIOUS.value: {"bpm": 70, "genre": "dark_ambient", "instruments": ["pad", "bell", "texture"]}
}

# Content-to-visual-style mapping
CONTENT_STYLE_MAP = {
    "technology": VisualStyle.KINETIC_TYPOGRAPHY.value,
    "business": VisualStyle.CORPORATE.value,
    "lifestyle": VisualStyle.SOCIAL_MEDIA.value,
    "history": VisualStyle.DOCUMENTARY.value,
    "philosophy": VisualStyle.MINIMALIST.value,
    "strategy": VisualStyle.CINEMATIC.value,
    "education": VisualStyle.ANIMATED_INFOGRAPHIC.value,
    "storytelling": VisualStyle.CINEMATIC.value,
    "default": VisualStyle.STOCK_FOOTAGE.value
}

# Gumroad product structure
GUMROAD_PRODUCT_TEMPLATE = {
    "product_type": "digital_asset_pack",
    "format_version": "1.0",
    "contents": {
        "video_script": None,
        "b_roll_prompts": [],
        "storyboard": None,
        "audio_design": None,
        "thumbnail_prompts": [],
        "description_copy": "",
        "hashtags": [],
        "seo_keywords": []
    }
}