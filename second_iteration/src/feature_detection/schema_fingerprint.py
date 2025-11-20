"""Creates schema fingerprints for dataset similarity."""

from __future__ import annotations


def fingerprint(columns: list[str]) -> str:
    """Return a fingerprint hash string."""
    raise NotImplementedError("Implement schema fingerprinting")
