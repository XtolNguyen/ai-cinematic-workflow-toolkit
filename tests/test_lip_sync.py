import pytest

from ai_cinematic_workflow.lip_sync import (
    normalize_lip_sync_mode,
    resolve_lip_sync_policy,
    resolve_music_video_lip_sync,
)
from ai_cinematic_workflow.music_video import (
    MusicSection,
    MusicVideoStructure,
)


def make_section(
    section_id: int,
    section_type: str,
    performance_mode: str,
    start_seconds: float = 0,
    end_seconds: float = 15,
    scene_ids: list[int] | None = None,
) -> MusicSection:
    """Create a reusable music section for lip-sync tests."""

    return MusicSection(
        section_id=section_id,
        section_type=section_type,
        start_seconds=start_seconds,
        end_seconds=end_seconds,
        performance_mode=performance_mode,
        scene_ids=scene_ids or [section_id],
    )


def test_normalize_lip_sync_mode():
    """Lip-sync modes should normalize consistently."""

    assert normalize_lip_sync_mode("AUTO") == "auto"
    assert normalize_lip_sync_mode("Required") == "required"
    assert normalize_lip_sync_mode("disabled") == "disabled"


def test_vocal_auto_requires_lip_sync():
    """Vocal sections should require lip-sync in auto mode."""

    section = make_section(
        section_id=1,
        section_type="verse",
        performance_mode="vocal",
    )

    result = resolve_lip_sync_policy(
        section
    )

    assert result.lip_sync_mode == "required"
    assert result.lip_sync_required is True
    assert result.lip_sync_allowed is True
    assert result.vocal_audio_expected is True

    assert (
        result.singing_mouth_movement_allowed
        is True
    )

    assert result.warnings == []


def test_chorus_auto_requires_lip_sync():
    """Chorus vocals should also resolve to required lip-sync."""

    section = make_section(
        section_id=1,
        section_type="chorus",
        performance_mode="vocal",
    )

    result = resolve_lip_sync_policy(
        section,
        requested_mode="auto",
    )

    assert result.lip_sync_required is True
    assert result.lip_sync_mode == "required"


def test_instrumental_auto_disables_lip_sync():
    """Instrumental sections must disable singing lip-sync."""

    section = make_section(
        section_id=1,
        section_type="instrumental",
        performance_mode="instrumental",
    )

    result = resolve_lip_sync_policy(
        section
    )

    assert result.lip_sync_mode == "disabled"
    assert result.lip_sync_required is False
    assert result.lip_sync_allowed is False
    assert result.vocal_audio_expected is False

    assert (
        result.singing_mouth_movement_allowed
        is False
    )

    assert "Do not lip-sync" in result.instruction


def test_instrumental_intro_disables_lip_sync():
    """Instrumental intros should never auto-enable lip-sync."""

    section = make_section(
        section_id=1,
        section_type="intro",
        performance_mode="instrumental",
    )

    result = resolve_lip_sync_policy(
        section
    )

    assert result.lip_sync_required is False

    assert (
        result.singing_mouth_movement_allowed
        is False
    )


def test_instrumental_outro_disables_lip_sync():
    """Instrumental outros should never auto-enable lip-sync."""

    section = make_section(
        section_id=1,
        section_type="outro",
        performance_mode="instrumental",
    )

    result = resolve_lip_sync_policy(
        section
    )

    assert result.lip_sync_required is False

    assert (
        result.singing_mouth_movement_allowed
        is False
    )


def test_dialogue_does_not_enable_singing_lip_sync():
    """Dialogue should not be treated as singing performance."""

    section = make_section(
        section_id=1,
        section_type="custom",
        performance_mode="dialogue",
    )

    section.label = "Spoken dialogue"

    result = resolve_lip_sync_policy(
        section
    )

    assert result.lip_sync_required is False
    assert result.lip_sync_allowed is False

    assert (
        result.singing_mouth_movement_allowed
        is False
    )

    assert (
        "Do not apply singing lip-sync"
        in result.instruction
    )


def test_performance_only_disables_lip_sync():
    """Performance-only sections should use acting without singing."""

    section = make_section(
        section_id=1,
        section_type="bridge",
        performance_mode="performance-only",
    )

    result = resolve_lip_sync_policy(
        section
    )

    assert result.lip_sync_required is False

    assert (
        result.singing_mouth_movement_allowed
        is False
    )


def test_cinematic_only_disables_lip_sync():
    """Cinematic-only sections should remain visually driven."""

    section = make_section(
        section_id=1,
        section_type="intro",
        performance_mode="cinematic-only",
    )

    result = resolve_lip_sync_policy(
        section
    )

    assert result.lip_sync_required is False

    assert (
        result.singing_mouth_movement_allowed
        is False
    )


def test_vocal_section_can_explicitly_disable_lip_sync():
    """
    Vocal audio may continue while visible lip-sync is disabled,
    such as during B-roll or off-camera performance.
    """

    section = make_section(
        section_id=1,
        section_type="verse",
        performance_mode="vocal",
    )

    result = resolve_lip_sync_policy(
        section,
        requested_mode="disabled",
    )

    assert result.lip_sync_mode == "disabled"
    assert result.lip_sync_required is False
    assert result.lip_sync_allowed is True
    assert result.vocal_audio_expected is True

    assert (
        result.singing_mouth_movement_allowed
        is False
    )

    assert len(result.warnings) == 1

    assert (
        "vocal section has lip-sync disabled"
        in result.warnings[0]
    )


def test_non_vocal_section_cannot_require_lip_sync():
    """Instrumental sections must reject forced lip-sync."""

    section = make_section(
        section_id=1,
        section_type="instrumental",
        performance_mode="instrumental",
    )

    with pytest.raises(
        ValueError,
        match=(
            "lip-sync cannot be required for "
            "non-vocal performance mode"
        ),
    ):
        resolve_lip_sync_policy(
            section,
            requested_mode="required",
        )


def test_invalid_requested_mode_is_rejected():
    """Unsupported lip-sync policy modes should fail."""

    section = make_section(
        section_id=1,
        section_type="verse",
        performance_mode="vocal",
    )

    with pytest.raises(
        ValueError,
        match="unsupported lip-sync mode",
    ):
        resolve_lip_sync_policy(
            section,
            requested_mode="sometimes",
        )


def test_invalid_music_section_is_rejected():
    """Policies should not resolve against invalid sections."""

    section = MusicSection(
        section_id=0,
        section_type="verse",
        start_seconds=0,
        end_seconds=15,
        performance_mode="vocal",
        scene_ids=[1],
    )

    with pytest.raises(
        ValueError,
        match=(
            "Cannot resolve lip-sync policy "
            "for an invalid music section"
        ),
    ):
        resolve_lip_sync_policy(
            section
        )


def test_complete_music_video_lip_sync_resolution():
    """
    A typical MV should resolve vocal and instrumental sections
    into the correct lip-sync policies.
    """

    structure = MusicVideoStructure(
        sections=[
            make_section(
                section_id=1,
                section_type="intro",
                performance_mode="instrumental",
                start_seconds=0,
                end_seconds=15,
                scene_ids=[1],
            ),
            make_section(
                section_id=2,
                section_type="verse",
                performance_mode="vocal",
                start_seconds=15,
                end_seconds=30,
                scene_ids=[2],
            ),
            make_section(
                section_id=3,
                section_type="chorus",
                performance_mode="vocal",
                start_seconds=30,
                end_seconds=45,
                scene_ids=[3],
            ),
            make_section(
                section_id=4,
                section_type="outro",
                performance_mode="instrumental",
                start_seconds=45,
                end_seconds=60,
                scene_ids=[4],
            ),
        ]
    )

    results = resolve_music_video_lip_sync(
        structure
    )

    assert len(results) == 4

    assert (
        results[0].lip_sync_required
        is False
    )

    assert (
        results[1].lip_sync_required
        is True
    )

    assert (
        results[2].lip_sync_required
        is True
    )

    assert (
        results[3].lip_sync_required
        is False
    )


def test_music_video_lip_sync_override():
    """A vocal section should support a deliberate B-roll override."""

    structure = MusicVideoStructure(
        sections=[
            make_section(
                section_id=1,
                section_type="verse",
                performance_mode="vocal",
                start_seconds=0,
                end_seconds=15,
                scene_ids=[1],
            ),
        ]
    )

    results = resolve_music_video_lip_sync(
        structure,
        overrides={
            1: "disabled",
        },
    )

    assert (
        results[0].lip_sync_mode
        == "disabled"
    )

    assert (
        results[0].vocal_audio_expected
        is True
    )

    assert results[0].warnings


def test_unknown_override_section_is_rejected():
    """Overrides must reference real music-section IDs."""

    structure = MusicVideoStructure(
        sections=[
            make_section(
                section_id=1,
                section_type="verse",
                performance_mode="vocal",
                start_seconds=0,
                end_seconds=15,
                scene_ids=[1],
            ),
        ]
    )

    with pytest.raises(
        ValueError,
        match=(
            "lip-sync overrides reference "
            "unknown section_id: 99"
        ),
    ):
        resolve_music_video_lip_sync(
            structure,
            overrides={
                99: "disabled",
            },
        )


def test_lip_sync_result_serialization():
    """Resolved policies should serialize cleanly."""

    section = make_section(
        section_id=1,
        section_type="chorus",
        performance_mode="vocal",
    )

    result = resolve_lip_sync_policy(
        section
    )

    data = result.to_dict()

    assert data["section_id"] == 1
    assert data["section_type"] == "chorus"
    assert data["performance_mode"] == "vocal"
    assert data["lip_sync_mode"] == "required"
    assert data["lip_sync_required"] is True

    assert (
        data["singing_mouth_movement_allowed"]
        is True
    )
