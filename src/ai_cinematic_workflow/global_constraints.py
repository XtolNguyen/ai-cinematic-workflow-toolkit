"""
Project-wide global cinematic constraints.

This module provides a platform-agnostic layer for production rules
that apply across an entire cinematic project.

It reuses the toolkit's existing negative-constraint normalization
and validation behavior rather than creating a separate negative
prompt system.
"""

from dataclasses import dataclass, field
from typing import Any

from .negative_validator import (
    normalize_constraint,
    validate_negative_constraints,
)
from .scene import Scene


def _normalize_unique(
    values: list[str],
) -> list[str]:
    """
    Normalize constraint values and remove duplicates
    while preserving their original order.
    """

    normalized: list[str] = []

    for value in values:
        item = normalize_constraint(
            value
        )

        if (
            item
            and item not in normalized
        ):
            normalized.append(
                item
            )

    return normalized


def _normalize_category_name(
    value: str,
) -> str:
    """
    Normalize a custom constraint-category name.

    Example:

        "Visual Effects" -> "visual_effects"
    """

    normalized = (
        value.strip()
        .lower()
        .replace("-", " ")
    )

    return "_".join(
        normalized.split()
    )


@dataclass
class GlobalConstraints:
    """
    Configurable project-wide cinematic constraints.

    These constraints describe production rules that should
    remain available across all scenes in a project.
    """

    name: str = "default"

    required_constraints: list[str] = field(
        default_factory=list
    )

    advisory_constraints: list[str] = field(
        default_factory=list
    )

    negative_constraints: list[str] = field(
        default_factory=list
    )

    prohibited_elements: list[str] = field(
        default_factory=list
    )

    character_identity_constraints: list[str] = field(
        default_factory=list
    )

    visual_style_constraints: list[str] = field(
        default_factory=list
    )

    camera_constraints: list[str] = field(
        default_factory=list
    )

    environment_constraints: list[str] = field(
        default_factory=list
    )

    custom_constraints: dict[
        str,
        list[str],
    ] = field(
        default_factory=dict
    )

    strict: bool = True

    @property
    def normalized_required_constraints(
        self,
    ) -> list[str]:
        return _normalize_unique(
            self.required_constraints
        )

    @property
    def normalized_advisory_constraints(
        self,
    ) -> list[str]:
        return _normalize_unique(
            self.advisory_constraints
        )

    @property
    def normalized_negative_constraints(
        self,
    ) -> list[str]:
        return _normalize_unique(
            self.negative_constraints
        )

    @property
    def normalized_prohibited_elements(
        self,
    ) -> list[str]:
        return _normalize_unique(
            self.prohibited_elements
        )

    @property
    def normalized_character_identity_constraints(
        self,
    ) -> list[str]:
        return _normalize_unique(
            self.character_identity_constraints
        )

    @property
    def normalized_visual_style_constraints(
        self,
    ) -> list[str]:
        return _normalize_unique(
            self.visual_style_constraints
        )

    @property
    def normalized_camera_constraints(
        self,
    ) -> list[str]:
        return _normalize_unique(
            self.camera_constraints
        )

    @property
    def normalized_environment_constraints(
        self,
    ) -> list[str]:
        return _normalize_unique(
            self.environment_constraints
        )

    @property
    def normalized_custom_constraints(
        self,
    ) -> dict[str, list[str]]:
        """
        Return normalized custom constraint categories.
        """

        result: dict[
            str,
            list[str],
        ] = {}

        for category, values in (
            self.custom_constraints.items()
        ):
            normalized_category = (
                _normalize_category_name(
                    category
                )
            )

            if normalized_category:
                result[
                    normalized_category
                ] = _normalize_unique(
                    values
                )

        return result

    @property
    def resolved_global_negative_constraints(
        self,
    ) -> list[str]:
        """
        Return project-wide constraints that should participate
        in negative-prompt resolution.

        Prohibited elements are treated as negative constraints
        while remaining separately represented in structured data.
        """

        return _normalize_unique(
            self.normalized_negative_constraints
            + self.normalized_prohibited_elements
        )

    def validate(self) -> list[str]:
        """Validate the GlobalConstraints configuration."""

        errors: list[str] = []

        if not self.name.strip():
            errors.append(
                "global constraints name cannot be empty"
            )

        groups: dict[
            str,
            list[str],
        ] = {
            "required_constraints": (
                self.required_constraints
            ),
            "advisory_constraints": (
                self.advisory_constraints
            ),
            "negative_constraints": (
                self.negative_constraints
            ),
            "prohibited_elements": (
                self.prohibited_elements
            ),
            "character_identity_constraints": (
                self.character_identity_constraints
            ),
            "visual_style_constraints": (
                self.visual_style_constraints
            ),
            "camera_constraints": (
                self.camera_constraints
            ),
            "environment_constraints": (
                self.environment_constraints
            ),
        }

        for group_name, values in groups.items():
            for value in values:
                if not normalize_constraint(
                    value
                ):
                    errors.append(
                        f"{group_name} cannot contain "
                        "empty constraints"
                    )
                    break

        normalized_custom_names: list[
            str
        ] = []

        for (
            category,
            values,
        ) in self.custom_constraints.items():
            normalized_category = (
                _normalize_category_name(
                    category
                )
            )

            if not normalized_category:
                errors.append(
                    "custom constraint category "
                    "name cannot be empty"
                )

                continue

            if (
                normalized_category
                in normalized_custom_names
            ):
                errors.append(
                    "custom constraint categories "
                    "cannot normalize to duplicate names"
                )

            normalized_custom_names.append(
                normalized_category
            )

            if not values:
                errors.append(
                    "custom constraint categories "
                    "must contain at least one constraint"
                )

                continue

            for value in values:
                if not normalize_constraint(
                    value
                ):
                    errors.append(
                        f"custom constraint category "
                        f"'{normalized_category}' cannot "
                        "contain empty constraints"
                    )
                    break

        required = set(
            self.normalized_required_constraints
        )

        advisory = set(
            self.normalized_advisory_constraints
        )

        negative_or_prohibited = set(
            self.resolved_global_negative_constraints
        )

        if required & advisory:
            errors.append(
                "constraints cannot be both required "
                "and advisory"
            )

        if required & negative_or_prohibited:
            errors.append(
                "required constraints cannot also be "
                "negative or prohibited constraints"
            )

        return errors

    def is_valid(self) -> bool:
        """Return True when configuration validation passes."""

        return not self.validate()

    def to_dict(self) -> dict[str, Any]:
        """Convert normalized global constraints into data."""

        return {
            "name": self.name,
            "strict": self.strict,
            "required_constraints": (
                self.normalized_required_constraints
            ),
            "advisory_constraints": (
                self.normalized_advisory_constraints
            ),
            "negative_constraints": (
                self.normalized_negative_constraints
            ),
            "prohibited_elements": (
                self.normalized_prohibited_elements
            ),
            "character_identity_constraints": (
                self.normalized_character_identity_constraints
            ),
            "visual_style_constraints": (
                self.normalized_visual_style_constraints
            ),
            "camera_constraints": (
                self.normalized_camera_constraints
            ),
            "environment_constraints": (
                self.normalized_environment_constraints
            ),
            "custom_constraints": (
                self.normalized_custom_constraints
            ),
        }


@dataclass(frozen=True)
class GlobalConstraintIssue:
    """One structured project constraint issue or warning."""

    issue_type: str
    severity: str
    message: str

    category: str | None = None
    scene_id: int | None = None
    value: Any = None

    def to_dict(self) -> dict[str, Any]:
        """Convert the issue into serializable data."""

        return {
            "issue_type": self.issue_type,
            "severity": self.severity,
            "message": self.message,
            "category": self.category,
            "scene_id": self.scene_id,
            "value": self.value,
        }


@dataclass
class ResolvedSceneConstraints:
    """
    Resolved global and scene-specific constraints
    for one cinematic scene.
    """

    scene_id: int

    global_negative_constraints: list[str]
    scene_negative_constraints: list[str]
    resolved_negative_constraints: list[str]

    issues: list[GlobalConstraintIssue] = field(
        default_factory=list
    )

    @property
    def warning_count(self) -> int:
        """Return the number of warning-level issues."""

        return sum(
            issue.severity == "warning"
            for issue in self.issues
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the scene resolution into data."""

        return {
            "scene_id": self.scene_id,
            "global_negative_constraints": list(
                self.global_negative_constraints
            ),
            "scene_negative_constraints": list(
                self.scene_negative_constraints
            ),
            "resolved_negative_constraints": list(
                self.resolved_negative_constraints
            ),
            "summary": {
                "global_negative_count": len(
                    self.global_negative_constraints
                ),
                "scene_negative_count": len(
                    self.scene_negative_constraints
                ),
                "resolved_negative_count": len(
                    self.resolved_negative_constraints
                ),
                "warning_count": (
                    self.warning_count
                ),
            },
            "issues": [
                issue.to_dict()
                for issue in self.issues
            ],
        }


@dataclass
class GlobalConstraintResolution:
    """Project-level global constraint resolution result."""

    constraints: GlobalConstraints

    scene_results: list[
        ResolvedSceneConstraints
    ] = field(
        default_factory=list
    )

    issues: list[
        GlobalConstraintIssue
    ] = field(
        default_factory=list
    )

    @property
    def scene_count(self) -> int:
        """Return the number of resolved scenes."""

        return len(
            self.scene_results
        )

    @property
    def issue_count(self) -> int:
        """Return total project-level issue count."""

        return len(
            self.issues
        ) + sum(
            len(result.issues)
            for result in self.scene_results
        )

    @property
    def warning_count(self) -> int:
        """Return total warning count."""

        return sum(
            issue.severity == "warning"
            for issue in self.issues
        ) + sum(
            result.warning_count
            for result in self.scene_results
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert project constraint resolution into data."""

        return {
            "summary": {
                "scene_count": self.scene_count,
                "issue_count": self.issue_count,
                "warning_count": self.warning_count,
            },
            "constraints": (
                self.constraints.to_dict()
            ),
            "scene_results": [
                result.to_dict()
                for result in self.scene_results
            ],
            "issues": [
                issue.to_dict()
                for issue in self.issues
            ],
        }


def resolve_scene_constraints(
    scene: Scene,
    constraints: GlobalConstraints,
) -> ResolvedSceneConstraints:
    """
    Resolve project-wide negative constraints with one Scene.

    The original Scene object is never mutated.
    """

    constraint_errors = (
        constraints.validate()
    )

    if constraint_errors:
        raise ValueError(
            "Invalid global constraints: "
            + "; ".join(
                constraint_errors
            )
        )

    scene_errors = scene.validate()

    if scene_errors:
        raise ValueError(
            f"Invalid scene {scene.scene_id}: "
            + "; ".join(
                scene_errors
            )
        )

    global_result = (
        validate_negative_constraints(
            constraints.resolved_global_negative_constraints
        )
    )

    scene_result = (
        validate_negative_constraints(
            list(
                scene.negative_constraints
            )
        )
    )

    merged_result = (
        validate_negative_constraints(
            global_result.constraints
            + scene_result.constraints
        )
    )

    issues: list[
        GlobalConstraintIssue
    ] = []

    for warning in global_result.warnings:
        issues.append(
            GlobalConstraintIssue(
                issue_type=(
                    "global_negative_warning"
                ),
                severity="warning",
                category="negative_constraints",
                scene_id=scene.scene_id,
                message=warning,
            )
        )

    for warning in scene_result.warnings:
        issues.append(
            GlobalConstraintIssue(
                issue_type=(
                    "scene_negative_warning"
                ),
                severity="warning",
                category="negative_constraints",
                scene_id=scene.scene_id,
                message=warning,
            )
        )

    for warning in merged_result.warnings:
        issue = GlobalConstraintIssue(
            issue_type=(
                "resolved_negative_warning"
            ),
            severity="warning",
            category="negative_constraints",
            scene_id=scene.scene_id,
            message=warning,
        )

        if issue not in issues:
            issues.append(
                issue
            )

    return ResolvedSceneConstraints(
        scene_id=scene.scene_id,
        global_negative_constraints=list(
            global_result.constraints
        ),
        scene_negative_constraints=list(
            scene_result.constraints
        ),
        resolved_negative_constraints=list(
            merged_result.constraints
        ),
        issues=issues,
    )


def resolve_project_constraints(
    scenes: list[Scene],
    constraints: GlobalConstraints,
) -> GlobalConstraintResolution:
    """
    Resolve global constraints across an ordered cinematic project.

    Original Scene objects remain unchanged.
    """

    constraint_errors = (
        constraints.validate()
    )

    if constraint_errors:
        raise ValueError(
            "Invalid global constraints: "
            + "; ".join(
                constraint_errors
            )
        )

    scene_ids = [
        scene.scene_id
        for scene in scenes
    ]

    if len(scene_ids) != len(set(scene_ids)):
        raise ValueError(
            "global constraint resolution "
            "requires unique scene IDs"
        )

    scene_results: list[
        ResolvedSceneConstraints
    ] = []

    for scene in scenes:
        scene_results.append(
            resolve_scene_constraints(
                scene,
                constraints,
            )
        )

    return GlobalConstraintResolution(
        constraints=constraints,
        scene_results=scene_results,
    )
