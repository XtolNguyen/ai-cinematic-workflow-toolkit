"""
Complete cinematic project JSON exporter.

This module validates a CinematicProject and supports both the
original backward-compatible project export behavior and the
optional Enhanced Project Export layer.

Enhanced exports may include reusable ProjectExportOptions,
a canonical ProjectExportManifest, configurable project layers,
PromptProfile resolution, GlobalConstraints, Structured Prompt
Sections, duration validation, continuity validation, timeline,
workflow processing, and portable JSON persistence.

Provider-specific WAN, Veo, Kling, or other adapter behavior does
not belong in this module.
"""

import json
from pathlib import Path
from typing import Any

from ..continuity_profiles import (
    ContinuityProfile,
    validate_project_continuity,
)
from ..duration import (
    DurationPolicy,
    validate_scene_duration,
)
from ..export_options import (
    PROJECT_EXPORT_SECTION_ORDER,
    ProjectExportOptions,
    build_project_export_manifest,
)
from ..global_constraints import (
    GlobalConstraints,
    resolve_project_constraints,
)
from ..lip_sync import (
    resolve_music_video_lip_sync,
)
from ..music_video_timing import (
    validate_music_video_timing,
)
from ..project import CinematicProject
from ..prompt_profiles import (
    PromptProfile,
    ResolvedPromptProfile,
    resolve_prompt_profile,
)
from ..structured_prompts import (
    assemble_structured_prompt,
)
from ..timeline import build_timeline
from ..workflow import process_project


def _build_duration_validation(
    project: CinematicProject,
    policy: DurationPolicy,
) -> dict[str, Any]:
    """
    Build duration-validation export data.

    Music-video projects receive complete cross-system timing
    validation. Regular cinematic projects receive scene-duration
    policy validation only.
    """

    if project.music_video_structure is not None:
        timing_result = (
            validate_music_video_timing(
                project.scenes,
                project.music_video_structure,
                policy,
            )
        )

        return {
            "mode": "music_video_timing",
            **timing_result.to_dict(),
        }

    scene_results = [
        validate_scene_duration(
            scene,
            policy,
        )
        for scene in project.scenes
    ]

    issues = [
        issue.to_dict()
        for result in scene_results
        for issue in result.issues
    ]

    return {
        "mode": "scene_duration",
        "summary": {
            "valid": all(
                result.is_valid
                for result in scene_results
            ),
            "scene_count": len(
                scene_results
            ),
            "issue_count": len(
                issues
            ),
        },
        "policy": policy.to_dict(),
        "scene_results": [
            result.to_dict()
            for result in scene_results
        ],
        "issues": issues,
    }


def _build_continuity_validation(
    project: CinematicProject,
    profile: ContinuityProfile,
) -> dict[str, Any]:
    """Build advanced continuity-validation export data."""

    result = validate_project_continuity(
        project.scenes,
        profile,
    )

    return {
        "mode": "advanced_continuity",
        **result.to_dict(),
    }


def _build_global_constraints(
    project: CinematicProject,
    constraints: GlobalConstraints,
) -> dict[str, Any]:
    """Build project-wide global constraint resolution data."""

    result = resolve_project_constraints(
        project.scenes,
        constraints,
    )

    return {
        "mode": "project_global_constraints",
        **result.to_dict(),
    }


def _resolve_prompt_profile_for_export(
    profile: PromptProfile,
    *,
    base_profile: PromptProfile | None = None,
    enable_overrides: list[str] | None = None,
    disable_overrides: list[str] | None = None,
    custom_config_overrides: dict[
        str,
        Any,
    ] | None = None,
    resolved_name: str | None = None,
) -> ResolvedPromptProfile:
    """
    Resolve PromptProfile configuration once for reuse by
    both profile export and structured prompt assembly.
    """

    return resolve_prompt_profile(
        profile,
        base_profile=base_profile,
        enable_overrides=enable_overrides,
        disable_overrides=disable_overrides,
        custom_config_overrides=(
            custom_config_overrides
        ),
        resolved_name=resolved_name,
    )


def _build_prompt_profile(
    resolved_profile: ResolvedPromptProfile,
) -> dict[str, Any]:
    """Build resolved PromptProfile export data."""

    return {
        "mode": "resolved_prompt_profile",
        **resolved_profile.to_dict(),
    }


def _build_structured_prompts(
    project: CinematicProject,
    *,
    resolved_prompt_profile: (
        ResolvedPromptProfile | None
    ) = None,
    global_constraints: (
        GlobalConstraints | None
    ) = None,
    include_empty_sections: bool = False,
) -> dict[str, Any]:
    """
    Build platform-agnostic structured prompt sections
    for every Scene in the project.
    """

    scene_results = [
        assemble_structured_prompt(
            scene,
            prompt_profile=(
                resolved_prompt_profile
            ),
            global_constraints=(
                global_constraints
            ),
            include_empty_sections=(
                include_empty_sections
            ),
        )
        for scene in project.scenes
    ]

    total_sections = sum(
        result.section_count
        for result in scene_results
    )

    valid_scene_count = sum(
        result.is_valid
        for result in scene_results
    )

    omitted_component_count = sum(
        len(
            result.omitted_components
        )
        for result in scene_results
    )

    return {
        "mode": "structured_prompt_sections",
        "summary": {
            "scene_count": len(
                scene_results
            ),
            "valid_scene_count": (
                valid_scene_count
            ),
            "total_section_count": (
                total_sections
            ),
            "omitted_component_count": (
                omitted_component_count
            ),
            "include_empty_sections": (
                include_empty_sections
            ),
            "prompt_profile_name": (
                resolved_prompt_profile.name
                if (
                    resolved_prompt_profile
                    is not None
                )
                else None
            ),
            "global_constraints_applied": (
                global_constraints is not None
            ),
        },
        "scene_results": [
            result.to_dict()
            for result in scene_results
        ],
    }


def _validate_prompt_profile_request(
    prompt_profile: PromptProfile | None,
    *,
    base_prompt_profile: PromptProfile | None,
    prompt_enable_overrides: list[str] | None,
    prompt_disable_overrides: list[str] | None,
    prompt_config_overrides: dict[
        str,
        Any,
    ] | None,
    prompt_resolved_name: str | None,
) -> None:
    """
    Reject PromptProfile options that have no source profile.
    """

    if prompt_profile is not None:
        return

    has_prompt_options = any(
        [
            base_prompt_profile is not None,
            bool(
                prompt_enable_overrides
            ),
            bool(
                prompt_disable_overrides
            ),
            bool(
                prompt_config_overrides
            ),
            (
                prompt_resolved_name
                is not None
                and bool(
                    prompt_resolved_name.strip()
                )
            ),
        ]
    )

    if has_prompt_options:
        raise ValueError(
            "prompt_profile is required when "
            "prompt-profile inheritance or overrides "
            "are supplied"
        )


def _validate_legacy_structured_prompt_request(
    *,
    include_structured_prompts: bool,
    include_empty_prompt_sections: bool,
) -> None:
    """
    Validate legacy Structured Prompt export flags.

    These flags remain supported for backward compatibility.
    """

    if (
        include_empty_prompt_sections
        and not include_structured_prompts
    ):
        raise ValueError(
            "include_structured_prompts must be True "
            "when include_empty_prompt_sections is enabled"
        )


def _validate_enhanced_export_request(
    export_options: ProjectExportOptions,
    *,
    legacy_include_structured_prompts: bool,
    legacy_include_empty_prompt_sections: bool,
) -> None:
    """
    Validate Enhanced Project Export configuration and
    reject contradictory legacy Structured Prompt flags.

    False legacy values are treated as their historical defaults.
    True legacy values may be supplied redundantly when they agree
    with ProjectExportOptions.
    """

    option_errors = export_options.validate()

    if option_errors:
        raise ValueError(
            "Invalid project export options: "
            + "; ".join(
                option_errors
            )
        )

    if (
        legacy_include_structured_prompts
        and not export_options.include_structured_prompts
    ):
        raise ValueError(
            "Conflicting structured prompt export configuration: "
            "include_structured_prompts=True but "
            "ProjectExportOptions disables structured prompts"
        )

    if (
        legacy_include_empty_prompt_sections
        and not export_options.include_empty_prompt_sections
    ):
        raise ValueError(
            "Conflicting empty prompt-section configuration: "
            "include_empty_prompt_sections=True but "
            "ProjectExportOptions disables empty prompt sections"
        )


def _build_enhanced_omission_reasons(
    options: ProjectExportOptions,
    *,
    duration_policy: DurationPolicy | None,
    continuity_profile: ContinuityProfile | None,
    global_constraints: GlobalConstraints | None,
    prompt_profile: PromptProfile | None,
) -> dict[str, str]:
    """
    Build explicit reasons for canonical sections that are
    absent from an Enhanced Project Export.
    """

    reasons: dict[str, str] = {}

    if not options.include_timeline:
        reasons[
            "timeline"
        ] = "disabled_by_export_options"

    if not options.include_workflow:
        reasons[
            "workflow"
        ] = "disabled_by_export_options"

    if not options.include_duration_validation:
        reasons[
            "duration_validation"
        ] = "disabled_by_export_options"
    elif duration_policy is None:
        reasons[
            "duration_validation"
        ] = "missing_duration_policy"

    if not options.include_continuity_validation:
        reasons[
            "continuity_validation"
        ] = "disabled_by_export_options"
    elif continuity_profile is None:
        reasons[
            "continuity_validation"
        ] = "missing_continuity_profile"

    if not options.include_global_constraints:
        reasons[
            "global_constraints"
        ] = "disabled_by_export_options"
    elif global_constraints is None:
        reasons[
            "global_constraints"
        ] = "missing_global_constraints"

    if not options.include_prompt_profile:
        reasons[
            "prompt_profile"
        ] = "disabled_by_export_options"
    elif prompt_profile is None:
        reasons[
            "prompt_profile"
        ] = "missing_prompt_profile"

    if not options.include_structured_prompts:
        reasons[
            "structured_prompts"
        ] = "disabled_by_export_options"

    return reasons


def project_to_dict(
    project: CinematicProject,
    duration_policy: DurationPolicy | None = None,
    continuity_profile: ContinuityProfile | None = None,
    global_constraints: GlobalConstraints | None = None,
    prompt_profile: PromptProfile | None = None,
    base_prompt_profile: PromptProfile | None = None,
    prompt_enable_overrides: list[str] | None = None,
    prompt_disable_overrides: list[str] | None = None,
    prompt_config_overrides: dict[
        str,
        Any,
    ] | None = None,
    prompt_resolved_name: str | None = None,
    include_structured_prompts: bool = False,
    include_empty_prompt_sections: bool = False,
    export_options: ProjectExportOptions | None = None,
) -> dict[str, Any]:
    """
    Process and convert a complete cinematic project into
    structured serializable data.

    Legacy mode
    -----------

    When export_options is omitted, behavior remains compatible
    with the existing exporter:

    - project is included
    - timeline is included
    - workflow is included
    - supplied optional production systems are exported
    - Structured Prompt Sections remain controlled by the
      legacy include_structured_prompts flags

    Enhanced mode
    -------------

    When ProjectExportOptions is supplied:

    - project remains mandatory
    - timeline and workflow become explicitly configurable
    - optional top-level production layers are controlled by
      ProjectExportOptions
    - requested layers without required source data are omitted
      and reported in the ProjectExportManifest
    - Structured Prompt Sections are controlled by
      ProjectExportOptions
    - a canonical manifest is added to the result

    PromptProfile and GlobalConstraints may still be used
    internally by Structured Prompt assembly even when their
    own top-level export sections are disabled.

    Provider-specific rendering is never performed here.
    """

    errors = project.validate()

    if errors:
        raise ValueError(
            "Project validation failed: "
            + "; ".join(
                errors
            )
        )

    if duration_policy is not None:
        policy_errors = (
            duration_policy.validate()
        )

        if policy_errors:
            raise ValueError(
                "Invalid duration policy: "
                + "; ".join(
                    policy_errors
                )
            )

    if continuity_profile is not None:
        continuity_errors = (
            continuity_profile.validate()
        )

        if continuity_errors:
            raise ValueError(
                "Invalid continuity profile: "
                + "; ".join(
                    continuity_errors
                )
            )

    if global_constraints is not None:
        global_constraint_errors = (
            global_constraints.validate()
        )

        if global_constraint_errors:
            raise ValueError(
                "Invalid global constraints: "
                + "; ".join(
                    global_constraint_errors
                )
            )

    _validate_prompt_profile_request(
        prompt_profile,
        base_prompt_profile=(
            base_prompt_profile
        ),
        prompt_enable_overrides=(
            prompt_enable_overrides
        ),
        prompt_disable_overrides=(
            prompt_disable_overrides
        ),
        prompt_config_overrides=(
            prompt_config_overrides
        ),
        prompt_resolved_name=(
            prompt_resolved_name
        ),
    )

    enhanced_mode = (
        export_options is not None
    )

    if enhanced_mode:
        _validate_enhanced_export_request(
            export_options,
            legacy_include_structured_prompts=(
                include_structured_prompts
            ),
            legacy_include_empty_prompt_sections=(
                include_empty_prompt_sections
            ),
        )

        include_timeline_section = (
            export_options.include_timeline
        )

        include_workflow_section = (
            export_options.include_workflow
        )

        include_duration_section = (
            export_options.include_duration_validation
        )

        include_continuity_section = (
            export_options.include_continuity_validation
        )

        include_global_section = (
            export_options.include_global_constraints
        )

        include_prompt_profile_section = (
            export_options.include_prompt_profile
        )

        include_structured_section = (
            export_options.include_structured_prompts
        )

        effective_include_empty_sections = (
            export_options.include_empty_prompt_sections
        )

    else:
        _validate_legacy_structured_prompt_request(
            include_structured_prompts=(
                include_structured_prompts
            ),
            include_empty_prompt_sections=(
                include_empty_prompt_sections
            ),
        )

        include_timeline_section = True
        include_workflow_section = True

        include_duration_section = (
            duration_policy is not None
        )

        include_continuity_section = (
            continuity_profile is not None
        )

        include_global_section = (
            global_constraints is not None
        )

        include_prompt_profile_section = (
            prompt_profile is not None
        )

        include_structured_section = (
            include_structured_prompts
        )

        effective_include_empty_sections = (
            include_empty_prompt_sections
        )

    resolved_prompt_profile: (
        ResolvedPromptProfile | None
    ) = None

    if prompt_profile is not None:
        prompt_errors = (
            prompt_profile.validate()
        )

        if prompt_errors:
            raise ValueError(
                "Invalid prompt profile: "
                + "; ".join(
                    prompt_errors
                )
            )

        if base_prompt_profile is not None:
            base_prompt_errors = (
                base_prompt_profile.validate()
            )

            if base_prompt_errors:
                raise ValueError(
                    "Invalid base prompt profile: "
                    + "; ".join(
                        base_prompt_errors
                    )
                )

        resolved_prompt_profile = (
            _resolve_prompt_profile_for_export(
                prompt_profile,
                base_profile=(
                    base_prompt_profile
                ),
                enable_overrides=(
                    prompt_enable_overrides
                ),
                disable_overrides=(
                    prompt_disable_overrides
                ),
                custom_config_overrides=(
                    prompt_config_overrides
                ),
                resolved_name=(
                    prompt_resolved_name
                ),
            )
        )

    project_data = project.to_dict()

    if project.music_video_structure is not None:
        lip_sync_results = (
            resolve_music_video_lip_sync(
                project.music_video_structure
            )
        )

        required_count = sum(
            result.lip_sync_required
            for result in lip_sync_results
        )

        disabled_count = sum(
            not result.lip_sync_required
            for result in lip_sync_results
        )

        warning_count = sum(
            len(
                result.warnings
            )
            for result in lip_sync_results
        )

        project_data[
            "music_video"
        ][
            "lip_sync_policies"
        ] = {
            "summary": {
                "policy_count": len(
                    lip_sync_results
                ),
                "required_count": (
                    required_count
                ),
                "disabled_count": (
                    disabled_count
                ),
                "warning_count": (
                    warning_count
                ),
            },
            "policies": [
                result.to_dict()
                for result in lip_sync_results
            ],
        }

    export_data: dict[str, Any] = {
        "project": project_data,
    }

    if include_timeline_section:
        timeline_result = build_timeline(
            project.scenes
        )

        export_data[
            "timeline"
        ] = timeline_result.to_dict()

    if include_workflow_section:
        workflow_results = process_project(
            project.scenes
        )

        export_data[
            "workflow"
        ] = {
            "scene_results": [
                result.to_dict()
                for result in workflow_results
            ],
            "summary": {
                "processed_scenes": len(
                    workflow_results
                ),
                "valid_scenes": sum(
                    result.valid
                    for result in workflow_results
                ),
                "scenes_with_continuity_issues": sum(
                    bool(
                        result.continuity_issues
                    )
                    for result in workflow_results
                ),
                "scenes_with_negative_warnings": sum(
                    bool(
                        result.negative_warnings
                    )
                    for result in workflow_results
                ),
            },
        }

    if (
        include_duration_section
        and duration_policy is not None
    ):
        export_data[
            "duration_validation"
        ] = _build_duration_validation(
            project,
            duration_policy,
        )

    if (
        include_continuity_section
        and continuity_profile is not None
    ):
        export_data[
            "continuity_validation"
        ] = _build_continuity_validation(
            project,
            continuity_profile,
        )

    if (
        include_global_section
        and global_constraints is not None
    ):
        export_data[
            "global_constraints"
        ] = _build_global_constraints(
            project,
            global_constraints,
        )

    if (
        include_prompt_profile_section
        and resolved_prompt_profile is not None
    ):
        export_data[
            "prompt_profile"
        ] = _build_prompt_profile(
            resolved_prompt_profile
        )

    if include_structured_section:
        export_data[
            "structured_prompts"
        ] = _build_structured_prompts(
            project,
            resolved_prompt_profile=(
                resolved_prompt_profile
            ),
            global_constraints=(
                global_constraints
            ),
            include_empty_sections=(
                effective_include_empty_sections
            ),
        )

    if enhanced_mode:
        included_sections = [
            section
            for section in PROJECT_EXPORT_SECTION_ORDER
            if section in export_data
        ]

        omission_reasons = (
            _build_enhanced_omission_reasons(
                export_options,
                duration_policy=(
                    duration_policy
                ),
                continuity_profile=(
                    continuity_profile
                ),
                global_constraints=(
                    global_constraints
                ),
                prompt_profile=(
                    prompt_profile
                ),
            )
        )

        manifest = build_project_export_manifest(
            export_options,
            included_sections=(
                included_sections
            ),
            omission_reasons=(
                omission_reasons
            ),
        )

        export_data = {
            "manifest": manifest.to_dict(),
            **export_data,
        }

    return export_data


def project_to_json(
    project: CinematicProject,
    indent: int = 2,
    duration_policy: DurationPolicy | None = None,
    continuity_profile: ContinuityProfile | None = None,
    global_constraints: GlobalConstraints | None = None,
    prompt_profile: PromptProfile | None = None,
    base_prompt_profile: PromptProfile | None = None,
    prompt_enable_overrides: list[str] | None = None,
    prompt_disable_overrides: list[str] | None = None,
    prompt_config_overrides: dict[
        str,
        Any,
    ] | None = None,
    prompt_resolved_name: str | None = None,
    include_structured_prompts: bool = False,
    include_empty_prompt_sections: bool = False,
    export_options: ProjectExportOptions | None = None,
) -> str:
    """Convert a complete cinematic project into JSON."""

    return json.dumps(
        project_to_dict(
            project,
            duration_policy=(
                duration_policy
            ),
            continuity_profile=(
                continuity_profile
            ),
            global_constraints=(
                global_constraints
            ),
            prompt_profile=(
                prompt_profile
            ),
            base_prompt_profile=(
                base_prompt_profile
            ),
            prompt_enable_overrides=(
                prompt_enable_overrides
            ),
            prompt_disable_overrides=(
                prompt_disable_overrides
            ),
            prompt_config_overrides=(
                prompt_config_overrides
            ),
            prompt_resolved_name=(
                prompt_resolved_name
            ),
            include_structured_prompts=(
                include_structured_prompts
            ),
            include_empty_prompt_sections=(
                include_empty_prompt_sections
            ),
            export_options=(
                export_options
            ),
        ),
        indent=indent,
        ensure_ascii=False,
    )


def save_project_json(
    project: CinematicProject,
    output_path: str | Path,
    indent: int = 2,
    duration_policy: DurationPolicy | None = None,
    continuity_profile: ContinuityProfile | None = None,
    global_constraints: GlobalConstraints | None = None,
    prompt_profile: PromptProfile | None = None,
    base_prompt_profile: PromptProfile | None = None,
    prompt_enable_overrides: list[str] | None = None,
    prompt_disable_overrides: list[str] | None = None,
    prompt_config_overrides: dict[
        str,
        Any,
    ] | None = None,
    prompt_resolved_name: str | None = None,
    include_structured_prompts: bool = False,
    include_empty_prompt_sections: bool = False,
    export_options: ProjectExportOptions | None = None,
) -> Path:
    """
    Validate, process, and save a complete cinematic project
    as portable JSON.
    """

    path = Path(
        output_path
    )

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    content = project_to_json(
        project,
        indent=indent,
        duration_policy=(
            duration_policy
        ),
        continuity_profile=(
            continuity_profile
        ),
        global_constraints=(
            global_constraints
        ),
        prompt_profile=(
            prompt_profile
        ),
        base_prompt_profile=(
            base_prompt_profile
        ),
        prompt_enable_overrides=(
            prompt_enable_overrides
        ),
        prompt_disable_overrides=(
            prompt_disable_overrides
        ),
        prompt_config_overrides=(
            prompt_config_overrides
        ),
        prompt_resolved_name=(
            prompt_resolved_name
        ),
        include_structured_prompts=(
            include_structured_prompts
        ),
        include_empty_prompt_sections=(
            include_empty_prompt_sections
        ),
        export_options=(
            export_options
        ),
    )

    path.write_text(
        content,
        encoding="utf-8",
    )

    return path
