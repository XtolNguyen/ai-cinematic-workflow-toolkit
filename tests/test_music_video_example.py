"""
Automated validation for the v0.2.0 runnable music-video example.

These tests treat examples/music_video_project.py as executable
documentation and verify that its major public-API demonstrations
remain coherent, provider-neutral, serializable, and directly runnable.
"""

import importlib.util
import json
from pathlib import Path


PROJECT_ROOT = Path(
    __file__
).resolve().parents[1]

EXAMPLE_PATH = (
    PROJECT_ROOT
    / "examples"
    / "music_video_project.py"
)


def load_example_module():
    """Load the runnable example without executing main()."""

    spec = importlib.util.spec_from_file_location(
        "ai_cinematic_workflow_music_video_example",
        EXAMPLE_PATH,
    )

    if (
        spec is None
        or spec.loader is None
    ):
        raise RuntimeError(
            "Could not load runnable music-video example"
        )

    module = (
        importlib.util.module_from_spec(
            spec
        )
    )

    spec.loader.exec_module(
        module
    )

    return module


example = load_example_module()


def test_demo_project_matches_v02_contract():
    """The runnable example should expose a valid v0.2 project."""

    project = (
        example.create_demo_project()
    )

    assert (
        project.validate()
        == []
    )

    assert (
        project.metadata.title
        == "Neon Echoes"
    )

    assert (
        project.metadata.project_type
        == "music-video"
    )

    assert (
        project.scene_count
        == 3
    )

    assert (
        project.total_duration_seconds
        == 45
    )

    assert (
        project.is_music_video
        is True
    )

    structure = (
        project.music_video_structure
    )

    assert structure is not None

    assert (
        structure.section_count
        == 3
    )

    assert (
        structure.total_duration_seconds
        == 45
    )

    assert (
        structure.mapped_scene_ids
        == [
            1,
            2,
            3,
        ]
    )

    assert [
        section.normalized_section_type
        for section in structure.sections
    ] == [
        "intro",
        "verse",
        "instrumental",
    ]

    assert [
        section.normalized_performance_mode
        for section in structure.sections
    ] == [
        "cinematic-only",
        "vocal",
        "instrumental",
    ]

    assert [
        section.scene_ids
        for section in structure.sections
    ] == [
        [1],
        [2],
        [3],
    ]


def test_demo_preserves_backward_compatible_scene_contract():
    """
    Retain the original project identity and intentional
    scene-3 wardrobe continuity event.
    """

    project = (
        example.create_demo_project()
    )

    assert (
        project.scenes[0].continuity[
            "wardrobe"
        ]
        == "black cinematic outfit"
    )

    assert (
        project.scenes[1].continuity[
            "wardrobe"
        ]
        == "black cinematic outfit"
    )

    assert (
        project.scenes[2].continuity[
            "wardrobe"
        ]
        == "white cinematic outfit"
    )

    workflow_results = (
        example.process_project(
            project.scenes
        )
    )

    assert (
        len(workflow_results)
        == 3
    )

    assert all(
        result.valid
        for result in workflow_results
    )

    scene_3_issue_fields = {
        issue["field"]
        for issue in (
            workflow_results[2]
            .continuity_issues
        )
    }

    assert (
        "continuity.wardrobe"
        in scene_3_issue_fields
    )


def test_demo_lip_sync_policy_matches_performance_modes():
    """
    Vocal sections should require lip-sync while cinematic-only
    and instrumental sections remain protected from singing.
    """

    project = (
        example.create_demo_project()
    )

    structure = (
        project.music_video_structure
    )

    assert structure is not None

    policies = (
        example.resolve_music_video_lip_sync(
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

    assert [
        policy.singing_mouth_movement_allowed
        for policy in policies
    ] == [
        False,
        True,
        False,
    ]

    assert [
        policy.lip_sync_mode
        for policy in policies
    ] == [
        "disabled",
        "required",
        "disabled",
    ]

    assert (
        policies[0].performance_mode
        == "cinematic-only"
    )

    assert (
        policies[1].performance_mode
        == "vocal"
    )

    assert (
        policies[2].performance_mode
        == "instrumental"
    )


def test_demo_duration_and_music_timing_are_valid():
    """The example should align three 15-second scenes to 45 seconds."""

    project = (
        example.create_demo_project()
    )

    policy = (
        example.create_duration_policy()
    )

    structure = (
        project.music_video_structure
    )

    assert structure is not None

    result = (
        example.validate_music_video_timing(
            project.scenes,
            structure,
            policy,
        )
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
        result.scene_count
        == 3
    )

    assert (
        result.section_count
        == 3
    )

    assert (
        result.cinematic_duration_seconds
        == 45
    )

    assert (
        result.music_duration_seconds
        == 45
    )


def test_demo_advanced_continuity_reports_expected_warning():
    """
    The deliberate wardrobe change should be a warning rather
    than an error under the example ContinuityProfile.
    """

    project = (
        example.create_demo_project()
    )

    profile = (
        example.create_continuity_profile()
    )

    result = (
        example.validate_project_continuity(
            project.scenes,
            profile,
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

    wardrobe_issues = [
        issue
        for issue in result.issues
        if (
            issue.field_name
            == "wardrobe"
        )
    ]

    assert (
        len(wardrobe_issues)
        == 1
    )

    issue = wardrobe_issues[0]

    assert (
        issue.severity
        == "warning"
    )

    assert (
        issue.previous_scene_id
        == 2
    )

    assert (
        issue.current_scene_id
        == 3
    )

    assert (
        issue.previous_value
        == "black cinematic outfit"
    )

    assert (
        issue.current_value
        == "white cinematic outfit"
    )


def test_demo_structured_prompts_use_profile_and_globals():
    """
    PromptProfile and GlobalConstraints should resolve before
    platform adaptation.
    """

    project = (
        example.create_demo_project()
    )

    prompt_profile = (
        example.create_prompt_profile()
    )

    global_constraints = (
        example.create_global_constraints()
    )

    (
        resolved_profile,
        structured_results,
    ) = example.build_structured_prompts(
        project,
        prompt_profile,
        global_constraints,
    )

    assert (
        resolved_profile.name
        == "neon-echoes-resolved"
    )

    assert (
        len(structured_results)
        == 3
    )

    assert [
        result.scene_id
        for result in structured_results
    ] == [
        1,
        2,
        3,
    ]

    assert all(
        result.prompt_profile_name
        == "neon-echoes-resolved"
        for result in structured_results
    )

    assert all(
        "global_constraints"
        in result.included_components
        for result in structured_results
    )

    assert all(
        "negative_constraints"
        in result.included_components
        for result in structured_results
    )

    assert all(
        result.is_valid
        for result in structured_results
    )


def test_demo_platform_adapter_is_provider_neutral():
    """
    The demonstration adapter should exercise the adapter
    foundation without pretending to be a real provider adapter.
    """

    adapter = (
        example.create_demo_adapter()
    )

    assert (
        adapter.is_valid
        is True
    )

    assert (
        adapter.canonical_platform_id
        == "example_video_platform"
    )

    assert (
        adapter.metadata[
            "provider_specific"
        ]
        is False
    )

    assert (
        adapter.capabilities
        .supports_structured_prompt_input
        is True
    )

    assert (
        adapter.capabilities
        .supports_enhanced_project_export
        is False
    )

    assert (
        adapter.capabilities
        .custom_capabilities[
            "network_execution"
        ]
        is False
    )


def test_demo_adapter_registry_and_capability_filtering():
    """
    Registry lookup and capability filtering should work across
    the runnable example's StructuredPromptResult objects.
    """

    project = (
        example.create_demo_project()
    )

    (
        _,
        structured_results,
    ) = example.build_structured_prompts(
        project,
        example.create_prompt_profile(),
        example.create_global_constraints(),
    )

    registry = (
        example.PlatformAdapterRegistry()
    )

    adapter = (
        example.create_demo_adapter()
    )

    registry.register(
        adapter
    )

    resolved = registry.get(
        "example-video-platform"
    )

    assert (
        resolved is adapter
    )

    assert (
        registry.platform_ids
        == [
            "example_video_platform",
        ]
    )

    results = [
        resolved.adapt_structured_prompt(
            source
        )
        for source in structured_results
    ]

    assert (
        len(results)
        == 3
    )

    assert all(
        result.is_valid
        for result in results
    )

    assert all(
        result.error_count
        == 0
        for result in results
    )

    assert all(
        "negative_constraints"
        in result.supported_features
        for result in results
    )

    assert all(
        "global_constraints"
        in result.unsupported_features
        for result in results
    )

    for result in results:
        assert (
            "api_key"
            not in result.payload
        )

        assert (
            "endpoint"
            not in result.payload
        )

        assert (
            "wan_parameters"
            not in result.payload
        )

        assert (
            "veo_parameters"
            not in result.payload
        )

        assert (
            "kling_parameters"
            not in result.payload
        )


def test_demo_enhanced_export_contains_all_requested_layers():
    """
    The example should demonstrate the complete currently
    implemented Enhanced Project Export layer.
    """

    project = (
        example.create_demo_project()
    )

    duration_policy = (
        example.create_duration_policy()
    )

    continuity_profile = (
        example.create_continuity_profile()
    )

    global_constraints = (
        example.create_global_constraints()
    )

    prompt_profile = (
        example.create_prompt_profile()
    )

    export_options = (
        example.create_export_options()
    )

    data = (
        example.build_enhanced_export(
            project,
            duration_policy,
            continuity_profile,
            global_constraints,
            prompt_profile,
            export_options,
        )
    )

    assert list(
        data.keys()
    ) == [
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

    manifest = data[
        "manifest"
    ]

    expected_sections = [
        "project",
        "timeline",
        "workflow",
        "duration_validation",
        "continuity_validation",
        "global_constraints",
        "prompt_profile",
        "structured_prompts",
    ]

    assert (
        manifest[
            "summary"
        ][
            "valid"
        ]
        is True
    )

    assert (
        manifest[
            "export_name"
        ]
        == "neon-echoes-v0.2-demo"
    )

    assert (
        manifest[
            "included_sections"
        ]
        == expected_sections
    )

    assert (
        manifest[
            "omitted_sections"
        ]
        == []
    )

    assert (
        manifest[
            "configuration"
        ][
            "requested_sections"
        ]
        == expected_sections
    )

    assert (
        manifest[
            "summary"
        ][
            "section_count"
        ]
        == 8
    )


def test_demo_export_contains_music_video_and_lip_sync_data():
    """Enhanced export should retain music structure and lip-sync data."""

    data = (
        example.build_enhanced_export(
            example.create_demo_project(),
            example.create_duration_policy(),
            example.create_continuity_profile(),
            example.create_global_constraints(),
            example.create_prompt_profile(),
            example.create_export_options(),
        )
    )

    music_video = (
        data[
            "project"
        ][
            "music_video"
        ]
    )

    assert (
        music_video[
            "summary"
        ][
            "section_count"
        ]
        == 3
    )

    assert (
        music_video[
            "summary"
        ][
            "total_duration_seconds"
        ]
        == 45
    )

    assert (
        music_video[
            "summary"
        ][
            "mapped_scene_count"
        ]
        == 3
    )

    assert (
        music_video[
            "summary"
        ][
            "vocal_section_count"
        ]
        == 1
    )

    assert (
        music_video[
            "summary"
        ][
            "instrumental_section_count"
        ]
        == 1
    )

    lip_sync = (
        music_video[
            "lip_sync_policies"
        ]
    )

    assert (
        lip_sync[
            "summary"
        ][
            "policy_count"
        ]
        == 3
    )

    assert (
        lip_sync[
            "summary"
        ][
            "required_count"
        ]
        == 1
    )

    assert (
        lip_sync[
            "summary"
        ][
            "disabled_count"
        ]
        == 2
    )


def test_demo_export_validation_layers_are_present():
    """Enhanced export should include each requested validation layer."""

    data = (
        example.build_enhanced_export(
            example.create_demo_project(),
            example.create_duration_policy(),
            example.create_continuity_profile(),
            example.create_global_constraints(),
            example.create_prompt_profile(),
            example.create_export_options(),
        )
    )

    assert (
        data[
            "duration_validation"
        ][
            "mode"
        ]
        == "music_video_timing"
    )

    assert (
        data[
            "duration_validation"
        ][
            "summary"
        ][
            "valid"
        ]
        is True
    )

    assert (
        data[
            "continuity_validation"
        ][
            "mode"
        ]
        == "advanced_continuity"
    )

    assert (
        data[
            "continuity_validation"
        ][
            "summary"
        ][
            "valid"
        ]
        is True
    )

    assert (
        data[
            "continuity_validation"
        ][
            "summary"
        ][
            "error_count"
        ]
        == 0
    )

    assert (
        data[
            "continuity_validation"
        ][
            "summary"
        ][
            "warning_count"
        ]
        == 1
    )

    assert (
        data[
            "global_constraints"
        ][
            "mode"
        ]
        == "project_global_constraints"
    )

    assert (
        data[
            "prompt_profile"
        ][
            "mode"
        ]
        == "resolved_prompt_profile"
    )

    assert (
        data[
            "structured_prompts"
        ][
            "mode"
        ]
        == "structured_prompt_sections"
    )

    assert (
        data[
            "structured_prompts"
        ][
            "summary"
        ][
            "scene_count"
        ]
        == 3
    )


def test_demo_export_is_json_serializable_and_provider_neutral():
    """The complete runnable-example export must remain portable."""

    data = (
        example.build_enhanced_export(
            example.create_demo_project(),
            example.create_duration_policy(),
            example.create_continuity_profile(),
            example.create_global_constraints(),
            example.create_prompt_profile(),
            example.create_export_options(),
        )
    )

    encoded = json.dumps(
        data,
        ensure_ascii=False,
    )

    decoded = json.loads(
        encoded
    )

    assert (
        decoded[
            "project"
        ][
            "metadata"
        ][
            "title"
        ]
        == "Neon Echoes"
    )

    assert (
        decoded[
            "project"
        ][
            "summary"
        ][
            "scene_count"
        ]
        == 3
    )

    assert (
        decoded[
            "project"
        ][
            "summary"
        ][
            "total_duration_seconds"
        ]
        == 45
    )

    assert (
        "wan_payload"
        not in decoded
    )

    assert (
        "veo_payload"
        not in decoded
    )

    assert (
        "kling_payload"
        not in decoded
    )

    assert (
        "api_key"
        not in decoded
    )

    assert (
        "endpoint"
        not in decoded
    )


def test_demo_main_runs_and_persists_complete_json(
    tmp_path,
    monkeypatch,
    capsys,
):
    """
    The example's public entry point should execute from beginning
    to end and create the expected enhanced JSON output.
    """

    monkeypatch.chdir(
        tmp_path
    )

    example.main()

    output = (
        capsys
        .readouterr()
        .out
    )

    assert (
        "AI CINEMATIC WORKFLOW TOOLKIT "
        "— V0.2 MUSIC VIDEO DEMO"
        in output
    )

    assert (
        "1. MULTI-SCENE WORKFLOW"
        in output
    )

    assert (
        "2. CINEMATIC TIMELINE"
        in output
    )

    assert (
        "3. MUSIC VIDEO STRUCTURE"
        in output
    )

    assert (
        "4. LIP-SYNC POLICY"
        in output
    )

    assert (
        "5. DURATION + MUSIC VIDEO TIMING VALIDATION"
        in output
    )

    assert (
        "6. ADVANCED CONTINUITY"
        in output
    )

    assert (
        "7. GLOBAL CONSTRAINTS"
        in output
    )

    assert (
        "8. PROMPT PROFILE + STRUCTURED PROMPTS"
        in output
    )

    assert (
        "9. PLATFORM ADAPTER FOUNDATION"
        in output
    )

    assert (
        "10. ENHANCED PROJECT EXPORT"
        in output
    )

    assert (
        "V0.2 MUSIC VIDEO DEMO COMPLETE"
        in output
    )

    assert (
        "External APIs required: no"
        in output
    )

    assert (
        "Provider-specific execution: no"
        in output
    )

    path = (
        tmp_path
        / "examples"
        / "output"
        / "music_video_project.json"
    )

    assert path.exists()

    data = json.loads(
        path.read_text(
            encoding="utf-8"
        )
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
            "project"
        ][
            "metadata"
        ][
            "title"
        ]
        == "Neon Echoes"
    )

    assert (
        data[
            "project"
        ][
            "summary"
        ][
            "scene_count"
        ]
        == 3
    )

    assert (
        data[
            "project"
        ][
            "summary"
        ][
            "total_duration_seconds"
        ]
        == 45
    )

    assert (
        data[
            "structured_prompts"
        ][
            "summary"
        ][
            "scene_count"
        ]
        == 3
    )
