"""
Entry point for orchestrating the gov data pipeline.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

sys.path.append(".")

from ingestion.ingest import IngestManager
from normalization.normalizer import Normalizer
from feature_detection.feature_manager import FeatureManager
from routing.strategy_router import StrategyRouter
from export.json_exporter import export_json
from ml_process.row_classifier import RowDropClassifier
from ontology.formatter import format_records as format_ontology_records


class Pipeline:
    """Coordinates ingestion → normalization → feature detection → export."""

    def __init__(self, workspace: Path) -> None:
        self.workspace = workspace

        self.raw_dir = workspace / "raw"
        self.clean_dir = workspace / "clean"
        self.processed_dir = workspace / "processed"

        self.clean_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

        self.ingestor = IngestManager()
        self.feature_manager = FeatureManager()
        self.router = StrategyRouter()
        self.row_classifier = RowDropClassifier()

    def run(self) -> None:
        """Run the pipeline on every dataset inside /raw."""
        print(f"Pipeline starting in workspace: {self.workspace}")

        for file_path in self.raw_dir.iterdir():
            if not file_path.is_file():
                continue

            print(f"Processing file: {file_path.name}")

            try:
                df = self.ingestor.load_data(file_path)
                print(f"Loaded ({len(df)} records)")

                df = Normalizer.normalize(df)
                print("Normalized")

                records = df.to_dict(orient="records")
                if records:
                    self.row_classifier.fit(records)
                    drop_mask = self.row_classifier.predict_drop(records, auto_fit=False)
                    dropped = sum(drop_mask)
                    if dropped:
                        keep_mask = [not flag for flag in drop_mask]
                        df = df.loc[keep_mask].reset_index(drop=True)
                        records = [record for record, keep in zip(records, keep_mask) if keep]
                        print(f"Dropped {dropped} suspect rows via ML filter")
                    model_path = self.processed_dir / f"{file_path.stem}_row_classifier.json"
                    self.row_classifier.save(model_path)

                features = self.feature_manager.evaluate(records)
                strategy = self.router.resolve(features)
                enriched_records = [strategy.apply(record) for record in records]
                print(
                    "Profiled:"
                    f" {features['column_count']} columns,"
                    f" fingerprint={features['schema_fingerprint']}"
                    f" strategy={strategy.name}"
                )

                output_path = self.clean_dir / f"{file_path.stem}_clean.csv"
                df.to_csv(output_path, index=False)

                profile_path = self.processed_dir / f"{file_path.stem}_profile.json"
                profile_path.write_text(json.dumps(features, indent=2))

                ontology_records, metadata_records = format_ontology_records(
                    records,
                    provider=file_path.stem,
                    provider_path=file_path,
                )
                ontology_path = self.processed_dir / f"{file_path.stem}_ontology.json"
                export_json(ontology_records, ontology_path)
                metadata_path = self.processed_dir / f"{file_path.stem}_mcp_metadata.json"
                export_json(metadata_records, metadata_path)

                print(f"Saved cleaned CSV to {output_path}")
                print(f"Wrote feature profile to {profile_path}")
                print(f"Exported ontology records to {ontology_path}")
                print(f"Wrote MCP metadata to {metadata_path}")

            except Exception as exc:  # pragma: no cover - cli side effects
                raise RuntimeError(f"Failed while processing {file_path}") from exc

        print("\nPipeline finished.")


def main() -> None:
    """Run the entire parsing pipeline."""
    workspace = Path("./data")
    pipeline = Pipeline(workspace)
    pipeline.run()


if __name__ == "__main__":
    main()
