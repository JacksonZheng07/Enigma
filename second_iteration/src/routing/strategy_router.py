"""Router that selects the strategy used for downstream enrichment."""

from __future__ import annotations


class StrategyRouter:  # pragma: no cover - placeholder facade
    """Selects the correct strategy implementation."""

    def route(self, dataset_profile: dict[str, object]) -> str:
        """Return the chosen strategy key."""
        raise NotImplementedError("Add routing logic")
