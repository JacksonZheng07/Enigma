"""
Coordinates ingestion loaders and file routing.
"""

from __future__ import annotations

from pathlib import Path
import pandas as pd
import os

from .loaders.api_loader import APILoader
from .loaders.csv_loader import CSVLoader
from .loaders.json_loader import JSONLoader
from .file_detector import FileDetector


class IngestManager:
    """
    High-level API that downstream stages will call.
    Dispatches to the appropriate loader based on file type or source.
    """

    loaders = {
        ".csv": CSVLoader(),
        ".json": JSONLoader(),
        "api": APILoader(),
    }

    def load_data(self, source: str | Path) -> pd.DataFrame:
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
        #Checks if it is an api request, done through checking if it starts with http
        if isinstance(source, str) and source.startswith("http"):
            loader = self.loaders["api"]
            return loader.load(source)

        path = Path(source)
        file_type = FileDetector().detect_file_type(path)

        if os.path.exists(path=path) is False:
            raise FileNotFoundError

        #Raising Error if the file suffix isnt a .json or a .csv
        if file_type not in self.loaders:
            raise ValueError(f"No loader registered for file type: {file_type}")

        loader = self.loaders[file_type]
        return loader.load(path)
