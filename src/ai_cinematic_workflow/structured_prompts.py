"""
Platform-agnostic structured cinematic prompt assembly.

This module converts cinematic Scene data into deterministic,
named, serializable prompt sections.

Structured prompt assembly sits between reusable PromptProfile
configuration and future platform-specific prompt adapters.

It does not replace the existing build_cinematic_prompt() API and
does not render WAN, Veo, Kling, or other provider-specific syntax.
"""

import json
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any

from .global_constraints import (
    GlobalConstraints,
    resolve_scene_constraints,
)
from .prompt_profiles import (
    ResolvedPromptProfile,
    normalize_prompt_component,
)
from .scene import Scene


STRUCTURED_PROMPT_SECTION_ORDER = (
    "characters",
    "location",
    "camera",
    "performance",
    "lighting",
    "mood",
    "dialogue_or_vocals",
    "continuity",
    "global_constraints",
    "negative_constraints",
)


STRUCTURED_PROMPT_SECTION_LABELS = {
    "characters": "Characters",
    "location": "Location",
    "camera": "Camera",
    "performance": "Performance",
    "lighting": "Lighting",
    "mood": "Mood",
    "dialogue_or_vocals": "Dialogue or Vocals",
    "continuity": "Continuity",
    "global_constraints": "Global Constraints",
    "negative_constraints": "Negative Constraints",
}


VALID_STRUCTURED_PROMPT_SECTIONS = set(
    STRUCTURED_PROMPT_SECTION_ORDER
)


def normalize_prompt_section(
    value: str,
) -> str:
    """
    Normalize a structured prompt-section identifier.

    The normalization behavior is shared with PromptProfile
    component normalization.

    Examples:

        "Dialogue Or Vocals"
        -> "dialogue_or_vocals"

        "negative-constraints"
        -> "negative_constraints"
    """

    return normalize_prompt_component(
        value
    )


def _is_empty_content(
    value: Any,
) -> bool:
    """
    Return True when section content should be considered empty.
    """

    if value is None:
        return True

    if isinstance(
        value,
        str,
    ):
        return not value.strip()

    if isinstance(
        value,
        (
            list,
            tuple,
            set,
            dict,
        ),
    ):
        return len(value) == 0

    return False


def _validate_serializable(
    value: Any,
    *,
    description: str,
) -> None:
    """
    Require JSON-serializable structured prompt data.
    """

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


def _has_meaningful_global_constraints(
    constraints: GlobalConstraints,
) -> bool:
    """
    Return whether a GlobalConstraints object contains
    production rules beyond its profile metadata.
    """

    data = constraints.to_dict()

    meaningful_keys = (
        "required_constraints",
        "advisory_constraints",
        "negative_constraints",
        "prohibited_elements",
        "character_identity_constraints",
        "visual_style_constraints",
        "camera_constraints",
        "environment_constraints",
        "custom_constraints",
    )

    return any(
        bool(
            data[key]
        )
        for key in meaningful_keys
    )


@dataclass(frozen=True)
class StructuredPromptSection:
    """
    One ordered cinematic prompt section.

    section_id:
        Canonical component identifier.

    label:
        Human-readable section name.

    order:
        Stable canonical position in the structured prompt.

    content:
        Structured serializable section data.

    metadata:
        Additional platform-agnostic section information.
    """

    section_id: str
    label: str
    order: int
    content: Any

    metadata: dict[
        str,
        Any,
    ] = field(
        default_factory=dict
    )

    def validate(self) -> list[str]:
        """Validate one structured prompt section."""

        errors: list[str] = []

        normalized_id = (
            normalize_prompt_section(
                self.section_id
            )
        )

        if (
            normalized_id
            not in VALID_STRUCTURED_PROMPT_SECTIONS
        ):
            errors.append(
                "unknown structured prompt section: "
                + normalized_id
            )

        if not self.label.strip():
            errors.append(
                "structured prompt section label "
                "cannot be empty"
            )

        if self.order <= 0:
            errors.append(
                "structured prompt section order "
                "must be greater than zero"
            )

        try:
            _validate_serializable(
                self.content,
                description=(
                    "structured prompt section content"
                ),
            )
        except ValueError as exc:
            errors.append(
                str(exc)
            )

        try:
            _validate_serializable(
                self.metadata,
                description=(
                    "structured prompt section metadata"
                ),
            )
        except ValueError as exc:
            errors.append(
                str(exc)
            )

        return errors

    @property
    def is_valid(self) -> bool:
        """Return True when the section passes validation."""

        return not self.validate()

    @property
    def is_empty(self) -> bool:
        """Return whether the section contains empty content."""

        return _is_empty_content(
            self.content
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the section into serializable data."""

        return {
            "section_id": (
                normalize_prompt_section(
                    self.section_id
                )
            ),
            "label": self.label,
            "order": self.order,
            "content": deepcopy(
                self.content
            ),
            "metadata": deepcopy(
                self.metadata
            ),
        }


@dataclass(frozen=True)
class OmittedPromptComponent:
    """
    One prompt component intentionally absent from
    structured prompt output.
    """

    component: str
    reason: str

    def to_dict(self) -> dict[str, str]:
        """Convert omission information into data."""

        return {
            "component": self.component,
            "reason": self.reason,
        }


@dataclass
class StructuredPromptResult:
    """
    Complete structured cinematic prompt result.

    The result preserves section ordering and reports both
    included and omitted prompt components.
    """

    scene_id: int

    sections: list[
        StructuredPromptSection
    ] = field(
        default_factory=list
    )

    omitted_components: list[
        OmittedPromptComponent
    ] = field(
        default_factory=list
    )

    prompt_profile_name: str | None = None

    include_empty_sections: bool = False

    @property
    def section_count(self) -> int:
        """Return the number of assembled sections."""

        return len(
            self.sections
        )

    @property
    def included_components(
        self,
    ) -> list[str]:
        """Return canonical IDs for included sections."""

        return [
            section.section_id
            for section in self.sections
        ]

    @property
    def omitted_component_names(
        self,
    ) -> list[str]:
        """Return canonical IDs for omitted components."""

        return [
            item.component
            for item in self.omitted_components
        ]

    def get_section(
        self,
        section_id: str,
    ) -> StructuredPromptSection | None:
        """
        Return one structured section by canonical or
        human-formatted component name.
        """

        normalized = (
            normalize_prompt_section(
                section_id
            )
        )

        for section in self.sections:
            if (
                section.section_id
                == normalized
            ):
                return section

        return None

    def validate(self) -> list[str]:
        """Validate the complete structured result."""

        errors: list[str] = []

        section_ids = [
            section.section_id
            for section in self.sections
        ]

        if (
            len(section_ids)
            != len(set(section_ids))
        ):
            errors.append(
                "structured prompt result cannot "
                "contain duplicate section IDs"
            )

        orders = [
            section.order
            for section in self.sections
        ]

        if orders != sorted(orders):
            errors.append(
                "structured prompt sections must use "
                "deterministic canonical ordering"
            )

        for section in self.sections:
            section_errors = (
                section.validate()
            )

            if section_errors:
                errors.append(
                    f"section '{section.section_id}': "
                    + "; ".join(
                        section_errors
                    )
                )

        return errors

    @property
    def is_valid(self) -> bool:
        """Return True when all structured sections are valid."""

        return not self.validate()

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the complete structured prompt into
        serializable data.
        """

        return {
            "summary": {
                "valid": self.is_valid,
                "scene_id": self.scene_id,
                "section_count": (
                    self.section_count
                ),
                "included_component_count": len(
                    self.included_components
                ),
                "omitted_component_count": len(
                    self.omitted_components
                ),
            },
            "scene_id": self.scene_id,
            "prompt_profile_name": (
                self.prompt_profile_name
            ),
            "include_empty_sections": (
                self.include_empty_sections
            ),
            "included_components": list(
                self.included_components
            ),
            "omitted_components": [
                item.to_dict()
                for item in self.omitted_components
            ],
            "sections": [
                section.to_dict()
                for section in self.sections
            ],
        }


def _camera_content(
    scene: Scene,
) -> dict[str, str]:
    """Build structured camera information."""

    return {
        "shot": scene.camera.shot,
        "movement": scene.camera.movement,
        "lens": scene.camera.lens,
    }


def _build_component_content(
    scene: Scene,
    component: str,
    *,
    global_constraints: GlobalConstraints | None,
) -> tuple[
    Any,
    str,
]:
    """
    Build one canonical prompt component.

    Returns:
        Tuple of section content and source label.
    """

    if component == "characters":
        return (
            deepcopy(
                scene.characters
            ),
            "scene",
        )

    if component == "location":
        return (
            scene.location,
            "scene",
        )

    if component == "camera":
        return (
            _camera_content(
                scene
            ),
            "scene",
        )

    if component == "performance":
        return (
            scene.performance,
            "scene",
        )

    if component == "lighting":
        return (
            scene.lighting,
            "scene",
        )

    if component == "mood":
        return (
            scene.mood,
            "scene",
        )

    if component == "dialogue_or_vocals":
        return (
            scene.dialogue_or_vocals,
            "scene",
        )

    if component == "continuity":
        return (
            deepcopy(
                scene.continuity
            ),
            "scene",
        )

    if component == "global_constraints":
        if global_constraints is None:
            return (
                {},
                "global_constraints",
            )

        if not _has_meaningful_global_constraints(
            global_constraints
        ):
            return (
                {},
                "global_constraints",
            )

        return (
            deepcopy(
                global_constraints.to_dict()
            ),
            "global_constraints",
        )

    if component == "negative_constraints":
        if global_constraints is None:
            return (
                deepcopy(
                    scene.negative_constraints
                ),
                "scene",
            )

        resolved = resolve_scene_constraints(
            scene,
            global_constraints,
        )

        return (
            deepcopy(
                resolved.resolved_negative_constraints
            ),
            "resolved_scene_constraints",
        )

    raise ValueError(
        "unsupported structured prompt component: "
        + component
    )


def _resolve_component_state(
    component: str,
    profile: ResolvedPromptProfile | None,
) -> str:
    """
    Determine whether one canonical component should be built.

    Returns:
        "enabled"
        "disabled"
        "not_enabled"

    Without a profile, all canonical components are enabled.
    """

    if profile is None:
        return "enabled"

    if profile.is_disabled(
        component
    ):
        return "disabled"

    if profile.is_enabled(
        component
    ):
        return "enabled"

    return "not_enabled"


def assemble_structured_prompt(
    scene: Scene,
    *,
    prompt_profile: ResolvedPromptProfile | None = None,
    global_constraints: GlobalConstraints | None = None,
    include_empty_sections: bool = False,
) -> StructuredPromptResult:
    """
    Assemble one Scene into deterministic structured prompt sections.

    Behavior:

    - Without PromptProfile:
      all canonical sections are considered active.

    - With ResolvedPromptProfile:
      only explicitly enabled components are built.
      Disabled components are reported as omitted.

    - When GlobalConstraints are supplied:
      the global-constraints section becomes available and the
      negative-constraints section uses resolved project + scene
      negatives.

    - Empty active sections are omitted by default.
      Set include_empty_sections=True to preserve them.

    Inputs are never mutated.
    """

    scene_errors = scene.validate()

    if scene_errors:
        raise ValueError(
            f"Invalid scene {scene.scene_id}: "
            + "; ".join(
                scene_errors
            )
        )

    if (
        prompt_profile is not None
        and not prompt_profile.is_valid
    ):
        raise ValueError(
            "Invalid resolved prompt profile: "
            "profile contains error-level issues"
        )

    if global_constraints is not None:
        constraint_errors = (
            global_constraints.validate()
        )

        if constraint_errors:
            raise ValueError(
                "Invalid global constraints: "
                + "; ".join(
                    constraint_errors
                )
            )

    sections: list[
        StructuredPromptSection
    ] = []

    omitted: list[
        OmittedPromptComponent
    ] = []

    if prompt_profile is not None:
        for component in (
            prompt_profile.enabled_components
        ):
            normalized = (
                normalize_prompt_section(
                    component
                )
            )

            if (
                normalized
                not in VALID_STRUCTURED_PROMPT_SECTIONS
            ):
                omitted.append(
                    OmittedPromptComponent(
                        component=normalized,
                        reason=(
                            "unsupported_component"
                        ),
                    )
                )

        for component in (
            prompt_profile.disabled_components
        ):
            normalized = (
                normalize_prompt_section(
                    component
                )
            )

            if (
                normalized
                not in VALID_STRUCTURED_PROMPT_SECTIONS
            ):
                omitted.append(
                    OmittedPromptComponent(
                        component=normalized,
                        reason=(
                            "disabled_by_profile"
                        ),
                    )
                )

    for (
        index,
        component,
    ) in enumerate(
        STRUCTURED_PROMPT_SECTION_ORDER,
        start=1,
    ):
        state = _resolve_component_state(
            component,
            prompt_profile,
        )

        if state == "disabled":
            omitted.append(
                OmittedPromptComponent(
                    component=component,
                    reason=(
                        "disabled_by_profile"
                    ),
                )
            )
            continue

        if state == "not_enabled":
            omitted.append(
                OmittedPromptComponent(
                    component=component,
                    reason=(
                        "not_enabled_by_profile"
                    ),
                )
            )
            continue

        content, source = (
            _build_component_content(
                scene,
                component,
                global_constraints=(
                    global_constraints
                ),
            )
        )

        empty = _is_empty_content(
            content
        )

        if (
            empty
            and not include_empty_sections
        ):
            omitted.append(
                OmittedPromptComponent(
                    component=component,
                    reason="empty",
                )
            )
            continue

        section = StructuredPromptSection(
            section_id=component,
            label=(
                STRUCTURED_PROMPT_SECTION_LABELS[
                    component
                ]
            ),
            order=index,
            content=deepcopy(
                content
            ),
            metadata={
                "component": component,
                "source": source,
                "empty": empty,
                "profile_controlled": (
                    prompt_profile is not None
                ),
            },
        )

        section_errors = (
            section.validate()
        )

        if section_errors:
            raise ValueError(
                f"Invalid structured prompt section "
                f"'{component}': "
                + "; ".join(
                    section_errors
                )
            )

        sections.append(
            section
        )

    result = StructuredPromptResult(
        scene_id=scene.scene_id,
        sections=sections,
        omitted_components=omitted,
        prompt_profile_name=(
            prompt_profile.name
            if prompt_profile is not None
            else None
        ),
        include_empty_sections=(
            include_empty_sections
        ),
    )

    result_errors = result.validate()

    if result_errors:
        raise ValueError(
            "Invalid structured prompt result: "
            + "; ".join(
                result_errors
            )
        )

    return result
