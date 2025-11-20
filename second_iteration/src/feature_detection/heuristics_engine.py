"""Combines analyzers to produce feature tags."""

from __future__ import annotations


def run_heuristics(record: dict[str, object]) -> set[str]:
    """Return detected feature tags."""
    raise NotImplementedError("Implement heuristic tagging")
