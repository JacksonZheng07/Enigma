"""Entry point for orchestrating the gov data pipeline."""

from __future__ import annotations

from pathlib import Path


class Pipeline:  # pragma: no cover - structure placeholder
    """Wires ingestion, normalization, feature detection, ML, and export stages."""

    def __init__(self, workspace: Path) -> None:
        self.workspace = workspace

    def run(self) -> None:
        """Kick off each pipeline stage. Replace with real orchestration logic."""
        raise NotImplementedError("Implement the orchestration logic once components are ready.")

def main() -> None:
    """
    main where the code runs
    """
    pass

if __name__ == "__main__":
    Pipeline(Path("./data"))
