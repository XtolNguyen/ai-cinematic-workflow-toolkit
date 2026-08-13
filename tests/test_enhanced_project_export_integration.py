import json

import pytest

from ai_cinematic_workflow import (
    Camera,
    CinematicProject,
    ContinuityProfile,
    DurationPolicy,
    GlobalConstraints,
    ProjectExportOptions,
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
        lighting=(
            "Blue cinematic night lighting"
        ),
        mood=(
            "Intimate and reflective"
        ),
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


def make_project() -> CinematicProject:
    """Create a reusable two-scene cinematic project."""

    return CinematicProject(
        metadata=ProjectMetadata(
            title="Enhanced Export Test",
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
            ),
        ],
    )


def make_duration_policy() -> DurationPolicy:
    """Create a strict reusable duration policy."""

    return DurationPolicy(
        preferred_scene_duration=15,
        allowed_scene_durations=[
            15,
        ],
        strict=True,
    )


def make_continuity_profile() -> ContinuityProfile:
    """Create reusable advanced continuity rules."""

    return ContinuityProfile(
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


def make_global_constraints() -> GlobalConstraints:
    """Create reusable project-wide cinematic rules."""

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


def make_prompt_profile() -> PromptProfile:
    """Create a reusable structured-prompt profile."""

    return PromptProfile(
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


def test_legacy_export_has_no_manifest():
    """
    Existing calls without ProjectExportOptions must preserve
    legacy export behavior.
    """

    data = project_to_dict(
        make_project()
    )

    assert "manifest" not in data

    assert (
        list(data.keys())
        == [
            "project",
            "timeline",
            "workflow",
        ]
    )


def test_legacy_optional_layers_remain_backward_compatible():
    """
    Existing optional arguments should continue exporting their
    layers without requiring ProjectExportOptions.
    """

    data = project_to_dict(
        make_project(),
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
        include_structured_prompts=True,
    )

    assert "manifest" not in data

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


def test_minimal_enhanced_export():
    """
    Enhanced options should allow a project-only export.
    """

    options = ProjectExportOptions(
        name="minimal",
        include_timeline=False,
        include_workflow=False,
    )

    data = project_to_dict(
        make_project(),
        export_options=options,
    )

    assert (
        list(data.keys())
        == [
            "manifest",
            "project",
        ]
    )

    manifest = data["manifest"]

    assert (
        manifest["export_name"]
        == "minimal"
    )

    assert (
        manifest["included_sections"]
        == [
            "project",
        ]
    )

    reasons = {
        item["section_id"]: item["reason"]
        for item in manifest[
            "omitted_sections"
        ]
    }

    assert (
        reasons["timeline"]
        == "disabled_by_export_options"
    )

    assert (
        reasons["workflow"]
        == "disabled_by_export_options"
    )


def test_default_enhanced_export_preserves_core_layers():
    """
    Default ProjectExportOptions should include project,
    timeline, and workflow plus a manifest.
    """

    options = ProjectExportOptions(
        name="default-enhanced",
    )

    data = project_to_dict(
        make_project(),
        export_options=options,
    )

    assert "manifest" in data
    assert "project" in data
    assert "timeline" in data
    assert "workflow" in data

    assert (
        data["manifest"][
            "included_sections"
        ]
        == [
            "project",
            "timeline",
            "workflow",
        ]
    )


def test_requested_duration_without_policy_is_reported():
    """
    A requested validation layer without its required source
    should be omitted with an explicit reason.
    """

    options = ProjectExportOptions(
        name="duration-request",
        include_duration_validation=True,
    )

    data = project_to_dict(
        make_project(),
        export_options=options,
    )

    assert (
        "duration_validation"
        not in data
    )

    reasons = {
        item["section_id"]: item["reason"]
        for item in data[
            "manifest"
        ][
            "omitted_sections"
        ]
    }

    assert (
        reasons["duration_validation"]
        == "missing_duration_policy"
    )


def test_requested_continuity_without_profile_is_reported():
    """Missing ContinuityProfile should be auditable."""

    options = ProjectExportOptions(
        name="continuity-request",
        include_continuity_validation=True,
    )

    data = project_to_dict(
        make_project(),
        export_options=options,
    )

    assert (
        "continuity_validation"
        not in data
    )

    reasons = {
        item["section_id"]: item["reason"]
        for item in data[
            "manifest"
        ][
            "omitted_sections"
        ]
    }

    assert (
        reasons["continuity_validation"]
        == "missing_continuity_profile"
    )


def test_requested_global_constraints_without_source_are_reported():
    """Missing GlobalConstraints should be auditable."""

    options = ProjectExportOptions(
        name="global-request",
        include_global_constraints=True,
    )

    data = project_to_dict(
        make_project(),
        export_options=options,
    )

    assert (
        "global_constraints"
        not in data
    )

    reasons = {
        item["section_id"]: item["reason"]
        for item in data[
            "manifest"
        ][
            "omitted_sections"
        ]
    }

    assert (
        reasons["global_constraints"]
        == "missing_global_constraints"
    )


def test_requested_prompt_profile_without_source_is_reported():
    """Missing PromptProfile should be auditable."""

    options = ProjectExportOptions(
        name="prompt-request",
        include_prompt_profile=True,
    )

    data = project_to_dict(
        make_project(),
        export_options=options,
    )

    assert (
        "prompt_profile"
        not in data
    )

    reasons = {
        item["section_id"]: item["reason"]
        for item in data[
            "manifest"
        ][
            "omitted_sections"
        ]
    }

    assert (
        reasons["prompt_profile"]
        == "missing_prompt_profile"
    )


def test_duration_layer_is_included_when_requested_and_available():
    """Requested DurationPolicy should produce its layer."""

    options = ProjectExportOptions(
        name="duration-export",
        include_duration_validation=True,
    )

    data = project_to_dict(
        make_project(),
        duration_policy=(
            make_duration_policy()
        ),
        export_options=options,
    )

    assert (
        "duration_validation"
        in data
    )

    assert (
        "duration_validation"
        in data["manifest"][
            "included_sections"
        ]
    )

    assert (
        data["duration_validation"][
            "summary"
        ]["valid"]
        is True
    )


def test_continuity_layer_is_included_when_requested_and_available():
    """Requested ContinuityProfile should produce its layer."""

    options = ProjectExportOptions(
        name="continuity-export",
        include_continuity_validation=True,
    )

    data = project_to_dict(
        make_project(),
        continuity_profile=(
            make_continuity_profile()
        ),
        export_options=options,
    )

    assert (
        "continuity_validation"
        in data
    )

    assert (
        "continuity_validation"
        in data["manifest"][
            "included_sections"
        ]
    )


def test_global_constraints_can_be_used_without_top_level_export():
    """
    GlobalConstraints may be used internally by Structured Prompts
    while their own top-level section remains disabled.
    """

    options = ProjectExportOptions(
        name="structured-only-global",
        include_global_constraints=False,
        include_structured_prompts=True,
    )

    data = project_to_dict(
        make_project(),
        global_constraints=(
            make_global_constraints()
        ),
        prompt_profile=(
            make_prompt_profile()
        ),
        export_options=options,
    )

    assert (
        "global_constraints"
        not in data
    )

    assert (
        "structured_prompts"
        in data
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

    reasons = {
        item["section_id"]: item["reason"]
        for item in data[
            "manifest"
        ][
            "omitted_sections"
        ]
    }

    assert (
        reasons["global_constraints"]
        == "disabled_by_export_options"
    )


def test_prompt_profile_can_be_used_without_top_level_export():
    """
    PromptProfile may control Structured Prompt Sections even when
    the prompt_profile top-level export section is disabled.
    """

    profile = PromptProfile(
        name="camera-only",
        enabled_components=[
            "camera",
        ],
    )

    options = ProjectExportOptions(
        name="structured-only-profile",
        include_prompt_profile=False,
        include_structured_prompts=True,
    )

    data = project_to_dict(
        make_project(),
        prompt_profile=profile,
        export_options=options,
    )

    assert (
        "prompt_profile"
        not in data
    )

    assert (
        "structured_prompts"
        in data
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
            "camera",
        ]
    )

    reasons = {
        item["section_id"]: item["reason"]
        for item in data[
            "manifest"
        ][
            "omitted_sections"
        ]
    }

    assert (
        reasons["prompt_profile"]
        == "disabled_by_export_options"
    )


def test_structured_prompts_can_be_enabled_without_prompt_profile():
    """
    Structured Prompt Sections do not require PromptProfile;
    all canonical non-empty scene sections may be assembled.
    """

    options = ProjectExportOptions(
        name="structured-default",
        include_structured_prompts=True,
    )

    data = project_to_dict(
        make_project(),
        export_options=options,
    )

    assert (
        "structured_prompts"
        in data
    )

    assert (
        data["structured_prompts"][
            "summary"
        ][
            "prompt_profile_name"
        ]
        is None
    )

    assert (
        "structured_prompts"
        in data["manifest"][
            "included_sections"
        ]
    )


def test_empty_prompt_sections_are_controlled_by_options():
    """Enhanced options should control empty prompt preservation."""

    project = CinematicProject(
        metadata=ProjectMetadata(
            title="Empty Prompt Test",
            project_type="cinematic",
        ),
        scenes=[
            make_scene(
                1,
                dialogue_or_vocals="",
            ),
        ],
    )

    profile = PromptProfile(
        name="dialogue-only",
        enabled_components=[
            "dialogue_or_vocals",
        ],
    )

    options = ProjectExportOptions(
        name="empty-sections",
        include_structured_prompts=True,
        include_empty_prompt_sections=True,
    )

    data = project_to_dict(
        project,
        prompt_profile=profile,
        export_options=options,
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

    assert (
        scene_result["sections"][0][
            "section_id"
        ]
        == "dialogue_or_vocals"
    )

    assert (
        scene_result["sections"][0][
            "metadata"
        ]["empty"]
        is True
    )


def test_full_enhanced_export():
    """
    All currently supported project production layers should
    coexist in one Enhanced Project Export.
    """

    options = ProjectExportOptions(
        name="full-production",
        include_timeline=True,
        include_workflow=True,
        include_duration_validation=True,
        include_continuity_validation=True,
        include_global_constraints=True,
        include_prompt_profile=True,
        include_structured_prompts=True,
    )

    data = project_to_dict(
        make_project(),
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
        list(data.keys())
        == [
            "manifest",
            "project",
            "timeline",
            "workflow",
            "duration_validation",
            "continuity_validation",
            "global_constraints",
            "prompt_profile",
            "structured_prompts",
        ]
    )

    manifest = data[
        "manifest"
    ]

    assert (
        manifest[
            "included_sections"
        ]
        == [
            "project",
            "timeline",
            "workflow",
            "duration_validation",
            "continuity_validation",
            "global_constraints",
            "prompt_profile",
            "structured_prompts",
        ]
    )

    assert (
        manifest[
            "omitted_sections"
        ]
        == []
    )

    assert (
        manifest[
            "active_optional_systems"
        ]
        == [
            "duration_validation",
            "continuity_validation",
            "global_constraints",
            "prompt_profile",
            "structured_prompts",
        ]
    )

    assert (
        manifest["summary"]["valid"]
        is True
    )


def test_manifest_configuration_matches_export_options():
    """Enhanced manifest should serialize the source configuration."""

    options = ProjectExportOptions(
        name="portable-config",
        include_timeline=False,
        include_structured_prompts=True,
    )

    data = project_to_dict(
        make_project(),
        export_options=options,
    )

    assert (
        data["manifest"][
            "configuration"
        ]
        == options.to_dict()
    )


def test_manifest_reports_actual_not_only_requested_sections():
    """
    Manifest inclusion should represent actual export output,
    not merely requested options.
    """

    options = ProjectExportOptions(
        name="partial-production",
        include_duration_validation=True,
        include_global_constraints=True,
        include_structured_prompts=True,
    )

    data = project_to_dict(
        make_project(),
        export_options=options,
    )

    assert (
        data["manifest"][
            "included_sections"
        ]
        == [
            "project",
            "timeline",
            "workflow",
            "structured_prompts",
        ]
    )

    reasons = {
        item["section_id"]: item["reason"]
        for item in data[
            "manifest"
        ][
            "omitted_sections"
        ]
    }

    assert (
        reasons["duration_validation"]
        == "missing_duration_policy"
    )

    assert (
        reasons["global_constraints"]
        == "missing_global_constraints"
    )


def test_enhanced_export_rejects_invalid_options():
    """Invalid ProjectExportOptions should fail before export."""

    options = ProjectExportOptions(
        name="invalid",
        include_structured_prompts=False,
        include_empty_prompt_sections=True,
    )

    with pytest.raises(
        ValueError,
        match=(
            "Invalid project export options"
        ),
    ):
        project_to_dict(
            make_project(),
            export_options=options,
        )


def test_conflicting_legacy_structured_prompt_flag_is_rejected():
    """
    Legacy Structured Prompt activation cannot contradict
    Enhanced ProjectExportOptions.
    """

    options = ProjectExportOptions(
        name="conflict",
        include_structured_prompts=False,
    )

    with pytest.raises(
        ValueError,
        match=(
            "Conflicting structured prompt "
            "export configuration"
        ),
    ):
        project_to_dict(
            make_project(),
            include_structured_prompts=True,
            export_options=options,
        )


def test_matching_legacy_structured_prompt_flag_is_allowed():
    """
    A redundant legacy True flag is allowed when it agrees
    with Enhanced ProjectExportOptions.
    """

    options = ProjectExportOptions(
        name="compatible",
        include_structured_prompts=True,
    )

    data = project_to_dict(
        make_project(),
        include_structured_prompts=True,
        export_options=options,
    )

    assert (
        "structured_prompts"
        in data
    )


def test_conflicting_empty_prompt_section_flag_is_rejected():
    """Legacy empty-section flags cannot contradict Enhanced options."""

    options = ProjectExportOptions(
        name="conflict",
        include_structured_prompts=True,
        include_empty_prompt_sections=False,
    )

    with pytest.raises(
        ValueError,
        match=(
            "Conflicting empty prompt-section "
            "configuration"
        ),
    ):
        project_to_dict(
            make_project(),
            include_structured_prompts=True,
            include_empty_prompt_sections=True,
            export_options=options,
        )


def test_project_to_json_preserves_enhanced_manifest():
    """Enhanced export should survive JSON serialization."""

    options = ProjectExportOptions(
        name="json-export",
        include_structured_prompts=True,
    )

    content = project_to_json(
        make_project(),
        export_options=options,
    )

    data = json.loads(
        content
    )

    assert "manifest" in data

    assert (
        data["manifest"][
            "export_name"
        ]
        == "json-export"
    )

    assert (
        "structured_prompts"
        in data
    )


def test_save_project_json_preserves_enhanced_manifest(
    tmp_path,
):
    """Enhanced exports should persist to disk and reload."""

    options = ProjectExportOptions(
        name="saved-export",
        include_structured_prompts=True,
    )

    output_path = (
        tmp_path
        / "enhanced"
        / "project.json"
    )

    saved_path = save_project_json(
        make_project(),
        output_path,
        export_options=options,
    )

    data = json.loads(
        saved_path.read_text(
            encoding="utf-8"
        )
    )

    assert (
        data["manifest"][
            "export_name"
        ]
        == "saved-export"
    )

    assert (
        "structured_prompts"
        in data
    )


def test_enhanced_export_does_not_mutate_inputs():
    """
    Enhanced export should not mutate project or supplied
    production configuration objects.
    """

    project = make_project()

    duration_policy = (
        make_duration_policy()
    )

    continuity_profile = (
        make_continuity_profile()
    )

    constraints = (
        make_global_constraints()
    )

    prompt_profile = (
        make_prompt_profile()
    )

    options = ProjectExportOptions(
        name="non-mutating",
        include_duration_validation=True,
        include_continuity_validation=True,
        include_global_constraints=True,
        include_prompt_profile=True,
        include_structured_prompts=True,
    )

    project_before = (
        project.to_dict()
    )

    duration_before = (
        duration_policy.to_dict()
    )

    continuity_before = (
        continuity_profile.to_dict()
    )

    constraints_before = (
        constraints.to_dict()
    )

    prompt_before = (
        prompt_profile.to_dict()
    )

    options_before = (
        options.to_dict()
    )

    project_to_dict(
        project,
        duration_policy=duration_policy,
        continuity_profile=(
            continuity_profile
        ),
        global_constraints=constraints,
        prompt_profile=prompt_profile,
        export_options=options,
    )

    assert (
        project.to_dict()
        == project_before
    )

    assert (
        duration_policy.to_dict()
        == duration_before
    )

    assert (
        continuity_profile.to_dict()
        == continuity_before
    )

    assert (
        constraints.to_dict()
        == constraints_before
    )

    assert (
        prompt_profile.to_dict()
        == prompt_before
    )

    assert (
        options.to_dict()
        == options_before
    )


def test_disabled_optional_top_level_sections_do_not_export():
    """
    Supplied production systems should not automatically become
    top-level sections in Enhanced Mode when options disable them.
    """

    options = ProjectExportOptions(
        name="disabled-top-level",
        include_duration_validation=False,
        include_continuity_validation=False,
        include_global_constraints=False,
        include_prompt_profile=False,
    )

    data = project_to_dict(
        make_project(),
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
        "duration_validation"
        not in data
    )

    assert (
        "continuity_validation"
        not in data
    )

    assert (
        "global_constraints"
        not in data
    )

    assert (
        "prompt_profile"
        not in data
    )


def test_manifest_is_platform_agnostic():
    """Core Enhanced Export should not introduce provider payloads."""

    options = ProjectExportOptions(
        name="provider-neutral",
        include_structured_prompts=True,
    )

    data = project_to_dict(
        make_project(),
        export_options=options,
    )

    assert "wan_payload" not in data
    assert "veo_payload" not in data
    assert "kling_payload" not in data

    assert (
        all(
            section
            not in {
                "wan_payload",
                "veo_payload",
                "kling_payload",
            }
            for section in data[
                "manifest"
            ][
                "included_sections"
            ]
        )
    )
