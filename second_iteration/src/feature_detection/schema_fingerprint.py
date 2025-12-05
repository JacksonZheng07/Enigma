"""Creates schema fingerprints for dataset similarity."""
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

    ordered = list(dict.fromkeys(columns))
    digest = hashlib.sha1("||".join(ordered).encode("utf-8"))
    return digest.hexdigest()[:16]
