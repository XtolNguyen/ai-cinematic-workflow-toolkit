# AI Cinematic Workflow Toolkit — Roadmap

This roadmap describes the planned development direction for **AI Cinematic Workflow Toolkit**.

The roadmap is intentionally modular. Features may be refined, reordered, or split into separate releases as the project evolves.

---

# Current Release

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

Status: **Planned**

The primary goal of v0.2.0 is to expand the toolkit from scene-by-scene workflow processing into structured **timeline-aware cinematic production planning**.

---

## 1. Cinematic Timeline Planner

Planned module:

```text
timeline.py
```

Goals:

* Build an ordered production timeline from scenes
* Calculate automatic scene start times
* Calculate automatic scene end times
* Track cumulative duration
* Detect timeline gaps
* Detect timeline overlaps
* Validate scene ordering
* Provide project-level timeline summaries

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

The timeline system should remain independent of any specific AI-video provider.

---

## 2. Music Video Structure Model

Planned module:

```text
music_video.py
```

The toolkit should support structured musical sections such as:

* Intro
* Verse
* Pre-Chorus
* Chorus
* Post-Chorus
* Instrumental
* Bridge
* Breakdown
* Final Chorus
* Outro

Each scene may optionally reference a musical section.

Example conceptual structure:

```text
INTRO
    ↓
Scene 01

VERSE 1
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

Scenes should be able to explicitly identify performance type.

Planned modes:

```text
vocal
instrumental
dialogue
performance-only
cinematic-only
```

This allows the toolkit to distinguish scenes requiring vocal performance from scenes that should contain no lip-sync behavior.

---

## 4. Lip-Sync Metadata

Planned support for explicit lip-sync requirements.

Possible metadata:

```text
lip_sync_required
vocal_text
performance_mode
audio_segment
```

The core toolkit will store and validate lip-sync metadata without performing the actual video-generation process.

Platform adapters may later translate this metadata into provider-specific prompts.

---

## 5. Scene Duration Rules

Introduce configurable duration policies.

Potential rules:

* Fixed duration
* Maximum duration
* Minimum duration
* Preferred duration
* Platform-specific duration constraints

Example:

```text
preferred_scene_duration = 15 seconds
```

Duration policies should remain separate from the core `Scene` model where possible.

---

## 6. Advanced Continuity Engine

Expand the current continuity system beyond basic comparisons.

Planned continuity categories:

* Character identity
* Wardrobe
* Hair
* Props
* Location
* Lighting
* Weather
* Time of day
* Emotional state
* Screen direction
* Camera position
* Camera movement
* Lens
* Character position
* Previous-scene state

Continuity checks should distinguish:

```text
ERROR
WARNING
INFORMATION
INTENTIONAL CHANGE
```

The system should continue to avoid treating every creative transition as a hard error.

---

## 7. Continuity Profiles

Introduce reusable continuity profiles.

Example conceptual profile:

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

Multiple scenes may reference the same profile instead of duplicating metadata manually.

---

## 8. Global Project Constraints

Introduce project-level constraints shared by all scenes.

Potential examples:

* Character consistency rules
* Camera-quality requirements
* Image-quality requirements
* Motion constraints
* Anatomy constraints
* Global negative constraints
* Visual-style requirements

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
Final Scene Constraints
```

---

## 9. Prompt Profiles

Introduce reusable cinematic prompt profiles.

Potential profiles may contain:

* Camera style
* Lens preference
* Lighting style
* Motion style
* Performance style
* Atmosphere
* Visual language

Profiles should reduce repeated configuration across large projects.

---

## 10. Structured Prompt Sections

Expand prompt generation into explicit reusable components.

Potential structure:

```text
SUBJECT
ENVIRONMENT
PERFORMANCE
BLOCKING
CAMERA
LENS
LIGHTING
MOTION
ATMOSPHERE
CONTINUITY
NEGATIVE CONSTRAINTS
```

The system should be able to produce both:

* Structured verbose prompts
* Concise generation-ready prompts

---

## 11. Music Video Timeline Validation

Planned validation rules may include:

* Missing intro mapping
* Missing outro mapping
* Vocal scene marked instrumental
* Instrumental scene marked lip-sync
* Scene duration mismatch
* Unmapped music sections
* Duplicate section assignments
* Timeline duration mismatch

---

## 12. Enhanced Project Export

Expand portable project export to include:

* Timeline
* Music sections
* Scene timestamps
* Performance modes
* Lip-sync metadata
* Global constraints
* Continuity profiles
* Prompt profiles

Planned JSON structure:

```text
Project
├── Metadata
├── Timeline
├── Music Structure
├── Global Constraints
├── Continuity Profiles
├── Prompt Profiles
├── Scenes
└── Workflow Results
```

---

# v0.3.0 — Production Adapters

Status: **Future**

The goal of this release family is to introduce provider-specific adapters while preserving a platform-independent core.

Potential architecture:

```text
Core Cinematic Project
          ↓
     Adapter Layer
          ↓
 ┌────────┼─────────┐
 ↓        ↓         ↓
Provider A Provider B Provider C
```

Potential adapter capabilities:

* Prompt transformation
* Duration constraints
* Provider-specific parameters
* Negative-prompt formatting
* Camera terminology mapping
* Export presets

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

Potential capabilities:

* Validate project files
* Generate workflow output
* Export production JSON
* Inspect continuity issues
* Print project summaries
* Run timeline checks

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
* Additional runnable examples

---

# Design Principles

Future development should continue following these principles:

## Platform-Agnostic Core

Core models and validation should not depend unnecessarily on a single AI-video provider.

## Structured Data First

Important cinematic information should be represented as structured data whenever practical.

## Validation Before Generation

Invalid production data should be detected before being passed downstream.

## Creative Flexibility

The toolkit should report potential continuity problems without incorrectly treating all cinematic changes as mistakes.

## Portable Output

Projects should remain exportable into formats that can be consumed by other tools.

## Testable Behavior

New workflow behavior should include automated tests whenever practical.

## Backward Compatibility

Public APIs should evolve carefully as adoption grows.

---

# v0.2.0 Definition of Done

The v0.2.0 milestone will be considered complete when the toolkit includes:

* [x] Cinematic Timeline Planner
* [x] Timeline validation
* [x] Music Video Structure Model
* [ ] Musical section mapping
* [x] Vocal/instrumental metadata
* [x] Lip-sync metadata
* [x] Lip-sync rules
* [ ] Configurable scene-duration policies
* [ ] Advanced continuity categories
* [ ] Continuity profiles
* [ ] Global project constraints
* [ ] Prompt profiles
* [ ] Structured prompt sections
* [ ] Music-video timeline validation
* [ ] Expanded project JSON export
* [ ] Automated tests for all new core behavior
* [ ] Updated runnable example
* [ ] Updated documentation
* [ ] Updated CHANGELOG

---

**Project direction:**
Structured · Reproducible · Portable · Transparent · Creator-friendly
