"""Tests for routing strategies and router selection."""

from __future__ import annotations

from pathlib import Path
import unittest

from routing.strategy_router import StrategyRouter
from routing.strategies.address_strategy import AddressStrategy
from routing.strategies.geo_strategy import GeoStrategy
from routing.strategies.financial_strategy import FinancialStrategy
from routing.strategies.demographic_strategy import DemographicStrategy
from routing.strategies.generic_strategy import GenericStrategy


class TestRoutingStrategies(unittest.TestCase):
    """Ensure strategies enrich records with expected metadata."""

    def test_address_strategy(self) -> None:
        """Address strategy should emit full address and coordinate flag."""
        strategy = AddressStrategy(name="address")
        record = {
            "address_building": "123",
            "address_street_name": "Main St",
            "address_city": "NYC",
            "address_state": "NY",
            "zip_code": "10001",
            "latitude": 40.71,
            "longitude": -73.99,
        }
        enriched = strategy.apply(record)
        self.assertEqual(enriched["full_address"], "123 Main St NYC NY 10001")
        self.assertTrue(enriched["has_coordinates"])

    def test_geo_strategy(self) -> None:
        """Geo strategy should coerce coordinates and centroid."""
        strategy = GeoStrategy(name="geo")
        record = {"lat": "40.71", "lon": "-73.99"}
        enriched = strategy.apply(record)
        self.assertAlmostEqual(enriched["latitude"], 40.71)
        self.assertAlmostEqual(enriched["longitude"], -73.99)
        self.assertTrue(enriched["has_valid_coordinates"])
        self.assertEqual(enriched["centroid"], (40.71, -73.99))

    def test_financial_strategy(self) -> None:
        """Financial totals should sum numeric fields."""
        strategy = FinancialStrategy(name="financial")
        record = {"fine_amount": "100.50", "payment_due": 50, "notes": "n/a"}
        enriched = strategy.apply(record)
        self.assertAlmostEqual(enriched["financial_total"], 150.5)
        self.assertFalse(enriched["has_financial_red_flag"])

    def test_demographic_strategy(self) -> None:
        """Demographic strategy should calculate density metrics."""
        strategy = DemographicStrategy(name="demographic")
        record = {"population": "1000", "households": 200, "area_sq_miles": 2}
        enriched = strategy.apply(record)
        self.assertEqual(enriched["population_density"], 500.0)
        self.assertEqual(enriched["average_household_size"], 5.0)

    def test_generic_strategy(self) -> None:
        """Generic strategy should produce record hash and notes."""
        strategy = GenericStrategy(name="generic")
        record = {"foo": "bar"}
        enriched = strategy.apply(record)
        self.assertIn("_record_hash", enriched)
        self.assertEqual(enriched["_strategy"], "generic")


class TestStrategyRouter(unittest.TestCase):
    """Validate router selection logic."""

    def setUp(self) -> None:
        self.router = StrategyRouter()

    def test_route_geo(self) -> None:
        """Presence of lat/lon should pick geo strategy."""
        profile = {"columns": {"latitude": {"tags": []}, "longitude": {"tags": []}}}
        self.assertEqual(self.router.route(profile), "geo")

    def test_route_address(self) -> None:
        """Address-specific fields should route to address strategy."""
        profile = {"columns": {"zip_code": {"tags": ["zip_code"]}, "address_city": {"tags": []}}}
        self.assertEqual(self.router.route(profile), "address")

    def test_route_financial(self) -> None:
        """Financial tokens should route to financial strategy."""
        profile = {"columns": {"fine_amount": {"tags": []}}}
        self.assertEqual(self.router.route(profile), "financial")

    def test_route_demographic(self) -> None:
        """Demographic tokens should route to demographic strategy."""
        profile = {"columns": {"population": {"tags": []}}}
        self.assertEqual(self.router.route(profile), "demographic")

    def test_route_generic(self) -> None:
        """Fallback when nothing matches."""
        profile = {"columns": {"name": {"tags": []}}}
        self.assertEqual(self.router.route(profile), "generic")

    def test_resolve_returns_strategy(self) -> None:
        """Resolve should produce usable strategy instance."""
        profile = {"columns": {"zip_code": {"tags": ["zip_code"]}}}
        strategy = self.router.resolve(profile)
        self.assertIsInstance(strategy, AddressStrategy)


if __name__ == "__main__":
    unittest.main()
