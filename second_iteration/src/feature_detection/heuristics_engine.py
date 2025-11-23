"""Combines analyzers to produce feature tags."""

from __future__ import annotations


def run_heuristics(record: dict[str, object]) -> set[str]:
    """
    Return heuristic feature tags for a column.

    The caller provides a record with the column `name`, a `summary` generated
    by :func:`unique_value_summary`, and the raw `values` list.
    """
    tags: set[str] = set()
    summary: dict[str, float] = record.get("summary", {}) or {}
    name = str(record.get("name", "")).lower()

    distinct_ratio = float(summary.get("distinct_ratio", 0.0))
    null_ratio = float(summary.get("null_ratio", 0.0))
    most_frequent_ratio = float(summary.get("most_frequent_ratio", 0.0))
    non_null_count = float(summary.get("non_null_count", 0.0))

    if name in {"id", "identifier"} or name.endswith("_id"):
        tags.add("likely_identifier")

    if distinct_ratio > 0.95 and null_ratio < 0.05:
        tags.add("high_uniqueness")

    if distinct_ratio < 0.15 and non_null_count >= 5:
        tags.add("low_cardinality")

    if most_frequent_ratio > 0.8:
        tags.add("dominant_value")

    if null_ratio > 0.4:
        tags.add("sparse_values")

    return tags
