"""
Repository-wide release metadata validation for v0.2.0.

These tests verify that package metadata, public documentation,
roadmap state, changelog history, and provider boundaries describe
one coherent release-preparation state before the v0.2.0 Git tag
and GitHub Release are created.
"""

import re
from pathlib import Path

import ai_cinematic_workflow


PROJECT_ROOT = Path(
    __file__
).resolve().parents[1]

PYPROJECT_PATH = (
    PROJECT_ROOT
    / "pyproject.toml"
)

README_PATH = (
    PROJECT_ROOT
    / "README.md"
)

ROADMAP_PATH = (
    PROJECT_ROOT
    / "ROADMAP.md"
)

CHANGELOG_PATH = (
    PROJECT_ROOT
    / "CHANGELOG.md"
)


EXPECTED_VERSION = "0.2.0"
EXPECTED_TAG = "v0.2.0"
EXPECTED_RELEASE_DATE = "2026-08-13"


def read_text(
    path: Path,
) -> str:
    """Read one repository text file."""

    return path.read_text(
        encoding="utf-8"
    )


def extract_pyproject_version() -> str:
    """
    Read project.version without requiring tomllib.

    The repository supports Python 3.10, where tomllib is not part
    of the standard library.
    """

    text = read_text(
        PYPROJECT_PATH
    )

    match = re.search(
        r'(?m)^version\s*=\s*"([^"]+)"\s*$',
        text,
    )

    if match is None:
        raise AssertionError(
            "Could not find project version "
            "in pyproject.toml"
        )

    return match.group(1)


def test_release_files_exist():
    """Release metadata sources must exist."""

    assert PYPROJECT_PATH.exists()
    assert README_PATH.exists()
    assert ROADMAP_PATH.exists()
    assert CHANGELOG_PATH.exists()


def test_pyproject_version_is_020():
    """Distribution metadata should be prepared at 0.2.0."""

    assert (
        extract_pyproject_version()
        == EXPECTED_VERSION
    )


def test_public_package_version_is_020():
    """Public Python package version should match release metadata."""

    assert (
        ai_cinematic_workflow.__version__
        == EXPECTED_VERSION
    )


def test_package_versions_match():
    """Distribution and runtime package versions must agree."""

    assert (
        extract_pyproject_version()
        == ai_cinematic_workflow.__version__
    )


def test_readme_documents_released_v020():
    """
    README should identify v0.2.0 as the current released
    provider-neutral toolkit version.
    """

    text = read_text(
        README_PATH
    )

    assert (
        "**Current released version:** `v0.2.0`"
        in text
    )

    assert (
        "**v0.2.0 status:** Released"
        in text
    )

    assert (
        "Version `0.2.0` is the current released software state "
        "of the toolkit."
        in text
    )

    assert (
        "The package metadata is synchronized at version `0.2.0`."
        in text
    )


def test_roadmap_documents_released_v020():
    """
    ROADMAP should identify v0.2.0 as the current released
    cinematic timeline and music-video foundation.
    """

    text = read_text(
        ROADMAP_PATH
    )

    assert (
        "# v0.2.0 — Cinematic Timeline "
        "& Music Video Foundation"
        in text
    )

    assert (
        "Current released version: **v0.2.0**"
        in text
    )

    assert (
        "Status: **Released**"
        in text
    )

    assert (
        "Release date: **2026-08-13**"
        in text
    )

    assert (
        "The defined v0.2.0 implementation, testing, "
        "runnable-example, and documentation scope is complete."
        in text
    )


def test_v020_definition_of_done_has_no_unchecked_items():
    """
    The v0.2.0 Definition of Done must be fully complete
    before tagging the release.
    """

    text = read_text(
        ROADMAP_PATH
    )

    marker = (
        "# v0.2.0 Definition of Done"
    )

    assert marker in text

    definition = text.split(
        marker,
        1,
    )[1]

    assert (
        "* [ ]"
        not in definition
    )


def test_changelog_contains_v020_release_section():
    """CHANGELOG must contain the dated v0.2.0 release history."""

    text = read_text(
        CHANGELOG_PATH
    )

    assert (
        f"## [{EXPECTED_VERSION}] "
        f"- {EXPECTED_RELEASE_DATE}"
        in text
    )


def test_changelog_preserves_fresh_unreleased_section():
    """Future development needs a fresh Unreleased section."""

    text = read_text(
        CHANGELOG_PATH
    )

    assert (
        "## [Unreleased]"
        in text
    )

    unreleased = text.split(
        "## [Unreleased]",
        1,
    )[1].split(
        f"## [{EXPECTED_VERSION}]",
        1,
    )[0]

    assert (
        "Platform-specific adapters"
        in unreleased
    )

    assert (
        "Command-line interface"
        in unreleased
    )


def test_changelog_preserves_v010_history():
    """The previous public release must remain in history."""

    text = read_text(
        CHANGELOG_PATH
    )

    assert (
        "## [0.1.0] - 2026-08-12"
        in text
    )


def test_v020_changelog_precedes_v010():
    """Release history should remain newest-first."""

    text = read_text(
        CHANGELOG_PATH
    )

    v020_position = text.index(
        "## [0.2.0]"
    )

    v010_position = text.index(
        "## [0.1.0]"
    )

    assert (
        v020_position
        < v010_position
    )


def test_provider_specific_adapters_remain_future_work():
    """
    v0.2.0 must not claim concrete provider-specific production
    adapters that belong to future Production Adapter work.
    """

    readme = read_text(
        README_PATH
    )

    roadmap = read_text(
        ROADMAP_PATH
    )

    changelog = read_text(
        CHANGELOG_PATH
    )

    assert (
        "Future Provider-Specific Adapters"
        in readme
    )

    assert (
        "# v0.3.0 — Production Adapters"
        in roadmap
    )

    assert (
        "Status: **Future**"
        in roadmap
    )

    unreleased = changelog.split(
        "## [Unreleased]",
        1,
    )[1].split(
        "## [0.2.0]",
        1,
    )[0]

    assert (
        "Platform-specific adapters"
        in unreleased
    )


def test_readme_does_not_claim_provider_release():
    """README must not claim concrete WAN/Veo/Kling adapters exist."""

    text = read_text(
        README_PATH
    )

    assert (
        "The current toolkit does **not** claim "
        "to contain production-ready provider-specific "
        "WAN, Veo, Kling"
        in text
    )


def test_release_preparation_does_not_require_provider_credentials():
    """Core release documentation should preserve local execution."""

    text = read_text(
        README_PATH
    )

    assert (
        "provider API keys"
        in text
    )

    assert (
        "provider credentials"
        in text
    )

    assert (
        "network execution"
        in text
    )


def test_release_version_is_not_accidentally_v010():
    """Current package metadata must no longer identify itself as 0.1.0."""

    assert (
        extract_pyproject_version()
        != "0.1.0"
    )

    assert (
        ai_cinematic_workflow.__version__
        != "0.1.0"
    )


def test_expected_tag_matches_package_version():
    """
    The future Git tag name should derive directly from the
    validated package version.
    """

    assert (
        EXPECTED_TAG
        == (
            "v"
            + ai_cinematic_workflow.__version__
        )
    )
