"""Base class for routing strategies."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BaseStrategy:  # pragma: no cover - structural placeholder
    """Defines the interface shared by concrete strategies."""

    name: str

    def apply(self, record: dict[str, object]) -> dict[str, object]:
        """Return the enriched record."""
        raise NotImplementedError("Override in subclasses")
