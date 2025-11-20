"""Casts columns to canonical Python types."""

from __future__ import annotations


def cast_types(record: dict[str, object]) -> dict[str, object]:
    """Cast raw values into well-defined Python types."""
    raise NotImplementedError("Implement type casting")
