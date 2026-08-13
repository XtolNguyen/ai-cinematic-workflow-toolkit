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
    location: str = "Rooftop at night",
    wardrobe: str = "black cinematic outfit",
    hair: str = "long dark hair",
    lighting: str = "Blue cinematic night lighting",
    mood: str = "Intimate and reflective",
    dialogue_or_vocals: str = "Song lyrics",
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
        characters=[
            "Lead performer",
        ],
        performance=(
            "Natural emotional vocal performance"
        ),
        lighting=lighting,
        mood=mood,
        dialogue_or_vocals=(
            dialogue_or_vocals
        ),
        continuity={
            "wardrobe": wardrobe,
            "hair": hair,
        },
        negative_constraints=list(
            negative_constraints
            or [
                "text artifacts",
            ]
        ),
    )


def make_project(
    scenes: list[Scene],
) -> CinematicProject:
    """Create a reusable cinematic project."""

    return CinematicProject(
        metadata=ProjectMetadata(
            title=(
                "Structured Prompt Integration Test"
            ),
            project_type="cinematic",
        ),
        scenes=scenes,
    )


def make_base_prompt_profile() -> PromptProfile:
    """Create a reusable base cinematic prompt profile."""

    return PromptProfile(
        name="cinematic-default",
        enabled_components=[
            "characters",
            "location",
            "camera",
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
        },
    )


def make_music_video_prompt_profile() -> PromptProfile:
    """Create a reusable music-video child profile."""

    return PromptProfile(
        name="music-video",
        enabled_components=[
            "dialogue_or_vocals",
            "continuity",
            "global_constraints",
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


def make_global_constraints() -> GlobalConstraints:
    """Create reusable project-wide production rules."""

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
    )


def test_structured_prompts_are_exported_per_scene():
    """
    Enabling structured prompts should create one
    StructuredPromptResult for every project Scene.
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
        include_structured_prompts=True,
    )

    assert (
        "structured_prompts"
        in data
    )

    result = data[
        "structured_prompts"
    ]

    assert (
        result["mode"]
        == "structured_prompt_sections"
    )

    assert (
        result["summary"]["scene_count"]
        == 3
    )

    assert (
        result["summary"][
            "valid_scene_count"
        ]
        == 3
    )

    assert (
        len(
            result["scene_results"]
        )
        == 3
    )

    assert [
        item["scene_id"]
        for item in result[
            "scene_results"
        ]
    ] == [
        1,
        2,
        3,
    ]


def test_structured_prompts_use_canonical_section_order():
    """
    Per-scene sections should preserve deterministic
    canonical ordering.
    """

    project = make_project(
        [
            make_scene(1),
        ]
    )

    data = project_to_dict(
        project,
        include_structured_prompts=True,
    )

    scene_result = data[
        "structured_prompts"
    ][
        "scene_results"
    ][0]

    assert (
        scene_result[
            "included_components"
        ]
        == [
            "characters",
            "location",
            "camera",
            "performance",
            "lighting",
            "mood",
            "dialogue_or_vocals",
            "continuity",
            "negative_constraints",
        ]
    )

    assert [
        section["order"]
        for section in scene_result[
            "sections"
        ]
    ] == [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        10,
    ]


def test_prompt_profile_filters_structured_sections():
    """
    The same resolved PromptProfile used for export should
    control structured prompt section inclusion.
    """

    project = make_project(
        [
            make_scene(1),
        ]
    )

    base = make_base_prompt_profile()
    child = (
        make_music_video_prompt_profile()
    )

    data = project_to_dict(
        project,
        prompt_profile=child,
        base_prompt_profile=base,
        include_structured_prompts=True,
    )

    prompt_profile = data[
        "prompt_profile"
    ]

    structured = data[
        "structured_prompts"
    ]

    scene_result = structured[
        "scene_results"
    ][0]

    assert (
        structured["summary"][
            "prompt_profile_name"
        ]
        == prompt_profile["name"]
    )

    assert (
        scene_result[
            "prompt_profile_name"
        ]
        == "music-video"
    )

    assert (
    scene_result[
        "included_components"
    ]
    == [
        "characters",
        "location",
        "camera",
        "performance",
        "lighting",
        "dialogue_or_vocals",
        "continuity",
        "negative_constraints",
    ]
)

    assert (
        "mood"
        not in scene_result[
            "included_components"
        ]
    )

    mood_omission = next(
        item
        for item in scene_result[
            "omitted_components"
        ]
        if (
            item["component"]
            == "mood"
        )
    )

    assert (
        mood_omission["reason"]
        == "disabled_by_profile"
    )


def test_structured_prompt_runtime_profile_overrides_are_applied():
    """
    Runtime PromptProfile overrides should affect the
    structured prompt representation.
    """

    project = make_project(
        [
            make_scene(1),
        ]
    )

    data = project_to_dict(
        project,
        prompt_profile=(
            make_music_video_prompt_profile()
        ),
        base_prompt_profile=(
            make_base_prompt_profile()
        ),
        prompt_enable_overrides=[
            "mood",
        ],
        prompt_disable_overrides=[
            "lighting",
        ],
        prompt_resolved_name=(
            "music-video-production"
        ),
        include_structured_prompts=True,
    )

    structured = data[
        "structured_prompts"
    ]

    scene_result = structured[
        "scene_results"
    ][0]

    assert (
        structured["summary"][
            "prompt_profile_name"
        ]
        == "music-video-production"
    )

    assert (
        scene_result[
            "prompt_profile_name"
        ]
        == "music-video-production"
    )

    assert (
        "mood"
        in scene_result[
            "included_components"
        ]
    )

    assert (
        "lighting"
        not in scene_result[
            "included_components"
        ]
    )

    lighting = next(
        item
        for item in scene_result[
            "omitted_components"
        ]
        if (
            item["component"]
            == "lighting"
        )
    )

    assert (
        lighting["reason"]
        == "disabled_by_profile"
    )


def test_global_constraints_are_available_to_structured_prompts():
    """
    GlobalConstraints should become a structured prompt
    section when enabled by PromptProfile.
    """

    project = make_project(
        [
            make_scene(1),
        ]
    )

    profile = PromptProfile(
        name="global-aware",
        enabled_components=[
            "global_constraints",
        ],
    )

    data = project_to_dict(
        project,
        global_constraints=(
            make_global_constraints()
        ),
        prompt_profile=profile,
        include_structured_prompts=True,
    )

    scene_result = data[
        "structured_prompts"
    ][
        "scene_results"
    ][0]

    global_section = next(
        section
        for section in scene_result[
            "sections"
        ]
        if (
            section["section_id"]
            == "global_constraints"
        )
    )

    assert (
        global_section["content"]["name"]
        == "cinematic-production"
    )

    assert (
        global_section["content"][
            "required_constraints"
        ]
        == [
            "maintain cinematic realism",
        ]
    )

    assert (
        global_section["content"][
            "visual_style_constraints"
        ]
        == [
            "cinematic photorealism",
        ]
    )

    assert (
        global_section["metadata"][
            "source"
        ]
        == "global_constraints"
    )


def test_global_and_scene_negatives_are_resolved_in_section():
    """
    Structured negative sections should contain global,
    prohibited, and Scene negatives without duplicates.
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

    profile = PromptProfile(
        name="negative-resolution",
        enabled_components=[
            "negative_constraints",
        ],
    )

    data = project_to_dict(
        project,
        global_constraints=(
            make_global_constraints()
        ),
        prompt_profile=profile,
        include_structured_prompts=True,
    )

    scene_result = data[
        "structured_prompts"
    ][
        "scene_results"
    ][0]

    negative_section = next(
        section
        for section in scene_result[
            "sections"
        ]
        if (
            section["section_id"]
            == "negative_constraints"
        )
    )

    assert (
        negative_section["content"]
        == [
            "distorted face",
            "extra fingers",
            "duplicate limbs",
            "text artifacts",
        ]
    )

    assert (
        negative_section[
            "metadata"
        ][
            "source"
        ]
        == "resolved_scene_constraints"
    )


def test_empty_sections_are_omitted_by_default():
    """
    Empty enabled sections should remain omitted when the
    include-empty flag is disabled.
    """

    project = make_project(
        [
            make_scene(
                1,
                dialogue_or_vocals="",
            ),
        ]
    )

    profile = PromptProfile(
        name="dialogue-test",
        enabled_components=[
            "dialogue_or_vocals",
        ],
    )

    data = project_to_dict(
        project,
        prompt_profile=profile,
        include_structured_prompts=True,
    )

    scene_result = data[
        "structured_prompts"
    ][
        "scene_results"
    ][0]

    assert (
        scene_result[
            "sections"
        ]
        == []
    )

    omission = next(
        item
        for item in scene_result[
            "omitted_components"
        ]
        if (
            item["component"]
            == "dialogue_or_vocals"
        )
    )

    assert (
        omission["reason"]
        == "empty"
    )

    assert (
        data["structured_prompts"][
            "summary"
        ][
            "include_empty_sections"
        ]
        is False
    )


def test_empty_sections_can_be_preserved():
    """
    include_empty_prompt_sections=True should preserve
    active empty prompt sections.
    """

    project = make_project(
        [
            make_scene(
                1,
                dialogue_or_vocals="",
            ),
        ]
    )

    profile = PromptProfile(
        name="dialogue-test",
        enabled_components=[
            "dialogue_or_vocals",
        ],
    )

    data = project_to_dict(
        project,
        prompt_profile=profile,
        include_structured_prompts=True,
        include_empty_prompt_sections=True,
    )

    scene_result = data[
        "structured_prompts"
    ][
        "scene_results"
    ][0]

    assert (
        len(
            scene_result["sections"]
        )
        == 1
    )

    section = scene_result[
        "sections"
    ][0]

    assert (
        section["section_id"]
        == "dialogue_or_vocals"
    )

    assert section["content"] == ""

    assert (
        section["metadata"]["empty"]
        is True
    )

    assert (
        data["structured_prompts"][
            "summary"
        ][
            "include_empty_sections"
        ]
        is True
    )


def test_empty_section_option_requires_structured_prompt_export():
    """
    The exporter should reject an empty-section option
    that would otherwise be silently ignored.
    """

    project = make_project(
        [
            make_scene(1),
        ]
    )

    with pytest.raises(
        ValueError,
        match=(
            "include_structured_prompts "
            "must be True"
        ),
    ):
        project_to_dict(
            project,
            include_empty_prompt_sections=True,
        )


def test_export_without_structured_prompts_is_backward_compatible():
    """
    Existing Project JSON should not gain a structured_prompts
    section unless explicitly enabled.
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
        "structured_prompts"
        not in data
    )

    assert "project" in data
    assert "timeline" in data
    assert "workflow" in data


def test_prompt_profile_export_does_not_force_structured_prompts():
    """
    PromptProfile resolution should remain independently
    usable without automatically enabling structured prompts.
    """

    project = make_project(
        [
            make_scene(1),
        ]
    )

    data = project_to_dict(
        project,
        prompt_profile=(
            make_base_prompt_profile()
        ),
    )

    assert (
        "prompt_profile"
        in data
    )

    assert (
        "structured_prompts"
        not in data
    )


def test_project_to_json_preserves_structured_prompts():
    """
    project_to_json should preserve per-scene structured
    prompt sections.
    """

    project = make_project(
        [
            make_scene(1),
            make_scene(2),
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
        global_constraints=(
            make_global_constraints()
        ),
        include_structured_prompts=True,
    )

    data = json.loads(
        content
    )

    assert (
        "structured_prompts"
        in data
    )

    structured = data[
        "structured_prompts"
    ]

    assert (
        structured["summary"][
            "scene_count"
        ]
        == 2
    )

    assert (
        structured["summary"][
            "valid_scene_count"
        ]
        == 2
    )

    assert (
        structured["summary"][
            "global_constraints_applied"
        ]
        is True
    )


def test_save_project_json_preserves_structured_prompts(
    tmp_path,
):
    """
    Saving and reloading Project JSON should preserve
    StructuredPromptResult data.
    """

    project = make_project(
        [
            make_scene(1),
            make_scene(2),
        ]
    )

    output_path = (
        tmp_path
        / "structured_prompts"
        / "project.json"
    )

    saved_path = save_project_json(
        project,
        output_path,
        prompt_profile=(
            make_base_prompt_profile()
        ),
        include_structured_prompts=True,
    )

    data = json.loads(
        saved_path.read_text(
            encoding="utf-8"
        )
    )

    assert (
        "structured_prompts"
        in data
    )

    assert (
        data["structured_prompts"][
            "summary"
        ][
            "scene_count"
        ]
        == 2
    )

    assert (
        len(
            data["structured_prompts"][
                "scene_results"
            ]
        )
        == 2
    )


def test_structured_prompt_export_does_not_mutate_inputs():
    """
    Structured Project export must not mutate Scene,
    PromptProfile, base profile, or GlobalConstraints.
    """

    scene = make_scene(
        1,
        negative_constraints=[
            "distorted face",
            "text artifacts",
        ],
    )

    project = make_project(
        [
            scene,
        ]
    )

    base = make_base_prompt_profile()
    child = (
        make_music_video_prompt_profile()
    )
    constraints = (
        make_global_constraints()
    )

    scene_before = scene.to_dict()
    base_before = base.to_dict()
    child_before = child.to_dict()
    constraints_before = (
        constraints.to_dict()
    )

    project_to_dict(
        project,
        prompt_profile=child,
        base_prompt_profile=base,
        global_constraints=constraints,
        prompt_enable_overrides=[
            "mood",
        ],
        prompt_config_overrides={
            "camera": {
                "include_lens": False,
            },
        },
        include_structured_prompts=True,
    )

    assert (
        scene.to_dict()
        == scene_before
    )

    assert (
        base.to_dict()
        == base_before
    )

    assert (
        child.to_dict()
        == child_before
    )

    assert (
        constraints.to_dict()
        == constraints_before
    )


def test_all_optional_project_layers_can_coexist():
    """
    Duration, Continuity, Global Constraints, PromptProfile,
    and Structured Prompts should coexist in one export.
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

    global_constraints = (
        make_global_constraints()
    )

    prompt_profile = PromptProfile(
        name="production-prompt",
        enabled_components=[
            "characters",
            "location",
            "camera",
            "performance",
            "lighting",
            "continuity",
            "global_constraints",
            "negative_constraints",
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
        include_structured_prompts=True,
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
        "structured_prompts"
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

    assert (
        data["structured_prompts"][
            "summary"
        ]["scene_count"]
        == 2
    )

    assert (
        data["structured_prompts"][
            "summary"
        ][
            "valid_scene_count"
        ]
        == 2
    )


def test_structured_prompts_preserve_existing_workflow_output():
    """
    Structured prompt export must not replace or remove
    the existing workflow output.
    """

    project = make_project(
        [
            make_scene(1),
            make_scene(2),
        ]
    )

    data = project_to_dict(
        project,
        include_structured_prompts=True,
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
