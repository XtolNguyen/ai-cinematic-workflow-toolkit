import pytest

from ai_cinematic_workflow.duration import (
    DurationPolicy,
    validate_scene_duration,
)
from ai_cinematic_workflow.scene import (
    Camera,
    Scene,
)


def make_scene(
    duration_seconds: float,
    scene_id: int = 1,
) -> Scene:
    """Create a reusable cinematic scene for duration tests."""

    return Scene(
        scene_id=scene_id,
        duration_seconds=duration_seconds,
        location="Cinematic test location",
        camera=Camera(
            shot="medium shot",
        ),
        characters=["Lead performer"],
    )


def make_strict_policy() -> DurationPolicy:
    """Create a reusable strict duration policy."""

    return DurationPolicy(
        preferred_scene_duration=15,
        minimum_scene_duration=5,
        maximum_scene_duration=30,
        allowed_scene_durations=[
            5,
            10,
            15,
            30,
        ],
        tolerance_seconds=0.25,
        strict=True,
    )


def test_valid_duration_policy():
    """A correctly configured policy should validate."""

    policy = make_strict_policy()

    assert policy.is_valid()
    assert policy.validate() == []


def test_exact_preferred_duration_is_valid():
    """A 15-second scene should satisfy the strict policy."""

    scene = make_scene(15)
    policy = make_strict_policy()

    result = validate_scene_duration(
        scene,
        policy,
    )

    assert result.is_valid
    assert result.issue_count == 0
    assert result.issues == []


def test_disallowed_duration_is_detected():
    """
    A 12-second scene should violate allowed durations
    and strict preferred duration.
    """

    scene = make_scene(12)
    policy = make_strict_policy()

    result = validate_scene_duration(
        scene,
        policy,
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


def test_below_minimum_duration_is_detected():
    """Durations below the configured minimum should fail."""

    scene = make_scene(4)

    policy = DurationPolicy(
        minimum_scene_duration=5,
    )

    result = validate_scene_duration(
        scene,
        policy,
    )

    assert result.is_valid is False
    assert result.issue_count == 1

    issue = result.issues[0]

    assert (
        issue.issue_type
        == "below_minimum_duration"
    )

    assert issue.expected_duration == 5
    assert issue.actual_duration == 4
    assert issue.difference_seconds == -1


def test_above_maximum_duration_is_detected():
    """Durations above the configured maximum should fail."""

    scene = make_scene(31)

    policy = DurationPolicy(
        maximum_scene_duration=30,
    )

    result = validate_scene_duration(
        scene,
        policy,
    )

    assert result.is_valid is False
    assert result.issue_count == 1

    issue = result.issues[0]

    assert (
        issue.issue_type
        == "above_maximum_duration"
    )

    assert issue.expected_duration == 30
    assert issue.actual_duration == 31
    assert issue.difference_seconds == 1


def test_allowed_duration_is_accepted():
    """A duration listed in allowed_scene_durations should pass."""

    scene = make_scene(10)

    policy = DurationPolicy(
        allowed_scene_durations=[
            5,
            10,
            15,
            30,
        ]
    )

    result = validate_scene_duration(
        scene,
        policy,
    )

    assert result.is_valid


def test_tolerance_accepts_duration_below_preferred():
    """A duration within negative tolerance should pass."""

    scene = make_scene(14.8)

    policy = DurationPolicy(
        preferred_scene_duration=15,
        tolerance_seconds=0.25,
        strict=True,
    )

    result = validate_scene_duration(
        scene,
        policy,
    )

    assert result.is_valid


def test_tolerance_accepts_duration_above_preferred():
    """A duration within positive tolerance should pass."""

    scene = make_scene(15.2)

    policy = DurationPolicy(
        preferred_scene_duration=15,
        tolerance_seconds=0.25,
        strict=True,
    )

    result = validate_scene_duration(
        scene,
        policy,
    )

    assert result.is_valid


def test_duration_outside_tolerance_is_rejected():
    """A strict preferred duration outside tolerance should fail."""

    scene = make_scene(14.5)

    policy = DurationPolicy(
        preferred_scene_duration=15,
        tolerance_seconds=0.25,
        strict=True,
    )

    result = validate_scene_duration(
        scene,
        policy,
    )

    assert result.is_valid is False
    assert result.issue_count == 1

    assert (
        result.issues[0].issue_type
        == "preferred_duration_mismatch"
    )


def test_non_strict_preferred_duration_is_not_enforced():
    """
    Preferred duration should remain advisory
    when strict mode is disabled.
    """

    scene = make_scene(12)

    policy = DurationPolicy(
        preferred_scene_duration=15,
        strict=False,
    )

    result = validate_scene_duration(
        scene,
        policy,
    )

    assert result.is_valid


def test_tolerance_applies_to_allowed_durations():
    """Allowed durations should respect configured tolerance."""

    scene = make_scene(14.8)

    policy = DurationPolicy(
        allowed_scene_durations=[
            15,
        ],
        tolerance_seconds=0.25,
    )

    result = validate_scene_duration(
        scene,
        policy,
    )

    assert result.is_valid


def test_invalid_policy_is_rejected_before_scene_validation():
    """Scene validation should reject invalid policy configuration."""

    scene = make_scene(15)

    policy = DurationPolicy(
        minimum_scene_duration=30,
        maximum_scene_duration=10,
    )

    with pytest.raises(
        ValueError,
        match="Invalid duration policy",
    ):
        validate_scene_duration(
            scene,
            policy,
        )


def test_negative_tolerance_is_invalid():
    """Negative tolerance values should fail policy validation."""

    policy = DurationPolicy(
        tolerance_seconds=-0.1,
    )

    assert not policy.is_valid()

    assert (
        "tolerance_seconds cannot be negative"
        in policy.validate()
    )


def test_duplicate_allowed_durations_are_invalid():
    """Allowed durations should not contain duplicates."""

    policy = DurationPolicy(
        allowed_scene_durations=[
            10,
            15,
            15,
        ]
    )

    assert not policy.is_valid()

    assert (
        "allowed_scene_durations cannot "
        "contain duplicates"
        in policy.validate()
    )


def test_non_positive_allowed_duration_is_invalid():
    """Allowed duration values must be greater than zero."""

    policy = DurationPolicy(
        allowed_scene_durations=[
            0,
            15,
        ]
    )

    assert not policy.is_valid()

    assert (
        "allowed_scene_durations must contain "
        "only values greater than 0"
        in policy.validate()
    )


def test_preferred_duration_below_minimum_is_invalid():
    """Preferred duration cannot contradict the minimum."""

    policy = DurationPolicy(
        preferred_scene_duration=5,
        minimum_scene_duration=10,
    )

    assert not policy.is_valid()

    assert (
        "preferred_scene_duration cannot be "
        "below minimum_scene_duration"
        in policy.validate()
    )


def test_preferred_duration_above_maximum_is_invalid():
    """Preferred duration cannot contradict the maximum."""

    policy = DurationPolicy(
        preferred_scene_duration=30,
        maximum_scene_duration=15,
    )

    assert not policy.is_valid()

    assert (
        "preferred_scene_duration cannot be "
        "above maximum_scene_duration"
        in policy.validate()
    )


def test_allowed_duration_below_minimum_is_invalid():
    """Allowed durations cannot contradict the minimum."""

    policy = DurationPolicy(
        minimum_scene_duration=10,
        allowed_scene_durations=[
            5,
            10,
            15,
        ],
    )

    assert not policy.is_valid()

    assert (
        "allowed_scene_durations cannot contain "
        "values below minimum_scene_duration"
        in policy.validate()
    )


def test_allowed_duration_above_maximum_is_invalid():
    """Allowed durations cannot contradict the maximum."""

    policy = DurationPolicy(
        maximum_scene_duration=15,
        allowed_scene_durations=[
            10,
            15,
            30,
        ],
    )

    assert not policy.is_valid()

    assert (
        "allowed_scene_durations cannot contain "
        "values above maximum_scene_duration"
        in policy.validate()
    )


def test_strict_preferred_duration_must_be_allowed():
    """
    Strict preferred duration should also belong
    to allowed durations when both are configured.
    """

    policy = DurationPolicy(
        preferred_scene_duration=15,
        allowed_scene_durations=[
            5,
            10,
            30,
        ],
        strict=True,
    )

    assert not policy.is_valid()

    assert (
        "strict preferred_scene_duration "
        "must also be present in "
        "allowed_scene_durations"
        in policy.validate()
    )


def test_duration_policy_serialization():
    """DurationPolicy should serialize cleanly."""

    policy = make_strict_policy()

    data = policy.to_dict()

    assert (
        data["preferred_scene_duration"]
        == 15
    )

    assert (
        data["minimum_scene_duration"]
        == 5
    )

    assert (
        data["maximum_scene_duration"]
        == 30
    )

    assert data["allowed_scene_durations"] == [
        5,
        10,
        15,
        30,
    ]

    assert data["tolerance_seconds"] == 0.25
    assert data["strict"] is True


def test_duration_validation_result_serialization():
    """Validation results and issues should serialize."""

    scene = make_scene(
        duration_seconds=12,
        scene_id=7,
    )

    policy = make_strict_policy()

    result = validate_scene_duration(
        scene,
        policy,
    )

    data = result.to_dict()

    assert data["scene_id"] == 7
    assert data["actual_duration"] == 12
    assert data["valid"] is False
    assert data["issue_count"] == 2

    issue_types = {
        issue["issue_type"]
        for issue in data["issues"]
    }

    assert issue_types == {
        "disallowed_duration",
        "preferred_duration_mismatch",
    }
