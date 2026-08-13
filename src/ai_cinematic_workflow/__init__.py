"""
AI Cinematic Workflow Toolkit.

Open-source tools for structured cinematic scene planning,
basic and advanced continuity validation, project-wide global
constraints, reusable prompt profiles, structured cinematic prompt
assembly, configurable duration policies, timeline planning,
music-video structure and timing validation, lip-sync policy
resolution, prompt construction, project management, workflow
processing, and portable export.
"""

from .continuity import (
    ContinuityIssue,
    compare_scenes,
    continuity_report,
    has_continuity_issues,
)
from .continuity_profiles import (
    AdvancedContinuityIssue,
    AdvancedContinuityValidationResult,
    ContinuityPairValidationResult,
    ContinuityProfile,
    normalize_continuity_field,
    validate_continuity_pair,
    validate_project_continuity,
)
from .duration import (
    DurationIssue,
    DurationPolicy,
    DurationValidationResult,
    validate_scene_duration,
)
from .export_options import (
    OPTIONAL_PROJECT_EXPORT_SECTIONS,
    PROJECT_EXPORT_SECTION_ORDER,
    VALID_PROJECT_EXPORT_SECTIONS,
    OmittedExportSection,
    ProjectExportManifest,
    ProjectExportOptions,
    build_project_export_manifest,
    normalize_export_section,
)
from .global_constraints import (
    GlobalConstraintIssue,
    GlobalConstraintResolution,
    GlobalConstraints,
    ResolvedSceneConstraints,
    resolve_project_constraints,
    resolve_scene_constraints,
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
from .music_video_timing import (
    MusicVideoTimingIssue,
    MusicVideoTimingValidationResult,
    validate_music_video_timing,
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
from .prompt_profiles import (
    VALID_PROMPT_COMPONENTS,
    PromptProfile,
    PromptProfileIssue,
    ResolvedPromptProfile,
    normalize_prompt_component,
    resolve_prompt_profile,
)
from .scene import Camera, Scene
from .structured_prompts import (
    STRUCTURED_PROMPT_SECTION_LABELS,
    STRUCTURED_PROMPT_SECTION_ORDER,
    VALID_STRUCTURED_PROMPT_SECTIONS,
    OmittedPromptComponent,
    StructuredPromptResult,
    StructuredPromptSection,
    assemble_structured_prompt,
    normalize_prompt_section,
)
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
    "ProjectExportOptions",
    "ProjectExportManifest",
    "OmittedExportSection",
    "PROJECT_EXPORT_SECTION_ORDER",
    "VALID_PROJECT_EXPORT_SECTIONS",
    "OPTIONAL_PROJECT_EXPORT_SECTIONS",
    "normalize_export_section",
    "build_project_export_manifest",
    "PromptResult",
    "build_cinematic_prompt",
    "PromptProfile",
    "PromptProfileIssue",
    "ResolvedPromptProfile",
    "VALID_PROMPT_COMPONENTS",
    "normalize_prompt_component",
    "resolve_prompt_profile",
    "StructuredPromptSection",
    "OmittedPromptComponent",
    "StructuredPromptResult",
    "STRUCTURED_PROMPT_SECTION_ORDER",
    "STRUCTURED_PROMPT_SECTION_LABELS",
    "VALID_STRUCTURED_PROMPT_SECTIONS",
    "normalize_prompt_section",
    "assemble_structured_prompt",
    "ContinuityIssue",
    "compare_scenes",
    "continuity_report",
    "has_continuity_issues",
    "ContinuityProfile",
    "AdvancedContinuityIssue",
    "ContinuityPairValidationResult",
    "AdvancedContinuityValidationResult",
    "normalize_continuity_field",
    "validate_continuity_pair",
    "validate_project_continuity",
    "GlobalConstraints",
    "GlobalConstraintIssue",
    "ResolvedSceneConstraints",
    "GlobalConstraintResolution",
    "resolve_scene_constraints",
    "resolve_project_constraints",
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
    "DurationPolicy",
    "DurationIssue",
    "DurationValidationResult",
    "validate_scene_duration",
    "MusicVideoTimingIssue",
    "MusicVideoTimingValidationResult",
    "validate_music_video_timing",
    "WorkflowSceneResult",
    "process_scene",
    "process_project",
]

__version__ = "0.1.0"
