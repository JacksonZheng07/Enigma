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
        import json

        with open(source, "r", encoding="utf-8") as f:
            payload = json.load(f)

        if isinstance(payload, list):
            df = pd.DataFrame(payload)

        elif isinstance(payload, dict):
            df = pd.json_normalize(payload)
            df = pd.DataFrame(df)

        else:
            raise TypeError(
                f"Unsupported JSON structure. Expected list or dict, got {type(payload)}"
            )

        df.astype(str)

        if not isinstance(df, pd.DataFrame):
            return pd.DataFrame(df)
        
        return df