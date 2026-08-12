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


def make_scene(scene_id: int) -> Scene:
    """Create a reusable 15-second cinematic scene."""

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
        },
        negative_constraints=[
            "distorted face",
            "camera jitter",
        ],
    )


def make_music_video_project() -> CinematicProject:
    """Create a complete MV with vocal and instrumental sections."""

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

    return CinematicProject(
        metadata=ProjectMetadata(
            title="Lip Sync Integration Test",
            project_type="music-video",
        ),
        scenes=[
            make_scene(1),
            make_scene(2),
            make_scene(3),
            make_scene(4),
        ],
        music_video_structure=structure,
    )


def test_project_export_contains_lip_sync_policies():
    """MV exports should contain resolved lip-sync policies."""

    project = make_music_video_project()

    data = project_to_dict(project)

    policies_data = (
        data["project"]["music_video"][
            "lip_sync_policies"
        ]
    )

    summary = policies_data["summary"]

    assert summary["policy_count"] == 4
    assert summary["required_count"] == 2
    assert summary["disabled_count"] == 2
    assert summary["warning_count"] == 0


def test_intro_and_outro_disable_lip_sync():
    """Instrumental intro and outro must reject singing behavior."""

    project = make_music_video_project()

    data = project_to_dict(project)

    policies = (
        data["project"]["music_video"][
            "lip_sync_policies"
        ]["policies"]
    )

    intro = policies[0]
    outro = policies[3]

    assert intro["section_type"] == "intro"
    assert intro["lip_sync_mode"] == "disabled"
    assert intro["lip_sync_required"] is False

    assert (
        intro["singing_mouth_movement_allowed"]
        is False
    )

    assert outro["section_type"] == "outro"
    assert outro["lip_sync_mode"] == "disabled"
    assert outro["lip_sync_required"] is False

    assert (
        outro["singing_mouth_movement_allowed"]
        is False
    )


def test_verse_and_chorus_require_lip_sync():
    """Visible vocal sections should receive required lip-sync."""

    project = make_music_video_project()

    data = project_to_dict(project)

    policies = (
        data["project"]["music_video"][
            "lip_sync_policies"
        ]["policies"]
    )

    verse = policies[1]
    chorus = policies[2]

    assert verse["section_type"] == "verse"
    assert verse["performance_mode"] == "vocal"
    assert verse["lip_sync_mode"] == "required"
    assert verse["lip_sync_required"] is True
    assert verse["vocal_audio_expected"] is True

    assert (
        verse["singing_mouth_movement_allowed"]
        is True
    )

    assert chorus["section_type"] == "chorus"
    assert chorus["performance_mode"] == "vocal"
    assert chorus["lip_sync_mode"] == "required"
    assert chorus["lip_sync_required"] is True

    assert (
        chorus["singing_mouth_movement_allowed"]
        is True
    )


def test_lip_sync_execution_instructions_are_exported():
    """Resolved execution instructions should survive export."""

    project = make_music_video_project()

    data = project_to_dict(project)

    policies = (
        data["project"]["music_video"][
            "lip_sync_policies"
        ]["policies"]
    )

    assert (
        "Do not lip-sync"
        in policies[0]["instruction"]
    )

    assert (
        "Perform precise natural lip-sync"
        in policies[1]["instruction"]
    )


def test_complete_json_preserves_lip_sync_policies():
    """Serialized JSON must preserve resolved policies."""

    project = make_music_video_project()

    content = project_to_json(project)
    data = json.loads(content)

    policies = (
        data["project"]["music_video"][
            "lip_sync_policies"
        ]["policies"]
    )

    assert len(policies) == 4

    assert [
        policy["lip_sync_mode"]
        for policy in policies
    ] == [
        "disabled",
        "required",
        "required",
        "disabled",
    ]


def test_regular_cinematic_project_has_no_lip_sync_data():
    """
    Non-music-video projects should not receive
    music-video or lip-sync policy data.
    """

    project = CinematicProject(
        metadata=ProjectMetadata(
            title="Regular Cinematic Project",
            project_type="cinematic",
        ),
        scenes=[
            make_scene(1),
        ],
    )

    data = project_to_dict(project)

    assert (
        data["project"]["summary"]["is_music_video"]
        is False
    )

    assert "music_video" not in data["project"]
