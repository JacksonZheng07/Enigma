"""
Entry point for orchestrating the gov data pipeline.
"""

from __future__ import annotations
from pathlib import Path
import sys
sys.path.append('.')

from ingestion.ingest import IngestManager
from normalization.normalizer import Normalizer


class Pipeline:
    """
    Coordinates ingestion → normalization → export.
    """

    def __init__(self, workspace: Path) -> None:
        self.workspace = workspace

        self.raw_dir = workspace / "raw"
        self.clean_dir = workspace / "clean"
        self.processed_dir = workspace / "processed"

        self.clean_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

        self.ingestor = IngestManager()

    def run(self) -> None:
        """
        Run the pipeline on every dataset inside /raw.
        """

        print(f"Pipeline starting in workspace: {self.workspace}")

        # Iterate over all source files in workspace/raw/
        for file_path in self.raw_dir.iterdir():
            print(f"Processing file: {file_path.name}")

            try:
                # 1. Ingest
                df = self.ingestor.load_data(file_path)
                print(f"Loaded ({len(df)} records)")

                # 2. Normalize
                df = Normalizer.normalize(df)
                print("Normalized")

                # 3. Export cleaned version
                output_path = self.clean_dir / f"{file_path.stem}_clean.csv"
                df.to_csv(output_path, index=False)
                print(f"Saved cleaned CSV to {output_path}")

            except Exception as e:
                raise RuntimeError(f"Failed while processing {file_path}") from e

        print("\nPipeline finished.")


def main() -> None:
    """
    Running the Entire Parsing Pipeline
    """
    workspace = Path("./data")
    pipeline = Pipeline(workspace)
    pipeline.run()


if __name__ == "__main__":
    main()
