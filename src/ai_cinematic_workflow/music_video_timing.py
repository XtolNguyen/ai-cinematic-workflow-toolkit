"""
Music-video timing and duration alignment validation.

This module connects:

- configurable scene DurationPolicy
- cinematic scene timelines
- MusicVideoStructure sections

It detects scene-duration policy violations, scene/music-section
alignment problems, and total runtime mismatches without hard-coding
a platform-specific clip duration.
"""

from dataclasses import asdict, dataclass, field
from typing import Any

from .duration import (
    DurationPolicy,
    validate_scene_duration,
)
from .music_video import MusicVideoStructure
from .scene import Scene
from .timeline import build_timeline


@dataclass(frozen=True)
class MusicVideoTimingIssue:
    """One structured music-video timing validation issue."""

    issue_type: str
    scope: str
    message: str

    scene_id: int | None = None
    section_id: int | None = None

    expected_duration: float | None = None
    actual_duration: float | None = None
    difference_seconds: float | None = None

    expected_start_seconds: float | None = None
    actual_start_seconds: float | None = None

    expected_end_seconds: float | None = None
    actual_end_seconds: float | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert the issue into serializable data."""

        return asdict(self)


@dataclass
class MusicVideoTimingValidationResult:
    """Complete timing validation result for a music-video project."""

    issues: list[MusicVideoTimingIssue] = field(
        default_factory=list
    )

    scene_count: int = 0
    section_count: int = 0

    cinematic_duration_seconds: float = 0.0
    music_duration_seconds: float = 0.0

    policy: DurationPolicy | None = None

    @property
    def is_valid(self) -> bool:
        """Return True when no timing issues were found."""

        return not self.issues

    @property
    def issue_count(self) -> int:
        """Return the total number of timing issues."""

        return len(self.issues)

    @property
    def scene_duration_issue_count(self) -> int:
        """Return the number of scene-duration policy issues."""

        return sum(
            issue.scope == "scene_duration"
            for issue in self.issues
        )

    @property
    def section_alignment_issue_count(self) -> int:
        """Return the number of section-alignment issues."""

        return sum(
            issue.scope == "section_alignment"
            for issue in self.issues
        )

    @property
    def runtime_issue_count(self) -> int:
        """Return the number of total-runtime issues."""

        return sum(
            issue.scope == "project_runtime"
            for issue in self.issues
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the complete result into serializable data."""

        return {
            "summary": {
                "valid": self.is_valid,
                "issue_count": self.issue_count,
                "scene_count": self.scene_count,
                "section_count": self.section_count,
                "cinematic_duration_seconds": (
                    self.cinematic_duration_seconds
                ),
                "music_duration_seconds": (
                    self.music_duration_seconds
                ),
                "scene_duration_issue_count": (
                    self.scene_duration_issue_count
                ),
                "section_alignment_issue_count": (
                    self.section_alignment_issue_count
                ),
                "runtime_issue_count": (
                    self.runtime_issue_count
                ),
            },
            "policy": (
                self.policy.to_dict()
                if self.policy is not None
                else None
            ),
            "issues": [
                issue.to_dict()
                for issue in self.issues
            ],
        }


def validate_music_video_timing(
    scenes: list[Scene],
    structure: MusicVideoStructure,
    policy: DurationPolicy,
) -> MusicVideoTimingValidationResult:
    """
    Validate cinematic scene timing against a music-video structure.

    Validation includes:

    - scene durations against DurationPolicy
    - mapped scene coverage against music sections
    - scenes extending outside assigned sections
    - music-section duration vs mapped scene duration
    - total cinematic runtime vs music-video runtime

    DurationPolicy tolerance is reused for timing comparisons.
    """

    if not scenes:
        raise ValueError(
            "music-video timing validation "
            "requires at least one scene"
        )

    policy_errors = policy.validate()

    if policy_errors:
        raise ValueError(
            "Invalid duration policy: "
            + "; ".join(policy_errors)
        )

    scene_ids = [
        scene.scene_id
        for scene in scenes
    ]

    if len(scene_ids) != len(set(scene_ids)):
        raise ValueError(
            "music-video timing validation "
            "requires unique scene IDs"
        )

    for scene in scenes:
        scene_errors = scene.validate()

        if scene_errors:
            raise ValueError(
                f"Invalid scene {scene.scene_id}: "
                + "; ".join(scene_errors)
            )

    structure_errors = structure.validate(
        project_scene_ids=scene_ids
    )

    if structure_errors:
        raise ValueError(
            "Invalid music-video structure: "
            + "; ".join(structure_errors)
        )

    timeline = build_timeline(
        scenes
    )

    entry_by_scene_id = {
        entry.scene_id: entry
        for entry in timeline.entries
    }

    tolerance = float(
        policy.tolerance_seconds
    )

    issues: list[MusicVideoTimingIssue] = []

    # ---------------------------------------------------------
    # Scene duration policy validation
    # ---------------------------------------------------------

    for scene in scenes:
        duration_result = (
            validate_scene_duration(
                scene,
                policy,
            )
        )

        for duration_issue in duration_result.issues:
            issues.append(
                MusicVideoTimingIssue(
                    issue_type=(
                        duration_issue.issue_type
                    ),
                    scope="scene_duration",
                    scene_id=scene.scene_id,
                    expected_duration=(
                        duration_issue.expected_duration
                    ),
                    actual_duration=(
                        duration_issue.actual_duration
                    ),
                    difference_seconds=(
                        duration_issue.difference_seconds
                    ),
                    message=(
                        duration_issue.message
                    ),
                )
            )

    # ---------------------------------------------------------
    # Music-section alignment validation
    # ---------------------------------------------------------

    for section in structure.sections:
        mapped_entries = [
            entry_by_scene_id[scene_id]
            for scene_id in section.scene_ids
            if scene_id in entry_by_scene_id
        ]

        if not mapped_entries:
            issues.append(
                MusicVideoTimingIssue(
                    issue_type="section_without_scenes",
                    scope="section_alignment",
                    section_id=section.section_id,
                    expected_duration=(
                        section.duration_seconds
                    ),
                    actual_duration=0.0,
                    difference_seconds=(
                        -section.duration_seconds
                    ),
                    message=(
                        f"music section "
                        f"{section.section_id} has no "
                        "mapped cinematic scene coverage"
                    ),
                )
            )

            continue

        mapped_duration = sum(
            float(entry.duration_seconds)
            for entry in mapped_entries
        )

        section_duration = float(
            section.duration_seconds
        )

        duration_difference = (
            mapped_duration
            - section_duration
        )

        if (
            abs(duration_difference)
            > tolerance
        ):
            issues.append(
                MusicVideoTimingIssue(
                    issue_type=(
                        "section_duration_mismatch"
                    ),
                    scope="section_alignment",
                    section_id=section.section_id,
                    expected_duration=(
                        section_duration
                    ),
                    actual_duration=(
                        mapped_duration
                    ),
                    difference_seconds=(
                        duration_difference
                    ),
                    message=(
                        f"music section "
                        f"{section.section_id} duration "
                        f"{section_duration:g}s does not "
                        "match its mapped cinematic "
                        f"scene duration "
                        f"{mapped_duration:g}s"
                    ),
                )
            )

        for entry in mapped_entries:
            starts_too_early = (
                entry.start_seconds
                < section.start_seconds
                - tolerance
            )

            ends_too_late = (
                entry.end_seconds
                > section.end_seconds
                + tolerance
            )

            if (
                starts_too_early
                or ends_too_late
            ):
                issues.append(
                    MusicVideoTimingIssue(
                        issue_type=(
                            "scene_outside_music_section"
                        ),
                        scope="section_alignment",
                        scene_id=entry.scene_id,
                        section_id=section.section_id,
                        expected_start_seconds=(
                            float(
                                section.start_seconds
                            )
                        ),
                        actual_start_seconds=(
                            float(
                                entry.start_seconds
                            )
                        ),
                        expected_end_seconds=(
                            float(
                                section.end_seconds
                            )
                        ),
                        actual_end_seconds=(
                            float(
                                entry.end_seconds
                            )
                        ),
                        message=(
                            f"scene {entry.scene_id} timing "
                            "extends outside music section "
                            f"{section.section_id}"
                        ),
                    )
                )

        coverage_start = min(
            float(entry.start_seconds)
            for entry in mapped_entries
        )

        coverage_end = max(
            float(entry.end_seconds)
            for entry in mapped_entries
        )

        if (
            abs(
                coverage_start
                - float(section.start_seconds)
            )
            > tolerance
        ):
            issues.append(
                MusicVideoTimingIssue(
                    issue_type=(
                        "section_start_mismatch"
                    ),
                    scope="section_alignment",
                    section_id=section.section_id,
                    expected_start_seconds=(
                        float(
                            section.start_seconds
                        )
                    ),
                    actual_start_seconds=(
                        coverage_start
                    ),
                    difference_seconds=(
                        coverage_start
                        - float(
                            section.start_seconds
                        )
                    ),
                    message=(
                        f"music section "
                        f"{section.section_id} starts at "
                        f"{section.start_seconds:g}s but "
                        "mapped cinematic coverage starts "
                        f"at {coverage_start:g}s"
                    ),
                )
            )

        if (
            abs(
                coverage_end
                - float(section.end_seconds)
            )
            > tolerance
        ):
            issues.append(
                MusicVideoTimingIssue(
                    issue_type=(
                        "section_end_mismatch"
                    ),
                    scope="section_alignment",
                    section_id=section.section_id,
                    expected_end_seconds=(
                        float(
                            section.end_seconds
                        )
                    ),
                    actual_end_seconds=(
                        coverage_end
                    ),
                    difference_seconds=(
                        coverage_end
                        - float(
                            section.end_seconds
                        )
                    ),
                    message=(
                        f"music section "
                        f"{section.section_id} ends at "
                        f"{section.end_seconds:g}s but "
                        "mapped cinematic coverage ends "
                        f"at {coverage_end:g}s"
                    ),
                )
            )

    # ---------------------------------------------------------
    # Total project runtime validation
    # ---------------------------------------------------------

    cinematic_duration = float(
        timeline.total_duration_seconds
    )

    music_duration = float(
        structure.total_duration_seconds
    )

    runtime_difference = (
        cinematic_duration
        - music_duration
    )

    if abs(runtime_difference) > tolerance:
        issues.append(
            MusicVideoTimingIssue(
                issue_type=(
                    "project_runtime_mismatch"
                ),
                scope="project_runtime",
                expected_duration=(
                    music_duration
                ),
                actual_duration=(
                    cinematic_duration
                ),
                difference_seconds=(
                    runtime_difference
                ),
                message=(
                    "cinematic project duration "
                    f"{cinematic_duration:g}s does not "
                    "match music-video duration "
                    f"{music_duration:g}s"
                ),
            )
        )

    return MusicVideoTimingValidationResult(
        issues=issues,
        scene_count=len(scenes),
        section_count=structure.section_count,
        cinematic_duration_seconds=(
            cinematic_duration
        ),
        music_duration_seconds=(
            music_duration
        ),
        policy=policy,
    )
