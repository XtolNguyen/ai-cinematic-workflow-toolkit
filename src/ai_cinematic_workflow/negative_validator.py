"""
Negative constraint validation and normalization.

This module cleans, deduplicates, and validates negative constraints
used in cinematic AI-generation workflows.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class NegativeValidationResult:
    """Normalized negative constraints and detected problems."""

    constraints: list[str]
    warnings: list[str]

    @property
    def is_valid(self) -> bool:
        """Return True when no warnings were detected."""
        return not self.warnings

    def to_prompt(self) -> str:
        """Return normalized constraints as a prompt string."""
        return ", ".join(self.constraints)


def normalize_constraint(value: str) -> str:
    """Normalize one negative constraint."""

    return " ".join(
        value.strip().lower().split()
    )


def validate_negative_constraints(
    constraints: list[str],
) -> NegativeValidationResult:
    """
    Normalize and validate negative constraints.

    Rules:
    - Remove empty values.
    - Normalize whitespace and casing.
    - Remove duplicates while preserving order.
    - Warn about extremely long entries.
    """

    normalized: list[str] = []
    warnings: list[str] = []
    seen: set[str] = set()

    for raw_constraint in constraints:
        constraint = normalize_constraint(raw_constraint)

        if not constraint:
            continue

        if constraint in seen:
            continue

        seen.add(constraint)
        normalized.append(constraint)

        if len(constraint) > 120:
            warnings.append(
                f"Negative constraint is unusually long: "
                f"{constraint[:40]}..."
            )

    if not normalized:
        warnings.append(
            "No usable negative constraints were provided."
        )

    return NegativeValidationResult(
        constraints=normalized,
        warnings=warnings,
    )


def merge_negative_constraints(
    *constraint_groups: list[str],
) -> list[str]:
    """
    Merge multiple negative-constraint lists
    and return a normalized deduplicated result.
    """

    combined: list[str] = []

    for group in constraint_groups:
        combined.extend(group)

    return validate_negative_constraints(
        combined
    ).constraints
