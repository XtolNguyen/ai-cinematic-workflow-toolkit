import json

from ai_cinematic_workflow import (
    Camera,
    CinematicProject,
    MusicSection,
    MusicVideoStructure,
    ProjectMetadata,
    Scene,
)
from ai_cinematic_workflow.exporters.project_json_exporter import (
    project_to_dict,
    project_to_json,
)


def make_scene(
    scene_id: int,
) -> Scene:
    """Create a reusable 15-second music-video scene."""

    return Scene(
        scene_id=scene_id,
        duration_seconds=15,
        location="Cinematic performance stage",
        camera=Camera(
            shot="medium shot",
            movement="slow dolly in",
            lens="50mm",
        ),
        characters=["Lead performer"],
        performance="Natural cinematic performance",
        lighting="Soft cinematic lighting",
        mood="Emotional",
        continuity={
            "wardrobe": "black cinematic outfit",
            "hair": "long dark hair",
        },
        negative_constraints=[
            "distorted face",
            "extra fingers",
            "camera jitter",
        ],
    )


def make_music_video_structure() -> MusicVideoStructure:
    """Create a four-section music-video structure."""

    return MusicVideoStructure(
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


def make_music_video_project() -> CinematicProject:
    """Create a complete four-scene music-video project."""

    return CinematicProject(
        metadata=ProjectMetadata(
            title="Music Video Integration Test",
            project_type="music-video",
            language="en",
            target_platform="AI video",
            aspect_ratio="16:9",
            frame_rate=24,
        ),
        scenes=[
            make_scene(1),
            make_scene(2),
            make_scene(3),
            make_scene(4),
        ],
        music_video_structure=(
            make_music_video_structure()
        ),
    )


def test_music_video_project_is_valid():
    """A correctly mapped music-video project should validate."""

    project = make_music_video_project()

    assert project.is_music_video
    assert project.is_valid()
    assert project.validate() == []

    assert project.scene_count == 4

    assert (
        project.total_duration_seconds
        == 60
    )


def test_music_video_structure_maps_all_project_scenes():
    """Every project scene should resolve to a musical section."""

    project = make_music_video_project()

    structure = project.music_video_structure

    assert structure is not None

    assert structure.mapped_scene_ids == [
        1,
        2,
        3,
        4,
    ]

    assert (
        structure.get_section_for_scene(
            1
        ).normalized_section_type
        == "intro"
    )

    assert (
        structure.get_section_for_scene(
            2
        ).normalized_section_type
        == "verse"
    )

    assert (
        structure.get_section_for_scene(
            3
        ).normalized_section_type
        == "chorus"
    )

    assert (
        structure.get_section_for_scene(
            4
        ).normalized_section_type
        == "outro"
    )


def test_vocal_and_instrumental_modes_are_preserved():
    """Vocal requirements should match the musical structure."""

    project = make_music_video_project()

    structure = project.music_video_structure

    assert structure is not None

    intro = structure.get_section_for_scene(1)
    verse = structure.get_section_for_scene(2)
    chorus = structure.get_section_for_scene(3)
    outro = structure.get_section_for_scene(4)

    assert intro is not None
    assert verse is not None
    assert chorus is not None
    assert outro is not None

    assert (
        intro.requires_vocal_performance
        is False
    )

    assert (
        verse.requires_vocal_performance
        is True
    )

    assert (
        chorus.requires_vocal_performance
        is True
    )

    assert (
        outro.requires_vocal_performance
        is False
    )


def test_project_serialization_contains_music_video_structure():
    """Project serialization should include music-video metadata."""

    project = make_music_video_project()

    data = project.to_dict()

    assert data["summary"]["is_music_video"] is True

    music_video = data["music_video"]

    assert (
        music_video["summary"]["section_count"]
        == 4
    )

    assert (
        music_video["summary"][
            "total_duration_seconds"
        ]
        == 60
    )

    assert (
        music_video["summary"][
            "mapped_scene_count"
        ]
        == 4
    )

    assert (
        music_video["summary"][
            "vocal_section_count"
        ]
        == 2
    )

    assert (
        music_video["summary"][
            "instrumental_section_count"
        ]
        == 2
    )


def test_complete_project_export_contains_music_video_data():
    """Complete project export should preserve music structure."""

    project = make_music_video_project()

    data = project_to_dict(project)

    assert "music_video" in data["project"]

    music_video = data["project"]["music_video"]

    assert len(
        music_video["sections"]
    ) == 4

    assert (
        music_video["sections"][0][
            "performance_mode"
        ]
        == "instrumental"
    )

    assert (
        music_video["sections"][1][
            "performance_mode"
        ]
        == "vocal"
    )

    assert (
        music_video["sections"][2][
            "performance_mode"
        ]
        == "vocal"
    )

    assert (
        music_video["sections"][3][
            "performance_mode"
        ]
        == "instrumental"
    )


def test_complete_json_contains_project_timeline_and_music_video():
    """
    Complete JSON should contain project,
    cinematic timeline, music structure and workflow.
    """

    project = make_music_video_project()

    content = project_to_json(project)
    data = json.loads(content)

    assert "project" in data
    assert "timeline" in data
    assert "workflow" in data

    assert "music_video" in data["project"]

    assert (
        data["timeline"]["summary"][
            "scene_count"
        ]
        == 4
    )

    assert (
        data["timeline"]["summary"][
            "total_duration_seconds"
        ]
        == 60
    )

    assert (
        data["project"]["music_video"][
            "summary"
        ]["section_count"]
        == 4
    )


def test_unknown_music_video_scene_invalidates_project():
    """
    Music structures referencing unknown scenes
    should invalidate the complete project.
    """

    structure = MusicVideoStructure(
        sections=[
            MusicSection(
                section_id=1,
                section_type="intro",
                start_seconds=0,
                end_seconds=15,
                performance_mode="instrumental",
                scene_ids=[99],
            ),
        ]
    )

    project = CinematicProject(
        metadata=ProjectMetadata(
            title="Invalid Music Video",
            project_type="music-video",
        ),
        scenes=[
            make_scene(1),
        ],
        music_video_structure=structure,
    )

    errors = project.validate()

    assert not project.is_valid()

    assert (
        "music_video: music structure "
        "references unknown scene_id: 99"
        in errors
    )

    assert (
        "music_video: project scene is not "
        "mapped to a music section: 1"
        in errors
    )
