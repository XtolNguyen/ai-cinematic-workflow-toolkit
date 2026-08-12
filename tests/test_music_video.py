from ai_cinematic_workflow.music_video import (
    MusicSection,
    MusicVideoStructure,
    normalize_music_token,
)


def test_normalize_music_token():
    """Section and mode names should normalize consistently."""

    assert normalize_music_token("Pre Chorus") == "pre-chorus"
    assert normalize_music_token("FINAL_CHORUS") == "final-chorus"
    assert normalize_music_token("Performance Only") == "performance-only"


def test_vocal_section_detection():
    """Vocal sections should require vocal performance."""

    section = MusicSection(
        section_id=1,
        section_type="verse",
        start_seconds=15,
        end_seconds=30,
        performance_mode="vocal",
        scene_ids=[2],
    )

    assert section.is_valid()
    assert section.requires_vocal_performance


def test_instrumental_section_detection():
    """Instrumental sections must not require vocal performance."""

    section = MusicSection(
        section_id=1,
        section_type="intro",
        start_seconds=0,
        end_seconds=15,
        performance_mode="instrumental",
        scene_ids=[1],
    )

    assert section.is_valid()
    assert not section.requires_vocal_performance


def test_section_duration():
    """Section duration should be calculated from start and end times."""

    section = MusicSection(
        section_id=1,
        section_type="chorus",
        start_seconds=30,
        end_seconds=60,
        performance_mode="vocal",
        scene_ids=[3, 4],
    )

    assert section.duration_seconds == 30


def test_valid_music_video_structure():
    """A complete intro/verse/chorus/outro structure should validate."""

    structure = MusicVideoStructure(
        sections=[
            MusicSection(
                section_id=1,
                section_type="intro",
                start_seconds=0,
                end_seconds=15,
                performance_mode="instrumental",
                scene_ids=[1],
            ),
            MusicSection(
                section_id=2,
                section_type="verse",
                start_seconds=15,
                end_seconds=30,
                performance_mode="vocal",
                scene_ids=[2],
            ),
            MusicSection(
                section_id=3,
                section_type="chorus",
                start_seconds=30,
                end_seconds=45,
                performance_mode="vocal",
                scene_ids=[3],
            ),
            MusicSection(
                section_id=4,
                section_type="outro",
                start_seconds=45,
                end_seconds=60,
                performance_mode="instrumental",
                scene_ids=[4],
            ),
        ]
    )

    assert structure.is_valid(
        project_scene_ids=[1, 2, 3, 4]
    )

    assert structure.validate(
        project_scene_ids=[1, 2, 3, 4]
    ) == []

    assert structure.section_count == 4
    assert structure.total_duration_seconds == 60


def test_music_video_summary():
    """Structure summary should count vocal and instrumental sections."""

    structure = MusicVideoStructure(
        sections=[
            MusicSection(
                section_id=1,
                section_type="intro",
                start_seconds=0,
                end_seconds=15,
                performance_mode="instrumental",
                scene_ids=[1],
            ),
            MusicSection(
                section_id=2,
                section_type="verse",
                start_seconds=15,
                end_seconds=30,
                performance_mode="vocal",
                scene_ids=[2],
            ),
            MusicSection(
                section_id=3,
                section_type="chorus",
                start_seconds=30,
                end_seconds=45,
                performance_mode="vocal",
                scene_ids=[3],
            ),
            MusicSection(
                section_id=4,
                section_type="outro",
                start_seconds=45,
                end_seconds=60,
                performance_mode="instrumental",
                scene_ids=[4],
            ),
        ]
    )

    data = structure.to_dict()

    assert data["summary"]["section_count"] == 4
    assert data["summary"]["total_duration_seconds"] == 60
    assert data["summary"]["mapped_scene_count"] == 4
    assert data["summary"]["vocal_section_count"] == 2
    assert data["summary"]["instrumental_section_count"] == 2


def test_get_section_for_scene():
    """Scene IDs should resolve to their assigned music section."""

    verse = MusicSection(
        section_id=2,
        section_type="verse",
        start_seconds=15,
        end_seconds=45,
        performance_mode="vocal",
        scene_ids=[2, 3],
    )

    structure = MusicVideoStructure(
        sections=[
            verse,
        ]
    )

    result = structure.get_section_for_scene(3)

    assert result is verse
    assert structure.get_section_for_scene(99) is None


def test_music_section_overlap_is_detected():
    """Overlapping music sections should be reported."""

    structure = MusicVideoStructure(
        sections=[
            MusicSection(
                section_id=1,
                section_type="intro",
                start_seconds=0,
                end_seconds=20,
                performance_mode="instrumental",
                scene_ids=[1],
            ),
            MusicSection(
                section_id=2,
                section_type="verse",
                start_seconds=15,
                end_seconds=30,
                performance_mode="vocal",
                scene_ids=[2],
            ),
        ]
    )

    errors = structure.validate()

    assert (
        "music sections overlap: 1 and 2"
        in errors
    )


def test_duplicate_scene_mapping_is_detected():
    """A scene cannot belong to multiple music sections."""

    structure = MusicVideoStructure(
        sections=[
            MusicSection(
                section_id=1,
                section_type="verse",
                start_seconds=0,
                end_seconds=15,
                performance_mode="vocal",
                scene_ids=[1],
            ),
            MusicSection(
                section_id=2,
                section_type="chorus",
                start_seconds=15,
                end_seconds=30,
                performance_mode="vocal",
                scene_ids=[1],
            ),
        ]
    )

    errors = structure.validate()

    assert (
        "scene assigned to multiple music sections: 1"
        in errors
    )


def test_unknown_project_scene_is_detected():
    """Music structure must not reference scenes absent from the project."""

    structure = MusicVideoStructure(
        sections=[
            MusicSection(
                section_id=1,
                section_type="verse",
                start_seconds=0,
                end_seconds=15,
                performance_mode="vocal",
                scene_ids=[99],
            ),
        ]
    )

    errors = structure.validate(
        project_scene_ids=[1]
    )

    assert (
        "music structure references unknown scene_id: 99"
        in errors
    )


def test_unmapped_project_scene_is_detected():
    """Every project scene should be mapped when project IDs are provided."""

    structure = MusicVideoStructure(
        sections=[
            MusicSection(
                section_id=1,
                section_type="intro",
                start_seconds=0,
                end_seconds=15,
                performance_mode="instrumental",
                scene_ids=[1],
            ),
        ]
    )

    errors = structure.validate(
        project_scene_ids=[1, 2]
    )

    assert (
        "project scene is not mapped to a music section: 2"
        in errors
    )


def test_invalid_performance_mode_is_detected():
    """Unsupported performance modes should fail validation."""

    section = MusicSection(
        section_id=1,
        section_type="verse",
        start_seconds=0,
        end_seconds=15,
        performance_mode="singing-mode",
        scene_ids=[1],
    )

    errors = section.validate()

    assert (
        "unsupported performance_mode: singing-mode"
        in errors
    )


def test_custom_section_requires_label():
    """Custom sections should provide a descriptive label."""

    section = MusicSection(
        section_id=1,
        section_type="custom",
        start_seconds=0,
        end_seconds=15,
        performance_mode="cinematic-only",
        scene_ids=[1],
    )

    errors = section.validate()

    assert (
        "custom music sections require a label"
        in errors
    )


def test_valid_custom_section():
    """Custom sections with labels should validate."""

    section = MusicSection(
        section_id=1,
        section_type="custom",
        label="Ambient Dream Sequence",
        start_seconds=0,
        end_seconds=15,
        performance_mode="cinematic-only",
        scene_ids=[1],
    )

    assert section.is_valid()


def test_music_section_serialization():
    """Music sections should serialize normalized values."""

    section = MusicSection(
        section_id=1,
        section_type="Pre Chorus",
        start_seconds=15,
        end_seconds=30,
        performance_mode="Performance Only",
        scene_ids=[2],
    )

    data = section.to_dict()

    assert data["section_type"] == "pre-chorus"
    assert data["performance_mode"] == "performance-only"
    assert data["duration_seconds"] == 15
    assert data["requires_vocal_performance"] is False
