"""Fallback strategy when no specialized route matches."""

from __future__ import annotations

from ..base_strategy import BaseStrategy
from normalization.cleaner import Cleaner


class GenericStrategy(BaseStrategy):
    """Performs basic enrichment shared by all datasets."""

    def apply(self, record: dict[str, object]) -> dict[str, object]:
        cleaned = Cleaner.clean_record(record or {})
        cleaned.setdefault("_notes", [])
        cleaned["_strategy"] = self.name
        cleaned["_record_hash"] = hash(repr(sorted(cleaned.items())))
        return cleaned
