"""
Validation for public README documentation examples.

These tests verify that representative APIs documented in README.md
remain importable and executable using the current provider-neutral
toolkit architecture.
"""

from pathlib import Path

from ai_cinematic_workflow import (
    Camera,
    CinematicProject,
    ContinuityProfile,
    DurationPolicy,
    GlobalConstraints,
    MusicSection,
    MusicVideoStructure,
    PlatformAdapter,
    PlatformAdapterCapabilities,
    PlatformAdapterRegistry,
    ProjectExportOptions,
    ProjectMetadata,
    PromptProfile,
    Scene,
    assemble_structured_prompt,
    build_timeline,
    process_project,
    process_scene,
    resolve_music_video_lip_sync,
    resolve_project_constraints,
    resolve_prompt_profile,
    validate_music_video_timing,
    validate_project_continuity,
)
from ai_cinematic_workflow.exporters.project_json_exporter import (
    project_to_dict,
    save_project_json,
)


PROJECT_ROOT = Path(
    __file__
).resolve().parents[1]

README_PATH = (
    PROJECT_ROOT
    / "README.md"
)


def make_scene(
    scene_id: int,
    *,
    wardrobe: str = "black outfit",
) -> Scene:
    """Create a reusable scene matching README-style examples."""

    return Scene(
        scene_id=scene_id,
        duration_seconds=15,
        location="Performance stage",
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
        lighting=(
            "Soft cinematic lighting"
        ),
        mood="Reflective",
        continuity={
            "wardrobe": wardrobe,
            "hair": "long dark hair",
        },
        negative_constraints=[
            "Distorted Face",
            "Extra Fingers",
            "Camera Jitter",
        ],
    )


def make_project() -> CinematicProject:
    """Create a compact project for documentation validation."""

    structure = MusicVideoStructure(
        sections=[
            MusicSection(
                section_id=1,
                section_type="intro",
                start_seconds=0,
                end_seconds=15,
                performance_mode=(
                    "cinematic-only"
                ),
                scene_ids=[
                    1,
                ],
                label="Intro",
            ),
            MusicSection(
                section_id=2,
                section_type="verse",
                start_seconds=15,
                end_seconds=30,
                performance_mode="vocal",
                scene_ids=[
                    2,
                ],
                label="Verse",
            ),
            MusicSection(
                section_id=3,
                section_type="instrumental",
                start_seconds=30,
                end_seconds=45,
                performance_mode="instrumental",
                scene_ids=[
                    3,
                ],
                label="Instrumental",
            ),
        ]
    )

    return CinematicProject(
        metadata=ProjectMetadata(
            title="Documentation Demo",
            project_type="music-video",
            language="en",
            aspect_ratio="16:9",
            frame_rate=24,
        ),
        scenes=[
            make_scene(
                1
            ),
            make_scene(
                2
            ),
            make_scene(
                3,
                wardrobe="white outfit",
            ),
        ],
        music_video_structure=structure,
    )


def make_duration_policy() -> DurationPolicy:
    """Create the duration policy documented in README."""

    return DurationPolicy(
        preferred_scene_duration=15,
        minimum_scene_duration=15,
        maximum_scene_duration=15,
        allowed_scene_durations=[
            15,
        ],
        tolerance_seconds=0,
        strict=True,
    )


def make_continuity_profile() -> ContinuityProfile:
    """Create representative advanced continuity configuration."""

    return ContinuityProfile(
        name="documentation-continuity",
        required_fields=[
            "characters",
            "wardrobe",
            "hair",
        ],
        strict_fields=[
            "characters",
            "hair",
        ],
        warning_fields=[
            "wardrobe",
        ],
        strict=True,
        missing_required_severity="error",
    )


def make_global_constraints() -> GlobalConstraints:
    """Create representative README GlobalConstraints."""

    return GlobalConstraints(
        name="documentation-production",
        required_constraints=[
            "maintain cinematic realism",
        ],
        advisory_constraints=[
            "preserve natural body movement",
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


def make_prompt_profile() -> PromptProfile:
    """Create representative README PromptProfile."""

    return PromptProfile(
        name="documentation-profile",
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


def test_readme_exists():
    """The primary public documentation must exist."""

    assert README_PATH.exists()

    text = README_PATH.read_text(
        encoding="utf-8"
    )

    assert (
        "# AI Cinematic Workflow Toolkit"
        in text
    )


def test_readme_documents_current_release_status():
    """README should distinguish released v0.1.0 from v0.2 work."""

    text = README_PATH.read_text(
        encoding="utf-8"
    )

    assert (
        "Current released version:"
        in text
    )

    assert (
        "`v0.1.0`"
        in text
    )

    assert (
        "v0.2.0"
        in text
    )

    assert (
        "In Progress"
        in text
    )


def test_readme_documents_provider_boundary():
    """
    Documentation must distinguish Platform Adapter foundation
    from future provider-specific implementations.
    """

    text = README_PATH.read_text(
        encoding="utf-8"
    )

    assert (
        "# Platform Adapter Foundation"
        in text
    )

    assert (
        "# Provider Boundary"
        in text
    )

    assert (
        "Future Provider-Specific Adapters"
        in text
    )

    assert (
        "provider API keys"
        in text
    )

    assert (
        "undocumented provider parameters"
        in text
    )


def test_readme_documents_current_core_layers():
    """README should expose all major implemented v0.2 core layers."""

    text = README_PATH.read_text(
        encoding="utf-8"
    )

    required_headings = [
        "# Cinematic Timeline",
        "# Music Video Structure",
        "# Lip-Sync Policy",
        "# DurationPolicy",
        "# Advanced Continuity",
        "# GlobalConstraints",
        "# PromptProfile",
        "# Structured Prompt Sections",
        "# Enhanced Project Export",
        "# Platform Adapter Foundation",
        "# Runnable v0.2.0 Music-Video Example",
        "# Testing",
    ]

    for heading in required_headings:
        assert heading in text


def test_readme_quick_start_api_executes():
    """Representative README Scene processing should execute."""

    scene = make_scene(
        1
    )

    result = process_scene(
        scene
    )

    assert (
        result.scene_id
        == 1
    )

    assert (
        result.valid
        is True
    )

    assert result.prompt

    assert (
        result.negative_prompt
    )


def test_readme_multi_scene_workflow_executes():
    """Representative multi-scene workflow should remain valid."""

    project = make_project()

    results = process_project(
        project.scenes
    )

    assert (
        len(results)
        == 3
    )

    assert all(
        result.valid
        for result in results
    )


def test_readme_timeline_api_executes():
    """README Timeline example should remain compatible."""

    project = make_project()

    timeline = build_timeline(
        project.scenes
    )

    assert (
        len(timeline.entries)
        == 3
    )

    assert (
        timeline.entries[0].start_seconds
        == 0
    )

    assert (
        timeline.entries[-1].end_seconds
        == 45
    )


def test_readme_music_structure_and_lip_sync_execute():
    """Music-video and Lip-Sync APIs documented in README should work."""

    project = make_project()

    structure = (
        project.music_video_structure
    )

    assert structure is not None

    policies = (
        resolve_music_video_lip_sync(
            structure
        )
    )

    assert (
        len(policies)
        == 3
    )

    assert [
        policy.lip_sync_required
        for policy in policies
    ] == [
        False,
        True,
        False,
    ]


def test_readme_duration_validation_executes():
    """README DurationPolicy workflow should remain valid."""

    project = make_project()

    structure = (
        project.music_video_structure
    )

    assert structure is not None

    result = validate_music_video_timing(
        project.scenes,
        structure,
        make_duration_policy(),
    )

    assert (
        result.is_valid
        is True
    )

    assert (
        result.issue_count
        == 0
    )

    assert (
        result.cinematic_duration_seconds
        == 45
    )

    assert (
        result.music_duration_seconds
        == 45
    )


def test_readme_advanced_continuity_executes():
    """README ContinuityProfile example should remain compatible."""

    project = make_project()

    result = (
        validate_project_continuity(
            project.scenes,
            make_continuity_profile(),
        )
    )

    assert (
        result.is_valid
        is True
    )

    assert (
        result.error_count
        == 0
    )

    assert (
        result.warning_count
        == 1
    )


def test_readme_global_constraints_execute():
    """README GlobalConstraints workflow should remain compatible."""

    project = make_project()

    resolution = (
        resolve_project_constraints(
            project.scenes,
            make_global_constraints(),
        )
    )

    assert (
        resolution.scene_count
        == 3
    )

    assert (
        len(
            resolution.scene_results
        )
        == 3
    )


def test_readme_prompt_profile_and_structured_prompt_execute():
    """
    PromptProfile and Structured Prompt examples documented
    in README should remain executable.
    """

    project = make_project()

    constraints = (
        make_global_constraints()
    )

    profile = (
        make_prompt_profile()
    )

    resolved = (
        resolve_prompt_profile(
            profile
        )
    )

    structured = (
        assemble_structured_prompt(
            project.scenes[0],
            prompt_profile=resolved,
            global_constraints=constraints,
        )
    )

    assert (
        structured.is_valid
        is True
    )

    assert (
        "camera"
        in structured.included_components
    )

    assert (
        "global_constraints"
        in structured.included_components
    )

    assert (
        "negative_constraints"
        in structured.included_components
    )


def test_readme_enhanced_export_executes():
    """README Enhanced Project Export workflow should remain valid."""

    project = make_project()

    options = ProjectExportOptions(
        name="documentation-export",
        include_timeline=True,
        include_workflow=True,
        include_duration_validation=True,
        include_continuity_validation=True,
        include_global_constraints=True,
        include_prompt_profile=True,
        include_structured_prompts=True,
    )

    data = project_to_dict(
        project,
        duration_policy=(
            make_duration_policy()
        ),
        continuity_profile=(
            make_continuity_profile()
        ),
        global_constraints=(
            make_global_constraints()
        ),
        prompt_profile=(
            make_prompt_profile()
        ),
        export_options=options,
    )

    assert (
        "manifest"
        in data
    )

    assert (
        data[
            "manifest"
        ][
            "summary"
        ][
            "valid"
        ]
        is True
    )

    assert (
        data[
            "manifest"
        ][
            "export_name"
        ]
        == "documentation-export"
    )

    assert (
        "structured_prompts"
        in data
    )


def test_readme_json_persistence_executes(
    tmp_path,
):
    """README JSON persistence API should remain functional."""

    project = make_project()

    output_path = (
        tmp_path
        / "project.json"
    )

    options = ProjectExportOptions(
        name="documentation-save",
        include_structured_prompts=True,
    )

    saved = save_project_json(
        project,
        output_path,
        export_options=options,
    )

    assert (
        saved
        == output_path
    )

    assert (
        output_path.exists()
        is True
    )


def test_readme_platform_adapter_foundation_executes():
    """
    README Platform Adapter example should remain provider-neutral
    and executable through the public API.
    """

    project = make_project()

    resolved_profile = (
        resolve_prompt_profile(
            make_prompt_profile()
        )
    )

    structured = (
        assemble_structured_prompt(
            project.scenes[0],
            prompt_profile=(
                resolved_profile
            ),
            global_constraints=(
                make_global_constraints()
            ),
        )
    )

    adapter = PlatformAdapter(
        platform_id=(
            "Example Video Platform"
        ),
        display_name=(
            "Example Video Platform"
        ),
        capabilities=(
            PlatformAdapterCapabilities(
                supported_prompt_sections=[
                    "characters",
                    "location",
                    "camera",
                    "performance",
                    "lighting",
                    "negative_constraints",
                ],
            )
        ),
    )

    registry = (
        PlatformAdapterRegistry()
    )

    registry.register(
        adapter
    )

    resolved_adapter = registry.get(
        "example-video-platform"
    )

    result = (
        resolved_adapter
        .adapt_structured_prompt(
            structured
        )
    )

    assert (
        result.is_valid
        is True
    )

    assert (
        result.platform_id
        == "example_video_platform"
    )

    assert (
        "camera"
        in result.supported_features
    )

    assert (
        "global_constraints"
        in result.unsupported_features
    )


def test_documented_platform_adapter_output_has_no_provider_execution():
    """Documentation examples must not imply real provider execution."""

    adapter = PlatformAdapter(
        platform_id="Documentation Demo",
        display_name="Documentation Demo",
        capabilities=(
            PlatformAdapterCapabilities(
                supported_prompt_sections=[
                    "camera",
                ],
            )
        ),
    )

    structured = (
        assemble_structured_prompt(
            make_scene(1)
        )
    )

    data = (
        adapter
        .adapt_structured_prompt(
            structured
        )
        .to_dict()
    )

    payload = data[
        "payload"
    ]

    assert (
        "api_key"
        not in payload
    )

    assert (
        "endpoint"
        not in payload
    )

    assert (
        "wan_parameters"
        not in payload
    )

    assert (
        "veo_parameters"
        not in payload
    )

    assert (
        "kling_parameters"
        not in payload
    )
