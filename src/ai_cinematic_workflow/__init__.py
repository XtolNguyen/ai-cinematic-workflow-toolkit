"""
AI Cinematic Workflow Toolkit.

Open-source tools for structured cinematic scene planning,
validation, continuity, timeline planning, music-video structure,
lip-sync policy resolution, prompt construction, project management,
workflow processing, and portable export.
"""

from .continuity import (
    ContinuityIssue,
    compare_scenes,
    continuity_report,
    has_continuity_issues,
)
from .lip_sync import (
    LipSyncPolicyResult,
    normalize_lip_sync_mode,
    resolve_lip_sync_policy,
    resolve_music_video_lip_sync,
)
from .music_video import (
    MusicSection,
    MusicVideoStructure,
    normalize_music_token,
)
from .negative_validator import (
    NegativeValidationResult,
    merge_negative_constraints,
    normalize_constraint,
    validate_negative_constraints,
)
from .project import (
    CinematicProject,
    ProjectMetadata,
)
from .prompt_builder import (
    PromptResult,
    build_cinematic_prompt,
)
from .scene import Camera, Scene
from .timeline import (
    TimelineEntry,
    TimelineIssue,
    TimelineResult,
    build_timeline,
    format_timestamp,
)
from .workflow import (
    WorkflowSceneResult,
    process_project,
    process_scene,
)

__all__ = [
    "Camera",
    "Scene",
    "ProjectMetadata",
    "CinematicProject",
    "PromptResult",
    "build_cinematic_prompt",
    "ContinuityIssue",
    "compare_scenes",
    "continuity_report",
    "has_continuity_issues",
    "NegativeValidationResult",
    "normalize_constraint",
    "validate_negative_constraints",
    "merge_negative_constraints",
    "TimelineEntry",
    "TimelineIssue",
    "TimelineResult",
    "build_timeline",
    "format_timestamp",
    "MusicSection",
    "MusicVideoStructure",
    "normalize_music_token",
    "LipSyncPolicyResult",
    "normalize_lip_sync_mode",
    "resolve_lip_sync_policy",
    "resolve_music_video_lip_sync",
    "WorkflowSceneResult",
    "process_scene",
    "process_project",
]

__version__ = "0.1.0"
