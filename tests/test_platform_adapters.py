import json

import pytest

from ai_cinematic_workflow.scene import (
    Camera,
    Scene,
)
from ai_cinematic_workflow.structured_prompts import (
    STRUCTURED_PROMPT_SECTION_ORDER,
    assemble_structured_prompt,
)
from ai_cinematic_workflow.platform_adapters import (
    PlatformAdapter,
    PlatformAdapterCapabilities,
    PlatformAdapterIssue,
    PlatformAdapterRegistry,
    PlatformAdapterResult,
    normalize_platform_identifier,
)


def make_scene(
    scene_id: int = 1,
) -> Scene:
    """Create a reusable valid cinematic Scene."""

    return Scene(
        scene_id=scene_id,
        duration_seconds=15,
        location="Rooftop at night",
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
            "Song lyrics"
        ),
        continuity={
            "wardrobe": (
                "black cinematic outfit"
            ),
            "hair": "long dark hair",
        },
        negative_constraints=[
            "distorted face",
            "text artifacts",
        ],
    )


def make_source(
    scene_id: int = 1,
):
    """Create a reusable StructuredPromptResult."""

    return assemble_structured_prompt(
        make_scene(
            scene_id
        )
    )


def make_adapter(
    *,
    platform_id: str = "Example Video Platform",
    display_name: str = "Example Video Platform",
    supported_sections: list[str] | None = None,
    supports_structured_prompt_input: bool = True,
    supports_enhanced_project_export: bool = False,
    supports_section_metadata: bool = True,
) -> PlatformAdapter:
    """Create a reusable provider-neutral PlatformAdapter."""

    capabilities = PlatformAdapterCapabilities(
        supported_prompt_sections=(
            supported_sections
            if supported_sections is not None
            else list(
                STRUCTURED_PROMPT_SECTION_ORDER
            )
        ),
        supports_structured_prompt_input=(
            supports_structured_prompt_input
        ),
        supports_enhanced_project_export=(
            supports_enhanced_project_export
        ),
        supports_section_metadata=(
            supports_section_metadata
        ),
    )

    return PlatformAdapter(
        platform_id=platform_id,
        display_name=display_name,
        adapter_version="1.0",
        capabilities=capabilities,
        metadata={
            "category": "video_generation",
        },
    )


def test_normalize_platform_identifier():
    """Platform identifiers should normalize canonically."""

    assert (
        normalize_platform_identifier(
            "Example Video Platform"
        )
        == "example_video_platform"
    )

    assert (
        normalize_platform_identifier(
            "example-video-platform"
        )
        == "example_video_platform"
    )

    assert (
        normalize_platform_identifier(
            "  Example   Video Platform  "
        )
        == "example_video_platform"
    )


def test_default_capabilities_support_all_prompt_sections():
    """
    Default base capabilities should accept every canonical
    Structured Prompt Section.
    """

    capabilities = (
        PlatformAdapterCapabilities()
    )

    assert capabilities.is_valid

    assert (
        capabilities.normalized_prompt_sections
        == list(
            STRUCTURED_PROMPT_SECTION_ORDER
        )
    )

    assert (
        capabilities.supports_structured_prompt_input
        is True
    )

    assert (
        capabilities.supports_enhanced_project_export
        is False
    )

    assert (
        capabilities.supports_section_metadata
        is True
    )


def test_capability_sections_are_canonically_ordered():
    """Capability serialization should use canonical section order."""

    capabilities = PlatformAdapterCapabilities(
        supported_prompt_sections=[
            "negative_constraints",
            "camera",
            "characters",
            "location",
        ],
    )

    assert (
        capabilities.normalized_prompt_sections
        == [
            "characters",
            "location",
            "camera",
            "negative_constraints",
        ]
    )


def test_capability_section_lookup_normalizes_name():
    """Capability lookup should accept formatted section names."""

    capabilities = PlatformAdapterCapabilities(
        supported_prompt_sections=[
            "camera",
            "negative_constraints",
        ],
    )

    assert (
        capabilities.supports_section(
            "Camera"
        )
        is True
    )

    assert (
        capabilities.supports_section(
            "negative-constraints"
        )
        is True
    )

    assert (
        capabilities.supports_section(
            "continuity"
        )
        is False
    )


def test_duplicate_capability_sections_are_invalid():
    """Normalized duplicate capability declarations are rejected."""

    capabilities = PlatformAdapterCapabilities(
        supported_prompt_sections=[
            "camera",
            "Camera",
        ],
    )

    assert capabilities.is_valid is False

    assert any(
        "cannot contain duplicates"
        in error
        for error in capabilities.validate()
    )


def test_unknown_capability_section_is_invalid():
    """Unknown provider-specific sections cannot enter core registry."""

    capabilities = PlatformAdapterCapabilities(
        supported_prompt_sections=[
            "camera",
            "provider_magic_mode",
        ],
    )

    assert capabilities.is_valid is False

    assert any(
        "unknown supported prompt section"
        in error
        for error in capabilities.validate()
    )


def test_custom_capabilities_must_be_json_serializable():
    """Custom adapter capability metadata must remain portable."""

    capabilities = PlatformAdapterCapabilities(
        custom_capabilities={
            "invalid": {
                "set-value",
            },
        },
    )

    assert capabilities.is_valid is False

    assert any(
        "custom adapter capabilities "
        "must be JSON serializable"
        in error
        for error in capabilities.validate()
    )


def test_capability_serialization():
    """Capability declarations should serialize cleanly."""

    capabilities = PlatformAdapterCapabilities(
        supported_prompt_sections=[
            "camera",
            "lighting",
        ],
        supports_structured_prompt_input=True,
        supports_enhanced_project_export=True,
        supports_section_metadata=False,
        custom_capabilities={
            "max_sections": 2,
        },
    )

    data = capabilities.to_dict()

    assert (
        data[
            "supported_prompt_sections"
        ]
        == [
            "camera",
            "lighting",
        ]
    )

    assert (
        data[
            "supports_enhanced_project_export"
        ]
        is True
    )

    assert (
        data[
            "supports_section_metadata"
        ]
        is False
    )

    assert (
        data[
            "custom_capabilities"
        ]["max_sections"]
        == 2
    )

    json.dumps(
        data,
        ensure_ascii=False,
    )


def test_platform_adapter_issue_is_valid():
    """Structured adapter warnings should validate."""

    issue = PlatformAdapterIssue(
        issue_type=(
            "unsupported_prompt_section"
        ),
        severity="warning",
        message=(
            "Continuity is unsupported"
        ),
        feature="continuity",
        section_id="continuity",
    )

    assert issue.is_valid
    assert issue.validate() == []


def test_platform_adapter_issue_serialization_normalizes_values():
    """Issue serialization should normalize severity and section ID."""

    issue = PlatformAdapterIssue(
        issue_type="example",
        severity=" WARNING ",
        message="Example warning",
        section_id="Negative Constraints",
    )

    data = issue.to_dict()

    assert (
        data["severity"]
        == "warning"
    )

    assert (
        data["section_id"]
        == "negative_constraints"
    )


def test_platform_adapter_issue_rejects_invalid_severity():
    """Only warning and error severities are supported."""

    issue = PlatformAdapterIssue(
        issue_type="example",
        severity="info",
        message="Example",
    )

    assert issue.is_valid is False

    assert any(
        "must be warning or error"
        in error
        for error in issue.validate()
    )


def test_platform_adapter_issue_rejects_unknown_section():
    """Issues may reference canonical prompt sections only."""

    issue = PlatformAdapterIssue(
        issue_type="example",
        severity="warning",
        message="Example",
        section_id="provider_magic_mode",
    )

    assert issue.is_valid is False

    assert any(
        "unknown platform adapter issue section"
        in error
        for error in issue.validate()
    )


def test_platform_adapter_identity_is_normalized():
    """Base adapter should expose canonical platform identity."""

    adapter = make_adapter(
        platform_id=(
            "Example Video Platform"
        ),
    )

    assert adapter.is_valid

    assert (
        adapter.canonical_platform_id
        == "example_video_platform"
    )

    assert (
        adapter.to_dict()[
            "platform_id"
        ]
        == "example_video_platform"
    )


def test_platform_adapter_requires_identity_metadata():
    """Adapter identity fields cannot be blank."""

    adapter = PlatformAdapter(
        platform_id="   ",
        display_name="   ",
        adapter_version="   ",
    )

    errors = adapter.validate()

    assert adapter.is_valid is False

    assert any(
        "platform ID cannot be empty"
        in error
        for error in errors
    )

    assert any(
        "display name cannot be empty"
        in error
        for error in errors
    )

    assert any(
        "version cannot be empty"
        in error
        for error in errors
    )


def test_platform_adapter_rejects_invalid_capabilities():
    """Invalid capability declarations invalidate the adapter."""

    adapter = PlatformAdapter(
        platform_id="example",
        display_name="Example",
        capabilities=(
            PlatformAdapterCapabilities(
                supported_prompt_sections=[
                    "provider_magic_mode",
                ],
            )
        ),
    )

    assert adapter.is_valid is False

    assert any(
        "capabilities:"
        in error
        for error in adapter.validate()
    )


def test_platform_adapter_metadata_must_be_json_serializable():
    """Adapter metadata must remain portable."""

    adapter = PlatformAdapter(
        platform_id="example",
        display_name="Example",
        metadata={
            "invalid": {
                "set-value",
            },
        },
    )

    assert adapter.is_valid is False

    assert any(
        "platform adapter metadata "
        "must be JSON serializable"
        in error
        for error in adapter.validate()
    )


def test_adapter_filters_supported_and_unsupported_sections():
    """
    StructuredPromptResult sections should be filtered using
    declared platform capabilities.
    """

    adapter = make_adapter(
        supported_sections=[
            "characters",
            "location",
            "camera",
            "performance",
            "lighting",
            "negative_constraints",
        ],
    )

    result = adapter.adapt_structured_prompt(
        make_source()
    )

    assert result.is_valid

    assert (
        result.supported_features
        == [
            "characters",
            "location",
            "camera",
            "performance",
            "lighting",
            "negative_constraints",
        ]
    )

    assert (
        result.unsupported_features
        == [
            "mood",
            "dialogue_or_vocals",
            "continuity",
        ]
    )

    assert (
        result.warning_count
        == 3
    )

    assert (
        result.error_count
        == 0
    )


def test_unsupported_sections_create_structured_warnings():
    """Unsupported sections should never disappear silently."""

    adapter = make_adapter(
        supported_sections=[
            "camera",
        ],
    )

    result = adapter.adapt_structured_prompt(
        make_source()
    )

    continuity_issue = next(
        issue
        for issue in result.issues
        if (
            issue.section_id
            == "continuity"
        )
    )

    assert (
        continuity_issue.issue_type
        == "unsupported_prompt_section"
    )

    assert (
        continuity_issue.severity
        == "warning"
    )

    assert (
        continuity_issue.feature
        == "continuity"
    )


def test_adapted_payload_preserves_supported_section_order():
    """Adapted payload sections should retain canonical order."""

    adapter = make_adapter(
        supported_sections=[
            "negative_constraints",
            "camera",
            "characters",
        ],
    )

    result = adapter.adapt_structured_prompt(
        make_source()
    )

    section_ids = [
        section["section_id"]
        for section in result.payload[
            "sections"
        ]
    ]

    assert (
        section_ids
        == [
            "characters",
            "camera",
            "negative_constraints",
        ]
    )


def test_adapter_can_strip_section_metadata():
    """
    Capability declarations should control whether source
    section metadata is propagated.
    """

    adapter = make_adapter(
        supported_sections=[
            "camera",
        ],
        supports_section_metadata=False,
    )

    result = adapter.adapt_structured_prompt(
        make_source()
    )

    assert (
        len(
            result.payload[
                "sections"
            ]
        )
        == 1
    )

    assert (
        result.payload[
            "sections"
        ][0]["metadata"]
        == {}
    )


def test_adapter_preserves_section_metadata_when_supported():
    """Supported metadata should remain available by default."""

    adapter = make_adapter(
        supported_sections=[
            "camera",
        ],
        supports_section_metadata=True,
    )

    result = adapter.adapt_structured_prompt(
        make_source()
    )

    metadata = result.payload[
        "sections"
    ][0]["metadata"]

    assert (
        metadata["component"]
        == "camera"
    )

    assert (
        metadata["source"]
        == "scene"
    )


def test_adapter_can_reject_structured_prompt_input():
    """
    Adapters that do not support StructuredPromptResult should
    return an error-level result rather than silently adapting it.
    """

    adapter = make_adapter(
        supports_structured_prompt_input=False,
    )

    result = adapter.adapt_structured_prompt(
        make_source()
    )

    assert result.is_valid is False

    assert (
        result.error_count
        == 1
    )

    assert (
        result.warning_count
        == 0
    )

    assert (
        result.unsupported_features
        == [
            "structured_prompt_input",
        ]
    )

    assert (
        result.payload[
            "sections"
        ]
        == []
    )

    assert (
        result.issues[0].issue_type
        == "unsupported_input_type"
    )


def test_adapter_result_serialization():
    """Adapter results should remain JSON serializable."""

    adapter = make_adapter(
        supported_sections=[
            "characters",
            "camera",
        ],
    )

    result = adapter.adapt_structured_prompt(
        make_source()
    )

    data = result.to_dict()

    assert (
        data["summary"]["valid"]
        is True
    )

    assert (
        data["platform_id"]
        == "example_video_platform"
    )

    assert (
        data["adapter_name"]
        == "Example Video Platform"
    )

    assert (
        data["adapter_version"]
        == "1.0"
    )

    assert (
        data["summary"][
            "supported_feature_count"
        ]
        == 2
    )

    json.dumps(
        data,
        ensure_ascii=False,
    )


def test_platform_adapter_result_detects_feature_overlap():
    """A feature cannot be both supported and unsupported."""

    result = PlatformAdapterResult(
        platform_id="example",
        adapter_name="Example",
        adapter_version="1.0",
        supported_features=[
            "camera",
        ],
        unsupported_features=[
            "camera",
        ],
    )

    assert result.is_valid is False

    assert any(
        "both supported and unsupported"
        in error
        for error in result.validate()
    )


def test_adapter_does_not_mutate_structured_prompt_source():
    """Platform adaptation must not mutate its source result."""

    source = make_source()

    before = source.to_dict()

    adapter = make_adapter(
        supported_sections=[
            "camera",
            "lighting",
        ],
        supports_section_metadata=False,
    )

    adapter.adapt_structured_prompt(
        source
    )

    assert (
        source.to_dict()
        == before
    )


def test_provider_specific_subclass_boundary_is_extensible():
    """
    Provider-specific implementations should be able to extend
    the common PlatformAdapter contract.
    """

    class ExampleProviderAdapter(
        PlatformAdapter
    ):
        pass

    adapter = ExampleProviderAdapter(
        platform_id="example-provider",
        display_name="Example Provider",
        capabilities=(
            PlatformAdapterCapabilities(
                supported_prompt_sections=[
                    "camera",
                ],
            )
        ),
    )

    assert isinstance(
        adapter,
        PlatformAdapter,
    )

    assert adapter.is_valid

    result = (
        adapter.adapt_structured_prompt(
            make_source()
        )
    )

    assert (
        result.platform_id
        == "example_provider"
    )


def test_registry_registers_and_normalizes_lookup():
    """Registry lookup should accept human-formatted identifiers."""

    registry = (
        PlatformAdapterRegistry()
    )

    adapter = make_adapter()

    registry.register(
        adapter
    )

    assert (
        registry.contains(
            "Example Video Platform"
        )
        is True
    )

    assert (
        registry.contains(
            "example-video-platform"
        )
        is True
    )

    assert (
        registry.get(
            "example_video_platform"
        )
        is adapter
    )


def test_registry_rejects_duplicate_canonical_platform_id():
    """
    Different input formatting must not allow duplicate
    canonical platform registrations.
    """

    registry = (
        PlatformAdapterRegistry()
    )

    registry.register(
        make_adapter(
            platform_id=(
                "Example Video Platform"
            ),
        )
    )

    duplicate = make_adapter(
        platform_id=(
            "example-video-platform"
        ),
        display_name=(
            "Duplicate Example"
        ),
    )

    with pytest.raises(
        ValueError,
        match=(
            "Platform adapter already registered"
        ),
    ):
        registry.register(
            duplicate
        )


def test_registry_rejects_invalid_adapter():
    """Invalid adapters cannot enter the registry."""

    registry = (
        PlatformAdapterRegistry()
    )

    invalid = PlatformAdapter(
        platform_id="   ",
        display_name="Invalid",
    )

    with pytest.raises(
        ValueError,
        match=(
            "Invalid platform adapter"
        ),
    ):
        registry.register(
            invalid
        )


def test_registry_unknown_adapter_handling():
    """Unknown platform lookup should fail explicitly."""

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
            "missing-platform"
        )


def test_registry_platform_ids_are_deterministic():
    """Registered platform IDs should be listed deterministically."""

    registry = (
        PlatformAdapterRegistry()
    )

    registry.register(
        make_adapter(
            platform_id="Zulu Platform",
            display_name="Zulu Platform",
        )
    )

    registry.register(
        make_adapter(
            platform_id="Alpha Platform",
            display_name="Alpha Platform",
        )
    )

    assert (
        registry.platform_ids
        == [
            "alpha_platform",
            "zulu_platform",
        ]
    )


def test_registry_serialization():
    """Adapter registry metadata should be portable."""

    registry = (
        PlatformAdapterRegistry()
    )

    registry.register(
        make_adapter(
            platform_id="Beta Platform",
            display_name="Beta Platform",
        )
    )

    registry.register(
        make_adapter(
            platform_id="Alpha Platform",
            display_name="Alpha Platform",
        )
    )

    data = registry.to_dict()

    assert (
        data["summary"][
            "adapter_count"
        ]
        == 2
    )

    assert (
        data["platform_ids"]
        == [
            "alpha_platform",
            "beta_platform",
        ]
    )

    assert [
        item["platform_id"]
        for item in data[
            "adapters"
        ]
    ] == [
        "alpha_platform",
        "beta_platform",
    ]

    json.dumps(
        data,
        ensure_ascii=False,
    )


def test_enhanced_project_export_capability_is_declarative():
    """
    Enhanced Project Export support should be declared without
    inventing provider-specific behavior in the base adapter.
    """

    adapter = make_adapter(
        supports_enhanced_project_export=True,
    )

    data = adapter.to_dict()

    assert (
        data["capabilities"][
            "supports_enhanced_project_export"
        ]
        is True
    )

    assert (
        "wan_payload"
        not in data
    )

    assert (
        "veo_payload"
        not in data
    )

    assert (
        "kling_payload"
        not in data
    )
