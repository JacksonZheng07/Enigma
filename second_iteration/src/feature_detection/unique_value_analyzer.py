"""Analyzes uniqueness for columns to infer IDs and enumerations."""

from __future__ import annotations


def unique_value_summary(values: list[object]) -> dict[str, float]:
    """Return stats like distinct ratios for decision making."""
    raise NotImplementedError("Implement unique value analysis")
