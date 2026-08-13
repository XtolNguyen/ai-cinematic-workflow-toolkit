"""
Platform-agnostic enhanced project export configuration.

This module defines reusable export options and a canonical export
manifest for cinematic projects.

It does not perform JSON export itself and does not contain
provider-specific WAN, Veo, Kling, or other adapter behavior.
"""

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any


PROJECT_EXPORT_SECTION_ORDER = (
    "project",
    "timeline",
    "workflow",
    "duration_validation",
    "continuity_validation",
    "global_constraints",
    "prompt_profile",
    "structured_prompts",
)


VALID_PROJECT_EXPORT_SECTIONS = set(
    PROJECT_EXPORT_SECTION_ORDER
)


OPTIONAL_PROJECT_EXPORT_SECTIONS = (
    "duration_validation",
    "continuity_validation",
    "global_constraints",
    "prompt_profile",
    "structured_prompts",
)


def normalize_export_section(
    value: str,
) -> str:
    """
    Normalize an export-section identifier.

    Examples:

        "Structured Prompts"
        -> "structured_prompts"

        "duration-validation"
        -> "duration_validation"
    """

    return "_".join(
        value.strip()
        .lower()
        .replace("-", " ")
        .split()
    )


def _normalize_unique_sections(
    values: list[str],
) -> list[str]:
    """
    Normalize and deduplicate section identifiers while
    preserving first-seen order.
    """

    result: list[str] = []

    for value in values:
        normalized = normalize_export_section(
            value
        )

        if (
            normalized
            and normalized not in result
        ):
            result.append(
                normalized
            )

    return result


def _canonical_sort(
    values: list[str],
) -> list[str]:
    """Return section identifiers in canonical export order."""

    normalized = _normalize_unique_sections(
        values
    )

    order_map = {
        section: index
        for index, section in enumerate(
            PROJECT_EXPORT_SECTION_ORDER
        )
    }

    return sorted(
        normalized,
        key=lambda section: order_map[
            section
        ],
    )


@dataclass(frozen=True)
class ProjectExportOptions:
    """
    Reusable named configuration for enhanced project export.

    Timeline and workflow remain enabled by default because
    they are part of the existing project exporter behavior.

    Optional production layers are disabled by default and can
    be explicitly enabled when enhanced export behavior is used.
    """

    name: str = "default"

    include_timeline: bool = True
    include_workflow: bool = True

    include_duration_validation: bool = False
    include_continuity_validation: bool = False
    include_global_constraints: bool = False
    include_prompt_profile: bool = False
    include_structured_prompts: bool = False

    include_empty_prompt_sections: bool = False

    def validate(self) -> list[str]:
        """Validate export configuration."""

        errors: list[str] = []

        if not self.name.strip():
            errors.append(
                "project export options name "
                "cannot be empty"
            )

        if (
            self.include_empty_prompt_sections
            and not self.include_structured_prompts
        ):
            errors.append(
                "include_structured_prompts must be True "
                "when include_empty_prompt_sections is enabled"
            )

        return errors

    @property
    def is_valid(self) -> bool:
        """Return True when configuration passes validation."""

        return not self.validate()

    @property
    def requested_sections(
        self,
    ) -> list[str]:
        """
        Return canonical sections requested by this
        export configuration.

        The project section is always present.
        """

        sections = [
            "project",
        ]

        if self.include_timeline:
            sections.append(
                "timeline"
            )

        if self.include_workflow:
            sections.append(
                "workflow"
            )

        if self.include_duration_validation:
            sections.append(
                "duration_validation"
            )

        if self.include_continuity_validation:
            sections.append(
                "continuity_validation"
            )

        if self.include_global_constraints:
            sections.append(
                "global_constraints"
            )

        if self.include_prompt_profile:
            sections.append(
                "prompt_profile"
            )

        if self.include_structured_prompts:
            sections.append(
                "structured_prompts"
            )

        return _canonical_sort(
            sections
        )

    @property
    def excluded_sections(
        self,
    ) -> list[str]:
        """
        Return canonical sections disabled by this
        configuration.
        """

        requested = set(
            self.requested_sections
        )

        return [
            section
            for section in PROJECT_EXPORT_SECTION_ORDER
            if section not in requested
        ]

    def to_dict(self) -> dict[str, Any]:
        """Convert export configuration into portable data."""

        return {
            "name": self.name,
            "include_timeline": (
                self.include_timeline
            ),
            "include_workflow": (
                self.include_workflow
            ),
            "include_duration_validation": (
                self.include_duration_validation
            ),
            "include_continuity_validation": (
                self.include_continuity_validation
            ),
            "include_global_constraints": (
                self.include_global_constraints
            ),
            "include_prompt_profile": (
                self.include_prompt_profile
            ),
            "include_structured_prompts": (
                self.include_structured_prompts
            ),
            "include_empty_prompt_sections": (
                self.include_empty_prompt_sections
            ),
            "requested_sections": list(
                self.requested_sections
            ),
            "excluded_sections": list(
                self.excluded_sections
            ),
        }


@dataclass(frozen=True)
class OmittedExportSection:
    """
    One canonical project export section not present
    in the completed export.
    """

    section_id: str
    reason: str

    def validate(self) -> list[str]:
        """Validate omission metadata."""

        errors: list[str] = []

        normalized = normalize_export_section(
            self.section_id
        )

        if (
            normalized
            not in VALID_PROJECT_EXPORT_SECTIONS
        ):
            errors.append(
                "unknown project export section: "
                + normalized
            )

        if not self.reason.strip():
            errors.append(
                "omitted export section reason "
                "cannot be empty"
            )

        return errors

    @property
    def is_valid(self) -> bool:
        """Return True when omission metadata is valid."""

        return not self.validate()

    def to_dict(self) -> dict[str, str]:
        """Convert omission metadata into portable data."""

        return {
            "section_id": (
                normalize_export_section(
                    self.section_id
                )
            ),
            "reason": self.reason,
        }


@dataclass
class ProjectExportManifest:
    """
    Canonical manifest describing one enhanced project export.

    The manifest reports what was actually included, what was
    omitted, the reusable export configuration, and which optional
    production systems are active in the completed export.
    """

    export_name: str

    included_sections: list[str] = field(
        default_factory=list
    )

    omitted_sections: list[
        OmittedExportSection
    ] = field(
        default_factory=list
    )

    configuration: dict[
        str,
        Any,
    ] = field(
        default_factory=dict
    )

    @property
    def active_optional_systems(
        self,
    ) -> list[str]:
        """Return optional production layers included in export."""

        included = set(
            self.included_sections
        )

        return [
            section
            for section in OPTIONAL_PROJECT_EXPORT_SECTIONS
            if section in included
        ]

    @property
    def section_count(self) -> int:
        """Return number of included export sections."""

        return len(
            self.included_sections
        )

    @property
    def omitted_section_count(self) -> int:
        """Return number of omitted export sections."""

        return len(
            self.omitted_sections
        )

    def validate(self) -> list[str]:
        """Validate the completed export manifest."""

        errors: list[str] = []

        if not self.export_name.strip():
            errors.append(
                "project export manifest name "
                "cannot be empty"
            )

        normalized_included = (
            _normalize_unique_sections(
                self.included_sections
            )
        )

        unknown = [
            section
            for section in normalized_included
            if (
                section
                not in VALID_PROJECT_EXPORT_SECTIONS
            )
        ]

        for section in unknown:
            errors.append(
                "unknown included export section: "
                + section
            )

        if (
            len(normalized_included)
            != len(self.included_sections)
        ):
            errors.append(
                "project export manifest cannot contain "
                "duplicate included sections"
            )

        if (
            normalized_included
            and "project"
            not in normalized_included
        ):
            errors.append(
                "project export manifest must include "
                "the project section"
            )

        known_included = [
            section
            for section in normalized_included
            if (
                section
                in VALID_PROJECT_EXPORT_SECTIONS
            )
        ]

        if (
            known_included
            != _canonical_sort(
                known_included
            )
        ):
            errors.append(
                "included export sections must use "
                "deterministic canonical ordering"
            )

        omitted_ids: list[str] = []

        for item in self.omitted_sections:
            item_errors = item.validate()

            if item_errors:
                errors.extend(
                    [
                        "omitted section: "
                        + error
                        for error in item_errors
                    ]
                )

            normalized = (
                normalize_export_section(
                    item.section_id
                )
            )

            omitted_ids.append(
                normalized
            )

        if (
            len(omitted_ids)
            != len(set(omitted_ids))
        ):
            errors.append(
                "project export manifest cannot contain "
                "duplicate omitted sections"
            )

        overlap = set(
            normalized_included
        ).intersection(
            omitted_ids
        )

        if overlap:
            errors.append(
                "project export sections cannot be both "
                "included and omitted: "
                + ", ".join(
                    sorted(
                        overlap
                    )
                )
            )

        return errors

    @property
    def is_valid(self) -> bool:
        """Return True when manifest passes validation."""

        return not self.validate()

    def to_dict(self) -> dict[str, Any]:
        """Convert manifest into JSON-compatible data."""

        return {
            "summary": {
                "valid": self.is_valid,
                "export_name": self.export_name,
                "section_count": (
                    self.section_count
                ),
                "omitted_section_count": (
                    self.omitted_section_count
                ),
                "active_optional_system_count": len(
                    self.active_optional_systems
                ),
            },
            "export_name": self.export_name,
            "included_sections": list(
                self.included_sections
            ),
            "omitted_sections": [
                item.to_dict()
                for item in self.omitted_sections
            ],
            "active_optional_systems": list(
                self.active_optional_systems
            ),
            "configuration": deepcopy(
                self.configuration
            ),
        }


def build_project_export_manifest(
    options: ProjectExportOptions,
    *,
    included_sections: list[str],
    omission_reasons: dict[
        str,
        str,
    ] | None = None,
) -> ProjectExportManifest:
    """
    Build a deterministic canonical manifest for an
    enhanced cinematic project export.

    included_sections describes sections that were actually
    produced by the exporter.

    omission_reasons may provide explicit reasons for absent
    canonical sections. Missing reasons default to "not_included".
    """

    option_errors = options.validate()

    if option_errors:
        raise ValueError(
            "Invalid project export options: "
            + "; ".join(
                option_errors
            )
        )

    normalized = (
        _normalize_unique_sections(
            included_sections
        )
    )

    unknown = [
        section
        for section in normalized
        if (
            section
            not in VALID_PROJECT_EXPORT_SECTIONS
        )
    ]

    if unknown:
        raise ValueError(
            "Unknown included export sections: "
            + ", ".join(
                unknown
            )
        )

    if (
        len(normalized)
        != len(included_sections)
    ):
        raise ValueError(
            "included_sections cannot contain "
            "duplicates"
        )

    if "project" not in normalized:
        raise ValueError(
            "included_sections must contain "
            "the project section"
        )

    ordered_included = _canonical_sort(
        normalized
    )

    normalized_reasons = {
        normalize_export_section(
            key
        ): value
        for key, value in (
            omission_reasons or {}
        ).items()
    }

    unknown_reason_sections = [
        section
        for section in normalized_reasons
        if (
            section
            not in VALID_PROJECT_EXPORT_SECTIONS
        )
    ]

    if unknown_reason_sections:
        raise ValueError(
            "Unknown omission reason sections: "
            + ", ".join(
                unknown_reason_sections
            )
        )

    omitted = [
        OmittedExportSection(
            section_id=section,
            reason=(
                normalized_reasons.get(
                    section,
                    "not_included",
                )
            ),
        )
        for section in PROJECT_EXPORT_SECTION_ORDER
        if section not in ordered_included
    ]

    manifest = ProjectExportManifest(
        export_name=options.name,
        included_sections=(
            ordered_included
        ),
        omitted_sections=omitted,
        configuration=(
            options.to_dict()
        ),
    )

    errors = manifest.validate()

    if errors:
        raise ValueError(
            "Invalid project export manifest: "
            + "; ".join(
                errors
            )
        )

    return manifest
