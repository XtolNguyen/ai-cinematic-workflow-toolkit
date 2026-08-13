import json

import pytest

from ai_cinematic_workflow.export_options import (
    OPTIONAL_PROJECT_EXPORT_SECTIONS,
    PROJECT_EXPORT_SECTION_ORDER,
    VALID_PROJECT_EXPORT_SECTIONS,
    OmittedExportSection,
    ProjectExportManifest,
    ProjectExportOptions,
    build_project_export_manifest,
    normalize_export_section,
)


def test_normalize_export_section():
    """Export section identifiers should normalize canonically."""

    assert (
        normalize_export_section(
            "Structured Prompts"
        )
        == "structured_prompts"
    )

    assert (
        normalize_export_section(
            "duration-validation"
        )
        == "duration_validation"
    )

    assert (
        normalize_export_section(
            "  Global Constraints  "
        )
        == "global_constraints"
    )


def test_export_section_registry_matches_canonical_order():
    """Canonical export registry should remain deterministic."""

    assert (
        PROJECT_EXPORT_SECTION_ORDER
        == (
            "project",
            "timeline",
            "workflow",
            "duration_validation",
            "continuity_validation",
            "global_constraints",
            "prompt_profile",
            "structured_prompts",
        )
    )

    assert (
        VALID_PROJECT_EXPORT_SECTIONS
        == set(
            PROJECT_EXPORT_SECTION_ORDER
        )
    )


def test_optional_export_section_registry():
    """Optional production layers should remain explicit."""

    assert (
        OPTIONAL_PROJECT_EXPORT_SECTIONS
        == (
            "duration_validation",
            "continuity_validation",
            "global_constraints",
            "prompt_profile",
            "structured_prompts",
        )
    )


def test_default_export_options_are_valid():
    """Default options should preserve existing exporter behavior."""

    options = ProjectExportOptions()

    assert options.is_valid
    assert options.validate() == []

    assert (
        options.name
        == "default"
    )

    assert (
        options.include_timeline
        is True
    )

    assert (
        options.include_workflow
        is True
    )

    assert (
        options.include_structured_prompts
        is False
    )


def test_export_options_require_name():
    """Reusable export configurations require a readable name."""

    options = ProjectExportOptions(
        name="   ",
    )

    assert options.is_valid is False

    assert (
        "project export options name "
        "cannot be empty"
        in options.validate()
    )


def test_empty_prompt_sections_require_structured_prompts():
    """
    Empty prompt sections cannot be requested without
    Structured Prompt Sections.
    """

    options = ProjectExportOptions(
        include_empty_prompt_sections=True,
    )

    assert options.is_valid is False

    assert (
        "include_structured_prompts must be True "
        "when include_empty_prompt_sections is enabled"
        in options.validate()
    )


def test_empty_prompt_sections_are_valid_with_structured_prompts():
    """The empty-section flag becomes valid when prompts are enabled."""

    options = ProjectExportOptions(
        include_structured_prompts=True,
        include_empty_prompt_sections=True,
    )

    assert options.is_valid


def test_default_requested_sections():
    """
    Default enhanced configuration should request the
    existing project, timeline, and workflow layers.
    """

    options = ProjectExportOptions()

    assert (
        options.requested_sections
        == [
            "project",
            "timeline",
            "workflow",
        ]
    )


def test_project_section_is_always_requested():
    """Project payload cannot be disabled."""

    options = ProjectExportOptions(
        include_timeline=False,
        include_workflow=False,
    )

    assert (
        options.requested_sections
        == [
            "project",
        ]
    )


def test_full_export_options_use_canonical_order():
    """A full configuration should use canonical section ordering."""

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

    assert (
        options.requested_sections
        == list(
            PROJECT_EXPORT_SECTION_ORDER
        )
    )

    assert (
        options.excluded_sections
        == []
    )


def test_default_excluded_sections():
    """Default options should report all optional layers as excluded."""

    options = ProjectExportOptions()

    assert (
        options.excluded_sections
        == [
            "duration_validation",
            "continuity_validation",
            "global_constraints",
            "prompt_profile",
            "structured_prompts",
        ]
    )


def test_minimal_export_excluded_sections():
    """A project-only configuration should report every other layer."""

    options = ProjectExportOptions(
        name="minimal",
        include_timeline=False,
        include_workflow=False,
    )

    assert (
        options.excluded_sections
        == [
            "timeline",
            "workflow",
            "duration_validation",
            "continuity_validation",
            "global_constraints",
            "prompt_profile",
            "structured_prompts",
        ]
    )


def test_export_options_serialization():
    """ProjectExportOptions should produce portable data."""

    options = ProjectExportOptions(
        name="structured-production",
        include_global_constraints=True,
        include_prompt_profile=True,
        include_structured_prompts=True,
        include_empty_prompt_sections=True,
    )

    data = options.to_dict()

    assert (
        data["name"]
        == "structured-production"
    )

    assert (
        data["include_global_constraints"]
        is True
    )

    assert (
        data["include_prompt_profile"]
        is True
    )

    assert (
        data["include_structured_prompts"]
        is True
    )

    assert (
        data["include_empty_prompt_sections"]
        is True
    )

    assert (
        data["requested_sections"]
        == [
            "project",
            "timeline",
            "workflow",
            "global_constraints",
            "prompt_profile",
            "structured_prompts",
        ]
    )

    json.dumps(
        data,
        ensure_ascii=False,
    )


def test_omitted_export_section_is_valid():
    """Canonical omission metadata should pass validation."""

    item = OmittedExportSection(
        section_id="duration_validation",
        reason="missing_duration_policy",
    )

    assert item.is_valid
    assert item.validate() == []


def test_omitted_export_section_normalizes_identifier():
    """Omission serialization should normalize section IDs."""

    item = OmittedExportSection(
        section_id="Structured Prompts",
        reason="not_requested",
    )

    assert (
        item.to_dict()
        == {
            "section_id": (
                "structured_prompts"
            ),
            "reason": "not_requested",
        }
    )


def test_unknown_omitted_export_section_is_invalid():
    """Unknown export sections should not enter the manifest."""

    item = OmittedExportSection(
        section_id="future_provider_payload",
        reason="not_available",
    )

    assert item.is_valid is False

    assert any(
        "unknown project export section"
        in error
        for error in item.validate()
    )


def test_omitted_export_section_requires_reason():
    """Every omitted section needs an auditable reason."""

    item = OmittedExportSection(
        section_id="timeline",
        reason="   ",
    )

    assert item.is_valid is False

    assert (
        "omitted export section reason "
        "cannot be empty"
        in item.validate()
    )


def test_manifest_builder_canonicalizes_included_order():
    """
    The completed manifest should use canonical order regardless
    of the order supplied by the caller.
    """

    options = ProjectExportOptions(
        name="production",
        include_structured_prompts=True,
    )

    manifest = build_project_export_manifest(
        options,
        included_sections=[
            "structured_prompts",
            "workflow",
            "project",
            "timeline",
        ],
    )

    assert (
        manifest.included_sections
        == [
            "project",
            "timeline",
            "workflow",
            "structured_prompts",
        ]
    )

    assert manifest.is_valid


def test_manifest_reports_included_and_omitted_sections():
    """Manifest should describe actual completed export contents."""

    options = ProjectExportOptions(
        name="production",
        include_structured_prompts=True,
    )

    manifest = build_project_export_manifest(
        options,
        included_sections=[
            "project",
            "timeline",
            "workflow",
            "structured_prompts",
        ],
    )

    assert (
        manifest.section_count
        == 4
    )

    assert (
        manifest.omitted_section_count
        == 4
    )

    assert [
        item.section_id
        for item in manifest.omitted_sections
    ] == [
        "duration_validation",
        "continuity_validation",
        "global_constraints",
        "prompt_profile",
    ]


def test_manifest_uses_default_omission_reason():
    """Absent canonical sections should receive a default reason."""

    options = ProjectExportOptions(
        name="minimal",
        include_timeline=False,
        include_workflow=False,
    )

    manifest = build_project_export_manifest(
        options,
        included_sections=[
            "project",
        ],
    )

    assert all(
        item.reason
        == "not_included"
        for item in manifest.omitted_sections
    )


def test_manifest_supports_explicit_omission_reasons():
    """Caller-supplied omission reasons should remain auditable."""

    options = ProjectExportOptions(
        name="production",
        include_duration_validation=True,
        include_continuity_validation=True,
    )

    manifest = build_project_export_manifest(
        options,
        included_sections=[
            "project",
            "timeline",
            "workflow",
        ],
        omission_reasons={
            "duration_validation": (
                "missing_duration_policy"
            ),
            "continuity-validation": (
                "missing_continuity_profile"
            ),
        },
    )

    reasons = {
        item.section_id: item.reason
        for item in manifest.omitted_sections
    }

    assert (
        reasons[
            "duration_validation"
        ]
        == "missing_duration_policy"
    )

    assert (
        reasons[
            "continuity_validation"
        ]
        == "missing_continuity_profile"
    )


def test_manifest_reports_active_optional_systems():
    """Only actually included optional systems should be active."""

    options = ProjectExportOptions(
        name="full",
        include_duration_validation=True,
        include_global_constraints=True,
        include_structured_prompts=True,
    )

    manifest = build_project_export_manifest(
        options,
        included_sections=[
            "project",
            "timeline",
            "workflow",
            "duration_validation",
            "global_constraints",
            "structured_prompts",
        ],
    )

    assert (
        manifest.active_optional_systems
        == [
            "duration_validation",
            "global_constraints",
            "structured_prompts",
        ]
    )


def test_manifest_preserves_export_configuration():
    """Completed manifest should contain the reusable options."""

    options = ProjectExportOptions(
        name="portable-production",
        include_global_constraints=True,
        include_prompt_profile=True,
    )

    manifest = build_project_export_manifest(
        options,
        included_sections=[
            "project",
            "timeline",
            "workflow",
            "global_constraints",
            "prompt_profile",
        ],
    )

    assert (
        manifest.configuration
        == options.to_dict()
    )


def test_manifest_serialization():
    """Completed manifest should be JSON serializable."""

    options = ProjectExportOptions(
        name="portable",
        include_structured_prompts=True,
    )

    manifest = build_project_export_manifest(
        options,
        included_sections=[
            "project",
            "timeline",
            "workflow",
            "structured_prompts",
        ],
    )

    data = manifest.to_dict()

    assert (
        data["summary"]["valid"]
        is True
    )

    assert (
        data["summary"]["export_name"]
        == "portable"
    )

    assert (
        data["summary"]["section_count"]
        == 4
    )

    assert (
        data["summary"][
            "active_optional_system_count"
        ]
        == 1
    )

    assert (
        data["active_optional_systems"]
        == [
            "structured_prompts",
        ]
    )

    json.dumps(
        data,
        ensure_ascii=False,
    )


def test_manifest_serialization_does_not_expose_configuration():
    """
    Mutating serialized manifest configuration should not mutate
    the manifest itself.
    """

    options = ProjectExportOptions(
        name="portable",
    )

    manifest = build_project_export_manifest(
        options,
        included_sections=[
            "project",
            "timeline",
            "workflow",
        ],
    )

    data = manifest.to_dict()

    data["configuration"][
        "name"
    ] = "changed"

    assert (
        manifest.configuration["name"]
        == "portable"
    )


def test_manifest_rejects_missing_project_section():
    """Every completed project export must contain project data."""

    options = ProjectExportOptions(
        name="invalid",
    )

    with pytest.raises(
        ValueError,
        match=(
            "included_sections must contain "
            "the project section"
        ),
    ):
        build_project_export_manifest(
            options,
            included_sections=[
                "timeline",
                "workflow",
            ],
        )


def test_manifest_rejects_unknown_included_section():
    """Unknown provider-specific sections cannot enter core export."""

    options = ProjectExportOptions(
        name="invalid",
    )

    with pytest.raises(
        ValueError,
        match=(
            "Unknown included export sections"
        ),
    ):
        build_project_export_manifest(
            options,
            included_sections=[
                "project",
                "wan_payload",
            ],
        )


def test_manifest_rejects_duplicate_included_sections():
    """Included section declarations must remain unique."""

    options = ProjectExportOptions(
        name="invalid",
    )

    with pytest.raises(
        ValueError,
        match=(
            "included_sections cannot contain "
            "duplicates"
        ),
    ):
        build_project_export_manifest(
            options,
            included_sections=[
                "project",
                "timeline",
                "timeline",
            ],
        )


def test_manifest_rejects_unknown_omission_reason_section():
    """Omission reasons may reference canonical sections only."""

    options = ProjectExportOptions(
        name="invalid",
    )

    with pytest.raises(
        ValueError,
        match=(
            "Unknown omission reason sections"
        ),
    ):
        build_project_export_manifest(
            options,
            included_sections=[
                "project",
                "timeline",
                "workflow",
            ],
            omission_reasons={
                "wan_payload": (
                    "provider_specific"
                ),
            },
        )


def test_manifest_rejects_invalid_options():
    """Manifest construction should validate ProjectExportOptions."""

    options = ProjectExportOptions(
        name="invalid",
        include_empty_prompt_sections=True,
        include_structured_prompts=False,
    )

    with pytest.raises(
        ValueError,
        match=(
            "Invalid project export options"
        ),
    ):
        build_project_export_manifest(
            options,
            included_sections=[
                "project",
            ],
        )


def test_direct_manifest_rejects_duplicate_sections():
    """Direct manifests cannot contain duplicate included IDs."""

    manifest = ProjectExportManifest(
        export_name="invalid",
        included_sections=[
            "project",
            "timeline",
            "timeline",
        ],
    )

    assert manifest.is_valid is False

    assert any(
        "duplicate included sections"
        in error
        for error in manifest.validate()
    )


def test_direct_manifest_rejects_noncanonical_order():
    """Direct manifest construction must preserve canonical order."""

    manifest = ProjectExportManifest(
        export_name="invalid",
        included_sections=[
            "project",
            "workflow",
            "timeline",
        ],
    )

    assert manifest.is_valid is False

    assert any(
        "deterministic canonical ordering"
        in error
        for error in manifest.validate()
    )


def test_direct_manifest_rejects_included_omitted_overlap():
    """One section cannot simultaneously be included and omitted."""

    manifest = ProjectExportManifest(
        export_name="invalid",
        included_sections=[
            "project",
            "timeline",
        ],
        omitted_sections=[
            OmittedExportSection(
                section_id="timeline",
                reason="example",
            ),
        ],
    )

    assert manifest.is_valid is False

    assert any(
        "both included and omitted"
        in error
        for error in manifest.validate()
    )


def test_direct_manifest_rejects_duplicate_omissions():
    """Omitted sections should also remain unique."""

    manifest = ProjectExportManifest(
        export_name="invalid",
        included_sections=[
            "project",
        ],
        omitted_sections=[
            OmittedExportSection(
                section_id="timeline",
                reason="not_requested",
            ),
            OmittedExportSection(
                section_id="timeline",
                reason="missing_data",
            ),
        ],
    )

    assert manifest.is_valid is False

    assert any(
        "duplicate omitted sections"
        in error
        for error in manifest.validate()
    )


def test_manifest_name_is_required():
    """Completed manifest requires a readable export name."""

    manifest = ProjectExportManifest(
        export_name="   ",
        included_sections=[
            "project",
        ],
    )

    assert manifest.is_valid is False

    assert (
        "project export manifest name "
        "cannot be empty"
        in manifest.validate()
    )
