"""
Music-video structure models.

This module represents musical sections, performance modes,
scene mappings, timing information, and validation rules for
structured music-video production workflows.
"""

from dataclasses import dataclass, field
from typing import Any


VALID_SECTION_TYPES = {
    "intro",
    "verse",
    "pre-chorus",
    "chorus",
    "post-chorus",
    "instrumental",
    "bridge",
    "breakdown",
    "final-chorus",
    "outro",
    "custom",
}

VALID_PERFORMANCE_MODES = {
    "vocal",
    "instrumental",
    "dialogue",
    "performance-only",
    "cinematic-only",
}


def normalize_music_token(value: str) -> str:
    """
    Normalize section and performance-mode names.

    Examples:
        "Pre Chorus" -> "pre-chorus"
        "FINAL_CHORUS" -> "final-chorus"
    """

    normalized = (
        value.strip()
        .lower()
        .replace("_", " ")
        .replace("-", " ")
    )

    return "-".join(
        normalized.split()
    )


@dataclass
class MusicSection:
    """One structured section of a music-video timeline."""

    section_id: int
    section_type: str
    start_seconds: float
    end_seconds: float
    performance_mode: str

    scene_ids: list[int] = field(
        default_factory=list
    )

    label: str = ""
    notes: str = ""

    @property
    def duration_seconds(self) -> float:
        """Return the duration of the musical section."""

        return (
            self.end_seconds
            - self.start_seconds
        )

    @property
    def normalized_section_type(self) -> str:
        """Return the canonical section type."""

        return normalize_music_token(
            self.section_type
        )

    @property
    def normalized_performance_mode(self) -> str:
        """Return the canonical performance mode."""

        return normalize_music_token(
            self.performance_mode
        )

    @property
    def requires_vocal_performance(self) -> bool:
        """
        Return True when the section requires vocal performance.
        """

        return (
            self.normalized_performance_mode
            == "vocal"
        )

    def validate(self) -> list[str]:
        """Validate this music section."""

        errors: list[str] = []

        if self.section_id < 1:
            errors.append(
                "section_id must be greater than 0"
            )

        if (
            self.normalized_section_type
            not in VALID_SECTION_TYPES
        ):
            errors.append(
                "unsupported section_type: "
                f"{self.section_type}"
            )

        if (
            self.normalized_performance_mode
            not in VALID_PERFORMANCE_MODES
        ):
            errors.append(
                "unsupported performance_mode: "
                f"{self.performance_mode}"
            )

        if self.start_seconds < 0:
            errors.append(
                "start_seconds cannot be negative"
            )

        if (
            self.end_seconds
            <= self.start_seconds
        ):
            errors.append(
                "end_seconds must be greater "
                "than start_seconds"
            )

        invalid_scene_ids = [
            scene_id
            for scene_id in self.scene_ids
            if scene_id < 1
        ]

        if invalid_scene_ids:
            errors.append(
                "scene_ids must contain only "
                "positive integers"
            )

        if (
            len(self.scene_ids)
            != len(set(self.scene_ids))
        ):
            errors.append(
                "scene_ids cannot contain duplicates"
            )

        if (
            self.normalized_section_type
            == "custom"
            and not self.label.strip()
        ):
            errors.append(
                "custom music sections require a label"
            )

        return errors

    def is_valid(self) -> bool:
        """Return True when this section passes validation."""

        return not self.validate()

    def to_dict(self) -> dict[str, Any]:
        """Convert the section into structured data."""

        return {
            "section_id": self.section_id,
            "section_type": (
                self.normalized_section_type
            ),
            "label": self.label,
            "start_seconds": self.start_seconds,
            "end_seconds": self.end_seconds,
            "duration_seconds": (
                self.duration_seconds
            ),
            "performance_mode": (
                self.normalized_performance_mode
            ),
            "requires_vocal_performance": (
                self.requires_vocal_performance
            ),
            "scene_ids": list(
                self.scene_ids
            ),
            "notes": self.notes,
        }


@dataclass
class MusicVideoStructure:
    """Ordered musical structure for a music-video project."""

    sections: list[MusicSection] = field(
        default_factory=list
    )

    @property
    def section_count(self) -> int:
        """Return the number of musical sections."""

        return len(self.sections)

    @property
    def total_duration_seconds(self) -> float:
        """Return the end time of the final musical structure."""

        if not self.sections:
            return 0.0

        return max(
            section.end_seconds
            for section in self.sections
        )

    @property
    def mapped_scene_ids(self) -> list[int]:
        """Return all mapped scene IDs in section order."""

        return [
            scene_id
            for section in self.sections
            for scene_id in section.scene_ids
        ]

    def get_section_for_scene(
        self,
        scene_id: int,
    ) -> MusicSection | None:
        """
        Return the section containing a scene ID,
        or None when the scene is not mapped.
        """

        for section in self.sections:
            if scene_id in section.scene_ids:
                return section

        return None

    def validate(
        self,
        project_scene_ids: list[int] | None = None,
    ) -> list[str]:
        """
        Validate the complete music-video structure.

        Optional project_scene_ids allows validation against
        the scenes contained in a CinematicProject.
        """

        errors: list[str] = []

        if not self.sections:
            errors.append(
                "music-video structure must contain "
                "at least one section"
            )

            return errors

        seen_section_ids: set[int] = set()
        seen_scene_ids: set[int] = set()

        previous_section: MusicSection | None = None

        for section in self.sections:
            if section.section_id in seen_section_ids:
                errors.append(
                    "duplicate section_id: "
                    f"{section.section_id}"
                )

            seen_section_ids.add(
                section.section_id
            )

            for error in section.validate():
                errors.append(
                    f"section {section.section_id}: "
                    f"{error}"
                )

            if previous_section is not None:
                if (
                    section.start_seconds
                    < previous_section.start_seconds
                ):
                    errors.append(
                        "section ordering is not chronological: "
                        f"section {section.section_id}"
                    )

                if (
                    section.start_seconds
                    < previous_section.end_seconds
                ):
                    errors.append(
                        "music sections overlap: "
                        f"{previous_section.section_id} "
                        f"and {section.section_id}"
                    )

            for scene_id in section.scene_ids:
                if scene_id in seen_scene_ids:
                    errors.append(
                        "scene assigned to multiple "
                        f"music sections: {scene_id}"
                    )

                seen_scene_ids.add(
                    scene_id
                )

            previous_section = section

        if project_scene_ids is not None:
            project_ids = set(
                project_scene_ids
            )

            mapped_ids = set(
                self.mapped_scene_ids
            )

            unknown_scene_ids = (
                mapped_ids - project_ids
            )

            for scene_id in sorted(
                unknown_scene_ids
            ):
                errors.append(
                    "music structure references "
                    f"unknown scene_id: {scene_id}"
                )

            unmapped_scene_ids = (
                project_ids - mapped_ids
            )

            for scene_id in sorted(
                unmapped_scene_ids
            ):
                errors.append(
                    "project scene is not mapped "
                    f"to a music section: {scene_id}"
                )

        return errors

    def is_valid(
        self,
        project_scene_ids: list[int] | None = None,
    ) -> bool:
        """Return True when the complete structure is valid."""

        return not self.validate(
            project_scene_ids
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the complete music-video structure to data."""

        vocal_sections = sum(
            section.requires_vocal_performance
            for section in self.sections
        )

        instrumental_sections = sum(
            section.normalized_performance_mode
            == "instrumental"
            for section in self.sections
        )

        return {
            "summary": {
                "section_count": (
                    self.section_count
                ),
                "total_duration_seconds": (
                    self.total_duration_seconds
                ),
                "mapped_scene_count": len(
                    set(self.mapped_scene_ids)
                ),
                "vocal_section_count": (
                    vocal_sections
                ),
                "instrumental_section_count": (
                    instrumental_sections
                ),
            },
            "sections": [
                section.to_dict()
                for section in self.sections
            ],
        }
