"""
Cinematic timeline planning.

This module converts ordered cinematic scenes into structured timeline
entries with start times, end times, cumulative duration, and optional
gap / overlap detection.
"""

from dataclasses import asdict, dataclass
from typing import Any

from .scene import Scene


@dataclass(frozen=True)
class TimelineIssue:
    """Represents a potential timeline planning problem."""

    issue_type: str
    scene_id: int
    message: str
    previous_scene_id: int | None = None
    duration_seconds: float | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert the timeline issue into serializable data."""
        return asdict(self)


@dataclass(frozen=True)
class TimelineEntry:
    """Represents one scene on the cinematic timeline."""

    scene_id: int
    start_seconds: float
    end_seconds: float
    duration_seconds: float

    def to_dict(self) -> dict[str, Any]:
        """Convert the timeline entry into serializable data."""
        return asdict(self)


@dataclass
class TimelineResult:
    """Complete result produced by the timeline planner."""

    entries: list[TimelineEntry]
    issues: list[TimelineIssue]
    total_duration_seconds: float

    @property
    def scene_count(self) -> int:
        """Return the number of timeline entries."""
        return len(self.entries)

    @property
    def has_issues(self) -> bool:
        """Return True when timeline issues were detected."""
        return bool(self.issues)

    def to_dict(self) -> dict[str, Any]:
        """Convert the complete timeline result to structured data."""

        return {
            "summary": {
                "scene_count": self.scene_count,
                "total_duration_seconds": self.total_duration_seconds,
                "issue_count": len(self.issues),
            },
            "entries": [
                entry.to_dict()
                for entry in self.entries
            ],
            "issues": [
                issue.to_dict()
                for issue in self.issues
            ],
        }


def format_timestamp(seconds: float) -> str:
    """
    Convert seconds into HH:MM:SS format.

    Fractional seconds are preserved when needed.
    """

    if seconds < 0:
        raise ValueError(
            "timestamp seconds cannot be negative"
        )

    total_seconds = float(seconds)

    hours = int(
        total_seconds // 3600
    )

    minutes = int(
        (total_seconds % 3600) // 60
    )

    remaining = (
        total_seconds % 60
    )

    if remaining.is_integer():
        seconds_text = (
            f"{int(remaining):02d}"
        )
    else:
        seconds_text = (
            f"{remaining:05.2f}"
        )

    return (
        f"{hours:02d}:"
        f"{minutes:02d}:"
        f"{seconds_text}"
    )


def build_timeline(
    scenes: list[Scene],
    start_times: dict[int, float] | None = None,
) -> TimelineResult:
    """
    Build a cinematic timeline from an ordered list of scenes.

    By default, scenes are placed continuously one after another.

    Optional ``start_times`` may explicitly define the start time
    of individual scene IDs. Explicit timing makes it possible to
    detect timeline gaps and overlaps.

    Raises:
        ValueError:
            If scene data is invalid, a scene ID is duplicated,
            or an explicit start time is negative.
    """

    if not scenes:
        return TimelineResult(
            entries=[],
            issues=[],
            total_duration_seconds=0,
        )

    start_times = start_times or {}

    seen_scene_ids: set[int] = set()
    entries: list[TimelineEntry] = []
    issues: list[TimelineIssue] = []

    previous_scene: Scene | None = None
    previous_entry: TimelineEntry | None = None

    for scene in scenes:
        validation_errors = scene.validate()

        if validation_errors:
            raise ValueError(
                f"Scene {scene.scene_id} validation failed: "
                + "; ".join(validation_errors)
            )

        if scene.scene_id in seen_scene_ids:
            raise ValueError(
                f"duplicate scene_id: {scene.scene_id}"
            )

        seen_scene_ids.add(
            scene.scene_id
        )

        if (
            previous_scene is not None
            and scene.scene_id <= previous_scene.scene_id
        ):
            issues.append(
                TimelineIssue(
                    issue_type="scene_order",
                    scene_id=scene.scene_id,
                    previous_scene_id=(
                        previous_scene.scene_id
                    ),
                    message=(
                        f"Scene {scene.scene_id} appears after "
                        f"scene {previous_scene.scene_id} but "
                        "does not have a greater scene_id."
                    ),
                )
            )

        if scene.scene_id in start_times:
            start_seconds = start_times[
                scene.scene_id
            ]

            if start_seconds < 0:
                raise ValueError(
                    f"Scene {scene.scene_id} start time "
                    "cannot be negative"
                )

        elif previous_entry is None:
            start_seconds = 0.0

        else:
            start_seconds = (
                previous_entry.end_seconds
            )

        end_seconds = (
            start_seconds
            + scene.duration_seconds
        )

        current_entry = TimelineEntry(
            scene_id=scene.scene_id,
            start_seconds=start_seconds,
            end_seconds=end_seconds,
            duration_seconds=(
                scene.duration_seconds
            ),
        )

        if previous_entry is not None:
            difference = (
                start_seconds
                - previous_entry.end_seconds
            )

            if difference > 0:
                issues.append(
                    TimelineIssue(
                        issue_type="gap",
                        scene_id=scene.scene_id,
                        previous_scene_id=(
                            previous_entry.scene_id
                        ),
                        duration_seconds=difference,
                        message=(
                            f"Gap of {difference} seconds "
                            f"between scene "
                            f"{previous_entry.scene_id} and "
                            f"scene {scene.scene_id}."
                        ),
                    )
                )

            elif difference < 0:
                overlap = abs(
                    difference
                )

                issues.append(
                    TimelineIssue(
                        issue_type="overlap",
                        scene_id=scene.scene_id,
                        previous_scene_id=(
                            previous_entry.scene_id
                        ),
                        duration_seconds=overlap,
                        message=(
                            f"Overlap of {overlap} seconds "
                            f"between scene "
                            f"{previous_entry.scene_id} and "
                            f"scene {scene.scene_id}."
                        ),
                    )
                )

        entries.append(
            current_entry
        )

        previous_scene = scene
        previous_entry = current_entry

    total_duration_seconds = max(
        entry.end_seconds
        for entry in entries
    )

    return TimelineResult(
        entries=entries,
        issues=issues,
        total_duration_seconds=(
            total_duration_seconds
        ),
    )
