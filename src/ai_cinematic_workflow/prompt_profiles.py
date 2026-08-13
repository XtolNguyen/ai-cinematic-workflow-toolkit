"""
Reusable cinematic prompt profiles.

This module defines platform-agnostic prompt configuration and
profile resolution.

Prompt profiles control which structured cinematic components are
available to future prompt-generation layers. They do not render
final prompt strings and do not replace the existing prompt builder.
"""

import json
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any


VALID_PROMPT_COMPONENTS = {
    "characters",
    "location",
    "camera",
    "performance",
    "lighting",
    "mood",
    "dialogue_or_vocals",
    "continuity",
    "negative_constraints",
    "global_constraints",
}


def normalize_prompt_component(
    value: str,
) -> str:
    """
    Normalize a prompt-component name.

    Examples:

        "Dialogue Or Vocals"
        -> "dialogue_or_vocals"

        "negative-constraints"
        -> "negative_constraints"
    """

    normalized = (
        value.strip()
        .lower()
        .replace("-", " ")
    )

    return "_".join(
        normalized.split()
    )


def _normalize_unique_components(
    values: list[str],
) -> list[str]:
    """
    Normalize component names and remove duplicates
    while preserving their original order.
    """

    result: list[str] = []

    for value in values:
        normalized = (
            normalize_prompt_component(
                value
            )
        )

        if (
            normalized
            and normalized not in result
        ):
            result.append(
                normalized
            )

    return result


def _find_unknown_components(
    values: list[str],
) -> list[str]:
    """Return normalized components outside the core registry."""

    return [
        value
        for value in values
        if value not in VALID_PROMPT_COMPONENTS
    ]


def _merge_config(
    base: dict[str, Any],
    override: dict[str, Any],
) -> dict[str, Any]:
    """
    Recursively merge custom prompt configuration.

    Neither source dictionary is mutated.
    """

    result = deepcopy(
        base
    )

    for key, value in override.items():
        if (
            key in result
            and isinstance(
                result[key],
                dict,
            )
            and isinstance(
                value,
                dict,
            )
        ):
            result[key] = _merge_config(
                result[key],
                value,
            )
        else:
            result[key] = deepcopy(
                value
            )

    return result


def _validate_custom_config(
    custom_config: dict[str, Any],
) -> list[str]:
    """
    Validate custom prompt configuration.

    Custom configuration must use non-empty string keys and
    JSON-serializable values.
    """

    errors: list[str] = []

    for key in custom_config:
        if (
            not isinstance(key, str)
            or not key.strip()
        ):
            errors.append(
                "custom prompt configuration keys "
                "must be non-empty strings"
            )
            break

    try:
        json.dumps(
            custom_config,
            ensure_ascii=False,
        )
    except (
        TypeError,
        ValueError,
    ):
        errors.append(
            "custom prompt configuration "
            "must be JSON serializable"
        )

    return errors


@dataclass
class PromptProfile:
    """
    Reusable platform-agnostic prompt configuration.

    enabled_components:
        Components made available to future prompt builders.

    disabled_components:
        Components explicitly excluded from prompt construction.

    strict_unknown_components:
        When True, unknown components are invalid.
        When False, unknown components are preserved and reported
        as warnings during resolution.

    custom_config:
        Serializable configuration values for future prompt layers.
    """

    name: str = "default"

    enabled_components: list[str] = field(
        default_factory=list
    )

    disabled_components: list[str] = field(
        default_factory=list
    )

    strict_unknown_components: bool = True

    custom_config: dict[
        str,
        Any,
    ] = field(
        default_factory=dict
    )

    @property
    def normalized_enabled_components(
        self,
    ) -> list[str]:
        """Return canonical enabled component names."""

        return _normalize_unique_components(
            self.enabled_components
        )

    @property
    def normalized_disabled_components(
        self,
    ) -> list[str]:
        """Return canonical disabled component names."""

        return _normalize_unique_components(
            self.disabled_components
        )

    @property
    def unknown_enabled_components(
        self,
    ) -> list[str]:
        """Return enabled components outside the core registry."""

        return _find_unknown_components(
            self.normalized_enabled_components
        )

    @property
    def unknown_disabled_components(
        self,
    ) -> list[str]:
        """Return disabled components outside the core registry."""

        return _find_unknown_components(
            self.normalized_disabled_components
        )

    def validate(self) -> list[str]:
        """Validate the prompt profile configuration."""

        errors: list[str] = []

        if not self.name.strip():
            errors.append(
                "prompt profile name cannot be empty"
            )

        for value in self.enabled_components:
            if not normalize_prompt_component(
                value
            ):
                errors.append(
                    "enabled_components cannot contain "
                    "empty component names"
                )
                break

        for value in self.disabled_components:
            if not normalize_prompt_component(
                value
            ):
                errors.append(
                    "disabled_components cannot contain "
                    "empty component names"
                )
                break

        enabled = set(
            self.normalized_enabled_components
        )

        disabled = set(
            self.normalized_disabled_components
        )

        if enabled & disabled:
            errors.append(
                "prompt components cannot be both "
                "enabled and disabled"
            )

        if self.strict_unknown_components:
            unknown = (
                self.unknown_enabled_components
                + self.unknown_disabled_components
            )

            if unknown:
                errors.append(
                    "unknown prompt components are not "
                    "allowed in strict mode: "
                    + ", ".join(
                        sorted(
                            set(unknown)
                        )
                    )
                )

        errors.extend(
            _validate_custom_config(
                self.custom_config
            )
        )

        return errors

    def is_valid(self) -> bool:
        """Return True when the profile configuration is valid."""

        return not self.validate()

    def to_dict(self) -> dict[str, Any]:
        """Convert the normalized profile into serializable data."""

        return {
            "name": self.name,
            "enabled_components": (
                self.normalized_enabled_components
            ),
            "disabled_components": (
                self.normalized_disabled_components
            ),
            "strict_unknown_components": (
                self.strict_unknown_components
            ),
            "custom_config": deepcopy(
                self.custom_config
            ),
        }


@dataclass(frozen=True)
class PromptProfileIssue:
    """One structured profile-resolution issue or warning."""

    issue_type: str
    severity: str
    message: str

    component: str | None = None
    profile_name: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert the issue into serializable data."""

        return {
            "issue_type": self.issue_type,
            "severity": self.severity,
            "message": self.message,
            "component": self.component,
            "profile_name": self.profile_name,
        }


@dataclass
class ResolvedPromptProfile:
    """
    Fully resolved reusable prompt configuration.

    This result may combine:

    - an optional base profile
    - a child profile
    - runtime enable/disable overrides
    - custom configuration overrides
    """

    name: str

    source_profile_name: str
    base_profile_name: str | None

    enabled_components: list[str]
    disabled_components: list[str]

    strict_unknown_components: bool

    custom_config: dict[
        str,
        Any,
    ] = field(
        default_factory=dict
    )

    issues: list[
        PromptProfileIssue
    ] = field(
        default_factory=list
    )

    @property
    def warning_count(self) -> int:
        """Return warning-level resolution issue count."""

        return sum(
            issue.severity == "warning"
            for issue in self.issues
        )

    @property
    def error_count(self) -> int:
        """Return error-level resolution issue count."""

        return sum(
            issue.severity == "error"
            for issue in self.issues
        )

    @property
    def is_valid(self) -> bool:
        """Return True when no error-level issue exists."""

        return self.error_count == 0

    def is_enabled(
        self,
        component: str,
    ) -> bool:
        """Return whether one component is enabled."""

        normalized = (
            normalize_prompt_component(
                component
            )
        )

        return (
            normalized
            in self.enabled_components
        )

    def is_disabled(
        self,
        component: str,
    ) -> bool:
        """Return whether one component is disabled."""

        normalized = (
            normalize_prompt_component(
                component
            )
        )

        return (
            normalized
            in self.disabled_components
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the resolved profile into serializable data."""

        return {
            "summary": {
                "valid": self.is_valid,
                "enabled_component_count": len(
                    self.enabled_components
                ),
                "disabled_component_count": len(
                    self.disabled_components
                ),
                "warning_count": self.warning_count,
                "error_count": self.error_count,
            },
            "name": self.name,
            "source_profile_name": (
                self.source_profile_name
            ),
            "base_profile_name": (
                self.base_profile_name
            ),
            "enabled_components": list(
                self.enabled_components
            ),
            "disabled_components": list(
                self.disabled_components
            ),
            "strict_unknown_components": (
                self.strict_unknown_components
            ),
            "custom_config": deepcopy(
                self.custom_config
            ),
            "issues": [
                issue.to_dict()
                for issue in self.issues
            ],
        }


def _validate_override_components(
    values: list[str],
    *,
    field_name: str,
    strict_unknown_components: bool,
) -> list[str]:
    """
    Normalize and validate runtime component overrides.
    """

    normalized = (
        _normalize_unique_components(
            values
        )
    )

    for value in values:
        if not normalize_prompt_component(
            value
        ):
            raise ValueError(
                f"{field_name} cannot contain "
                "empty component names"
            )

    unknown = (
        _find_unknown_components(
            normalized
        )
    )

    if (
        strict_unknown_components
        and unknown
    ):
        raise ValueError(
            "unknown prompt components are not "
            "allowed in strict mode: "
            + ", ".join(
                sorted(
                    set(unknown)
                )
            )
        )

    return normalized


def _append_unknown_component_warnings(
    issues: list[PromptProfileIssue],
    components: list[str],
    *,
    profile_name: str,
) -> None:
    """
    Add warning issues for permissively accepted
    unknown prompt components.
    """

    for component in (
        _find_unknown_components(
            components
        )
    ):
        issue = PromptProfileIssue(
            issue_type=(
                "unknown_prompt_component"
            ),
            severity="warning",
            component=component,
            profile_name=profile_name,
            message=(
                f"Unknown prompt component "
                f"'{component}' was preserved "
                "because strict unknown-component "
                "handling is disabled."
            ),
        )

        if issue not in issues:
            issues.append(
                issue
            )


def resolve_prompt_profile(
    profile: PromptProfile,
    *,
    base_profile: PromptProfile | None = None,
    enable_overrides: list[str] | None = None,
    disable_overrides: list[str] | None = None,
    custom_config_overrides: dict[
        str,
        Any,
    ] | None = None,
    resolved_name: str | None = None,
) -> ResolvedPromptProfile:
    """
    Resolve a reusable prompt profile.

    Resolution order:

    1. Optional base profile
    2. Child/source profile
    3. Runtime enable overrides
    4. Runtime disable overrides
    5. Custom configuration overrides

    Later layers take precedence.

    Source profiles are never mutated.
    """

    profile_errors = (
        profile.validate()
    )

    if profile_errors:
        raise ValueError(
            "Invalid prompt profile: "
            + "; ".join(
                profile_errors
            )
        )

    if base_profile is not None:
        base_errors = (
            base_profile.validate()
        )

        if base_errors:
            raise ValueError(
                "Invalid base prompt profile: "
                + "; ".join(
                    base_errors
                )
            )

        if (
            base_profile is profile
        ):
            raise ValueError(
                "a prompt profile cannot inherit "
                "from itself"
            )

    enable_overrides = list(
        enable_overrides or []
    )

    disable_overrides = list(
        disable_overrides or []
    )

    normalized_enable_overrides = (
        _validate_override_components(
            enable_overrides,
            field_name="enable_overrides",
            strict_unknown_components=(
                profile.strict_unknown_components
            ),
        )
    )

    normalized_disable_overrides = (
        _validate_override_components(
            disable_overrides,
            field_name="disable_overrides",
            strict_unknown_components=(
                profile.strict_unknown_components
            ),
        )
    )

    override_conflicts = (
        set(
            normalized_enable_overrides
        )
        & set(
            normalized_disable_overrides
        )
    )

    if override_conflicts:
        raise ValueError(
            "prompt components cannot be both "
            "enabled and disabled by overrides: "
            + ", ".join(
                sorted(
                    override_conflicts
                )
            )
        )

    if custom_config_overrides is None:
        custom_config_overrides = {}

    custom_override_errors = (
        _validate_custom_config(
            custom_config_overrides
        )
    )

    if custom_override_errors:
        raise ValueError(
            "Invalid custom prompt configuration "
            "overrides: "
            + "; ".join(
                custom_override_errors
            )
        )

    enabled: list[str] = []

    disabled: list[str] = []

    custom_config: dict[
        str,
        Any,
    ] = {}

    issues: list[
        PromptProfileIssue
    ] = []

    if base_profile is not None:
        enabled = list(
            base_profile.normalized_enabled_components
        )

        disabled = list(
            base_profile.normalized_disabled_components
        )

        custom_config = deepcopy(
            base_profile.custom_config
        )

        if not base_profile.strict_unknown_components:
            _append_unknown_component_warnings(
                issues,
                enabled + disabled,
                profile_name=base_profile.name,
            )

    for component in (
        profile.normalized_enabled_components
    ):
        if component in disabled:
            disabled.remove(
                component
            )

        if component not in enabled:
            enabled.append(
                component
            )

    for component in (
        profile.normalized_disabled_components
    ):
        if component in enabled:
            enabled.remove(
                component
            )

        if component not in disabled:
            disabled.append(
                component
            )

    custom_config = _merge_config(
        custom_config,
        profile.custom_config,
    )

    for component in (
        normalized_enable_overrides
    ):
        if component in disabled:
            disabled.remove(
                component
            )

        if component not in enabled:
            enabled.append(
                component
            )

    for component in (
        normalized_disable_overrides
    ):
        if component in enabled:
            enabled.remove(
                component
            )

        if component not in disabled:
            disabled.append(
                component
            )

    custom_config = _merge_config(
        custom_config,
        custom_config_overrides,
    )

    if not profile.strict_unknown_components:
        _append_unknown_component_warnings(
            issues,
            (
                profile.normalized_enabled_components
                + profile.normalized_disabled_components
                + normalized_enable_overrides
                + normalized_disable_overrides
            ),
            profile_name=profile.name,
        )

    return ResolvedPromptProfile(
        name=(
            resolved_name.strip()
            if (
                resolved_name is not None
                and resolved_name.strip()
            )
            else profile.name
        ),
        source_profile_name=profile.name,
        base_profile_name=(
            base_profile.name
            if base_profile is not None
            else None
        ),
        enabled_components=enabled,
        disabled_components=disabled,
        strict_unknown_components=(
            profile.strict_unknown_components
        ),
        custom_config=custom_config,
        issues=issues,
    )
