from ai_cinematic_workflow.negative_validator import (
    merge_negative_constraints,
    normalize_constraint,
    validate_negative_constraints,
)


def test_normalize_constraint():
    """Constraint text should be trimmed, lowercased and normalized."""

    result = normalize_constraint(
        "  Distorted   Face  "
    )

    assert result == "distorted face"


def test_validate_negative_constraints_removes_duplicates():
    """Duplicate and empty constraints should be removed."""

    result = validate_negative_constraints(
        [
            "Distorted Face",
            " distorted face ",
            "EXTRA FINGERS",
            "",
            "camera jitter",
            "Camera Jitter",
        ]
    )

    assert result.constraints == [
        "distorted face",
        "extra fingers",
        "camera jitter",
    ]

    assert result.warnings == []
    assert result.is_valid


def test_empty_constraints_generate_warning():
    """An empty usable constraint list should produce a warning."""

    result = validate_negative_constraints(
        [
            "",
            "   ",
        ]
    )

    assert result.constraints == []

    assert (
        "No usable negative constraints were provided."
        in result.warnings
    )

    assert not result.is_valid


def test_long_constraint_generates_warning():
    """Very long constraints should produce a warning."""

    long_constraint = "x" * 121

    result = validate_negative_constraints(
        [long_constraint]
    )

    assert len(result.constraints) == 1
    assert len(result.warnings) == 1

    assert "unusually long" in result.warnings[0]


def test_negative_prompt_output():
    """Normalized constraints should convert to prompt text."""

    result = validate_negative_constraints(
        [
            "Distorted Face",
            "Extra Fingers",
            "Camera Jitter",
        ]
    )

    assert result.to_prompt() == (
        "distorted face, extra fingers, camera jitter"
    )


def test_merge_negative_constraints():
    """Multiple constraint groups should merge without duplicates."""

    global_constraints = [
        "distorted face",
        "extra fingers",
    ]

    scene_constraints = [
        "camera jitter",
        "Distorted Face",
    ]

    result = merge_negative_constraints(
        global_constraints,
        scene_constraints,
    )

    assert result == [
        "distorted face",
        "extra fingers",
        "camera jitter",
    ]
