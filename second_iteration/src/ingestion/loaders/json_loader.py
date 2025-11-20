"""
JSON loader that normalizes deeply nested objects.
"""

from __future__ import annotations
from pathlib import Path
import pandas as pd
from .base_loader import BaseLoader

class JSONLoader(BaseLoader):
    """
    Load a dataset from a JSON file into a pandas DataFrame.
    Automatically flattens deeply nested objects.
    """

    def load(self, source: str | Path) -> pd.DataFrame:
        """
        Load the JSON file and convert it into a normalized pandas DataFrame.

        Parameters
        ----------
        source : str | Path
            Path to a JSON file.

        Returns
        -------
        pd.DataFrame
            A DataFrame containing the normalized dataset.
        """

        # Load raw JSON (could be list or dict)
        raw = pd.read_json(source)

        # If it's already a DataFrame (list of objects)
        if isinstance(raw, pd.DataFrame):
            df = raw

        # If it's a dict or nested structure → flatten
        else:
            df = pd.json_normalize(raw)

        return df.astype(str)