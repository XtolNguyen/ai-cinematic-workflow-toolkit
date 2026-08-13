import json

import pytest

from ai_cinematic_workflow import (
    Camera,
    CinematicProject,
    ContinuityProfile,
    DurationPolicy,
    GlobalConstraints,
    ProjectMetadata,
    PromptProfile,
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
            title="Prompt Profile Integration Test",
            project_type="cinematic",
        ),
        scenes=scenes,
    )


def make_base_prompt_profile() -> PromptProfile:
    """Create a reusable cinematic base prompt profile."""

    return PromptProfile(
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
        custom_config={
            "camera": {
                "detail_level": "medium",
                "include_lens": True,
            },
            "style": {
                "detail_level": "cinematic",
            },
        },
    )


def make_music_video_prompt_profile() -> PromptProfile:
    """Create a reusable child prompt profile."""

    return PromptProfile(
        name="music-video",
        enabled_components=[
            "dialogue_or_vocals",
            "global_constraints",
        ],
        disabled_components=[
            "mood",
        ],
        custom_config={
            "camera": {
                "detail_level": "high",
            },
            "performance": {
                "priority": "high",
            },
        },
    )


def test_prompt_profile_is_exported():
    """
    Supplying a PromptProfile should add a structured
    prompt_profile section to the complete project export.
    """

    project = make_project(
        [
            make_scene(1),
            make_scene(2),
        ]
    )

    profile = PromptProfile(
        name="cinematic",
        enabled_components=[
            "characters",
            "location",
            "camera",
            "lighting",
        ],
        disabled_components=[
            "mood",
        ],
    )

    data = project_to_dict(
        project,
        prompt_profile=profile,
    )

    assert "prompt_profile" in data

    result = data[
        "prompt_profile"
    ]

    assert (
        result["mode"]
        == "resolved_prompt_profile"
    )

    assert (
        result["name"]
        == "cinematic"
    )

    assert (
        result["source_profile_name"]
        == "cinematic"
    )

    assert (
        result["base_profile_name"]
        is None
    )

    assert (
        result["enabled_components"]
        == [
            "characters",
            "location",
            "camera",
            "lighting",
        ]
    )

    assert (
        result["disabled_components"]
        == [
            "mood",
        ]
    )

    assert (
        result["summary"]["valid"]
        is True
    )


def test_base_profile_inheritance_is_exported():
    """
    Complete project export should preserve resolved
    base-profile inheritance.
    """

    project = make_project(
        [
            make_scene(1),
        ]
    )

    base = make_base_prompt_profile()
    child = make_music_video_prompt_profile()

    data = project_to_dict(
        project,
        prompt_profile=child,
        base_prompt_profile=base,
    )

    result = data[
        "prompt_profile"
    ]

    assert (
        result["base_profile_name"]
        == "cinematic-default"
    )

    assert (
        result["source_profile_name"]
        == "music-video"
    )

    assert (
        result["enabled_components"]
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
        result["disabled_components"]
        == [
            "mood",
        ]
    )


def test_prompt_profile_runtime_overrides_are_exported():
    """
    Runtime enable and disable overrides should be applied
    after base and child profile configuration.
    """

    project = make_project(
        [
            make_scene(1),
        ]
    )

    base = make_base_prompt_profile()
    child = make_music_video_prompt_profile()

    data = project_to_dict(
        project,
        prompt_profile=child,
        base_prompt_profile=base,
        prompt_enable_overrides=[
            "continuity",
        ],
        prompt_disable_overrides=[
            "lighting",
        ],
        prompt_resolved_name=(
            "music-video-production"
        ),
    )

    result = data[
        "prompt_profile"
    ]

    assert (
        result["name"]
        == "music-video-production"
    )

    assert (
        "continuity"
        in result["enabled_components"]
    )

    assert (
        "lighting"
        not in result["enabled_components"]
    )

    assert (
        "lighting"
        in result["disabled_components"]
    )

    assert (
        "mood"
        in result["disabled_components"]
    )


def test_nested_custom_config_is_resolved_in_export():
    """
    Base, child, and runtime custom configuration should
    merge recursively in the complete export.
    """

    project = make_project(
        [
            make_scene(1),
        ]
    )

    base = make_base_prompt_profile()
    child = make_music_video_prompt_profile()

    data = project_to_dict(
        project,
        prompt_profile=child,
        base_prompt_profile=base,
        prompt_config_overrides={
            "camera": {
                "include_lens": False,
            },
            "style": {
                "contrast": "natural",
            },
        },
    )

    custom_config = data[
        "prompt_profile"
    ][
        "custom_config"
    ]

    assert (
        custom_config
        == {
            "camera": {
                "detail_level": "high",
                "include_lens": False,
            },
            "style": {
                "detail_level": "cinematic",
                "contrast": "natural",
            },
            "performance": {
                "priority": "high",
            },
        }
    )


def test_profile_resolution_does_not_mutate_source_profiles():
    """
    Export-time inheritance and overrides must not mutate
    either source PromptProfile.
    """

    project = make_project(
        [
            make_scene(1),
        ]
    )

    base = make_base_prompt_profile()
    child = make_music_video_prompt_profile()

    base_before = base.to_dict()
    child_before = child.to_dict()

    project_to_dict(
        project,
        prompt_profile=child,
        base_prompt_profile=base,
        prompt_enable_overrides=[
            "continuity",
        ],
        prompt_disable_overrides=[
            "lighting",
        ],
        prompt_config_overrides={
            "camera": {
                "include_lens": False,
            },
        },
    )

    assert (
        base.to_dict()
        == base_before
    )

    assert (
        child.to_dict()
        == child_before
    )


def test_permissive_unknown_component_warning_is_exported():
    """
    Permissive profiles should preserve extension components
    and export their structured warning.
    """

    project = make_project(
        [
            make_scene(1),
        ]
    )

    profile = PromptProfile(
        name="extension-profile",
        enabled_components=[
            "camera",
            "future_platform_component",
        ],
        strict_unknown_components=False,
    )

    data = project_to_dict(
        project,
        prompt_profile=profile,
    )

    result = data[
        "prompt_profile"
    ]

    assert (
        "future_platform_component"
        in result["enabled_components"]
    )

    assert (
        result["summary"]["valid"]
        is True
    )

    assert (
        result["summary"]["warning_count"]
        == 1
    )

    assert (
        result["issues"][0][
            "issue_type"
        ]
        == "unknown_prompt_component"
    )

    assert (
        result["issues"][0][
            "component"
        ]
        == "future_platform_component"
    )


def test_export_without_prompt_profile_is_backward_compatible():
    """
    Existing project exports should not gain prompt_profile
    data unless a profile is explicitly supplied.
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
        "prompt_profile"
        not in data
    )

    assert "project" in data
    assert "timeline" in data
    assert "workflow" in data


def test_prompt_options_without_source_profile_are_rejected():
    """
    Exporter should not silently ignore prompt-profile
    inheritance or overrides when no PromptProfile exists.
    """

    project = make_project(
        [
            make_scene(1),
        ]
    )

    with pytest.raises(
        ValueError,
        match=(
            "prompt_profile is required when "
            "prompt-profile inheritance or overrides "
            "are supplied"
        ),
    ):
        project_to_dict(
            project,
            prompt_enable_overrides=[
                "camera",
            ],
        )


def test_base_profile_without_source_profile_is_rejected():
    """
    A base profile alone is incomplete because profile
    resolution requires a source PromptProfile.
    """

    project = make_project(
        [
            make_scene(1),
        ]
    )

    with pytest.raises(
        ValueError,
        match=(
            "prompt_profile is required when "
            "prompt-profile inheritance or overrides "
            "are supplied"
        ),
    ):
        project_to_dict(
            project,
            base_prompt_profile=(
                make_base_prompt_profile()
            ),
        )


def test_invalid_prompt_profile_is_rejected_by_exporter():
    """Exporter should reject invalid strict PromptProfiles."""

    project = make_project(
        [
            make_scene(1),
        ]
    )

    profile = PromptProfile(
        name="strict-invalid",
        enabled_components=[
            "unknown_component",
        ],
        strict_unknown_components=True,
    )

    with pytest.raises(
        ValueError,
        match="Invalid prompt profile",
    ):
        project_to_dict(
            project,
            prompt_profile=profile,
        )


def test_project_to_json_preserves_prompt_profile():
    """
    JSON serialization should preserve resolved prompt-profile
    inheritance and configuration.
    """

    project = make_project(
        [
            make_scene(1),
        ]
    )

    content = project_to_json(
        project,
        prompt_profile=(
            make_music_video_prompt_profile()
        ),
        base_prompt_profile=(
            make_base_prompt_profile()
        ),
        prompt_resolved_name=(
            "portable-music-video"
        ),
    )

    data = json.loads(
        content
    )

    result = data[
        "prompt_profile"
    ]

    assert (
        result["mode"]
        == "resolved_prompt_profile"
    )

    assert (
        result["name"]
        == "portable-music-video"
    )

    assert (
        result["base_profile_name"]
        == "cinematic-default"
    )

    assert (
        "global_constraints"
        in result["enabled_components"]
    )

    assert (
        "mood"
        in result["disabled_components"]
    )


def test_save_project_json_preserves_prompt_profile(
    tmp_path,
):
    """
    Saving and reloading complete project JSON should preserve
    PromptProfile resolution.
    """

    project = make_project(
        [
            make_scene(1),
            make_scene(2),
        ]
    )

    output_path = (
        tmp_path
        / "prompt_profiles"
        / "project.json"
    )

    saved_path = save_project_json(
        project,
        output_path,
        prompt_profile=(
            make_music_video_prompt_profile()
        ),
        base_prompt_profile=(
            make_base_prompt_profile()
        ),
    )

    data = json.loads(
        saved_path.read_text(
            encoding="utf-8"
        )
    )

    assert (
        "prompt_profile"
        in data
    )

    assert (
        data["prompt_profile"][
            "source_profile_name"
        ]
        == "music-video"
    )

    assert (
        data["prompt_profile"][
            "base_profile_name"
        ]
        == "cinematic-default"
    )


def test_all_optional_project_layers_can_coexist():
    """
    DurationPolicy, ContinuityProfile, GlobalConstraints,
    and PromptProfile should coexist in one complete export.
    """

    project = make_project(
        [
            make_scene(
                1,
                location="Beach",
                negative_constraints=[
                    "text artifacts",
                ],
            ),
            make_scene(
                2,
                location="City",
                negative_constraints=[
                    "camera jitter",
                ],
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

    global_constraints = GlobalConstraints(
        name="production-rules",
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
        visual_style_constraints=[
            "cinematic photorealism",
        ],
    )

    prompt_profile = PromptProfile(
        name="cinematic-prompt",
        enabled_components=[
            "characters",
            "location",
            "camera",
            "performance",
            "lighting",
            "continuity",
            "negative_constraints",
            "global_constraints",
        ],
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
        prompt_profile=(
            prompt_profile
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
        "prompt_profile"
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

    assert (
        data["prompt_profile"][
            "summary"
        ]["valid"]
        is True
    )


def test_prompt_profile_preserves_existing_workflow_output():
    """
    Opt-in PromptProfile resolution should not remove or replace
    existing workflow processing.
    """

    project = make_project(
        [
            make_scene(1),
            make_scene(2),
        ]
    )

    data = project_to_dict(
        project,
        prompt_profile=(
            make_base_prompt_profile()
        ),
    )

    assert "workflow" in data

    assert (
        data["workflow"][
            "summary"
        ][
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
