"""
Scene continuity validation.

This module compares consecutive cinematic scenes and reports
potential continuity changes in characters, location, lighting,
and custom continuity metadata.
"""

from dataclasses import asdict, dataclass
from typing import Any

from .scene import Scene


@dataclass(frozen=True)
class ContinuityIssue:
    """Represents one potential continuity mismatch."""

    field: str
    previous_value: Any
    current_value: Any
    message: str

    def to_dict(self) -> dict[str, Any]:
        """Convert the issue into a serializable dictionary."""

        return asdict(self)


def compare_scenes(
    previous_scene: Scene,
    current_scene: Scene,
    check_fields: tuple[str, ...] = (
        "characters",
        "location",
        "lighting",
    ),
) -> list[ContinuityIssue]:
    """
    Compare two consecutive scenes.

    The function reports changes instead of automatically treating them
    as fatal errors. This allows intentional cinematic transitions while
    still surfacing possible continuity problems.
    """

    issues: list[ContinuityIssue] = []

    for field_name in check_fields:
        previous_value = getattr(
            previous_scene,
            field_name,
            None,
        )
        current_value = getattr(
            current_scene,
            field_name,
            None,
        )

        if previous_value != current_value:
            issues.append(
                ContinuityIssue(
                    field=field_name,
                    previous_value=previous_value,
                    current_value=current_value,
                    message=(
                        f"{field_name} changed between "
                        f"scene {previous_scene.scene_id} and "
                        f"scene {current_scene.scene_id}"
                    ),
                )
            )

    shared_continuity_keys = (
        previous_scene.continuity.keys()
        & current_scene.continuity.keys()
    )

    for key in sorted(shared_continuity_keys):
        previous_value = previous_scene.continuity[key]
        current_value = current_scene.continuity[key]

        if previous_value != current_value:
            issues.append(
                ContinuityIssue(
                    field=f"continuity.{key}",
                    previous_value=previous_value,
                    current_value=current_value,
                    message=(
                        f"continuity field '{key}' changed between "
                        f"scene {previous_scene.scene_id} and "
                        f"scene {current_scene.scene_id}"
                    ),
                )
            )

    return issues


def has_continuity_issues(
    previous_scene: Scene,
    current_scene: Scene,
) -> bool:
    """Return True when possible continuity issues are detected."""

    return bool(
        compare_scenes(
            previous_scene,
            current_scene,
        )
    )


def continuity_report(
    previous_scene: Scene,
    current_scene: Scene,
) -> list[dict[str, Any]]:
    """
    Return continuity issues as serializable dictionaries.
    """

    return [
        issue.to_dict()
        for issue in compare_scenes(
            previous_scene,
            current_scene,
        )
    ]
