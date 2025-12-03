"""Integration test for the full pipeline."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import tempfile
import unittest

from pipeline import Pipeline


class TestPipelineIntegration(unittest.TestCase):
    """Run the pipeline against a disposable dataset and verify outputs."""

    def test_pipeline_produces_expected_artifacts(self) -> None:
        """Pipeline should create cleaned CSV and ontology/metadata files."""
        workspace = Path(tempfile.mkdtemp(prefix="pipeline-test-"))
        try:
            # Prepare fake workspace layout
            raw_dir = workspace / "raw"
            raw_dir.mkdir(parents=True, exist_ok=True)
            clean_dir = workspace / "clean"
            processed_dir = workspace / "processed"
            clean_dir.mkdir(parents=True, exist_ok=True)
            processed_dir.mkdir(parents=True, exist_ok=True)

            # Seed a small dataset using existing sample data for realism
            sample_source = Path("data/raw/testing_data.json")
            sample_target = raw_dir / "testing_data.json"
            shutil.copy(sample_source, sample_target)

            pipeline = Pipeline(workspace)
            pipeline.run()

            dataset_clean = clean_dir / "testing_data" / "clean.csv"
            dataset_processed = processed_dir / "testing_data"
            ontology_path = dataset_processed / "ontology.json"
            metadata_path = dataset_processed / "mcp_metadata.json"
            self.assertTrue(dataset_clean.exists(), "Clean CSV missing")
            self.assertTrue(ontology_path.exists(), "Ontology export missing")
            self.assertTrue(metadata_path.exists(), "MCP metadata missing")

            ontology_records = json.loads(ontology_path.read_text())
            metadata_records = json.loads(metadata_path.read_text())

            self.assertGreater(len(ontology_records), 0)
            self.assertGreater(len(metadata_records), 0)
            canonical = ontology_records[0]
            self.assertIn("canonical_legal_entity_name", canonical)
            self.assertIn("provider_record_id", canonical)

        finally:
            shutil.rmtree(workspace, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
