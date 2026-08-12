"""
Lip-sync policy engine.

This module converts music-video performance metadata into
explicit lip-sync rules.

Core behavior:

- Vocal sections default to required lip-sync.
- Instrumental sections disable lip-sync.
- Performance-only and cinematic-only sections disable lip-sync.
- Dialogue remains protected from automatic singing lip-sync.
- A caller may explicitly disable lip-sync for a vocal section.
- Lip-sync cannot be forced on non-vocal sections.
"""

from dataclasses import asdict, dataclass, field
from typing import Any

from .music_video import (
    MusicSection,
    MusicVideoStructure,
    normalize_music_token,
)


VALID_LIP_SYNC_MODES = {
    "auto",
    "required",
    "disabled",
}


def normalize_lip_sync_mode(
    value: str,
) -> str:
    """Normalize a lip-sync policy mode."""

    return normalize_music_token(value)


@dataclass
class LipSyncPolicyResult:
    """Resolved lip-sync behavior for one music section."""

    section_id: int
    section_type: str
    performance_mode: str

    lip_sync_mode: str

    lip_sync_required: bool
    lip_sync_allowed: bool

    vocal_audio_expected: bool
    singing_mouth_movement_allowed: bool

    instruction: str

    warnings: list[str] = field(
        default_factory=list
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert the resolved policy to serializable data."""

        return asdict(self)


def resolve_lip_sync_policy(
    section: MusicSection,
    requested_mode: str = "auto",
) -> LipSyncPolicyResult:
    """
    Resolve lip-sync behavior for one music section.

    Auto policy:

        vocal
            -> required lip-sync

        instrumental
            -> lip-sync disabled

        dialogue
            -> singing lip-sync disabled

        performance-only
            -> lip-sync disabled

        cinematic-only
            -> lip-sync disabled

    A vocal section may explicitly disable lip-sync when the
    vocalist is off-camera or the scene is cinematic B-roll.

    Requiring lip-sync on a non-vocal section is rejected.
    """

    section_errors = section.validate()

    if section_errors:
        raise ValueError(
            "Cannot resolve lip-sync policy for "
            "an invalid music section: "
            + "; ".join(section_errors)
        )

    mode = normalize_lip_sync_mode(
        requested_mode
    )

    if mode not in VALID_LIP_SYNC_MODES:
        raise ValueError(
            "unsupported lip-sync mode: "
            f"{requested_mode}"
        )

    performance_mode = (
        section.normalized_performance_mode
    )

    section_type = (
        section.normalized_section_type
    )

    is_vocal = (
        performance_mode == "vocal"
    )

    warnings: list[str] = []

    if mode == "required" and not is_vocal:
        raise ValueError(
            "lip-sync cannot be required for "
            "non-vocal performance mode: "
            f"{performance_mode}"
        )

    if mode == "auto":
        resolved_mode = (
            "required"
            if is_vocal
            else "disabled"
        )
    else:
        resolved_mode = mode

    if (
        is_vocal
        and resolved_mode == "disabled"
    ):
        warnings.append(
            "vocal section has lip-sync disabled; "
            "use this only when the vocalist is "
            "off-camera or visible singing is not required"
        )

    if resolved_mode == "required":
        return LipSyncPolicyResult(
            section_id=section.section_id,
            section_type=section_type,
            performance_mode=performance_mode,
            lip_sync_mode="required",
            lip_sync_required=True,
            lip_sync_allowed=True,
            vocal_audio_expected=True,
            singing_mouth_movement_allowed=True,
            instruction=(
                "Perform precise natural lip-sync to the "
                "vocal audio. Match visible mouth shapes, "
                "phrasing, timing, syllables, breathing, "
                "expression, and performance energy."
            ),
            warnings=warnings,
        )

    if performance_mode == "instrumental":
        instruction = (
            "Do not lip-sync or simulate singing. "
            "Keep the mouth naturally relaxed and use "
            "acting, movement, expression, or cinematic "
            "performance only."
        )

    elif performance_mode == "dialogue":
        instruction = (
            "Do not apply singing lip-sync. "
            "Treat dialogue synchronization as a separate "
            "spoken-performance concern."
        )

    elif performance_mode == "performance-only":
        instruction = (
            "Do not lip-sync. Use physical performance, "
            "expression, choreography, or cinematic acting "
            "without singing mouth movements."
        )

    elif performance_mode == "cinematic-only":
        instruction = (
            "Do not lip-sync. Use cinematic visual action "
            "only and avoid artificial singing mouth movement."
        )

    else:
        instruction = (
            "Lip-sync is disabled for this vocal section. "
            "Do not require visible synchronized singing."
        )

    return LipSyncPolicyResult(
        section_id=section.section_id,
        section_type=section_type,
        performance_mode=performance_mode,
        lip_sync_mode="disabled",
        lip_sync_required=False,
        lip_sync_allowed=is_vocal,
        vocal_audio_expected=is_vocal,
        singing_mouth_movement_allowed=False,
        instruction=instruction,
        warnings=warnings,
    )


def resolve_music_video_lip_sync(
    structure: MusicVideoStructure,
    overrides: dict[int, str] | None = None,
) -> list[LipSyncPolicyResult]:
    """
    Resolve lip-sync policies for all sections in a music video.

    Overrides are keyed by section_id.

    Example:

        {
            2: "disabled",
            4: "required",
        }
    """

    structure_errors = structure.validate()

    if structure_errors:
        raise ValueError(
            "Cannot resolve lip-sync policies for "
            "an invalid music-video structure: "
            + "; ".join(structure_errors)
        )

    overrides = overrides or {}

    known_section_ids = {
        section.section_id
        for section in structure.sections
    }

    unknown_override_ids = (
        set(overrides)
        - known_section_ids
    )

    if unknown_override_ids:
        unknown_text = ", ".join(
            str(section_id)
            for section_id in sorted(
                unknown_override_ids
            )
        )

        raise ValueError(
            "lip-sync overrides reference "
            "unknown section_id: "
            f"{unknown_text}"
        )

    results: list[LipSyncPolicyResult] = []

    for section in structure.sections:
        requested_mode = overrides.get(
            section.section_id,
            "auto",
        )

        results.append(
            resolve_lip_sync_policy(
                section,
                requested_mode=requested_mode,
            )
        )

    return results
