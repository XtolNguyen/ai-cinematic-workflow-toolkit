"""
Cinematic project model.

This module represents a complete AI cinematic production project
containing metadata, ordered scenes, and optional music-video
structure information.
"""

from dataclasses import asdict, dataclass, field
from typing import Any

from .music_video import MusicVideoStructure
from .scene import Scene


@dataclass
class ProjectMetadata:
    """General metadata for a cinematic project."""

    title: str
    project_type: str = "cinematic"
    description: str = ""
    language: str = "en"
    target_platform: str = ""
    aspect_ratio: str = ""
    frame_rate: float | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert metadata to a serializable dictionary."""
        return asdict(self)


@dataclass
class CinematicProject:
    """A complete ordered cinematic production project."""

    metadata: ProjectMetadata
    scenes: list[Scene] = field(default_factory=list)

    music_video_structure: MusicVideoStructure | None = None

    @property
    def scene_count(self) -> int:
        """Return the total number of scenes."""
        return len(self.scenes)

    @property
    def total_duration_seconds(self) -> float:
        """Return the total duration of all scenes."""
        return sum(
            scene.duration_seconds
            for scene in self.scenes
        )

    @property
    def is_music_video(self) -> bool:
        """
        Return True when the project contains
        a music-video structure.
        """

        return (
            self.music_video_structure
            is not None
        )

    def add_scene(self, scene: Scene) -> None:
        """Append a scene to the project."""
        self.scenes.append(scene)

    def validate(self) -> list[str]:
        """
        Validate project metadata, scenes,
        and optional music-video structure.

        Returns a list of validation problems.
        """

        errors: list[str] = []

        if not self.metadata.title.strip():
            errors.append(
                "project title cannot be empty"
            )

        if not self.scenes:
            errors.append(
                "project must contain at least one scene"
            )

        scene_ids: set[int] = set()

        for scene in self.scenes:
            if scene.scene_id in scene_ids:
                errors.append(
                    f"duplicate scene_id: {scene.scene_id}"
                )

            scene_ids.add(
                scene.scene_id
            )

            for error in scene.validate():
                errors.append(
                    f"scene {scene.scene_id}: {error}"
                )

        if self.music_video_structure is not None:
            music_errors = (
                self.music_video_structure.validate(
                    project_scene_ids=[
                        scene.scene_id
                        for scene in self.scenes
                    ]
                )
            )

            for error in music_errors:
                errors.append(
                    f"music_video: {error}"
                )

        return errors

    def is_valid(self) -> bool:
        """Return True when the project passes validation."""
        return not self.validate()

    def to_dict(self) -> dict[str, Any]:
        """Convert the full project into structured data."""

        data: dict[str, Any] = {
            "metadata": self.metadata.to_dict(),
            "summary": {
                "scene_count": self.scene_count,
                "total_duration_seconds": (
                    self.total_duration_seconds
                ),
                "is_music_video": (
                    self.is_music_video
                ),
            },
            "scenes": [
                scene.to_dict()
                for scene in self.scenes
            ],
        }

        if self.music_video_structure is not None:
            data["music_video"] = (
                self.music_video_structure.to_dict()
            )

        return data
