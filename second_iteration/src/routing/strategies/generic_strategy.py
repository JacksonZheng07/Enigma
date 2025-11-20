"""Fallback strategy when no specialized route matches."""

from __future__ import annotations

from ..base_strategy import BaseStrategy


class GenericStrategy(BaseStrategy):
    """Performs basic enrichment shared by all datasets."""

    def apply(self, record: dict[str, object]) -> dict[str, object]:
        raise NotImplementedError("Implement generic enrichment")
