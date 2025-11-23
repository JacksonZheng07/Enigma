"""Tests for ontology formatter."""

from __future__ import annotations

from pathlib import Path
import unittest

from ontology.formatter import format_record


class TestOntologyFormatter(unittest.TestCase):
    """Ensure ontology formatter produces expected structure."""

    def test_format_record(self) -> None:
        """Formatter should normalize core fields and produce canonical names."""
        record = {
            "business_name": "ACME, INC.",
            "business_name_2": "ACME Retail",
            "address_building": "123",
            "address_street_name": "main st",
            "address_city": "new york",
            "address_state": "New York",
            "zip_code": "10001-1234",
            "contact_phone_number": "(212) 555-0199",
            "latitude": "40.0",
            "longitude": "-73.0",
            "dca_license_number": "12345",
            "license_status": "active",
            "industry": "Retail",
        }

        canonical, metadata = format_record(record, provider="testing", provider_path=Path("data/raw/testing.json"))

        self.assertEqual(canonical["canonical_legal_entity_name"], "Acme Inc")
        self.assertEqual(canonical["canonical_brand_name"], "Acme Retail")
        self.assertEqual(canonical["street_address"], "123 MAIN ST")
        self.assertEqual(canonical["city"], "New York")
        self.assertEqual(canonical["state"], "NY")
        self.assertEqual(canonical["zip_code"], "10001")
        self.assertEqual(canonical["zip_plus_4"], "1234")
        self.assertEqual(canonical["phone_number"], "2125550199")
        self.assertAlmostEqual(canonical["latitude"], 40.0)
        self.assertAlmostEqual(canonical["longitude"], -73.0)
        self.assertEqual(canonical["provider_record_id"], "12345")
        self.assertEqual(canonical["entity_status"], "ACTIVE")
        self.assertEqual(metadata["provider_record_id"], "12345")
        self.assertIn("raw_record", metadata)


if __name__ == "__main__":
    unittest.main()
