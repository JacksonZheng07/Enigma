"""Facade that surfaces feature detection decisions."""

from __future__ import annotations

from collections import defaultdict

from .heuristics_engine import run_heuristics
from .pattern_detector import detect_patterns
from .schema_fingerprint import fingerprint
from .unique_value_analyzer import unique_value_summary


class FeatureManager:
    """Provides a simple API to downstream components."""

    def evaluate(self, records: list[dict[str, object]]) -> dict[str, object]:
        """
        Return derived metadata for each column.

        The output includes per-column uniqueness summaries, pattern matches,
        and heuristic tags alongside dataset-level counts.
        """
        if not records:
            return {
                "row_count": 0,
                "column_count": 0,
                "schema_fingerprint": "",
                "columns": {},
            }

        column_values: dict[str, list[object]] = defaultdict(list)
        column_order: list[str] = []
        for record in records:
            for column, value in (record or {}).items():
                if column not in column_values:
                    column_order.append(column)
                column_values[column].append(value)

        column_reports: dict[str, dict[str, object]] = {}
        for column in column_order:
            values = column_values[column]
            summary = unique_value_summary(values)

            string_values = [value for value in values if isinstance(value, str)]
            patterns = detect_patterns(string_values)

            heuristics_input = {
                "name": column,
                "summary": summary,
                "values": values,
            }
            tags = sorted(run_heuristics(heuristics_input) | set(patterns))

            column_reports[column] = {
                "summary": summary,
                "patterns": patterns,
                "tags": tags,
            }

        return {
            "row_count": len(records),
            "column_count": len(column_order),
            "schema_fingerprint": fingerprint(column_order),
            "columns": column_reports,
        }
