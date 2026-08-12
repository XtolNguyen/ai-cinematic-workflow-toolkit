import pytest

from ai_cinematic_workflow import Camera, Scene
from ai_cinematic_workflow.timeline import (
    build_timeline,
    format_timestamp,
)


def make_scene(
    scene_id: int,
    *,
    duration_seconds: float = 15,
) -> Scene:
    """Create a reusable scene for timeline tests."""

    return Scene(
        scene_id=scene_id,
        duration_seconds=duration_seconds,
        location="Cinematic studio",
        camera=Camera(
            shot="medium shot",
            movement="slow dolly in",
            lens="50mm",
        ),
        characters=["Lead performer"],
        lighting="Soft cinematic lighting",
        mood="Emotional",
    )


def test_automatic_continuous_timeline():
    """Scenes should be placed continuously by default."""

    scenes = [
        make_scene(
            1,
            duration_seconds=15,
        ),
        make_scene(
            2,
            duration_seconds=15,
        ),
        make_scene(
            3,
            duration_seconds=30,
        ),
    ]

    result = build_timeline(scenes)

    assert result.scene_count == 3
    assert result.total_duration_seconds == 60
    assert result.issues == []

    assert result.entries[0].start_seconds == 0
    assert result.entries[0].end_seconds == 15

    assert result.entries[1].start_seconds == 15
    assert result.entries[1].end_seconds == 30

    assert result.entries[2].start_seconds == 30
    assert result.entries[2].end_seconds == 60


def test_timestamp_formatting():
    """Timeline timestamps should use HH:MM:SS formatting."""

    assert format_timestamp(0) == "00:00:00"
    assert format_timestamp(15) == "00:00:15"
    assert format_timestamp(60) == "00:01:00"
    assert format_timestamp(3600) == "01:00:00"

    assert format_timestamp(15.5) == "00:00:15.50"


def test_negative_timestamp_is_rejected():
    """Negative timestamps should not be accepted."""

    with pytest.raises(
        ValueError,
        match="timestamp seconds cannot be negative",
    ):
        format_timestamp(-1)


def test_timeline_gap_detection():
    """An explicit late start should create a gap issue."""

    scenes = [
        make_scene(
            1,
            duration_seconds=15,
        ),
        make_scene(
            2,
            duration_seconds=15,
        ),
    ]

    result = build_timeline(
        scenes,
        start_times={
            1: 0,
            2: 20,
        },
    )

    assert len(result.issues) == 1

    issue = result.issues[0]

    assert issue.issue_type == "gap"
    assert issue.previous_scene_id == 1
    assert issue.scene_id == 2
    assert issue.duration_seconds == 5


def test_timeline_overlap_detection():
    """An explicit early start should create an overlap issue."""

    scenes = [
        make_scene(
            1,
            duration_seconds=15,
        ),
        make_scene(
            2,
            duration_seconds=15,
        ),
    ]

    result = build_timeline(
        scenes,
        start_times={
            1: 0,
            2: 12,
        },
    )

    assert len(result.issues) == 1

    issue = result.issues[0]

    assert issue.issue_type == "overlap"
    assert issue.previous_scene_id == 1
    assert issue.scene_id == 2
    assert issue.duration_seconds == 3


def test_scene_order_issue_is_detected():
    """Non-increasing scene IDs should produce an ordering issue."""

    scenes = [
        make_scene(2),
        make_scene(1),
    ]

    result = build_timeline(scenes)

    issue_types = {
        issue.issue_type
        for issue in result.issues
    }

    assert "scene_order" in issue_types


def test_duplicate_scene_ids_are_rejected():
    """Duplicate scene IDs should raise an error."""

    scenes = [
        make_scene(1),
        make_scene(1),
    ]

    with pytest.raises(
        ValueError,
        match="duplicate scene_id: 1",
    ):
        build_timeline(scenes)


def test_invalid_scene_is_rejected():
    """Invalid scene data should stop timeline generation."""

    scenes = [
        make_scene(
            1,
            duration_seconds=0,
        ),
    ]

    with pytest.raises(
        ValueError,
        match="Scene 1 validation failed",
    ):
        build_timeline(scenes)


def test_negative_explicit_start_time_is_rejected():
    """Explicit scene start times cannot be negative."""

    scenes = [
        make_scene(1),
    ]

    with pytest.raises(
        ValueError,
        match="start time cannot be negative",
    ):
        build_timeline(
            scenes,
            start_times={
                1: -5,
            },
        )


def test_timeline_result_serialization():
    """Timeline results should be serializable."""

    scenes = [
        make_scene(1),
        make_scene(2),
    ]

    result = build_timeline(scenes)
    data = result.to_dict()

    assert data["summary"]["scene_count"] == 2
    assert data["summary"]["total_duration_seconds"] == 30
    assert data["summary"]["issue_count"] == 0

    assert len(data["entries"]) == 2
    assert data["entries"][0]["scene_id"] == 1
    assert data["entries"][1]["scene_id"] == 2
