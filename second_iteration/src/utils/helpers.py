"""Miscellaneous helper utilities shared across modules."""

from __future__ import annotations


def chunk(iterable: list[object], size: int) -> list[list[object]]:
    """Yield chunks of the iterable."""
    return [iterable[i : i + size] for i in range(0, len(iterable), size)]
