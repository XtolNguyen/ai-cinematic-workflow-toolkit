import pytest

from ai_cinematic_workflow.prompt_profiles import (
    PromptProfile,
    PromptProfileIssue,
    ResolvedPromptProfile,
    VALID_PROMPT_COMPONENTS,
    normalize_prompt_component,
    resolve_prompt_profile,
)


def test_normalize_prompt_component():
    """Prompt component names should normalize consistently."""

    assert (
        normalize_prompt_component(
            "Dialogue Or Vocals"
        )
        == "dialogue_or_vocals"
    )

    assert (
        normalize_prompt_component(
            "negative-constraints"
        )
        == "negative_constraints"
    )

    assert (
        normalize_prompt_component(
            "  Global Constraints  "
        )
        == "global_constraints"
    )


def test_default_prompt_profile_is_valid():
    """Default reusable prompt profile should validate."""

    profile = PromptProfile()

    assert profile.is_valid()
    assert profile.validate() == []


def test_prompt_profile_requires_name():
    """Prompt profiles require a meaningful name."""

    profile = PromptProfile(
        name="   ",
    )

    assert not profile.is_valid()

    assert (
        "prompt profile name cannot be empty"
        in profile.validate()
    )


def test_enabled_components_are_normalized_and_deduplicated():
    """
    Enabled component names should normalize and
    remove duplicates while preserving order.
    """

    profile = PromptProfile(
        enabled_components=[
            "Camera",
            "camera",
            "Dialogue Or Vocals",
            "dialogue-or-vocals",
        ],
    )

    assert (
        profile.normalized_enabled_components
        == [
            "camera",
            "dialogue_or_vocals",
        ]
    )


def test_disabled_components_are_normalized_and_deduplicated():
    """Disabled components should use canonical names."""

    profile = PromptProfile(
        disabled_components=[
            "Mood",
            "mood",
            "Negative Constraints",
        ],
    )

    assert (
        profile.normalized_disabled_components
        == [
            "mood",
            "negative_constraints",
        ]
    )


def test_empty_enabled_component_is_invalid():
    """Enabled component lists cannot contain blank names."""

    profile = PromptProfile(
        enabled_components=[
            "camera",
            "   ",
        ],
    )

    assert not profile.is_valid()

    assert (
        "enabled_components cannot contain "
        "empty component names"
        in profile.validate()
    )


def test_empty_disabled_component_is_invalid():
    """Disabled component lists cannot contain blank names."""

    profile = PromptProfile(
        disabled_components=[
            "mood",
            "   ",
        ],
    )

    assert not profile.is_valid()

    assert (
        "disabled_components cannot contain "
        "empty component names"
        in profile.validate()
    )


def test_enabled_and_disabled_conflict_is_invalid():
    """
    Canonically equivalent component names cannot be
    both enabled and disabled.
    """

    profile = PromptProfile(
        enabled_components=[
            "Dialogue Or Vocals",
        ],
        disabled_components=[
            "dialogue-or-vocals",
        ],
    )

    assert not profile.is_valid()

    assert (
        "prompt components cannot be both "
        "enabled and disabled"
        in profile.validate()
    )


def test_all_core_prompt_components_are_supported():
    """
    Every registered cinematic prompt component should
    be accepted by a strict profile.
    """

    components = sorted(
        VALID_PROMPT_COMPONENTS
    )

    profile = PromptProfile(
        name="all-core-components",
        enabled_components=components,
        strict_unknown_components=True,
    )

    assert profile.is_valid()

    resolved = resolve_prompt_profile(
        profile
    )

    assert set(
        resolved.enabled_components
    ) == set(
        VALID_PROMPT_COMPONENTS
    )

    assert resolved.is_valid


def test_strict_profile_rejects_unknown_component():
    """Strict profiles should reject unknown components."""

    profile = PromptProfile(
        enabled_components=[
            "future_platform_feature",
        ],
        strict_unknown_components=True,
    )

    assert not profile.is_valid()

    errors = profile.validate()

    assert any(
        "unknown prompt components are not "
        "allowed in strict mode"
        in error
        for error in errors
    )


def test_strict_profile_resolution_rejects_unknown_component():
    """
    Invalid strict profiles should be rejected before
    profile resolution.
    """

    profile = PromptProfile(
        enabled_components=[
            "future_component",
        ],
        strict_unknown_components=True,
    )

    with pytest.raises(
        ValueError,
        match="Invalid prompt profile",
    ):
        resolve_prompt_profile(
            profile
        )


def test_permissive_profile_preserves_unknown_component():
    """
    Permissive profiles should preserve extension
    components instead of rejecting them.
    """

    profile = PromptProfile(
        name="extension-profile",
        enabled_components=[
            "camera",
            "future_platform_feature",
        ],
        strict_unknown_components=False,
    )

    assert profile.is_valid()

    resolved = resolve_prompt_profile(
        profile
    )

    assert (
        "future_platform_feature"
        in resolved.enabled_components
    )

    assert resolved.is_valid
    assert resolved.warning_count == 1
    assert resolved.error_count == 0

    issue = resolved.issues[0]

    assert (
        issue.issue_type
        == "unknown_prompt_component"
    )

    assert issue.severity == "warning"

    assert (
        issue.component
        == "future_platform_feature"
    )

    assert (
        issue.profile_name
        == "extension-profile"
    )


def test_permissive_unknown_disabled_component_is_preserved():
    """
    Unknown disabled extension components should also
    survive permissive resolution.
    """

    profile = PromptProfile(
        name="permissive-disabled",
        disabled_components=[
            "future_audio_layer",
        ],
        strict_unknown_components=False,
    )

    resolved = resolve_prompt_profile(
        profile
    )

    assert (
        "future_audio_layer"
        in resolved.disabled_components
    )

    assert resolved.warning_count == 1


def test_profile_serialization_is_normalized():
    """PromptProfile.to_dict should expose canonical values."""

    profile = PromptProfile(
        name="cinematic",
        enabled_components=[
            "Camera",
            "Dialogue Or Vocals",
        ],
        disabled_components=[
            "Mood",
        ],
        strict_unknown_components=True,
        custom_config={
            "detail_level": "high",
        },
    )

    data = profile.to_dict()

    assert data["name"] == "cinematic"

    assert (
        data["enabled_components"]
        == [
            "camera",
            "dialogue_or_vocals",
        ]
    )

    assert (
        data["disabled_components"]
        == [
            "mood",
        ]
    )

    assert (
        data["strict_unknown_components"]
        is True
    )

    assert (
        data["custom_config"]
        == {
            "detail_level": "high",
        }
    )


def test_profile_serialization_does_not_expose_mutable_config():
    """
    Mutating serialized custom configuration should not
    mutate the original profile.
    """

    profile = PromptProfile(
        custom_config={
            "camera": {
                "detail_level": "medium",
            },
        },
    )

    data = profile.to_dict()

    data["custom_config"][
        "camera"
    ][
        "detail_level"
    ] = "changed"

    assert (
        profile.custom_config[
            "camera"
        ][
            "detail_level"
        ]
        == "medium"
    )


def test_custom_config_requires_non_empty_string_keys():
    """Custom prompt configuration requires valid keys."""

    profile = PromptProfile(
        custom_config={
            "": "invalid",
        },
    )

    assert not profile.is_valid()

    assert (
        "custom prompt configuration keys "
        "must be non-empty strings"
        in profile.validate()
    )


def test_custom_config_must_be_json_serializable():
    """
    Custom configuration should remain portable
    through JSON-based project exports.
    """

    profile = PromptProfile(
        custom_config={
            "invalid_value": {
                "a",
                "b",
            },
        },
    )

    assert not profile.is_valid()

    assert (
        "custom prompt configuration "
        "must be JSON serializable"
        in profile.validate()
    )


def test_profile_resolves_without_base():
    """A standalone profile should resolve directly."""

    profile = PromptProfile(
        name="standalone",
        enabled_components=[
            "camera",
            "characters",
        ],
        disabled_components=[
            "mood",
        ],
    )

    resolved = resolve_prompt_profile(
        profile
    )

    assert (
        resolved.name
        == "standalone"
    )

    assert (
        resolved.source_profile_name
        == "standalone"
    )

    assert (
        resolved.base_profile_name
        is None
    )

    assert (
        resolved.enabled_components
        == [
            "camera",
            "characters",
        ]
    )

    assert (
        resolved.disabled_components
        == [
            "mood",
        ]
    )


def test_base_profile_inheritance():
    """
    A child profile should inherit a base and then apply
    its own component configuration.
    """

    base = PromptProfile(
        name="cinematic-default",
        enabled_components=[
            "camera",
            "characters",
            "location",
            "performance",
            "lighting",
            "mood",
            "negative_constraints",
        ],
        disabled_components=[
            "dialogue_or_vocals",
        ],
    )

    child = PromptProfile(
        name="music-video",
        enabled_components=[
            "dialogue_or_vocals",
            "global_constraints",
        ],
        disabled_components=[
            "mood",
        ],
    )

    resolved = resolve_prompt_profile(
        child,
        base_profile=base,
    )

    assert (
        resolved.base_profile_name
        == "cinematic-default"
    )

    assert (
        resolved.source_profile_name
        == "music-video"
    )

    assert (
        resolved.enabled_components
        == [
            "camera",
            "characters",
            "location",
            "performance",
            "lighting",
            "negative_constraints",
            "dialogue_or_vocals",
            "global_constraints",
        ]
    )

    assert (
        resolved.disabled_components
        == [
            "mood",
        ]
    )


def test_child_can_disable_base_enabled_component():
    """
    Child profile settings should take precedence
    over inherited base settings.
    """

    base = PromptProfile(
        enabled_components=[
            "camera",
            "mood",
        ],
    )

    child = PromptProfile(
        name="child",
        disabled_components=[
            "mood",
        ],
    )

    resolved = resolve_prompt_profile(
        child,
        base_profile=base,
    )

    assert (
        "mood"
        not in resolved.enabled_components
    )

    assert (
        "mood"
        in resolved.disabled_components
    )


def test_child_can_enable_base_disabled_component():
    """Child profile may re-enable a base-disabled component."""

    base = PromptProfile(
        disabled_components=[
            "dialogue_or_vocals",
        ],
    )

    child = PromptProfile(
        name="dialogue-profile",
        enabled_components=[
            "dialogue_or_vocals",
        ],
    )

    resolved = resolve_prompt_profile(
        child,
        base_profile=base,
    )

    assert (
        "dialogue_or_vocals"
        in resolved.enabled_components
    )

    assert (
        "dialogue_or_vocals"
        not in resolved.disabled_components
    )


def test_profile_cannot_inherit_from_itself():
    """Self inheritance should be rejected."""

    profile = PromptProfile(
        name="self-profile",
    )

    with pytest.raises(
        ValueError,
        match=(
            "a prompt profile cannot inherit "
            "from itself"
        ),
    ):
        resolve_prompt_profile(
            profile,
            base_profile=profile,
        )


def test_invalid_base_profile_is_rejected():
    """Resolution should reject invalid base profiles."""

    base = PromptProfile(
        name="   ",
    )

    child = PromptProfile(
        name="child",
    )

    with pytest.raises(
        ValueError,
        match="Invalid base prompt profile",
    ):
        resolve_prompt_profile(
            child,
            base_profile=base,
        )


def test_enable_override_takes_precedence():
    """
    Runtime enable overrides should be applied after
    base and child configuration.
    """

    profile = PromptProfile(
        name="override-profile",
        disabled_components=[
            "camera",
        ],
    )

    resolved = resolve_prompt_profile(
        profile,
        enable_overrides=[
            "camera",
        ],
    )

    assert (
        "camera"
        in resolved.enabled_components
    )

    assert (
        "camera"
        not in resolved.disabled_components
    )


def test_disable_override_takes_precedence():
    """
    Runtime disable overrides should be able to remove
    previously enabled components.
    """

    profile = PromptProfile(
        name="override-profile",
        enabled_components=[
            "location",
            "lighting",
        ],
    )

    resolved = resolve_prompt_profile(
        profile,
        disable_overrides=[
            "location",
        ],
    )

    assert (
        "location"
        not in resolved.enabled_components
    )

    assert (
        "location"
        in resolved.disabled_components
    )

    assert (
        "lighting"
        in resolved.enabled_components
    )


def test_conflicting_runtime_overrides_are_rejected():
    """
    The same component cannot be enabled and disabled
    by one runtime override operation.
    """

    profile = PromptProfile(
        name="runtime-profile",
    )

    with pytest.raises(
        ValueError,
        match=(
            "prompt components cannot be both "
            "enabled and disabled by overrides"
        ),
    ):
        resolve_prompt_profile(
            profile,
            enable_overrides=[
                "camera",
            ],
            disable_overrides=[
                "Camera",
            ],
        )


def test_strict_profile_rejects_unknown_runtime_override():
    """Strict mode should also apply to runtime overrides."""

    profile = PromptProfile(
        name="strict-runtime",
        strict_unknown_components=True,
    )

    with pytest.raises(
        ValueError,
        match=(
            "unknown prompt components are not "
            "allowed in strict mode"
        ),
    ):
        resolve_prompt_profile(
            profile,
            enable_overrides=[
                "future_component",
            ],
        )


def test_permissive_profile_accepts_unknown_runtime_override():
    """Permissive runtime extensions should be preserved."""

    profile = PromptProfile(
        name="permissive-runtime",
        strict_unknown_components=False,
    )

    resolved = resolve_prompt_profile(
        profile,
        enable_overrides=[
            "future_component",
        ],
    )

    assert (
        "future_component"
        in resolved.enabled_components
    )

    assert resolved.warning_count == 1
    assert resolved.is_valid


def test_base_profile_is_not_mutated():
    """
    Inheritance and child resolution must not mutate
    the source base profile.
    """

    base = PromptProfile(
        name="base",
        enabled_components=[
            "camera",
            "mood",
        ],
        disabled_components=[
            "dialogue_or_vocals",
        ],
        custom_config={
            "camera": {
                "detail_level": "medium",
            },
        },
    )

    child = PromptProfile(
        name="child",
        enabled_components=[
            "dialogue_or_vocals",
        ],
        disabled_components=[
            "mood",
        ],
        custom_config={
            "camera": {
                "detail_level": "high",
            },
        },
    )

    base_before = base.to_dict()

    resolve_prompt_profile(
        child,
        base_profile=base,
    )

    assert (
        base.to_dict()
        == base_before
    )


def test_child_profile_is_not_mutated():
    """Runtime overrides must not mutate the source profile."""

    profile = PromptProfile(
        name="child",
        enabled_components=[
            "camera",
        ],
        custom_config={
            "camera": {
                "detail_level": "medium",
            },
        },
    )

    before = profile.to_dict()

    resolve_prompt_profile(
        profile,
        enable_overrides=[
            "lighting",
        ],
        custom_config_overrides={
            "camera": {
                "detail_level": "high",
            },
        },
    )

    assert (
        profile.to_dict()
        == before
    )


def test_nested_custom_configuration_is_merged():
    """
    Base, child, and runtime custom configuration should
    merge recursively.
    """

    base = PromptProfile(
        name="base",
        custom_config={
            "camera": {
                "detail_level": "medium",
                "include_lens": True,
            },
            "style": {
                "contrast": "natural",
            },
        },
    )

    child = PromptProfile(
        name="child",
        custom_config={
            "camera": {
                "detail_level": "high",
            },
            "style": {
                "grain": "fine",
            },
        },
    )

    resolved = resolve_prompt_profile(
        child,
        base_profile=base,
        custom_config_overrides={
            "camera": {
                "include_lens": False,
            },
        },
    )

    assert (
        resolved.custom_config
        == {
            "camera": {
                "detail_level": "high",
                "include_lens": False,
            },
            "style": {
                "contrast": "natural",
                "grain": "fine",
            },
        }
    )


def test_invalid_custom_config_override_is_rejected():
    """
    Runtime custom configuration should obey the
    same serialization rules as profile configuration.
    """

    profile = PromptProfile(
        name="runtime-config",
    )

    with pytest.raises(
        ValueError,
        match=(
            "Invalid custom prompt configuration "
            "overrides"
        ),
    ):
        resolve_prompt_profile(
            profile,
            custom_config_overrides={
                "invalid": {
                    "not",
                    "json",
                },
            },
        )


def test_resolved_name_can_be_overridden():
    """Callers may assign a reusable resolved profile name."""

    profile = PromptProfile(
        name="music-video",
    )

    resolved = resolve_prompt_profile(
        profile,
        resolved_name=(
            "music-video-performance"
        ),
    )

    assert (
        resolved.name
        == "music-video-performance"
    )

    assert (
        resolved.source_profile_name
        == "music-video"
    )


def test_blank_resolved_name_falls_back_to_profile_name():
    """Blank resolved names should not replace the source name."""

    profile = PromptProfile(
        name="cinematic-default",
    )

    resolved = resolve_prompt_profile(
        profile,
        resolved_name="   ",
    )

    assert (
        resolved.name
        == "cinematic-default"
    )


def test_resolved_profile_component_helpers():
    """
    Resolved profiles should provide normalized
    component lookup helpers.
    """

    profile = PromptProfile(
        enabled_components=[
            "Dialogue Or Vocals",
            "Camera",
        ],
        disabled_components=[
            "Mood",
        ],
    )

    resolved = resolve_prompt_profile(
        profile
    )

    assert resolved.is_enabled(
        "dialogue-or-vocals"
    )

    assert resolved.is_enabled(
        "CAMERA"
    )

    assert resolved.is_disabled(
        "mood"
    )

    assert not resolved.is_enabled(
        "lighting"
    )


def test_prompt_profile_issue_serialization():
    """Structured profile issues should serialize cleanly."""

    issue = PromptProfileIssue(
        issue_type=(
            "unknown_prompt_component"
        ),
        severity="warning",
        message="Example warning",
        component="future_component",
        profile_name="extension-profile",
    )

    data = issue.to_dict()

    assert (
        data["issue_type"]
        == "unknown_prompt_component"
    )

    assert data["severity"] == "warning"

    assert (
        data["message"]
        == "Example warning"
    )

    assert (
        data["component"]
        == "future_component"
    )

    assert (
        data["profile_name"]
        == "extension-profile"
    )


def test_resolved_profile_serialization():
    """
    ResolvedPromptProfile should serialize summary,
    inheritance, components, configuration, and issues.
    """

    issue = PromptProfileIssue(
        issue_type=(
            "unknown_prompt_component"
        ),
        severity="warning",
        message="Extension component preserved",
        component="future_component",
        profile_name="extension",
    )

    resolved = ResolvedPromptProfile(
        name="resolved-extension",
        source_profile_name="extension",
        base_profile_name="base",
        enabled_components=[
            "camera",
            "future_component",
        ],
        disabled_components=[
            "mood",
        ],
        strict_unknown_components=False,
        custom_config={
            "detail_level": "high",
        },
        issues=[
            issue,
        ],
    )

    data = resolved.to_dict()

    assert (
        data["summary"]["valid"]
        is True
    )

    assert (
        data["summary"][
            "enabled_component_count"
        ]
        == 2
    )

    assert (
        data["summary"][
            "disabled_component_count"
        ]
        == 1
    )

    assert (
        data["summary"]["warning_count"]
        == 1
    )

    assert (
        data["summary"]["error_count"]
        == 0
    )

    assert (
        data["name"]
        == "resolved-extension"
    )

    assert (
        data["base_profile_name"]
        == "base"
    )

    assert (
        data["issues"][0][
            "component"
        ]
        == "future_component"
    )


def test_resolved_profile_serialization_does_not_leak_mutable_config():
    """
    Serialized resolved configuration should not expose
    the result's internal custom configuration.
    """

    profile = PromptProfile(
        name="safe-config",
        custom_config={
            "camera": {
                "detail_level": "high",
            },
        },
    )

    resolved = resolve_prompt_profile(
        profile
    )

    data = resolved.to_dict()

    data["custom_config"][
        "camera"
    ][
        "detail_level"
    ] = "changed"

    assert (
        resolved.custom_config[
            "camera"
        ][
            "detail_level"
        ]
        == "high"
    )
