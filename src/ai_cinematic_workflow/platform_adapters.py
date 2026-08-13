"""
Provider-neutral Platform Adapter foundation.

This module defines reusable adapter metadata, capability declarations,
structured adapter results, deterministic StructuredPromptResult
adaptation, and an adapter registry.

The core adapter layer does not implement undocumented WAN, Veo, Kling,
or other provider-specific API parameters and does not perform network
execution.
"""

import json
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any

from .structured_prompts import (
    STRUCTURED_PROMPT_SECTION_ORDER,
    VALID_STRUCTURED_PROMPT_SECTIONS,
    StructuredPromptResult,
    normalize_prompt_section,
)


VALID_ADAPTER_ISSUE_SEVERITIES = {
    "warning",
    "error",
}


def normalize_platform_identifier(
    value: str,
) -> str:
    """
    Normalize a platform identifier.

    Examples:

        "Example Video Platform"
        -> "example_video_platform"

        "example-video-platform"
        -> "example_video_platform"
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
    Normalize and deduplicate structured prompt sections
    while preserving first-seen order.
    """

    result: list[str] = []

    for value in values:
        normalized = normalize_prompt_section(
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


def _canonical_section_sort(
    values: list[str],
) -> list[str]:
    """Return structured prompt sections in canonical order."""

    normalized = _normalize_unique_sections(
        values
    )

    order_map = {
        section: index
        for index, section in enumerate(
            STRUCTURED_PROMPT_SECTION_ORDER
        )
    }

    known = [
        section
        for section in normalized
        if (
            section
            in VALID_STRUCTURED_PROMPT_SECTIONS
        )
    ]

    return sorted(
        known,
        key=lambda section: order_map[
            section
        ],
    )


def _validate_json_serializable(
    value: Any,
    *,
    description: str,
) -> None:
    """Require portable JSON-compatible adapter data."""

    try:
        json.dumps(
            value,
            ensure_ascii=False,
        )
    except (
        TypeError,
        ValueError,
    ) as exc:
        raise ValueError(
            f"{description} must be JSON serializable"
        ) from exc


@dataclass(frozen=True)
class PlatformAdapterCapabilities:
    """
    Canonical capabilities declared by one Platform Adapter.

    supported_prompt_sections describes which core
    Structured Prompt Sections the adapter can accept.

    supports_structured_prompt_input controls whether the adapter
    accepts StructuredPromptResult at all.

    supports_enhanced_project_export declares whether a future or
    provider-specific implementation accepts Enhanced Project Export
    packages directly.

    custom_capabilities allows documented adapter extensions without
    changing the core capability model.
    """

    supported_prompt_sections: list[str] = field(
        default_factory=lambda: list(
            STRUCTURED_PROMPT_SECTION_ORDER
        )
    )

    supports_structured_prompt_input: bool = True
    supports_enhanced_project_export: bool = False
    supports_section_metadata: bool = True

    custom_capabilities: dict[
        str,
        Any,
    ] = field(
        default_factory=dict
    )

    @property
    def normalized_prompt_sections(
        self,
    ) -> list[str]:
        """Return unique supported sections in canonical order."""

        return _canonical_section_sort(
            self.supported_prompt_sections
        )

    def supports_section(
        self,
        section_id: str,
    ) -> bool:
        """Return whether one canonical prompt section is supported."""

        normalized = normalize_prompt_section(
            section_id
        )

        return (
            normalized
            in self.normalized_prompt_sections
        )

    def validate(self) -> list[str]:
        """Validate declared adapter capabilities."""

        errors: list[str] = []

        normalized = _normalize_unique_sections(
            self.supported_prompt_sections
        )

        if (
            len(normalized)
            != len(
                self.supported_prompt_sections
            )
        ):
            errors.append(
                "supported prompt sections cannot contain "
                "duplicates or blank values"
            )

        unknown = [
            section
            for section in normalized
            if (
                section
                not in VALID_STRUCTURED_PROMPT_SECTIONS
            )
        ]

        for section in unknown:
            errors.append(
                "unknown supported prompt section: "
                + section
            )

        try:
            _validate_json_serializable(
                self.custom_capabilities,
                description=(
                    "custom adapter capabilities"
                ),
            )
        except ValueError as exc:
            errors.append(
                str(exc)
            )

        return errors

    @property
    def is_valid(self) -> bool:
        """Return True when capability declarations are valid."""

        return not self.validate()

    def to_dict(self) -> dict[str, Any]:
        """Convert capabilities into portable structured data."""

        return {
            "supported_prompt_sections": list(
                self.normalized_prompt_sections
            ),
            "supports_structured_prompt_input": (
                self.supports_structured_prompt_input
            ),
            "supports_enhanced_project_export": (
                self.supports_enhanced_project_export
            ),
            "supports_section_metadata": (
                self.supports_section_metadata
            ),
            "custom_capabilities": deepcopy(
                self.custom_capabilities
            ),
        }


@dataclass(frozen=True)
class PlatformAdapterIssue:
    """
    One structured warning or error produced during adaptation.
    """

    issue_type: str
    severity: str
    message: str

    feature: str | None = None
    section_id: str | None = None

    def validate(self) -> list[str]:
        """Validate one adapter issue."""

        errors: list[str] = []

        if not self.issue_type.strip():
            errors.append(
                "platform adapter issue type "
                "cannot be empty"
            )

        normalized_severity = (
            self.severity.strip().lower()
        )

        if (
            normalized_severity
            not in VALID_ADAPTER_ISSUE_SEVERITIES
        ):
            errors.append(
                "platform adapter issue severity "
                "must be warning or error"
            )

        if not self.message.strip():
            errors.append(
                "platform adapter issue message "
                "cannot be empty"
            )

        if self.section_id is not None:
            normalized_section = (
                normalize_prompt_section(
                    self.section_id
                )
            )

            if (
                normalized_section
                not in VALID_STRUCTURED_PROMPT_SECTIONS
            ):
                errors.append(
                    "unknown platform adapter issue section: "
                    + normalized_section
                )

        return errors

    @property
    def is_valid(self) -> bool:
        """Return True when issue data is valid."""

        return not self.validate()

    def to_dict(self) -> dict[str, Any]:
        """Convert issue data into portable form."""

        return {
            "issue_type": self.issue_type,
            "severity": (
                self.severity.strip().lower()
            ),
            "message": self.message,
            "feature": self.feature,
            "section_id": (
                normalize_prompt_section(
                    self.section_id
                )
                if self.section_id is not None
                else None
            ),
        }


@dataclass
class PlatformAdapterResult:
    """
    Deterministic result of one platform adaptation.

    payload remains structured and provider-neutral at the base layer.
    Provider-specific implementations may override adaptation behavior
    while preserving this result contract.
    """

    platform_id: str
    adapter_name: str
    adapter_version: str

    capabilities: dict[
        str,
        Any,
    ] = field(
        default_factory=dict
    )

    supported_features: list[str] = field(
        default_factory=list
    )

    unsupported_features: list[str] = field(
        default_factory=list
    )

    payload: dict[
        str,
        Any,
    ] = field(
        default_factory=dict
    )

    issues: list[
        PlatformAdapterIssue
    ] = field(
        default_factory=list
    )

    @property
    def warning_count(self) -> int:
        """Return number of warning issues."""

        return sum(
            issue.severity.strip().lower()
            == "warning"
            for issue in self.issues
        )

    @property
    def error_count(self) -> int:
        """Return number of error issues."""

        return sum(
            issue.severity.strip().lower()
            == "error"
            for issue in self.issues
        )

    @property
    def is_valid(self) -> bool:
        """Return True when no error-level issues exist."""

        return (
            self.error_count == 0
            and not self.validate()
        )

    def validate(self) -> list[str]:
        """Validate adapter output."""

        errors: list[str] = []

        if not normalize_platform_identifier(
            self.platform_id
        ):
            errors.append(
                "platform adapter result platform ID "
                "cannot be empty"
            )

        if not self.adapter_name.strip():
            errors.append(
                "platform adapter result adapter name "
                "cannot be empty"
            )

        if not self.adapter_version.strip():
            errors.append(
                "platform adapter result adapter version "
                "cannot be empty"
            )

        overlap = set(
            self.supported_features
        ).intersection(
            self.unsupported_features
        )

        if overlap:
            errors.append(
                "platform adapter features cannot be both "
                "supported and unsupported: "
                + ", ".join(
                    sorted(
                        overlap
                    )
                )
            )

        for issue in self.issues:
            issue_errors = issue.validate()

            if issue_errors:
                errors.extend(
                    [
                        "adapter issue: "
                        + error
                        for error in issue_errors
                    ]
                )

        try:
            _validate_json_serializable(
                self.capabilities,
                description=(
                    "platform adapter result capabilities"
                ),
            )
        except ValueError as exc:
            errors.append(
                str(exc)
            )

        try:
            _validate_json_serializable(
                self.payload,
                description=(
                    "platform adapter result payload"
                ),
            )
        except ValueError as exc:
            errors.append(
                str(exc)
            )

        return errors

    def to_dict(self) -> dict[str, Any]:
        """Convert adapter result into JSON-compatible data."""

        return {
            "summary": {
                "valid": self.is_valid,
                "platform_id": (
                    normalize_platform_identifier(
                        self.platform_id
                    )
                ),
                "supported_feature_count": len(
                    self.supported_features
                ),
                "unsupported_feature_count": len(
                    self.unsupported_features
                ),
                "warning_count": (
                    self.warning_count
                ),
                "error_count": (
                    self.error_count
                ),
            },
            "platform_id": (
                normalize_platform_identifier(
                    self.platform_id
                )
            ),
            "adapter_name": self.adapter_name,
            "adapter_version": (
                self.adapter_version
            ),
            "capabilities": deepcopy(
                self.capabilities
            ),
            "supported_features": list(
                self.supported_features
            ),
            "unsupported_features": list(
                self.unsupported_features
            ),
            "payload": deepcopy(
                self.payload
            ),
            "issues": [
                issue.to_dict()
                for issue in self.issues
            ],
        }


@dataclass
class PlatformAdapter:
    """
    Provider-neutral base Platform Adapter.

    The default implementation adapts StructuredPromptResult by
    filtering its canonical sections against declared capabilities.

    Provider-specific subclasses may transform the structured payload
    further, but must not mutate source cinematic data.
    """

    platform_id: str
    display_name: str

    adapter_version: str = "1.0"

    capabilities: PlatformAdapterCapabilities = field(
        default_factory=PlatformAdapterCapabilities
    )

    metadata: dict[
        str,
        Any,
    ] = field(
        default_factory=dict
    )

    @property
    def canonical_platform_id(
        self,
    ) -> str:
        """Return normalized adapter platform identifier."""

        return normalize_platform_identifier(
            self.platform_id
        )

    def validate(self) -> list[str]:
        """Validate adapter identity, metadata, and capabilities."""

        errors: list[str] = []

        if not self.canonical_platform_id:
            errors.append(
                "platform adapter platform ID "
                "cannot be empty"
            )

        if not self.display_name.strip():
            errors.append(
                "platform adapter display name "
                "cannot be empty"
            )

        if not self.adapter_version.strip():
            errors.append(
                "platform adapter version "
                "cannot be empty"
            )

        capability_errors = (
            self.capabilities.validate()
        )

        errors.extend(
            [
                "capabilities: "
                + error
                for error in capability_errors
            ]
        )

        try:
            _validate_json_serializable(
                self.metadata,
                description=(
                    "platform adapter metadata"
                ),
            )
        except ValueError as exc:
            errors.append(
                str(exc)
            )

        return errors

    @property
    def is_valid(self) -> bool:
        """Return True when adapter configuration is valid."""

        return not self.validate()

    def to_dict(self) -> dict[str, Any]:
        """Convert adapter identity into portable data."""

        return {
            "platform_id": (
                self.canonical_platform_id
            ),
            "display_name": self.display_name,
            "adapter_version": (
                self.adapter_version
            ),
            "capabilities": (
                self.capabilities.to_dict()
            ),
            "metadata": deepcopy(
                self.metadata
            ),
        }

    def adapt_structured_prompt(
        self,
        source: StructuredPromptResult,
    ) -> PlatformAdapterResult:
        """
        Adapt one StructuredPromptResult using declared capabilities.

        Supported sections are copied into deterministic adapter
        payload data.

        Unsupported source sections are reported as warnings and are
        excluded from the adapted payload.

        The source StructuredPromptResult is never mutated.
        """

        adapter_errors = self.validate()

        if adapter_errors:
            raise ValueError(
                "Invalid platform adapter: "
                + "; ".join(
                    adapter_errors
                )
            )

        source_errors = source.validate()

        if source_errors:
            raise ValueError(
                "Invalid StructuredPromptResult: "
                + "; ".join(
                    source_errors
                )
            )

        if (
            not self.capabilities
            .supports_structured_prompt_input
        ):
            issue = PlatformAdapterIssue(
                issue_type=(
                    "unsupported_input_type"
                ),
                severity="error",
                message=(
                    "This adapter does not support "
                    "StructuredPromptResult input"
                ),
                feature=(
                    "structured_prompt_input"
                ),
            )

            return PlatformAdapterResult(
                platform_id=(
                    self.canonical_platform_id
                ),
                adapter_name=(
                    self.display_name
                ),
                adapter_version=(
                    self.adapter_version
                ),
                capabilities=(
                    self.capabilities.to_dict()
                ),
                supported_features=[],
                unsupported_features=[
                    "structured_prompt_input",
                ],
                payload={
                    "mode": (
                        "structured_prompt_adapter"
                    ),
                    "scene_id": source.scene_id,
                    "sections": [],
                },
                issues=[
                    issue,
                ],
            )

        supported_sections: list[str] = []
        unsupported_sections: list[str] = []

        adapted_sections: list[
            dict[str, Any]
        ] = []

        issues: list[
            PlatformAdapterIssue
        ] = []

        for section in source.sections:
            section_id = (
                normalize_prompt_section(
                    section.section_id
                )
            )

            if self.capabilities.supports_section(
                section_id
            ):
                section_data = (
                    section.to_dict()
                )

                if (
                    not self.capabilities
                    .supports_section_metadata
                ):
                    section_data[
                        "metadata"
                    ] = {}

                adapted_sections.append(
                    deepcopy(
                        section_data
                    )
                )

                supported_sections.append(
                    section_id
                )

            else:
                unsupported_sections.append(
                    section_id
                )

                issues.append(
                    PlatformAdapterIssue(
                        issue_type=(
                            "unsupported_prompt_section"
                        ),
                        severity="warning",
                        message=(
                            "Structured prompt section "
                            f"'{section_id}' is not supported "
                            "by this adapter"
                        ),
                        feature=section_id,
                        section_id=section_id,
                    )
                )

        supported_sections = (
            _canonical_section_sort(
                supported_sections
            )
        )

        unsupported_sections = (
            _canonical_section_sort(
                unsupported_sections
            )
        )

        payload = {
            "mode": (
                "structured_prompt_adapter"
            ),
            "scene_id": source.scene_id,
            "source_prompt_profile_name": (
                source.prompt_profile_name
            ),
            "sections": adapted_sections,
        }

        return PlatformAdapterResult(
            platform_id=(
                self.canonical_platform_id
            ),
            adapter_name=(
                self.display_name
            ),
            adapter_version=(
                self.adapter_version
            ),
            capabilities=(
                self.capabilities.to_dict()
            ),
            supported_features=(
                supported_sections
            ),
            unsupported_features=(
                unsupported_sections
            ),
            payload=payload,
            issues=issues,
        )


@dataclass
class PlatformAdapterRegistry:
    """
    In-memory registry for canonical Platform Adapter lookup.

    Registration is explicit and duplicate canonical platform IDs
    are rejected.
    """

    _adapters: dict[
        str,
        PlatformAdapter,
    ] = field(
        default_factory=dict
    )

    def register(
        self,
        adapter: PlatformAdapter,
    ) -> None:
        """Register one validated adapter."""

        errors = adapter.validate()

        if errors:
            raise ValueError(
                "Invalid platform adapter: "
                + "; ".join(
                    errors
                )
            )

        platform_id = (
            adapter.canonical_platform_id
        )

        if platform_id in self._adapters:
            raise ValueError(
                "Platform adapter already registered: "
                + platform_id
            )

        self._adapters[
            platform_id
        ] = adapter

    def get(
        self,
        platform_id: str,
    ) -> PlatformAdapter:
        """Return adapter by canonical or human-formatted ID."""

        normalized = (
            normalize_platform_identifier(
                platform_id
            )
        )

        if normalized not in self._adapters:
            raise KeyError(
                "Unknown platform adapter: "
                + normalized
            )

        return self._adapters[
            normalized
        ]

    def contains(
        self,
        platform_id: str,
    ) -> bool:
        """Return whether a platform adapter is registered."""

        normalized = (
            normalize_platform_identifier(
                platform_id
            )
        )

        return (
            normalized
            in self._adapters
        )

    @property
    def platform_ids(
        self,
    ) -> list[str]:
        """Return deterministic registered platform identifiers."""

        return sorted(
            self._adapters.keys()
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert registry metadata into portable data."""

        return {
            "summary": {
                "adapter_count": len(
                    self._adapters
                ),
            },
            "platform_ids": list(
                self.platform_ids
            ),
            "adapters": [
                self._adapters[
                    platform_id
                ].to_dict()
                for platform_id in (
                    self.platform_ids
                )
            ],
        }
