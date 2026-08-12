"""
Configurable cinematic duration policies and scene validation.

This module provides platform-agnostic duration rules for cinematic
scenes. Fixed clip lengths such as 15 seconds are represented through
configuration rather than hard-coded into the core toolkit.
"""

from dataclasses import asdict, dataclass, field
from typing import Any

from .scene import Scene


@dataclass
class DurationPolicy:
    """
    Configurable duration rules for cinematic scenes.

    Rules may define:

    - preferred scene duration
    - minimum scene duration
    - maximum scene duration
    - explicitly allowed durations
    - comparison tolerance
    - strict preferred-duration enforcement

    The toolkit does not assume a universal clip duration.
    """

    preferred_scene_duration: float | None = None
    minimum_scene_duration: float | None = None
    maximum_scene_duration: float | None = None

    allowed_scene_durations: list[float] = field(
        default_factory=list
    )

    tolerance_seconds: float = 0.0
    strict: bool = False

    def validate(self) -> list[str]:
        """Validate the duration-policy configuration."""

        errors: list[str] = []

        if (
            self.preferred_scene_duration is not None
            and self.preferred_scene_duration <= 0
        ):
            errors.append(
                "preferred_scene_duration must be "
                "greater than 0"
            )

        if (
            self.minimum_scene_duration is not None
            and self.minimum_scene_duration <= 0
        ):
            errors.append(
                "minimum_scene_duration must be "
                "greater than 0"
            )

        if (
            self.maximum_scene_duration is not None
            and self.maximum_scene_duration <= 0
        ):
            errors.append(
                "maximum_scene_duration must be "
                "greater than 0"
            )

        if self.tolerance_seconds < 0:
            errors.append(
                "tolerance_seconds cannot be negative"
            )

        if (
            self.minimum_scene_duration is not None
            and self.maximum_scene_duration is not None
            and self.minimum_scene_duration
            > self.maximum_scene_duration
        ):
            errors.append(
                "minimum_scene_duration cannot be "
                "greater than maximum_scene_duration"
            )

        invalid_allowed_durations = [
            duration
            for duration in self.allowed_scene_durations
            if duration <= 0
        ]

        if invalid_allowed_durations:
            errors.append(
                "allowed_scene_durations must contain "
                "only values greater than 0"
            )

        if (
            len(self.allowed_scene_durations)
            != len(set(self.allowed_scene_durations))
        ):
            errors.append(
                "allowed_scene_durations cannot "
                "contain duplicates"
            )

        preferred = self.preferred_scene_duration
        minimum = self.minimum_scene_duration
        maximum = self.maximum_scene_duration

        if preferred is not None:
            if (
                minimum is not None
                and preferred < minimum
            ):
                errors.append(
                    "preferred_scene_duration cannot be "
                    "below minimum_scene_duration"
                )

            if (
                maximum is not None
                and preferred > maximum
            ):
                errors.append(
                    "preferred_scene_duration cannot be "
                    "above maximum_scene_duration"
                )

        for duration in self.allowed_scene_durations:
            if (
                minimum is not None
                and duration < minimum
            ):
                errors.append(
                    "allowed_scene_durations cannot "
                    "contain values below "
                    "minimum_scene_duration"
                )
                break

        for duration in self.allowed_scene_durations:
            if (
                maximum is not None
                and duration > maximum
            ):
                errors.append(
                    "allowed_scene_durations cannot "
                    "contain values above "
                    "maximum_scene_duration"
                )
                break

        if (
            self.strict
            and preferred is not None
            and self.allowed_scene_durations
        ):
            preferred_is_allowed = any(
                abs(
                    preferred
                    - allowed_duration
                )
                <= self.tolerance_seconds
                for allowed_duration
                in self.allowed_scene_durations
            )

            if not preferred_is_allowed:
                errors.append(
                    "strict preferred_scene_duration "
                    "must also be present in "
                    "allowed_scene_durations"
                )

        return errors

    def is_valid(self) -> bool:
        """Return True when the policy configuration is valid."""

        return not self.validate()

    def to_dict(self) -> dict[str, Any]:
        """Convert the policy into serializable data."""

        return asdict(self)


@dataclass(frozen=True)
class DurationIssue:
    """One structured scene-duration validation issue."""

    issue_type: str
    message: str

    scene_id: int

    expected_duration: float | None = None
    actual_duration: float | None = None
    difference_seconds: float | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert the issue into serializable data."""

        return asdict(self)


@dataclass
class DurationValidationResult:
    """Validation result for one cinematic scene."""

    scene_id: int
    actual_duration: float
    issues: list[DurationIssue] = field(
        default_factory=list
    )

    @property
    def is_valid(self) -> bool:
        """Return True when no duration issues were found."""

        return not self.issues

    @property
    def issue_count(self) -> int:
        """Return the number of duration issues."""

        return len(self.issues)

    def to_dict(self) -> dict[str, Any]:
        """Convert the result into serializable data."""

        return {
            "scene_id": self.scene_id,
            "actual_duration": (
                self.actual_duration
            ),
            "valid": self.is_valid,
            "issue_count": self.issue_count,
            "issues": [
                issue.to_dict()
                for issue in self.issues
            ],
        }


def validate_scene_duration(
    scene: Scene,
    policy: DurationPolicy,
) -> DurationValidationResult:
    """
    Validate one scene against a configurable duration policy.

    Minimum, maximum, and allowed-duration constraints are
    always enforced when configured.

    The preferred duration becomes mandatory only when
    policy.strict is True.

    Duration tolerance is applied to all comparisons.
    """

    policy_errors = policy.validate()

    if policy_errors:
        raise ValueError(
            "Invalid duration policy: "
            + "; ".join(policy_errors)
        )

    actual = float(
        scene.duration_seconds
    )

    tolerance = float(
        policy.tolerance_seconds
    )

    issues: list[DurationIssue] = []

    if actual <= 0:
        issues.append(
            DurationIssue(
                issue_type=(
                    "invalid_scene_duration"
                ),
                scene_id=scene.scene_id,
                actual_duration=actual,
                message=(
                    "scene duration must be "
                    "greater than 0"
                ),
            )
        )

        return DurationValidationResult(
            scene_id=scene.scene_id,
            actual_duration=actual,
            issues=issues,
        )

    minimum = (
        policy.minimum_scene_duration
    )

    if (
        minimum is not None
        and actual + tolerance
        < minimum
    ):
        issues.append(
            DurationIssue(
                issue_type=(
                    "below_minimum_duration"
                ),
                scene_id=scene.scene_id,
                expected_duration=float(
                    minimum
                ),
                actual_duration=actual,
                difference_seconds=(
                    actual
                    - float(minimum)
                ),
                message=(
                    f"scene {scene.scene_id} duration "
                    f"{actual:g}s is below the "
                    f"minimum duration {minimum:g}s"
                ),
            )
        )

    maximum = (
        policy.maximum_scene_duration
    )

    if (
        maximum is not None
        and actual - tolerance
        > maximum
    ):
        issues.append(
            DurationIssue(
                issue_type=(
                    "above_maximum_duration"
                ),
                scene_id=scene.scene_id,
                expected_duration=float(
                    maximum
                ),
                actual_duration=actual,
                difference_seconds=(
                    actual
                    - float(maximum)
                ),
                message=(
                    f"scene {scene.scene_id} duration "
                    f"{actual:g}s exceeds the "
                    f"maximum duration {maximum:g}s"
                ),
            )
        )

    allowed_durations = [
        float(duration)
        for duration
        in policy.allowed_scene_durations
    ]

    if allowed_durations:
        matches_allowed_duration = any(
            abs(actual - duration)
            <= tolerance
            for duration
            in allowed_durations
        )

        if not matches_allowed_duration:
            closest_duration = min(
                allowed_durations,
                key=lambda duration: abs(
                    actual - duration
                ),
            )

            issues.append(
                DurationIssue(
                    issue_type=(
                        "disallowed_duration"
                    ),
                    scene_id=scene.scene_id,
                    expected_duration=(
                        closest_duration
                    ),
                    actual_duration=actual,
                    difference_seconds=(
                        actual
                        - closest_duration
                    ),
                    message=(
                        f"scene {scene.scene_id} duration "
                        f"{actual:g}s does not match "
                        "an allowed scene duration"
                    ),
                )
            )

    preferred = (
        policy.preferred_scene_duration
    )

    if (
        policy.strict
        and preferred is not None
        and abs(
            actual
            - float(preferred)
        )
        > tolerance
    ):
        issues.append(
            DurationIssue(
                issue_type=(
                    "preferred_duration_mismatch"
                ),
                scene_id=scene.scene_id,
                expected_duration=float(
                    preferred
                ),
                actual_duration=actual,
                difference_seconds=(
                    actual
                    - float(preferred)
                ),
                message=(
                    f"scene {scene.scene_id} duration "
                    f"{actual:g}s does not match "
                    f"the strict preferred duration "
                    f"{preferred:g}s"
                ),
            )
        )

    return DurationValidationResult(
        scene_id=scene.scene_id,
        actual_duration=actual,
        issues=issues,
    )
