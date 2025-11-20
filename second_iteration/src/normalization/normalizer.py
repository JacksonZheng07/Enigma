"""Coordinates cleaning, aliasing, and type casting."""

from __future__ import annotations


class Normalizer:  # pragma: no cover - placeholder facade
    """Sequentially applies the normalization primitives."""

    def normalize(self, records: list[dict[str, object]]) -> list[dict[str, object]]:
        """Return normalized records."""
        raise NotImplementedError("Add normalization pipeline")
