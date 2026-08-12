# Contributing to AI Cinematic Workflow Toolkit

Thank you for your interest in contributing to **AI Cinematic Workflow Toolkit**.

This project is developed openly and welcomes contributions that improve cinematic workflow structure, validation, testing, documentation, exporters, and developer tooling.

---

## Ways to Contribute

You can contribute by:

* Reporting bugs
* Suggesting new features
* Improving documentation
* Adding automated tests
* Improving cinematic workflow logic
* Improving scene validation
* Improving continuity detection
* Improving prompt generation
* Adding new export formats
* Adding examples
* Improving developer tooling

---

## Development Setup

### 1. Fork the Repository

Create a fork of the repository on GitHub.

### 2. Clone Your Fork

```bash
git clone https://github.com/YOUR-USERNAME/ai-cinematic-workflow-toolkit.git
cd ai-cinematic-workflow-toolkit
```

### 3. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it.

On Windows:

```bash
.venv\Scripts\activate
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

### 4. Install Development Dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

### 5. Run the Test Suite

```bash
pytest
```

All tests should pass before submitting a contribution.

---

## Running the Example Project

The repository includes a runnable music-video example.

Run:

```bash
python examples/music_video_project.py
```

The example demonstrates:

* Cinematic project creation
* Scene validation
* Prompt generation
* Negative constraint normalization
* Scene-to-scene continuity checks
* Complete JSON project export

Generated output is written locally under:

```text
examples/output/
```

Generated output files are ignored by Git.

---

## Development Workflow

Before making changes, create a dedicated branch.

Example:

```bash
git checkout -b feature/my-feature
```

Use descriptive branch names such as:

```text
feature/yaml-exporter
feature/timeline-planner
fix/continuity-validation
docs/quick-start
test/project-exporter
```

Avoid making unrelated changes in the same branch.

---

## Code Guidelines

Please keep contributions:

* Focused
* Readable
* Tested
* Platform-agnostic when possible
* Backward-compatible when reasonable
* Documented when introducing public behavior

Python code should favor clear, explicit implementations over unnecessary complexity.

Public functions and classes should include useful docstrings.

---

## Testing Requirements

New behavior should normally include automated tests.

Tests are located under:

```text
tests/
```

Run the complete suite with:

```bash
pytest
```

The project also uses GitHub Actions to run automated checks across supported Python versions.

A pull request should not intentionally break the existing test suite.

---

## Cinematic Workflow Contributions

When contributing cinematic workflow logic, consider the distinction between:

* Hard validation errors
* Warnings
* Intentional creative changes
* Platform-specific behavior

For example, a wardrobe change between two scenes may represent a continuity problem, but it may also be an intentional cinematic transition.

For this reason, continuity tools should generally report potential mismatches rather than automatically treating every change as an error.

---

## Platform-Specific Integrations

The core toolkit aims to remain platform-agnostic.

Platform-specific integrations should ideally be implemented as separate adapters or modules instead of placing provider-specific behavior directly inside the core models.

This helps keep the toolkit reusable across different AI-video generation systems.

---

## Commit Messages

Use concise and descriptive commit messages.

Examples:

```text
feat: add cinematic timeline planner
fix: correct project duration validation
test: add continuity edge-case tests
docs: improve installation guide
refactor: simplify scene processing
ci: add automated lint checks
```

Common prefixes include:

```text
feat:
fix:
test:
docs:
refactor:
ci:
build:
chore:
example:
```

---

## Pull Requests

Before opening a pull request:

* Make sure the project installs successfully.
* Run the complete test suite.
* Check that your changes are focused.
* Add or update tests when appropriate.
* Update documentation if public behavior changed.
* Make sure generated files or local secrets are not included.

In the pull request description, explain:

1. What was changed
2. Why the change is useful
3. How it was tested
4. Whether it changes public behavior

---

## Bug Reports

When reporting a bug, include useful information when possible:

* Python version
* Operating system
* Toolkit version or commit
* Minimal reproduction steps
* Expected behavior
* Actual behavior
* Relevant error output

Please do not include passwords, API keys, tokens, or other private credentials.

---

## Feature Requests

Feature proposals are welcome.

Useful proposals should explain:

* The production problem
* The proposed workflow
* Why the feature belongs in the toolkit
* Whether it should be core or platform-specific
* Example input and expected output when relevant

---

## Security

Do not publish private credentials or security-sensitive information in public Issues.

If a future dedicated security reporting process is added, this document will be updated accordingly.

---

## License

By contributing to this repository, you agree that your contributions may be distributed under the project's **MIT License**.

---

## Project Philosophy

AI Cinematic Workflow Toolkit aims to make AI-assisted cinematic production:

**Structured · Reproducible · Portable · Transparent · Creator-friendly**

Contributions that support these principles are welcome.
