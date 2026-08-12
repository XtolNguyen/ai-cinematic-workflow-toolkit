"""
Complete cinematic project JSON exporter.

This module validates a CinematicProject, processes all of its scenes
through the workflow engine, and exports project metadata, raw scene
data, generated prompts, continuity reports, and validation results
into a portable JSON structure.
"""

import json
from pathlib import Path
from typing import Any

from ..project import CinematicProject
from ..workflow import process_project


def project_to_dict(
    project: CinematicProject,
) -> dict[str, Any]:
    """
    Process and convert a complete cinematic project
    into structured serializable data.

    Raises:
        ValueError: If the project fails validation.
    """

    errors = project.validate()

    if errors:
        raise ValueError(
            "Project validation failed: "
            + "; ".join(errors)
        )

    workflow_results = process_project(
        project.scenes
    )

    return {
        "project": project.to_dict(),
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
