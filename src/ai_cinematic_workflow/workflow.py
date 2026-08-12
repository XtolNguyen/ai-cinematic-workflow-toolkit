"""
Core cinematic workflow engine.

This module combines scene validation, continuity checking,
negative-constraint normalization, prompt generation, and
structured workflow output.
"""

from dataclasses import asdict, dataclass
from typing import Any

from .continuity import continuity_report
from .negative_validator import validate_negative_constraints
from .prompt_builder import build_cinematic_prompt
from .scene import Scene


@dataclass
class WorkflowSceneResult:
    """Processed result for a single cinematic scene."""

    scene_id: int
    valid: bool
    validation_errors: list[str]
    prompt: str
    negative_prompt: str
    negative_warnings: list[str]
    continuity_issues: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        """Convert the workflow result to a serializable dictionary."""
        return asdict(self)


def process_scene(
    scene: Scene,
    previous_scene: Scene | None = None,
) -> WorkflowSceneResult:
    """
    Process one scene through the core cinematic workflow.

    Pipeline:
    1. Validate scene data.
    2. Normalize negative constraints.
    3. Compare continuity with the previous scene.
    4. Generate cinematic prompt.
    5. Return structured result.
    """

    validation_errors = scene.validate()

    if validation_errors:
        return WorkflowSceneResult(
            scene_id=scene.scene_id,
            valid=False,
            validation_errors=validation_errors,
            prompt="",
            negative_prompt="",
            negative_warnings=[],
            continuity_issues=[],
        )

    negative_result = validate_negative_constraints(
        scene.negative_constraints
    )

    normalized_scene = Scene(
        scene_id=scene.scene_id,
        duration_seconds=scene.duration_seconds,
        location=scene.location,
        camera=scene.camera,
        characters=list(scene.characters),
        performance=scene.performance,
        lighting=scene.lighting,
        mood=scene.mood,
        dialogue_or_vocals=scene.dialogue_or_vocals,
        continuity=dict(scene.continuity),
        negative_constraints=list(
            negative_result.constraints
        ),
    )

    prompt_result = build_cinematic_prompt(
        normalized_scene
    )

    issues: list[dict[str, Any]] = []

    if previous_scene is not None:
        issues = continuity_report(
            previous_scene,
            normalized_scene,
        )

    return WorkflowSceneResult(
        scene_id=scene.scene_id,
        valid=True,
        validation_errors=[],
        prompt=prompt_result.prompt,
        negative_prompt=prompt_result.negative_prompt,
        negative_warnings=negative_result.warnings,
        continuity_issues=issues,
    )


def process_project(
    scenes: list[Scene],
) -> list[WorkflowSceneResult]:
    """
    Process an ordered list of cinematic scenes.

    Each scene is compared with the previous scene for continuity.
    """

    results: list[WorkflowSceneResult] = []
    previous_scene: Scene | None = None

    for scene in scenes:
        result = process_scene(
            scene,
            previous_scene=previous_scene,
        )

        results.append(result)

        if result.valid:
            previous_scene = scene

    return results
