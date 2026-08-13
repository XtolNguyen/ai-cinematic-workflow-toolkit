# Changelog

All notable changes to **AI Cinematic Workflow Toolkit** will be documented in this file.

The project follows a simple versioned release process. Versions may evolve toward Semantic Versioning as the public API matures.

---

## [Unreleased]

### Added

- Configurable Duration Policy model
- Preferred, minimum, maximum, and allowed scene-duration rules
- Strict and advisory scene-duration enforcement
- Configurable duration tolerance support
- Structured scene-duration validation issues and results
- Music-video timing validation across cinematic scenes and music sections
- Scene-to-music-section duration alignment validation
- Scene timing overflow and section-boundary validation
- Music-section start and end coverage validation
- Total cinematic runtime and music-video runtime comparison
- Public Duration Policy and Music Video Timing Validation API
- Optional duration validation in complete project JSON exports
- Scene-duration validation mode for regular cinematic projects
- Music-video timing validation mode for music-video projects
- Backward-compatible project exports when no DurationPolicy is supplied
- Automated duration-policy, music-video timing, and project integration tests
- Lip-Sync Policy Engine
- Automatic lip-sync policy resolution for vocal music sections
- Instrumental-section protection against unintended singing mouth movement
- Dialogue, performance-only and cinematic-only lip-sync handling
- Explicit vocal B-roll lip-sync override support
- Validation preventing forced lip-sync on non-vocal sections
- Per-section lip-sync execution instructions
- Lip-sync policy warnings and summary metadata
- Public Lip-Sync Policy API
- Lip-sync policy integration with complete music-video project JSON export
- Automated unit and project integration tests for lip-sync policies
- Cinematic Timeline Planner
- Automatic scene start and end time calculation
- Cumulative project timeline duration
- Timeline gap detection
- Timeline overlap detection
- Scene-order validation
- Duplicate scene ID validation
- Cinematic timestamp formatting
- Serializable timeline entries and reports
- Public Timeline API
- Timeline integration with complete project JSON export
- Automated timeline unit and integration tests
- Music Video Structure Model
- Structured music sections including intro, verse, pre-chorus, chorus, instrumental, bridge, breakdown, final chorus and outro
- Vocal, instrumental, dialogue, performance-only and cinematic-only performance modes
- Scene-to-music-section mapping
- Music-section duration and chronological validation
- Music-section overlap detection
- Duplicate scene mapping detection
- Project-scene mapping validation
- Vocal-performance requirement metadata
- Music-video structure serialization
- Music-video integration with CinematicProject
- Music-video integration with complete project JSON export
- Public Music Video Structure API
- Automated unit and project integration tests for music-video structures
- Advanced Continuity Profiles
- Configurable required, optional, ignored, strict, warning-only, and allowed-change continuity fields
- Scene-to-scene strict continuity locks
- Warning-level continuity validation
- Allowed intentional continuity transitions
- Missing required continuity-field detection
- Configurable missing-field severity
- Structured advanced continuity issues with error and warning severity
- Previous and current scene ID reporting for continuity issues
- Previous and current continuity value reporting
- Support for native Scene fields and arbitrary custom continuity metadata
- Character identity continuity with order-insensitive character comparison
- Camera shot, movement, and lens continuity support
- Project-level advanced continuity validation
- Serializable ContinuityProfile and validation results
- Public Advanced Continuity API
- Optional advanced continuity validation in complete project JSON exports
- Backward compatibility with the existing basic continuity API
- Coexistence of DurationPolicy and ContinuityProfile validation in project exports
- Automated advanced continuity unit and project integration tests
- Project-wide Global Constraints
- Configurable required and advisory project constraints
- Global negative constraints
- Prohibited-element constraints
- Character identity constraints
- Visual-style constraints
- Camera constraints
- Environment constraints
- Custom named constraint categories
- Constraint normalization and duplicate removal
- Validation for conflicting required, advisory, negative, and prohibited constraints
- Project-wide and scene-level negative-constraint resolution
- Deduplicated global and scene negative constraints
- Non-mutating scene constraint resolution
- Structured GlobalConstraintIssue reporting
- Per-scene ResolvedSceneConstraints output
- Project-level GlobalConstraintResolution output
- Serializable global constraint configuration and resolution data
- Public Global Constraints API
- Optional Global Constraints integration in complete project JSON exports
- Backward compatibility with existing scene-level negative constraints
- Coexistence with DurationPolicy and ContinuityProfile validation
- Automated Global Constraints unit and project integration tests
- Reusable Prompt Profiles
- Configurable named PromptProfile presets
- Enabled and disabled prompt-component configuration
- Canonical prompt-component normalization
- Duplicate prompt-component removal
- Enabled/disabled component conflict detection
- Strict unknown-component validation
- Permissive extension-component handling with structured warnings
- Optional base-profile inheritance
- Child-profile precedence over inherited configuration
- Runtime enable and disable component overrides
- Runtime override conflict detection
- Non-mutating PromptProfile resolution
- Structured ResolvedPromptProfile output
- Character prompt-component support
- Location prompt-component support
- Camera prompt-component support
- Performance prompt-component support
- Lighting prompt-component support
- Mood prompt-component support
- Dialogue-or-vocals prompt-component support
- Continuity prompt-component support
- Scene negative-constraint prompt-component support
- Global Constraints prompt-component support
- JSON-serializable custom prompt configuration
- Recursive nested custom-configuration merging
- Runtime custom-configuration overrides
- Public Prompt Profiles API
- Optional PromptProfile resolution in complete project JSON exports
- Backward compatibility with the existing cinematic prompt builder
- Coexistence with DurationPolicy, ContinuityProfile, and GlobalConstraints
- Automated Prompt Profiles unit and project integration tests
- Platform-agnostic Structured Prompt Sections
- StructuredPromptSection model for named cinematic prompt components
- StructuredPromptResult model for complete per-scene structured prompt output
- OmittedPromptComponent reporting for excluded or unavailable components
- Canonical structured prompt-section identifiers
- Deterministic cinematic prompt-section ordering
- Human-readable canonical prompt-section labels
- Character prompt section
- Location prompt section
- Structured camera section with shot, movement, and lens data
- Performance prompt section
- Lighting prompt section
- Mood prompt section
- Dialogue-or-vocals prompt section
- Continuity prompt section
- Project-wide Global Constraints prompt section
- Scene and resolved negative-constraint prompt sections
- PromptProfile-driven prompt-section inclusion and exclusion
- Explicit disabled, not-enabled, empty, and unsupported-component reporting
- Optional empty-section preservation
- Structured section metadata including component, source, empty state, and profile control
- Included and omitted component reporting
- Non-mutating structured prompt assembly
- JSON-serializable structured prompt output
- Public Structured Prompt Sections API
- Optional per-scene Structured Prompt Sections in complete Project JSON exports
- Reuse of resolved PromptProfile configuration during structured prompt export
- GlobalConstraints-aware structured prompt assembly
- Deduplicated project-wide and scene-level negative-constraint resolution
- Backward compatibility with the existing build_cinematic_prompt() API
- Backward-compatible opt-in structured prompt project exports
- Coexistence with DurationPolicy, ContinuityProfile, GlobalConstraints, PromptProfile, timeline, and workflow output
- Automated Structured Prompt Sections unit and project integration tests
  
### Fixed

- Improved timestamp formatting compatibility across Python 3.10 through Python 3.13
  
### Planned

* Music-video section mapping
* Additional project exporters
* Improved continuity rules
* Platform-specific adapters
* Command-line interface
* Extended documentation and examples

---

## [0.1.0] - 2026-08-12

Initial public development release of **AI Cinematic Workflow Toolkit**.

### Added

* Structured `Camera` model
* Structured cinematic `Scene` model
* Scene-level validation
* Cinematic prompt builder
* Structured positive prompt generation
* Negative constraint normalization
* Negative constraint deduplication
* Negative constraint validation
* Scene-to-scene continuity comparison
* Continuity issue reporting
* Multi-scene workflow engine
* Cinematic project metadata model
* Multi-scene `CinematicProject` model
* Project-level validation
* Scene count calculation
* Total project duration calculation
* Scene JSON export
* Complete cinematic project JSON export
* Workflow processing summaries
* Public Python package API
* Runnable three-scene music-video example
* MIT License
* Contribution guidelines
* Python `.gitignore`
* Installation and Quick Start documentation

### Testing

* Scene validation tests
* JSON exporter tests
* Cinematic prompt builder tests
* Negative constraint validator tests
* Continuity validator tests
* End-to-end workflow engine tests
* Cinematic project model tests
* Complete project JSON exporter tests
* Runnable example validation

### Continuous Integration

* GitHub Actions workflow
* Automated test execution on Python 3.10
* Automated test execution on Python 3.11
* Automated test execution on Python 3.12
* Automated test execution on Python 3.13
* Automated execution of the runnable music-video example
* Automated validation of generated example JSON output

### Documentation

* Expanded project overview
* Project architecture
* Development roadmap
* Installation instructions
* Basic usage examples
* Multi-scene project example
* JSON export documentation
* Testing instructions
* Contribution workflow
* Development philosophy
* Platform-agnostic design guidance

### Fixed

* Corrected initial nested source-directory structure during repository setup
* Updated Python project license metadata for current setuptools compatibility
* Verified package installation and imports through GitHub Actions

---

## Release Philosophy

Early releases focus on building a stable, transparent, and testable foundation for AI-assisted cinematic workflow development.

The core toolkit aims to remain:

**Structured · Reproducible · Portable · Transparent · Creator-friendly**

Platform-specific functionality should generally be implemented through dedicated adapters so the core architecture remains reusable across different AI-video systems.
