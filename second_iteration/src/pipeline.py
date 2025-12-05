"""Entry point for orchestrating the gov data pipeline."""

from __future__ import annotations

from pathlib import Path

if __package__ in (None, ""):
    from ingestion.ingest import IngestManager
    from normalization.normalizer import Normalizer
    from feature_detection.feature_manager import FeatureManager
    from routing.strategy_router import StrategyRouter
    from export.json_exporter import export_json
    from ml_process.row_classifier import RowDropClassifier
    from ontology.formatter import format_records as format_ontology_records
else:
    from .ingestion.ingest import IngestManager
    from .normalization.normalizer import Normalizer
    from .feature_detection.feature_manager import FeatureManager
    from .routing.strategy_router import StrategyRouter
    from .export.json_exporter import export_json
    from .ml_process.row_classifier import RowDropClassifier
    from .ontology.formatter import format_records as format_ontology_records


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
            dataset_key = file_path.stem
            clean_dataset_dir = self.clean_dir / dataset_key
            processed_dataset_dir = self.processed_dir / dataset_key
            clean_dataset_dir.mkdir(parents=True, exist_ok=True)
            processed_dataset_dir.mkdir(parents=True, exist_ok=True)

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

                features = self.feature_manager.evaluate(records)
                strategy = self.router.resolve(features)
                enriched_records = [strategy.apply(record) for record in records]

                output_path = clean_dataset_dir / "clean.csv"
                df.to_csv(output_path, index=False)

                ontology_records, metadata_records = format_ontology_records(
                    records,
                    provider=file_path.stem,
                    provider_path=file_path,
                )
                ontology_path = processed_dataset_dir / "ontology.json"
                export_json(ontology_records, ontology_path)
                metadata_path = processed_dataset_dir / "mcp_metadata.json"
                export_json(metadata_records, metadata_path)

                print(f"Saved cleaned CSV to {output_path}")
                print(f"Exported ontology records to {ontology_path}")
                print(f"Wrote MCP metadata to {metadata_path}")

            except Exception as exc:  # pragma: no cover - cli side effects
                raise RuntimeError(f"Failed while processing {file_path}") from exc

        print("\nPipeline finished.")


def main() -> None:
    """Run the entire parsing pipeline."""
    workspace = Path(__file__).resolve().parents[1] / "data"
    pipeline = Pipeline(workspace)
    pipeline.run()


if __name__ == "__main__":
    main()
