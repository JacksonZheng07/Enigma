"""Strategy designed for demographic datasets."""

from __future__ import annotations

from ..base_strategy import BaseStrategy


class DemographicStrategy(BaseStrategy):
    """Adds demographic derived fields."""

    def apply(self, record: dict[str, object]) -> dict[str, object]:
        raise NotImplementedError("Implement demographic enrichment")
