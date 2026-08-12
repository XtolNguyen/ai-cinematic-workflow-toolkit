"""
Core cinematic scene model.

This module defines a structured representation of a cinematic scene
and performs basic validation before the scene is passed to other
workflow modules.
"""

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class Camera:
    """Camera configuration for a cinematic scene."""

    shot: str
    movement: str = ""
    lens: str = ""


@dataclass
class Scene:
    """Structured representation of one cinematic scene."""

    scene_id: int
    duration_seconds: float
    location: str
    camera: Camera

    characters: list[str] = field(default_factory=list)
    performance: str = ""
    lighting: str = ""
    mood: str = ""
    dialogue_or_vocals: str = ""

    continuity: dict[str, Any] = field(default_factory=dict)
    negative_constraints: list[str] = field(default_factory=list)

    def validate(self) -> list[str]:
        """
        Validate the scene and return a list of problems.

        An empty list means the scene passed all current validation rules.
        """

        errors: list[str] = []

        if self.scene_id < 1:
            errors.append("scene_id must be greater than 0")

        if self.duration_seconds <= 0:
            errors.append("duration_seconds must be greater than 0")

        if not self.location.strip():
            errors.append("location cannot be empty")

        if not self.camera.shot.strip():
            errors.append("camera.shot cannot be empty")

        return errors

    def is_valid(self) -> bool:
        """Return True when the scene passes validation."""

        return len(self.validate()) == 0

    def to_dict(self) -> dict[str, Any]:
        """Convert the scene into a serializable dictionary."""

        return asdict(self)
