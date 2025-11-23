"""Exports normalized records to JSON."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable


def _json_default(value: Any) -> Any:
    """Best-effort serializer for sets and dataclasses."""
    if isinstance(value, set):
        return sorted(value)
    if hasattr(value, "__dict__"):
        return value.__dict__
    return str(value)


def export_json(records: Iterable[dict[str, object]], path: Path) -> None:
    """
    Write the records to the provided path in UTF-8 encoded JSON.

    Non-serializable values are coerced to strings to provide a resilient export
    for exploratory data.
    """
    normalized_records = list(records or [])
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(normalized_records, indent=2, default=_json_default),
        encoding="utf-8",
    )
