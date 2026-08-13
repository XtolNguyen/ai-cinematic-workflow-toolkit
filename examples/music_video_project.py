"""
Runnable v0.2.0 music-video example.

This example demonstrates how the AI Cinematic Workflow Toolkit
combines its provider-neutral cinematic production layers:

- CinematicProject
- Multi-scene workflow processing
- Cinematic Timeline
- Music Video Structure
- Vocal / instrumental performance modes
- Lip-Sync Policy
- DurationPolicy
- Music-video timing validation
- ContinuityProfile
- GlobalConstraints
- PromptProfile
- Structured Prompt Sections
- Enhanced Project Export
- ProjectExportOptions
- ProjectExportManifest
- PlatformAdapter
- PlatformAdapterRegistry
- JSON persistence

The example intentionally uses no external API, API key, network
execution, or provider-specific WAN, Veo, Kling, or other parameters.
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
    format_timestamp,
    process_project,
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


SEPARATOR = "=" * 72
SUB_SEPARATOR = "-" * 72


def create_demo_project() -> CinematicProject:
    """
    Create a three-scene music-video project.

    Scene 3 intentionally changes wardrobe so both the original
    workflow continuity report and the advanced ContinuityProfile
    demonstration have a visible continuity event.
    """

    metadata = ProjectMetadata(
        title="Neon Echoes",
        project_type="music-video",
        description=(
            "Provider-neutral v0.2.0 demonstration project for the "
            "AI Cinematic Workflow Toolkit."
        ),
        language="en",
        target_platform="provider-neutral AI video",
        aspect_ratio="16:9",
        frame_rate=24,
    )

    scene_1 = Scene(
        scene_id=1,
        duration_seconds=15,
        location="Neon cinematic performance stage",
        camera=Camera(
            shot="medium close-up",
            movement="slow dolly in",
            lens="50mm",
        ),
        characters=[
            "Lead performer",
        ],
        performance=(
            "Quiet cinematic acting during the opening "
            "instrumental atmosphere"
        ),
        lighting=(
            "Soft blue and magenta cinematic lighting"
        ),
        mood="Reflective and atmospheric",
        dialogue_or_vocals="",
        continuity={
            "wardrobe": "black cinematic outfit",
            "hair": "long dark hair",
        },
        negative_constraints=[
            "Distorted Face",
            "Extra Fingers",
            "Camera Jitter",
            "distorted face",
        ],
    )

    scene_2 = Scene(
        scene_id=2,
        duration_seconds=15,
        location="Neon cinematic performance stage",
        camera=Camera(
            shot="close-up",
            movement="slow push in",
            lens="85mm",
        ),
        characters=[
            "Lead performer",
        ],
        performance=(
            "Natural professional vocal performance with "
            "increasing emotional intensity"
        ),
        lighting=(
            "Soft blue and magenta cinematic lighting"
        ),
        mood="Emotional and intimate",
        dialogue_or_vocals=(
            "Professional emotional vocal performance"
        ),
        continuity={
            "wardrobe": "black cinematic outfit",
            "hair": "long dark hair",
        },
        negative_constraints=[
            "Distorted Face",
            "Extra Fingers",
            "Camera Jitter",
        ],
    )

    scene_3 = Scene(
        scene_id=3,
        duration_seconds=15,
        location="Neon cinematic performance stage",
        camera=Camera(
            shot="medium shot",
            movement="slow orbit",
            lens="50mm",
        ),
        characters=[
            "Lead performer",
        ],
        performance=(
            "Controlled cinematic physical performance during "
            "the instrumental closing section"
        ),
        lighting=(
            "Soft blue and magenta cinematic lighting"
        ),
        mood="Powerful and cinematic",
        dialogue_or_vocals="",
        continuity={
            # Intentional change retained for continuity demonstration
            # and backward-compatible CI validation.
            "wardrobe": "white cinematic outfit",
            "hair": "long dark hair",
        },
        negative_constraints=[
            "Distorted Face",
            "Extra Fingers",
            "Camera Jitter",
        ],
    )

    music_video_structure = MusicVideoStructure(
        sections=[
            MusicSection(
                section_id=1,
                section_type="intro",
                start_seconds=0,
                end_seconds=15,
                performance_mode="cinematic-only",
                scene_ids=[
                    1,
                ],
                label="Intro",
                notes=(
                    "Atmospheric opening without singing."
                ),
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
                notes=(
                    "Visible professional vocal performance."
                ),
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
                notes=(
                    "Instrumental performance with no lip-sync."
                ),
            ),
        ]
    )

    return CinematicProject(
        metadata=metadata,
        scenes=[
            scene_1,
            scene_2,
            scene_3,
        ],
        music_video_structure=(
            music_video_structure
        ),
    )


def create_duration_policy() -> DurationPolicy:
    """Create the provider-neutral scene-duration policy."""

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


def create_continuity_profile() -> ContinuityProfile:
    """
    Create an advanced continuity profile.

    Character identity and hair are strictly locked.
    Wardrobe changes are reported as warnings rather than errors.
    """

    return ContinuityProfile(
        name="neon-echoes-continuity",
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


def create_global_constraints() -> GlobalConstraints:
    """Create reusable project-wide cinematic constraints."""

    return GlobalConstraints(
        name="neon-echoes-production",
        required_constraints=[
            "maintain cinematic realism",
            "maintain professional performance quality",
        ],
        advisory_constraints=[
            "preserve natural body movement",
        ],
        negative_constraints=[
            "distorted face",
            "extra fingers",
            "camera jitter",
        ],
        prohibited_elements=[
            "duplicate limbs",
        ],
        character_identity_constraints=[
            "preserve lead performer identity",
        ],
        visual_style_constraints=[
            "cinematic photorealism",
            "consistent blue and magenta visual language",
        ],
        camera_constraints=[
            "avoid unstable accidental camera motion",
        ],
        environment_constraints=[
            "preserve stage geometry",
        ],
        custom_constraints={
            "performance_quality": [
                "natural facial expression",
                "professional cinematic acting",
            ],
        },
    )


def create_prompt_profile() -> PromptProfile:
    """Create a reusable complete cinematic PromptProfile."""

    return PromptProfile(
        name="neon-echoes-cinematic",
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
        custom_config={
            "purpose": (
                "provider-neutral music-video demonstration"
            ),
        },
    )


def create_export_options() -> ProjectExportOptions:
    """Enable all currently implemented enhanced export layers."""

    return ProjectExportOptions(
        name="neon-echoes-v0.2-demo",
        include_timeline=True,
        include_workflow=True,
        include_duration_validation=True,
        include_continuity_validation=True,
        include_global_constraints=True,
        include_prompt_profile=True,
        include_structured_prompts=True,
        include_empty_prompt_sections=False,
    )


def create_demo_adapter() -> PlatformAdapter:
    """
    Create a provider-neutral demonstration adapter.

    This is intentionally not a WAN, Veo, Kling, or other
    provider-specific implementation.
    """

    return PlatformAdapter(
        platform_id="Example Video Platform",
        display_name="Example Video Platform",
        adapter_version="1.0",
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
                supports_structured_prompt_input=True,
                supports_enhanced_project_export=False,
                supports_section_metadata=True,
                custom_capabilities={
                    "demo_only": True,
                    "network_execution": False,
                },
            )
        ),
        metadata={
            "category": "video_generation",
            "provider_specific": False,
            "purpose": (
                "provider-neutral adapter demonstration"
            ),
        },
    )


def print_project_summary(
    project: CinematicProject,
) -> None:
    """Print the basic project summary."""

    print(SEPARATOR)
    print(
        "AI CINEMATIC WORKFLOW TOOLKIT "
        "— V0.2 MUSIC VIDEO DEMO"
    )
    print(SEPARATOR)

    print(
        f"Project: {project.metadata.title}"
    )
    print(
        f"Scenes: {project.scene_count}"
    )
    print(
        "Total duration: "
        f"{project.total_duration_seconds} seconds"
    )
    print(
        "Provider mode: "
        f"{project.metadata.target_platform}"
    )
    print()


def print_workflow_results(
    project: CinematicProject,
) -> None:
    """Run and display the original multi-scene workflow layer."""

    print(SEPARATOR)
    print("1. MULTI-SCENE WORKFLOW")
    print(SEPARATOR)

    results = process_project(
        project.scenes
    )

    for result in results:
        print(
            f"Scene {result.scene_id}: "
            f"valid={result.valid}"
        )

        if result.continuity_issues:
            print(
                "  Continuity issues:"
            )

            for issue in (
                result.continuity_issues
            ):
                print(
                    "  - "
                    f"{issue['field']}: "
                    f"{issue['previous_value']} "
                    "-> "
                    f"{issue['current_value']}"
                )
        else:
            print(
                "  Continuity issues: none"
            )

    print()


def print_timeline(
    project: CinematicProject,
) -> None:
    """Build and display the cinematic timeline."""

    print(SEPARATOR)
    print("2. CINEMATIC TIMELINE")
    print(SEPARATOR)

    timeline = build_timeline(
        project.scenes
    )

    for entry in timeline.entries:
        print(
            f"Scene {entry.scene_id}: "
            f"{format_timestamp(entry.start_seconds)} "
            "-> "
            f"{format_timestamp(entry.end_seconds)} "
            f"({entry.duration_seconds}s)"
        )

    print(
        "Timeline issues: "
        f"{len(timeline.issues)}"
    )
    print()


def print_music_structure(
    project: CinematicProject,
) -> None:
    """Display music sections and scene mappings."""

    print(SEPARATOR)
    print("3. MUSIC VIDEO STRUCTURE")
    print(SEPARATOR)

    structure = (
        project.music_video_structure
    )

    assert structure is not None

    for section in structure.sections:
        print(
            f"Section {section.section_id}: "
            f"{section.normalized_section_type}"
        )
        print(
            "  Time: "
            f"{section.start_seconds}s "
            "-> "
            f"{section.end_seconds}s"
        )
        print(
            "  Performance mode: "
            f"{section.normalized_performance_mode}"
        )
        print(
            "  Scene IDs: "
            f"{section.scene_ids}"
        )

    print()


def print_lip_sync_policies(
    project: CinematicProject,
) -> None:
    """Resolve and display lip-sync behavior."""

    print(SEPARATOR)
    print("4. LIP-SYNC POLICY")
    print(SEPARATOR)

    structure = (
        project.music_video_structure
    )

    assert structure is not None

    results = (
        resolve_music_video_lip_sync(
            structure
        )
    )

    for result in results:
        print(
            f"Section {result.section_id}: "
            f"{result.performance_mode}"
        )
        print(
            "  Lip-sync mode: "
            f"{result.lip_sync_mode}"
        )
        print(
            "  Required: "
            f"{result.lip_sync_required}"
        )
        print(
            "  Singing mouth movement allowed: "
            f"{result.singing_mouth_movement_allowed}"
        )
        print(
            "  Instruction: "
            f"{result.instruction}"
        )

    print()


def print_duration_validation(
    project: CinematicProject,
    policy: DurationPolicy,
) -> None:
    """Run music-video timing and DurationPolicy validation."""

    print(SEPARATOR)
    print("5. DURATION + MUSIC VIDEO TIMING VALIDATION")
    print(SEPARATOR)

    structure = (
        project.music_video_structure
    )

    assert structure is not None

    result = validate_music_video_timing(
        project.scenes,
        structure,
        policy,
    )

    print(
        f"Valid: {result.is_valid}"
    )
    print(
        f"Issues: {result.issue_count}"
    )
    print(
        "Cinematic duration: "
        f"{result.cinematic_duration_seconds}s"
    )
    print(
        "Music duration: "
        f"{result.music_duration_seconds}s"
    )

    for issue in result.issues:
        print(
            f"- {issue.scope}: "
            f"{issue.message}"
        )

    print()


def print_continuity_validation(
    project: CinematicProject,
    profile: ContinuityProfile,
) -> None:
    """Run advanced project continuity validation."""

    print(SEPARATOR)
    print("6. ADVANCED CONTINUITY")
    print(SEPARATOR)

    result = validate_project_continuity(
        project.scenes,
        profile,
    )

    print(
        f"Valid: {result.is_valid}"
    )
    print(
        f"Errors: {result.error_count}"
    )
    print(
        f"Warnings: {result.warning_count}"
    )

    for issue in result.issues:
        print(
            f"- {issue.severity.upper()} "
            f"{issue.field_name}: "
            f"{issue.previous_value} "
            "-> "
            f"{issue.current_value}"
        )

    print()


def print_global_constraints(
    project: CinematicProject,
    constraints: GlobalConstraints,
) -> None:
    """Resolve and display project-wide constraints."""

    print(SEPARATOR)
    print("7. GLOBAL CONSTRAINTS")
    print(SEPARATOR)

    resolution = (
        resolve_project_constraints(
            project.scenes,
            constraints,
        )
    )

    print(
        f"Constraint profile: {constraints.name}"
    )
    print(
        f"Resolved scenes: {resolution.scene_count}"
    )
    print(
        f"Warnings: {resolution.warning_count}"
    )

    for result in (
        resolution.scene_results
    ):
        print(
            f"Scene {result.scene_id} "
            "resolved negatives:"
        )

        for constraint in (
            result.resolved_negative_constraints
        ):
            print(
                f"  - {constraint}"
            )

    print()


def build_structured_prompts(
    project: CinematicProject,
    prompt_profile: PromptProfile,
    global_constraints: GlobalConstraints,
):
    """
    Resolve PromptProfile and build StructuredPromptResult
    objects for all scenes.
    """

    resolved_profile = (
        resolve_prompt_profile(
            prompt_profile,
            resolved_name=(
                "neon-echoes-resolved"
            ),
        )
    )

    results = [
        assemble_structured_prompt(
            scene,
            prompt_profile=(
                resolved_profile
            ),
            global_constraints=(
                global_constraints
            ),
            include_empty_sections=False,
        )
        for scene in project.scenes
    ]

    return (
        resolved_profile,
        results,
    )


def print_structured_prompts(
    resolved_profile,
    structured_results,
) -> None:
    """Display PromptProfile and Structured Prompt Sections."""

    print(SEPARATOR)
    print("8. PROMPT PROFILE + STRUCTURED PROMPTS")
    print(SEPARATOR)

    print(
        "Resolved PromptProfile: "
        f"{resolved_profile.name}"
    )
    print(
        "Enabled components: "
        + ", ".join(
            resolved_profile.enabled_components
        )
    )

    for result in structured_results:
        print(
            f"Scene {result.scene_id}:"
        )
        print(
            "  Included: "
            + ", ".join(
                result.included_components
            )
        )

        if result.omitted_components:
            print(
                "  Omitted:"
            )

            for omitted in (
                result.omitted_components
            ):
                print(
                    f"    - {omitted.component}: "
                    f"{omitted.reason}"
                )

    print()


def print_adapter_results(
    structured_results,
) -> None:
    """Register and execute the provider-neutral demo adapter."""

    print(SEPARATOR)
    print("9. PLATFORM ADAPTER FOUNDATION")
    print(SEPARATOR)

    registry = (
        PlatformAdapterRegistry()
    )

    adapter = create_demo_adapter()

    registry.register(
        adapter
    )

    resolved_adapter = registry.get(
        "example-video-platform"
    )

    print(
        "Registered platform IDs: "
        + ", ".join(
            registry.platform_ids
        )
    )
    print(
        "Resolved adapter: "
        f"{resolved_adapter.display_name}"
    )
    print(
        "Provider-specific: "
        f"{resolved_adapter.metadata['provider_specific']}"
    )

    for source in structured_results:
        result = (
            resolved_adapter
            .adapt_structured_prompt(
                source
            )
        )

        print(
            f"Scene {source.scene_id}:"
        )
        print(
            "  Supported: "
            + (
                ", ".join(
                    result.supported_features
                )
                or "none"
            )
        )
        print(
            "  Unsupported: "
            + (
                ", ".join(
                    result.unsupported_features
                )
                or "none"
            )
        )
        print(
            "  Warnings: "
            f"{result.warning_count}"
        )
        print(
            "  Errors: "
            f"{result.error_count}"
        )

    print()


def build_enhanced_export(
    project: CinematicProject,
    duration_policy: DurationPolicy,
    continuity_profile: ContinuityProfile,
    global_constraints: GlobalConstraints,
    prompt_profile: PromptProfile,
    export_options: ProjectExportOptions,
):
    """Build the complete provider-neutral Enhanced Project Export."""

    return project_to_dict(
        project,
        duration_policy=(
            duration_policy
        ),
        continuity_profile=(
            continuity_profile
        ),
        global_constraints=(
            global_constraints
        ),
        prompt_profile=(
            prompt_profile
        ),
        prompt_resolved_name=(
            "neon-echoes-resolved"
        ),
        export_options=(
            export_options
        ),
    )


def print_export_manifest(
    export_data,
) -> None:
    """Display the Enhanced Project Export manifest."""

    print(SEPARATOR)
    print("10. ENHANCED PROJECT EXPORT")
    print(SEPARATOR)

    manifest = export_data[
        "manifest"
    ]

    print(
        "Export name: "
        f"{manifest['export_name']}"
    )
    print(
        "Manifest valid: "
        f"{manifest['summary']['valid']}"
    )
    print(
        "Included sections:"
    )

    for section in (
        manifest["included_sections"]
    ):
        print(
            f"  - {section}"
        )

    print(
        "Omitted sections:"
    )

    if manifest[
        "omitted_sections"
    ]:
        for section in (
            manifest[
                "omitted_sections"
            ]
        ):
            print(
                "  - "
                f"{section['section_id']}: "
                f"{section['reason']}"
            )
    else:
        print(
            "  none"
        )

    print()


def save_enhanced_project(
    project: CinematicProject,
    duration_policy: DurationPolicy,
    continuity_profile: ContinuityProfile,
    global_constraints: GlobalConstraints,
    prompt_profile: PromptProfile,
    export_options: ProjectExportOptions,
) -> Path:
    """Persist the complete enhanced project JSON."""

    output_path = Path(
        "examples/output/"
        "music_video_project.json"
    )

    return save_project_json(
        project,
        output_path,
        duration_policy=(
            duration_policy
        ),
        continuity_profile=(
            continuity_profile
        ),
        global_constraints=(
            global_constraints
        ),
        prompt_profile=(
            prompt_profile
        ),
        prompt_resolved_name=(
            "neon-echoes-resolved"
        ),
        export_options=(
            export_options
        ),
    )


def main() -> None:
    """Run the complete v0.2.0 provider-neutral demonstration."""

    project = create_demo_project()

    duration_policy = (
        create_duration_policy()
    )

    continuity_profile = (
        create_continuity_profile()
    )

    global_constraints = (
        create_global_constraints()
    )

    prompt_profile = (
        create_prompt_profile()
    )

    export_options = (
        create_export_options()
    )

    project_errors = (
        project.validate()
    )

    if project_errors:
        raise ValueError(
            "Demo project validation failed: "
            + "; ".join(
                project_errors
            )
        )

    print_project_summary(
        project
    )

    print_workflow_results(
        project
    )

    print_timeline(
        project
    )

    print_music_structure(
        project
    )

    print_lip_sync_policies(
        project
    )

    print_duration_validation(
        project,
        duration_policy,
    )

    print_continuity_validation(
        project,
        continuity_profile,
    )

    print_global_constraints(
        project,
        global_constraints,
    )

    (
        resolved_profile,
        structured_results,
    ) = build_structured_prompts(
        project,
        prompt_profile,
        global_constraints,
    )

    print_structured_prompts(
        resolved_profile,
        structured_results,
    )

    print_adapter_results(
        structured_results
    )

    export_data = (
        build_enhanced_export(
            project,
            duration_policy,
            continuity_profile,
            global_constraints,
            prompt_profile,
            export_options,
        )
    )

    print_export_manifest(
        export_data
    )

    saved_path = (
        save_enhanced_project(
            project,
            duration_policy,
            continuity_profile,
            global_constraints,
            prompt_profile,
            export_options,
        )
    )

    print(SEPARATOR)
    print("V0.2 MUSIC VIDEO DEMO COMPLETE")
    print(SEPARATOR)
    print(
        f"JSON saved to: {saved_path}"
    )
    print(
        "External APIs required: no"
    )
    print(
        "Provider-specific execution: no"
    )


if __name__ == "__main__":
    main()
