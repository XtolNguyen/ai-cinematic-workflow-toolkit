"""
Cinematic prompt builder.

Transforms validated Scene objects into concise, structured prompts
that can be adapted for AI video generation systems.
"""

from dataclasses import dataclass

from .scene import Scene


@dataclass
class PromptResult:
    """Generated cinematic prompt and negative prompt."""

    prompt: str
    negative_prompt: str


def build_cinematic_prompt(scene: Scene) -> PromptResult:
    """
    Build a cinematic prompt from a validated Scene.

    Raises:
        ValueError: If the scene contains invalid data.
    """

    errors = scene.validate()

    if errors:
        raise ValueError(
            "Scene validation failed: " + "; ".join(errors)
        )

    components: list[str] = []

    components.append(
        f"Scene {scene.scene_id}: {scene.location}."
    )

    if scene.characters:
        components.append(
            "Characters: " + ", ".join(scene.characters) + "."
        )

    if scene.performance:
        components.append(
            f"Performance: {scene.performance}."
        )

    camera_parts = [scene.camera.shot]

    if scene.camera.movement:
        camera_parts.append(scene.camera.movement)

    if scene.camera.lens:
        camera_parts.append(scene.camera.lens)

    components.append(
        "Camera: " + ", ".join(camera_parts) + "."
    )

    if scene.lighting:
        components.append(
            f"Lighting: {scene.lighting}."
        )

    if scene.mood:
        components.append(
            f"Mood: {scene.mood}."
        )

    if scene.dialogue_or_vocals:
        components.append(
            f"Dialogue/Vocals: {scene.dialogue_or_vocals}."
        )

    if scene.continuity:
        continuity_text = ", ".join(
            f"{key}: {value}"
            for key, value in scene.continuity.items()
        )

        components.append(
            f"Continuity: {continuity_text}."
        )

    prompt = " ".join(components)

    negative_prompt = ", ".join(
        scene.negative_constraints
    )

    return PromptResult(
        prompt=prompt,
        negative_prompt=negative_prompt,
    )
