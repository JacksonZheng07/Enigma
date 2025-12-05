"""File type detector used before selecting a loader."""

from pathlib import Path


class FileDetector:
    """Normalize file suffixes so the ingestion manager can pick a loader."""

    def detect_file_type(self, path: Path) -> str:
        """
        Return the lowercase file suffix for ``path``.

        The detector does not enforce the extension whitelist so the caller can
        decide how to handle unknown types (e.g. raise a helpful error).
        """
        return path.suffix.lower()
