import json

import pytest

from ai_cinematic_workflow import (
    Camera,
    CinematicProject,
    GlobalConstraints,
    PlatformAdapter,
    PlatformAdapterCapabilities,
    PlatformAdapterRegistry,
    ProjectExportOptions,
    ProjectMetadata,
    PromptProfile,
    Scene,
    assemble_structured_prompt,
    resolve_prompt_profile,
)
from ai_cinematic_workflow.exporters.project_json_exporter import (
    project_to_dict,
)


def make_scene(
    scene_id: int,
    *,
    location: str = "Rooftop at night",
    lighting: str = "Blue cinematic night lighting",
    dialogue_or_vocals: str = "Song lyrics",
    negative_constraints: list[str] | None = None,
) -> Scene:
    """Create a reusable valid cinematic Scene."""

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
            "Natural emotional performance"
        ),
        lighting=lighting,
        mood=(
            "Intimate and reflective"
        ),
        dialogue_or_vocals=(
            dialogue_or_vocals
        ),
        continuity={
            "wardrobe": (
                "black cinematic outfit"
            ),
            "hair": (
                "long dark hair"
            ),
        },
        negative_constraints=list(
            negative_constraints
            or [
                "text artifacts",
            ]
        ),
    )


def make_project() -> CinematicProject:
    """Create a reusable multi-scene cinematic project."""

    return CinematicProject(
        metadata=ProjectMetadata(
            title=(
                "Platform Adapter Integration Test"
            ),
            project_type="cinematic",
        ),
        scenes=[
            make_scene(
                1,
                location="Rooftop at night",
            ),
            make_scene(
                2,
                location="Neon city street",
                lighting=(
                    "Soft neon street lighting"
                ),
            ),
            make_scene(
                3,
                location="Empty theater stage",
                lighting=(
                    "Warm cinematic spotlight"
                ),
            ),
        ],
    )


def make_global_constraints() -> GlobalConstraints:
    """Create reusable project-wide constraints."""

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


def make_full_prompt_profile() -> PromptProfile:
    """Create a reusable cinematic prompt profile."""

    return PromptProfile(
        name="adapter-production",
        enabled_components=[
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
        ],
    )


def make_adapter(
    *,
    platform_id: str = "Example Video Platform",
    display_name: str = "Example Video Platform",
    supported_sections: list[str] | None = None,
    supports_structured_prompt_input: bool = True,
    supports_section_metadata: bool = True,
) -> PlatformAdapter:
    """Create a reusable provider-neutral adapter."""

    return PlatformAdapter(
        platform_id=platform_id,
        display_name=display_name,
        adapter_version="1.0",
        capabilities=(
            PlatformAdapterCapabilities(
                supported_prompt_sections=(
                    supported_sections
                    if supported_sections is not None
                    else [
                        "characters",
                        "location",
                        "camera",
                        "performance",
                        "lighting",
                        "negative_constraints",
                    ]
                ),
                supports_structured_prompt_input=(
                    supports_structured_prompt_input
                ),
                supports_section_metadata=(
                    supports_section_metadata
                ),
            )
        ),
        metadata={
            "category": "video_generation",
        },
    )


def test_project_scenes_can_be_adapted_independently():
    """
    Every Scene in a CinematicProject should be convertible into
    a StructuredPromptResult and then independently adapted.
    """

    project = make_project()

    adapter = make_adapter(
        supported_sections=[
            "characters",
            "location",
            "camera",
            "lighting",
            "negative_constraints",
        ],
    )

    results = [
        adapter.adapt_structured_prompt(
            assemble_structured_prompt(
                scene
            )
        )
        for scene in project.scenes
    ]

    assert (
        len(results)
        == 3
    )

    assert [
        result.payload["scene_id"]
        for result in results
    ] == [
        1,
        2,
        3,
    ]

    assert all(
        result.is_valid
        for result in results
    )


def test_registry_can_drive_multi_scene_project_adaptation():
    """
    A registered adapter should be resolvable once and reused
    consistently across a complete project.
    """

    project = make_project()

    registry = (
        PlatformAdapterRegistry()
    )

    adapter = make_adapter(
        platform_id=(
            "Example Video Platform"
        ),
    )

    registry.register(
        adapter
    )

    resolved = registry.get(
        "example-video-platform"
    )

    results = [
        resolved.adapt_structured_prompt(
            assemble_structured_prompt(
                scene
            )
        )
        for scene in project.scenes
    ]

    assert (
        resolved is adapter
    )

    assert (
        len(results)
        == len(
            project.scenes
        )
    )

    assert all(
        result.platform_id
        == "example_video_platform"
        for result in results
    )


def test_capability_filtering_is_consistent_across_project():
    """
    The same capability declaration should produce the same
    supported-section policy across all project scenes.
    """

    project = make_project()

    adapter = make_adapter(
        supported_sections=[
            "camera",
            "lighting",
            "negative_constraints",
        ],
    )

    results = [
        adapter.adapt_structured_prompt(
            assemble_structured_prompt(
                scene
            )
        )
        for scene in project.scenes
    ]

    assert all(
        result.supported_features
        == [
            "camera",
            "lighting",
            "negative_constraints",
        ]
        for result in results
    )

    assert all(
        "continuity"
        in result.unsupported_features
        for result in results
    )


def test_unsupported_sections_are_reported_for_each_scene():
    """
    Unsupported project-scene sections should generate auditable
    warnings rather than disappearing silently.
    """

    project = make_project()

    adapter = make_adapter(
        supported_sections=[
            "camera",
        ],
    )

    results = [
        adapter.adapt_structured_prompt(
            assemble_structured_prompt(
                scene
            )
        )
        for scene in project.scenes
    ]

    for result in results:
        assert (
            result.warning_count
            > 0
        )

        assert (
            result.error_count
            == 0
        )

        assert any(
            issue.issue_type
            == "unsupported_prompt_section"
            for issue in result.issues
        )


def test_prompt_profile_controls_sections_before_platform_adaptation():
    """
    PromptProfile should determine Structured Prompt content before
    PlatformAdapter capability filtering is applied.
    """

    project = make_project()

    profile = PromptProfile(
        name="camera-only",
        enabled_components=[
            "camera",
        ],
    )

    resolved_profile = (
        resolve_prompt_profile(
            profile
        )
    )

    adapter = make_adapter(
        supported_sections=[
            "camera",
            "lighting",
        ],
    )

    results = [
        adapter.adapt_structured_prompt(
            assemble_structured_prompt(
                scene,
                prompt_profile=(
                    resolved_profile
                ),
            )
        )
        for scene in project.scenes
    ]

    for result in results:
        assert (
            result.supported_features
            == [
                "camera",
            ]
        )

        assert (
            result.unsupported_features
            == []
        )

        assert [
            section["section_id"]
            for section in result.payload[
                "sections"
            ]
        ] == [
            "camera",
        ]


def test_global_constraints_resolve_before_adapter_filtering():
    """
    GlobalConstraints should be resolved by the Structured Prompt
    layer before PlatformAdapter capability filtering.
    """

    scene = make_scene(
        1,
        negative_constraints=[
            "distorted face",
            "text artifacts",
        ],
    )

    constraints = (
        make_global_constraints()
    )

    profile = PromptProfile(
        name="global-aware",
        enabled_components=[
            "global_constraints",
            "negative_constraints",
        ],
    )

    resolved_profile = (
        resolve_prompt_profile(
            profile
        )
    )

    source = assemble_structured_prompt(
        scene,
        prompt_profile=(
            resolved_profile
        ),
        global_constraints=constraints,
    )

    adapter = make_adapter(
        supported_sections=[
            "negative_constraints",
        ],
    )

    result = (
        adapter.adapt_structured_prompt(
            source
        )
    )

    assert (
        result.supported_features
        == [
            "negative_constraints",
        ]
    )

    assert (
        result.unsupported_features
        == [
            "global_constraints",
        ]
    )

    negative_section = (
        result.payload[
            "sections"
        ][0]
    )

    assert (
        negative_section["section_id"]
        == "negative_constraints"
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


def test_global_constraints_unsupported_section_creates_warning():
    """Unsupported global constraint sections should remain auditable."""

    constraints = (
        make_global_constraints()
    )

    profile = PromptProfile(
        name="global-aware",
        enabled_components=[
            "global_constraints",
        ],
    )

    source = assemble_structured_prompt(
        make_scene(1),
        prompt_profile=(
            resolve_prompt_profile(
                profile
            )
        ),
        global_constraints=constraints,
    )

    adapter = make_adapter(
        supported_sections=[
            "camera",
        ],
    )

    result = (
        adapter.adapt_structured_prompt(
            source
        )
    )

    global_issue = next(
        issue
        for issue in result.issues
        if (
            issue.section_id
            == "global_constraints"
        )
    )

    assert (
        global_issue.severity
        == "warning"
    )

    assert (
        global_issue.issue_type
        == "unsupported_prompt_section"
    )


def test_adapter_without_structured_input_support_returns_error_per_scene():
    """
    A project flow targeting an adapter that rejects structured
    input should receive explicit error-level results.
    """

    project = make_project()

    adapter = make_adapter(
        supports_structured_prompt_input=False,
    )

    results = [
        adapter.adapt_structured_prompt(
            assemble_structured_prompt(
                scene
            )
        )
        for scene in project.scenes
    ]

    assert all(
        result.is_valid is False
        for result in results
    )

    assert all(
        result.error_count
        == 1
        for result in results
    )

    assert all(
        result.unsupported_features
        == [
            "structured_prompt_input",
        ]
        for result in results
    )


def test_multiple_registered_adapters_produce_independent_results():
    """
    Different adapters should transform the same source according
    to their own capability declarations.
    """

    registry = (
        PlatformAdapterRegistry()
    )

    camera_adapter = make_adapter(
        platform_id="Camera Platform",
        display_name="Camera Platform",
        supported_sections=[
            "camera",
        ],
    )

    lighting_adapter = make_adapter(
        platform_id="Lighting Platform",
        display_name="Lighting Platform",
        supported_sections=[
            "lighting",
        ],
    )

    registry.register(
        camera_adapter
    )

    registry.register(
        lighting_adapter
    )

    source = assemble_structured_prompt(
        make_scene(1)
    )

    camera_result = registry.get(
        "camera-platform"
    ).adapt_structured_prompt(
        source
    )

    lighting_result = registry.get(
        "lighting-platform"
    ).adapt_structured_prompt(
        source
    )

    assert [
        section["section_id"]
        for section in camera_result.payload[
            "sections"
        ]
    ] == [
        "camera",
    ]

    assert [
        section["section_id"]
        for section in lighting_result.payload[
            "sections"
        ]
    ] == [
        "lighting",
    ]

    assert (
        camera_result.platform_id
        == "camera_platform"
    )

    assert (
        lighting_result.platform_id
        == "lighting_platform"
    )


def test_unknown_registry_platform_fails_in_project_flow():
    """Project adaptation should fail explicitly for unknown adapters."""

    registry = (
        PlatformAdapterRegistry()
    )

    with pytest.raises(
        KeyError,
        match=(
            "Unknown platform adapter"
        ),
    ):
        registry.get(
            "missing-video-platform"
        )


def test_project_adaptation_does_not_mutate_project_or_sources():
    """
    Running platform adaptation across a project must not mutate
    CinematicProject or StructuredPromptResult inputs.
    """

    project = make_project()

    project_before = (
        project.to_dict()
    )

    sources = [
        assemble_structured_prompt(
            scene
        )
        for scene in project.scenes
    ]

    source_before = [
        source.to_dict()
        for source in sources
    ]

    adapter = make_adapter(
        supported_sections=[
            "camera",
            "lighting",
        ],
        supports_section_metadata=False,
    )

    results = [
        adapter.adapt_structured_prompt(
            source
        )
        for source in sources
    ]

    assert (
        project.to_dict()
        == project_before
    )

    assert [
        source.to_dict()
        for source in sources
    ] == source_before

    assert (
        len(results)
        == 3
    )


def test_enhanced_export_and_platform_adaptation_can_coexist():
    """
    Enhanced Project Export and PlatformAdapter results should
    coexist without merging provider behavior into core export.
    """

    project = make_project()

    constraints = (
        make_global_constraints()
    )

    profile = (
        make_full_prompt_profile()
    )

    options = ProjectExportOptions(
        name="adapter-ready-project",
        include_global_constraints=True,
        include_prompt_profile=True,
        include_structured_prompts=True,
    )

    export_data = project_to_dict(
        project,
        global_constraints=constraints,
        prompt_profile=profile,
        export_options=options,
    )

    resolved_profile = (
        resolve_prompt_profile(
            profile
        )
    )

    adapter = make_adapter(
        supported_sections=[
            "characters",
            "location",
            "camera",
            "lighting",
            "negative_constraints",
        ],
    )

    adapter_results = [
        adapter.adapt_structured_prompt(
            assemble_structured_prompt(
                scene,
                prompt_profile=(
                    resolved_profile
                ),
                global_constraints=(
                    constraints
                ),
            )
        )
        for scene in project.scenes
    ]

    assert (
        "manifest"
        in export_data
    )

    assert (
        "structured_prompts"
        in export_data
    )

    assert (
        len(adapter_results)
        == export_data[
            "structured_prompts"
        ][
            "summary"
        ][
            "scene_count"
        ]
    )

    assert all(
        result.is_valid
        for result in adapter_results
    )


def test_enhanced_export_remains_provider_neutral_after_adaptation():
    """
    Executing PlatformAdapter logic must not add provider payloads
    to Enhanced Project Export data.
    """

    project = make_project()

    options = ProjectExportOptions(
        name="provider-neutral",
        include_structured_prompts=True,
    )

    before = project_to_dict(
        project,
        export_options=options,
    )

    adapter = make_adapter(
        platform_id="Example Provider",
        display_name="Example Provider",
        supported_sections=[
            "camera",
        ],
    )

    for scene in project.scenes:
        source = (
            assemble_structured_prompt(
                scene
            )
        )

        adapter.adapt_structured_prompt(
            source
        )

    after = project_to_dict(
        project,
        export_options=options,
    )

    assert (
        after
        == before
    )

    assert "wan_payload" not in after
    assert "veo_payload" not in after
    assert "kling_payload" not in after

    assert (
        "example_provider"
        not in after
    )


def test_platform_adapter_results_are_json_serializable_across_project():
    """
    Adapter results from an entire project should remain portable
    and JSON serializable.
    """

    project = make_project()

    adapter = make_adapter(
        supported_sections=[
            "characters",
            "camera",
            "lighting",
            "negative_constraints",
        ],
    )

    results = [
        adapter.adapt_structured_prompt(
            assemble_structured_prompt(
                scene
            )
        ).to_dict()
        for scene in project.scenes
    ]

    encoded = json.dumps(
        {
            "platform": (
                adapter.canonical_platform_id
            ),
            "scene_results": results,
        },
        ensure_ascii=False,
    )

    decoded = json.loads(
        encoded
    )

    assert (
        decoded["platform"]
        == "example_video_platform"
    )

    assert (
        len(
            decoded["scene_results"]
        )
        == 3
    )

    assert [
        result["payload"][
            "scene_id"
        ]
        for result in decoded[
            "scene_results"
        ]
    ] == [
        1,
        2,
        3,
    ]


def test_adapter_registry_and_enhanced_export_remain_separate_layers():
    """
    Adapter registry metadata should not be injected automatically
    into Enhanced Project Export.
    """

    registry = (
        PlatformAdapterRegistry()
    )

    registry.register(
        make_adapter(
            platform_id="Alpha Platform",
            display_name="Alpha Platform",
        )
    )

    registry.register(
        make_adapter(
            platform_id="Beta Platform",
            display_name="Beta Platform",
        )
    )

    data = project_to_dict(
        make_project(),
        export_options=(
            ProjectExportOptions(
                name="clean-export",
                include_structured_prompts=True,
            )
        ),
    )

    assert (
        registry.platform_ids
        == [
            "alpha_platform",
            "beta_platform",
        ]
    )

    assert (
        "platform_adapters"
        not in data
    )

    assert (
        "adapter_registry"
        not in data
    )


def test_platform_foundation_does_not_assume_real_provider_parameters():
    """
    Integration output should remain generic until documented
    provider-specific adapters are implemented.
    """

    source = (
        assemble_structured_prompt(
            make_scene(1)
        )
    )

    adapter = make_adapter(
        platform_id="Example Provider",
        display_name="Example Provider",
        supported_sections=[
            "camera",
            "lighting",
        ],
    )

    result = (
        adapter.adapt_structured_prompt(
            source
        ).to_dict()
    )

    payload = result[
        "payload"
    ]

    assert (
        payload["mode"]
        == "structured_prompt_adapter"
    )

    assert "api_key" not in payload
    assert "endpoint" not in payload
    assert "model_id" not in payload
    assert "wan_parameters" not in payload
    assert "veo_parameters" not in payload
    assert "kling_parameters" not in payload
