"""Tests for export utilities."""

from __future__ import annotations

from pathlib import Path
import json
import unittest

from export.json_exporter import export_json


class TestJsonExporter(unittest.TestCase):
    """Ensure the JSON exporter writes expected files."""

    def test_export_json_writes_file(self) -> None:
        """Exporter should serialize records, including sets."""
        path = Path("tests/.tmp_export.json")
        records = [{"name": "Acme", "tags": {"a", "b"}}]
        export_json(records, path)

        contents = json.loads(path.read_text())
        self.assertEqual(contents[0]["name"], "Acme")
        self.assertEqual(sorted(contents[0]["tags"]), ["a", "b"])

        path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
