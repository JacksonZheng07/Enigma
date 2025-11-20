"""
base_loader.py creates the interface for the other loader classes
in this directory.

All loaders (CSVLoader, JSONLoader, XMLLoader, APILoader) must inherit
from this BaseLoader class and implement the `load()` method.

Each loader returns a pandas DataFrame, keeping ingestion consistent
across file-based and API-based sources.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union
import pandas as pd


PathOrStr = Union[str, Path]


class BaseLoader(ABC):
    """Abstract interface that all loaders must implement."""

    @abstractmethod
    def load(self, source: PathOrStr) -> pd.DataFrame:
        """
        Load a dataset from a file path or URL/endpoint
        and return a pandas DataFrame.

        Parameters
        ----------
        source : PathOrStr
            The file path (CSV/JSON/XML) or URL/endpoint for API loaders.

        Returns
        -------
        pd.DataFrame
            The ingested dataset, converted into a DataFrame.
        """
        raise NotImplementedError
