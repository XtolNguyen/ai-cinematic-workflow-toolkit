# Changelog

All notable changes to **AI Cinematic Workflow Toolkit** will be documented in this file.

The project follows a simple versioned release process. Versions may evolve toward Semantic Versioning as the public API matures.

---

## [Unreleased]

### Planned

* Cinematic timeline planner
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
