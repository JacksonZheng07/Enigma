"""Strategy for geospatial datasets."""

from __future__ import annotations

from ..base_strategy import BaseStrategy

try:  # pragma: no cover
    from ...normalization.cleaner import Cleaner
except ImportError:  # pragma: no cover
    from normalization.cleaner import Cleaner


class GeoStrategy(BaseStrategy):
    """Adds geometry or coordinate derived features."""

    def apply(self, record: dict[str, object]) -> dict[str, object]:
        cleaned = Cleaner.clean_record(record or {})

        lat = cleaned.get("latitude") or cleaned.get("lat")
        lon = cleaned.get("longitude") or cleaned.get("lon")
        latitude = Cleaner._to_float(lat)  # type: ignore[attr-defined]
        longitude = Cleaner._to_float(lon)  # type: ignore[attr-defined]

        cleaned["latitude"] = latitude
        cleaned["longitude"] = longitude
        cleaned.pop("lat", None)
        cleaned.pop("lon", None)

        cleaned["has_valid_coordinates"] = (
            cleaned["latitude"] is not None and cleaned["longitude"] is not None
        )
        cleaned["centroid"] = (
            (cleaned["latitude"], cleaned["longitude"])
            if cleaned["has_valid_coordinates"]
            else None
        )
        cleaned["_strategy"] = self.name
        return cleaned
