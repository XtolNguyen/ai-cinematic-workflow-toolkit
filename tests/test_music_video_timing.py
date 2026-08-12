import pytest

from ai_cinematic_workflow.duration import (
    DurationPolicy,
)
from ai_cinematic_workflow.music_video import (
    MusicSection,
    MusicVideoStructure,
)
from ai_cinematic_workflow.music_video_timing import (
    validate_music_video_timing,
)
from ai_cinematic_workflow.scene import (
    Camera,
    Scene,
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


def make_strict_15_second_policy(
    tolerance_seconds: float = 0.0,
) -> DurationPolicy:
    """Create a reusable strict 15-second duration policy."""

    return DurationPolicy(
        preferred_scene_duration=15,
        allowed_scene_durations=[15],
        tolerance_seconds=tolerance_seconds,
        strict=True,
    )


def make_standard_structure() -> MusicVideoStructure:
    """Create a standard four-section 60-second MV."""

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


def test_valid_music_video_timing():
    """A perfectly aligned 60-second MV should pass."""

    scenes = [
        make_scene(1),
        make_scene(2),
        make_scene(3),
        make_scene(4),
    ]

    structure = make_standard_structure()

    policy = make_strict_15_second_policy()

    result = validate_music_video_timing(
        scenes,
        structure,
        policy,
    )

    assert result.is_valid
    assert result.issue_count == 0
    assert result.issues == []

    assert result.scene_count == 4
    assert result.section_count == 4

    assert (
        result.cinematic_duration_seconds
        == 60
    )

    assert (
        result.music_duration_seconds
        == 60
    )


def test_short_scene_produces_duration_and_alignment_issues():
    """
    A short scene should affect both its duration policy
    and downstream music-video timing.
    """

    scenes = [
        make_scene(1, 15),
        make_scene(2, 12),
        make_scene(3, 15),
        make_scene(4, 15),
    ]

    result = validate_music_video_timing(
        scenes,
        make_standard_structure(),
        make_strict_15_second_policy(),
    )

    issue_types = {
        issue.issue_type
        for issue in result.issues
    }

    assert result.is_valid is False

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
        "section_end_mismatch"
        in issue_types
    )

    assert (
        "scene_outside_music_section"
        in issue_types
    )

    assert (
        "project_runtime_mismatch"
        in issue_types
    )

    assert (
        result.cinematic_duration_seconds
        == 57
    )

    assert (
        result.music_duration_seconds
        == 60
    )


def test_scene_outside_assigned_music_section_is_detected():
    """Scene timing outside its assigned section should fail."""

    scenes = [
        make_scene(1, 10),
        make_scene(2, 20),
    ]

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
        ]
    )

    policy = DurationPolicy(
        minimum_scene_duration=1,
        maximum_scene_duration=30,
    )

    result = validate_music_video_timing(
        scenes,
        structure,
        policy,
    )

    issue_types = {
        issue.issue_type
        for issue in result.issues
    }

    assert (
        "scene_outside_music_section"
        in issue_types
    )

    assert (
        "section_start_mismatch"
        in issue_types
    )


def test_section_duration_mismatch_is_detected():
    """Mapped cinematic duration must match section duration."""

    scenes = [
        make_scene(1, 10),
        make_scene(2, 20),
    ]

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
        ]
    )

    result = validate_music_video_timing(
        scenes,
        structure,
        DurationPolicy(),
    )

    mismatches = [
        issue
        for issue in result.issues
        if (
            issue.issue_type
            == "section_duration_mismatch"
        )
    ]

    assert len(mismatches) == 2


def test_project_runtime_mismatch_is_detected():
    """Cinematic and music runtimes must align."""

    scenes = [
        make_scene(1, 15),
        make_scene(2, 15),
        make_scene(3, 15),
        make_scene(4, 10),
    ]

    result = validate_music_video_timing(
        scenes,
        make_standard_structure(),
        DurationPolicy(),
    )

    runtime_issues = [
        issue
        for issue in result.issues
        if (
            issue.issue_type
            == "project_runtime_mismatch"
        )
    ]

    assert len(runtime_issues) == 1

    issue = runtime_issues[0]

    assert issue.expected_duration == 60
    assert issue.actual_duration == 55
    assert issue.difference_seconds == -5


def test_tolerance_accepts_small_timing_differences():
    """
    Small cumulative timing differences should pass
    when they remain within configured tolerance.
    """

    scenes = [
        make_scene(1, 14.9),
        make_scene(2, 15.1),
        make_scene(3, 14.9),
        make_scene(4, 15.1),
    ]

    policy = make_strict_15_second_policy(
        tolerance_seconds=0.25,
    )

    result = validate_music_video_timing(
        scenes,
        make_standard_structure(),
        policy,
    )

    assert result.is_valid
    assert result.issue_count == 0

    assert (
        result.cinematic_duration_seconds
        == pytest.approx(60)
    )


def test_tolerance_rejects_large_timing_difference():
    """Timing differences outside tolerance should fail."""

    scenes = [
        make_scene(1, 14.5),
        make_scene(2, 15.5),
        make_scene(3, 14.5),
        make_scene(4, 15.5),
    ]

    policy = make_strict_15_second_policy(
        tolerance_seconds=0.25,
    )

    result = validate_music_video_timing(
        scenes,
        make_standard_structure(),
        policy,
    )

    assert result.is_valid is False

    assert result.issue_count > 0


def test_result_counts_issue_scopes():
    """Validation result should summarize issue scopes."""

    scenes = [
        make_scene(1, 15),
        make_scene(2, 12),
        make_scene(3, 15),
        make_scene(4, 15),
    ]

    result = validate_music_video_timing(
        scenes,
        make_standard_structure(),
        make_strict_15_second_policy(),
    )

    assert (
        result.scene_duration_issue_count
        > 0
    )

    assert (
        result.section_alignment_issue_count
        > 0
    )

    assert (
        result.runtime_issue_count
        == 1
    )


def test_result_serialization():
    """Timing validation results should serialize cleanly."""

    scenes = [
        make_scene(1),
        make_scene(2),
        make_scene(3),
        make_scene(4),
    ]

    result = validate_music_video_timing(
        scenes,
        make_standard_structure(),
        make_strict_15_second_policy(),
    )

    data = result.to_dict()

    assert data["summary"]["valid"] is True
    assert data["summary"]["issue_count"] == 0
    assert data["summary"]["scene_count"] == 4
    assert data["summary"]["section_count"] == 4

    assert (
        data["summary"][
            "cinematic_duration_seconds"
        ]
        == 60
    )

    assert (
        data["summary"][
            "music_duration_seconds"
        ]
        == 60
    )

    assert data["policy"][
        "preferred_scene_duration"
    ] == 15

    assert data["issues"] == []


def test_empty_scene_list_is_rejected():
    """Timing validation requires cinematic scenes."""

    with pytest.raises(
        ValueError,
        match=(
            "music-video timing validation "
            "requires at least one scene"
        ),
    ):
        validate_music_video_timing(
            [],
            make_standard_structure(),
            DurationPolicy(),
        )


def test_duplicate_scene_ids_are_rejected():
    """Project scenes must use unique IDs."""

    scenes = [
        make_scene(1),
        make_scene(1),
    ]

    structure = MusicVideoStructure(
        sections=[
            MusicSection(
                section_id=1,
                section_type="verse",
                start_seconds=0,
                end_seconds=30,
                performance_mode="vocal",
                scene_ids=[1],
            ),
        ]
    )

    with pytest.raises(
        ValueError,
        match=(
            "music-video timing validation "
            "requires unique scene IDs"
        ),
    ):
        validate_music_video_timing(
            scenes,
            structure,
            DurationPolicy(),
        )


def test_invalid_duration_policy_is_rejected():
    """Invalid policy configuration should fail immediately."""

    scenes = [
        make_scene(1),
    ]

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

    policy = DurationPolicy(
        minimum_scene_duration=30,
        maximum_scene_duration=10,
    )

    with pytest.raises(
        ValueError,
        match="Invalid duration policy",
    ):
        validate_music_video_timing(
            scenes,
            structure,
            policy,
        )


def test_invalid_music_video_mapping_is_rejected():
    """Music structures must map existing project scenes."""

    scenes = [
        make_scene(1),
    ]

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

    with pytest.raises(
        ValueError,
        match=(
            "Invalid music-video structure"
        ),
    ):
        validate_music_video_timing(
            scenes,
            structure,
            DurationPolicy(),
        )
