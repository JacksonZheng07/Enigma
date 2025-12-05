"""Coordinates ingestion loaders and file routing."""

from pathlib import Path
from typing import Mapping, Optional, Protocol, Union

import pandas as pd

from .loaders.api_loader import APILoader
from .loaders.csv_loader import CSVLoader
from .loaders.json_loader import JSONLoader
from .file_detector import FileDetector


class IngestManager:
    """
    High-level API that downstream stages will call.
    Dispatches to the appropriate loader based on file type or source.
    """

    def __init__(
        self,
        detector: Optional[FileDetector] = None,
        loaders: Optional[Mapping[str, "LoaderProtocol"]] = None,
    ) -> None:
        self._detector = detector or FileDetector()
        self.loaders: dict[str, LoaderProtocol] = dict(
            loaders
            or {
                ".csv": CSVLoader(),
                ".json": JSONLoader(),
                "api": APILoader(),
            }
        )

    def load_data(self, source: Union[str, Path]) -> pd.DataFrame:
        """
        Route ingestion to the appropriate loader based on the file extension
        or API prefix.

        Parameters
        ----------
        source : str | Path
            File path to CSV/JSON, or API URL.

        Returns
        -------
        pd.DataFrame
            The loaded dataset as a pandas DataFrame.
        """
        if isinstance(source, str) and source.startswith(("http://", "https://")):
            return self.loaders["api"].load(source)

        path = Path(source).expanduser()
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        file_type = self._detector.detect_file_type(path)
        loader = self.loaders.get(file_type)
        if loader is None:
            raise ValueError(f"No loader registered for file type: {file_type}")

        return loader.load(path)


class LoaderProtocol(Protocol):
    """Tiny protocol so loaders can be type-checked."""

    def load(self, source: Union[str, Path]) -> pd.DataFrame:
        ...
