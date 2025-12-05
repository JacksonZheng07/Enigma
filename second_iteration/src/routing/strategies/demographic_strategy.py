"""Strategy designed for demographic datasets."""

from __future__ import annotations

from ..base_strategy import BaseStrategy

try:  # pragma: no cover
    from ...normalization.cleaner import Cleaner
except ImportError:  # pragma: no cover
    from normalization.cleaner import Cleaner


class DemographicStrategy(BaseStrategy):
    """Adds demographic derived fields."""

    def apply(self, record: dict[str, object]) -> dict[str, object]:
        cleaned = Cleaner.clean_record(record or {})
        population = _to_number(cleaned.get("population"))
        households = _to_number(cleaned.get("households"))
        area = _to_number(
            cleaned.get("area_sq_miles")
            or cleaned.get("area_sq_km")
            or cleaned.get("land_area")
        )

        cleaned["population_density"] = (
            population / area if population is not None and area not in (None, 0) else None
        )
        cleaned["average_household_size"] = (
            population / households
            if population is not None and households not in (None, 0)
            else None
        )
        cleaned["_strategy"] = self.name
        return cleaned


def _to_number(value: object) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).replace(",", ""))
    except ValueError:
        return None
