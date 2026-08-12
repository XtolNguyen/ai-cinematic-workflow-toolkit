"""
Complete cinematic project JSON exporter.

This module validates a CinematicProject, builds its cinematic
timeline, resolves music-video lip-sync policies when applicable,
processes all scenes through the workflow engine, and exports the
complete project as portable structured JSON.
"""

import json
from pathlib import Path
from typing import Any

from ..lip_sync import (
    resolve_music_video_lip_sync,
)
from ..project import CinematicProject
from ..timeline import build_timeline
from ..workflow import process_project


def project_to_dict(
    project: CinematicProject,
) -> dict[str, Any]:
    """
    Process and convert a complete cinematic project
    into structured serializable data.

    Music-video projects automatically receive resolved
    lip-sync policy data.

    Raises:
        ValueError: If the project fails validation.
    """

    errors = project.validate()

    if errors:
        raise ValueError(
            "Project validation failed: "
            + "; ".join(errors)
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

    return {
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


def project_to_json(
    project: CinematicProject,
    indent: int = 2,
) -> str:
    """
    Convert a complete cinematic project
    into formatted JSON.
    """

    return json.dumps(
        project_to_dict(project),
        indent=indent,
        ensure_ascii=False,
    )


def save_project_json(
    project: CinematicProject,
    output_path: str | Path,
    indent: int = 2,
) -> Path:
    """
    Validate, process, and save a complete
    cinematic project as JSON.

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
    )

    path.write_text(
        content,
        encoding="utf-8",
    )

    return path
