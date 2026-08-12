"""
JSON exporter for cinematic workflow data.

This module converts Scene objects and other serializable workflow
data into clean JSON output.
"""

import json
from pathlib import Path
from typing import Any

from ..scene import Scene


def scene_to_json(scene: Scene, indent: int = 2) -> str:
    """
    Convert a Scene object to a formatted JSON string.

    Raises:
        ValueError: If the scene fails validation.
    """

    errors = scene.validate()

    if errors:
        raise ValueError(
            "Scene validation failed: " + "; ".join(errors)
        )

    return json.dumps(
        scene.to_dict(),
        indent=indent,
        ensure_ascii=False,
    )


def save_scene_json(
    scene: Scene,
    output_path: str | Path,
    indent: int = 2,
) -> Path:
    """
    Validate a scene and save it as a JSON file.

    Returns the final output path.
    """

    path = Path(output_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    json_content = scene_to_json(
        scene,
        indent=indent,
    )

    path.write_text(
        json_content,
        encoding="utf-8",
    )

    return path


def export_data(
    data: dict[str, Any],
    indent: int = 2,
) -> str:
    """
    Export generic workflow data as formatted JSON.
    """

    return json.dumps(
        data,
        indent=indent,
        ensure_ascii=False,
    )
