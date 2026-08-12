import pytest

from ai_cinematic_workflow.continuity_profiles import (
    ContinuityProfile,
    normalize_continuity_field,
    validate_continuity_pair,
    validate_project_continuity,
)
from ai_cinematic_workflow.scene import (
    Camera,
    Scene,
)


def make_scene(
    scene_id: int,
    *,
    characters: list[str] | None = None,
    location: str = "Cinematic studio",
    lighting: str = "Warm cinematic light",
    mood: str = "Emotional",
    continuity: dict | None = None,
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
        characters=(
            characters
            if characters is not None
            else ["Lead performer"]
        ),
        performance="Natural cinematic performance",
        lighting=lighting,
        mood=mood,
        continuity=continuity or {},
    )


def test_normalize_continuity_field():
    """Continuity field names should normalize consistently."""

    assert (
        normalize_continuity_field(
            "Time Of Day"
        )
        == "time_of_day"
    )

    assert (
        normalize_continuity_field(
            "camera-shot"
        )
        == "camera_shot"
    )

    assert (
        normalize_continuity_field(
            "  Hair Style  "
        )
        == "hair_style"
    )


def test_valid_continuity_profile():
    """A correctly configured profile should validate."""

    profile = ContinuityProfile(
        name="character-lock",
        required_fields=[
            "wardrobe",
            "hair",
        ],
        optional_fields=[
            "location",
        ],
        warning_fields=[
            "lighting",
        ],
        strict=True,
    )

    assert profile.is_valid()
    assert profile.validate() == []


def test_profile_serialization_uses_normalized_fields():
    """Serialized profiles should contain canonical field names."""

    profile = ContinuityProfile(
        name="normalized-profile",
        required_fields=[
            "Time Of Day",
            "Hair Style",
        ],
        warning_fields=[
            "camera-shot",
        ],
    )

    data = profile.to_dict()

    assert data["name"] == "normalized-profile"

    assert data["required_fields"] == [
        "time_of_day",
        "hair_style",
    ]

    assert data["warning_fields"] == [
        "camera_shot",
    ]


def test_empty_profile_name_is_invalid():
    """Continuity profiles require a name."""

    profile = ContinuityProfile(
        name="   ",
    )

    assert not profile.is_valid()

    assert (
        "continuity profile name cannot be empty"
        in profile.validate()
    )


def test_duplicate_profile_fields_are_invalid():
    """Duplicate field names inside one category should fail."""

    profile = ContinuityProfile(
        required_fields=[
            "wardrobe",
            "Wardrobe",
        ]
    )

    assert not profile.is_valid()

    assert (
        "required_fields cannot contain "
        "duplicate field names"
        in profile.validate()
    )


def test_required_and_optional_field_conflict():
    """A field cannot be both required and optional."""

    profile = ContinuityProfile(
        required_fields=[
            "wardrobe",
        ],
        optional_fields=[
            "wardrobe",
        ],
    )

    assert not profile.is_valid()

    assert (
        "continuity fields cannot be both "
        "required and optional"
        in profile.validate()
    )


def test_ignored_and_active_field_conflict():
    """Ignored fields cannot also participate in validation."""

    profile = ContinuityProfile(
        required_fields=[
            "wardrobe",
        ],
        ignored_fields=[
            "wardrobe",
        ],
    )

    assert not profile.is_valid()

    assert (
        "ignored continuity fields cannot also "
        "be active continuity fields"
        in profile.validate()
    )


def test_strict_and_warning_field_conflict():
    """A field cannot be both strict and warning-only."""

    profile = ContinuityProfile(
        strict_fields=[
            "wardrobe",
        ],
        warning_fields=[
            "wardrobe",
        ],
    )

    assert not profile.is_valid()

    assert (
        "continuity fields cannot be both "
        "strict and warning-only"
        in profile.validate()
    )


def test_allowed_change_must_reference_active_field():
    """Allowed-change rules must reference active continuity fields."""

    profile = ContinuityProfile(
        allowed_change_fields=[
            "location",
        ],
    )

    assert not profile.is_valid()

    assert (
        "allowed_change_fields must reference "
        "active continuity fields"
        in profile.validate()
    )


def test_required_wardrobe_change_is_error_in_strict_profile():
    """Required continuity changes should fail in strict mode."""

    previous = make_scene(
        1,
        continuity={
            "wardrobe": "black outfit",
        },
    )

    current = make_scene(
        2,
        continuity={
            "wardrobe": "white outfit",
        },
    )

    profile = ContinuityProfile(
        required_fields=[
            "wardrobe",
        ],
        strict=True,
    )

    result = validate_continuity_pair(
        previous,
        current,
        profile,
    )

    assert result.is_valid is False
    assert result.error_count == 1
    assert result.warning_count == 0

    issue = result.issues[0]

    assert (
        issue.issue_type
        == "continuity_change"
    )

    assert issue.field_name == "wardrobe"
    assert issue.severity == "error"

    assert issue.previous_scene_id == 1
    assert issue.current_scene_id == 2

    assert (
        issue.previous_value
        == "black outfit"
    )

    assert (
        issue.current_value
        == "white outfit"
    )


def test_unchanged_hair_passes():
    """Unchanged continuity metadata should not produce issues."""

    previous = make_scene(
        1,
        continuity={
            "hair": "long dark hair",
        },
    )

    current = make_scene(
        2,
        continuity={
            "hair": "long dark hair",
        },
    )

    profile = ContinuityProfile(
        required_fields=[
            "hair",
        ],
    )

    result = validate_continuity_pair(
        previous,
        current,
        profile,
    )

    assert result.is_valid
    assert result.issue_count == 0
    assert result.issues == []


def test_warning_field_change_does_not_invalidate_pair():
    """Warning-only changes should be reported without failing."""

    previous = make_scene(
        1,
        lighting="Warm sunset",
    )

    current = make_scene(
        2,
        lighting="Soft blue night",
    )

    profile = ContinuityProfile(
        warning_fields=[
            "lighting",
        ],
        strict=True,
    )

    result = validate_continuity_pair(
        previous,
        current,
        profile,
    )

    assert result.is_valid
    assert result.error_count == 0
    assert result.warning_count == 1

    issue = result.issues[0]

    assert issue.field_name == "lighting"
    assert issue.severity == "warning"


def test_non_strict_profile_turns_change_into_warning():
    """
    Changes to ordinary active fields should become warnings
    when global strict mode is disabled.
    """

    previous = make_scene(
        1,
        continuity={
            "environment": "forest",
        },
    )

    current = make_scene(
        2,
        continuity={
            "environment": "city",
        },
    )

    profile = ContinuityProfile(
        optional_fields=[
            "environment",
        ],
        strict=False,
    )

    result = validate_continuity_pair(
        previous,
        current,
        profile,
    )

    assert result.is_valid
    assert result.warning_count == 1
    assert result.error_count == 0


def test_strict_field_change_is_always_error():
    """Explicit strict fields should fail even in non-strict profiles."""

    previous = make_scene(
        1,
        continuity={
            "hair": "long dark hair",
        },
    )

    current = make_scene(
        2,
        continuity={
            "hair": "short blonde hair",
        },
    )

    profile = ContinuityProfile(
        strict_fields=[
            "hair",
        ],
        strict=False,
    )

    result = validate_continuity_pair(
        previous,
        current,
        profile,
    )

    assert result.is_valid is False
    assert result.error_count == 1

    assert (
        result.issues[0].severity
        == "error"
    )


def test_allowed_location_change_produces_no_issue():
    """Explicitly allowed scene changes should pass."""

    previous = make_scene(
        1,
        location="Beach",
    )

    current = make_scene(
        2,
        location="City",
    )

    profile = ContinuityProfile(
        optional_fields=[
            "location",
        ],
        allowed_change_fields=[
            "location",
        ],
        strict=True,
    )

    result = validate_continuity_pair(
        previous,
        current,
        profile,
    )

    assert result.is_valid
    assert result.issue_count == 0


def test_ignored_field_does_not_participate_in_validation():
    """Ignored fields should not generate continuity issues."""

    previous = make_scene(
        1,
        mood="Calm",
    )

    current = make_scene(
        2,
        mood="Intense",
    )

    profile = ContinuityProfile(
        ignored_fields=[
            "mood",
        ],
        strict=True,
    )

    result = validate_continuity_pair(
        previous,
        current,
        profile,
    )

    assert result.is_valid
    assert result.issue_count == 0


def test_missing_required_field_is_detected():
    """Missing required metadata should create an error."""

    previous = make_scene(
        1,
        continuity={
            "wardrobe": "black outfit",
        },
    )

    current = make_scene(
        2,
        continuity={},
    )

    profile = ContinuityProfile(
        required_fields=[
            "wardrobe",
        ],
        missing_required_severity="error",
    )

    result = validate_continuity_pair(
        previous,
        current,
        profile,
    )

    assert result.is_valid is False
    assert result.error_count == 1

    issue = result.issues[0]

    assert (
        issue.issue_type
        == "missing_required_field"
    )

    assert issue.field_name == "wardrobe"
    assert issue.severity == "error"

    assert (
        issue.previous_value
        == "black outfit"
    )

    assert issue.current_value is None


def test_missing_required_field_can_be_warning():
    """Missing required fields may be configured as warnings."""

    previous = make_scene(
        1,
        continuity={
            "hair": "long dark hair",
        },
    )

    current = make_scene(
        2,
        continuity={},
    )

    profile = ContinuityProfile(
        required_fields=[
            "hair",
        ],
        missing_required_severity="warning",
    )

    result = validate_continuity_pair(
        previous,
        current,
        profile,
    )

    assert result.is_valid
    assert result.warning_count == 1
    assert result.error_count == 0


def test_missing_required_field_can_be_ignored():
    """Profiles may explicitly ignore missing required metadata."""

    previous = make_scene(
        1,
        continuity={
            "hair": "long dark hair",
        },
    )

    current = make_scene(
        2,
        continuity={},
    )

    profile = ContinuityProfile(
        required_fields=[
            "hair",
        ],
        missing_required_severity="ignore",
    )

    result = validate_continuity_pair(
        previous,
        current,
        profile,
    )

    assert result.is_valid
    assert result.issue_count == 0


def test_missing_strict_field_is_error():
    """A strict continuity field must be present in both scenes."""

    previous = make_scene(
        1,
        continuity={
            "makeup": "natural",
        },
    )

    current = make_scene(
        2,
        continuity={},
    )

    profile = ContinuityProfile(
        strict_fields=[
            "makeup",
        ],
        strict=False,
    )

    result = validate_continuity_pair(
        previous,
        current,
        profile,
    )

    assert result.is_valid is False
    assert result.error_count == 1

    assert (
        result.issues[0].issue_type
        == "missing_strict_field"
    )


def test_custom_continuity_key_is_supported():
    """Arbitrary continuity metadata should be supported."""

    previous = make_scene(
        1,
        continuity={
            "magic_energy_state": "low",
        },
    )

    current = make_scene(
        2,
        continuity={
            "magic_energy_state": "high",
        },
    )

    profile = ContinuityProfile(
        warning_fields=[
            "magic_energy_state",
        ],
    )

    result = validate_continuity_pair(
        previous,
        current,
        profile,
    )

    assert result.is_valid
    assert result.warning_count == 1

    assert (
        result.issues[0].field_name
        == "magic_energy_state"
    )


def test_native_camera_field_is_supported():
    """Native camera metadata should participate in continuity rules."""

    previous = make_scene(1)
    current = make_scene(2)

    current.camera.shot = "close-up"

    profile = ContinuityProfile(
        warning_fields=[
            "camera_shot",
        ],
    )

    result = validate_continuity_pair(
        previous,
        current,
        profile,
    )

    assert result.is_valid
    assert result.warning_count == 1

    assert (
        result.issues[0].field_name
        == "camera_shot"
    )


def test_character_order_does_not_create_false_issue():
    """Character continuity should ignore list ordering."""

    previous = make_scene(
        1,
        characters=[
            "Lead performer",
            "Guitarist",
        ],
    )

    current = make_scene(
        2,
        characters=[
            "Guitarist",
            "Lead performer",
        ],
    )

    profile = ContinuityProfile(
        required_fields=[
            "characters",
        ],
    )

    result = validate_continuity_pair(
        previous,
        current,
        profile,
    )

    assert result.is_valid
    assert result.issue_count == 0


def test_character_identity_change_is_detected():
    """Actual character changes should create continuity issues."""

    previous = make_scene(
        1,
        characters=[
            "Lead performer",
        ],
    )

    current = make_scene(
        2,
        characters=[
            "Different performer",
        ],
    )

    profile = ContinuityProfile(
        required_fields=[
            "characters",
        ],
        strict=True,
    )

    result = validate_continuity_pair(
        previous,
        current,
        profile,
    )

    assert result.is_valid is False
    assert result.error_count == 1

    assert (
        result.issues[0].field_name
        == "characters"
    )


def test_project_level_continuity_validation():
    """Project validation should compare every adjacent scene pair."""

    scenes = [
        make_scene(
            1,
            continuity={
                "wardrobe": "black outfit",
                "hair": "long dark hair",
            },
        ),
        make_scene(
            2,
            continuity={
                "wardrobe": "black outfit",
                "hair": "long dark hair",
            },
        ),
        make_scene(
            3,
            continuity={
                "wardrobe": "white outfit",
                "hair": "long dark hair",
            },
        ),
    ]

    profile = ContinuityProfile(
        required_fields=[
            "wardrobe",
            "hair",
        ],
        strict=True,
    )

    result = validate_project_continuity(
        scenes,
        profile,
    )

    assert result.scene_count == 3
    assert result.checked_pairs == 2

    assert result.is_valid is False
    assert result.issue_count == 1
    assert result.error_count == 1
    assert result.warning_count == 0

    issue = result.issues[0]

    assert issue.previous_scene_id == 2
    assert issue.current_scene_id == 3
    assert issue.field_name == "wardrobe"


def test_project_warning_does_not_invalidate_project():
    """Warning-only project issues should preserve valid status."""

    scenes = [
        make_scene(
            1,
            lighting="Warm sunset",
        ),
        make_scene(
            2,
            lighting="Soft blue night",
        ),
    ]

    profile = ContinuityProfile(
        warning_fields=[
            "lighting",
        ],
    )

    result = validate_project_continuity(
        scenes,
        profile,
    )

    assert result.is_valid
    assert result.error_count == 0
    assert result.warning_count == 1


def test_project_result_serialization():
    """Advanced project continuity results should serialize cleanly."""

    scenes = [
        make_scene(
            1,
            continuity={
                "wardrobe": "black outfit",
            },
        ),
        make_scene(
            2,
            continuity={
                "wardrobe": "white outfit",
            },
        ),
    ]

    profile = ContinuityProfile(
        name="wardrobe-lock",
        required_fields=[
            "wardrobe",
        ],
        strict=True,
    )

    result = validate_project_continuity(
        scenes,
        profile,
    )

    data = result.to_dict()

    assert data["summary"]["valid"] is False
    assert data["summary"]["scene_count"] == 2
    assert data["summary"]["checked_pairs"] == 1
    assert data["summary"]["issue_count"] == 1
    assert data["summary"]["error_count"] == 1

    assert (
        data["profile"]["name"]
        == "wardrobe-lock"
    )

    assert (
        data["issues"][0]["field_name"]
        == "wardrobe"
    )

    assert (
        data["issues"][0][
            "previous_scene_id"
        ]
        == 1
    )

    assert (
        data["issues"][0][
            "current_scene_id"
        ]
        == 2
    )


def test_duplicate_scene_ids_are_rejected():
    """Project continuity requires unique scene IDs."""

    scenes = [
        make_scene(1),
        make_scene(1),
    ]

    with pytest.raises(
        ValueError,
        match=(
            "advanced continuity validation "
            "requires unique scene IDs"
        ),
    ):
        validate_project_continuity(
            scenes,
            ContinuityProfile(),
        )


def test_invalid_profile_is_rejected_before_validation():
    """Continuity validation should reject invalid profiles."""

    previous = make_scene(1)
    current = make_scene(2)

    profile = ContinuityProfile(
        required_fields=[
            "wardrobe",
        ],
        ignored_fields=[
            "wardrobe",
        ],
    )

    with pytest.raises(
        ValueError,
        match="Invalid continuity profile",
    ):
        validate_continuity_pair(
            previous,
            current,
            profile,
        )
