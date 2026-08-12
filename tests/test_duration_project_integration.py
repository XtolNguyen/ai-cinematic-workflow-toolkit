import json

from ai_cinematic_workflow import (
    Camera,
    CinematicProject,
    DurationPolicy,
    MusicSection,
    MusicVideoStructure,
    ProjectMetadata,
    Scene,
)
from ai_cinematic_workflow.exporters.project_json_exporter import (
    project_to_dict,
    project_to_json,
    save_project_json,
)


def make_scene(
    scene_id: int,
    duration_seconds: float = 15,
) -> Scene:
    """Create a reusable cinematic scene."""

    return Scene(
        scene_id=scene_id,
        duration_seconds=duration_seconds,
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


def make_duration_policy() -> DurationPolicy:
    """Create a strict reusable 15-second workflow policy."""

    return DurationPolicy(
        preferred_scene_duration=15,
        allowed_scene_durations=[15],
        tolerance_seconds=0.25,
        strict=True,
    )


def make_music_video_structure() -> MusicVideoStructure:
    """Create a standard 60-second music-video structure."""

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


def make_valid_music_video_project() -> CinematicProject:
    """Create a correctly aligned 60-second MV."""

    return CinematicProject(
        metadata=ProjectMetadata(
            title="Duration Integration MV",
            project_type="music-video",
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


def test_valid_music_video_export_contains_duration_validation():
    """
    A valid MV should export complete timing validation
    with no duration issues.
    """

    project = (
        make_valid_music_video_project()
    )

    data = project_to_dict(
        project,
        duration_policy=(
            make_duration_policy()
        ),
    )

    assert "duration_validation" in data

    validation = data[
        "duration_validation"
    ]

    assert (
        validation["mode"]
        == "music_video_timing"
    )

    summary = validation["summary"]

    assert summary["valid"] is True
    assert summary["issue_count"] == 0
    assert summary["scene_count"] == 4
    assert summary["section_count"] == 4

    assert (
        summary[
            "cinematic_duration_seconds"
        ]
        == 60
    )

    assert (
        summary[
            "music_duration_seconds"
        ]
        == 60
    )

    assert (
        summary[
            "scene_duration_issue_count"
        ]
        == 0
    )

    assert (
        summary[
            "section_alignment_issue_count"
        ]
        == 0
    )

    assert (
        summary["runtime_issue_count"]
        == 0
    )

    assert validation["issues"] == []


def test_invalid_music_video_export_reports_timing_issues():
    """
    A short scene should create scene, section,
    and total-runtime validation issues.
    """

    project = CinematicProject(
        metadata=ProjectMetadata(
            title="Misaligned Duration MV",
            project_type="music-video",
        ),
        scenes=[
            make_scene(1, 15),
            make_scene(2, 12),
            make_scene(3, 15),
            make_scene(4, 15),
        ],
        music_video_structure=(
            make_music_video_structure()
        ),
    )

    data = project_to_dict(
        project,
        duration_policy=(
            make_duration_policy()
        ),
    )

    validation = data[
        "duration_validation"
    ]

    summary = validation["summary"]

    assert summary["valid"] is False
    assert summary["issue_count"] > 0

    assert (
        summary[
            "scene_duration_issue_count"
        ]
        > 0
    )

    assert (
        summary[
            "section_alignment_issue_count"
        ]
        > 0
    )

    assert (
        summary["runtime_issue_count"]
        == 1
    )

    assert (
        summary[
            "cinematic_duration_seconds"
        ]
        == 57
    )

    assert (
        summary[
            "music_duration_seconds"
        ]
        == 60
    )

    issue_types = {
        issue["issue_type"]
        for issue in validation["issues"]
    }

    assert (
        "disallowed_duration"
        in issue_types
    )

    assert (
        "preferred_duration_mismatch"
        in issue_types
    )

    assert (
        "section_duration_mismatch"
        in issue_types
    )

    assert (
        "project_runtime_mismatch"
        in issue_types
    )


def test_regular_cinematic_project_uses_scene_duration_mode():
    """
    A regular cinematic project should receive
    scene-duration validation without MV timing logic.
    """

    project = CinematicProject(
        metadata=ProjectMetadata(
            title="Regular Cinematic Project",
            project_type="cinematic",
        ),
        scenes=[
            make_scene(1, 15),
            make_scene(2, 15),
        ],
    )

    data = project_to_dict(
        project,
        duration_policy=(
            make_duration_policy()
        ),
    )

    validation = data[
        "duration_validation"
    ]

    assert (
        validation["mode"]
        == "scene_duration"
    )

    assert (
        validation["summary"]["valid"]
        is True
    )

    assert (
        validation["summary"][
            "scene_count"
        ]
        == 2
    )

    assert (
        validation["summary"][
            "issue_count"
        ]
        == 0
    )

    assert len(
        validation["scene_results"]
    ) == 2

    assert validation["issues"] == []


def test_regular_cinematic_project_reports_bad_scene_duration():
    """
    Regular cinematic projects should report
    duration-policy violations per scene.
    """

    project = CinematicProject(
        metadata=ProjectMetadata(
            title="Invalid Duration Film",
            project_type="cinematic",
        ),
        scenes=[
            make_scene(1, 15),
            make_scene(2, 12),
        ],
    )

    data = project_to_dict(
        project,
        duration_policy=(
            make_duration_policy()
        ),
    )

    validation = data[
        "duration_validation"
    ]

    assert (
        validation["summary"]["valid"]
        is False
    )

    assert (
        validation["summary"][
            "issue_count"
        ]
        == 2
    )

    second_scene = (
        validation["scene_results"][1]
    )

    assert second_scene["valid"] is False
    assert second_scene["issue_count"] == 2

    issue_types = {
        issue["issue_type"]
        for issue in second_scene["issues"]
    }

    assert issue_types == {
        "disallowed_duration",
        "preferred_duration_mismatch",
    }


def test_export_without_duration_policy_is_backward_compatible():
    """
    Existing callers should receive no duration-validation
    block when no DurationPolicy is supplied.
    """

    project = (
        make_valid_music_video_project()
    )

    data = project_to_dict(
        project
    )

    assert (
        "duration_validation"
        not in data
    )

    assert "project" in data
    assert "timeline" in data
    assert "workflow" in data

    assert (
        "music_video"
        in data["project"]
    )

    assert (
        "lip_sync_policies"
        in data["project"]["music_video"]
    )


def test_complete_json_preserves_duration_validation():
    """
    JSON serialization should preserve the complete
    duration-validation result.
    """

    project = (
        make_valid_music_video_project()
    )

    content = project_to_json(
        project,
        duration_policy=(
            make_duration_policy()
        ),
    )

    data = json.loads(content)

    validation = data[
        "duration_validation"
    ]

    assert (
        validation["mode"]
        == "music_video_timing"
    )

    assert (
        validation["summary"]["valid"]
        is True
    )

    assert (
        validation["policy"][
            "preferred_scene_duration"
        ]
        == 15
    )

    assert (
        validation["policy"][
            "allowed_scene_durations"
        ]
        == [15]
    )

    assert (
        validation["policy"][
            "tolerance_seconds"
        ]
        == 0.25
    )

    assert (
        validation["policy"]["strict"]
        is True
    )


def test_saved_project_json_preserves_duration_validation(
    tmp_path,
):
    """
    Saving and reading a project JSON file should
    preserve duration-validation data.
    """

    project = (
        make_valid_music_video_project()
    )

    output_path = (
        tmp_path
        / "duration"
        / "project.json"
    )

    saved_path = save_project_json(
        project,
        output_path,
        duration_policy=(
            make_duration_policy()
        ),
    )

    data = json.loads(
        saved_path.read_text(
            encoding="utf-8"
        )
    )

    assert (
        "duration_validation"
        in data
    )

    assert (
        data["duration_validation"][
            "mode"
        ]
        == "music_video_timing"
    )

    assert (
        data["duration_validation"][
            "summary"
        ]["valid"]
        is True
    )

    assert (
        data["duration_validation"][
            "summary"
        ][
            "cinematic_duration_seconds"
        ]
        == 60
    )
