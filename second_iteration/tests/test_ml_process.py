"""Tests for the lightweight ML row drop classifier."""

from __future__ import annotations

from pathlib import Path
import unittest

from ml_process.row_classifier import RowDropClassifier


class TestRowDropClassifier(unittest.TestCase):
    """
    Validate the lightweight row drop classifier.
    """

    def test_flags_sparse_row(self) -> None:
        """Sparse rows with null-like values should be flagged for dropping."""
        records = [
            {"name": "Acme", "amount": 100, "city": "NY"},
            {"name": "", "amount": 0, "city": None},
        ]

        classifier = RowDropClassifier(threshold=0.5)
        classifier.fit(records)
        drop_mask = classifier.predict_drop(records, auto_fit=False)

        self.assertEqual(drop_mask, [False, True])

        kept, dropped = classifier.filter_records(records, auto_fit=False)
        self.assertEqual(len(kept), 1)
        self.assertEqual(dropped, 1)
        self.assertEqual(kept[0]["name"], "Acme")

    def test_save_and_load_classifier(self) -> None:
        """Persisting the classifier should retain predictions."""
        records = [
            {"name": "Acme", "amount": 100, "city": "NY"},
            {"name": "", "amount": 0, "city": None},
        ]
        classifier = RowDropClassifier(threshold=0.5).fit(records)
        path = Path("tests/.tmp_row_classifier.json")
        classifier.save(path)

        loaded = RowDropClassifier.load(path)
        probabilities = loaded.predict_proba(records)
        self.assertEqual(len(probabilities), len(records))
        path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
