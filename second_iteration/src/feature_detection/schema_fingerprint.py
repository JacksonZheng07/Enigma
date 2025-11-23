"""Creates schema fingerprints for dataset similarity."""

from __future__ import annotations

import hashlib


def fingerprint(columns: list[str]) -> str:
    """
    Return a deterministic short hash representing the column layout.

    The hash is stable for the same ordered set of column names, letting the
    caller quickly compare schemas across datasets without storing the entire
    structure.
    """
    if not columns:
        return ""

    # Preserve the original order but de-duplicate successive repeats.
    ordered = []
    seen = set()
    for name in columns:
        if name not in seen:
            ordered.append(name)
            seen.add(name)

    digest = hashlib.sha1("||".join(ordered).encode("utf-8"))
    return digest.hexdigest()[:16]
