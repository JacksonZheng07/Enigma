"""Strategy for geospatial datasets."""

from __future__ import annotations

from ..base_strategy import BaseStrategy


class GeoStrategy(BaseStrategy):
    """Adds geometry or coordinate derived features."""

    def apply(self, record: dict[str, object]) -> dict[str, object]:
        raise NotImplementedError("Implement geo enrichment")
