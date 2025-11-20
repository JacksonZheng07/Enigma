"""Strategy for location-focused datasets."""

from __future__ import annotations

from ..base_strategy import BaseStrategy


class AddressStrategy(BaseStrategy):
    """Enriches address-like records."""

    def apply(self, record: dict[str, object]) -> dict[str, object]:
        raise NotImplementedError("Implement address enrichment")
