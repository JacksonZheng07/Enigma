"""
CSV loader responsible for structured flat-file ingestion.
"""

from pathlib import Path
import pandas as pd
from .base_loader import BaseLoader


class CSVLoader(BaseLoader):
    """
    Load a dataset from a CSV file into a pandas DataFrame.
    """
    def load(self, source: str | Path) -> pd.DataFrame:
        """
        Load the CSV file and convert it into a pandas DataFrame.

        Parameters
        ----------
        source : str | Path
            Path to the CSV file.

        Returns
        -------
        pd.DataFrame
            A DataFrame containing the loaded dataset.
        """
        df = pd.read_csv(source, dtype=str)
        return df
