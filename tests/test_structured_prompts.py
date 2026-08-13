import pytest

from ai_cinematic_workflow.global_constraints import (
    GlobalConstraints,
)
from ai_cinematic_workflow.prompt_profiles import (
    PromptProfile,
    PromptProfileIssue,
    ResolvedPromptProfile,
    resolve_prompt_profile,
)
from ai_cinematic_workflow.scene import (
    Camera,
    Scene,
)
from ai_cinematic_workflow.structured_prompts import (
    STRUCTURED_PROMPT_SECTION_ORDER,
    VALID_STRUCTURED_PROMPT_SECTIONS,
    OmittedPromptComponent,
    StructuredPromptResult,
    StructuredPromptSection,
    assemble_structured_prompt,
    normalize_prompt_section,
)


def make_scene(
    scene_id: int = 1,
    *,
    characters: list[str] | None = None,
    location: str = "Rooftop at night",
    shot: str = "medium shot",
    movement: str = "slow dolly in",
    lens: str = "50mm",
    performance: str = "Emotional vocal performance",
    lighting: str = "Blue cinematic night lighting",
    mood: str = "Intimate and reflective",
    dialogue_or_vocals: str = "Song lyrics",
    continuity: dict | None = None,
    negative_constraints: list[str] | None = None,
) -> Scene:
    """Create a reusable valid cinematic Scene."""

    return Scene(
        scene_id=scene_id,
        duration_seconds=15,
        location=location,
        camera=Camera(
            shot=shot,
            movement=movement,
            lens=lens,
        ),
        characters=(
            characters
            if characters is not None
            else ["Lead performer"]
        ),
        performance=performance,
        lighting=lighting,
        mood=mood,
        dialogue_or_vocals=(
            dialogue_or_vocals
        ),
        continuity=(
            continuity
            if continuity is not None
            else {
                "wardrobe": (
                    "black cinematic outfit"
                ),
                "hair": "long dark hair",
            }
        ),
        negative_constraints=(
            list(
                negative_constraints
            )
            if negative_constraints is not None
            else [
                "distorted face",
                "text artifacts",
            ]
        ),
    )


def make_resolved_profile(
    *,
    enabled: list[str],
    disabled: list[str] | None = None,
    name: str = "test-profile",
) -> ResolvedPromptProfile:
    """Create a valid resolved PromptProfile."""

    profile = PromptProfile(
        name=name,
        enabled_components=enabled,
        disabled_components=(
            disabled or []
        ),
    )

    return resolve_prompt_profile(
        profile
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
    )


def test_normalize_prompt_section():
    """Section identifiers should normalize canonically."""

    assert (
        normalize_prompt_section(
            "Dialogue Or Vocals"
        )
        == "dialogue_or_vocals"
    )

    assert (
        normalize_prompt_section(
            "negative-constraints"
        )
        == "negative_constraints"
    )

    assert (
        normalize_prompt_section(
            "  Global Constraints  "
        )
        == "global_constraints"
    )


def test_section_registry_matches_canonical_order():
    """
    Every canonical ordered section should belong
    to the structured prompt registry.
    """

    assert (
        VALID_STRUCTURED_PROMPT_SECTIONS
        == set(
            STRUCTURED_PROMPT_SECTION_ORDER
        )
    )

    assert (
        STRUCTURED_PROMPT_SECTION_ORDER
        == (
            "characters",
            "location",
            "camera",
            "performance",
            "lighting",
            "mood",
            "dialogue_or_vocals",
            "continuity",
            "global_constraints",
            "negative_constraints",
        )
    )


def test_structured_prompt_section_is_valid():
    """A valid canonical section should pass validation."""

    section = StructuredPromptSection(
        section_id="camera",
        label="Camera",
        order=3,
        content={
            "shot": "medium shot",
            "movement": "slow dolly in",
            "lens": "50mm",
        },
        metadata={
            "source": "scene",
        },
    )

    assert section.is_valid
    assert section.validate() == []
    assert section.is_empty is False


def test_unknown_section_is_invalid():
    """Unknown section identifiers should fail validation."""

    section = StructuredPromptSection(
        section_id="future-provider-section",
        label="Future",
        order=1,
        content="Example",
    )

    assert section.is_valid is False

    assert any(
        "unknown structured prompt section"
        in error
        for error in section.validate()
    )


def test_section_requires_label():
    """Structured sections require a readable label."""

    section = StructuredPromptSection(
        section_id="camera",
        label="   ",
        order=3,
        content={
            "shot": "medium shot",
        },
    )

    assert section.is_valid is False

    assert (
        "structured prompt section label "
        "cannot be empty"
        in section.validate()
    )


def test_section_order_must_be_positive():
    """Canonical section order must be positive."""

    section = StructuredPromptSection(
        section_id="camera",
        label="Camera",
        order=0,
        content={
            "shot": "medium shot",
        },
    )

    assert section.is_valid is False

    assert (
        "structured prompt section order "
        "must be greater than zero"
        in section.validate()
    )


def test_section_content_must_be_json_serializable():
    """Section content must remain portable."""

    section = StructuredPromptSection(
        section_id="camera",
        label="Camera",
        order=3,
        content={
            "invalid": {
                "set-value",
            },
        },
    )

    assert section.is_valid is False

    assert any(
        "structured prompt section content "
        "must be JSON serializable"
        in error
        for error in section.validate()
    )


def test_section_metadata_must_be_json_serializable():
    """Section metadata must also remain portable."""

    section = StructuredPromptSection(
        section_id="camera",
        label="Camera",
        order=3,
        content={
            "shot": "medium shot",
        },
        metadata={
            "invalid": {
                "set-value",
            },
        },
    )

    assert section.is_valid is False

    assert any(
        "structured prompt section metadata "
        "must be JSON serializable"
        in error
        for error in section.validate()
    )


def test_section_serialization_normalizes_identifier():
    """Serialized section IDs should use canonical form."""

    section = StructuredPromptSection(
        section_id="Dialogue Or Vocals",
        label="Dialogue or Vocals",
        order=7,
        content="Song lyrics",
        metadata={
            "source": "scene",
        },
    )

    data = section.to_dict()

    assert (
        data["section_id"]
        == "dialogue_or_vocals"
    )

    assert (
        data["label"]
        == "Dialogue or Vocals"
    )

    assert data["order"] == 7


def test_section_serialization_does_not_expose_mutable_content():
    """
    Mutating serialized section content should not mutate
    the original section data.
    """

    section = StructuredPromptSection(
        section_id="camera",
        label="Camera",
        order=3,
        content={
            "shot": "medium shot",
        },
        metadata={
            "source": "scene",
        },
    )

    data = section.to_dict()

    data["content"][
        "shot"
    ] = "changed"

    data["metadata"][
        "source"
    ] = "changed"

    assert (
        section.content["shot"]
        == "medium shot"
    )

    assert (
        section.metadata["source"]
        == "scene"
    )


def test_omitted_component_serialization():
    """Omitted component reporting should serialize."""

    item = OmittedPromptComponent(
        component="mood",
        reason="disabled_by_profile",
    )

    assert item.to_dict() == {
        "component": "mood",
        "reason": "disabled_by_profile",
    }


def test_without_profile_all_non_empty_sections_are_considered():
    """
    Without PromptProfile control, all canonical components
    should be considered active.
    """

    scene = make_scene()

    result = assemble_structured_prompt(
        scene
    )

    assert result.is_valid

    assert (
        result.included_components
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

    assert (
        result.prompt_profile_name
        is None
    )

    assert (
        "global_constraints"
        in result.omitted_component_names
    )

    global_omission = next(
        item
        for item in result.omitted_components
        if (
            item.component
            == "global_constraints"
        )
    )

    assert (
        global_omission.reason
        == "empty"
    )


def test_sections_follow_deterministic_canonical_order():
    """
    Section positions should preserve canonical order even
    when intermediate sections are omitted.
    """

    profile = make_resolved_profile(
        enabled=[
            "characters",
            "camera",
            "lighting",
            "negative_constraints",
        ],
    )

    result = assemble_structured_prompt(
        make_scene(),
        prompt_profile=profile,
    )

    assert (
        result.included_components
        == [
            "characters",
            "camera",
            "lighting",
            "negative_constraints",
        ]
    )

    assert [
        section.order
        for section in result.sections
    ] == [
        1,
        3,
        5,
        10,
    ]

    assert result.is_valid


def test_profile_controls_section_inclusion():
    """Only enabled profile components should be assembled."""

    profile = make_resolved_profile(
        enabled=[
            "characters",
            "location",
            "camera",
            "performance",
            "lighting",
            "dialogue_or_vocals",
            "negative_constraints",
        ],
        disabled=[
            "mood",
        ],
        name="music-video",
    )

    result = assemble_structured_prompt(
        make_scene(),
        prompt_profile=profile,
    )

    assert (
        result.prompt_profile_name
        == "music-video"
    )

    assert (
        result.included_components
        == [
            "characters",
            "location",
            "camera",
            "performance",
            "lighting",
            "dialogue_or_vocals",
            "negative_constraints",
        ]
    )

    assert (
        "mood"
        not in result.included_components
    )


def test_profile_disabled_component_is_reported():
    """Disabled profile sections should be auditable."""

    profile = make_resolved_profile(
        enabled=[
            "camera",
            "lighting",
        ],
        disabled=[
            "mood",
        ],
    )

    result = assemble_structured_prompt(
        make_scene(),
        prompt_profile=profile,
    )

    mood = next(
        item
        for item in result.omitted_components
        if item.component == "mood"
    )

    assert (
        mood.reason
        == "disabled_by_profile"
    )


def test_profile_not_enabled_component_is_reported():
    """
    Canonical components absent from the profile's enabled set
    should be reported separately from explicitly disabled ones.
    """

    profile = make_resolved_profile(
        enabled=[
            "camera",
        ],
    )

    result = assemble_structured_prompt(
        make_scene(),
        prompt_profile=profile,
    )

    continuity = next(
        item
        for item in result.omitted_components
        if (
            item.component
            == "continuity"
        )
    )

    assert (
        continuity.reason
        == "not_enabled_by_profile"
    )


def test_characters_section_content():
    """Character data should remain structured."""

    profile = make_resolved_profile(
        enabled=[
            "characters",
        ],
    )

    result = assemble_structured_prompt(
        make_scene(
            characters=[
                "Lead performer",
                "Guitarist",
            ]
        ),
        prompt_profile=profile,
    )

    section = result.get_section(
        "Characters"
    )

    assert section is not None

    assert (
        section.content
        == [
            "Lead performer",
            "Guitarist",
        ]
    )

    assert (
        section.metadata["source"]
        == "scene"
    )


def test_location_section_content():
    """Location should produce its own section."""

    profile = make_resolved_profile(
        enabled=[
            "location",
        ],
    )

    result = assemble_structured_prompt(
        make_scene(
            location="Rainy neon alley",
        ),
        prompt_profile=profile,
    )

    section = result.get_section(
        "location"
    )

    assert section is not None

    assert (
        section.content
        == "Rainy neon alley"
    )


def test_camera_section_is_structured():
    """
    Camera information should remain split into shot,
    movement, and lens values.
    """

    profile = make_resolved_profile(
        enabled=[
            "camera",
        ],
    )

    result = assemble_structured_prompt(
        make_scene(
            shot="close-up",
            movement="slow orbit",
            lens="85mm",
        ),
        prompt_profile=profile,
    )

    section = result.get_section(
        "camera"
    )

    assert section is not None

    assert (
        section.content
        == {
            "shot": "close-up",
            "movement": "slow orbit",
            "lens": "85mm",
        }
    )

    assert section.order == 3


def test_performance_section_content():
    """Performance should remain independently addressable."""

    profile = make_resolved_profile(
        enabled=[
            "performance",
        ],
    )

    result = assemble_structured_prompt(
        make_scene(
            performance=(
                "Natural emotional performance"
            ),
        ),
        prompt_profile=profile,
    )

    section = result.get_section(
        "performance"
    )

    assert section is not None

    assert (
        section.content
        == "Natural emotional performance"
    )


def test_lighting_section_content():
    """Lighting should produce a canonical section."""

    profile = make_resolved_profile(
        enabled=[
            "lighting",
        ],
    )

    result = assemble_structured_prompt(
        make_scene(
            lighting="Soft golden-hour light",
        ),
        prompt_profile=profile,
    )

    section = result.get_section(
        "lighting"
    )

    assert section is not None

    assert (
        section.content
        == "Soft golden-hour light"
    )


def test_mood_section_content():
    """Mood should remain separately configurable."""

    profile = make_resolved_profile(
        enabled=[
            "mood",
        ],
    )

    result = assemble_structured_prompt(
        make_scene(
            mood="Melancholic and intimate",
        ),
        prompt_profile=profile,
    )

    section = result.get_section(
        "mood"
    )

    assert section is not None

    assert (
        section.content
        == "Melancholic and intimate"
    )


def test_dialogue_or_vocals_section_content():
    """Dialogue or vocals should remain structured."""

    profile = make_resolved_profile(
        enabled=[
            "dialogue_or_vocals",
        ],
    )

    result = assemble_structured_prompt(
        make_scene(
            dialogue_or_vocals=(
                "Precise vocal performance"
            ),
        ),
        prompt_profile=profile,
    )

    section = result.get_section(
        "Dialogue Or Vocals"
    )

    assert section is not None

    assert (
        section.content
        == "Precise vocal performance"
    )

    assert section.order == 7


def test_continuity_section_content():
    """Scene continuity metadata should remain structured."""

    profile = make_resolved_profile(
        enabled=[
            "continuity",
        ],
    )

    continuity = {
        "wardrobe": "black outfit",
        "hair": "long dark hair",
        "time_of_day": "night",
    }

    result = assemble_structured_prompt(
        make_scene(
            continuity=continuity,
        ),
        prompt_profile=profile,
    )

    section = result.get_section(
        "continuity"
    )

    assert section is not None

    assert (
        section.content
        == continuity
    )


def test_scene_negative_constraints_section():
    """
    Without GlobalConstraints, negative section should use
    Scene-level negatives only.
    """

    profile = make_resolved_profile(
        enabled=[
            "negative_constraints",
        ],
    )

    result = assemble_structured_prompt(
        make_scene(
            negative_constraints=[
                "distorted face",
                "text artifacts",
            ],
        ),
        prompt_profile=profile,
    )

    section = result.get_section(
        "negative_constraints"
    )

    assert section is not None

    assert (
        section.content
        == [
            "distorted face",
            "text artifacts",
        ]
    )

    assert (
        section.metadata["source"]
        == "scene"
    )


def test_global_constraints_section_is_structured():
    """Project-wide rules should be exported as structured data."""

    profile = make_resolved_profile(
        enabled=[
            "global_constraints",
        ],
    )

    constraints = (
        make_global_constraints()
    )

    result = assemble_structured_prompt(
        make_scene(),
        prompt_profile=profile,
        global_constraints=constraints,
    )

    section = result.get_section(
        "global_constraints"
    )

    assert section is not None

    assert (
        section.content["name"]
        == "cinematic-production"
    )

    assert (
        section.content[
            "required_constraints"
        ]
        == [
            "maintain cinematic realism",
        ]
    )

    assert (
        section.content[
            "character_identity_constraints"
        ]
        == [
            "preserve lead performer identity",
        ]
    )

    assert (
        section.metadata["source"]
        == "global_constraints"
    )


def test_global_constraints_resolve_negative_section():
    """
    Global negatives, prohibited elements, and Scene negatives
    should become one deduplicated structured section.
    """

    profile = make_resolved_profile(
        enabled=[
            "negative_constraints",
        ],
    )

    constraints = (
        make_global_constraints()
    )

    scene = make_scene(
        negative_constraints=[
            "distorted face",
            "text artifacts",
        ],
    )

    result = assemble_structured_prompt(
        scene,
        prompt_profile=profile,
        global_constraints=constraints,
    )

    section = result.get_section(
        "negative_constraints"
    )

    assert section is not None

    assert (
        section.content
        == [
            "distorted face",
            "extra fingers",
            "duplicate limbs",
            "text artifacts",
        ]
    )

    assert (
        section.metadata["source"]
        == "resolved_scene_constraints"
    )


def test_empty_active_section_is_omitted_by_default():
    """
    Active optional sections with empty content should
    be omitted unless explicitly preserved.
    """

    profile = make_resolved_profile(
        enabled=[
            "dialogue_or_vocals",
        ],
    )

    result = assemble_structured_prompt(
        make_scene(
            dialogue_or_vocals="",
        ),
        prompt_profile=profile,
    )

    assert (
        result.get_section(
            "dialogue_or_vocals"
        )
        is None
    )

    omission = next(
        item
        for item in result.omitted_components
        if (
            item.component
            == "dialogue_or_vocals"
        )
    )

    assert omission.reason == "empty"


def test_empty_active_section_can_be_preserved():
    """
    include_empty_sections=True should preserve empty
    structured sections.
    """

    profile = make_resolved_profile(
        enabled=[
            "dialogue_or_vocals",
        ],
    )

    result = assemble_structured_prompt(
        make_scene(
            dialogue_or_vocals="",
        ),
        prompt_profile=profile,
        include_empty_sections=True,
    )

    section = result.get_section(
        "dialogue_or_vocals"
    )

    assert section is not None
    assert section.is_empty

    assert (
        section.metadata["empty"]
        is True
    )

    assert (
        result.include_empty_sections
        is True
    )


def test_empty_global_constraints_are_omitted():
    """
    A default GlobalConstraints profile should not create
    a meaningless Global Constraints section.
    """

    profile = make_resolved_profile(
        enabled=[
            "global_constraints",
        ],
    )

    result = assemble_structured_prompt(
        make_scene(),
        prompt_profile=profile,
        global_constraints=(
            GlobalConstraints()
        ),
    )

    assert (
        result.get_section(
            "global_constraints"
        )
        is None
    )

    omission = next(
        item
        for item in result.omitted_components
        if (
            item.component
            == "global_constraints"
        )
    )

    assert omission.reason == "empty"


def test_section_metadata_reports_component_and_profile_control():
    """Every assembled section should carry core metadata."""

    profile = make_resolved_profile(
        enabled=[
            "camera",
        ],
    )

    result = assemble_structured_prompt(
        make_scene(),
        prompt_profile=profile,
    )

    section = result.get_section(
        "camera"
    )

    assert section is not None

    assert (
        section.metadata["component"]
        == "camera"
    )

    assert (
        section.metadata["source"]
        == "scene"
    )

    assert (
        section.metadata["empty"]
        is False
    )

    assert (
        section.metadata[
            "profile_controlled"
        ]
        is True
    )


def test_without_profile_metadata_reports_not_profile_controlled():
    """Default assembly should record its non-profile origin."""

    result = assemble_structured_prompt(
        make_scene()
    )

    camera = result.get_section(
        "camera"
    )

    assert camera is not None

    assert (
        camera.metadata[
            "profile_controlled"
        ]
        is False
    )


def test_permissive_unknown_profile_component_is_reported():
    """
    Extension components accepted by a permissive PromptProfile
    should be reported as unsupported by the current core
    structured prompt assembler.
    """

    source = PromptProfile(
        name="extension-profile",
        enabled_components=[
            "camera",
            "future_platform_component",
        ],
        strict_unknown_components=False,
    )

    resolved = resolve_prompt_profile(
        source
    )

    result = assemble_structured_prompt(
        make_scene(),
        prompt_profile=resolved,
    )

    assert (
        "camera"
        in result.included_components
    )

    extension = next(
        item
        for item in result.omitted_components
        if (
            item.component
            == "future_platform_component"
        )
    )

    assert (
        extension.reason
        == "unsupported_component"
    )


def test_get_section_normalizes_lookup_name():
    """Section lookup should accept human-formatted names."""

    profile = make_resolved_profile(
        enabled=[
            "negative_constraints",
        ],
    )

    result = assemble_structured_prompt(
        make_scene(),
        prompt_profile=profile,
    )

    assert (
        result.get_section(
            "Negative Constraints"
        )
        is not None
    )

    assert (
        result.get_section(
            "negative-constraints"
        )
        is not None
    )


def test_structured_result_serialization():
    """Complete structured prompt output should serialize."""

    profile = make_resolved_profile(
        enabled=[
            "characters",
            "camera",
            "lighting",
        ],
        disabled=[
            "mood",
        ],
        name="cinematic-profile",
    )

    result = assemble_structured_prompt(
        make_scene(),
        prompt_profile=profile,
    )

    data = result.to_dict()

    assert (
        data["summary"]["valid"]
        is True
    )

    assert (
        data["summary"]["scene_id"]
        == 1
    )

    assert (
        data["summary"]["section_count"]
        == 3
    )

    assert (
        data["prompt_profile_name"]
        == "cinematic-profile"
    )

    assert (
        data["included_components"]
        == [
            "characters",
            "camera",
            "lighting",
        ]
    )

    assert (
        len(data["sections"])
        == 3
    )

    assert (
        data["sections"][1][
            "section_id"
        ]
        == "camera"
    )


def test_result_rejects_duplicate_section_ids():
    """Structured results cannot contain duplicate sections."""

    sections = [
        StructuredPromptSection(
            section_id="camera",
            label="Camera",
            order=3,
            content={
                "shot": "medium shot",
            },
        ),
        StructuredPromptSection(
            section_id="camera",
            label="Camera",
            order=3,
            content={
                "shot": "close-up",
            },
        ),
    ]

    result = StructuredPromptResult(
        scene_id=1,
        sections=sections,
    )

    assert result.is_valid is False

    assert (
        "structured prompt result cannot "
        "contain duplicate section IDs"
        in result.validate()
    )


def test_result_rejects_non_deterministic_order():
    """Structured result ordering must remain deterministic."""

    sections = [
        StructuredPromptSection(
            section_id="camera",
            label="Camera",
            order=3,
            content={
                "shot": "medium shot",
            },
        ),
        StructuredPromptSection(
            section_id="location",
            label="Location",
            order=2,
            content="Rooftop",
        ),
    ]

    result = StructuredPromptResult(
        scene_id=1,
        sections=sections,
    )

    assert result.is_valid is False

    assert (
        "structured prompt sections must use "
        "deterministic canonical ordering"
        in result.validate()
    )


def test_assembly_does_not_mutate_scene():
    """Structured prompt assembly must not mutate Scene."""

    scene = make_scene(
        negative_constraints=[
            "distorted face",
            "text artifacts",
        ],
    )

    before = scene.to_dict()

    assemble_structured_prompt(
        scene,
        global_constraints=(
            make_global_constraints()
        ),
    )

    assert (
        scene.to_dict()
        == before
    )


def test_assembly_does_not_mutate_resolved_profile():
    """
    Structured assembly must not modify the resolved
    PromptProfile input.
    """

    profile = make_resolved_profile(
        enabled=[
            "camera",
            "lighting",
            "negative_constraints",
        ],
        disabled=[
            "mood",
        ],
    )

    before = profile.to_dict()

    assemble_structured_prompt(
        make_scene(),
        prompt_profile=profile,
    )

    assert (
        profile.to_dict()
        == before
    )


def test_assembly_does_not_mutate_global_constraints():
    """
    Structured assembly must not mutate project-wide
    GlobalConstraints.
    """

    constraints = (
        make_global_constraints()
    )

    before = constraints.to_dict()

    assemble_structured_prompt(
        make_scene(),
        global_constraints=constraints,
    )

    assert (
        constraints.to_dict()
        == before
    )


def test_invalid_scene_is_rejected():
    """Assembler should reject invalid Scene data."""

    scene = make_scene()

    scene.duration_seconds = 0

    with pytest.raises(
        ValueError,
        match="Invalid scene 1",
    ):
        assemble_structured_prompt(
            scene
        )


def test_invalid_global_constraints_are_rejected():
    """Assembler should reject invalid project constraints."""

    constraints = GlobalConstraints(
        name="   ",
    )

    with pytest.raises(
        ValueError,
        match="Invalid global constraints",
    ):
        assemble_structured_prompt(
            make_scene(),
            global_constraints=constraints,
        )


def test_invalid_resolved_prompt_profile_is_rejected():
    """
    Error-level ResolvedPromptProfile issues should prevent
    structured prompt assembly.
    """

    invalid_profile = ResolvedPromptProfile(
        name="invalid-profile",
        source_profile_name=(
            "invalid-profile"
        ),
        base_profile_name=None,
        enabled_components=[
            "camera",
        ],
        disabled_components=[],
        strict_unknown_components=True,
        issues=[
            PromptProfileIssue(
                issue_type="example_error",
                severity="error",
                message="Example error",
                component="camera",
                profile_name=(
                    "invalid-profile"
                ),
            ),
        ],
    )

    with pytest.raises(
        ValueError,
        match=(
            "Invalid resolved prompt profile"
        ),
    ):
        assemble_structured_prompt(
            make_scene(),
            prompt_profile=(
                invalid_profile
            ),
        )
