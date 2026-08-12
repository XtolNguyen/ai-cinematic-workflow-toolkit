"""
Advanced cinematic continuity profiles and validation.

This module extends the toolkit's basic continuity capabilities with
configurable scene-to-scene continuity policies.

The existing continuity.py API remains unchanged for backward
compatibility.
"""

from dataclasses import asdict, dataclass, field
from typing import Any

from .scene import Scene


VALID_CONTINUITY_SEVERITIES = {
    "error",
    "warning",
    "ignore",
}


def normalize_continuity_field(
    value: str,
) -> str:
    """
    Normalize a continuity field name.

    Examples:

        "Time Of Day" -> "time_of_day"
        "camera-shot" -> "camera_shot"
    """

    normalized = (
        value.strip()
        .lower()
        .replace("-", " ")
    )

    return "_".join(
        normalized.split()
    )


def _normalize_fields(
    values: list[str],
) -> list[str]:
    """Normalize a collection of continuity field names."""

    return [
        normalize_continuity_field(value)
        for value in values
    ]


def _find_duplicates(
    values: list[str],
) -> list[str]:
    """Return duplicate values while preserving stable order."""

    seen: set[str] = set()
    duplicates: list[str] = []

    for value in values:
        if (
            value in seen
            and value not in duplicates
        ):
            duplicates.append(value)

        seen.add(value)

    return duplicates


@dataclass
class ContinuityProfile:
    """
    Configurable continuity policy for cinematic scenes.

    Fields may be:

    - required
    - optional
    - ignored
    - strictly locked
    - warning-only
    - explicitly allowed to change

    Global strict mode controls the default severity for changes
    that are not explicitly categorized.
    """

    name: str = "default"

    required_fields: list[str] = field(
        default_factory=list
    )

    optional_fields: list[str] = field(
        default_factory=list
    )

    ignored_fields: list[str] = field(
        default_factory=list
    )

    strict_fields: list[str] = field(
        default_factory=list
    )

    warning_fields: list[str] = field(
        default_factory=list
    )

    allowed_change_fields: list[str] = field(
        default_factory=list
    )

    strict: bool = True

    missing_required_severity: str = "error"

    @property
    def normalized_required_fields(
        self,
    ) -> list[str]:
        return _normalize_fields(
            self.required_fields
        )

    @property
    def normalized_optional_fields(
        self,
    ) -> list[str]:
        return _normalize_fields(
            self.optional_fields
        )

    @property
    def normalized_ignored_fields(
        self,
    ) -> list[str]:
        return _normalize_fields(
            self.ignored_fields
        )

    @property
    def normalized_strict_fields(
        self,
    ) -> list[str]:
        return _normalize_fields(
            self.strict_fields
        )

    @property
    def normalized_warning_fields(
        self,
    ) -> list[str]:
        return _normalize_fields(
            self.warning_fields
        )

    @property
    def normalized_allowed_change_fields(
        self,
    ) -> list[str]:
        return _normalize_fields(
            self.allowed_change_fields
        )

    @property
    def active_fields(
        self,
    ) -> list[str]:
        """
        Return all fields actively evaluated by this profile.

        Ordering follows profile configuration while duplicates
        across categories are removed.
        """

        fields: list[str] = []

        candidates = (
            self.normalized_required_fields
            + self.normalized_optional_fields
            + self.normalized_strict_fields
            + self.normalized_warning_fields
        )

        for field_name in candidates:
            if (
                field_name
                and field_name not in fields
            ):
                fields.append(field_name)

        return fields

    def validate(self) -> list[str]:
        """Validate the continuity-profile configuration."""

        errors: list[str] = []

        if not self.name.strip():
            errors.append(
                "continuity profile name cannot be empty"
            )

        if (
            self.missing_required_severity
            not in VALID_CONTINUITY_SEVERITIES
        ):
            errors.append(
                "missing_required_severity must be "
                "error, warning, or ignore"
            )

        groups = {
            "required_fields": (
                self.normalized_required_fields
            ),
            "optional_fields": (
                self.normalized_optional_fields
            ),
            "ignored_fields": (
                self.normalized_ignored_fields
            ),
            "strict_fields": (
                self.normalized_strict_fields
            ),
            "warning_fields": (
                self.normalized_warning_fields
            ),
            "allowed_change_fields": (
                self.normalized_allowed_change_fields
            ),
        }

        for group_name, values in groups.items():
            if any(
                not value
                for value in values
            ):
                errors.append(
                    f"{group_name} cannot contain "
                    "empty field names"
                )

            duplicates = _find_duplicates(
                values
            )

            if duplicates:
                errors.append(
                    f"{group_name} cannot contain "
                    "duplicate field names"
                )

        required = set(
            self.normalized_required_fields
        )

        optional = set(
            self.normalized_optional_fields
        )

        ignored = set(
            self.normalized_ignored_fields
        )

        strict_fields = set(
            self.normalized_strict_fields
        )

        warning_fields = set(
            self.normalized_warning_fields
        )

        allowed_changes = set(
            self.normalized_allowed_change_fields
        )

        if required & optional:
            errors.append(
                "continuity fields cannot be both "
                "required and optional"
            )

        active_without_ignored = (
            required
            | optional
            | strict_fields
            | warning_fields
        )

        if ignored & active_without_ignored:
            errors.append(
                "ignored continuity fields cannot also "
                "be active continuity fields"
            )

        if strict_fields & warning_fields:
            errors.append(
                "continuity fields cannot be both "
                "strict and warning-only"
            )

        if allowed_changes & strict_fields:
            errors.append(
                "allowed-change fields cannot also "
                "be strict continuity fields"
            )

        if allowed_changes & warning_fields:
            errors.append(
                "allowed-change fields cannot also "
                "be warning continuity fields"
            )

        if (
            allowed_changes
            - set(self.active_fields)
        ):
            errors.append(
                "allowed_change_fields must reference "
                "active continuity fields"
            )

        return errors

    def is_valid(self) -> bool:
        """Return True when the profile configuration is valid."""

        return not self.validate()

    def to_dict(self) -> dict[str, Any]:
        """Convert the normalized profile into serializable data."""

        return {
            "name": self.name,
            "required_fields": (
                self.normalized_required_fields
            ),
            "optional_fields": (
                self.normalized_optional_fields
            ),
            "ignored_fields": (
                self.normalized_ignored_fields
            ),
            "strict_fields": (
                self.normalized_strict_fields
            ),
            "warning_fields": (
                self.normalized_warning_fields
            ),
            "allowed_change_fields": (
                self.normalized_allowed_change_fields
            ),
            "strict": self.strict,
            "missing_required_severity": (
                self.missing_required_severity
            ),
        }


@dataclass(frozen=True)
class AdvancedContinuityIssue:
    """One structured advanced continuity issue."""

    issue_type: str
    field_name: str
    severity: str
    message: str

    previous_scene_id: int
    current_scene_id: int

    previous_value: Any = None
    current_value: Any = None

    def to_dict(self) -> dict[str, Any]:
        """Convert the issue into serializable data."""

        return asdict(self)


@dataclass
class ContinuityPairValidationResult:
    """Continuity validation result for one adjacent scene pair."""

    previous_scene_id: int
    current_scene_id: int

    issues: list[AdvancedContinuityIssue] = field(
        default_factory=list
    )

    @property
    def is_valid(self) -> bool:
        """
        Return True when the pair contains no error-level issues.

        Warning-level issues do not invalidate the pair.
        """

        return not any(
            issue.severity == "error"
            for issue in self.issues
        )

    @property
    def issue_count(self) -> int:
        return len(self.issues)

    @property
    def error_count(self) -> int:
        return sum(
            issue.severity == "error"
            for issue in self.issues
        )

    @property
    def warning_count(self) -> int:
        return sum(
            issue.severity == "warning"
            for issue in self.issues
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the pair result into serializable data."""

        return {
            "previous_scene_id": (
                self.previous_scene_id
            ),
            "current_scene_id": (
                self.current_scene_id
            ),
            "valid": self.is_valid,
            "issue_count": self.issue_count,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "issues": [
                issue.to_dict()
                for issue in self.issues
            ],
        }


@dataclass
class AdvancedContinuityValidationResult:
    """Project-level advanced continuity validation result."""

    scene_count: int
    checked_pairs: int
    profile: ContinuityProfile

    issues: list[AdvancedContinuityIssue] = field(
        default_factory=list
    )

    @property
    def is_valid(self) -> bool:
        """Return True when no error-level issue exists."""

        return not any(
            issue.severity == "error"
            for issue in self.issues
        )

    @property
    def issue_count(self) -> int:
        return len(self.issues)

    @property
    def error_count(self) -> int:
        return sum(
            issue.severity == "error"
            for issue in self.issues
        )

    @property
    def warning_count(self) -> int:
        return sum(
            issue.severity == "warning"
            for issue in self.issues
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert project validation into serializable data."""

        return {
            "summary": {
                "valid": self.is_valid,
                "scene_count": self.scene_count,
                "checked_pairs": self.checked_pairs,
                "issue_count": self.issue_count,
                "error_count": self.error_count,
                "warning_count": self.warning_count,
            },
            "profile": self.profile.to_dict(),
            "issues": [
                issue.to_dict()
                for issue in self.issues
            ],
        }


_MISSING = object()


def _get_scene_continuity_value(
    scene: Scene,
    field_name: str,
) -> Any:
    """
    Resolve a continuity value from either a native Scene field
    or the scene.continuity metadata dictionary.
    """

    normalized = normalize_continuity_field(
        field_name
    )

    native_values: dict[str, Any] = {
        "characters": scene.characters,
        "location": scene.location,
        "lighting": scene.lighting,
        "mood": scene.mood,
        "performance": scene.performance,
        "dialogue_or_vocals": (
            scene.dialogue_or_vocals
        ),
        "camera_shot": scene.camera.shot,
        "camera_movement": (
            scene.camera.movement
        ),
        "camera_lens": scene.camera.lens,
    }

    if normalized in native_values:
        return native_values[normalized]

    for key, value in scene.continuity.items():
        if (
            normalize_continuity_field(key)
            == normalized
        ):
            return value

    return _MISSING


def _value_is_missing(
    value: Any,
) -> bool:
    """Return True when a continuity value should be considered absent."""

    if value is _MISSING:
        return True

    if value is None:
        return True

    if (
        isinstance(value, str)
        and not value.strip()
    ):
        return True

    if (
        isinstance(
            value,
            (
                list,
                tuple,
                set,
                dict,
            ),
        )
        and not value
    ):
        return True

    return False


def _continuity_values_equal(
    field_name: str,
    previous_value: Any,
    current_value: Any,
) -> bool:
    """
    Compare continuity values.

    Character ordering is ignored because character identity
    continuity should not depend on list ordering.
    """

    if (
        field_name == "characters"
        and isinstance(
            previous_value,
            (list, tuple, set),
        )
        and isinstance(
            current_value,
            (list, tuple, set),
        )
    ):
        return {
            str(value)
            for value in previous_value
        } == {
            str(value)
            for value in current_value
        }

    return previous_value == current_value


def validate_continuity_pair(
    previous_scene: Scene,
    current_scene: Scene,
    profile: ContinuityProfile,
) -> ContinuityPairValidationResult:
    """
    Validate continuity between two adjacent cinematic scenes.
    """

    profile_errors = profile.validate()

    if profile_errors:
        raise ValueError(
            "Invalid continuity profile: "
            + "; ".join(profile_errors)
        )

    for scene in (
        previous_scene,
        current_scene,
    ):
        scene_errors = scene.validate()

        if scene_errors:
            raise ValueError(
                f"Invalid scene {scene.scene_id}: "
                + "; ".join(scene_errors)
            )

    required_fields = set(
        profile.normalized_required_fields
    )

    strict_fields = set(
        profile.normalized_strict_fields
    )

    warning_fields = set(
        profile.normalized_warning_fields
    )

    ignored_fields = set(
        profile.normalized_ignored_fields
    )

    allowed_change_fields = set(
        profile.normalized_allowed_change_fields
    )

    issues: list[AdvancedContinuityIssue] = []

    for field_name in profile.active_fields:
        if field_name in ignored_fields:
            continue

        previous_value = (
            _get_scene_continuity_value(
                previous_scene,
                field_name,
            )
        )

        current_value = (
            _get_scene_continuity_value(
                current_scene,
                field_name,
            )
        )

        previous_missing = (
            _value_is_missing(
                previous_value
            )
        )

        current_missing = (
            _value_is_missing(
                current_value
            )
        )

        is_required = (
            field_name in required_fields
        )

        is_strict_field = (
            field_name in strict_fields
        )

        if (
            previous_missing
            or current_missing
        ):
            if (
                is_required
                or is_strict_field
            ):
                if is_required:
                    severity = (
                        profile.missing_required_severity
                    )

                    issue_type = (
                        "missing_required_field"
                    )
                else:
                    severity = "error"

                    issue_type = (
                        "missing_strict_field"
                    )

                if severity != "ignore":
                    missing_scene_ids: list[int] = []

                    if previous_missing:
                        missing_scene_ids.append(
                            previous_scene.scene_id
                        )

                    if current_missing:
                        missing_scene_ids.append(
                            current_scene.scene_id
                        )

                    missing_text = ", ".join(
                        str(scene_id)
                        for scene_id
                        in missing_scene_ids
                    )

                    issues.append(
                        AdvancedContinuityIssue(
                            issue_type=issue_type,
                            field_name=field_name,
                            severity=severity,
                            previous_scene_id=(
                                previous_scene.scene_id
                            ),
                            current_scene_id=(
                                current_scene.scene_id
                            ),
                            previous_value=(
                                None
                                if previous_missing
                                else previous_value
                            ),
                            current_value=(
                                None
                                if current_missing
                                else current_value
                            ),
                            message=(
                                f"continuity field "
                                f"'{field_name}' is missing "
                                f"from scene(s): "
                                f"{missing_text}"
                            ),
                        )
                    )

            continue

        if _continuity_values_equal(
            field_name,
            previous_value,
            current_value,
        ):
            continue

        if (
            field_name
            in allowed_change_fields
        ):
            continue

        if field_name in warning_fields:
            severity = "warning"

        elif field_name in strict_fields:
            severity = "error"

        elif profile.strict:
            severity = "error"

        else:
            severity = "warning"

        issues.append(
            AdvancedContinuityIssue(
                issue_type="continuity_change",
                field_name=field_name,
                severity=severity,
                previous_scene_id=(
                    previous_scene.scene_id
                ),
                current_scene_id=(
                    current_scene.scene_id
                ),
                previous_value=previous_value,
                current_value=current_value,
                message=(
                    f"continuity field "
                    f"'{field_name}' changed between "
                    f"scene {previous_scene.scene_id} "
                    f"and scene {current_scene.scene_id}"
                ),
            )
        )

    return ContinuityPairValidationResult(
        previous_scene_id=(
            previous_scene.scene_id
        ),
        current_scene_id=(
            current_scene.scene_id
        ),
        issues=issues,
    )


def validate_project_continuity(
    scenes: list[Scene],
    profile: ContinuityProfile,
) -> AdvancedContinuityValidationResult:
    """
    Validate advanced continuity across an ordered scene sequence.

    Each scene is compared with the immediately preceding scene.
    """

    profile_errors = profile.validate()

    if profile_errors:
        raise ValueError(
            "Invalid continuity profile: "
            + "; ".join(profile_errors)
        )

    scene_ids = [
        scene.scene_id
        for scene in scenes
    ]

    if len(scene_ids) != len(set(scene_ids)):
        raise ValueError(
            "advanced continuity validation "
            "requires unique scene IDs"
        )

    for scene in scenes:
        scene_errors = scene.validate()

        if scene_errors:
            raise ValueError(
                f"Invalid scene {scene.scene_id}: "
                + "; ".join(scene_errors)
            )

    issues: list[AdvancedContinuityIssue] = []

    for index in range(
        1,
        len(scenes),
    ):
        pair_result = (
            validate_continuity_pair(
                scenes[index - 1],
                scenes[index],
                profile,
            )
        )

        issues.extend(
            pair_result.issues
        )

    return AdvancedContinuityValidationResult(
        scene_count=len(scenes),
        checked_pairs=max(
            0,
            len(scenes) - 1,
        ),
        profile=profile,
        issues=issues,
    )
