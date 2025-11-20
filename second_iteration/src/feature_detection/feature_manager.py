"""Facade that surfaces feature detection decisions."""

from __future__ import annotations


class FeatureManager:  # pragma: no cover - placeholder facade
    """Provides a simple API to downstream components."""

    def evaluate(self, records: list[dict[str, object]]) -> dict[str, object]:
        """Return derived metadata for each column."""
        raise NotImplementedError("Implement feature management")
