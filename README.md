# AI Cinematic Workflow Toolkit

[![Python Tests](https://github.com/XtolNguyen/ai-cinematic-workflow-toolkit/actions/workflows/tests.yml/badge.svg)](https://github.com/XtolNguyen/ai-cinematic-workflow-toolkit/actions/workflows/tests.yml)
[![Release](https://img.shields.io/github/v/release/XtolNguyen/ai-cinematic-workflow-toolkit)](https://github.com/XtolNguyen/ai-cinematic-workflow-toolkit/releases)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/github/license/XtolNguyen/ai-cinematic-workflow-toolkit)](LICENSE)

**AI Cinematic Workflow Toolkit** is an open-source Python toolkit for structuring, validating, organizing, and exporting AI-assisted cinematic production workflows.

It provides reusable models and validation layers for cinematic scenes, music-video structure, timeline planning, lip-sync policy, duration rules, continuity, global production constraints, prompt profiles, structured prompts, portable project export, and provider-neutral platform adaptation.

The project is designed for creators, filmmakers, developers, researchers, and workflow designers building transparent and reproducible AI-video production pipelines.

---

## Project Status

**Current released version:** `v0.2.0`

**Current milestone:** `v0.2.0 — Cinematic Timeline & Music Video Foundation`

**v0.2.0 status:** Released

The v0.2.0 milestone has completed its defined implementation, testing, runnable-example, and documentation scope.

Version `0.2.0` is the current released software state of the toolkit.

The package metadata is synchronized at version `0.2.0`.

The v0.2.0 release remains provider-neutral and includes the completed cinematic timeline, music-video, validation, structured prompt, enhanced export, Platform Adapter foundation, runnable-example, and documentation work defined by the milestone.

Concrete provider-specific WAN, Veo, Kling, and other production adapters remain future work.

The project is developed publicly and incrementally through source code, issues, automated tests, documentation, roadmap updates, and releases.

---

## What the Toolkit Does

AI-assisted cinematic production often requires multiple connected stages:

```text
Creative Input
      ↓
Scene Planning
      ↓
Timeline Planning
      ↓
Music / Performance Structure
      ↓
Lip-Sync Policy
      ↓
Duration Validation
      ↓
Continuity Validation
      ↓
Global Production Constraints
      ↓
Prompt Profiles
      ↓
Structured Prompt Sections
      ↓
Portable Project Export
      ↓
Platform Adapter Layer
      ↓
Future Provider-Specific Integrations
```

The toolkit focuses on making these stages:

**Structured · Reproducible · Portable · Transparent · Creator-friendly**

---

# Installation

## Requirements

* Python 3.10 or newer
* Git
* pip

Clone the repository:

```bash
git clone https://github.com/XtolNguyen/ai-cinematic-workflow-toolkit.git
cd ai-cinematic-workflow-toolkit
```

Create a virtual environment:

```bash
python -m venv .venv
```

### Windows

```bash
.venv\Scripts\activate
```

### macOS / Linux

```bash
source .venv/bin/activate
```

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

Install the toolkit:

```bash
python -m pip install -e .
```

For development and testing:

```bash
python -m pip install -e ".[dev]"
```

---

# Quick Start

Create and process a cinematic scene using the public package API:

```python
from ai_cinematic_workflow import (
    Camera,
    Scene,
    process_scene,
)

scene = Scene(
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
        "Natural emotional performance"
    ),
    lighting=(
        "Soft cinematic lighting"
    ),
    mood="Reflective",
    negative_constraints=[
        "Distorted Face",
        "Extra Fingers",
        "Camera Jitter",
    ],
)

result = process_scene(scene)

print(result.prompt)
print(result.negative_prompt)
```

The basic scene workflow performs:

```text
Scene
  ↓
Scene Validation
  ↓
Negative Constraint Normalization
  ↓
Cinematic Prompt Generation
  ↓
WorkflowSceneResult
```

---

# Multi-Scene Cinematic Projects

A complete cinematic production can contain multiple ordered scenes.

```python
from ai_cinematic_workflow import (
    Camera,
    CinematicProject,
    ProjectMetadata,
    Scene,
    process_project,
)

project = CinematicProject(
    metadata=ProjectMetadata(
        title="Demo Project",
        project_type="cinematic",
        language="en",
        aspect_ratio="16:9",
        frame_rate=24,
    ),
    scenes=[
        Scene(
            scene_id=1,
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
            continuity={
                "wardrobe": "black outfit",
            },
        ),
        Scene(
            scene_id=2,
            duration_seconds=15,
            location="Performance stage",
            camera=Camera(
                shot="close-up",
                movement="slow push in",
                lens="85mm",
            ),
            characters=[
                "Lead performer",
            ],
            continuity={
                "wardrobe": "black outfit",
            },
        ),
    ],
)

results = process_project(
    project.scenes
)

for result in results:
    print(
        result.scene_id,
        result.valid,
        result.prompt,
    )
```

The workflow engine preserves ordered scene processing and reports potential continuity changes between consecutive scenes.

---

# v0.2.0 Architecture

The current development architecture extends the original scene workflow into a complete provider-neutral cinematic production pipeline.

```text
CinematicProject
       ↓
Cinematic Timeline
       ↓
Music Video Structure
       ↓
Performance Mode
       ↓
Lip-Sync Policy
       ↓
DurationPolicy
       ↓
ContinuityProfile
       ↓
GlobalConstraints
       ↓
PromptProfile
       ↓
StructuredPromptResult
       ↓
Enhanced Project Export
       ↓
Platform Adapter Foundation
       ↓
Future Provider-Specific Adapters
```

Each layer is designed to have a focused responsibility and to remain inspectable and testable.

---

# Cinematic Timeline

The Timeline Planner converts ordered scenes into deterministic production timing.

```python
from ai_cinematic_workflow import (
    build_timeline,
    format_timestamp,
)

timeline = build_timeline(
    project.scenes
)

for entry in timeline.entries:
    print(
        entry.scene_id,
        format_timestamp(
            entry.start_seconds
        ),
        format_timestamp(
            entry.end_seconds
        ),
    )
```

Conceptually:

```text
Scene 01
15 seconds
    ↓
00:00 → 00:15

Scene 02
15 seconds
    ↓
00:15 → 00:30

Scene 03
15 seconds
    ↓
00:30 → 00:45
```

The Timeline layer supports ordered scene timing, cumulative duration, timeline validation, gap detection, overlap detection, duplicate scene-ID detection, and serializable timeline reports.

---

# Music Video Structure

Music-video projects can define explicit musical sections and map scenes to those sections.

```python
from ai_cinematic_workflow import (
    MusicSection,
    MusicVideoStructure,
)

music_structure = MusicVideoStructure(
    sections=[
        MusicSection(
            section_id=1,
            section_type="intro",
            start_seconds=0,
            end_seconds=15,
            performance_mode="cinematic-only",
            scene_ids=[1],
            label="Intro",
        ),
        MusicSection(
            section_id=2,
            section_type="verse",
            start_seconds=15,
            end_seconds=30,
            performance_mode="vocal",
            scene_ids=[2],
            label="Verse",
        ),
        MusicSection(
            section_id=3,
            section_type="instrumental",
            start_seconds=30,
            end_seconds=45,
            performance_mode="instrumental",
            scene_ids=[3],
            label="Instrumental",
        ),
    ]
)
```

Supported workflow concepts include musical sections such as:

```text
intro
verse
pre-chorus
chorus
instrumental
bridge
breakdown
final chorus
outro
```

The structure supports scene mapping, chronological validation, duration validation, overlap detection, duplicate mapping detection, and project-scene validation.

---

# Vocal and Instrumental Performance Modes

The toolkit distinguishes performance state from simple scene content.

Structured performance modes include:

```text
vocal
instrumental
dialogue
performance-only
cinematic-only
```

This allows downstream workflow logic to distinguish scenes that require visible vocal performance from scenes where singing mouth movement should not occur.

---

# Lip-Sync Policy

The Lip-Sync Policy Engine resolves lip-sync behavior from structured music-video performance metadata.

```python
from ai_cinematic_workflow import (
    resolve_music_video_lip_sync,
)

policies = (
    resolve_music_video_lip_sync(
        music_structure
    )
)

for policy in policies:
    print(
        policy.section_id,
        policy.performance_mode,
        policy.lip_sync_required,
        policy.lip_sync_mode,
    )
```

Typical policy behavior:

```text
VOCAL
→ lip-sync required

INSTRUMENTAL
→ lip-sync disabled

CINEMATIC-ONLY
→ lip-sync disabled

PERFORMANCE-ONLY
→ no automatic singing requirement
```

The core toolkit resolves and validates lip-sync policy but does not perform video generation.

Provider-specific translation belongs to future provider adapters.

---

# DurationPolicy

Scene duration rules are represented through a reusable `DurationPolicy`.

```python
from ai_cinematic_workflow import (
    DurationPolicy,
)

duration_policy = DurationPolicy(
    preferred_scene_duration=15,
    minimum_scene_duration=15,
    maximum_scene_duration=15,
    allowed_scene_durations=[
        15,
    ],
    tolerance_seconds=0,
    strict=True,
)
```

Duration policies can define:

* Preferred duration
* Minimum duration
* Maximum duration
* Allowed durations
* Tolerance
* Strict or advisory enforcement

For music-video projects:

```python
from ai_cinematic_workflow import (
    validate_music_video_timing,
)

timing_result = (
    validate_music_video_timing(
        project.scenes,
        music_structure,
        duration_policy,
    )
)

print(
    timing_result.is_valid
)
```

Music-video timing validation compares scene timing with structured music sections before downstream production.

---

# Advanced Continuity

The toolkit contains both the original lightweight continuity API and an advanced configurable continuity layer.

A `ContinuityProfile` controls how selected fields are treated.

```python
from ai_cinematic_workflow import (
    ContinuityProfile,
    validate_project_continuity,
)

continuity_profile = ContinuityProfile(
    name="production-continuity",
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

continuity_result = (
    validate_project_continuity(
        project.scenes,
        continuity_profile,
    )
)

print(
    continuity_result.is_valid
)

print(
    continuity_result.error_count
)

print(
    continuity_result.warning_count
)
```

Advanced continuity supports concepts such as:

```text
required fields
optional fields
ignored fields
strict fields
warning-only fields
allowed intentional changes
native Scene fields
custom continuity metadata
```

Creative transitions do not have to be treated as hard errors.

---

# GlobalConstraints

Project-wide cinematic constraints can be represented once and resolved together with scene-level constraints.

```python
from ai_cinematic_workflow import (
    GlobalConstraints,
    resolve_project_constraints,
)

constraints = GlobalConstraints(
    name="cinematic-production",
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

resolution = (
    resolve_project_constraints(
        project.scenes,
        constraints,
    )
)
```

Conceptual resolution:

```text
Global Constraints
        +
Scene Constraints
        ↓
Normalization
        ↓
Deduplication
        ↓
Resolved Scene Constraints
```

Constraint resolution is designed to avoid mutating the source scene data.

---

# PromptProfile

Reusable Prompt Profiles control which cinematic prompt components are active.

```python
from ai_cinematic_workflow import (
    PromptProfile,
    resolve_prompt_profile,
)

profile = PromptProfile(
    name="cinematic-profile",
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

resolved_profile = (
    resolve_prompt_profile(
        profile
    )
)
```

Canonical prompt components include:

```text
characters
location
camera
performance
lighting
mood
dialogue_or_vocals
continuity
global_constraints
negative_constraints
```

Prompt Profiles support reusable configuration, inheritance, runtime component overrides, validation, and non-mutating resolution.

---

# Structured Prompt Sections

The Structured Prompt layer converts scene information into explicit reusable components.

```python
from ai_cinematic_workflow import (
    assemble_structured_prompt,
)

structured = (
    assemble_structured_prompt(
        project.scenes[0],
        prompt_profile=resolved_profile,
        global_constraints=constraints,
    )
)

print(
    structured.included_components
)

for section in structured.sections:
    print(
        section.section_id,
        section.content,
    )
```

Canonical Structured Prompt Sections are:

```text
characters
location
camera
performance
lighting
mood
dialogue_or_vocals
continuity
global_constraints
negative_constraints
```

The structured prompt system provides:

* Deterministic section ordering
* Included-component reporting
* Omitted-component reporting
* Empty-component handling
* PromptProfile control
* GlobalConstraints integration
* Resolved negative constraints
* Structured metadata
* JSON-serializable results
* Non-mutating assembly

The original `build_cinematic_prompt()` API remains available.

---

# Enhanced Project Export

The toolkit supports both legacy project export and a configurable Enhanced Project Export.

Enhanced export uses `ProjectExportOptions` to select project layers.

```python
from ai_cinematic_workflow import (
    ProjectExportOptions,
)

from ai_cinematic_workflow.exporters.project_json_exporter import (
    project_to_dict,
)

options = ProjectExportOptions(
    name="portable-project",
    include_timeline=True,
    include_workflow=True,
    include_structured_prompts=True,
)

data = project_to_dict(
    project,
    export_options=options,
)

print(
    data[
        "manifest"
    ][
        "included_sections"
    ]
)
```

Enhanced export can control inclusion of:

```text
project
timeline
workflow
duration_validation
continuity_validation
global_constraints
prompt_profile
structured_prompts
```

The export manifest reports:

* Export configuration
* Included sections
* Omitted sections
* Omission reasons
* Active optional production systems
* Deterministic export structure

Conceptual enhanced package:

```text
Manifest
    ↓
Project
    ↓
Timeline
    ↓
Workflow
    ↓
Duration Validation
    ↓
Continuity Validation
    ↓
Global Constraints
    ↓
Prompt Profile
    ↓
Structured Prompts
```

Optional layers are controlled by `ProjectExportOptions` and available source data.

---

# JSON Persistence

Portable project output can be written directly to JSON.

```python
from ai_cinematic_workflow.exporters.project_json_exporter import (
    save_project_json,
)

save_project_json(
    project,
    "output/project.json",
    export_options=options,
)
```

The exporter remains provider-neutral.

Enhanced Project Export packages production information but does not perform provider-specific API translation or network execution.

---

# Platform Adapter Foundation

The v0.2.0 development architecture includes a provider-neutral Platform Adapter foundation.

It defines a clean boundary between structured cinematic data and future provider-specific integrations.

```python
from ai_cinematic_workflow import (
    PlatformAdapter,
    PlatformAdapterCapabilities,
    PlatformAdapterRegistry,
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

adapter_result = (
    resolved_adapter
    .adapt_structured_prompt(
        structured
    )
)

print(
    adapter_result.supported_features
)

print(
    adapter_result.unsupported_features
)
```

The Platform Adapter foundation provides:

```text
PlatformAdapter
PlatformAdapterCapabilities
PlatformAdapterIssue
PlatformAdapterResult
PlatformAdapterRegistry
canonical platform identifier normalization
capability declarations
supported-feature reporting
unsupported-feature reporting
structured warnings and errors
deterministic adapter results
JSON-serializable results
registry lookup
duplicate registration protection
unknown adapter handling
non-mutating adaptation
```

The base adapter layer remains provider-neutral.

---

# Provider Boundary

The current toolkit does **not** claim to contain production-ready provider-specific WAN, Veo, Kling, or other external AI-video adapters.

Current architecture:

```text
Core Cinematic Project
          ↓
Structured Prompt Sections
          ↓
Enhanced Project Export
          ↓
Platform Adapter Foundation
          ↓
Future Provider-Specific Adapters
```

Planned future production-adapter architecture:

```text
Platform Adapter Foundation
          ↓
 ┌────────┼─────────┐
 ↓        ↓         ↓
WAN      Veo       Kling
Adapter  Adapter    Adapter
```

Provider-specific adapters belong to future Production Adapters work.

The core toolkit does not require:

```text
provider API keys
provider credentials
network execution
undocumented provider parameters
```

This separation helps keep the core reusable across different production environments.

---

# Runnable v0.2.0 Music-Video Example

A complete provider-neutral end-to-end demonstration is included:

```bash
python examples/music_video_project.py
```

The example currently demonstrates:

* `CinematicProject`
* Three ordered cinematic scenes
* Multi-scene workflow processing
* Cinematic Timeline
* Music Video Structure
* Scene-to-music-section mapping
* Vocal and instrumental performance modes
* Lip-Sync Policy
* DurationPolicy
* Music-video timing validation
* ContinuityProfile
* GlobalConstraints
* PromptProfile
* Structured Prompt Sections
* Enhanced Project Export
* ProjectExportOptions
* ProjectExportManifest
* PlatformAdapter
* PlatformAdapterRegistry
* Supported and unsupported adapter reporting
* JSON persistence
* Provider-neutral execution

The demonstration project is named:

```text
Neon Echoes
```

It contains:

```text
3 scenes
15 seconds per scene
45 seconds total
```

Scene 3 intentionally changes wardrobe so the continuity systems have a visible continuity event to report.

Generated project output is written to:

```text
examples/output/music_video_project.json
```

The example requires no external AI-video API, API key, or network connection.

---

# Testing

Install development dependencies:

```bash
python -m pip install -e ".[dev]"
```

Run the complete test suite:

```bash
pytest -q
```

Run the runnable example directly:

```bash
python examples/music_video_project.py
```

The repository uses GitHub Actions to test:

```text
Python 3.10
Python 3.11
Python 3.12
Python 3.13
```

CI currently performs:

```text
Repository checkout
      ↓
Python setup
      ↓
Development installation
      ↓
pytest -q
      ↓
Runnable music-video example
      ↓
Generated JSON validation
```

Automated tests cover the implemented core behavior, including scene processing, timeline planning, music-video structure, lip-sync policy, duration validation, continuity, global constraints, prompt profiles, structured prompts, Enhanced Project Export, Platform Adapter foundation, and runnable-example behavior.

---

# Current Public API Areas

The public Python package exposes APIs for:

```text
Camera and Scene
CinematicProject and ProjectMetadata

Basic Continuity
Advanced Continuity
ContinuityProfile

DurationPolicy
Timeline

MusicSection
MusicVideoStructure
Music-video timing validation

Lip-Sync Policy

GlobalConstraints

PromptProfile
ResolvedPromptProfile

StructuredPromptSection
StructuredPromptResult

ProjectExportOptions
ProjectExportManifest
OmittedExportSection

PlatformAdapter
PlatformAdapterCapabilities
PlatformAdapterIssue
PlatformAdapterResult
PlatformAdapterRegistry

Prompt Builder
Negative Constraint utilities
Workflow Engine
```

Public APIs are intended to evolve carefully with backward compatibility where practical.

---

# Architecture Principles

## Platform-Agnostic Core

Core cinematic models and validation should not unnecessarily depend on one AI-video provider.

Provider-specific behavior belongs behind explicit adapter boundaries.

## Structured Data First

Important cinematic information should be represented as structured data whenever practical.

Structured data should remain inspectable, reusable, serializable, and testable.

## Validation Before Generation

Potential production problems should be detected before data is passed downstream.

Validation should produce actionable structured results where practical.

## Creative Flexibility

Continuity systems should identify possible inconsistencies without treating every intentional cinematic transition as an error.

## Portable Output

Project information should remain exportable into reusable structured formats.

Portable project packaging and provider-specific transformation remain separate responsibilities.

## Non-Mutating Processing

Validation, constraint resolution, prompt resolution, export processing, and platform adaptation should avoid modifying source production data unless mutation is explicitly documented.

## Deterministic Behavior

Canonical identifiers, prompt-section ordering, export ordering, registry output, and structured results should remain deterministic whenever practical.

## Testable Behavior

New core behavior should include automated tests appropriate to its scope.

---

# Development Roadmap

The development roadmap is maintained in:

```text
ROADMAP.md
```

High-level direction:

```text
v0.1.0
Foundation
RELEASED
    ↓
v0.2.0
Cinematic Timeline &
Music Video Foundation
RELEASED
    ↓
v0.3.0
Production Adapters
FUTURE
    ↓
v0.4.0
Command-Line Interface
FUTURE
```

The v0.2.0 milestone completes the provider-neutral cinematic and music-video production foundation.

Concrete provider-specific adapters remain future v0.3.0 Production Adapters work.

See [ROADMAP.md](ROADMAP.md) for the detailed development plan.

---

# Changelog

Development history and release notes are maintained in:

```text
CHANGELOG.md
```

See [CHANGELOG.md](CHANGELOG.md) for implemented features, fixes, planned work, and release history.

---

# Contributing

Contributions are welcome.

Please read:

```text
CONTRIBUTING.md
```

before submitting changes.

Potential contribution areas include:

* Python development
* Testing
* Cinematic workflow design
* Music-video workflow design
* Validation systems
* Continuity logic
* Structured prompt systems
* Export formats
* Documentation
* Examples
* Future provider adapters

If you find a bug or have an idea for a feature, open a GitHub Issue using the repository templates.

Pull Requests should remain focused, testable, documented, and consistent with the project architecture.

See [CONTRIBUTING.md](CONTRIBUTING.md).

---

# Security

Security-related reporting guidance is maintained in:

```text
SECURITY.md
```

Please use the documented security-reporting process rather than publishing sensitive vulnerability details in a normal public Issue.

See [SECURITY.md](SECURITY.md).

---

# Open-Source Development

AI Cinematic Workflow Toolkit is developed publicly.

The repository aims to make its evolution visible through:

* Source-code history
* Public Issues
* Automated tests
* CI
* Documentation
* CHANGELOG updates
* ROADMAP updates
* Releases
* Community contributions

The project prioritizes real, testable implementation over unsupported feature claims.

---

# Disclaimer

This is an independent open-source project.

It is not affiliated with, endorsed by, or sponsored by WAN, Veo, Kling, or any other AI-video platform or model provider unless explicitly stated.

Users are responsible for complying with the terms, licenses, usage requirements, and policies of any third-party services used with the toolkit.

---

# License

This project is released under the **MIT License**.

See [LICENSE](LICENSE) for details.

---

# Project Direction

**Structured · Reproducible · Portable · Transparent · Creator-friendly**
