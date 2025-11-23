"""Unit tests for the feature_detection package."""

from __future__ import annotations

import unittest

from feature_detection.unique_value_analyzer import unique_value_summary
from feature_detection.pattern_detector import detect_patterns
from feature_detection.heuristics_engine import run_heuristics
from feature_detection.feature_manager import FeatureManager


class TestFeatureDetection(unittest.TestCase):
    """Test the primitive feature detection utilities and facade."""

    def test_unique_value_summary(self) -> None:
        """Unique-value summary should compute expected ratios."""
        stats = unique_value_summary([1, 1, 2, None, "NA"])
        self.assertEqual(stats["distinct_count"], 3.0)
        self.assertAlmostEqual(stats["distinct_ratio"], 3 / 5)
        self.assertAlmostEqual(stats["null_ratio"], 1 / 5)
        self.assertAlmostEqual(stats["most_frequent_ratio"], 2 / 5)

    def test_pattern_detector_zip(self) -> None:
        """Zip-like patterns should be surfaced."""
        values = ["12345", "12345-6789", "99999", "10001", "bad"]
        patterns = detect_patterns(values)
        self.assertIn("zip_code", patterns)

    def test_heuristics_engine_tags(self) -> None:
        """ID-like columns should receive identifier heuristics."""
        summary = {
            "distinct_ratio": 1.0,
            "null_ratio": 0.0,
            "most_frequent_ratio": 0.1,
            "non_null_count": 10,
        }
        tags = run_heuristics({"name": "id", "summary": summary, "values": list(range(10))})
        self.assertIn("likely_identifier", tags)
        self.assertIn("high_uniqueness", tags)

    def test_feature_manager_evaluate(self) -> None:
        """FeatureManager should combine stats, patterns, and tags."""
        records = [
            {"id": 1, "zip_code": "10001", "state_code": "NY"},
            {"id": 2, "zip_code": "10001", "state_code": "NY"},
        ]
        feature_manager = FeatureManager()
        profile = feature_manager.evaluate(records)

        self.assertEqual(profile["row_count"], 2)
        self.assertEqual(profile["column_count"], 3)

        id_tags = profile["columns"]["id"]["tags"]
        self.assertIn("high_uniqueness", id_tags)
        self.assertIn("likely_identifier", id_tags)

        zip_tags = profile["columns"]["zip_code"]["tags"]
        self.assertIn("zip_code", zip_tags)


if __name__ == "__main__":
    unittest.main()
