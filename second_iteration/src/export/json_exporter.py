"""Exports normalized records to JSON."""

from __future__ import annotations

from pathlib import Path


def export_json(records: list[dict[str, object]], path: Path) -> None:
    """Write the records to the provided path."""
    raise NotImplementedError("Implement JSON exporting")
