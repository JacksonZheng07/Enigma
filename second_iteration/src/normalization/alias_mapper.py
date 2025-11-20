"""Maps provider specific column names to canonical aliases."""

from __future__ import annotations


ALIASES = {"fname": "first_name", "lname": "last_name"}


def map_aliases(record: dict[str, object]) -> dict[str, object]:
    """Rename keys using alias table."""
    return {ALIASES.get(key, key): value for key, value in record.items()}
