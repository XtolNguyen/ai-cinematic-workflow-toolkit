import json

from ai_cinematic_workflow import (
    Camera,
    CinematicProject,
    ContinuityProfile,
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
    *,
    wardrobe: str = "black cinematic outfit",
    hair: str = "long dark hair",
    lighting: str = "Warm cinematic light",
    location: str = "Cinematic studio",
) -> Scene:
    """Create a reusable cinematic scene."""

    return Scene(
        scene_id=scene_id,
        duration_seconds=15,
        location=location,
        camera=Camera(
            shot="medium shot",
            movement="slow dolly in",
            lens="50mm",
        ),
        characters=["Lead performer"],
        performance="Natural cinematic performance",
        lighting=lighting,
        mood="Emotional",
        continuity={
            "wardrobe": wardrobe,
            "hair": hair,
        },
        negative_constraints=[
            "distorted face",
            "camera jitter",
        ],
    )


def make_project(
    scenes: list[Scene],
) -> CinematicProject:
    """Create a reusable cinematic project."""

    return CinematicProject(
        metadata=ProjectMetadata(
            title="Advanced Continuity Integration Test",
            project_type="cinematic",
        ),
        scenes=scenes,
    )


def make_character_lock_profile() -> ContinuityProfile:
    """Create a continuity profile for character consistency."""

    return ContinuityProfile(
        name="character-lock",
        required_fields=[
            "wardrobe",
            "hair",
        ],
        warning_fields=[
            "lighting",
        ],
        strict=True,
    )


def test_clean_project_continuity_export():
    """
    A project with stable character continuity
    should export a valid continuity report.
    """

    project = make_project(
        [
            make_scene(1),
            make_scene(2),
            make_scene(3),
        ]
    )

    data = project_to_dict(
        project,
        continuity_profile=(
            make_character_lock_profile()
        ),
    )

    assert "continuity_validation" in data

    validation = data[
        "continuity_validation"
    ]

    assert (
        validation["mode"]
        == "advanced_continuity"
    )

    summary = validation["summary"]

    assert summary["valid"] is True
    assert summary["scene_count"] == 3
    assert summary["checked_pairs"] == 2
    assert summary["issue_count"] == 0
    assert summary["error_count"] == 0
    assert summary["warning_count"] == 0

    assert validation["issues"] == []


def test_wardrobe_error_and_lighting_warning_are_exported():
    """
    A wardrobe change should be an error while a configured
    lighting change should remain a warning.
    """

    project = make_project(
        [
            make_scene(
                1,
                wardrobe="black cinematic outfit",
                lighting="Warm sunset",
            ),
            make_scene(
                2,
                wardrobe="white cinematic outfit",
                lighting="Soft blue night",
            ),
        ]
    )

    data = project_to_dict(
        project,
        continuity_profile=(
            make_character_lock_profile()
        ),
    )

    validation = data[
        "continuity_validation"
    ]

    summary = validation["summary"]

    assert summary["valid"] is False
    assert summary["issue_count"] == 2
    assert summary["error_count"] == 1
    assert summary["warning_count"] == 1

    issues = validation["issues"]

    wardrobe_issue = next(
        issue
        for issue in issues
        if issue["field_name"] == "wardrobe"
    )

    lighting_issue = next(
        issue
        for issue in issues
        if issue["field_name"] == "lighting"
    )

    assert (
        wardrobe_issue["severity"]
        == "error"
    )

    assert (
        wardrobe_issue["previous_scene_id"]
        == 1
    )

    assert (
        wardrobe_issue["current_scene_id"]
        == 2
    )

    assert (
        wardrobe_issue["previous_value"]
        == "black cinematic outfit"
    )

    assert (
        wardrobe_issue["current_value"]
        == "white cinematic outfit"
    )

    assert (
        lighting_issue["severity"]
        == "warning"
    )

    assert (
        lighting_issue["previous_value"]
        == "Warm sunset"
    )

    assert (
        lighting_issue["current_value"]
        == "Soft blue night"
    )


def test_allowed_location_change_does_not_create_issue():
    """
    Intentional location changes should pass when explicitly
    allowed by the continuity profile.
    """

    project = make_project(
        [
            make_scene(
                1,
                location="Beach",
            ),
            make_scene(
                2,
                location="City",
            ),
        ]
    )

    profile = ContinuityProfile(
        name="location-transition",
        optional_fields=[
            "location",
        ],
        allowed_change_fields=[
            "location",
        ],
        strict=True,
    )

    data = project_to_dict(
        project,
        continuity_profile=profile,
    )

    validation = data[
        "continuity_validation"
    ]

    assert (
        validation["summary"]["valid"]
        is True
    )

    assert (
        validation["summary"]["issue_count"]
        == 0
    )

    assert validation["issues"] == []


def test_export_without_continuity_profile_is_backward_compatible():
    """
    Existing project exports should remain unchanged when no
    ContinuityProfile is supplied.
    """

    project = make_project(
        [
            make_scene(1),
            make_scene(2),
        ]
    )

    data = project_to_dict(
        project
    )

    assert (
        "continuity_validation"
        not in data
    )

    assert "project" in data
    assert "timeline" in data
    assert "workflow" in data


def test_complete_json_preserves_advanced_continuity():
    """
    JSON serialization should preserve advanced continuity
    configuration, issues, severities, and scene values.
    """

    project = make_project(
        [
            make_scene(
                1,
                wardrobe="black cinematic outfit",
                lighting="Warm sunset",
            ),
            make_scene(
                2,
                wardrobe="white cinematic outfit",
                lighting="Soft blue night",
            ),
        ]
    )

    content = project_to_json(
        project,
        continuity_profile=(
            make_character_lock_profile()
        ),
    )

    data = json.loads(
        content
    )

    validation = data[
        "continuity_validation"
    ]

    assert (
        validation["profile"]["name"]
        == "character-lock"
    )

    assert (
        validation["profile"][
            "required_fields"
        ]
        == [
            "wardrobe",
            "hair",
        ]
    )

    assert (
        validation["profile"][
            "warning_fields"
        ]
        == [
            "lighting",
        ]
    )

    assert (
        validation["summary"]["error_count"]
        == 1
    )

    assert (
        validation["summary"][
            "warning_count"
        ]
        == 1
    )


def test_saved_json_preserves_continuity_validation(
    tmp_path,
):
    """
    Saving and reading a project JSON file should preserve
    advanced continuity validation.
    """

    project = make_project(
        [
            make_scene(1),
            make_scene(2),
        ]
    )

    output_path = (
        tmp_path
        / "continuity"
        / "project.json"
    )

    saved_path = save_project_json(
        project,
        output_path,
        continuity_profile=(
            make_character_lock_profile()
        ),
    )

    data = json.loads(
        saved_path.read_text(
            encoding="utf-8"
        )
    )

    assert (
        "continuity_validation"
        in data
    )

    assert (
        data["continuity_validation"][
            "mode"
        ]
        == "advanced_continuity"
    )

    assert (
        data["continuity_validation"][
            "summary"
        ]["valid"]
        is True
    )


def test_duration_and_continuity_validation_can_coexist():
    """
    Optional validation layers should be able to coexist
    in the same complete project export.
    """

    from ai_cinematic_workflow import (
        DurationPolicy,
    )

    project = make_project(
        [
            make_scene(1),
            make_scene(2),
        ]
    )

    duration_policy = DurationPolicy(
        preferred_scene_duration=15,
        allowed_scene_durations=[15],
        strict=True,
    )

    continuity_profile = (
        make_character_lock_profile()
    )

    data = project_to_dict(
        project,
        duration_policy=duration_policy,
        continuity_profile=(
            continuity_profile
        ),
    )

    assert (
        "duration_validation"
        in data
    )

    assert (
        "continuity_validation"
        in data
    )

    assert (
        data["duration_validation"][
            "summary"
        ]["valid"]
        is True
    )

    assert (
        data["continuity_validation"][
            "summary"
        ]["valid"]
        is True
    )
