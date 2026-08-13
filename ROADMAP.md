# AI Cinematic Workflow Toolkit — Roadmap

This roadmap describes the planned development direction for **AI Cinematic Workflow Toolkit**.

The roadmap is intentionally modular. Features may be refined, reordered, or split into separate releases as the project evolves.

---

# Release Status

Current released version: **v0.2.0**

Previous released version: **v0.1.0**

## v0.1.0 — Foundation

Status: **Released**

The first release established the core architecture for structured AI-assisted cinematic production.

Completed capabilities include:

* Camera model
* Scene model
* Scene validation
* Cinematic Prompt Builder
* Negative Constraint Validator
* Negative-prompt normalization
* Negative-prompt deduplication
* Continuity Validator
* Multi-scene Workflow Engine
* Cinematic Project Model
* Project-level validation
* JSON exporters
* Complete project JSON export
* Public Python API
* Runnable music-video example
* Automated pytest suite
* Multi-version GitHub Actions CI
* Open-source documentation
* Contribution guidelines
* Security policy
* Issue Forms
* Pull Request template
* Release workflow

---

# v0.2.0 — Cinematic Timeline & Music Video Foundation

Status: **Released**

Release date: **2026-08-13**

The defined v0.2.0 implementation, testing, runnable-example, and documentation scope is complete.

v0.2.0 is the current released cinematic timeline and music-video foundation of the toolkit.

The primary goal of v0.2.0 is to expand the toolkit from scene-by-scene workflow processing into structured **timeline-aware cinematic production planning**.

The v0.2.0 architecture remains provider-neutral and builds a reusable cinematic production layer before provider-specific integrations are introduced.

---

# v0.3.0 — Production Adapters

Status: **Future**

---

## 1. Cinematic Timeline Planner

Implemented module:

```text
timeline.py
```

Implemented capabilities include:

* Ordered production timelines built from scenes
* Automatic scene start-time calculation
* Automatic scene end-time calculation
* Cumulative project duration
* Timeline gap detection
* Timeline overlap detection
* Scene-order validation
* Duplicate scene-ID validation
* Cinematic timestamp formatting
* Serializable timeline entries
* Serializable timeline reports
* Project-level timeline summaries
* Public Timeline API
* Complete Project JSON Export integration
* Automated unit and project integration tests

Conceptual pipeline:

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

The timeline system remains independent of any specific AI-video provider.

---

## 2. Music Video Structure Model

Implemented module:

```text
music_video.py
```

The toolkit supports structured musical sections such as:

* Intro
* Verse
* Pre-Chorus
* Chorus
* Instrumental
* Bridge
* Breakdown
* Final Chorus
* Outro

Implemented capabilities include:

* Structured music-section models
* Chronological music-section validation
* Music-section duration validation
* Music-section overlap detection
* Scene-to-music-section mapping
* Duplicate scene-mapping detection
* Project-scene mapping validation
* Vocal-performance requirement metadata
* Serializable music-video structures
* CinematicProject integration
* Complete Project JSON Export integration
* Public Music Video Structure API
* Automated unit and project integration tests

Conceptual structure:

```text
INTRO
    ↓
Scene 01

VERSE
    ↓
Scene 02
Scene 03

CHORUS
    ↓
Scene 04
Scene 05

INSTRUMENTAL
    ↓
Scene 06

OUTRO
    ↓
Scene 07
```

---

## 3. Vocal / Instrumental Scene Metadata

The toolkit supports explicit musical performance modes.

Implemented performance modes include:

```text
vocal
instrumental
dialogue
performance-only
cinematic-only
```

This allows cinematic workflows to distinguish scenes requiring vocal performance from scenes that should not trigger lip-sync behavior.

Implemented capabilities include:

* Vocal-performance metadata
* Instrumental-performance metadata
* Dialogue-performance metadata
* Performance-only metadata
* Cinematic-only metadata
* Scene-to-music-section performance relationships
* Serializable performance metadata
* Music Video Structure integration
* Lip-Sync Policy integration

---

## 4. Lip-Sync Metadata and Policy Rules

Implemented module:

```text
lip_sync.py
```

The core toolkit stores, resolves, and validates lip-sync behavior without performing video generation itself.

Implemented capabilities include:

* Lip-Sync Policy Engine
* Automatic lip-sync policy resolution for vocal music sections
* Instrumental-section protection against unintended singing mouth movement
* Dialogue handling
* Performance-only handling
* Cinematic-only handling
* Explicit vocal B-roll lip-sync override support
* Validation preventing forced lip-sync on non-vocal sections
* Per-section lip-sync execution instructions
* Lip-sync warnings
* Lip-sync summary metadata
* Public Lip-Sync Policy API
* Music-video project export integration
* Automated unit and project integration tests

Platform-specific adapters may later translate this structured metadata into documented provider-specific instructions.

---

## 5. Scene Duration Rules

Implemented module:

```text
duration.py
```

The toolkit provides configurable duration policies while keeping duration-policy behavior separate from the core Scene model where practical.

Implemented capabilities include:

* Preferred scene duration
* Minimum scene duration
* Maximum scene duration
* Allowed scene durations
* Configurable duration tolerance
* Strict duration enforcement
* Advisory duration enforcement
* Structured scene-duration validation issues
* Structured scene-duration validation results
* Regular cinematic-project duration validation
* Music-video duration validation integration
* Public Duration Policy API
* Complete Project JSON Export integration
* Automated unit and project integration tests

Duration policies remain provider-neutral.

Provider-specific duration restrictions belong to the Platform Adapter layer.

---

## 6. Advanced Continuity Engine

The toolkit extends basic scene continuity into configurable project-level continuity validation.

Implemented continuity capabilities include:

* Character identity continuity
* Wardrobe continuity
* Hair continuity
* Props continuity
* Location continuity
* Lighting continuity
* Weather continuity where supplied
* Time-of-day continuity where supplied
* Emotional-state continuity where supplied
* Screen-direction continuity where supplied
* Camera shot continuity
* Camera movement continuity
* Lens continuity
* Native Scene field continuity
* Arbitrary custom continuity metadata
* Required continuity fields
* Optional continuity fields
* Ignored continuity fields
* Strict continuity fields
* Warning-only continuity fields
* Allowed intentional changes
* Missing required-field detection
* Configurable missing-field severity
* Previous-scene reporting
* Current-scene reporting
* Previous-value reporting
* Current-value reporting
* Project-level advanced continuity validation
* Serializable continuity validation results
* Backward compatibility with the existing basic continuity API
* Automated unit and project integration tests

Continuity checks distinguish between:

```text
ERROR
WARNING
ALLOWED INTENTIONAL CHANGE
```

The toolkit avoids treating every creative transition as a hard continuity error.

---

## 7. Continuity Profiles

The toolkit provides reusable Continuity Profiles for configuring continuity requirements across multiple scenes.

Implemented capabilities include:

* Required continuity fields
* Optional continuity fields
* Ignored continuity fields
* Strict continuity fields
* Warning-only continuity fields
* Allowed-change fields
* Configurable missing-field severity
* Native Scene field support
* Custom continuity metadata support
* Character identity comparison
* Camera continuity support
* Serializable ContinuityProfile configuration
* Project-level validation integration
* Enhanced Project Export integration
* Automated unit and project integration tests

Conceptual profile:

```text
Character:
    Lead performer

Wardrobe:
    Black cinematic outfit

Hair:
    Long dark hair

Primary prop:
    Vintage microphone

Lighting:
    Soft blue-magenta lighting
```

Profiles reduce repeated continuity configuration across large cinematic projects.

---

## 8. Global Project Constraints

Implemented module:

```text
global_constraints.py
```

The toolkit provides reusable project-wide constraints that can be resolved together with scene-level constraints.

Implemented capabilities include:

* Required project constraints
* Advisory project constraints
* Global negative constraints
* Prohibited-element constraints
* Character identity constraints
* Visual-style constraints
* Camera constraints
* Environment constraints
* Custom named constraint categories
* Constraint normalization
* Constraint deduplication
* Conflict validation
* Project-wide constraint resolution
* Scene-level negative-constraint resolution
* Deduplicated global and scene negative constraints
* Non-mutating scene constraint resolution
* Structured GlobalConstraintIssue reporting
* ResolvedSceneConstraints
* GlobalConstraintResolution
* Serializable configuration and resolution data
* Public Global Constraints API
* Complete Project JSON Export integration
* Prompt Profile integration
* Structured Prompt Sections integration
* Automated unit and project integration tests

Pipeline:

```text
GLOBAL CONSTRAINTS
        +
SCENE CONSTRAINTS
        ↓
Normalization
        ↓
Deduplication
        ↓
Resolved Scene Constraints
```

---

## 9. Prompt Profiles

Implemented module:

```text
prompt_profiles.py
```

The toolkit provides reusable cinematic Prompt Profiles for controlling structured prompt behavior.

Implemented capabilities include:

* Named PromptProfile presets
* Enabled prompt-component configuration
* Disabled prompt-component configuration
* Canonical prompt-component normalization
* Duplicate prompt-component removal
* Enabled/disabled component conflict detection
* Strict unknown-component validation
* Permissive extension-component handling
* Structured warnings for extension components
* Optional base-profile inheritance
* Child-profile precedence
* Runtime enable overrides
* Runtime disable overrides
* Runtime override conflict detection
* Runtime configuration overrides
* Recursive nested configuration merging
* Non-mutating PromptProfile resolution
* ResolvedPromptProfile output
* JSON-serializable custom configuration
* Public Prompt Profiles API
* Complete Project JSON Export integration
* Structured Prompt Sections integration
* Backward compatibility with the existing cinematic prompt builder
* Automated unit and project integration tests

Supported cinematic components include:

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

Prompt Profiles reduce repeated configuration across large projects without introducing provider-specific behavior into the core toolkit.

---

## 10. Structured Prompt Sections

Implemented module:

```text
structured_prompts.py
```

The toolkit converts cinematic scene information into explicit reusable structured prompt sections.

Implemented canonical sections:

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

Implemented capabilities include:

* StructuredPromptSection model
* StructuredPromptResult model
* OmittedPromptComponent reporting
* Canonical prompt-section identifiers
* Deterministic prompt-section ordering
* Human-readable canonical section labels
* Character prompt sections
* Location prompt sections
* Structured camera sections
* Performance prompt sections
* Lighting prompt sections
* Mood prompt sections
* Dialogue-or-vocals prompt sections
* Continuity prompt sections
* Global Constraints prompt sections
* Resolved negative-constraint prompt sections
* PromptProfile-controlled inclusion
* PromptProfile-controlled exclusion
* Disabled-component reporting
* Not-enabled-component reporting
* Empty-component reporting
* Unsupported-component reporting
* Optional empty-section preservation
* Structured section metadata
* Included-component reporting
* Omitted-component reporting
* GlobalConstraints-aware assembly
* Resolved scene/global negative-constraint integration
* Non-mutating structured prompt assembly
* JSON-serializable structured prompt output
* Public Structured Prompt Sections API
* Complete Project JSON Export integration
* Backward compatibility with build_cinematic_prompt()
* Automated unit and project integration tests

Pipeline:

```text
Scene
   +
PromptProfile
   +
GlobalConstraints
        ↓
Structured Prompt Assembly
        ↓
StructuredPromptResult
```

Structured Prompt Sections remain platform-agnostic.

---

## 11. Music Video Timeline Validation

Implemented module:

```text
music_video_timing.py
```

The toolkit validates cinematic scene timing against structured music-video timing.

Implemented validation capabilities include:

* Scene-to-music-section duration alignment validation
* Scene timing overflow detection
* Music-section boundary validation
* Music-section start coverage validation
* Music-section end coverage validation
* Total cinematic runtime calculation
* Music-video runtime comparison
* Structured timing validation issues
* Structured timing validation results
* DurationPolicy coexistence
* Music Video Structure integration
* Complete Project JSON Export integration
* Automated unit and project integration tests

The validation layer detects timing conflicts before cinematic data is passed downstream.

---

## 12. Enhanced Project Export

Implemented modules:

```text
export_options.py
exporters/project_json_exporter.py
```

The Enhanced Project Export system provides reusable and configurable portable cinematic project packaging.

Implemented capabilities include:

* Reusable named ProjectExportOptions
* Timeline inclusion control
* Workflow inclusion control
* Duration validation inclusion control
* Continuity validation inclusion control
* GlobalConstraints inclusion control
* PromptProfile inclusion control
* Structured Prompt Sections inclusion control
* Empty structured-prompt section configuration
* Canonical export-section registry
* Deterministic enhanced export ordering
* ProjectExportManifest
* OmittedExportSection reporting
* Included-section reporting
* Omitted-section reporting
* Explicit omission reasons
* Active optional production-system reporting
* Serializable export configuration
* Missing DurationPolicy reporting
* Missing ContinuityProfile reporting
* Missing GlobalConstraints reporting
* Missing PromptProfile reporting
* Disabled-by-export-options reporting
* Separation between requested export layers and actually produced layers
* Internal PromptProfile reuse without requiring top-level PromptProfile export
* Internal GlobalConstraints reuse without requiring top-level Global Constraints export
* Validation of incompatible legacy and enhanced export options
* Non-mutating enhanced export processing
* JSON-serializable enhanced project output
* JSON file persistence
* Backward compatibility with project_to_dict()
* Backward compatibility with project_to_json()
* Backward compatibility with save_project_json()
* Backward compatibility with legacy Structured Prompt export flags
* Public Enhanced Project Export API
* Provider-neutral enhanced project packages
* Automated unit tests
* Automated project integration tests

Canonical enhanced export layers:

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

Optional layers are included according to ProjectExportOptions and available source data.

Enhanced Project Export remains provider-neutral.

It packages cinematic production data but does not perform provider-specific transformation.

---

## 13. Platform Adapter Foundation

Implemented module:

```text
platform_adapters.py
```

The toolkit now includes a provider-neutral Platform Adapter foundation that establishes a clean extension boundary between structured cinematic production data and future provider-specific implementations.

Implemented capabilities include:

* PlatformAdapter base contract
* PlatformAdapterCapabilities declarations
* PlatformAdapterIssue structured warning and error reporting
* PlatformAdapterResult deterministic adaptation results
* PlatformAdapterRegistry
* Canonical platform identifier normalization
* Adapter identity
* Adapter display name
* Adapter version metadata
* Adapter metadata
* Canonical Structured Prompt Section capability declarations
* StructuredPromptResult adaptation
* Supported prompt-section reporting
* Unsupported prompt-section reporting
* Capability-based section filtering
* Structured warning generation for unsupported sections
* Error-level reporting for unsupported StructuredPromptResult input
* Deterministic adapted section ordering
* Section metadata preservation
* Configurable section metadata stripping
* Custom adapter capability metadata
* JSON-serializable adapter capabilities
* JSON-serializable adapter metadata
* JSON-serializable adapter results
* Adapter-result validity reporting
* Warning-count reporting
* Error-count reporting
* Non-mutating StructuredPromptResult adaptation
* Explicit adapter registration
* Canonical adapter lookup
* Duplicate canonical adapter registration protection
* Invalid adapter registration protection
* Unknown adapter handling
* Deterministic registry listing
* Extensible provider-specific subclass boundary
* Multi-scene CinematicProject integration
* PromptProfile-aware platform adaptation
* GlobalConstraints-aware platform adaptation
* Resolved negative-constraint preservation before adapter filtering
* Multiple independent adapters for the same cinematic source
* Enhanced Project Export coexistence
* Separation between portable project export and target-platform adaptation
* Public Platform Adapter API
* Automated Platform Adapter unit tests
* Automated Platform Adapter project integration tests

Conceptual pipeline:

```text
CinematicProject
       ↓
Scene
       ↓
PromptProfile
       ↓
GlobalConstraints
       ↓
StructuredPromptResult
       ↓
PlatformAdapter
       ↓
PlatformAdapterResult
```

The Platform Adapter foundation remains provider-neutral.

It does not implement undocumented WAN, Veo, Kling, or other provider-specific parameters.

It does not contain provider API endpoints, API credentials, or network execution.

Provider-specific adapters belong to the v0.3.0 Production Adapters layer.

---

# v0.3.0 — Production Adapters

Status: **Future**

The provider-neutral Platform Adapter foundation is established in v0.2.0.

The goal of v0.3.0 is to introduce concrete provider-specific adapters on top of that shared adapter contract while preserving a platform-independent core.

Potential architecture:

```text
Core Cinematic Project
          ↓
Structured Prompt Sections
          ↓
Platform Adapter Foundation
          ↓
 ┌────────┼─────────┐
 ↓        ↓         ↓
WAN      Veo       Kling
Adapter  Adapter    Adapter
```

Potential provider-adapter capabilities include:

* Prompt transformation
* Provider duration constraints
* Documented provider-specific parameters
* Negative-prompt formatting
* Camera terminology mapping
* Provider capability translation
* Provider export presets

Provider implementations should only use documented and intentionally implemented provider behavior.

No provider-specific implementation should become mandatory for using the core toolkit.

---

# v0.4.0 — Command-Line Interface

Status: **Future**

Planned CLI concepts:

```bash
cinematic validate project.json
cinematic process project.json
cinematic export project.json
cinematic timeline project.json
```

Potential capabilities include:

* Validate project files
* Generate workflow output
* Export production JSON
* Inspect continuity issues
* Print project summaries
* Run timeline checks
* Inspect export manifests
* Inspect adapter capabilities

The CLI should operate on the same public Python APIs rather than creating a separate workflow engine.

---

# Future Exploration

Additional ideas may include:

* YAML export
* Markdown production reports
* Shot-list export
* Story-to-scene utilities
* Scene templates
* Character profiles
* Environment profiles
* Camera libraries
* Lens libraries
* Production presets
* Workflow visualization
* Batch project validation
* Plugin architecture
* API integration layer
* Additional project exporters
* Additional continuity enhancements
* Additional runnable examples
* Provider adapter presets
* Adapter capability discovery
* Adapter configuration files

---

# Design Principles

Future development should continue following these principles.

## Platform-Agnostic Core

Core models and validation should not depend unnecessarily on a single AI-video provider.

Provider-specific behavior should remain behind explicit adapter boundaries.

## Structured Data First

Important cinematic information should be represented as structured data whenever practical.

Structured data should remain inspectable, reusable, serializable, and testable.

## Validation Before Generation

Invalid production data should be detected before being passed downstream.

Validation should produce structured and actionable results where practical.

## Creative Flexibility

The toolkit should report potential continuity or production problems without incorrectly treating all cinematic changes as mistakes.

Intentional creative transitions should remain possible.

## Portable Output

Projects should remain exportable into formats that can be consumed by other tools.

Portable project export should remain separate from provider-specific adaptation.

## Explicit Provider Boundaries

Core cinematic models should not contain undocumented provider-specific parameters.

Provider-specific behavior should be introduced through explicit Platform Adapter implementations.

## Non-Mutating Processing

Validation, prompt resolution, export processing, and platform adaptation should avoid mutating source production data unless an API explicitly documents mutation.

## Deterministic Behavior

Canonical identifiers, section ordering, export ordering, registry output, and structured results should remain deterministic whenever practical.

## Testable Behavior

New workflow behavior should include automated tests whenever practical.

Core features should include unit tests and integration tests appropriate to their scope.

## Backward Compatibility

Public APIs should evolve carefully as adoption grows.

Existing public behavior should remain compatible unless a documented release intentionally introduces a breaking change.

---

# v0.2.0 Definition of Done

The v0.2.0 milestone will be considered complete when the toolkit includes:

* [x] Duration rules
* [x] Cinematic Timeline Planner
* [x] Timeline validation
* [x] Music Video Structure Model
* [x] Musical section mapping
* [x] Vocal/instrumental metadata
* [x] Lip-sync metadata
* [x] Lip-sync rules
* [x] Configurable scene-duration policies
* [x] Advanced continuity
* [x] Continuity profiles
* [x] Global project constraints
* [x] Prompt profiles
* [x] Structured prompt sections
* [x] Music video timeline validation
* [x] Expanded project JSON export
* [x] Platform Adapter foundation
* [x] Automated tests for all implemented new core behavior
* [x] Updated runnable example
* [x] Updated documentation
* [x] Updated CHANGELOG

---

**Project direction:**

Structured · Reproducible · Portable · Transparent · Creator-friendly
