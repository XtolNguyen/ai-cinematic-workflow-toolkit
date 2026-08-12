from ai_cinematic_workflow import Camera, Scene
from ai_cinematic_workflow.project import (
    CinematicProject,
    ProjectMetadata,
)


def make_scene(
    scene_id: int,
    *,
    duration_seconds: float = 15,
    location: str = "Cinematic studio",
) -> Scene:
    """Create a reusable scene for project tests."""

    return Scene(
        scene_id=scene_id,
        duration_seconds=duration_seconds,
        location=location,
        camera=Camera(
            shot="medium shot",
            movement="slow dolly in",
            lens="50mm",
        ),
        characters=["Lead performer"],
        lighting="Soft cinematic lighting",
        mood="Emotional",
    )


def make_metadata(
    title: str = "Test Cinematic Project",
) -> ProjectMetadata:
    """Create reusable project metadata."""

    return ProjectMetadata(
        title=title,
        project_type="music-video",
        description="Automated project model test",
        language="en",
        target_platform="AI video",
        aspect_ratio="16:9",
        frame_rate=24,
    )


def test_valid_project():
    """A project with valid metadata and scenes should pass validation."""

    project = CinematicProject(
        metadata=make_metadata(),
        scenes=[
            make_scene(1),
            make_scene(2),
        ],
    )

    assert project.is_valid()
    assert project.validate() == []


def test_project_scene_count():
    """Project should report the correct number of scenes."""

    project = CinematicProject(
        metadata=make_metadata(),
        scenes=[
            make_scene(1),
            make_scene(2),
            make_scene(3),
        ],
    )

    assert project.scene_count == 3


def test_project_total_duration():
    """Project should calculate total scene duration."""

    project = CinematicProject(
        metadata=make_metadata(),
        scenes=[
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
        ],
    )

    assert project.total_duration_seconds == 60


def test_project_rejects_empty_title():
    """A project must contain a non-empty title."""

    project = CinematicProject(
        metadata=make_metadata(
            title="",
        ),
        scenes=[
            make_scene(1),
        ],
    )

    errors = project.validate()

    assert "project title cannot be empty" in errors
    assert not project.is_valid()


def test_project_requires_at_least_one_scene():
    """A project with no scenes should fail validation."""

    project = CinematicProject(
        metadata=make_metadata(),
        scenes=[],
    )

    errors = project.validate()

    assert (
        "project must contain at least one scene"
        in errors
    )

    assert not project.is_valid()


def test_duplicate_scene_ids_are_detected():
    """Duplicate scene IDs should be reported."""

    project = CinematicProject(
        metadata=make_metadata(),
        scenes=[
            make_scene(1),
            make_scene(1),
        ],
    )

    errors = project.validate()

    assert "duplicate scene_id: 1" in errors


def test_invalid_scene_is_reported():
    """Scene validation errors should appear at project level."""

    project = CinematicProject(
        metadata=make_metadata(),
        scenes=[
            make_scene(
                1,
                duration_seconds=0,
            ),
        ],
    )

    errors = project.validate()

    assert (
        "scene 1: duration_seconds must be greater than 0"
        in errors
    )


def test_add_scene():
    """Scenes should be appendable after project creation."""

    project = CinematicProject(
        metadata=make_metadata(),
    )

    project.add_scene(
        make_scene(1)
    )

    assert project.scene_count == 1
    assert project.scenes[0].scene_id == 1


def test_project_serialization():
    """Project should serialize metadata, summary and scenes."""

    project = CinematicProject(
        metadata=make_metadata(),
        scenes=[
            make_scene(1),
            make_scene(2),
        ],
    )

    data = project.to_dict()

    assert data["metadata"]["title"] == (
        "Test Cinematic Project"
    )

    assert data["metadata"]["project_type"] == (
        "music-video"
    )

    assert data["summary"]["scene_count"] == 2

    assert (
        data["summary"]["total_duration_seconds"]
        == 30
    )

    assert len(data["scenes"]) == 2
    assert data["scenes"][0]["scene_id"] == 1
    assert data["scenes"][1]["scene_id"] == 2
