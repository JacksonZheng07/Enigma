"""Detects regex-style patterns in textual columns."""

from __future__ import annotations

import re

_PATTERNS: dict[str, re.Pattern[str]] = {
    "zip_code": re.compile(r"^\d{5}(?:-\d{4})?$"),
    "state_code": re.compile(r"^[A-Z]{2}$"),
    "iso_date": re.compile(r"^\d{4}-\d{2}-\d{2}$"),
    "email": re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$"),
    "phone": re.compile(r"^\+?[\d\-\s().]{7,}$"),
}

_MIN_RATIO = 0.8


def detect_patterns(values: list[str]) -> list[str]:
    """Return names of patterns that match the majority of provided strings."""
    normalized = [value.strip() for value in values if isinstance(value, str)]
    if not normalized:
        return []

    total = len(normalized)
    matches: list[str] = []
    for name, pattern in _PATTERNS.items():
        count = sum(1 for value in normalized if pattern.fullmatch(value))
        if total and (count / total) >= _MIN_RATIO:
            matches.append(name)
    return matches
