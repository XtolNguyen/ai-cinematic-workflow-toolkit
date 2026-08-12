import pytest

from ai_cinematic_workflow.global_constraints import (
    GlobalConstraintIssue,
    GlobalConstraintResolution,
    GlobalConstraints,
    ResolvedSceneConstraints,
    resolve_project_constraints,
    resolve_scene_constraints,
)
from ai_cinematic_workflow.scene import (
    Camera,
    Scene,
)


def make_scene(
    scene_id: int,
    *,
    negative_constraints: list[str] | None = None,
) -> Scene:
    """Create a reusable valid cinematic scene."""

    return Scene(
        scene_id=scene_id,
        duration_seconds=15,
        location="Cinematic studio",
        camera=Camera(
            shot="medium shot",
            movement="slow dolly in",
            lens="50mm",
        ),
        characters=["Lead performer"],
        performance="Natural cinematic performance",
        lighting="Warm cinematic light",
        mood="Emotional",
        continuity={
            "wardrobe": "black cinematic outfit",
            "hair": "long dark hair",
        },
        negative_constraints=list(
            negative_constraints or []
        ),
    )


def test_default_global_constraints_are_valid():
    """Default project-wide constraints should validate."""

    constraints = GlobalConstraints()

    assert constraints.is_valid()
    assert constraints.validate() == []


def test_global_constraints_require_name():
    """A global constraint profile requires a name."""

    constraints = GlobalConstraints(
        name="   ",
    )

    assert not constraints.is_valid()

    assert (
        "global constraints name cannot be empty"
        in constraints.validate()
    )


def test_duplicate_constraints_are_removed():
    """Duplicate normalized constraints should appear once."""

    constraints = GlobalConstraints(
        required_constraints=[
            "preserve performer identity",
            "preserve performer identity",
        ],
        negative_constraints=[
            "distorted face",
            "distorted face",
        ],
        prohibited_elements=[
            "duplicate limbs",
            "duplicate limbs",
        ],
    )

    assert (
        constraints.normalized_required_constraints
        == [
            "preserve performer identity",
        ]
    )

    assert (
        constraints.normalized_negative_constraints
        == [
            "distorted face",
        ]
    )

    assert (
        constraints.normalized_prohibited_elements
        == [
            "duplicate limbs",
        ]
    )


def test_required_and_advisory_conflict_is_invalid():
    """
    The same constraint cannot be both required
    and advisory.
    """

    constraints = GlobalConstraints(
        required_constraints=[
            "cinematic realism",
        ],
        advisory_constraints=[
            "cinematic realism",
        ],
    )

    assert not constraints.is_valid()

    assert (
        "constraints cannot be both required "
        "and advisory"
        in constraints.validate()
    )


def test_required_and_negative_conflict_is_invalid():
    """
    A required production rule cannot simultaneously
    be a negative constraint.
    """

    constraints = GlobalConstraints(
        required_constraints=[
            "preserve performer identity",
        ],
        negative_constraints=[
            "preserve performer identity",
        ],
    )

    assert not constraints.is_valid()

    assert (
        "required constraints cannot also be "
        "negative or prohibited constraints"
        in constraints.validate()
    )


def test_required_and_prohibited_conflict_is_invalid():
    """
    A required production rule cannot simultaneously
    be prohibited.
    """

    constraints = GlobalConstraints(
        required_constraints=[
            "cinematic realism",
        ],
        prohibited_elements=[
            "cinematic realism",
        ],
    )

    assert not constraints.is_valid()

    assert (
        "required constraints cannot also be "
        "negative or prohibited constraints"
        in constraints.validate()
    )


def test_empty_constraint_value_is_invalid():
    """Constraint groups cannot contain empty values."""

    constraints = GlobalConstraints(
        camera_constraints=[
            "avoid camera shake",
            "   ",
        ],
    )

    assert not constraints.is_valid()

    assert (
        "camera_constraints cannot contain "
        "empty constraints"
        in constraints.validate()
    )


def test_custom_constraint_category_is_normalized():
    """Custom category names should use canonical keys."""

    constraints = GlobalConstraints(
        custom_constraints={
            "Visual Effects": [
                "avoid excessive particles",
            ],
            "Production-Safety": [
                "maintain safe staging",
            ],
        },
    )

    normalized = (
        constraints.normalized_custom_constraints
    )

    assert "visual_effects" in normalized
    assert "production_safety" in normalized

    assert normalized[
        "visual_effects"
    ] == [
        "avoid excessive particles",
    ]

    assert normalized[
        "production_safety"
    ] == [
        "maintain safe staging",
    ]


def test_duplicate_normalized_custom_categories_are_invalid():
    """
    Different category spellings must not collapse
    into duplicate canonical names.
    """

    constraints = GlobalConstraints(
        custom_constraints={
            "Visual Effects": [
                "avoid sparks",
            ],
            "visual-effects": [
                "avoid smoke",
            ],
        },
    )

    assert not constraints.is_valid()

    assert (
        "custom constraint categories cannot "
        "normalize to duplicate names"
        in constraints.validate()
    )


def test_empty_custom_category_name_is_invalid():
    """Custom categories require meaningful names."""

    constraints = GlobalConstraints(
        custom_constraints={
            "   ": [
                "production rule",
            ],
        },
    )

    assert not constraints.is_valid()

    assert (
        "custom constraint category "
        "name cannot be empty"
        in constraints.validate()
    )


def test_custom_category_requires_constraints():
    """Custom categories cannot be empty."""

    constraints = GlobalConstraints(
        custom_constraints={
            "production": [],
        },
    )

    assert not constraints.is_valid()

    assert (
        "custom constraint categories "
        "must contain at least one constraint"
        in constraints.validate()
    )


def test_custom_category_rejects_empty_constraint():
    """Custom categories cannot contain blank rules."""

    constraints = GlobalConstraints(
        custom_constraints={
            "production": [
                "maintain realism",
                "   ",
            ],
        },
    )

    assert not constraints.is_valid()

    assert (
        "custom constraint category "
        "'production' cannot contain "
        "empty constraints"
        in constraints.validate()
    )


def test_prohibited_elements_join_global_negative_constraints():
    """
    Prohibited elements should participate in
    global negative-prompt resolution.
    """

    constraints = GlobalConstraints(
        negative_constraints=[
            "distorted face",
            "extra fingers",
        ],
        prohibited_elements=[
            "duplicate limbs",
        ],
    )

    assert (
        constraints.resolved_global_negative_constraints
        == [
            "distorted face",
            "extra fingers",
            "duplicate limbs",
        ]
    )


def test_duplicate_between_negative_and_prohibited_is_removed():
    """
    A rule appearing in negative and prohibited groups
    should appear once in resolved negatives.
    """

    constraints = GlobalConstraints(
        negative_constraints=[
            "distorted face",
        ],
        prohibited_elements=[
            "distorted face",
            "duplicate limbs",
        ],
    )

    assert (
        constraints.resolved_global_negative_constraints
        == [
            "distorted face",
            "duplicate limbs",
        ]
    )


def test_scene_constraints_merge_global_and_scene_negatives():
    """
    Scene resolution should merge project-wide and
    scene-specific negative constraints.
    """

    scene = make_scene(
        1,
        negative_constraints=[
            "distorted face",
            "text artifacts",
        ],
    )

    constraints = GlobalConstraints(
        negative_constraints=[
            "distorted face",
            "extra fingers",
        ],
        prohibited_elements=[
            "duplicate limbs",
        ],
    )

    result = resolve_scene_constraints(
        scene,
        constraints,
    )

    assert result.scene_id == 1

    assert (
        result.global_negative_constraints
        == [
            "distorted face",
            "extra fingers",
            "duplicate limbs",
        ]
    )

    assert (
        result.scene_negative_constraints
        == [
            "distorted face",
            "text artifacts",
        ]
    )

    assert (
        result.resolved_negative_constraints
        == [
            "distorted face",
            "extra fingers",
            "duplicate limbs",
            "text artifacts",
        ]
    )


def test_scene_resolution_does_not_mutate_scene():
    """
    Resolving global constraints must not modify
    the original Scene object.
    """

    scene = make_scene(
        1,
        negative_constraints=[
            "text artifacts",
        ],
    )

    original_constraints = list(
        scene.negative_constraints
    )

    constraints = GlobalConstraints(
        negative_constraints=[
            "distorted face",
        ],
    )

    result = resolve_scene_constraints(
        scene,
        constraints,
    )

    assert (
        scene.negative_constraints
        == original_constraints
    )

    assert (
        result.resolved_negative_constraints
        == [
            "distorted face",
            "text artifacts",
        ]
    )


def test_non_negative_global_rules_remain_structured():
    """
    Identity, style, camera, and environment rules
    should not automatically become negative prompts.
    """

    constraints = GlobalConstraints(
        required_constraints=[
            "maintain cinematic realism",
        ],
        character_identity_constraints=[
            "preserve lead performer identity",
        ],
        visual_style_constraints=[
            "cinematic photorealism",
        ],
        camera_constraints=[
            "controlled camera movement",
        ],
        environment_constraints=[
            "preserve environment geometry",
        ],
        negative_constraints=[
            "distorted face",
        ],
    )

    scene = make_scene(1)

    result = resolve_scene_constraints(
        scene,
        constraints,
    )

    assert (
        result.resolved_negative_constraints
        == [
            "distorted face",
        ]
    )

    data = constraints.to_dict()

    assert data[
        "required_constraints"
    ] == [
        "maintain cinematic realism",
    ]

    assert data[
        "character_identity_constraints"
    ] == [
        "preserve lead performer identity",
    ]

    assert data[
        "visual_style_constraints"
    ] == [
        "cinematic photorealism",
    ]

    assert data[
        "camera_constraints"
    ] == [
        "controlled camera movement",
    ]

    assert data[
        "environment_constraints"
    ] == [
        "preserve environment geometry",
    ]


def test_strict_mode_is_serialized():
    """Global strict mode should remain portable."""

    constraints = GlobalConstraints(
        name="advisory-production",
        strict=False,
    )

    data = constraints.to_dict()

    assert data["name"] == "advisory-production"
    assert data["strict"] is False


def test_global_constraints_serialization():
    """
    Complete GlobalConstraints configuration
    should serialize into structured data.
    """

    constraints = GlobalConstraints(
        name="cinematic-production",
        required_constraints=[
            "maintain cinematic realism",
        ],
        advisory_constraints=[
            "prefer natural movement",
        ],
        negative_constraints=[
            "distorted face",
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
            "preserve set geometry",
        ],
        custom_constraints={
            "Production Rules": [
                "maintain temporal coherence",
            ],
        },
        strict=True,
    )

    data = constraints.to_dict()

    assert (
        data["name"]
        == "cinematic-production"
    )

    assert data["strict"] is True

    assert (
        data["negative_constraints"]
        == [
            "distorted face",
        ]
    )

    assert (
        data["prohibited_elements"]
        == [
            "duplicate limbs",
        ]
    )

    assert (
        data["custom_constraints"][
            "production_rules"
        ]
        == [
            "maintain temporal coherence",
        ]
    )


def test_structured_global_constraint_issue_serialization():
    """Constraint issues should serialize consistently."""

    issue = GlobalConstraintIssue(
        issue_type="constraint_warning",
        severity="warning",
        message="Example production warning",
        category="camera",
        scene_id=2,
        value="unstable camera",
    )

    data = issue.to_dict()

    assert (
        data["issue_type"]
        == "constraint_warning"
    )

    assert data["severity"] == "warning"

    assert (
        data["message"]
        == "Example production warning"
    )

    assert data["category"] == "camera"
    assert data["scene_id"] == 2

    assert (
        data["value"]
        == "unstable camera"
    )


def test_resolved_scene_constraint_summary():
    """Per-scene resolution should expose useful counts."""

    issue = GlobalConstraintIssue(
        issue_type="example_warning",
        severity="warning",
        message="Example warning",
        scene_id=1,
    )

    result = ResolvedSceneConstraints(
        scene_id=1,
        global_negative_constraints=[
            "distorted face",
            "extra fingers",
        ],
        scene_negative_constraints=[
            "text artifacts",
        ],
        resolved_negative_constraints=[
            "distorted face",
            "extra fingers",
            "text artifacts",
        ],
        issues=[
            issue,
        ],
    )

    data = result.to_dict()

    assert data["scene_id"] == 1

    assert (
        data["summary"][
            "global_negative_count"
        ]
        == 2
    )

    assert (
        data["summary"][
            "scene_negative_count"
        ]
        == 1
    )

    assert (
        data["summary"][
            "resolved_negative_count"
        ]
        == 3
    )

    assert (
        data["summary"]["warning_count"]
        == 1
    )


def test_project_constraints_resolve_multiple_scenes():
    """
    Project resolution should process every scene
    independently.
    """

    scenes = [
        make_scene(
            1,
            negative_constraints=[
                "text artifacts",
            ],
        ),
        make_scene(
            2,
            negative_constraints=[
                "camera jitter",
            ],
        ),
        make_scene(
            3,
        ),
    ]

    constraints = GlobalConstraints(
        negative_constraints=[
            "distorted face",
        ],
        prohibited_elements=[
            "duplicate limbs",
        ],
    )

    result = resolve_project_constraints(
        scenes,
        constraints,
    )

    assert isinstance(
        result,
        GlobalConstraintResolution,
    )

    assert result.scene_count == 3

    assert [
        item.scene_id
        for item in result.scene_results
    ] == [
        1,
        2,
        3,
    ]

    assert (
        "text artifacts"
        in result.scene_results[
            0
        ].resolved_negative_constraints
    )

    assert (
        "camera jitter"
        in result.scene_results[
            1
        ].resolved_negative_constraints
    )

    for scene_result in (
        result.scene_results
    ):
        assert (
            "distorted face"
            in scene_result.resolved_negative_constraints
        )

        assert (
            "duplicate limbs"
            in scene_result.resolved_negative_constraints
        )


def test_project_resolution_serialization():
    """Project-level resolution should serialize cleanly."""

    scenes = [
        make_scene(1),
        make_scene(2),
    ]

    constraints = GlobalConstraints(
        name="production-lock",
        negative_constraints=[
            "distorted face",
        ],
    )

    result = resolve_project_constraints(
        scenes,
        constraints,
    )

    data = result.to_dict()

    assert (
        data["summary"]["scene_count"]
        == 2
    )

    assert (
        data["summary"]["issue_count"]
        == result.issue_count
    )

    assert (
        data["summary"]["warning_count"]
        == result.warning_count
    )

    assert (
        data["constraints"]["name"]
        == "production-lock"
    )

    assert (
        len(data["scene_results"])
        == 2
    )

    assert (
        data["scene_results"][0][
            "scene_id"
        ]
        == 1
    )

    assert (
        data["scene_results"][1][
            "scene_id"
        ]
        == 2
    )


def test_duplicate_scene_ids_are_rejected():
    """
    Project constraint resolution requires
    unique scene IDs.
    """

    scenes = [
        make_scene(1),
        make_scene(1),
    ]

    with pytest.raises(
        ValueError,
        match=(
            "global constraint resolution "
            "requires unique scene IDs"
        ),
    ):
        resolve_project_constraints(
            scenes,
            GlobalConstraints(),
        )


def test_invalid_global_constraints_are_rejected():
    """Scene resolution should reject invalid configuration."""

    scene = make_scene(1)

    constraints = GlobalConstraints(
        name="   ",
    )

    with pytest.raises(
        ValueError,
        match="Invalid global constraints",
    ):
        resolve_scene_constraints(
            scene,
            constraints,
        )


def test_invalid_scene_is_rejected():
    """Constraint resolution should reject invalid scenes."""

    scene = make_scene(1)

    scene.duration_seconds = 0

    constraints = GlobalConstraints()

    with pytest.raises(
        ValueError,
        match="Invalid scene 1",
    ):
        resolve_scene_constraints(
            scene,
            constraints,
        )
