"""
Complete cinematic project JSON exporter.

This module validates a CinematicProject, builds its cinematic
timeline, optionally applies configurable duration validation,
advanced continuity validation, project-wide global constraints,
and reusable prompt-profile resolution, resolves music-video
lip-sync policies when applicable, processes all scenes through
the workflow engine, and exports the complete project as portable
structured JSON.
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
    resolve_prompt_profile,
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
    """
    Build advanced continuity-validation export data.

    Advanced continuity remains opt-in and does not replace
    the toolkit's existing basic continuity workflow.
    """

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
    """
    Build project-wide global constraint resolution data.

    Global constraints remain opt-in and preserve the original
    Scene objects while resolving project-wide and scene-level
    negative constraints into per-scene structured results.
    """

    result = resolve_project_constraints(
        project.scenes,
        constraints,
    )

    return {
        "mode": "project_global_constraints",
        **result.to_dict(),
    }


def _build_prompt_profile(
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
) -> dict[str, Any]:
    """
    Resolve reusable prompt-profile configuration for export.

    This produces structured prompt configuration only.
    It does not render final prompt strings.
    """

    result = resolve_prompt_profile(
        profile,
        base_profile=base_profile,
        enable_overrides=enable_overrides,
        disable_overrides=disable_overrides,
        custom_config_overrides=(
            custom_config_overrides
        ),
        resolved_name=resolved_name,
    )

    return {
        "mode": "resolved_prompt_profile",
        **result.to_dict(),
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
    Reject prompt-profile options that have no source profile.

    This prevents silently ignoring inheritance or override
    configuration when prompt_profile is omitted.
    """

    if prompt_profile is not None:
        return

    has_prompt_options = any(
        [
            base_prompt_profile is not None,
            bool(prompt_enable_overrides),
            bool(prompt_disable_overrides),
            bool(prompt_config_overrides),
            (
                prompt_resolved_name is not None
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
) -> dict[str, Any]:
    """
    Process and convert a complete cinematic project
    into structured serializable data.

    Music-video projects automatically receive resolved
    lip-sync policy data.

    Optional duration_policy:
    - validates cinematic scene duration
    - validates complete music-video timing when applicable

    Optional continuity_profile:
    - performs advanced scene-to-scene continuity validation

    Optional global_constraints:
    - resolves project-wide production constraints
    - merges project and scene negative constraints

    Optional prompt_profile:
    - resolves reusable prompt configuration
    - supports optional base-profile inheritance
    - supports enable and disable overrides
    - supports nested custom configuration overrides
    - does not render final prompt strings

    All optional systems preserve backward compatibility when
    omitted.

    Raises:
        ValueError: If the project or supplied optional
        configuration fails validation.
    """

    errors = project.validate()

    if errors:
        raise ValueError(
            "Project validation failed: "
            + "; ".join(errors)
        )

    if duration_policy is not None:
        policy_errors = (
            duration_policy.validate()
        )

        if policy_errors:
            raise ValueError(
                "Invalid duration policy: "
                + "; ".join(policy_errors)
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

    project_data = project.to_dict()

    timeline_result = build_timeline(
        project.scenes
    )

    workflow_results = process_project(
        project.scenes
    )

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
            len(result.warnings)
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
        "timeline": timeline_result.to_dict(),
        "workflow": {
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
                    bool(result.continuity_issues)
                    for result in workflow_results
                ),
                "scenes_with_negative_warnings": sum(
                    bool(result.negative_warnings)
                    for result in workflow_results
                ),
            },
        },
    }

    if duration_policy is not None:
        export_data[
            "duration_validation"
        ] = _build_duration_validation(
            project,
            duration_policy,
        )

    if continuity_profile is not None:
        export_data[
            "continuity_validation"
        ] = _build_continuity_validation(
            project,
            continuity_profile,
        )

    if global_constraints is not None:
        export_data[
            "global_constraints"
        ] = _build_global_constraints(
            project,
            global_constraints,
        )

    if prompt_profile is not None:
        export_data[
            "prompt_profile"
        ] = _build_prompt_profile(
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
) -> str:
    """
    Convert a complete cinematic project
    into formatted JSON.
    """

    return json.dumps(
        project_to_dict(
            project,
            duration_policy=duration_policy,
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
) -> Path:
    """
    Validate, process, and save a complete
    cinematic project as JSON.

    Optional configuration layers include:

    - DurationPolicy
    - ContinuityProfile
    - GlobalConstraints
    - PromptProfile

    Prompt profiles are resolved as structured configuration only.
    They do not render final platform-specific prompt strings.

    Returns:
        Path to the generated JSON file.
    """

    path = Path(output_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    content = project_to_json(
        project,
        indent=indent,
        duration_policy=duration_policy,
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
    )

    path.write_text(
        content,
        encoding="utf-8",
    )

    return path
