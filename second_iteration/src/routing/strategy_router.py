"""Router that selects the strategy used for downstream enrichment."""

from __future__ import annotations

from collections.abc import Mapping

from .strategies.address_strategy import AddressStrategy
from .strategies.demographic_strategy import DemographicStrategy
from .strategies.financial_strategy import FinancialStrategy
from .strategies.geo_strategy import GeoStrategy
from .strategies.generic_strategy import GenericStrategy


class StrategyRouter:
    """Selects the correct strategy implementation."""

    def __init__(self) -> None:
        self._strategies = {
            "address": AddressStrategy(name="address"),
            "geo": GeoStrategy(name="geo"),
            "financial": FinancialStrategy(name="financial"),
            "demographic": DemographicStrategy(name="demographic"),
            "generic": GenericStrategy(name="generic"),
        }

    def route(self, dataset_profile: Mapping[str, object] | None) -> str:
        """Return the chosen strategy key."""
        columns = (dataset_profile or {}).get("columns", {})  # type: ignore[assignment]
        column_names = {name.lower(): meta for name, meta in columns.items()}
        tags = _collect_values(columns, "tags") | _collect_values(columns, "patterns")

        if _looks_geo(column_names, tags):
            return "geo"
        if _looks_address(column_names, tags):
            return "address"
        if _looks_financial(column_names):
            return "financial"
        if _looks_demographic(column_names):
            return "demographic"
        return "generic"

    def get_strategy(self, key: str) -> GenericStrategy:
        """Return the instantiated strategy, defaulting to generic."""
        return self._strategies.get(key, self._strategies["generic"])

    def resolve(self, dataset_profile: Mapping[str, object] | None) -> GenericStrategy:
        """Convenience helper returning the routed strategy instance."""
        key = self.route(dataset_profile)
        return self.get_strategy(key)


def _collect_values(columns: Mapping[str, dict[str, object]], key: str) -> set[str]:
    values: set[str] = set()
    for meta in columns.values():
        for value in meta.get(key, []) or []:
            values.add(str(value).lower())
    return values


def _looks_geo(column_names: Mapping[str, object], tags: set[str]) -> bool:
    geo_columns = {"lat", "lon", "latitude", "longitude", "geometry", "geom"}
    return bool(geo_columns & set(column_names) or {"geo"}.intersection(tags))


def _looks_address(column_names: Mapping[str, object], tags: set[str]) -> bool:
    address_tokens = {
        "address",
        "address_building",
        "address_street_name",
        "secondary_address_street_name",
        "zip_code",
        "address_city",
        "address_state",
        "borough",
        "borough_code",
    }
    return bool(address_tokens & set(column_names) or {"zip_code", "state_code"} & tags)


def _looks_financial(column_names: Mapping[str, object]) -> bool:
    financial_tokens = {"revenue", "amount", "fine", "fee", "payment", "tax", "cost"}
    return any(any(token in name for token in financial_tokens) for name in column_names)


def _looks_demographic(column_names: Mapping[str, object]) -> bool:
    demographic_tokens = {
        "population",
        "median_age",
        "median_income",
        "households",
        "demographic",
        "gender",
        "race",
    }
    return bool(demographic_tokens & set(column_names))
