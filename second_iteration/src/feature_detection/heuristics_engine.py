"""Combines analyzers to produce feature tags."""

from typing import Mapping


def run_heuristics(record: Mapping[str, object]) -> set[str]:
    """
    Return heuristic feature tags for a column.

    The caller provides a record with the column `name`, a `summary` generated
    by :func:`unique_value_summary`, and the raw `values` list.
    """
    tags: set[str] = set()
    summary = record.get("summary", {}) or {}
    name = str(record.get("name", "")).lower()

    distinct_ratio = _safe_ratio(summary, "distinct_ratio")
    null_ratio = _safe_ratio(summary, "null_ratio")
    most_frequent_ratio = _safe_ratio(summary, "most_frequent_ratio")
    non_null_count = _safe_ratio(summary, "non_null_count")

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


def _safe_ratio(summary: Mapping[str, object], key: str) -> float:
    """Best-effort conversion of the summary values to floats."""
    value = summary.get(key, 0.0)
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0
