import json

import pytest

from ai_cinematic_workflow import (
    Camera,
    CinematicProject,
    ContinuityProfile,
    DurationPolicy,
    GlobalConstraints,
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
    location: str = "Cinematic studio",
    wardrobe: str = "black cinematic outfit",
    hair: str = "long dark hair",
    lighting: str = "Warm cinematic light",
    negative_constraints: list[str] | None = None,
) -> Scene:
    """Create a reusable valid cinematic scene."""

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
        negative_constraints=list(
            negative_constraints or []
        ),
    )


def make_project(
    scenes: list[Scene],
) -> CinematicProject:
    """Create a reusable cinematic project."""

    return CinematicProject(
        metadata=ProjectMetadata(
            title="Global Constraints Integration Test",
            project_type="cinematic",
        ),
        scenes=scenes,
    )


def make_global_constraints() -> GlobalConstraints:
    """Create reusable project-wide production constraints."""

    return GlobalConstraints(
        name="cinematic-production",
        required_constraints=[
            "maintain cinematic realism",
        ],
        negative_constraints=[
            "distorted face",
            "extra fingers",
        ],
        prohibited_elements=[
            "duplicate limbs",
        ],
        character_identity_constraints=[
            "preserve lead performer identity",
        ],
        visual_style_constraints=[
            "cinematic photorealism",
        ],
        camera_constraints=[
            "avoid unstable camera shake",
        ],
        environment_constraints=[
            "preserve environment geometry",
        ],
        custom_constraints={
            "Production Rules": [
                "maintain temporal coherence",
            ],
        },
        strict=True,
    )


def test_global_constraints_are_exported():
    """
    Supplying GlobalConstraints should add structured
    project-wide constraint data to the export.
    """

    project = make_project(
        [
            make_scene(1),
            make_scene(2),
        ]
    )

    data = project_to_dict(
        project,
        global_constraints=(
            make_global_constraints()
        ),
    )

    assert "global_constraints" in data

    result = data[
        "global_constraints"
    ]

    assert (
        result["mode"]
        == "project_global_constraints"
    )

    assert (
        result["constraints"]["name"]
        == "cinematic-production"
    )

    assert (
        result["summary"]["scene_count"]
        == 2
    )

    assert (
        len(result["scene_results"])
        == 2
    )


def test_global_and_scene_negative_constraints_are_merged():
    """
    Global negative rules and scene-specific rules
    should resolve into one deduplicated list.
    """

    project = make_project(
        [
            make_scene(
                1,
                negative_constraints=[
                    "distorted face",
                    "text artifacts",
                ],
            ),
        ]
    )

    data = project_to_dict(
        project,
        global_constraints=(
            make_global_constraints()
        ),
    )

    scene_result = data[
        "global_constraints"
    ][
        "scene_results"
    ][0]

    assert (
        scene_result[
            "global_negative_constraints"
        ]
        == [
            "distorted face",
            "extra fingers",
            "duplicate limbs",
        ]
    )

    assert (
        scene_result[
            "scene_negative_constraints"
        ]
        == [
            "distorted face",
            "text artifacts",
        ]
    )

    assert (
        scene_result[
            "resolved_negative_constraints"
        ]
        == [
            "distorted face",
            "extra fingers",
            "duplicate limbs",
            "text artifacts",
        ]
    )


def test_global_constraint_resolution_does_not_mutate_scene():
    """
    Project export must not alter the original
    Scene negative constraints.
    """

    scene = make_scene(
        1,
        negative_constraints=[
            "text artifacts",
        ],
    )

    project = make_project(
        [scene]
    )

    original_negative_constraints = list(
        scene.negative_constraints
    )

    data = project_to_dict(
        project,
        global_constraints=(
            make_global_constraints()
        ),
    )

    assert (
        scene.negative_constraints
        == original_negative_constraints
    )

    assert (
        data["global_constraints"][
            "scene_results"
        ][0][
            "resolved_negative_constraints"
        ]
        == [
            "distorted face",
            "extra fingers",
            "duplicate limbs",
            "text artifacts",
        ]
    )


def test_structured_non_negative_constraints_are_preserved():
    """
    Identity, style, camera, environment, and custom
    constraints should remain structured in project JSON.
    """

    project = make_project(
        [
            make_scene(1),
        ]
    )

    data = project_to_dict(
        project,
        global_constraints=(
            make_global_constraints()
        ),
    )

    constraints = data[
        "global_constraints"
    ][
        "constraints"
    ]

    assert (
        constraints[
            "required_constraints"
        ]
        == [
            "maintain cinematic realism",
        ]
    )

    assert (
        constraints[
            "character_identity_constraints"
        ]
        == [
            "preserve lead performer identity",
        ]
    )

    assert (
        constraints[
            "visual_style_constraints"
        ]
        == [
            "cinematic photorealism",
        ]
    )

    assert (
        constraints[
            "camera_constraints"
        ]
        == [
            "avoid unstable camera shake",
        ]
    )

    assert (
        constraints[
            "environment_constraints"
        ]
        == [
            "preserve environment geometry",
        ]
    )

    assert (
        constraints[
            "custom_constraints"
        ][
            "production_rules"
        ]
        == [
            "maintain temporal coherence",
        ]
    )


def test_export_without_global_constraints_is_backward_compatible():
    """
    Existing project exports should not gain a
    global_constraints section unless explicitly requested.
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
        "global_constraints"
        not in data
    )

    assert "project" in data
    assert "timeline" in data
    assert "workflow" in data


def test_project_to_json_preserves_global_constraints():
    """
    JSON serialization should preserve the complete
    GlobalConstraints resolution.
    """

    project = make_project(
        [
            make_scene(
                1,
                negative_constraints=[
                    "text artifacts",
                ],
            ),
        ]
    )

    content = project_to_json(
        project,
        global_constraints=(
            make_global_constraints()
        ),
    )

    data = json.loads(
        content
    )

    result = data[
        "global_constraints"
    ]

    assert (
        result["mode"]
        == "project_global_constraints"
    )

    assert (
        result["constraints"]["strict"]
        is True
    )

    assert (
        result["scene_results"][0][
            "resolved_negative_constraints"
        ]
        == [
            "distorted face",
            "extra fingers",
            "duplicate limbs",
            "text artifacts",
        ]
    )


def test_save_project_json_preserves_global_constraints(
    tmp_path,
):
    """
    Saving and loading the complete project JSON should
    preserve global constraint data.
    """

    project = make_project(
        [
            make_scene(1),
            make_scene(2),
        ]
    )

    output_path = (
        tmp_path
        / "global_constraints"
        / "project.json"
    )

    saved_path = save_project_json(
        project,
        output_path,
        global_constraints=(
            make_global_constraints()
        ),
    )

    data = json.loads(
        saved_path.read_text(
            encoding="utf-8"
        )
    )

    assert (
        "global_constraints"
        in data
    )

    assert (
        data["global_constraints"][
            "summary"
        ]["scene_count"]
        == 2
    )

    assert (
        data["global_constraints"][
            "constraints"
        ]["name"]
        == "cinematic-production"
    )


def test_duration_continuity_and_global_constraints_can_coexist():
    """
    DurationPolicy, ContinuityProfile, and GlobalConstraints
    should work simultaneously in one complete project export.
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

    duration_policy = DurationPolicy(
        preferred_scene_duration=15,
        allowed_scene_durations=[
            15,
        ],
        strict=True,
    )

    continuity_profile = ContinuityProfile(
        name="production-continuity",
        required_fields=[
            "wardrobe",
            "hair",
        ],
        optional_fields=[
            "location",
        ],
        allowed_change_fields=[
            "location",
        ],
        warning_fields=[
            "lighting",
        ],
        strict=True,
    )

    global_constraints = (
        make_global_constraints()
    )

    data = project_to_dict(
        project,
        duration_policy=duration_policy,
        continuity_profile=(
            continuity_profile
        ),
        global_constraints=(
            global_constraints
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
        "global_constraints"
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

    assert (
        data["global_constraints"][
            "summary"
        ]["scene_count"]
        == 2
    )


def test_global_constraints_preserve_existing_workflow_output():
    """
    Opt-in global constraints should not remove or replace
    existing workflow processing data.
    """

    project = make_project(
        [
            make_scene(1),
            make_scene(2),
        ]
    )

    data = project_to_dict(
        project,
        global_constraints=(
            make_global_constraints()
        ),
    )

    assert "workflow" in data

    assert (
        data["workflow"]["summary"][
            "processed_scenes"
        ]
        == 2
    )

    assert (
        len(
            data["workflow"][
                "scene_results"
            ]
        )
        == 2
    )


def test_invalid_global_constraints_are_rejected_by_exporter():
    """
    Complete project export should reject invalid
    GlobalConstraints before producing output.
    """

    project = make_project(
        [
            make_scene(1),
        ]
    )

    constraints = GlobalConstraints(
        name="   ",
    )

    with pytest.raises(
        ValueError,
        match="Invalid global constraints",
    ):
        project_to_dict(
            project,
            global_constraints=constraints,
        )
