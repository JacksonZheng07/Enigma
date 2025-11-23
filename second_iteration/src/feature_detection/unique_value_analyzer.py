"""Analyzes uniqueness for columns to infer IDs and enumerations."""

from __future__ import annotations

from collections import Counter
from collections.abc import Hashable
import math
from typing import Any


def _is_missing(value: object) -> bool:
    """Return True for common null sentinels."""
    if value is None:
        return True
    if isinstance(value, float):
        return math.isnan(value)
    return False


def _make_hashable(value: object) -> Hashable | str:
    """Best-effort conversion so non-hashables (list/dict) can be counted."""
    if isinstance(value, dict):
        return tuple(sorted((k, _make_hashable(v)) for k, v in value.items()))
    if isinstance(value, (list, tuple)):
        return tuple(_make_hashable(v) for v in value)
    if isinstance(value, set):
        return tuple(sorted(_make_hashable(v) for v in value))
    if isinstance(value, (str, bytes)):
        return value
    if isinstance(value, Hashable):
        return value
    # Fallback for exotic objects – representation is stable enough for stats.
    return repr(value)


def unique_value_summary(values: list[object]) -> dict[str, float]:
    """Return lightweight uniqueness metrics for downstream heuristics."""
    total = float(len(values))
    if total == 0:
        return {
            "total_count": 0.0,
            "non_null_count": 0.0,
            "distinct_count": 0.0,
            "distinct_ratio": 0.0,
            "null_ratio": 0.0,
            "most_frequent_ratio": 0.0,
        }

    non_null_values: list[Any] = []
    null_count = 0
    for value in values:
        if _is_missing(value):
            null_count += 1
            continue
        non_null_values.append(_make_hashable(value))

    non_null_count = float(len(non_null_values))
    distinct_count = float(len(set(non_null_values))) if non_null_values else 0.0
    distinct_ratio = distinct_count / total
    null_ratio = null_count / total

    most_common_ratio = 0.0
    if non_null_values:
        most_common_count = Counter(non_null_values).most_common(1)[0][1]
        most_common_ratio = most_common_count / total

    return {
        "total_count": total,
        "non_null_count": non_null_count,
        "distinct_count": distinct_count,
        "distinct_ratio": distinct_ratio,
        "null_ratio": null_ratio,
        "most_frequent_ratio": most_common_ratio,
    }
