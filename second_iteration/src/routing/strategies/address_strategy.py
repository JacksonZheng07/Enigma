"""Strategy for location-focused datasets."""

from __future__ import annotations

from ..base_strategy import BaseStrategy

try:  # pragma: no cover - allow running strategy standalone
    from ...normalization.cleaner import Cleaner
except ImportError:  # pragma: no cover
    from normalization.cleaner import Cleaner


class AddressStrategy(BaseStrategy):
    """Enriches address-like records."""

    def apply(self, record: dict[str, object]) -> dict[str, object]:
        cleaned = Cleaner.clean_record(record or {})
        parts = [
            cleaned.get("address_building"),
            cleaned.get("address_street_name"),
            cleaned.get("secondary_address_street_name"),
            cleaned.get("address_city"),
            cleaned.get("address_state"),
            cleaned.get("zip_code"),
        ]
        cleaned["full_address"] = " ".join(part for part in parts if part) or None
        cleaned["has_coordinates"] = bool(
            cleaned.get("latitude") is not None and cleaned.get("longitude") is not None
        )
        cleaned["_strategy"] = self.name
        return cleaned
